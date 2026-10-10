#!/usr/bin/env python3
"""Dependency-ordered, environment-level audit of the Lean library (book appendix A / chapter 10).

WHY THIS REPLACES THE FIRST DRIVER.  The first driver compiled every file of lean_src/ independently with
`lake env lean` inside the OpenAI NavierStokesAndEuler tree.  Nine modules import a sibling module
(`import VortexWinding`, `import DualLength`, ...); the sibling's .olean is not on that tree's search path,
so those nine "failed" with `unknown module prefix` -- a driver artefact, not a Lean error.  And the
`#print axioms` lines it collected are only the ones the authors wrote into the sources: seven modules
(DissipativeVortexDynamics, EinsteinRelation, FrictionKinetic, KTFlow, MatchingScreening, PairPolarisation,
QuasiPeriodicBound) carry none, so their logs were empty although they compiled (exit 0).

WHAT THIS DOES.  (1) Topologically sorts the modules by their `import` lines.  (2) Compiles each module from a
scratch copy to which a small meta-program is appended; the module's .olean is written to a scratch directory that
is put on LEAN_PATH, so dependents resolve.  (3) The appended meta-program walks the kernel environment of the
module (every constant declared in that file, not only the ones somebody remembered to `#print axioms`), calls
`Lean.collectAxioms` on each, and prints one machine-readable line per named theorem, plus a summary
(constants, named theorems, user axioms, whether sorryAx occurs, the union of axioms).  (4) Compiles the umbrella
`QuantumFluids.lean` against those oleans.  The library sources are never modified; nothing is written into the
Lean project trees (no `lake update`, no `lake build`).

Run (heavy: ~1 h on a loaded machine, one Lean process at a time through the shared lock):
    python3 book/facts/lean_audit.py            # all modules
    python3 book/facts/lean_audit.py --resume   # skip modules whose facts/audit/<M>.json exists
    python3 book/facts/lean_audit.py --report   # only rebuild facts/lean_audit.md from the stored JSON
Environment:  QF_AUDIT_WORK = scratch dir (default /mnt/data/xdev-cache/tmp/qf_audit), QF_LOCK = lock file.
"""
from __future__ import annotations
import fcntl, hashlib, json, os, re, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOOK = HERE.parent
ROOT = BOOK.parent
SRC = ROOT / "lean_src"
AUD = HERE / "audit"
TREE = Path("/home/xavkal/xdev/OpenAINavierStokesEuler/NavierStokesAndEuler")      # pinned Mathlib v4.34.0-rc2 (read-only use)
WORK = Path(os.environ.get("QF_AUDIT_WORK", "/mnt/data/xdev-cache/tmp/qf_audit"))
LOCK = os.environ.get("QF_LOCK", "/mnt/data/xdev-cache/tmp/qf_heavy.lock")
TIMEOUT = 2400

SNIPPET = r'''

/-! ## Book audit (appended by book/facts/lean_audit.py to a scratch copy; not part of the library) -/
open Lean Elab Command in
run_cmd do
  let env ← getEnv
  let locals := env.checked.get.constants.foldStage2
    (fun (acc : Array (Name × ConstantInfo)) n ci => acc.push (n, ci)) #[]
  let userName (n : Name) : Name := (privateToUserName? n).getD n
  let isNamed (n : Name) : Bool := !(userName n).isInternal
  let namedThms := locals.filter (fun (n, ci) => ci.isTheorem && isNamed n)
  let namedDefs := locals.filter (fun (n, ci) => (ci matches .defnInfo _) && isNamed n)
  let axDecls := locals.filter (fun (_, ci) => ci matches .axiomInfo _)
  let thmNames : NameSet := namedThms.foldl (fun s (n, _) => s.insert n) {}
  let mut union : NameSet := {}
  let mut rows : Array String := #[]
  for (n, _) in locals do
    let axs ← collectAxioms n
    for a in axs do union := union.insert a
    if thmNames.contains n then
      let line ← match (← findDeclarationRanges? n) with
        | some r => pure (toString r.range.pos.line)
        | none => pure "-1"
      rows := rows.push s!"QFAUDIT|THM|{userName n}|{line}|{", ".intercalate (axs.toList.map toString)}"
  IO.println s!"QFAUDIT|SUMMARY|{locals.size}|{namedThms.size}|{namedDefs.size}|{axDecls.size}|{union.contains ``sorryAx}|{", ".intercalate (union.toList.map toString)}"
  for (n, _) in axDecls do IO.println s!"QFAUDIT|AXIOMDECL|{n}"
  for r in rows do IO.println r
'''

