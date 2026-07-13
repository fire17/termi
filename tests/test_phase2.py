"""Phase 2 battery — multi-shell, registries, env, skill install, TUI, budgets.

Real shells only: bash/fish/pwsh tests skip honestly when a shell is absent.
Every `verified` claim in support/shells.toml is expected to have a test here.
"""

import json
import os
import pty
import select
import shutil
import subprocess
import tempfile
import time
import tomllib
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TERMI = REPO / "bin" / "termi"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

HAVE = {s: bool(shutil.which(s)) for s in ("bash", "fish", "pwsh", "zsh")}


class P2Home:
    def __init__(self):
        self.home = Path(tempfile.mkdtemp(prefix="termi-p2-"))

    def env(self, **extra):
        e = dict(os.environ)
        e.update(HOME=str(self.home), TERMI_DIR=str(self.home / ".termi"),
                 TERMI_ZSHRC=str(self.home / ".zshrc"),
                 TERMI_PACKS_DIR=str(extra.pop("packs_dir", FIXTURES)),
                 NO_COLOR="1", ZDOTDIR=str(self.home), **extra)
        return e

    def run(self, *args, input_text=None, timeout=90, **envkw):
        return subprocess.run(["python3", str(TERMI), *args], capture_output=True,
                              text=True, env=self.env(**envkw),
                              input=input_text, timeout=timeout)

    def cleanup(self):
        shutil.rmtree(self.home, ignore_errors=True)


class RegistryTest(unittest.TestCase):
    def test_all_shell_entries_carry_required_fields(self):
        data = tomllib.loads((REPO / "support/shells.toml").read_text())
        for s in data["shell"]:
            for field in ("id", "name", "detect", "rc", "dir", "ext",
                          "loader_file", "block", "loader", "features"):
                self.assertIn(field, s, f"{s.get('id')} missing {field}")
            for feat, status in s["features"].items():
                self.assertIn(status, ("verified", "native", "core", "planned",
                                       "untested"), f"{s['id']}.{feat}={status}")

    def test_terminal_and_harness_registries_load(self):
        t = tomllib.loads((REPO / "support/terminals.toml").read_text())["terminal"]
        h = tomllib.loads((REPO / "support/harnesses.toml").read_text())["harness"]
        self.assertGreaterEqual(len(t), 8)
        self.assertGreaterEqual(len(h), 6)
        self.assertTrue(all("skills_dir" in x and "detect" in x for x in h))

    def test_extensibility_new_shell_is_additive_toml_only(self):
        """BUDGETS row 'easily extend': a new shell = a TOML entry, zero code."""
        h = P2Home()
        self.addCleanup(h.cleanup)
        sup = h.home / "support"
        shutil.copytree(REPO / "support", sup)
        with open(sup / "shells.toml", "a") as f:
            f.write('\n[[shell]]\nid = "fakeshell"\nname = "FakeShell"\n'
                    'detect = "true"\nrc = "~/.fakerc"\ncomment = "#"\n'
                    'dir = "fake.d"\next = ".fake"\nloader_file = "termi.fake"\n'
                    'block = "source ~/.termi/termi.fake"\nloader = "# fake\\n"\n'
                    '[shell.features]\nblock = "planned"\n')
        r = h.run("env", "--json", TERMI_SUPPORT_DIR=str(sup))
        self.assertEqual(r.returncode, 0, r.stderr)
        env = json.loads(r.stdout)
        self.assertIn("fakeshell", env["shells"])
        self.assertTrue(env["shells"]["fakeshell"]["present"])
        # and it can be enabled — block lands in its rc
        r2 = h.run("shells", "enable", "fakeshell", TERMI_SUPPORT_DIR=str(sup))
        self.assertEqual(r2.returncode, 0, r2.stderr)
        self.assertIn(">>> termi >>>", (h.home / ".fakerc").read_text())


