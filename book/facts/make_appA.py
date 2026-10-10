#!/usr/bin/env python3
"""Appendix A of the book: the COMPLETE catalogue of the QuantumFluids Lean library, generated from ../lean_src.

    python3 book/facts/make_appA.py

RE-RUNNABLE.  Run it again whenever lean_src/, facts/audit/*.json (written by facts/lean_audit.py), chapters/*.tex or
book/lean/*.lean change.  It writes
    book/chapters/appA.tex                  the appendix (inputs: lean_src, the audit JSON, the chapters, book/lean)
    book/facts/appA_citation_check.md       every \\Lthm{Module}{name} and every `theorem` copied into a chapter's leanbox,
                                            checked against the library (name exists? statement identical up to white space?)
    book/facts/lean_namespaces.json/.md     the TRUE Lean namespace of every module (13 of 37 differ from QuantumFluids.<Module>)
    book/lean_ns.tex                        the namespace table only (qfbook.sty loads it and defines \\Lthm after it)
    book/qf_unicode_lst.tex                 fix for non-ASCII characters in lstlisting under LuaLaTeX (qfbook.sty loads it)

Parsing = the declaration regex of facts/make_lean_index.py (same 413 declarations: 310 theorem/lemma, 100 def, 2 structure,
1 abbrev), but the statement is kept COMPLETE and verbatim (line breaks included) up to the first top-level `:=` / `where`,
whereas the index joins lines and truncates at 300 characters.  Nothing here is hand-typed except the explanatory prose.
"""
from __future__ import annotations
import difflib, hashlib, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lean_audit import audit_is_current, is_negative_control, is_placeholder   # noqa: E402  (the audit driver is a script with a main guard)

HERE = Path(__file__).resolve().parent
BOOK = HERE.parent
ROOT = BOOK.parent
SRC = ROOT / "lean_src"
AUD = HERE / "audit"
CH = BOOK / "chapters"
BL = BOOK / "lean"

DECL = re.compile(r"^(?:noncomputable\s+)?(?:@\[[^\]]*\]\s*)?(theorem|lemma|def|structure|abbrev|inductive|instance)\s+([^\s:({\[]+)")
OPEN, CLOSE = "([{⟨⦃⌊⌈", ")]}⟩⦄⌋⌉"
STD = ("propext", "Classical.choice", "Quot.sound")
SHORT = {"propext": "p", "Classical.choice": "c", "Quot.sound": "q"}
ABBREV = {"Phys", "Rev", "Eq", "Eqs", "Thm", "Nucl", "J", "Rev", "Lett", "al", "et", "cf", "vs", "Fig", "Sec", "No", "Vol", "pp", "arXiv", "Math", "Commun", "Ann", "Sov", "Mod", "Proc"}


