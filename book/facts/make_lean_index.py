#!/usr/bin/env python3
"""Index of the Lean library for the book: for each module the header comment and every declaration with its statement.
    python3 book/facts/make_lean_index.py > book/facts/lean_index.md"""
import re, sys
from pathlib import Path
SRC = Path(__file__).resolve().parents[2] / "lean_src"
DECL = re.compile(r"^(?:noncomputable\s+)?(?:@\[[^\]]*\]\s*)?(theorem|lemma|def|structure|abbrev|inductive|instance)\s+([^\s:({\[]+)")
out = ["# Lean library index (auto-generated; statements truncated at `:=`)\n",
       "Namespaces: 24 of the 37 modules live in `QuantumFluids.<Module>`; the other 13 do not (table in `facts/lean_namespaces.md`). Quote theorem names exactly as written here.\n"]
n_thm = 0
for f in sorted(SRC.glob("*.lean")):
    if f.name.startswith("_tmp") or f.name in ("lakefile.lean", "QuantumFluids.lean"):
        continue
    txt = f.read_text()
    m = re.match(r"\s*/-[!\-]?(.*?)-/", txt, re.S)
    head = (m.group(1).strip() if m else "")[:2600]
    out.append(f"\n## {f.stem}\n\n```\n{head}\n```\n")
    lines = txt.split("\n"); i = 0; items = []
    while i < len(lines):
        d = DECL.match(lines[i])
        if d and not lines[i].startswith(" "):
            stmt = lines[i]; j = i
            while ":=" not in stmt and " by" not in stmt[-6:] and j + 1 < len(lines) and j - i < 8 and lines[j + 1].strip() and not DECL.match(lines[j + 1]):
                j += 1; stmt += " " + lines[j].strip()
            stmt = re.split(r":=|\bwhere\b", stmt)[0].strip()
            items.append((d.group(1), d.group(2), stmt)); i = j
        i += 1
    for kind, name, stmt in items:
        if kind in ("theorem", "lemma"): n_thm += 1
        out.append(f"- `{kind} {name}`: `{stmt[:300]}`")
out.insert(2, f"Total theorems/lemmas indexed: **{n_thm}**\n")
print("\n".join(out))