IMPORT = re.compile(r"^import\s+(\S+)", re.M)
THM_SRC = re.compile(r"^[ \t]*(?:@\[[^\]]*\][ \t]*\n?[ \t]*)*(?:(?:private|protected|nonrec)[ \t]+)*(?:theorem|lemma)[ \t]+([^\s:({\[]+)", re.M)
MSG = re.compile(r"^(?P<file>[^:\n]+):(?P<line>\d+):(?P<col>\d+): (?P<sev>error|warning|info)(?:\([^)]*\))?: (?P<msg>.*)$")


def module_list() -> list[str]:
    return sorted(f.stem for f in SRC.glob("*.lean")
                  if not f.name.startswith("_tmp") and f.name not in ("lakefile.lean", "QuantumFluids.lean"))


def order(mods: list[str], priority: list[str]) -> list[str]:
    deps = {m: [d for d in IMPORT.findall((SRC / f"{m}.lean").read_text()) if d in mods] for m in mods}
    out: list[str] = []
    def visit(m: str):
        if m in out: return
        for d in deps[m]: visit(d)
        out.append(m)
    for m in priority + mods:
        if m in mods: visit(m)
    return out


class Lock:
    """The shared heavy-job lock (same file `flock(1)` uses).  POLICY (changed 2026-10-10 after 25 other jobs queued behind this driver): the lock is
    held for ONE module (QF_BATCH_SECONDS, default 1: the batch ends after the first module that has run longer than that) and, after releasing it,
    the driver stays away for QF_YIELD_SECONDS (default 30) so that a waiting job takes the lock first.  An earlier version held it for 25-minute
    batches and re-acquired it with no wait at all ('lock acquired after 0s'), because the releasing process is running and the waiters are not."""
    def __init__(self, path: str):
        self.path, self.fd = path, None
    def acquire(self) -> float:
        t = time.time(); self.fd = open(self.path, "a"); fcntl.flock(self.fd, fcntl.LOCK_EX); return time.time() - t
    def release(self) -> None:
        if self.fd:
            fcntl.flock(self.fd, fcntl.LOCK_UN); self.fd.close(); self.fd = None
    def yield_to_waiters(self) -> None:
        time.sleep(float(os.environ.get("QF_YIELD_SECONDS", 30)))