# ----------------------------------------------------------------------------------------------------- parsing
def blank_comments(t: str) -> str:
    """Replace block comments and line comments by spaces (newlines kept) so structure can be scanned safely."""
    t = re.sub(r"/-.*?-/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), t, flags=re.S)
    return "\n".join(re.sub(r"--.*$", lambda m: " " * len(m.group(0)), l) for l in t.split("\n"))


def namespaces(lines: list[str]) -> list[str]:
    """Namespace in force at each line (from `namespace X` / `section` / `end`)."""
    stack: list[tuple[str, str]] = []
    out = []
    for l in lines:
        m = re.match(r"namespace\s+(\S+)", l)
        if m:
            stack.append(("ns", m.group(1)))
        elif re.match(r"section(\s+\S+)?\s*$", l):
            stack.append(("sec", ""))
        elif re.match(r"end(\s+\S+)?\s*$", l) and stack:
            stack.pop()
        out.append(".".join(n for k, n in stack if k == "ns"))
    return out


def statement(lines: list[str], i: int) -> tuple[str, int]:
    """Declaration text from line i up to (not including) the first top-level `:=` or `where`; returns (text, last line index)."""
    depth = 0
    buf: list[str] = []
    j = i
    while j < len(lines) and j - i < 80:
        line = lines[j].replace("\t", "    ")
        k, cut, in_str = 0, None, False
        while k < len(line):
            c = line[k]
            if in_str:
                if c == "\\":
                    k += 2
                    continue
                if c == '"':
                    in_str = False
            else:
                if c == '"':
                    in_str = True
                elif line.startswith("--", k):
                    break
                elif c in OPEN:
                    depth += 1
                elif c in CLOSE:
                    depth -= 1
                elif depth <= 0 and line.startswith(":=", k):
                    cut = k
                    break
                elif depth <= 0 and re.match(r"\swhere\b", line[k:k + 7]):
                    cut = k
                    break
            k += 1
        if cut is not None:
            head = line[:cut].rstrip()
            if head.strip():
                buf.append(head)
            return "\n".join(buf), j
        if j > i and (not line.strip() or DECL.match(line) or line.lstrip().startswith("|")):
            return "\n".join(buf), j - 1                     # pattern-matching def without `:=`
        buf.append(line.rstrip())
        j += 1
    return "\n".join(buf), j - 1


def dedent_tail(text: str) -> str:
    ls = text.split("\n")
    if len(ls) < 2:
        return text
    tail = [l for l in ls[1:] if l.strip()]
    if not tail:
        return text
    m = min(len(l) - len(l.lstrip()) for l in tail)
    keep = 4 if m >= 4 else m                                   # continuation lines at most 4 spaces deep
    return "\n".join([ls[0]] + [(" " * keep + l[m:]) if l.strip() else l for l in ls[1:]])


def parse_decls(path: Path) -> list[dict]:
    txt = path.read_text()
    lines = txt.split("\n")
    code = blank_comments(txt).split("\n")
    nss = namespaces(code)
    decls, i = [], 0
    while i < len(lines):
        d = DECL.match(lines[i])
        if d and not lines[i].startswith(" "):
            stmt, last = statement(lines, i)
            name = d.group(2)
            ns = nss[i]
            decls.append(dict(kind=d.group(1), name=name, ns=ns, full=(ns + "." + name) if ns and not name.startswith("_root_") else name.replace("_root_.", ""),
                              line=i + 1, text=dedent_tail(stmt)))
            i = max(i, last)
        i += 1
    return decls


def header(txt: str) -> str:
    m = re.match(r"\s*/-[!\-]?(.*?)-/", txt, re.S) or re.search(r"/-[!\-]?(.*?)-/", txt, re.S)
    return m.group(1) if m else ""


def oneliner(txt: str, stem: str, skip_meta: bool = False) -> str:
    """One sentence/line of the module docstring: a paragraph of the header, markup and file-name prefix stripped.  With skip_meta (the book's own
    files) paragraphs that only say 'NEW for the book / written for chapter N / not part of the library' are skipped."""
    lines = [l.strip() for l in header(txt).split("\n")]
    paras: list[list[str]] = [[]]
    for l in lines:
        l = re.sub(r"^#+\s*", "", l)
        if not l or re.fullmatch(r"[=\-_*#~\s]+", l) or l.startswith("MATHESIS"):
            if paras[-1]:
                paras.append([])
            continue
        l = re.sub(r"^" + re.escape(stem) + r"\.lean\s*(--|—|-|:)\s*", "", l)
        paras[-1].append(l)
    paras = [x for x in paras if x]
    if skip_meta:
        good = [x for x in paras if not re.search(r"\bNEW\b|not part of|written for|nothing else", " ".join(x))]
        paras = good or paras
    par = paras[0] if paras else []
    s = " ".join(par).replace("`", "")
    s = s[:1].upper() + s[1:]
    # first sentence, skipping abbreviation/initial full stops
    for m in re.finditer(r"([.!?])(?=\s|$)", s):
        pre = re.findall(r"([A-Za-z]+)$", s[:m.start()])
        word = pre[0] if pre else ""
        if word in ABBREV or len(word) == 1 or s[:m.start()].endswith(("[G21", "(CLAIM")):
            continue
        s = s[:m.end()]
        break
    if len(s) > 190:
        s = s[:190].rsplit(" ", 1)[0] + " …"
    return s


# ------------------------------------------------------------------------------------------------ TeX helpers
TEXESC = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "$": r"\$", "&": r"\&", "#": r"\#", "%": r"\%", "_": r"\_\allowbreak{}", "^": r"\^{}", "~": r"\~{}"}


def tt(s: str) -> str:
    out = []
    for c in s:
        out.append(TEXESC.get(c, c))
        if c in "/.,-" :
            out.append(r"\allowbreak{}")
    return "".join(out)


ESC = ";"                                    # listing escape character: must not occur in any statement (checked in main)
SCRIPT = {"𝓝": r"$\mathcal{N}$", "𝓧": r"$\mathcal{X}$"}      # glyphs missing in the monospace font


def lst(text: str, mark: str = "") -> str:
    body = text.rstrip("\n")
    for k, v in SCRIPT.items():
        body = body.replace(k, ESC + v + ESC)
    if mark:
        body = ESC + r"\llap{\citedmark{" + mark + r"}\,}" + ESC + body
    return "\\begin{lstlisting}[style=leancat]\n" + body + "\n\\end{lstlisting}\n"


# ------------------------------------------------------------------------------------------------ citations
def chapter_label(p: Path) -> str:
    m = re.match(r"ch(\d+)", p.stem)                            # ch03.tex, ch03_part1.tex, ... -> "3"
    if m:
        return str(int(m.group(1)))
    m = re.match(r"app([A-Z])", p.stem)
    return m.group(1) if m else re.sub(r"[^A-Za-z0-9]", "", p.stem)


