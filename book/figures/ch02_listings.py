"""Keep the code boxes of chapters/ch02.tex verbatim.
  python3 book/figures/ch02_listings.py splice   copies, into chapters/ch02.tex, the code blocks of figures/ch02_snippets.py (between '# <<< name' and
                                                 '# >>> name'), the function lean_nl of figures/ch02_compute.py and the stored output of ch02_snippets.py
                                                 (figures/ch02_snippets_output.txt) into the listings that follow the markers  % CODE name  /  % OUTPUT name
  python3 book/figures/ch02_listings.py check    reports whether every marked listing equals its source (exit code 1 if not)
Output lines are split among the snippets by count: snippet1 prints 2 lines, snippet2 1 line, snippet3 3 lines."""
import re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEX = HERE.parent / "chapters" / "ch02.tex"
SNIP = (HERE / "ch02_snippets.py").read_text()
COMP = (HERE / "ch02_compute.py").read_text()
OUT = (HERE / "ch02_snippets_output.txt").read_text().rstrip("\n").split("\n")
NLINES = {"snippet1": 2, "snippet2": 1, "snippet3": 3}

def code_block(name):
    if name == "engine_vs_lean":                      # an excerpt of bridge_case, dedented
        m = re.search(r"# <<< engine_vs_lean\n(.*?)\n\s*# >>> engine_vs_lean", COMP, re.S)
        return "\n".join(l[4:] if l.startswith("    ") else l for l in m.group(1).split("\n"))
    if name == "lean_nl":
        a = COMP.index("def lean_nl(Lam, A):"); b = COMP.index("def lean_dens_sq")
        return COMP[a:b].rstrip("\n")
    m = re.search(r"# <<< " + name + r"[^\n]*\n(.*?)# >>> " + name, SNIP, re.S)
    return m.group(1).rstrip("\n")

def output_block(name):
    start = 0
    for k, n in NLINES.items():
        if k == name:
            return "\n".join(OUT[start:start + n])
        start += n
    raise KeyError(name)

PAT = re.compile(r"(% (CODE|OUTPUT) (\w+)\n\\begin\{lstlisting\}\[[^\]]*\]\n)(.*?)(\n\\end\{lstlisting\})", re.S)

def run(mode):
    txt = TEX.read_text(); bad = []
    def sub(m):
        kind, name = m.group(2), m.group(3)
        want = code_block(name) if kind == "CODE" else output_block(name)
        if m.group(4) != want: bad.append((kind, name))
        return m.group(1) + want + m.group(5)
    new = PAT.sub(sub, txt)
    n = len(PAT.findall(txt))
    if mode == "splice":
        TEX.write_text(new); print(f"{n} listings spliced; {len(bad)} had differed: {bad}")
    else:
        print(f"{n} marked listings; differing from their source: {bad}"); sys.exit(1 if bad else 0)

if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "check")
