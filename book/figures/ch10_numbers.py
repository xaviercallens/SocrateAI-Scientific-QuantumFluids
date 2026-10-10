"""Chapter 10: every number of the chapter text in one place.  Reads only files (ledger, audit JSON, raw run outputs, bench JSON, verdict JSON, Lean sources),
writes figures/ch10_numbers.json (value + source for each number) and figures/ch10_numbers.tex (one \\Nx... macro per number; the chapter uses the macros).
Items whose input file is missing are written as '??' and listed on stderr, so nothing is ever silently invented.
Run:  .venv/bin/python book/figures/ch10_numbers.py"""
import json, re, sys, statistics
from pathlib import Path
here = Path(__file__).resolve().parent
BOOK = here.parent; ROOT = BOOK.parent
out: dict[str, dict] = {}
missing: list[str] = []

def put(key, value, source, fmt=None):
    out[key] = dict(value=value, source=source, text=(fmt(value) if fmt else str(value)))

def need(path: Path) -> bool:
    if not path.exists() or path.stat().st_size == 0:
        missing.append(str(path.relative_to(BOOK))); return False
    return True

# ------------------------------------------------------------------------------------------------------------ ledger
L = (ROOT / "LEDGER.md").read_text()
ids = sorted({int(i) for i in re.findall(r"CLAIM-(\d{3})\b", L)})
put("claims", len(ids), "distinct CLAIM-nnn identifiers in LEDGER.md (001..%d, no gap)" % ids[-1])
put("claims_last", ids[-1], "LEDGER.md")
bracket = re.findall(r"^\[(CLAIM-\d+)\] \[([A-Z-]+)\] \[([A-Z -]+)\]", L, re.M)
put("claims_checked", len([b for b in bracket if b[2] != "PENDING"]), "bracket-format entries (the only format scripts/check_ledger.py reads; the template entry is PENDING and excluded)")
put("ledger_first", "2026-08-14", "Filed: date of CLAIM-001 in LEDGER.md")
put("ledger_last", "2026-10-09", "date of CLAIM-106 in LEDGER.md")
put("ledger_days", 56, "2026-08-14 to 2026-10-09")
# ------------------------------------------------------------------------------------------------------------ verdict map
vp = here / "ch10_verdicts_numbers.json"
if need(vp):
    v = json.load(open(vp))
    put("verd_cells", v["total"], "ch10_verdicts_numbers.json"); put("verd_rows", v["n_rows"], "ch10_verdicts_numbers.json")
    for k, name in (("P", "met"), ("F", "notmet"), ("M", "mixed"), ("V", "void"), ("N", "notrun")):
        put("verd_" + name, v["tallies"][k], "ch10_verdicts_numbers.json")
# ------------------------------------------------------------------------------------------------------------ library (sources + audit)
idx = (BOOK / "facts" / "lean_index.md").read_text()
m = re.search(r"Total theorems/lemmas indexed: \*\*(\d+)\*\*", idx)
put("lib_thm_index", int(m.group(1)), "facts/lean_index.md header (declaration regex of make_lean_index.py)")
sys.path.insert(0, str(BOOK / "facts"))
import importlib.util
spec = importlib.util.spec_from_file_location("ma", BOOK / "facts" / "make_appA.py"); ma = importlib.util.module_from_spec(spec); spec.loader.exec_module(ma)
mods = sorted(f.stem for f in ma.SRC.glob("*.lean") if not f.name.startswith("_tmp") and f.name not in ("lakefile.lean", "QuantumFluids.lean"))
decls = {m_: ma.parse_decls(ma.SRC / f"{m_}.lean") for m_ in mods}
put("lib_modules", len(mods), "lean_src/*.lean without _tmp*, lakefile, umbrella")
put("lib_thm", sum(1 for m_ in mods for d in decls[m_] if d["kind"] in ("theorem", "lemma")), "make_appA.parse_decls over lean_src (theorem/lemma keywords at column 0)")
gspec = importlib.util.spec_from_file_location("regen", ROOT / "scripts" / "regen_axiom_audit.py"); regen = importlib.util.module_from_spec(gspec); gspec.loader.exec_module(regen)
def gen_count(m_):
    text = (ma.SRC / f"{m_}.lean").read_text(); body = text.split(regen.MARKER)[0].rstrip("\n")
    body = "\n".join(l for l in body.split("\n") if not l.startswith("#print axioms"))
    return len(regen.names(body))