def norm_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def canon(arg: str, index: dict, alias: dict) -> str | None:
    """Module argument of \\Lthm / leanbox -> key of the index: a library module, or a file of book/lean (by stem or by short name)."""
    a = arg.replace("\\_", "_").replace("\\ ", " ").replace("~", " ").strip()
    a = re.sub(r"^new:\s*", "", a, flags=re.I)
    a = re.sub(r"\s*\(.*?\)\s*$", "", a).strip()
    if a in index:
        return a
    return alias.get(a)


def scan_chapters(index: dict[str, list[dict]], alias: dict[str, str]) -> tuple[dict, list, list]:
    """cited[(module, declname)] -> chapter labels (module = library module or book/lean stem); problems; verbatim-copy checks."""
    cited: dict[tuple[str, str], set[str]] = {}
    problems, copies = [], []
    for p in sorted(CH.glob("*.tex")):
        if p.stem in ("appA", "appB", "chtest"):
            continue
        lab = chapter_label(p)
        txt = p.read_text()
        for m in re.finditer(r"\\Lthm\{([^}]*)\}\{([^}]*)\}", txt):
            arg, name = m.group(1).strip(), m.group(2).replace("\\_", "_").strip()
            if arg == "Module":                                      # the placeholder of an explanation
                continue
            mod = canon(arg, index, alias)
            if mod is None:
                problems.append((p.name, arg, name, "unknown module", []))
                continue
            hit = find_decl(index, mod, name)
            if hit is None:
                near = difflib.get_close_matches(name, [d["name"] for d in index[mod]], n=3, cutoff=0.6)
                problems.append((p.name, arg, name, "no such declaration", near))
            else:
                cited.setdefault((mod, hit["name"]), set()).add(lab)
        # theorem statements copied into leanbox environments
        for bm in re.finditer(r"\\begin\{leanbox\}(?:\[[^\]]*\])?\{([^}]*)\}(.*?)\\end\{leanbox\}", txt, re.S):
            arg, body = bm.group(1).strip(), bm.group(2)
            mod = canon(arg, index, alias)
            if mod is None:
                problems.append((p.name, arg, "(leanbox)", "unknown module in leanbox argument", []))
                continue
            for lm in re.finditer(r"\\begin\{lstlisting\}[^\n]*\n(.*?)\\end\{lstlisting\}", body, re.S):
                code = lm.group(1)
                for dm in re.finditer(r"(?m)^[ \t]*(?:@\[[^\]]*\]\s*)?(?:(?:private|protected|noncomputable)\s+)*(theorem|lemma|def|structure|abbrev)\s+([^\s:({\[]+)(.*?)(?=:=|\n\s*\n|\Z)", code, re.S):
                    name = dm.group(2)
                    hit = find_decl(index, mod, name)
                    chunk = dm.group(0)
                    if hit is None:
                        problems.append((p.name, arg, name, "leanbox copy: no such declaration in the module", []))
                        continue
                    cited.setdefault((mod, hit["name"]), set()).add(lab)
                    lib, mine = norm_ws(hit["text"]), norm_ws(re.sub(r"--[^\n]*", "", chunk))      # a trailing `-- comment` of the chapter is not a difference
                    same = lib == mine
                    abridged = "\u2026" in chunk or "..." in chunk or "abridged" in code.lower()
                    copies.append((p.name, mod, name, "identical" if same else ("abridged/marked" if abridged else "DIFFERS"), lib if not same else "", mine if not same else ""))
        # generic dotted citations in running text / listings: QuantumFluids.Module.name
        for m in re.finditer(r"QuantumFluids\.([A-Za-z0-9]+)\.([A-Za-z0-9_\\']+)", txt):
            mod, name = m.group(1), m.group(2).replace("\\_", "_")
            mod = canon(mod, index, alias)
            if mod:
                hit = find_decl(index, mod, name)
                if hit:
                    cited.setdefault((mod, hit["name"]), set()).add(lab)
    return cited, problems, copies


def find_decl(index: dict[str, list[dict]], mod: str, name: str):
    for d in index.get(mod, []):
        if d["name"] == name or d["full"] == name or d["full"].endswith("." + name) or name.endswith("." + d["name"]):
            return d
    return None


