#!/usr/bin/env python3
"""Inject seed.json into template.html and write board.html, the page Claude Code publishes.
Run from board/: python3 build_seed.py && python3 build_board.py"""
import json, re, subprocess, sys
from pathlib import Path
here = Path(__file__).resolve().parent
seed = json.loads((here / "seed.json").read_text())
blob = json.dumps(seed, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
def _leak_words():
    p = Path.home() / ".musterout" / "leak_words.txt"
    if not p.exists():
        print("leak guard skipped: no private word list at ~/.musterout/leak_words.txt")
        return []
    return [w for w in p.read_text(encoding="utf-8").splitlines() if w]
tpl = (here / "template.html").read_text()
assert "/*SEED*/" in tpl and "MUSTEROUT_PATCHED" in tpl
out = tpl.replace("/*SEED*/", blob)
for d in (chr(0x2014), chr(0x2013)):
    if d in out: sys.exit("dash found in page")
# The exact, source-verified enlisted counseling quote uses generic pronouns.
privacy_text = out.replace('Counsel the Marine concerning his or her potential for recall to active duty and/or mobilization.', '')
for bad in _leak_words():
    if bad in privacy_text: sys.exit(f"personal string in page: {bad}")
(here / "board.html").write_text(out)
# syntax check the inline script
js = re.findall(r"<script>(.*?)</script>", out, re.S)[-1]
chk = here / "_dev" / "_board_check.js"; chk.write_text(js)
r = subprocess.run(["node", "--check", str(chk)], capture_output=True, text=True)
chk.unlink()
if r.returncode: sys.exit("script does not parse:\n" + r.stderr)
print(f"board.html {len(out)//1024} KB, script parses")