def compile_one(m: str, snippet: bool = True, srcname: str | None = None, held: bool = False, srcdir: Path | None = None, tag: str = "") -> dict:
    """Compile `<srcdir>/<m>.lean` (default: lean_src) from a scratch copy with the audit program appended; outputs are named `<tag><m>`."""
    (WORK / "src").mkdir(parents=True, exist_ok=True); (WORK / "olean").mkdir(parents=True, exist_ok=True)
    base = srcdir or SRC
    text = (base / f"{m}.lean").read_text() if srcname is None else (base / srcname).read_text()
    scratch = WORK / "src" / f"{tag}{m}.lean"
    scratch.write_text(text + (SNIPPET if snippet else ""))
    inner = (f'TIMEFORMAT="QF_WALL %R"; time nice lake env lean -R {WORK / "src"} -o {WORK / "olean" / (tag + m + ".olean")} {scratch}')
    env = dict(os.environ, LEAN_PATH=str(WORK / "olean"))
    t_req = time.time()
    try:
        cmd = ["bash", "-c", inner] if held else ["flock", LOCK, "bash", "-c", inner]
        r = subprocess.run(cmd, cwd=TREE, env=env, capture_output=True, text=True, timeout=TIMEOUT)
        out, err, rc = r.stdout, r.stderr, r.returncode
    except subprocess.TimeoutExpired as e:
        out, err, rc = (e.stdout or ""), (e.stderr or ""), 124
        out = out.decode() if isinstance(out, bytes) else out
        err = (err.decode() if isinstance(err, bytes) else err) + "\nTIMEOUT"
    total = time.time() - t_req
    wall = re.search(r"QF_WALL ([0-9.]+)", err)
    wall_s = float(wall.group(1)) if wall else None
    log = out + (("\n--- stderr ---\n" + err) if err.strip() else "")
    AUD.mkdir(exist_ok=True)
    (AUD / f"{tag}{m}.log").write_text(log)
    msgs = [MSG.match(l) for l in out.splitlines()]
    msgs = [x.groupdict() for x in msgs if x]
    res = dict(module=tag + m, exit=rc, compile_s=round(wall_s, 1) if wall_s else None, request_to_done_s=round(total, 1),
               errors=sum(1 for x in msgs if x["sev"] == "error"), warnings=sum(1 for x in msgs if x["sev"] == "warning"),
               sorry_warnings=sum(1 for x in msgs if "sorry" in x["msg"]),
               first_error=next((x["msg"][:200] for x in msgs if x["sev"] == "error"), None))
    summ = None; thms = []; axdecls = []
    for l in out.splitlines():
        if not l.startswith("QFAUDIT|"): continue
        p = l.split("|")
        if p[1] == "SUMMARY":
            summ = dict(constants=int(p[2]), named_theorems=int(p[3]), named_defs=int(p[4]), axiom_decls=int(p[5]),
                        sorryAx=(p[6] == "true"), union_axioms=sorted(a.strip() for a in p[7].split(",") if a.strip()))
        elif p[1] == "AXIOMDECL": axdecls.append(p[2])
        elif p[1] == "THM": thms.append(dict(name=p[2], line=int(p[3]), axioms=sorted(a.strip() for a in p[4].split(",") if a.strip())))
    res["audit"] = summ; res["theorems"] = sorted(thms, key=lambda t: (t["line"], t["name"])); res["user_axioms"] = axdecls
    return res


def code_sha(t: str) -> str:
    """Hash of a Lean source with block comments (docstrings included), line comments and white space removed: what an audit depends on.
    A docstring-only edit (e.g. a corrected author list) does not change it, so it does not invalidate an audit; any change of code does."""
    code = re.sub(r"/-.*?-/", "", t, flags=re.S)
    code = "\n".join(re.sub(r"--.*$", "", l) for l in code.split("\n"))
    return hashlib.sha256(re.sub(r"\s+", " ", code).strip().encode()).hexdigest()[:16]


def audit_is_current(j: Path, src: Path) -> bool:
    """True if the audit JSON `j` was made on the present code of `src` (code hash if the JSON has one, else the hash of the full text)."""
    if not j.exists() or not src.exists(): return False
    so = json.loads(j.read_text()).get("source", {}); t = src.read_text()
    if so.get("code_sha256"): return so["code_sha256"] == code_sha(t)
    return so.get("sha256") == hashlib.sha256(t.encode()).hexdigest()[:16]


def source_facts(m: str) -> dict:
    p = SRC / f"{m}.lean"; t = p.read_text()
    code = re.sub(r"/-.*?-/", "", t, flags=re.S)                    # drop block comments / docstrings
    code = "\n".join(re.sub(r"--.*$", "", l) for l in code.split("\n"))
    return dict(sha256=hashlib.sha256(t.encode()).hexdigest()[:16], code_sha256=code_sha(t), lines=t.count("\n") + 1,
                imports=[d for d in IMPORT.findall(t)],
                theorem_decls=len(THM_SRC.findall(code)),
                print_axioms_lines=sum(1 for l in t.split("\n") if l.startswith("#print axioms")),
                has_sorry_text=bool(re.search(r"\bsorry\b", code)), has_axiom_text=bool(re.search(r"^\s*axiom\s", code, re.M)))


def match_source(m: str, res: dict) -> dict:
    """Which env theorems are source-declared (name + line agree with a theorem/lemma keyword), which are auto-generated."""
    t = (SRC / f"{m}.lean").read_text().split("\n")
    src_names = []
    code = "\n".join(t)
    for mm in THM_SRC.finditer(re.sub(r"/-.*?-/", lambda x: re.sub(r"[^\n]", " ", x.group(0)), code, flags=re.S)):
        src_names.append(mm.group(1))
    env_names = [th["name"] for th in res["theorems"] if th["line"] >= 0]       # theorems generated by Lean have no source position and are not compared
    unmatched_src = [n for n in src_names if not any(e == n or e.endswith("." + n) for e in env_names)]
    gen = [e for e in env_names if not any(e == n or e.endswith("." + n) for n in src_names)]
    return dict(source_theorem_names=len(src_names), source_unmatched=unmatched_src, env_not_in_source=gen)


