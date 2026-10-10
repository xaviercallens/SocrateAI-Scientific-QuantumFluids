#!/usr/bin/env python3
"""Appendix B of the book: reproducibility -- how to rebuild every figure and how to run the Lean audit.

    python3 book/facts/make_appB.py

RE-RUNNABLE: run it (after facts/make_appA.py) whenever chapters/*.tex, figures/*.py or book/lean/*.lean change.  It writes book/chapters/appB.tex.
The figure table is built from the \\includegraphics calls of the chapters present, matched to the scripts that write the files; the audit meta-program is
printed from facts/lean_audit.py (the very text that is appended to every module), so the appendix cannot drift from the code; the software versions are
read from the machine when the script runs."""
from __future__ import annotations
import importlib.util, math, re, subprocess, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOOK = HERE.parent
ROOT = BOOK.parent
CH = BOOK / "chapters"; FIG = BOOK / "figures"
spec = importlib.util.spec_from_file_location("ma", HERE / "make_appA.py"); ma = importlib.util.module_from_spec(spec); spec.loader.exec_module(ma)
lspec = importlib.util.spec_from_file_location("la", HERE / "lean_audit.py"); la = importlib.util.module_from_spec(lspec); lspec.loader.exec_module(la)
tt = ma.tt

def _git_ignored(path) -> bool:
    """True if git ignores the file (superseded stubs that could not be deleted are ignored, so the book must not list them)."""
    import subprocess
    return subprocess.run(["git", "check-ignore", "-q", str(path)], cwd=str(Path(__file__).resolve().parent), capture_output=True).returncode == 0

def sh(cmd, cwd=None):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd, timeout=60).stdout.strip()
    except Exception as e:                                   # pragma: no cover
        return f"(unavailable: {e})"

PY = ROOT / ".venv/bin/python"
ver = dict(
    python=sh(f"{PY} -c 'import sys;print(sys.version.split()[0])'"),
    numpy=sh(f"{PY} -c 'import numpy;print(numpy.__version__)'"), scipy=sh(f"{PY} -c 'import scipy;print(scipy.__version__)'"),
    matplotlib=sh(f"{PY} -c 'import matplotlib;print(matplotlib.__version__)'"),
    lualatex=sh("lualatex --version | head -1"), lean=sh("lake env lean --version", cwd=str(la.TREE)),
    mathlib=next((p["rev"][:12] + " (" + p.get("inputRev", "") + ")" for p in json.load(open(la.TREE / "lake-manifest.json"))["packages"] if p["name"] == "mathlib"), "?"),
    rusty=sh("git describe --tags --always", cwd="/home/xavkal/xdev/rusty-SUNDIALS-c3") + " (" + sh("git rev-parse --short HEAD", cwd="/home/xavkal/xdev/rusty-SUNDIALS-c3") + ")",
    cpu=sh("lscpu | grep 'Model name' | sed 's/Model name: *//'"), cores=sh("lscpu | grep -E '^CPU\\(s\\):' | sed 's/[^0-9]//g'"),
    jax=(lambda d: d["results"][0]["jax"] if d.get("results") else "?")(json.load(open(ROOT / "data/generated/pgpe/bench/jax_cpu.json"))) if (ROOT / "data/generated/pgpe/bench/jax_cpu.json").exists() else "?",
)

# ---- print order of the chapters (second edition: read from the master file; file names are not print numbers) ----------------------------------
ORDER = re.findall(r"\\IfCh\{(ch\d\d)\}", (BOOK / "quantum_fluids_book.tex").read_text())
POS = {c: i for i, c in enumerate(ORDER)}

# ---- figures of the chapters present ----------------------------------------------------------------------------------------------------------
scripts = {p: p.read_text() for p in sorted(FIG.glob("*.py"))}
rows = []
for chp in sorted(CH.glob("ch*.tex")):
    m = re.fullmatch(r"ch(\d+)", chp.stem)                 # ch03_part1.tex (a draft of ch03) and chtest.tex are not chapters
    if not m: continue
    num = POS.get(chp.stem, 99)
    for im in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{figures/([A-Za-z0-9_\-]+)\.(?:pdf|png)\}", chp.read_text()):
        name = im.group(1)
        cand = [p for p, t in scripts.items() if re.search(r"""save\(\s*\w+\s*,\s*["']""" + re.escape(name) + r"""["']""", t) or f'"{name}.pdf"' in t or f"'{name}.pdf'" in t]
        if not cand and (FIG / f"{name}.py").exists(): cand = [FIG / f"{name}.py"]
        script = cand[0].name if cand else None
        doc = ""
        if script:
            d = re.match(r'\s*"""(.*?)"""', scripts[cand[0]], re.S)
            doc = " ".join((d.group(1) if d else "").strip().split("\n")[0:1])
            if len(doc) > 92: doc = doc[:92].rsplit(" ", 1)[0] + " ..."
        rows.append((num, chp.stem, name, script, doc))