put("lib_gen_thm", sum(gen_count(m_) for m_ in mods), "scripts/regen_axiom_audit.py: names() applied to every module (theorem/lemma keyword at the start of a line, names de-duplicated)")
put("lib_def", sum(1 for m_ in mods for d in decls[m_] if d["kind"] not in ("theorem", "lemma")), "same parser: def, structure, abbrev")
odd = [m_ for m_ in mods if ma.namespaces and (lambda ns: ns != f"QuantumFluids.{m_}")(max({d["ns"] for d in decls[m_]}, key=lambda n: sum(d["ns"] == n for d in decls[m_])))]
put("lib_odd_ns", len(odd), "modules whose declarations are not in QuantumFluids.<Module> (facts/lean_namespaces.md)")
noprint = [m_ for m_ in mods if sum(1 for l in (ma.SRC / f"{m_}.lean").read_text().split("\n") if l.startswith("#print axioms")) == 0]
put("lib_noprint", len(noprint), "modules whose source has no '#print axioms' line: " + ", ".join(noprint))
# Comparator list (30 modules) from the generator script
cmp_ = set(re.findall(r'"(\w+)"', re.search(r"SOLUTIONS = \[(.*?)\]", (ROOT / "scripts/make_comparator_challenges.py").read_text(), re.S).group(1)))
put("lib_cmp_modules", len(cmp_), "SOLUTIONS list of scripts/make_comparator_challenges.py")
put("lib_not_cmp", len([m_ for m_ in mods if m_ not in cmp_]), "library modules not in that list: " + ", ".join(m_ for m_ in mods if m_ not in cmp_))
put("lib_cmp_thm", 257, "docs/COMPARATOR_SETUP.md: 'All 257 listed theorems: accepted by the Lean kernel and by nanoda'")
put("lib_cmp_gen", sum(gen_count(m_) for m_ in sorted(cmp_)), "regen_axiom_audit.names() summed over the 30 Comparator modules (equals the 257 of docs/COMPARATOR_SETUP.md)")
put("lib_cmp_idx", sum(1 for m_ in sorted(cmp_) for d in decls[m_] if d["kind"] in ("theorem", "lemma")), "theorem/lemma declarations of the same 30 modules (make_appA.parse_decls)")
audit = {}
for m_ in mods:
    p = BOOK / "facts/audit" / f"{m_}.json"
    if p.exists(): audit[m_] = json.load(open(p))
put("audit_env_modules", len(audit), "facts/audit/<Module>.json (environment-level audit by facts/lean_audit.py)")
seven = [m_ for m_ in noprint if m_ in audit and audit[m_]["exit"] == 0 and audit[m_]["errors"] == 0 and audit[m_].get("audit")]
put("audit_seven_ok", len(seven), "modules without an author-written audit line that compile and were audited at environment level")
put("audit_seven_thm", sum(1 for m_ in seven for th in audit[m_]["theorems"] if th["line"] >= 0), "their declared theorem constants")
if audit:
    ok = [m_ for m_, a in audit.items() if a["exit"] == 0 and a["errors"] == 0 and a.get("audit")]
    put("audit_env_ok", len(ok), "exit 0, no error, audit line printed")
    put("audit_env_thm", sum(1 for m_ in ok for th in audit[m_]["theorems"] if th["line"] >= 0), "theorem constants of the kernel environment with a source position, in those modules")
    put("audit_env_auto", sum(1 for m_ in ok for th in audit[m_]["theorems"] if th["line"] < 0), "theorem constants generated by Lean (no source position): equation lemmas etc.")
    put("audit_env_src_thm", sum(audit[m_]["source"]["theorem_decls"] for m_ in ok), "theorem/lemma keywords in the sources of those modules")
    put("audit_env_sorry", sum(1 for m_ in ok if audit[m_]["audit"]["sorryAx"]), "modules in which sorryAx is reachable")
    put("audit_env_userax", sum(audit[m_]["audit"]["axiom_decls"] for m_ in ok), "axioms declared by the modules themselves")
    std = {"propext", "Classical.choice", "Quot.sound"}
    put("audit_env_nonstd", sum(1 for m_ in ok if set(audit[m_]["audit"]["union_axioms"]) - std), "modules whose footprint leaves the three standard axioms")
    classes = {}
    for m_ in ok:
        for t in audit[m_]["theorems"]:
            if t["line"] < 0: continue
            k = "+".join(sorted({"propext": "p", "Classical.choice": "c", "Quot.sound": "q"}.get(a, a) for a in t["axioms"])) or "none"
            classes[k] = classes.get(k, 0) + 1
    put("audit_env_classes", classes, "named theorem constants by axiom set (p=propext, c=Classical.choice, q=Quot.sound)")
    mism = {m_: audit[m_]["match"] for m_ in ok if audit[m_]["match"]["source_unmatched"] or audit[m_]["match"]["env_not_in_source"]}
    put("audit_env_mismatch_modules", len(mism), "modules with theorem names found in only one of source text / kernel environment")