def run_all(resume: bool) -> None:
    mods = module_list()
    priority = ["DissipativeVortexDynamics", "EinsteinRelation", "FrictionKinetic", "KTFlow", "MatchingScreening", "PairPolarisation", "QuasiPeriodicBound",
                "ContinuumWinding", "Fricke", "PhononSpecificHeat", "QuantizedCirculation", "ScaleResolvedWinding", "SectorTemperature", "ShellHamiltonian", "SigmaRule", "TopologicalProtection",
                # second tier: PhononSeries (cited in the Godfrin box; its docstring was corrected 2026-10-10, so its audit must be redone), Villani (the two `@[simp] theorem`s that the
                # generators never saw), and the modules that other chapters of the book cite
                "PhononSeries", "Villani", "ZeroSound", "HeliumKinematics", "GPGalerkin"]
    seq = order(mods, priority)
    print("order:", seq, flush=True)
    AUD.mkdir(exist_ok=True)
    pending = [m for m in seq if not (resume and audit_is_current(AUD / f"{m}.json", SRC / f"{m}.lean"))]
    only = [x for x in os.environ.get("QF_ONLY", "").split(",") if x]                  # QF_ONLY=Villani,ZeroSound restricts the run to those modules (their imports must already be compiled)
    if only: pending = [m for m in pending if m in only]
    for m in seq:
        if m not in pending: print("skip", m, flush=True)
    lock = Lock(LOCK); batch_s = float(os.environ.get("QF_BATCH_SECONDS", 1)); i = 0
    while i < len(pending):
        waited = lock.acquire(); t0 = time.time(); print(f"[lock acquired after {waited:.0f}s]", flush=True)
        try:
            while i < len(pending) and (i == 0 or time.time() - t0 < batch_s):
                m = pending[i]; i += 1
                t = time.time(); res = compile_one(m, held=True)
                res["source"] = source_facts(m); res["match"] = match_source(m, res)
                res["when"] = time.strftime("%Y-%m-%d %H:%M:%S")
                (AUD / f"{m}.json").write_text(json.dumps(res, indent=1))
                a = res["audit"] or {}
                print(f"{m:28s} exit={res['exit']} err={res['errors']} thm={a.get('named_theorems')} sorryAx={a.get('sorryAx')} axioms={a.get('union_axioms')} "
                      f"compile={res['compile_s']}s", flush=True)
        finally:
            lock.release()
        if i < len(pending): lock.yield_to_waiters()
    # umbrella: only when every module of the library has a current audit (its compiled siblings are then all on the scratch path); one more hold of the lock
    if only or any(not audit_is_current(AUD / f"{m}.json", SRC / f"{m}.lean") for m in mods):
        print("umbrella skipped: the library is not completely audited yet", flush=True); report(); return
    um = SRC / "QuantumFluids.lean"
    (WORK / "src").mkdir(parents=True, exist_ok=True)
    (WORK / "src" / "QuantumFluids.lean").write_text(um.read_text())
    inner = f'TIMEFORMAT="QF_WALL %R"; time nice lake env lean -R {WORK / "src"} {WORK / "src" / "QuantumFluids.lean"}'
    r = subprocess.run(["flock", LOCK, "bash", "-c", inner], cwd=TREE, env=dict(os.environ, LEAN_PATH=str(WORK / "olean")), capture_output=True, text=True, timeout=TIMEOUT)
    (AUD / "QuantumFluids_umbrella.log").write_text(r.stdout + r.stderr)
    (AUD / "QuantumFluids_umbrella.json").write_text(json.dumps(dict(exit=r.returncode, imports=IMPORT.findall(um.read_text())), indent=1))
    print("umbrella exit", r.returncode, flush=True)
    report()