rows = sorted(set(rows))

T = []
def breakify(s):
    """\\texttt{long/path_name.ext} -> breakable after / _ . (no overfull lines)."""
    def fix(m):
        body = m.group(1)
        if "\\allowbreak" in body or len(body.replace("\\_", "_")) < 13 or re.search(r"[\s$#{}]", body): return m.group(0)
        return "\\texttt{" + re.sub(r"(/|\\_|\.)", lambda x: x.group(1) + r"\allowbreak{}", body) + "}"
    return re.sub(r"\\texttt\{([^{}]*)\}", fix, s)
def A(s): T.append(breakify(s))
A(r"\chapter{Reproducibility: Rebuilding the Figures and Running the Audit}\label{appB}")
A(r"\InputIfFileExists{figures/appB_numbers}{}{}")
A(r"\noindent The figures of this book are written by scripts in \texttt{book/figures/}, and the numbers a chapter quotes are meant to come from files named in its numbers file. "
  r"This appendix says where each piece is, how to rerun it, and what it costs. It is itself partly generated: the figure table, the software versions and the "
  r"listing of the audit program are written by \texttt{book/facts/make\_appB.py} from the files as they are when it runs, so they cannot drift from the code. "
  r"Appendix~\ref{appA} (the catalogue of the library) is likewise generated, by \texttt{book/facts/make\_appA.py}; \emph{both scripts are meant to be rerun} "
  r"after the last chapter has been written, which refreshes the marks of cited theorems in the catalogue, the citation check "
  r"(\texttt{facts/appA\_citation\_check.md}) and the table of figures below.")
A(r"\section{The machine and the software}")
A(r"The computations of the book were run on one machine that was shared with other work (load average between about $8$ and $35$ while the audit and the chapter "
  r"runs were queued), so timings are indications and not benchmarks; the benchmark of chapter~\ref{ch10} carries its own caveats. "
  r"Table~\ref{appB:tab-versions} lists what was used.")
A(r"\begin{table}[h]\centering\small\renewcommand{\arraystretch}{1.1}\begin{tabularx}{\linewidth}{@{}>{\raggedright}p{0.27\linewidth}>{\raggedright\arraybackslash}X@{}}\toprule component & version\\\midrule")
for k, v in (("CPU", f"{ver['cpu']}, {ver['cores']} hardware threads, no GPU"), ("Python (project venv)", f"{ver['python']}; numpy {ver['numpy']}, scipy {ver['scipy']}, matplotlib {ver['matplotlib']}"),
             ("JAX (benchmark only)", ver["jax"]), ("Lean 4", ver["lean"].replace("Lean (version ", "").replace(")", "")), ("Mathlib", f"tag v4.34.0-rc2, commit {ver['mathlib'].split(' ')[0]}"),
             ("rusty-SUNDIALS (working tree used)", ver["rusty"]), ("typesetting", ver["lualatex"].replace("This is ", ""))):
    A(rf"{tt(k)} & \texttt{{{tt(v)}}} \\")
A(r"\bottomrule\end{tabularx}\caption{Software and hardware used. Read from the machine by \texttt{make\_appB.py}. The Lean and Mathlib versions are the ones pinned in "
  r"\texttt{lean\_src/lakefile.lean} and \texttt{lean-toolchain}; the library is never rebuilt with \texttt{lake update}.}\label{appB:tab-versions}\end{table}")
A(r"\section{Rebuilding a figure}")
A(r"A figure is written by a Python script in \texttt{book/figures/}. From the repository root, with the project environment,")
A(r"\begin{lstlisting}[style=plainmono]" + "\n" + ".venv/bin/python book/figures/chNN_name.py        # writes book/figures/chNN_name.pdf and .png\n" +
  "PYTHONPATH=/mnt/data/xdev-cache/qf_ext ...          # only for scripts that call the Rust extension qf_pgpe\n" + r"\end{lstlisting}")
A(r"The convention of the book is that the scripts of a chapter save the numbers that its figures and its text use in \texttt{figures/chNN\_numbers.json} (a value and its source "
  r"for each number); the list at the end of this section shows which chapters have such a file. "
  r"Heavy runs --- more than a minute of computation --- were serialised on the shared machine with \texttt{flock} on one lock file: " + f"{sum(1 for t in scripts.values() if 'flock' in t)} of the {len(scripts)} scripts of " + r"\texttt{book/figures/} call it themselves, "
  r"and the others were launched under it by the command line of their author. Table~\ref{appB:tab-figures} lists, for the chapters present when this appendix was generated, each figure and the script "
  r"that writes it (matched by the name of the file it saves).")