# --------------------------------------------------------------------------------------------------- audit
def audit_of(stem: str, prefix: str = "") -> dict | None:
    """Environment-level audit (facts/audit/<M>.json from lean_audit.py); else, for library modules only, the first-pass compile log
    (author-written `#print axioms` lines) if it is clean; else None."""
    p = AUD / f"{prefix}{stem}.json"
    if p.exists():
        a = json.loads(p.read_text())
        src = (BL / f"{stem}.lean") if prefix == "book_" else (SRC / f"{stem}.lean")
        if a.get("source") and src.exists() and not audit_is_current(p, src):
            return dict(module=stem, stale=True, audited_when=a.get("when", "?"))         # the code of the file has changed since it was audited
        return a
    lp = AUD / f"{prefix}{stem}.log"
    if prefix == "" and lp.exists():
        t = lp.read_text()
        sets = re.findall(r"depends on axioms: \[([^\]]*)\]", t)
        if sets and not re.search(r":\d+:\d+: error", t) and "sorry" not in t:
            fp = sorted({a.strip() for x in sets for a in x.replace("\n", " ").split(",") if a.strip()})
            return dict(module=stem, exit=0, errors=0, firstpass=True, audit=dict(named_theorems=len(sets), sorryAx=False, axiom_decls=0, union_axioms=fp))
    return None


def audit_short(a: dict | None) -> str:
    if not a:
        return "n/c"
    if a.get("stale"):
        return "stale"
    if a.get("exit") != 0 or a.get("errors") or not a.get("audit"):
        return "FAIL"
    s = a["audit"]
    if s["sorryAx"] or s["axiom_decls"] or any(x not in STD for x in s["union_axioms"]):
        return "!"
    return (" ".join(SHORT[x] for x in STD if x in s["union_axioms"]) or "none") + ("$^\\dagger$" if a.get("firstpass") else "")


def audit_long(a: dict | None, own_print: int) -> str:
    if not a:
        return "not re-checked (no audit on file)"
    if a.get("stale"):
        return "not re-checked: the file has changed since the audit on file was made (" + str(a.get("audited_when", "?")) + ")"
    if a.get("exit") != 0 or a.get("errors"):
        return f"NOT AUDITED: compile failed (exit {a.get('exit')}, {a.get('errors')} errors)"
    s = a.get("audit")
    if not s:
        return "NOT AUDITED: the audit meta-program printed nothing"
    fp = s["union_axioms"]
    if a.get("firstpass"):
        return (f"first-pass compile log only: {s['named_theorems']} author-written #print axioms lines, no error, no sorry; axioms printed: {', '.join(fp) if fp else 'none'}; "
                "this does not show that every theorem of the module carries such a line")
    sorry = "sorryAx reachable" if s["sorryAx"] else "0 sorry"
    decl = sum(1 for t in a.get("theorems", []) if t["line"] >= 0); auto = sum(1 for t in a.get("theorems", []) if t["line"] < 0)
    txt = (f"{decl} theorem constants audited" + (f" (+{auto} generated by Lean)" if auto else "") +
           f", {sorry}, {s['axiom_decls']} user axioms; axioms used: {', '.join(fp) if fp else 'none'}")
    if own_print == 0:
        txt += "; the source has no #print axioms line (footprint from the appended environment audit)"
    return txt


