"""End-to-end key proof: drive a REAL interactive zsh through a pty, press the
actual bytes a terminal sends, and ask ZLE itself what its buffer is.

Born 2026-07-13 from a live miss: unit tests said the bindings existed, but
fire17 pressed ⌥← and got `;3D` — because the pack was never installed and the
installer wrongly rejected snippet-only items. Screen-scraping also lied (the
redraw uses backspaces). Only ZLE's own $BUFFER tells the truth.
"""

import os
import pty
import select
import shutil
import tempfile
import time
import tomllib
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def keys_snippet() -> str:
    pack = tomllib.loads((REPO / "packs" / "keys.toml").read_text())
    return pack["item"][0]["snippet"]


class KeysPtyTest(unittest.TestCase):
    def setUp(self):
        self.work = Path(tempfile.mkdtemp(prefix="termi-pty-"))
        self.addCleanup(shutil.rmtree, self.work, True)
        self.out = self.work / "probe.out"
        (self.work / "keys.zsh").write_text(keys_snippet())
        # a hermetic zshrc: ONLY the keys snippet + a widget that dumps ZLE state
        (self.work / ".zshrc").write_text(
            f"source {self.work}/keys.zsh\n"
            f'_termi_probe() {{ print -r -- "[$BUFFER]|$CURSOR" >! {self.out} }}\n'
            "zle -N _termi_probe\n"
            "bindkey '^G' _termi_probe\n"
            "PS1='> '\n"
        )

    def _drain(self, fd, t=0.6):
        end = time.time() + t
        while time.time() < end:
            if select.select([fd], [], [], 0.1)[0]:
                try:
                    if not os.read(fd, 65536):
                        return
                except OSError:
                    return

    def press(self, typed: bytes, keys: bytes, then: bytes = b"X") -> str:
        """Type `typed`, send `keys`, then `then`; return ZLE's own [BUFFER]|CURSOR."""
        if self.out.exists():
            self.out.unlink()
        pid, fd = pty.fork()
        if pid == 0:  # child
            os.environ["TERM"] = "xterm-256color"
            os.environ["ZDOTDIR"] = str(self.work)
            os.environ["HOME"] = str(self.work)
            os.execvp("zsh", ["zsh", "-i"])
        try:
            self._drain(fd, 2.0)
            os.write(fd, typed)
            self._drain(fd, 0.5)
            os.write(fd, keys)
            self._drain(fd, 0.4)
            if then:
                os.write(fd, then)
                self._drain(fd, 0.4)
            os.write(fd, b"\x07")   # ctrl-G → dump ZLE buffer
            self._drain(fd, 0.8)
            os.write(fd, b"\x03")   # ctrl-C — never execute
            time.sleep(0.2)
        finally:
            os.close(fd)
            os.waitpid(pid, 0)
        self.assertTrue(self.out.exists(), "ZLE probe never fired")
        return self.out.read_text().strip()

    def test_option_left_jumps_a_word(self):
        self.assertEqual(self.press(b"hello world", b"\x1b[1;3D"), "[hello Xworld]|7")

    def test_ctrl_left_jumps_a_word(self):
        self.assertEqual(self.press(b"hello world", b"\x1b[1;5D"), "[hello Xworld]|7")

    def test_option_right_jumps_a_word(self):
        got = self.press(b"hello world", b"\x1b[1;3D\x1b[1;3D\x1b[1;3C")
        self.assertEqual(got, "[helloX world]|6")   # forward-word → end of word

    def test_option_backspace_deletes_a_word(self):
        self.assertEqual(self.press(b"hello world", b"\x1b\x7f"), "[hello X]|7")

    def test_shift_option_left_selects_and_typing_replaces(self):
        # ⇧⌥← selects "world"; typing X replaces the selection (like a real app)
        self.assertEqual(self.press(b"hello world", b"\x1b[1;4D"), "[hello X]|7")

    def test_backspace_kills_the_selection(self):
        self.assertEqual(
            self.press(b"hello world", b"\x1b[1;4D", then=b"\x7f"), "[hello ]|6")

    def test_words_break_on_slashes_in_paths(self):
        # select-word-style bash: /usr/local/bin → ⌥← stops at "bin", not the whole path
        self.assertEqual(self.press(b"cd /usr/local/bin", b"\x1b[1;3D"),
                         "[cd /usr/local/Xbin]|15")

    def test_plain_arrows_still_work(self):
        self.assertEqual(self.press(b"hello world", b"\x1b[D\x1b[D"),
                         "[hello worXld]|10")

    def test_home_end_and_line_kill(self):
        self.assertEqual(self.press(b"hello world", b"\x1b[H"), "[Xhello world]|1")
        self.assertEqual(self.press(b"hello world", b"\x01\x1b[F"), "[hello worldX]|12")

    # ── what ⌘←/⌘→/⌘⌫ actually send once the emulator is configured (ADR-10) ──
    def test_cmd_left_sequence_goes_to_line_start(self):
        # wezterm ⌘← → \e[H   (verified via `wezterm show-keys`)
        self.assertEqual(self.press(b"echo hello", b"\x1b[H"), "[Xecho hello]|1")

    def test_cmd_right_sequence_goes_to_line_end(self):
        # ⌘→ → \e[F ; start from line start so the move is observable
        self.assertEqual(self.press(b"echo hello", b"\x1b[H\x1b[F"), "[echo helloX]|11")

    def test_cmd_backspace_sequence_kills_to_line_start(self):
        # ⌘⌫ → \x15 (backward-kill-line)
        self.assertEqual(self.press(b"rm -rf /tmp/x", b"\x15", then=b"ls"), "[ls]|2")

    def test_shift_cmd_left_selects_to_line_start_and_typing_replaces(self):
        # ⇧⌘← → \e[1;2H : selects to line start, typing replaces the selection
        self.assertEqual(self.press(b"hello world", b"\x1b[1;2H"), "[X]|1")

    # ── ⇧⌘ marks whole lines (fire17's ask, 2026-07-13) ──────────────────
    def test_shift_cmd_left_marks_the_line_and_backspace_deletes_it(self):
        self.assertEqual(
            self.press(b"rm -rf /tmp/danger", b"\x1b[1;2H", then=b"\x7f"), "[]|0")

    def test_shift_cmd_right_marks_to_line_end_from_mid_line(self):
        # ⌘← (line start), ⌥→ (past "echo"), then ⇧⌘→ marks the REST of the line
        self.assertEqual(
            self.press(b"echo hello world", b"\x1b[H\x1b[1;3C\x1b[1;2F"), "[echoX]|5")

    def test_cmd_left_then_shift_cmd_right_marks_the_ENTIRE_line(self):
        # the "select the whole line" gesture: go home, then mark to the end
        self.assertEqual(
            self.press(b"git commit -m wip", b"\x1b[H\x1b[1;2F"), "[X]|1")

    def test_marked_line_survives_extending_the_selection(self):
        # ⇧⌘← marks the whole line (MARK stays at the end, cursor goes to 0);
        # a further ⇧⌥→ moves the cursor forward inside that SAME region, so the
        # selection shrinks to " beta" — correct editor behavior. Typing eats it.
        got = self.press(b"alpha beta", b"\x1b[1;2H\x1b[1;4C", then=b"Z")
        self.assertEqual(got, "[alphaZ]|6")