A(r"\begin{center}\captionof{table}{Figures of the chapters present when this appendix was generated, and the scripts that write them (the first line of the docstring of each script, shortened; a script whose name differs from the figure's is named in the last column). "
  r"The table is set in blocks so that it can break across pages.}\label{appB:tab-figures}\end{center}")
HDR = r"\toprule ch. & figure file (written by the script of the same name) & first line of the script's docstring\\\midrule"
SPEC = r"{@{}r>{\raggedright}p{0.34\linewidth}>{\raggedright\arraybackslash}X@{}}"
if not rows:
    A(r"\emph{No chapter with a figure was present when this appendix was generated.}")
for k in range(0, len(rows), 5):
    A(r"\begin{center}\footnotesize\setlength{\tabcolsep}{3pt}\begin{tabularx}{\linewidth}" + SPEC + HDR)
    for num, chs, name, script, doc in rows[k:k + 5]:
        note = "" if script == f"{name}.py" else (r"\textbf{script not found} " if not script else rf"[script \texttt{{{tt(script)}}}] ")
        A(rf"\ref{{{chs}}} & \texttt{{{tt(name)}}} & {note}{tt(doc) if doc else ''} \\")
    A(r"\bottomrule\end{tabularx}\end{center}")

# per-chapter artefacts
A(r"\paragraph{Other files by chapter.} Besides figure scripts a chapter may own: a numbers file (\texttt{figures/chNN\_numbers.json}), a bibliography "
  r"file (\texttt{refs\_chNN.bib}, merged into \texttt{refs\_all.bib} by \texttt{build\_refs.py}), Lean files written for the book "
  r"(\texttt{lean/ChNN\_*.lean}, compiled against the same pinned Mathlib and listed in appendix~\ref{appA}), Rust sources (\texttt{rust/}) and "
  r"a report of what was verified (\texttt{facts/chNN\_report.md}). Present when this appendix was generated:")
items = []
for chs in ORDER:
    nn = chs[2:]
    have = []
    if list(FIG.glob(f"ch{nn}*numbers*.json")): have.append("numbers")
    if (BOOK / f"refs_ch{nn}.bib").exists(): have.append("bib")
    ls = sorted((BOOK / "lean").glob(f"Ch{nn}_*.lean"))
    real = [p for p in ls if not la.is_negative_control(p) and not la.is_placeholder(p)]
    ctl = [p for p in ls if la.is_negative_control(p)]
    ph = [p for p in ls if la.is_placeholder(p) and not la.is_negative_control(p) and not _git_ignored(p)]
    if real: have.append("Lean: " + ", ".join(p.stem for p in real))
    if ctl: have.append("negative control (meant to fail, not counted): " + ", ".join(p.stem for p in ctl))
    if ph: have.append("empty placeholder (not counted): " + ", ".join(p.stem for p in ph))
    if (BOOK / "rust").exists() and list((BOOK / "rust").glob(f"ch{nn}*")): have.append("Rust")
    if (HERE / f"ch{nn}_report.md").exists(): have.append("report")
    if (CH / f"sol{nn}.tex").exists(): have.append("solutions (appendix~\\ref{appC})")
    sl = sorted((BOOK / "lean").glob(f"Sol{nn}_*.lean"))
    if sl: have.append("Lean of the solutions: " + ", ".join(p.stem for p in sl))
    items.append(rf"\item chapter~\ref{{{chs}}} (file \texttt{{{chs}}}): " + ("; ".join(tt(h) if h.startswith(("Lean", "negative", "empty")) else h for h in have) if have else r"\emph{nothing yet}"))
A(r"\begin{itemize}[nosep]" + "\n" + "\n".join(items) + "\n" + r"\end{itemize}")

# ---- CVODE: which build is imported -------------------------------------------------------------------------------------------------------------
def probe(tag):
    f = FIG / "ch10_raw" / f"cvode_probe_{tag}.json"
    return json.load(open(f)) if f.exists() else None