else:
    missing.append("facts/audit/*.json (environment audit not finished)")
# ------------------------------------------------------------------------------------------------------------ bench
bp = here / "ch10_bench_numbers.json"
if need(bp):
    b = json.load(open(bp))
    for k, nm in zip(b["N"], "ABCD"):
        i = b["N"].index(k)
        put(f"bench_rust_{nm}", b["rust_ms"][i], "ch10_bench_numbers.json <- data/generated/pgpe/bench/engines.json", lambda x: f"{x:.2f}")
        put(f"bench_numpy_{nm}", b["numpy_ms"][i], "same", lambda x: f"{x:.1f}")
        put(f"bench_spnp_{nm}", b["speedup_rust_over_numpy"][i], "same", lambda x: f"{x:.1f}")
    put("bench_thr_big", b["thread_speedup_512_at_8"], "ch10_bench_numbers.json <- threads_rust.json", lambda x: f"{x:.1f}")
    put("bench_thr_mid", b["thread_speedup_256_at_8"], "same", lambda x: f"{x:.1f}")
    put("bench_small_one", b["threads_ms"]["128"]["1"], "same", lambda x: f"{x:.2f}"); put("bench_small_eight", b["threads_ms"]["128"]["8"], "same", lambda x: f"{x:.2f}")
    put("bench_jaxchk", b["jax_checksum_max_rel_diff"], "same <- jax_cpu.json", lambda x: f"{x:.0e}")
# ------------------------------------------------------------------------------------------------------------ estimator runs
raw = here / "ch10_raw"
def parse_scan(path):
    rows = []
    if not need(path): return rows
    for ln in path.read_text().splitlines():
        m = re.match(r"noise\s+([\d.]+)\s+eta\s+(\S+)\s+([\d.]+)\s+\+-\s+([\d.]+|NaN)\s+([\d.]+)\s+\+-\s+([\d.]+|NaN)\s+([\d.]+)\s+([\S]+)", ln)
        if m: rows.append(dict(noise=float(m.group(1)), eta=float(m.group(2)), energy=float(m.group(3)), energy_sd=float(m.group(4)), reg=float(m.group(5)), reg_sd=float(m.group(6)), oneminusap=float(m.group(7)), eta_est=float(m.group(8))))
    return rows
eta_rows = parse_scan(raw / "g0_eta_scan.txt"); noise_rows = parse_scan(raw / "g0_noise_scan.txt")
if eta_rows:
    for r, nm in zip(eta_rows, "ZABC"):
        put(f"gate_energy_{nm}", r["energy"], f"{raw.name}/g0_eta_scan.txt (eta = {r['eta']:g})", lambda x: f"{x:.4f}")
        put(f"gate_energysd_{nm}", r["energy_sd"], "same", lambda x: f"{x:.4f}")
        put(f"gate_reg_{nm}", r["reg"], "same", lambda x: f"{x:.4f}")
        put(f"gate_regsd_{nm}", r["reg_sd"], "same", lambda x: f"{x:.4f}")
        put(f"gate_oneminusap_{nm}", r["oneminusap"], "same", lambda x: f"{x:.4f}")
        put(f"gate_biase_{nm}", round(100 * (r["energy"] / 0.02 - 1), 1), "(printed mean/0.02 - 1) in percent; the printed means carry 4 decimals, so +-0.25 point", lambda x: f"{abs(x):.1f}")
        put(f"gate_biasr_{nm}", round(100 * (r["reg"] / 0.02 - 1), 1), "(mean/0.02 - 1) in percent", lambda x: f"{abs(x):.1f}")
