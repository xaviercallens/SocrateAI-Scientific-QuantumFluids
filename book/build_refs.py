#!/usr/bin/env python3
"""Merge refs.bib and refs_ch*.bib into refs_all.bib, dropping duplicate keys (first definition wins; later duplicates are reported)."""
import re, glob
from pathlib import Path
here = Path(__file__).resolve().parent
files = [here / "refs.bib"] + sorted(Path(p) for p in glob.glob(str(here / "refs_ch*.bib")))
seen, out = {}, []
for f in files:
    txt = f.read_text()
    for m in re.finditer(r"@\w+\s*\{\s*([^,\s]+)\s*,", txt):
        pass
    # split on entry starts
    parts = re.split(r"(?m)^(?=@\w+\s*\{)", txt)
    for p in parts:
        m = re.match(r"@\w+\s*\{\s*([^,\s]+)\s*,", p)
        if not m: continue
        k = m.group(1)
        if k in seen: print("duplicate key", k, "in", f.name, "(kept the one from", seen[k] + ")"); continue
        seen[k] = f.name; out.append(p.rstrip() + "\n")
(here / "refs_all.bib").write_text("\n".join(out)); print(len(out), "entries ->", here / "refs_all.bib")