def report() -> None:
    rows = [json.loads(p.read_text()) for p in sorted(AUD.glob("*.json")) if p.name not in ("QuantumFluids_umbrella.json", "summary.json") and not p.name.startswith("book_")]
    rows.sort(key=lambda r: r["module"])
    um = json.loads((AUD / "QuantumFluids_umbrella.json").read_text()) if (AUD / "QuantumFluids_umbrella.json").exists() else None
    ver = subprocess.run(["lake", "env", "lean", "--version"], cwd=TREE, capture_output=True, text=True).stdout.strip()
    std = {"propext", "Classical.choice", "Quot.sound"}
    L = ["# Lean audit of the QuantumFluids library (environment level)\n",
         f"Generated by `book/facts/lean_audit.py`.  Toolchain: `{ver}`; Mathlib v4.34.0-rc2 (the OpenAI tree's copy, read-only).",
         "Each module is compiled from a scratch copy in dependency order (siblings resolved through scratch .olean files); a meta-program appended to the",
         "copy calls `Lean.collectAxioms` on **every constant declared in the module** and reports the union of axioms.  `sorryAx` = a `sorry` is reachable.",
         "Columns: *thms* = theorem constants of the kernel environment that have a source position (i.e. declared in the file); *auto* = theorem constants generated by Lean itself",
         "(equation lemmas, structure projections' injectivity lemmas, ...; they have no source position); *src* = `theorem`/`lemma` keywords found in the source text; *own #print* =",
         "`#print axioms` lines the author wrote in the source (a module can have a clean footprint and still carry none); *s* = Lean wall time in seconds on a shared",
         "machine (load 8-35), not a benchmark.\n",
         "| module | exit | errors | thms | auto | src | own #print | user axioms | sorryAx | axiom footprint | s |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    tot = dict(mods=0, ok=0, thms=0, auto=0, src=0, own=0, sorry=0, useraxioms=0, nonstd=0)
    for r in rows:
        a = r.get("audit") or {}
        fp = a.get("union_axioms") or []
        nonstd = [x for x in fp if x not in std]
        decl = sum(1 for t in r.get("theorems", []) if t["line"] >= 0); auto = sum(1 for t in r.get("theorems", []) if t["line"] < 0)
        tot["mods"] += 1; tot["ok"] += int(r["exit"] == 0 and r["errors"] == 0); tot["thms"] += decl; tot["auto"] += auto
        tot["src"] += r["source"]["theorem_decls"]; tot["own"] += r["source"]["print_axioms_lines"]
        tot["sorry"] += int(bool(a.get("sorryAx"))); tot["useraxioms"] += a.get("axiom_decls", 0) or 0; tot["nonstd"] += int(bool(nonstd))
        L.append(f"| {r['module']} | {r['exit']} | {r['errors']} | {decl} | {auto} | {r['source']['theorem_decls']} | {r['source']['print_axioms_lines']} | "
                 f"{a.get('axiom_decls', '?')} | {a.get('sorryAx', '?')} | {', '.join(fp) if fp else '(none)'} | {r['compile_s']} |")
    L.append("")
    L.append(f"**Totals**: {tot['mods']} modules, {tot['ok']} compile with exit 0 and no error; {tot['thms']} named theorem constants "
             f"(+ {tot['auto']} generated by Lean; {tot['src']} theorem/lemma keywords in the sources); {tot['own']} author-written `#print axioms` lines; "
             f"{tot['useraxioms']} user-declared axioms; {tot['sorry']} modules in which `sorryAx` is reachable; {tot['nonstd']} modules whose footprint leaves {{propext, Classical.choice, Quot.sound}}.")
    if um: L.append(f"\nUmbrella `QuantumFluids.lean` ({len(um['imports'])} imports) compiled against the scratch oleans: exit {um['exit']}.")
    for r in rows: r["match"] = match_source(r["module"], r)                      # recompute with the current rule (declared theorems only)
    mism = [(r["module"], r["match"]) for r in rows if r["match"]["source_unmatched"] or r["match"]["env_not_in_source"]]
    if mism:
        L.append("\n## Source/kernel mismatches (theorem names found in only one of the two)\n")
        for m, d in mism: L.append(f"* {m}: in source but no kernel theorem: {d['source_unmatched']}; kernel theorem not in source text (auto-generated?): {d['env_not_in_source']}")
    ball = [json.loads(p.read_text()) for p in sorted(AUD.glob("book_*.json"))]
    brows = [r for r in ball if not r.get("expect_fail")]
    bctl = [r for r in ball if r.get("expect_fail")]
    if bctl:
        L.append("\n## Deliberate negative controls among the book's Lean files (compiled expecting errors; never counted as failures or as theorem files)\n")
        L.append("| file | exit | errors | failed as intended | first error | audited |"); L.append("|---|---|---|---|---|---|")
        for r in bctl:
            L.append(f"| {r['module'][5:]} | {r['exit']} | {r['errors']} | {'yes' if r.get('as_expected') else 'NO - the control did not fail'} | {(r.get('first_error') or '')[:90]} | {r.get('when', '')} |")
    if brows:
        L.append("\n## The book's own Lean files (book/lean/, `python3 book/facts/lean_audit.py --book`)\n")
        L.append("| file | exit | errors | thms | auto | src | own #print | user axioms | sorryAx | axiom footprint | s | audited |"); L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for r in brows:
            a = r.get("audit") or {}
            decl = sum(1 for t in r.get("theorems", []) if t["line"] >= 0); auto = sum(1 for t in r.get("theorems", []) if t["line"] < 0)
            L.append(f"| {r['module'][5:]} | {r['exit']} | {r['errors']} | {decl} | {auto} | {r['source']['theorem_decls']} | {r['source']['print_axioms_lines']} | {a.get('axiom_decls', '?')} | {a.get('sorryAx', '?')} | "
                     f"{', '.join(a.get('union_axioms') or []) or '(none)'} | {r['compile_s']} | {r.get('when', '')} |")
    (HERE / "lean_audit.md").write_text("\n".join(L) + "\n")
    (AUD / "summary.json").write_text(json.dumps(dict(totals=tot, toolchain=ver, modules=[dict(module=r["module"], exit=r["exit"], errors=r["errors"], compile_s=r["compile_s"],
        named_theorems=sum(1 for t in r.get("theorems", []) if t["line"] >= 0), auto_theorems=sum(1 for t in r.get("theorems", []) if t["line"] < 0), src_theorems=r["source"]["theorem_decls"], own_print=r["source"]["print_axioms_lines"],
        sorryAx=(r.get("audit") or {}).get("sorryAx"), user_axioms=(r.get("audit") or {}).get("axiom_decls"), footprint=(r.get("audit") or {}).get("union_axioms"),
        imports=r["source"]["imports"]) for r in rows]), indent=1))
    print("wrote", HERE / "lean_audit.md")


def _header(path: Path) -> str:
    return path.read_text()[:2500]


def is_negative_control(path: Path) -> bool:
    """A file that is MEANT to fail (a negative control quoted in a chapter): its name contains 'NegativeControl', or its header says it is meant to fail.
    Such a file is never counted as a theorem file or as a failure: the audit compiles it expecting errors (`run_book`)."""
    return "negativecontrol" in path.stem.lower() or re.search(r"meant\s+to\s+fail", _header(path), re.I) is not None


def is_placeholder(path: Path) -> bool:
    """An empty file kept only because files cannot be deleted in the working environment (its header says SUPERSEDED)."""
    return re.search(r"\bSUPERSEDED\b", _header(path)) is not None


def book_stems() -> list[str]:
    """The book's own Lean files that the audit covers as theorem files: all of book/lean/*.lean except negative controls and placeholders."""
    BL = BOOK / "lean"
    return [f.stem for f in sorted(BL.glob("*.lean")) if not is_negative_control(f) and not is_placeholder(f)]


def book_controls() -> list[str]:
    """The book's deliberate negative controls (compiled expecting errors)."""
    BL = BOOK / "lean"
    return [f.stem for f in sorted(BL.glob("*.lean")) if is_negative_control(f)]


def book_placeholders() -> list[str]:
    BL = BOOK / "lean"
    return [f.stem for f in sorted(BL.glob("*.lean")) if is_placeholder(f) and not is_negative_control(f)]


def run_book(resume: bool) -> None:
    """Environment audit of the book's own Lean files (book/lean/*.lean; they import Mathlib only).  Theorem files get the same appended program as the library
    modules.  A negative control (a file that is meant to fail) is compiled WITHOUT the program and EXPECTED to fail: the record says whether it did.  A placeholder
    (SUPERSEDED) is skipped.  Outputs: facts/audit/book_<stem>.{json,log}.  One module per hold of the shared lock, as for the library."""
    BL = BOOK / "lean"
    stems = book_stems(); ctrls = book_controls()
    work = [(m, "file") for m in stems if not (resume and audit_is_current(AUD / f"book_{m}.json", BL / f"{m}.lean"))] + \
           [(m, "control") for m in ctrls if not (resume and audit_is_current(AUD / f"book_{m}.json", BL / f"{m}.lean"))]
    print("book files:", stems, "negative controls:", ctrls, "placeholders (skipped):", book_placeholders(), "pending:", [m for m, _ in work], flush=True)
    lock = Lock(LOCK); batch_s = float(os.environ.get("QF_BATCH_SECONDS", 1)); i = 0
    while i < len(work):
        waited = lock.acquire(); t0 = time.time(); print(f"[lock acquired after {waited:.0f}s]", flush=True)
        try:
            while i < len(work) and (i == 0 or time.time() - t0 < batch_s):
                m, kind = work[i]; i += 1
                res = compile_one(m, snippet=(kind == "file"), held=True, srcdir=BL, tag="book_")
                text = (BL / f"{m}.lean").read_text()
                code = re.sub(r"/-.*?-/", "", text, flags=re.S)
                res["source"] = dict(sha256=hashlib.sha256(text.encode()).hexdigest()[:16], code_sha256=code_sha(text), lines=text.count("\n") + 1, imports=IMPORT.findall(text),
                                     theorem_decls=len(THM_SRC.findall(code)), print_axioms_lines=sum(1 for l in text.split("\n") if l.startswith("#print axioms")))
                res["when"] = time.strftime("%Y-%m-%d %H:%M:%S")
                res["kind"] = kind
                if kind == "control":
                    res["expect_fail"] = True
                    log = (AUD / f"book_{m}.log").read_text()
                    res["import_failure"] = bool(re.search(r"unknown (module|package)|object file .* does not exist|failed to read file", log))   # failing to import is not the intended failure
                    res["as_expected"] = bool(res["exit"] != 0 and res["errors"] >= 1 and not res["import_failure"])   # a negative control that compiles (or fails for the wrong reason) is itself a defect
                    (AUD / f"book_{m}.json").write_text(json.dumps(res, indent=1))
                    print(f"book_{m:26s} NEGATIVE CONTROL, expected to fail: exit={res['exit']} errors={res['errors']} as_expected={res['as_expected']} first_error={res['first_error']!r}", flush=True)
                    continue
                (AUD / f"book_{m}.json").write_text(json.dumps(res, indent=1))
                a = res["audit"] or {}
                print(f"book_{m:26s} exit={res['exit']} err={res['errors']} thm={a.get('named_theorems')} sorryAx={a.get('sorryAx')} user_axioms={a.get('axiom_decls')} axioms={a.get('union_axioms')} compile={res['compile_s']}s", flush=True)
        finally:
            lock.release()
        if i < len(work): lock.yield_to_waiters()


def controls() -> None:
    """Negative control of the auditor: run the appended meta-program on facts/audit_controls/AuditControls.lean, which plants a sorry (direct,
    inherited and in a private theorem), an axiom of its own, a native_decide, and clean theorems.  Needs only `import Lean`: seconds."""
    d = HERE / "audit_controls"
    (d / "AuditControls_audited.lean").write_text((d / "AuditControls.lean").read_text() + SNIPPET)
    r = subprocess.run(["lake", "env", "lean", str(d / "AuditControls_audited.lean")], cwd=TREE, capture_output=True, text=True)
    (d / "AuditControls.out").write_text(r.stdout + r.stderr)
    print(r.stdout + r.stderr)


if __name__ == "__main__":
    if "--controls" in sys.argv: controls()
    elif "--book" in sys.argv: run_book("--resume" in sys.argv)
    elif "--report" in sys.argv: report()
    else: run_all("--resume" in sys.argv)