stale, fixed = probe("stale"), probe("fixed")
A(r"\section{CVODE: which build is imported}\label{appB:cvode}")
A(r"The solver library has a history that the book's CVODE results depend on. Until the repair of 28~September 2026 its Adams method was, in effect, implicit Euler "
  r"(\texttt{docs/CVODE\_ADAMS\_FIX.md} of rusty-SUNDIALS): the order never rose above one, so the work grew like $\mathrm{rtol}^{-1/2}$. The Python module "
  r"\texttt{rusty\_sundials} that sits in the project's virtual environment was built on 26~September, before the repair, and is \emph{stale}. Every CVODE result "
  r"of this book must come from rusty-SUNDIALS commit \texttt{5db8041fd2e3840defcff2b4a8c26c1cbb2467fd} (the v11.6.0 line) or later. The recipe:")
A(r"\begin{lstlisting}[style=plainmono]" + "\n" +
  "# 1. build the module from the checkout into a scratch directory (about 3 minutes; nothing is written to the checkout)\n"
  "flock /mnt/data/xdev-cache/tmp/qf_heavy.lock nice book/rust/ch02_build_py.sh OUTDIR     # writes OUTDIR/py/rusty_sundials.so, OUTDIR/commit.txt\n"
  "# 2. a stable copy of the build used for the book (commit 5db8041fd2e3840defcff2b4a8c26c1cbb2467fd):\n"
  "#      /mnt/data/xdev-cache/rs_py_5db8041/rusty_sundials.so   sha256 0bdb1b4a504fb4817738c483f797e6a109b99121b666f1e51ad8e05c2fb996d7\n"
  "# 3. run with the repaired module FIRST on the path, then the quantum-fluids extension:\n"
  "PYTHONPATH=/mnt/data/xdev-cache/rs_py_5db8041:/mnt/data/xdev-cache/qf_ext  .venv/bin/python book/figures/chNN_script.py\n"
  "# 4. check which build a script imports, whenever in doubt:\n"
  ".venv/bin/python book/figures/ch10_cvode_probe.py stale        # the module in the virtual environment\n"
  "PYTHONPATH=/mnt/data/xdev-cache/rs_py_5db8041:/mnt/data/xdev-cache/qf_ext .venv/bin/python book/figures/ch10_cvode_probe.py fixed\n" + r"\end{lstlisting}")
if stale and fixed:
    A(r"The probe integrates $y'=-y$ on $[0,10]$ with absolute tolerance $10^{-14}$ and counts the right-hand-side calls and the relative error of $y(10)$. "
      r"It tells the two builds apart at once (table~\ref{appB:tab-cvode}): in the stale one the Adams error falls only as the square root of the tolerance and the cost explodes.")
    A(r"\begin{table}[h]\centering\small\setlength{\tabcolsep}{4pt}\begin{tabular}{@{}llrrrr@{}}\toprule & & \multicolumn{2}{c}{stale module (built " + stale["built"] + r")} & \multicolumn{2}{c}{repaired build (commit 5db8041)}\\")
    A(r"method & rtol & RHS calls & rel. error & RHS calls & rel. error\\\midrule")
    def fe(x): return "--" if x is None else (f"{x:.1e}".replace("e-0", r"\!\times\!10^{-").replace("e-", r"\!\times\!10^{-") + "}").join(["$", "$"])
    for rs, rf in zip(stale["rows"], fixed["rows"]):
        A((rf"{rs['method']} & $10^{{{round(math.log10(rs['rtol']))}}}$ & {rs['nfe']:,} & {fe(rs['relerr'])} & {rf['nfe']:,} & {fe(rf['relerr'])} \\").replace(",", r"\,"))
    A(r"\bottomrule\end{tabular}\caption{The probe $y'=-y$, $t\in[0,10]$, atol $10^{-14}$, run with the module of the virtual environment (shared object "
      + tt(stale["sha256"][:12]) + r"\ldots) and with the repaired build (" + tt(fixed["sha256"][:12]) + r"\ldots). The BDF method is shown for comparison; it differs little between the builds.}\label{appB:tab-cvode}\end{table}")
A(r"A result obtained with the stale module is wrong in a way that no convergence \emph{within} the module reveals, and no test of the source tree can: the tests ran on the source "
  r"(chapter~\ref{ch10}, section~\ref{ch10:sec-failures}). The rule for the book's scripts is therefore to check the probe once per session, and to record the commit and the checksum of "
  r"the module in the numbers file of the chapter.")

A(r"\section{Running the Lean audit}\label{appB:audit}")
A(r"The audit of chapter~\ref{ch10} has three parts, all driven by \texttt{book/facts/lean\_audit.py}; nothing is written into the Lean project trees, and "
  r"\texttt{lake update} is never run. From the repository root:")
