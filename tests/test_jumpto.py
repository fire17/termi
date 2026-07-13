"""jumpto (F17) — the matcher, and the interactive mode driven through a real pty."""

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


def snippet(pack: str, item: int = 0) -> str:
    data = tomllib.loads((REPO / "packs" / f"{pack}.toml").read_text())
    return data["item"][item]["snippet"]


class MatcherTest(unittest.TestCase):
    """_termi_jump_matches runs per keystroke — it must be right AND fork-free."""

    def match(self, buffer: str, query: str) -> list[str]:
        script = (
            f"{snippet('jumpto')}\n"
            f'_termi_jump_matches "{buffer}" "{query}"\n'
            'print -l -- "${_termi_jm_out[@]}"\n'
        )
        r = subprocess.run(["zsh", "-fc", script], capture_output=True, text=True,
                           timeout=30)
        self.assertEqual(r.returncode, 0, r.stderr)
        return [ln for ln in r.stdout.splitlines() if ln.strip()]

    def test_exact_substring(self):
        # "git commit -m wip"  → "commit" starts at 4, ends at 10
        self.assertEqual(self.match("git commit -m wip", "commit"), ["4 10"])

    def test_case_insensitive(self):
        self.assertEqual(self.match("Git COMMIT", "commit"), ["4 10"])
        self.assertEqual(self.match("git commit", "COMMIT"), ["4 10"])

    def test_every_occurrence_is_returned_in_order(self):
        self.assertEqual(self.match("foo bar foo baz foo", "foo"),
                         ["0 3", "8 11", "16 19"])

    def test_fuzzy_only_when_no_exact_match(self):
        # "cmt" isn't a substring of "git commit" → fuzzy: c…m…t
        got = self.match("git commit", "cmt")
        self.assertTrue(got, "fuzzy should have matched c-m-t")
        start, end = got[0].split()
        self.assertEqual(int(start), 4)          # anchors on the 'c' of commit
        self.assertGreater(int(end), int(start))

    def test_exact_beats_fuzzy(self):
        # 'ab' exists literally, so we must NOT return scattered fuzzy anchors
        self.assertEqual(self.match("xab a-b", "ab"), ["1 3"])

    def test_no_match_returns_nothing(self):
        self.assertEqual(self.match("hello", "zzz"), [])

    def test_empty_query_returns_nothing(self):
        self.assertEqual(self.match("hello", ""), [])

    def test_matcher_does_not_fork(self):
        """It runs on every keystroke — a fork here would be felt.
        NB: $((arith)) is not a fork; only $( cmd ) and backticks are."""
        import re as _re
        src = snippet("jumpto")
        body = src[src.index("_termi_jump_matches()"):src.index("_termi_jump_csi()")]
        self.assertIsNone(_re.search(r"\$\((?!\()", body),
                          "matcher must not use command substitution")
        for forky in ("`", "grep", "sed", "awk", "python", "tr "):
            self.assertNotIn(forky, body, f"matcher must not shell out to {forky}")


