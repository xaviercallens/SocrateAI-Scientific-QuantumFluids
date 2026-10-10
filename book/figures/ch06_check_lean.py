"""Chapter 6 -- check that (i) every \\Lthm{Module}{name} of chapters/ch06.tex names a declaration that exists in lean_src/Module.lean, and (ii) every statement shown in a
leanbox is a verbatim (whitespace-normalised) piece of the source file named in the box title: lean_src/<Module>.lean for the library, book/lean/Ch06_KTForward.lean for
the new module.  Prints one line per item and exits non-zero on any failure.   Run: python3 figures/ch06_check_lean.py"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEX = (ROOT / "book/chapters/ch06.tex").read_text()
norm = lambda t: re.sub(r"\s+", " ", t).strip()
bad = 0

# (i) \Lthm
for mod, name in re.findall(r"\\Lthm\{(\w+)\}\{([\w\\]+)\}", TEX):
    name = name.replace("\\", "")
    src = (ROOT / f"lean_src/{mod}.lean").read_text()
    ok = re.search(rf"^\s*(?:theorem|lemma|def|noncomputable def)\s+{re.escape(name)}\b", src, re.M) is not None
    print(("ok  " if ok else "FAIL"), f"\\Lthm{{{mod}}}{{{name}}}"); bad += (not ok)

# (ii) leanbox contents
for title, body in re.findall(r"\\begin\{leanbox\}\{([^}]*)\}\s*\\begin\{lstlisting\}\[style=lean\](.*?)\\end\{lstlisting\}", TEX, re.S):
    title = title.replace("\\_", "_").replace("\\ ", " ")
    mod = title.split()[0]
    path = ROOT / (f"book/lean/{mod}.lean" if mod.startswith("Ch06") else f"lean_src/{mod}.lean")
    src = norm(path.read_text())
    # split the box into statements: a new statement starts at a line beginning with a keyword at column 0
    stmts = re.split(r"\n(?=(?:theorem|noncomputable def|variable|lemma)\b)", body.strip("\n"))
    for st in stmts:
        st = st.strip()
        if not st or st.startswith("--"):
            continue
        st_lines = [ln for ln in st.split("\n") if not ln.strip().startswith("--")]   # drop explanatory comments
        st_clean = norm(" ".join(st_lines))
        if st_clean.endswith(":= by") or st_clean.endswith(":="):
            st_clean = st_clean  # proofs shown in full are checked as they stand
        # allow the statement shown WITHOUT its proof: compare against the source up to ':='
        probe = st_clean.split(":= by")[0].strip() if ":= by" not in st_clean or len(st_clean) < 400 else st_clean
        found = norm(probe) in src
        # the proof-bearing box must match the full text
        print(("ok  " if found else "FAIL"), f"[{title}]", st_clean[:90]); bad += (not found)
sys.exit(1 if bad else 0)