A(r"\begin{lstlisting}[style=plainmono]" + "\n" +
  "python3 book/facts/lean_audit.py            # compile every module in import order, audit its environment; ~1 h on a loaded machine\n"
  "python3 book/facts/lean_audit.py --resume   # skip the modules whose facts/audit/<Module>.json exists and was made on the present code\n"
  "python3 book/facts/lean_audit.py --book --resume   # the same program on the Lean files written for the book (book/lean/*.lean); a file that is meant to fail is compiled expecting errors\n"
  "python3 book/facts/lean_audit.py --report   # only rebuild facts/lean_audit.md from the stored JSON\n"
  "python3 book/facts/lean_audit.py --controls # negative control: run the auditor on a file with planted defects (seconds)\n"
  "python3 scripts/regen_axiom_audit.py --check # the library's own staleness check of the #print axioms blocks (read-only)\n"
  "python3 book/facts/make_appA.py              # regenerate the catalogue, the citation check and the namespace table\n" + r"\end{lstlisting}")
A(r"The driver copies each module to a scratch directory (\texttt{QF\_AUDIT\_WORK}, default \texttt{/mnt/data/xdev-cache/tmp/qf\_audit}), appends the program below, "
  r"and compiles it with \texttt{lake env lean -R <scratch> -o <scratch>/<Module>.olean} inside the pinned Mathlib tree, with the scratch directory on "
  r"\texttt{LEAN\_PATH} so that a module finds its compiled siblings. It takes the shared lock of the machine (\texttt{QF\_LOCK}) for a short batch only: it starts "
  r"a new module while the hold is younger than \texttt{QF\_BATCH\_SECONDS} (the run for this book used $100$~s, so one to three modules per hold), and then stays away from "
  r"the lock for \texttt{QF\_YIELD\_SECONDS} ($45$~s) so that a job that is waiting takes it first. An audit counts as current only if it was made on the present "
  r"\emph{code} of the file: the driver stores a hash of the source with comments and white space removed, so that a corrected docstring does not invalidate an audit and any change "
  r"of code does (appendix~\ref{appA} then prints \texttt{stale}). Its output is one log and one JSON file per module in \texttt{facts/audit/}, the table "
  r"\texttt{facts/lean\_audit.md}, and \texttt{facts/audit/summary.json}. The program that is appended --- new for this book, and tested on the file with "
  r"planted defects before it was trusted --- is:")
snippet = la.SNIPPET.strip("\n")
A(r"\begin{lstlisting}[style=lean]" + "\n" + snippet + "\n" + r"\end{lstlisting}")
A(r"Reading it: \texttt{foldStage2} lists the constants that this file added to the environment; \texttt{collectAxioms} returns the axioms a constant "
  r"depends on, through the whole chain of lemmas it uses; the union over all constants is the footprint of the module; a constant whose footprint contains "
  r"\texttt{sorryAx} contains a \texttt{sorry} somewhere below it, even if its own proof does not. The negative control "
  r"(\texttt{facts/audit\_controls/AuditControls.lean}, output in \texttt{AuditControls.out}) plants a \texttt{sorry}, the same \texttt{sorry} inherited, "
  r"a \texttt{sorry} in a private theorem, an axiom of its own and a \texttt{native\_decide}; the auditor reports each.")
_tracked = sh("git ls-files data/generated/pgpe | wc -l", cwd=str(ROOT)); _size = sh("du -sh data/generated/pgpe | cut -f1", cwd=str(ROOT))
gen_desc = (f"{_size} on the machine of the author; the directory \\texttt{{data/generated/}} is git-ignored, and only {_tracked} small analysis files of it were committed (measured when this appendix "
            "was generated)")
A(r"\section{Limits of what can be reproduced}")
A(r"\begin{itemize}[nosep]")
A(r"\item Timings depend on the machine and on its load; the benchmark of chapter~\ref{ch10} was taken on a shared machine and is to be repeated on an idle one.")
A(r"\item The long campaign runs behind chapters~\ref{ch06}, \ref{ch07} and~\ref{ch09} (the pre-registered runs of tens of hours) are not rerun by the book's scripts; "
  + r"their saved outputs are under \texttt{data/generated/pgpe/}: " + gen_desc + r", and the scripts of the chapters read those outputs.")
A(r"\item No computation of this book used a GPU or a TPU.")
A(r"\item The environment audit trusts Lean's own elaborator and kernel; the second kernel (nanoda) is run through the Comparator, whose recorded results are in "
  r"\texttt{docs/COMPARATOR\_SETUP.md} and were not rerun for the book.")
A(r"\end{itemize}")
(CH / "appB.tex").write_text("\n".join(T) + "\n")
print(f"appB.tex: {len(rows)} figures matched ({sum(1 for r in rows if r[2] is None)} without a script), versions: " + ", ".join(f"{k}={v}" for k, v in ver.items() if k in ('python', 'lean')))