class MultiShellTest(unittest.TestCase):
    def setUp(self):
        self.h = P2Home()
        self.addCleanup(self.h.cleanup)

    def test_env_json_shape(self):
        r = self.h.run("env", "--json")
        env = json.loads(r.stdout)
        for k in ("os", "terminal", "current_shell", "shells", "harnesses", "mux"):
            self.assertIn(k, env)
        self.assertIn("zsh", env["shells"])

    @unittest.skipUnless(HAVE["bash"], "bash not installed")
    def test_bash_enable_block_loader_and_live_marker(self):
        r = self.h.run("shells", "enable", "bash")
        self.assertEqual(r.returncode, 0, r.stderr)
        rc = self.h.home / ".bashrc"
        self.assertIn(">>> termi >>>", rc.read_text())
        probe = subprocess.run(
            ["bash", "-ic", "echo TERMIA:$TERMI_ACTIVE"], capture_output=True,
            text=True, env=self.h.env(TERMI_ACTIVE=""), timeout=30)
        self.assertIn("TERMIA:bash", probe.stdout)

    @unittest.skipUnless(HAVE["fish"], "fish not installed")
    def test_fish_enable_block_loader_and_live_marker(self):
        r = self.h.run("shells", "enable", "fish")
        self.assertEqual(r.returncode, 0, r.stderr)
        rc = self.h.home / ".config/fish/config.fish"
        self.assertIn(">>> termi >>>", rc.read_text())
        probe = subprocess.run(
            ["fish", "-ic", "echo TERMIA:$TERMI_ACTIVE"], capture_output=True,
            text=True, env=self.h.env(TERMI_ACTIVE=""), timeout=30)
        self.assertIn("TERMIA:fish", probe.stdout)

    @unittest.skipUnless(HAVE["pwsh"], "pwsh not installed")
    def test_powershell_enable_block_loader_and_live_marker(self):
        r = self.h.run("shells", "enable", "powershell")
        self.assertEqual(r.returncode, 0, r.stderr)
        rc = self.h.home / ".config/powershell/Microsoft.PowerShell_profile.ps1"
        self.assertIn(">>> termi >>>", rc.read_text())
        probe = subprocess.run(
            ["pwsh", "-Command", 'Write-Output "TERMIA:$env:TERMI_ACTIVE"'],
            capture_output=True, text=True, env=self.h.env(TERMI_ACTIVE=""),
            timeout=60)
        self.assertIn("TERMIA:powershell", probe.stdout)

    @unittest.skipUnless(HAVE["bash"], "bash not installed")
    def test_bash_recover_variant_suggests_and_falls_through(self):
        self.h.run("shells", "enable", "bash")
        pk = self.h.home / "packs"
        shutil.copytree(REPO / "packs", pk)
        r = self.h.run("install", "recover", "--shell", "bash", "--yes",
                       packs_dir=pk)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        env = self.h.env(TERMI_ACTIVE="")
        env["PATH"] = f"{REPO / 'bin'}:{env['PATH']}"
        out = subprocess.run(["bash", "-ic", "gti status"], capture_output=True,
                             text=True, env=env, timeout=60)
        self.assertIn("did you mean", out.stdout + out.stderr)

    @unittest.skipUnless(HAVE["pwsh"], "pwsh not installed")
    def test_pwsh_recover_variant_suggests(self):
        self.h.run("shells", "enable", "powershell")
        pk = self.h.home / "packs"
        shutil.copytree(REPO / "packs", pk)
        self.h.run("install", "recover", "--shell", "powershell", "--yes",
                   packs_dir=pk)
        env = self.h.env(TERMI_ACTIVE="")
        env["PATH"] = f"{REPO / 'bin'}:{env['PATH']}"
        out = subprocess.run(["pwsh", "-Command", "gti"], capture_output=True,
                             text=True, env=env, timeout=60)
        self.assertIn("did you mean", out.stdout + out.stderr)

    @unittest.skipUnless(HAVE["bash"], "bash not installed")
    def test_undo_restores_bash_rc_and_dir(self):
        rc = self.h.home / ".bashrc"
        rc.write_text("# mine\nalias g=git\n")
        self.h.run("shells", "enable", "bash")
        self.assertIn(">>> termi >>>", rc.read_text())
        r = self.h.run("undo")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(rc.read_text(), "# mine\nalias g=git\n")

    def test_shells_disable_removes_block_keeps_snippets(self):
        self.h.run("shells", "enable", "bash")
        d = self.h.home / ".termi/bash.d"
        d.mkdir(parents=True, exist_ok=True)
        (d / "50-x.bash").write_text("# keepme\n")
        r = self.h.run("shells", "disable", "bash")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn(">>> termi >>>", (self.h.home / ".bashrc").read_text())
        self.assertTrue((d / "50-x.bash").exists())