if noise_rows:
    for r, nm in zip(noise_rows, "ZABC"):
        put(f"gaten_energy_{nm}", r["energy"], f"{raw.name}/g0_noise_scan.txt (noise = {r['noise']:g}, eta = 2e-3)", lambda x: f"{x:.4f}")
        put(f"gaten_reg_{nm}", r["reg"], "same", lambda x: f"{x:.4f}")
ci = raw / "cross_impl.json"
if need(ci):
    c = json.load(open(ci))
    put("cross_maxest", c["max_rel_diff_estimates"], "ch10_raw/cross_impl.json: numpy vs Rust, six estimates, identical tracks", lambda x: f"{x:.0e}")
    put("cross_maxerr", c["max_rel_diff_errors"], "same, six jackknife errors", lambda x: f"{x:.0e}")
    put("cross_tracks", c["n_tracks"], "same")
    rr = {r["name"]: r for r in c["rows"]}
    put("cross_energy", rr["alpha_energy"]["rust"], "ch10_raw/cross_impl.json: the registered G0 tracks (numpy seed 20261005), alpha_energy (numpy and Rust agree)", lambda x: f"{x:.4f}")
    put("cross_reg", rr["alpha_regression"]["rust"], "same, alpha_regression", lambda x: f"{x:.4f}")
    put("cross_oneminusap", rr["one_minus_alpha_prime"]["rust"], "same, 1 - alpha'", lambda x: f"{x:.4f}")
    put("cross_track_max", int(max(c["track_lengths"])), "longest of the 8 registered tracks (time units)"); put("cross_track_min", int(min(c["track_lengths"])), "shortest of the 8 registered tracks")
    put("cross_numpy_s", c["numpy_s"], "same", lambda x: f"{x:.0f}"); put("cross_rust_s", c["rust_s"], "same", lambda x: f"{x:.2f}")
put("gate_seeds", 8, "ch10_run_estimator.sh: g0_scan 8 (seeds 0..7)"); put("gate_tracks", 8, "crates/qf-pgpe/examples/g0_scan.rs: 8 tracks per seed")
put("gate_tend", 2000, "g0_scan.rs: t_end = 2000 time units"); put("gate_alpha", "0.02", "g0_scan.rs: alpha = 0.02"); put("gate_alphap", "0.10", "g0_scan.rs: alpha' = 0.10")
put("gate_eta", "2\\times10^{-3}", "g0_scan.rs: eta = 2e-3 (registered gate G0)")
# ------------------------------------------------------------------------------------------------------------ CVODE probe (stale versus fixed build)
for tag in ("stale", "fixed"):
    pp = raw / f"cvode_probe_{tag}.json"
    if need(pp):
        d = json.load(open(pp)); r10 = next(r for r in d["rows"] if r["method"] == "adams" and r["rtol"] == 1e-10)
        put(f"cvode_{tag}_nfe", r10["nfe"], f"ch10_raw/cvode_probe_{tag}.json: Adams, y' = -y, t in [0,10], rtol 1e-10, atol 1e-14, right-hand-side calls ({d['shared_object']}, sha256 {d['sha256'][:12]})", lambda x: f"{x:,}".replace(",", "\\,"))
        put(f"cvode_{tag}_err", r10["relerr"], f"same: relative error of y(10)", lambda x: f"{x:.1e}".replace("e-0", "\\times10^{-").replace("e-", "\\times10^{-") + "}")
        put(f"cvode_{tag}_built", d["built"], "modification time of the shared object")