class JumptoPtyTest(unittest.TestCase):
    """Drive jumpto for real: press ⌘⌥→, type a query, and ask ZLE where it went."""

    def setUp(self):
        self.work = Path(tempfile.mkdtemp(prefix="termi-jump-"))
        self.addCleanup(shutil.rmtree, self.work, True)
        self.out = self.work / "probe.out"
        (self.work / "k.zsh").write_text(snippet("keys"))
        (self.work / "j.zsh").write_text(snippet("jumpto"))
        (self.work / ".zshrc").write_text(
            f"source {self.work}/k.zsh\nsource {self.work}/j.zsh\n"
            f'_termi_probe() {{ print -r -- "[$BUFFER]|$CURSOR" >! {self.out} }}\n'
            "zle -N _termi_probe\nbindkey '^T' _termi_probe\nPS1='> '\n"
        )

    def _drain(self, fd, t=0.5):
        end = time.time() + t
        while time.time() < end:
            if select.select([fd], [], [], 0.1)[0]:
                try:
                    if not os.read(fd, 65536):
                        return
                except OSError:
                    return

    def jump(self, text: bytes, keys: bytes, env=None) -> str:
        if self.out.exists():
            self.out.unlink()
        pid, fd = pty.fork()
        if pid == 0:
            os.environ.update({"TERM": "xterm-256color", "ZDOTDIR": str(self.work),
                               "HOME": str(self.work), **(env or {})})
            os.execvp("zsh", ["zsh", "-i"])
        try:
            self._drain(fd, 2.0)
            os.write(fd, text)
            self._drain(fd, 0.5)
            for k in keys:
                os.write(fd, bytes([k]))
                time.sleep(0.05)
            self._drain(fd, 0.6)
            os.write(fd, b"\x14")     # ctrl-T → dump ZLE state
            self._drain(fd, 0.8)
            os.write(fd, b"\x03")
            time.sleep(0.2)
        finally:
            os.close(fd)
            os.waitpid(pid, 0)
        self.assertTrue(self.out.exists(), "ZLE probe never fired")
        return self.out.read_text().strip()

    FWD = b"\x1b[1;7C"
    BACK = b"\x1b[1;7D"

    def test_jump_forward_to_a_word(self):
        # cursor at end; ⌘⌥← searches BACK for "commit"; ↵ accepts → cursor on it
        got = self.jump(b"git commit -m wip", self.BACK + b"commit\r")
        self.assertEqual(got, "[git commit -m wip]|4")

    def test_jump_is_case_insensitive(self):
        got = self.jump(b"git COMMIT -m wip", self.BACK + b"commit\r")
        self.assertEqual(got, "[git COMMIT -m wip]|4")

    def test_jump_is_fuzzy(self):
        # "cmt" → fuzzy-matches c-o-m-m-i-t
        got = self.jump(b"git commit -m wip", self.BACK + b"cmt\r")
        self.assertEqual(got, "[git commit -m wip]|4")

    def test_forward_search_from_line_start(self):
        # go home first (\e[H), then ⌘⌥→ forward to "wip"
        got = self.jump(b"git commit -m wip", b"\x1b[H" + self.FWD + b"wip\r")
        self.assertEqual(got, "[git commit -m wip]|14")

    def test_ctrl_n_walks_to_the_next_match(self):
        # back-search "foo" from the end: nearest is the LAST foo (16); ⌃N → 8
        got = self.jump(b"foo bar foo baz foo", self.BACK + b"foo\x0e\r")
        self.assertEqual(got, "[foo bar foo baz foo]|8")

    def test_escape_cancels_and_restores_the_cursor(self):
        got = self.jump(b"git commit -m wip", self.BACK + b"commit\x1b")
        self.assertEqual(got, "[git commit -m wip]|17")   # back at the end

    def test_backspace_refines_the_query(self):
        # type "commitX" (no match), backspace → "commit" matches again
        got = self.jump(b"git commit -m wip", self.BACK + b"commitX\x7f\r")
        self.assertEqual(got, "[git commit -m wip]|4")

    def test_jumpto_can_be_switched_off(self):
        # TERMI_JUMPTO=0 → the widget declines: cursor unmoved, buffer untouched.
        # (No Enter here — Enter would EXECUTE the line, not probe it.)
        got = self.jump(b"git commit", self.BACK, env={"TERMI_JUMPTO": "0"})
        self.assertEqual(got, "[git commit]|10")

    def test_off_switch_does_not_leak_the_escape_sequence_into_the_buffer(self):
        got = self.jump(b"echo hi", self.BACK, env={"TERMI_JUMPTO": "0"})
        self.assertEqual(got, "[echo hi]|7")   # no stray ";7D" text

    def test_typing_after_jump_edits_at_the_new_spot(self):
        got = self.jump(b"git commit -m wip", self.BACK + b"wip\rZ")
        self.assertEqual(got, "[git commit -m Zwip]|15")


if __name__ == "__main__":
    unittest.main()
