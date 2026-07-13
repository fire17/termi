"""termi v0.1 test battery — runs the real CLI inside a throwaway $HOME.

Every test builds a fresh fake home (ORACLE §6 done-means: nearly every bug
this product can have is visible in a fake home directory).
"""

import hashlib
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TERMI = REPO / "bin" / "termi"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

MARK_BEGIN = "# >>> termi >>>"
MARK_END = "# <<< termi <<<"


def strip_block(text: str) -> str:
    return re.sub(re.escape(MARK_BEGIN) + r".*?" + re.escape(MARK_END),
                  "", text, flags=re.DOTALL)


def load_termi():
    """Import bin/termi as a module so pure helpers can be unit-tested."""
    import importlib.util
    spec = importlib.util.spec_from_loader(
        "termi_mod", importlib.machinery.SourceFileLoader("termi_mod", str(TERMI)))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TermiHome:
    def __init__(self):
        self.home = Path(tempfile.mkdtemp(prefix="termi-test-home-"))

    @property
    def zshrc(self) -> Path:
        return self.home / ".zshrc"

    @property
    def termi_dir(self) -> Path:
        return self.home / ".termi"

    def run(self, *args, input_text=None, timeout=60, packs_dir=None):
        env = dict(os.environ)
        env.update(
            HOME=str(self.home),
            TERMI_DIR=str(self.termi_dir),
            TERMI_ZSHRC=str(self.zshrc),
            TERMI_PACKS_DIR=str(packs_dir or FIXTURES),
            NO_COLOR="1",
            ZDOTDIR=str(self.home),  # keep `zsh -ic` probes hermetic too
        )
        return subprocess.run(
            ["python3", str(TERMI), *args],
            capture_output=True, text=True, env=env,
            input=input_text, timeout=timeout,
        )

    def cleanup(self):
        shutil.rmtree(self.home, ignore_errors=True)