class RecoverChainTest(unittest.TestCase):
    """auto-recover must CHAIN onto a pre-existing command_not_found_handler,
    never clobber it and never be silently shut out by it (live bug 2026-07-13:
    fire17 had his own handler, so termi's never hooked up — and doctor lied)."""

    def setUp(self):
        self.work = Path(tempfile.mkdtemp(prefix="termi-cnf-"))
        self.addCleanup(shutil.rmtree, self.work, True)
        pack = tomllib.loads((REPO / "packs" / "recover.toml").read_text())
        (self.work / "recover.zsh").write_text(pack["item"][0]["snippet"])

    def run_zsh(self, script: str) -> str:
        import subprocess
        pre = "command_not_found_handler() { print \"PREEXISTING:$1\" }\n"
        full = pre + f"source {self.work}/recover.zsh\n" + script
        r = subprocess.run(["zsh", "-ic", full], capture_output=True, text=True,
                           env={**os.environ, "ZDOTDIR": str(self.work),
                                "PATH": os.environ["PATH"]}, timeout=60)
        return r.stdout + r.stderr

    def test_typo_gets_a_suggestion(self):
        self.assertIn("did you mean", self.run_zsh("gti status"))

    def test_unknown_command_falls_through_to_the_previous_handler(self):
        out = self.run_zsh("qqzzxxqqzznope")
        self.assertIn("PREEXISTING:qqzzxxqqzznope", out)
        self.assertNotIn("did you mean", out)

    def test_resourcing_does_not_recurse(self):
        out = self.run_zsh(
            f"source {self.work}/recover.zsh\nsource {self.work}/recover.zsh\n"
            "qqzzxxqqzznope")
        self.assertIn("PREEXISTING:qqzzxxqqzznope", out)
        self.assertNotIn("maximum nested function level", out)

    def test_active_probe_is_honest(self):
        """The probe must be FALSE when someone else owns the hook."""
        pack = tomllib.loads((REPO / "packs" / "recover.toml").read_text())
        probe = pack["item"][0]["active"]
        import subprocess
        # ours installed → probe true
        ours = subprocess.run(
            ["zsh", "-ic", f"source {self.work}/recover.zsh; {probe} && print YES"],
            capture_output=True, text=True, timeout=60)
        self.assertIn("YES", ours.stdout)
        # someone else's handler wins afterwards → probe must be false
        theirs = subprocess.run(
            ["zsh", "-ic", f"source {self.work}/recover.zsh; "
             "command_not_found_handler() { print nope }; "
             f"{probe} && print YES || print NO"],
            capture_output=True, text=True, timeout=60)
        self.assertIn("NO", theirs.stdout)


if __name__ == "__main__":
    unittest.main()