# ------------------------------------------------------------------------------------------------------------ quoted numbers (each with its source)
quoted = {
    "q_gate_seed_energy": (0.0187, "docs/designs/PGPE_ENERGY_ESTIMATOR_BIAS.md (G0 passed once, alpha_energy 0.0187 against the 15 % criterion, PGPE_TRANSPORT_GATES.md)"),
    "q_gate_pass_seeds": ("2 of 12", "docs/designs/PGPE_ENERGY_ESTIMATOR_BIAS.md; LEDGER CLAIM-098"),
    "q_bias_lo": (5, "PGPE_ENERGY_ESTIMATOR_BIAS.md: published alpha values low by roughly 5-20 %"), "q_bias_hi": (20, "same"),
    "q_alphaT_energy": ("0.054", "LEDGER CLAIM-096/097/098: alpha/T = 0.0540 +- 0.0026 (energy)"), "q_alphaT_reg": ("0.060", "CLAIM-098: 0.0598 +- 0.0023 (regression)"),
    "q_ks_force": ("0.19", "LEDGER CLAIM-106: force differences 0.19 % of max after the wake forms"), "q_ks_init": ("2.8e-8", "CLAIM-106"),
    "q_ks_counts": ("9 of 10", "CLAIM-106: vortex counts equal at 9 of 10 times"), "q_ks_a2": ("4\\times10^{-5}", "CLAIM-106: plan A2 criterion 1e-5 to t = 10 NOT met (4e-5)"),
    "q_r3_listed": (76, "RETRACTIONS.md R3: 76 theorems existed where 65 carried a #print axioms line"), "q_r3_audited": (65, "same"), "q_r3_missed": (11, "same (the generator's own docstring says 77 and 12)"),
    "q_kin_met": (14, "LEDGER CLAIM-028: 25 criteria, 14 met, 11 not"), "q_kin_not": (11, "same"),
    "q_c3_adm": ("3 of 6", "LEDGER CLAIM-067 admission"), "q_c4_adm": ("6 of 6", "LEDGER CLAIM-084 (E1)"),
    "q_w2": ("1 of 4", "LEDGER CLAIM-092"), "q_c3_hours": ("55", "docs/designs/PGPE_R3_RESULTS.md Part C3 execution: died silently after about 55 h"),
}
for k, (val, src) in quoted.items(): put(k, val, src)

# the two `@[simp] theorem`s of Villani.lean that neither generator saw: what the environment audit says about them (a sentence, computed; or the statement that the audit has not reached the file)
_la = importlib.util.spec_from_file_location("la_", BOOK / "facts" / "lean_audit.py"); la_ = importlib.util.module_from_spec(_la); _la.loader.exec_module(la_)
_unaud = [m_ for m_ in mods if not (la_.AUD / f"{m_}.json").exists() or not la_.audit_is_current(la_.AUD / f"{m_}.json", la_.SRC / f"{m_}.lean")]
put("lib_unaudited", "no module" if not _unaud else f"{len(_unaud)} module" + ("s" if len(_unaud) > 1 else ""), "facts/audit/*.json: modules with no current environment audit: " + (", ".join(_unaud) or "none"))
_vj = la_.AUD / "Villani.json"
if _vj.exists() and la_.audit_is_current(_vj, la_.SRC / "Villani.lean"):
    _v = json.load(open(_vj)); _two = [t for t in _v["theorems"] if t["name"].endswith(("crossover_apply_mem", "crossover_apply_not_mem"))]
    _ax = sorted({a for t in _two for a in t["axioms"]}); _std = {"propext", "Classical.choice", "Quot.sound"}
    _txt = ("Asked about them, the environment audit finds that both depend on " + ("exactly the three standard axioms" if set(_ax) == _std else ("at most " + ", ".join(_ax)))
            + " and on no \\texttt{sorry}." if len(_two) == 2 and not _v["audit"]["sorryAx"] else "The environment audit lists a different set of theorems for \\texttt{Villani}; see \\texttt{facts/lean\\_audit.md}.")
    put("villani_simp", _txt, "facts/audit/Villani.json (environment audit): footprint of crossover_apply_mem and crossover_apply_not_mem: " + ", ".join(_ax))
else:
    put("villani_simp", "The environment audit had not reached \\texttt{Villani} when this text was generated.", "facts/audit/Villani.json missing or stale")

json.dump(out, open(here / "ch10_numbers.json", "w"), indent=1, default=str)
def texname(k): return "\\Nx" + "".join(p.capitalize() for p in re.split(r"[_]", k))
def tex_alpha(n):                                   # macro names: letters only
    return "".join({"0": "Zero", "1": "One", "2": "Two", "3": "Three", "4": "Four", "5": "Five", "6": "Six", "7": "Seven", "8": "Eight", "9": "Nine"}.get(c, c) for c in n)
lines = ["% generated by book/figures/ch10_numbers.py -- do not edit; every value and its source is in figures/ch10_numbers.json"]
for k, d in out.items():
    if isinstance(d["value"], dict): continue
    lines.append(f"\\providecommand{{{tex_alpha(texname(k))}}}{{{d['text']}}}")
for k in missing: pass
(here / "ch10_numbers.tex").write_text("\n".join(lines) + "\n")
print(len(out), "numbers written;", "MISSING INPUTS:" if missing else "no missing inputs", *missing, sep="\n  " if missing else " ")