class SkillInstallTest(unittest.TestCase):
    def setUp(self):
        self.h = P2Home()
        self.addCleanup(self.h.cleanup)
        self.sup = self.h.home / "support"
        shutil.copytree(REPO / "support", self.sup)
        fake = self.h.home / "fake-harness/skills"
        fake.mkdir(parents=True)
        (self.sup / "harnesses.toml").write_text(
            f'[[harness]]\nid = "fakeh"\nname = "Fake"\ndetect = "true"\n'
            f'skills_dir = "{fake}"\ndir_status = "verified"\n'
            f'[[harness]]\nid = "ghost"\nname = "Ghost"\ndetect = "true"\n'
            f'skills_dir = "{self.h.home}/nope/skills"\ndir_status = "guessed"\n')
        self.fake = fake

    def test_skill_installs_into_verified_dir_and_skips_guessed(self):
        r = self.h.run("skill", "install", "--yes",
                       TERMI_SUPPORT_DIR=str(self.sup))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((self.fake / "termi/SKILL.md").exists())
        self.assertIn("skipped — skills dir is a guess", r.stdout)
        self.assertFalse((self.h.home / "nope").exists())

    def test_force_dir_creates_guessed(self):
        r = self.h.run("skill", "install", "--yes", "--force-dir",
                       TERMI_SUPPORT_DIR=str(self.sup))
        self.assertTrue((self.h.home / "nope/skills/termi/SKILL.md").exists(),
                        r.stdout + r.stderr)


class TuiSmokeTest(unittest.TestCase):
    def _drive(self, keys_after_render):
        h = P2Home()
        self.addCleanup(h.cleanup)
        pid, fd = pty.fork()
        if pid == 0:
            os.environ.update(h.env())
            os.execvp("python3", ["python3", str(TERMI), "tui"])
        out = b""
        wrote = False
        end = time.time() + 30
        while time.time() < end:
            if not select.select([fd], [], [], 0.25)[0]:
                continue
            try:
                chunk = os.read(fd, 65536)
            except OSError:
                break  # child exited (EIO on macOS pty)
            if not chunk:
                break
            out += chunk
            if b"control center" in out and not wrote:
                wrote = True
                for k in keys_after_render:
                    time.sleep(0.35)
                    os.write(fd, k)
        os.close(fd)
        _, status = os.waitpid(pid, 0)
        return wrote, os.waitstatus_to_exitcode(status), out

    def test_tui_renders_and_quits_clean(self):
        wrote, code, out = self._drive([b"q"])
        self.assertTrue(wrote, f"TUI never rendered: {out[-300:]!r}")
        self.assertEqual(code, 0, out[-300:])

    def test_tui_navigation_does_not_crash(self):
        wrote, code, out = self._drive([b"\x1b[B", b"\x1b[B", b"\x1b[A", b"q"])
        self.assertTrue(wrote)
        self.assertEqual(code, 0, out[-300:])


class BudgetTest(unittest.TestCase):
    def test_env_shallow_meets_budget(self):
        h = P2Home()
        self.addCleanup(h.cleanup)
        t0 = time.time()
        r = h.run("env")
        wall = time.time() - t0
        self.assertEqual(r.returncode, 0)
        self.assertLess(wall, 1.0, f"env took {wall:.2f}s (budget 0.35s + CI slack)")


if __name__ == "__main__":
    unittest.main()