# --------------------------------------------------------------------------------------------------- main
def main() -> int:
    mods = sorted(f.stem for f in SRC.glob("*.lean") if not f.name.startswith("_tmp") and f.name not in ("lakefile.lean", "QuantumFluids.lean"))
    index: dict[str, list[dict]] = {}
    info: dict[str, dict] = {}
    for m in mods:
        txt = (SRC / f"{m}.lean").read_text()
        index[m] = parse_decls(SRC / f"{m}.lean")
        nss = sorted({d["ns"] for d in index[m]})
        ns = max(set(nss), key=lambda n: sum(d["ns"] == n for d in index[m])) if nss else ""
        info[m] = dict(doc=oneliner(txt, m), ns=ns, own_print=sum(1 for l in txt.split("\n") if l.startswith("#print axioms")))
    global ESC
    alltext = "".join(d["text"] for m in mods for d in index[m]) + "".join(d["text"] for f in sorted(BL.glob("*.lean")) for d in parse_decls(f))
    ESC = next(c for c in ";?~&" if c not in alltext)                 # escape character not occurring in any statement
    n_thm = sum(1 for m in mods for d in index[m] if d["kind"] in ("theorem", "lemma"))
    n_def = sum(1 for m in mods for d in index[m] if d["kind"] in ("def", "abbrev", "structure", "inductive", "instance"))
    book_index: dict[str, list[dict]] = {}
    alias: dict[str, str] = {}
    for f in sorted(BL.glob("*.lean")):
        book_index[f.stem] = parse_decls(f)
        alias[f.stem] = f.stem
        alias.setdefault(re.sub(r"^Ch\d+_", "", f.stem), f.stem)
        alias.setdefault(f.stem.replace("_", ""), f.stem)                    # Ch03PointVortexPair
        if book_index[f.stem]:                                                  # last component of the namespace: KTForward, FlowPast, ...
            ns_ = max({d["ns"] for d in book_index[f.stem]}, key=lambda n: sum(d["ns"] == n for d in book_index[f.stem]))
            if ns_:
                alias.setdefault(ns_.split(".")[-1], f.stem)
    full_index = dict(index); full_index.update(book_index)
    cited, problems, copies = scan_chapters(full_index, alias)

    # ---------- Unicode in lstlisting (book-wide fix; see the comment written into the file)
    from fontTools.ttLib import TTFont  # noqa: E402  (available in the project's venv; falls back to no filtering)
    used: set[str] = set()
    for q in list(SRC.glob("*.lean")) + list(BL.glob("*.lean")) + list(CH.glob("*.tex")) + list((BOOK / "figures").glob("*.py")) + list((BOOK / "rust").rglob("*.rs")) + [HERE / "lean_audit.py"]:
        try:
            used |= {c for c in q.read_text() if ord(c) > 255}
        except (UnicodeDecodeError, OSError):
            pass
    try:
        cmap = TTFont("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf").getBestCmap()
        used = {c for c in used if ord(c) in cmap}                                   # only glyphs the monospace font has
    except Exception:                                                                  # pragma: no cover
        pass
    ucs = "".join(f"\\qfucode{{{ord(c):X}}}" for c in sorted(used, key=ord))
    (BOOK / "qf_unicode_lst.tex").write_text(
        "% generated by book/facts/make_appA.py (re-run it after the chapters change) -- \\input this after \\usepackage{qfbook}.\n"
        "% PROBLEM: under LuaLaTeX the listings package (v1.9) makes only characters < 256 'active'.  Every other Unicode character in an\n"
        "% lstlisting is typeset at once, AHEAD of the ASCII text listings still holds in its buffer: `(pi / 2)` prints as `pi( / 2)`,\n"
        "% `(R)` as `R()`, and the first non-ASCII character of a listing can float above its first line.\n"
        "% FIX (tested with style=lean, style=py and inside leanbox): make each such character active inside listings and let\n"
        "% listings process it as an ordinary character.  Only characters the monospace font (DejaVu Sans Mono) contains are listed.\n"
        "\\makeatletter\n"
        "\\providecommand\\qfucode[1]{\\catcode\"#1=13\\relax\\begingroup\\lccode`\\~=\"#1\\relax\\lccode`\\/=\"#1\\relax\\lowercase{\\endgroup\\def~{\\lst@ProcessOther/}}}\n"
        f"\\lst@AddToHook{{SelectCharTable}}{{{ucs}}}\n"
        "\\makeatother\n")

    # ---------- namespaces (files for the editor)
    nsmap = {m: info[m]["ns"] for m in mods}
    (HERE / "lean_namespaces.json").write_text(json.dumps(nsmap, indent=1))
    odd = [m for m in mods if nsmap[m] != f"QuantumFluids.{m}"]
    md = ["# True Lean namespace of every library module (generated by facts/make_appA.py)\n",
          f"`\\Lthm{{Module}}{{name}}` prints `QuantumFluids.Module.name`.  That is the TRUE fully qualified name for {len(mods) - len(odd)} of {len(mods)} modules;",
          f"for the {len(odd)} below the namespace declared in the source is different, so the printed name would be wrong.\n",
          "| module | namespace in the source | example fully qualified name |", "|---|---|---|"]
    for m in odd:
        ex = next((d["full"] for d in index[m] if d["kind"] in ("theorem", "lemma")), "")
        md.append(f"| {m} | `{nsmap[m]}` | `{ex}` |")
    (HERE / "lean_namespaces.md").write_text("\n".join(md) + "\n")
    tex = ["% generated by book/facts/make_appA.py -- the TRUE Lean namespace of every library module (a table only).",
           "% qfbook.sty loads this file at its end and defines its own \\Lthm after it, which looks the namespace up here and falls back to",
           f"% QuantumFluids.<Module> for a module not in the table.  {len(odd)} of the {len(mods)} modules do not live in QuantumFluids.<Module>.",
           "\\makeatletter"]
    for m in mods:
        tex.append(f"\\@namedef{{lns@{m}}}{{{nsmap[m]}}}")
    for stem, ds in book_index.items():                       # the book's own Lean files, under their file stem and their short name
        if not ds:
            continue
        ns = max({d["ns"] for d in ds}, key=lambda n: sum(d["ns"] == n for d in ds))
        for key in sorted({stem, re.sub(r"^Ch\d+_", "", stem), stem.replace("_", ""), ns.split(".")[-1]}):
            if key not in nsmap:
                tex.append(f"\\@namedef{{lns@{key}}}{{{ns}}}")
    tex += ["\\makeatother", ""]
    (BOOK / "lean_ns.tex").write_text("\n".join(tex))

    # ---------- citation report
    rep = ["# Citation check: chapters against the library (generated by facts/make_appA.py)\n"]
    rep.append(f"{len(cited)} distinct library declarations are cited (\\Lthm, a statement copied into a leanbox, or a literal QuantumFluids.Module.name).\n")
    if problems:
        rep.append("## Citations that do NOT resolve (wrong module or name)\n")
        for f, mod, name, why, near in problems:
            rep.append(f"* `{f}`: `{mod}` / `{name}` -- {why}" + (f"; did you mean {', '.join(near)}?" if near else ""))
    else:
        rep.append("## All \\Lthm citations resolve.\n")
    wrong_ns = sorted({(f, mod, name) for f, mod, name, why, near in problems if False})
    bad_ns_cites = sorted({(mod, name) for (mod, name) in cited if mod in nsmap and nsmap[mod] != f"QuantumFluids.{mod}"})
    if bad_ns_cites:
        rep.append("\n## Cited library declarations whose naive `\\Lthm` output (QuantumFluids.Module.name) is NOT the real qualified name (the table lean_ns.tex corrects it)\n")
        for mod, name in bad_ns_cites:
            rep.append(f"* `\\Lthm{{{mod}}}{{{name}}}` prints `QuantumFluids.{mod}.{name}`; real name: `{nsmap[mod]}.{name}`")
    if copies:
        rep.append("\n## Statements copied into leanbox environments\n")
        for f, mod, name, st, lib, mine in copies:
            rep.append(f"* `{f}` `{mod}.{name}`: {st}")
            if st == "DIFFERS":
                rep.append(f"    * library: `{lib[:400]}`\n    * chapter: `{mine[:400]}`")
    (HERE / "appA_citation_check.md").write_text("\n".join(rep) + "\n")

    # ---------- appendix A
    T = []
    A = T.append
    audited = [m for m in mods if audit_of(m) and audit_of(m).get("audit") and not audit_of(m).get("firstpass")]
    firstpass = [m for m in mods if audit_of(m) and audit_of(m).get("firstpass")]
    A(r"\chapter{The Lean Library: a Complete Catalogue}\label{appA}")
    A(r"\providecommand{\citedmark}[1]{\textcolor{qfgold}{$\star$}{\fontsize{6}{6}\selectfont\,#1}}")
    A(r"\lstdefinestyle{leancat}{style=lean,basicstyle=\ttfamily\fontsize{8.4}{9.9}\selectfont,columns=fixed,xleftmargin=0.9em,xrightmargin=0pt,"
      r"aboveskip=1.6pt,belowskip=2.8pt,breakindent=1.0em,escapeinside={" + ESC + "}{" + ESC + "}}")
    A(r"\noindent This appendix lists the whole of the Lean~4 library \lean{QuantumFluids} that the book is about: "
      f"{len(mods)} modules, {n_thm} theorems and lemmas, and {n_def} definitions, structures and abbreviations. "
      r"It is \emph{generated} from the sources in \texttt{lean\_src/} by \texttt{book/facts/make\_appA.py} (see appendix~\ref{appB}); "
      r"nothing in it is typed by hand except these paragraphs. Every statement is copied verbatim, line breaks included, up to the "
      r"\texttt{:=} that starts its proof or definition body; the proofs are not reproduced.")
    A(r"\paragraph{How to read an entry.} Each module is headed by one line of its own docstring, by the namespace in which its declarations live "
      r"(for " + f"{len(odd)} of the {len(mods)}" + r" modules this is \emph{not} \texttt{QuantumFluids.}\emph{Module}; see table~\ref{appA:tab-ns}), by the numbers of theorems and of "
      r"definitions, and by its audit status. A gold $\star$ in the margin followed by chapter numbers marks a declaration that those chapters cite "
      r"(through \texttt{\textbackslash Lthm} or by copying its statement). The catalogue is a statement of \emph{what is proved}, not of what is measured: "
      r"to read a statement as physics, go to the chapter that cites it.")
    n_aud = len(audited)
    noprint = [m for m in mods if info[m]["own_print"] == 0]
    A(r"\paragraph{What the audit status means.} \emph{The audit is of the kernel environment, not of the source text.} For each module the book's audit "
      r"driver (\texttt{book/facts/lean\_audit.py}, appendix~\ref{appB}) compiles the module in dependency order against the pinned Mathlib and asks Lean, for "
      r"\emph{every constant the file declares}, which axioms it depends on (\texttt{Lean.collectAxioms}). The status line reports the number of theorem "
      r"constants found, whether \texttt{sorryAx} is reachable, the number of axioms the module declares itself, and the union of the axioms used. "
      r"The three standard axioms are abbreviated $p$ = \texttt{propext}, $c$ = \texttt{Classical.choice}, $q$ = \texttt{Quot.sound}. "
      f"At the time this appendix was generated, {n_aud} of {len(mods)} modules had such an environment audit on file; {len(firstpass)} more carry only the first-pass compile log "
      r"(author-written \texttt{\#print axioms} lines, marked $^\dagger$ in the table); for the remaining {} the status reads ``not re-checked''. ".replace("{}", str(len(mods) - n_aud - len(firstpass))) +
      r"Compiling a module with exit code~0 is not the same as auditing it: " + f"{len(noprint)} modules (" + ", ".join(r"\texttt{" + m + "}" for m in noprint) + ") "
      r"carry no \texttt{\#print axioms} line in their sources, so a compile log of theirs is empty; the environment audit is what supplies their footprint (chapter~\ref{ch10}).")

    # ---- overview table
    A(r"\begin{table}[p]\centering\footnotesize\setlength{\tabcolsep}{3.2pt}")
    A(rf"\caption{{The {len(mods)} modules of the library at a glance. " + r"\emph{thm}: theorems and lemmas; \emph{def}: definitions, structures, abbreviations; "
      r"\emph{audit}: axiom footprint ($p$, $c$, $q$ as in the text; \texttt{n/c}: not re-checked; \texttt{stale}: the file changed after it was audited; \texttt{!}: a non-standard axiom or \texttt{sorryAx}); "
      r"\emph{cited by}: chapters that cite a declaration of the module.}\label{appA:tab-modules}")
    A(r"\begin{tabular}{@{}lrrll@{}}\toprule module & thm & def & audit & cited by \\\midrule")
    for m in mods:
        th = sum(1 for d in index[m] if d["kind"] in ("theorem", "lemma"))
        df = len(index[m]) - th
        chs = sorted({c for (mm, _), cs in cited.items() if mm == m for c in cs}, key=lambda x: (not x.isdigit(), int(x) if x.isdigit() else 0, x))
        a = audit_of(m)
        A(rf"\hyperref[appA:{m}]{{{m}}} & {th} & {df} & {audit_short(a)} & {', '.join(chs) if chs else '--'} \\")
    A(r"\bottomrule\end{tabular}\end{table}")

    # ---- namespace table
    A(r"\begin{table}[t]\centering\footnotesize\setlength{\tabcolsep}{3.2pt}")
    A(r"\caption{Modules whose declarations do \emph{not} live in \texttt{QuantumFluids.}\emph{Module}. The fully qualified name of a theorem is the namespace "
      r"below, a dot, and the name printed in the catalogue.}\label{appA:tab-ns}")
    A(r"\begin{tabular}{@{}ll@{}}\toprule module & namespace in the source \\\midrule")
    for m in odd:
        A(rf"{m} & \texttt{{{tt(nsmap[m])}}} \\")
    A(r"\bottomrule\end{tabular}\end{table}")

    # ---- catalogue
    A(r"\section{The catalogue, module by module}")
    for m in mods:
        th = [d for d in index[m] if d["kind"] in ("theorem", "lemma")]
        df = [d for d in index[m] if d["kind"] not in ("theorem", "lemma")]
        a = audit_of(m)
        A(rf"\subsection{{{m}}}\label{{appA:{m}}}")
        A(r"{\footnotesize\raggedright\texttt{" + tt(info[m]["doc"]) + r"}\par}")
        A(r"{\footnotesize\raggedright\emph{Namespace} \texttt{" + tt(info[m]["ns"]) + rf"}} $\cdot$ {len(th)} theorem{'s' if len(th) != 1 else ''}, {len(df)} definition{'s' if len(df) != 1 else ''} $\cdot$ \emph{{audit}}: {audit_long(a, info[m]['own_print']).replace('`', '').replace('_', r'\_').replace('#', r'\#')}." + r"\par}")
        A(r"\vspace{1pt}")
        for d in index[m]:
            chs = cited.get((m, d["name"]))
            mark = ",".join(sorted(chs, key=lambda x: (not x.isdigit(), int(x) if x.isdigit() else 0, x))) if chs else ""
            A(lst(d["text"], mark))

    # ---- the book's own Lean
    allfiles = sorted(BL.glob("*.lean"))
    newfiles = [f for f in allfiles if not is_negative_control(f) and not is_placeholder(f)]       # theorem files: the only ones that are counted
    ctrlfiles = [f for f in allfiles if is_negative_control(f)]                                     # deliberate negative controls: expected to fail
    phfiles = [f for f in allfiles if is_placeholder(f) and not is_negative_control(f)]
    A(r"\section{Lean written for this book}\label{appA:new}")
    A(r"The files below are \emph{new}: they were written for the book, are not part of the \lean{QuantumFluids} library, and live in \texttt{book/lean/}. "
      r"Each is compiled by its chapter author against the same pinned Mathlib (Lean 4.34.0-rc2), together with the library modules it imports when it says so, and, as the book's rules require, ends with \texttt{\#print axioms} lines. "
      r"Their statements are listed here in the same way as the library's; the status line says whether the book's audit driver has checked them. "
      r"A file that is \emph{meant to fail} (a negative control quoted in a chapter) is never counted as a theorem file or as a failure: such files are listed apart, at the end of this section. "
      r"One more piece of Lean written for the book is not a module: the twenty-odd lines of meta-program that the audit driver appends to a scratch copy of every "
      r"library module (printed in appendix~\ref{appB}); they define no theorem, and they were compiled as part of each of those runs.")
    if not newfiles:
        A(r"\emph{No such file existed when this appendix was generated.}")
    for f in newfiles:
        txt = f.read_text()
        ds = parse_decls(f)
        th = [d for d in ds if d["kind"] in ("theorem", "lemma")]
        a = audit_of(f.stem, "book_")
        own = sum(1 for l in txt.split("\n") if l.startswith("#print axioms"))
        A(rf"\subsection{{{tt(f.stem)}}}")
        A(r"{\footnotesize\raggedright\texttt{" + tt(oneliner(txt, f.stem, skip_meta=True)) + r"}\par}")
        A(r"{\footnotesize\raggedright\emph{File} \texttt{book/lean/" + tt(f.name) + r"} $\cdot$ " + (r"\emph{namespace} \texttt{" + tt(ds[0]["ns"]) + r"} $\cdot$ " if ds else "")
          + rf"{len(th)} theorems, {len(ds) - len(th)} definitions $\cdot$ {own} \texttt{{\#print axioms}} lines in the file $\cdot$ \emph{{audit}}: "
          + (audit_long(a, own).replace('`', '').replace('_', r'\_').replace('#', r'\#') if a else "no audit on file (not re-checked by the book's audit driver)") + r".\par}")
        for d in ds:
            chs = cited.get((f.stem, d["name"]))
            A(lst(d["text"], ",".join(sorted(chs, key=lambda x: (not x.isdigit(), int(x) if x.isdigit() else 0, x))) if chs else ""))
    if ctrlfiles or phfiles:
        A(r"\subsection*{Files that are not counted}")
        for f in ctrlfiles:
            txt = f.read_text()
            cm = re.sub(r"^\s*" + re.escape(f.stem) + r"\.lean\s*(--|—|-|:)?\s*", "", header(txt).strip())
            cm = " ".join(cm.split())
            cm = re.sub(r'"([^"]*)"', "\u201c\\1\u201d", cm)                            # straight double quotes -> typographic quotes (LaTeX would print two closing marks)
            if len(cm) > 340:                                                        # cut at the last sentence end before 340 characters (never in the middle of a sentence)
                cut = cm[:340]; k = max(cut.rfind(". "), cut.rfind(".) "))
                cm = cut[:k + 1] if k > 60 else cut.rsplit(" ", 1)[0] + " ..."
            j = AUD / f"book_{f.stem}.json"
            if j.exists() and audit_is_current(j, f):
                r = json.loads(j.read_text())
                obs = (f"compiled by the audit driver expecting errors: exit code {r['exit']}, {r['errors']} error{'s' if r['errors'] != 1 else ''}; it failed, as intended" if r.get("as_expected")
                       else f"compiled by the audit driver expecting errors, but exit code {r['exit']} and {r['errors']} errors: THE CONTROL DID NOT FAIL AS INTENDED")
            else:
                obs = "not compiled by the audit driver (no current record)"
            A(rf"\paragraph{{{tt(f.stem)} (deliberate negative control).}} {{\footnotesize\raggedright\texttt{{book/lean/{tt(f.name)}}}: {tt(cm)} "
              rf"\emph{{Expected result}}: a compile error. \emph{{Observed}}: {obs}. It declares no theorem, is not audited for axioms, and is counted neither as a failure nor as a file of the book's Lean.\par}}")
        for f in phfiles:
            A(rf"\paragraph{{{tt(f.stem)} (empty placeholder).}} {{\footnotesize\raggedright\texttt{{book/lean/{tt(f.name)}}} says in its header that it is superseded and holds no declaration; "
              r"it exists only because files cannot be deleted in the working environment of the book. It is not counted.\par}")
    (CH / "appA.tex").write_text("\n".join(T) + "\n")
    print(f"appA.tex: {len(mods)} modules, {n_thm} theorems/lemmas, {n_def} other declarations, {len(cited)} cited, {n_aud} audited, {len(newfiles)} new book files (+ {len(ctrlfiles)} negative control, {len(phfiles)} placeholder, not counted)")
    print(f"citation problems: {len(problems)}; leanbox copies: {len(copies)} ({sum(1 for c in copies if c[3] == 'DIFFERS')} differ)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