class TermiTest(unittest.TestCase):
    def setUp(self):
        self.h = TermiHome()
        self.addCleanup(self.h.cleanup)

    # ── basics ──────────────────────────────────────────────────────────
    def test_version(self):
        r = self.h.run("version")
        self.assertEqual(r.returncode, 0)
        self.assertIn("termi 0.1.0", r.stdout)

    def test_packs_lists_fixture(self):
        r = self.h.run("packs")
        self.assertEqual(r.returncode, 0)
        for name in ("testpack", "alpha", "beta", "gamma"):
            self.assertIn(name, r.stdout)

    # ── doctor honesty (ORACLE P7, I4) ──────────────────────────────────
    def test_doctor_three_states_and_exit_code(self):
        r = self.h.run("doctor")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)  # gamma lies
        self.assertIn("alpha", r.stdout)
        self.assertIn("not installed", r.stdout)          # beta
        self.assertIn("installed, not active", r.stdout)  # gamma

    # ── install & managed block (ORACLE ADR-3, P4, P9) ──────────────────
    def test_install_creates_block_and_snippet(self):
        r = self.h.run("install", "testpack/alpha", "--yes")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        text = self.h.zshrc.read_text()
        self.assertEqual(text.count(MARK_BEGIN), 1)
        self.assertTrue((self.h.termi_dir / "zsh.d" / "10-alpha.zsh").exists())
        self.assertTrue((self.h.termi_dir / "termi.zsh").exists())
        # the whole chain works: a real interactive zsh now activates alpha
        d = self.h.run("doctor")
        self.assertRegex(d.stdout, r"alpha\s+active")

    def test_install_idempotent(self):
        self.h.run("install", "testpack/alpha", "--yes")
        before = self.h.zshrc.read_text()
        r = self.h.run("install", "testpack/alpha", "--yes")
        self.assertEqual(r.returncode, 0)
        self.assertIn("already active", r.stdout)
        self.assertEqual(self.h.zshrc.read_text(), before)  # P9: no-op

    def test_I2_user_content_never_altered(self):
        original = ("# my precious config\nalias ll='ls -la'\n"
                    "export EDITOR=nvim\nsetopt autocd\n")
        self.h.zshrc.write_text(original)
        sha_before = hashlib.sha256(original.encode()).hexdigest()
        self.h.run("install", "testpack/alpha", "--yes")
        after = strip_block(self.h.zshrc.read_text()).replace("\n\n", "\n", 1)
        # user lines must survive byte-identical inside the stripped text
        self.assertIn(original.rstrip("\n"), self.h.zshrc.read_text())
        sha_after = hashlib.sha256(
            (original.rstrip("\n") + "\n").encode()).hexdigest()
        self.assertEqual(sha_before, sha_after)

    # ── snapshots & undo (ORACLE I3) ────────────────────────────────────
    def test_undo_restores_fresh_home_to_no_file(self):
        self.h.run("install", "testpack/alpha", "--yes")
        self.assertTrue(self.h.zshrc.exists())
        r = self.h.run("undo")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse(self.h.zshrc.exists())
        self.assertFalse((self.h.termi_dir / "zsh.d").exists())

    def test_undo_restores_existing_zshrc_bytes(self):
        original = "# mine\nalias g=git\n"
        self.h.zshrc.write_text(original)
        self.h.run("install", "testpack/alpha", "--yes")
        self.assertNotEqual(self.h.zshrc.read_text(), original)
        self.h.run("undo")
        self.assertEqual(self.h.zshrc.read_text(), original)

    # ── symlinked zshrc (ORACLE P3) ─────────────────────────────────────
    def test_symlink_zshrc_preserved(self):
        real = self.h.home / "dotfiles" / "zshrc"
        real.parent.mkdir()
        real.write_text("# dotfiles-managed\n")
        self.h.zshrc.symlink_to(real)
        r = self.h.run("install", "testpack/alpha", "--yes")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(self.h.zshrc.is_symlink())      # never replaced
        self.assertIn(MARK_BEGIN, real.read_text())     # target edited
        self.assertIn("symlink", r.stderr)              # warned, on stderr

    # ── profile export/import (ORACLE P11, R1, R7) ──────────────────────
    def test_export_lists_active_tools_and_screens_secrets(self):
        self.h.zshrc.write_text(
            "alias ok=1\nexport GITHUB_TOKEN=ghp_abc123\n")
        self.h.run("install", "testpack/alpha", "--yes")   # make alpha active
        r = self.h.run("export", "--include-zshrc")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('id = "testpack/alpha"', r.stdout)   # active tool exported
        self.assertNotIn("testpack/gamma", r.stdout)       # liar not exported
        self.assertNotIn("ghp_abc123", r.stdout)           # R7: secret stays home
        self.assertIn("screened out", r.stderr)            # notice, NOT in profile
        self.assertIn("alias ok=1", r.stdout)

    def test_import_untrusted_requires_typed_yes(self):
        profile = self.h.home / "friend.toml"
        profile.write_text(
            '[[tool]]\nid = "testpack/alpha"\n'
            '[zshrc_extra]\ncontent = """\nalias evil=whoami\n"""\n')
        # decline (empty input) → nothing adopted
        r = self.h.run("import", str(profile), input_text="\n")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("UNTRUSTED", r.stdout)
        self.assertFalse(
            (self.h.termi_dir / "zsh.d" / "90-imported-extra.zsh").exists())
        # 'y' is NOT enough (P11: typed yes only)
        self.h.run("import", str(profile), input_text="y\n")
        self.assertFalse(
            (self.h.termi_dir / "zsh.d" / "90-imported-extra.zsh").exists())
        # explicit yes → adopted
        self.h.run("import", str(profile), input_text="yes\n")
        adopted = self.h.termi_dir / "zsh.d" / "90-imported-extra.zsh"
        self.assertTrue(adopted.exists())
        self.assertIn("alias evil=whoami", adopted.read_text())

    # ── auto-recover (F2 · ADR-8) ───────────────────────────────────────
    def test_suggest_catches_transpositions(self):
        r = self.h.run("_suggest", "gti")      # difflib alone misses this
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "git")

    def test_suggest_stays_silent_on_garbage(self):
        r = self.h.run("_suggest", "qqzzxxqqzz")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout.strip(), "")

    def test_suggest_refuses_real_commands(self):
        r = self.h.run("_suggest", "git")      # not a typo → no suggestion
        self.assertEqual(r.returncode, 1)

    def test_recover_snippet_is_valid_zsh(self):
        import tomllib
        pack = tomllib.loads(
            (REPO / "packs" / "recover.toml").read_text())
        snippet = pack["item"][0]["snippet"]
        f = self.h.home / "snippet.zsh"
        f.write_text(snippet)
        r = subprocess.run(["zsh", "-n", str(f)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_snippet_only_item_installs(self):
        """Regression 2026-07-13: an item with a snippet but no brew/apt was
        wrongly reported 'unavailable on this OS' — it silently killed the keys
        and recover packs. Shell-native items need no package manager."""
        r = self.h.run("install", "testpack/delta", "--yes")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("unavailable", r.stdout)
        self.assertIn("installed ✓", r.stdout)
        self.assertTrue((self.h.termi_dir / "zsh.d" / "60-delta.zsh").exists())
        d = self.h.run("doctor")
        self.assertRegex(d.stdout, r"delta\s+active")

    def test_real_packs_shell_native_items_are_installable(self):
        """The shipped keys/recover items must never regress to 'unavailable'."""
        import tomllib
        for pack in ("keys", "recover"):
            data = tomllib.loads((REPO / "packs" / f"{pack}.toml").read_text())
            for item in data["item"]:
                self.assertTrue(
                    item.get("snippet") or item.get("brew") or item.get("apt"),
                    f"{pack}/{item['name']} has no way to install")

    # ── keys / F16 (ADR-9) ──────────────────────────────────────────────
    def _keys_snippet(self) -> str:
        import tomllib
        pack = tomllib.loads((REPO / "packs" / "keys.toml").read_text())
        return pack["item"][0]["snippet"]

    def test_keys_snippet_is_valid_zsh(self):
        f = self.h.home / "keys.zsh"
        f.write_text(self._keys_snippet())
        r = subprocess.run(["zsh", "-n", str(f)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_keys_snippet_binds_and_defines_widgets_in_real_zsh(self):
        """Load it in an interactive zsh and interrogate ZLE itself."""
        f = self.h.home / "keys.zsh"
        f.write_text(self._keys_snippet())
        script = (
            f"source {f}\n"
            "bindkey | grep -q '\\^\\[\\[1;3D. backward-word' && print BIND_WORD_LEFT\n"
            "bindkey | grep -q '\\^\\[\\[1;3C. forward-word'  && print BIND_WORD_RIGHT\n"
            "bindkey | grep -q '\\^\\[\\^?. backward-kill-word' && print BIND_DEL_WORD\n"
            "bindkey | grep -q '\\^\\[\\[1;4D. _termi_sel_backward_word' && print BIND_SEL_WORD\n"
            "(( $+functions[_termi_sel] )) && print FN_SEL\n"
            "zle -l | grep -q '^_termi_sel_backward_word$' && print WIDGET_SEL_WORD\n"
            "zle -l | grep -q '^_termi_backspace$' && print WIDGET_BACKSPACE\n"
            # select-word-style bash works via zstyle word-chars '' + the -match
            # widgets (NOT $WORDCHARS) — that's what makes / - . break words.
            "zstyle -L ':zle:*' | grep -q \"word-chars ''\" && print WORD_CHARS_EMPTY\n"
            "zle -l | grep -q 'backward-word (backward-word-match)' && print WORD_MATCH\n"
        )
        r = subprocess.run(["zsh", "-ic", script], capture_output=True, text=True,
                           env={**os.environ, "ZDOTDIR": str(self.h.home)}, timeout=30)
        for token in ("BIND_WORD_LEFT", "BIND_WORD_RIGHT", "BIND_DEL_WORD",
                      "BIND_SEL_WORD", "FN_SEL", "WIDGET_SEL_WORD",
                      "WIDGET_BACKSPACE", "WORD_CHARS_EMPTY", "WORD_MATCH"):
            self.assertIn(token, r.stdout, f"missing {token}\n{r.stdout}\n{r.stderr}")

    def test_keys_never_rebinds_plain_keys(self):
        """A terminal sending a plain key for a modified combo must be REFUSED."""
        termi = load_termi()
        for plain in (b"\x1b[D", b"\x1b[C", b"\x7f", b"\r", b"", b"\x03", b" "):
            self.assertFalse(termi.learnable(plain), f"would clobber {plain!r}")
        for good in (b"\x1b[1;3D", b"\x1b\x7f", b"\x1b[1;4C", b"\x17"):
            self.assertTrue(termi.learnable(good), f"should accept {good!r}")

    def test_zsh_quote_seq_roundtrips_through_real_zsh(self):
        """The literal we write must make zsh see the exact original bytes."""
        termi = load_termi()
        for seq in (b"\x1b[1;3D", b"\x1b\x7f", b"\x1bb", b"\x1b[1;4C"):
            lit = termi.zsh_quote_seq(seq)
            r = subprocess.run(
                ["zsh", "-c", f"printf '%s' {lit} | xxd -p"],
                capture_output=True, text=True)
            self.assertEqual(r.stdout.strip(), seq.hex(), f"{lit} != {seq!r}")

    def test_keys_status_reports_emulator_and_tips(self):
        r = self.h.run("keys")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("terminal:", r.stdout)
        self.assertIn("emulator half", r.stdout)

    def test_pack_update_propagates_to_installed_snippet(self):
        """Upgrade path (2026-07-13): editing a pack must reach users on the next
        install run — 'already active' used to skip the rewrite forever."""
        packs = self.h.home / "packs-live"
        shutil.copytree(FIXTURES, packs)
        self.h.run("install", "testpack/alpha", "--yes", packs_dir=packs)
        toml_f = packs / "testpack.toml"
        toml_f.write_text(toml_f.read_text().replace(
            "export TERMI_TEST_ALPHA=1", "export TERMI_TEST_ALPHA=2"))
        r2 = self.h.run("install", "testpack/alpha", "--yes", packs_dir=packs)
        self.assertIn("snippet refreshed", r2.stdout)
        self.assertIn("TERMI_TEST_ALPHA=2",
                      (self.h.termi_dir / "zsh.d" / "10-alpha.zsh").read_text())
        # and a THIRD run with the same pack is a clean no-op again
        r3 = self.h.run("install", "testpack/alpha", "--yes", packs_dir=packs)
        self.assertIn("already active", r3.stdout)

    def test_refresh_never_creates_a_file_for_foreign_active_items(self):
        """Active via zinit (no termi snippet file) → refresh must NOT write one."""
        r = self.h.run("doctor")  # alpha inactive → install normally first
        self.h.run("install", "testpack/gamma", "--yes")  # gamma: no snippet
        self.assertFalse((self.h.termi_dir / "zsh.d" / "50-gamma.zsh").exists())

    # ── keys apply: the EMULATOR half (ADR-10) ──────────────────────────
    def _apply_env(self, emu_file: Path):
        """Run `termi keys apply` against a fake wezterm config path."""
        termi = load_termi()
        termi.TERMI_DIR = self.h.termi_dir
        termi.ZSHD = self.h.termi_dir / "zsh.d"
        termi.SNAPS = self.h.termi_dir / "snapshots"
        termi.STATE = self.h.termi_dir / "state.json"
        termi.LOADER = self.h.termi_dir / "termi.zsh"
        termi.ZSHRC = self.h.zshrc
        termi.EMULATOR_CONFIG = {
            "wezterm": (emu_file, termi.LUA_BLOCK, "--")}
        return termi

    def test_keys_apply_creates_wezterm_config(self):
        cfg = self.h.home / ".wezterm.lua"
        termi = self._apply_env(cfg)
        self.assertEqual(termi.cmd_keys_apply("wezterm"), 0)
        text = cfg.read_text()
        self.assertIn(">>> termi >>>", text)
        self.assertIn("LeftArrow", text)
        self.assertIn("\\x1b[H", text)
        self.assertTrue(text.rstrip().endswith("return config"))  # block before return

    def test_keys_apply_is_idempotent(self):
        cfg = self.h.home / ".wezterm.lua"
        termi = self._apply_env(cfg)
        termi.cmd_keys_apply("wezterm")
        first = cfg.read_text()
        termi.cmd_keys_apply("wezterm")
        self.assertEqual(cfg.read_text(), first)
        self.assertEqual(first.count(">>> termi >>>"), 1)

    def test_keys_apply_injects_before_return_in_existing_config(self):
        cfg = self.h.home / ".wezterm.lua"
        cfg.write_text("local wezterm = require 'wezterm'\n"
                       "local cfg = wezterm.config_builder()\n"
                       "cfg.font_size = 14\n"
                       "return cfg\n")
        termi = self._apply_env(cfg)
        self.assertEqual(termi.cmd_keys_apply("wezterm"), 0)
        text = cfg.read_text()
        self.assertIn("cfg.font_size = 14", text)          # their setting survives
        self.assertIn("cfg.keys = cfg.keys or {}", text)   # retargeted to THEIR var
        self.assertLess(text.index(">>> termi >>>"), text.index("return cfg"))

    def test_keys_apply_injects_before_the_LAST_return(self):
        """An early `return` inside a helper function must not attract the block."""
        cfg = self.h.home / ".wezterm.lua"
        cfg.write_text("local wezterm = require 'wezterm'\n"
                       "local cfg = wezterm.config_builder()\n"
                       "local function pick(x)\n"
                       "  return x\n"
                       "end\n"
                       "cfg.font_size = pick(14)\n"
                       "return cfg\n")
        termi = self._apply_env(cfg)
        self.assertEqual(termi.cmd_keys_apply("wezterm"), 0)
        text = cfg.read_text()
        self.assertLess(text.index("return x"), text.index(">>> termi >>>"),
                        "block landed inside the helper function")
        self.assertLess(text.index(">>> termi >>>"), text.index("return cfg"))

    def test_keys_apply_undo_removes_a_config_it_created(self):
        cfg = self.h.home / ".wezterm.lua"
        termi = self._apply_env(cfg)
        termi.cmd_keys_apply("wezterm")
        self.assertTrue(cfg.exists())
        termi._lock_fh = None
        termi.cmd_undo(None)
        self.assertFalse(cfg.exists(), "undo must delete a config termi created")

    def test_keys_apply_undo_restores_a_preexisting_config(self):
        cfg = self.h.home / ".wezterm.lua"
        original = ("local wezterm = require 'wezterm'\n"
                    "local config = wezterm.config_builder()\n"
                    "config.font_size = 99\n"
                    "return config\n")
        cfg.write_text(original)
        termi = self._apply_env(cfg)
        termi.cmd_keys_apply("wezterm")
        self.assertNotEqual(cfg.read_text(), original)
        termi._lock_fh = None
        termi.cmd_undo(None)
        self.assertEqual(cfg.read_text(), original)  # byte-exact

    def test_keys_probe_refuses_without_tty(self):
        r = self.h.run("keys", "probe")
        self.assertEqual(r.returncode, 1)
        self.assertIn("needs a real terminal", r.stderr)

    # ── lock (ORACLE P8) ────────────────────────────────────────────────
    def test_second_termi_refuses_lock(self):
        import fcntl
        self.h.termi_dir.mkdir(parents=True, exist_ok=True)
        with open(self.h.termi_dir / "lock", "w") as fh:
            fcntl.flock(fh, fcntl.LOCK_EX)
            r = self.h.run("undo")
            self.assertEqual(r.returncode, 3)
            self.assertIn("another termi", r.stderr)


if __name__ == "__main__":
    unittest.main()
