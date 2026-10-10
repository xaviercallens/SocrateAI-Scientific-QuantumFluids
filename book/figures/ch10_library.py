"""Chapter 10, figure 'library': the QuantumFluids Lean library as audited for this book.
(a) a map of the modules: disc area = number of theorems (source keywords), arrows = imports between library modules, fill = axiom footprint from the
environment audit (facts/audit/<Module>.json, written by facts/lean_audit.py), gold ring = the module's source carries no `#print axioms` line of its own;
(b) every theorem constant of every audited module, by the set of axioms it depends on.
Run:  .venv/bin/python book/figures/ch10_library.py"""
import sys, json, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figstyle import *
plt.rcParams["axes.unicode_minus"] = False
from matplotlib.patches import Circle, FancyArrowPatch, Patch
import matplotlib.patheffects as pe
HALO = [pe.withStroke(linewidth=1.8, foreground="white")]       # keeps a label legible where an import arrow passes behind it
import importlib.util
here = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ma", ROOT / "book/facts/make_appA.py"); ma = importlib.util.module_from_spec(spec); spec.loader.exec_module(ma)
mods = sorted(f.stem for f in ma.SRC.glob("*.lean") if not f.name.startswith("_tmp") and f.name not in ("lakefile.lean", "QuantumFluids.lean"))
nthm = {m: sum(1 for d in ma.parse_decls(ma.SRC / f"{m}.lean") if d["kind"] in ("theorem", "lemma")) for m in mods}
own = {m: sum(1 for l in (ma.SRC / f"{m}.lean").read_text().split("\n") if l.startswith("#print axioms")) for m in mods}
imports = {m: [d for d in re.findall(r"^import\s+(\S+)", (ma.SRC / f"{m}.lean").read_text(), re.M) if d in mods] for m in mods}
audit = {m: json.load(open(ma.AUD / f"{m}.json")) for m in mods if (ma.AUD / f"{m}.json").exists() and ma.audit_is_current(ma.AUD / f"{m}.json", ma.SRC / f"{m}.lean")}   # an audit of changed code does not count
STD = {"propext", "Classical.choice", "Quot.sound"}
def cls(axs):
    s = set(axs)
    if s - STD: return "other"
    return {frozenset(): "none", frozenset({"propext"}): "propext", frozenset({"propext", "Quot.sound"}): "propext, Quot.sound", frozenset(STD): "propext, Classical.choice, Quot.sound"}.get(frozenset(s), "a subset of the three")
COLOR = {"none": "#DCE9F2", "propext": "#9EC1DD", "propext, Quot.sound": TEAL, "a subset of the three": GOLD, "propext, Classical.choice, Quot.sound": BLUE, "other": RED}
def firstpass(m):
    lp = ma.AUD / f"{m}.log"
    if not lp.exists(): return None
    t = lp.read_text(); sets = re.findall(r"depends on axioms: \[([^\]]*)\]", t)
    if sets and not re.search(r":\d+:\d+: error", t) and "sorry" not in t:
        return sorted({x.strip() for y in sets for x in y.replace("\n", " ").split(",") if x.strip()})
    return None
def module_class(m):
    """(footprint class, level) with level 'env' (environment audit), 'first' (first-pass compile log only) or None."""
    a = audit.get(m)
    if a and a["exit"] == 0 and not a["errors"] and a.get("audit"): return cls(a["audit"]["union_axioms"]), "env"
    fp = firstpass(m)
    if fp is not None: return cls(fp), "first"
    return None, None

# ---- layout: components of the import graph on the left, isolated modules in a grid on the right ---------------------------------------
parent = {m: m for m in mods}
def find(x):
    while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
    return x
for m in mods:
    for d in imports[m]: parent[find(m)] = find(d)
comps = {}
for m in mods: comps.setdefault(find(m), []).append(m)
linked = sorted([c for c in comps.values() if len(c) > 1], key=lambda c: -len(c))
isolated = sorted([c[0] for c in comps.values() if len(c) == 1])
level = {}
def lev(m):
    if m not in level: level[m] = 0 if not imports[m] else 1 + max(lev(d) for d in imports[m])
    return level[m]
pos = {}
LS = 1.55; LX = 1.95                                                # centre-to-centre spacing of nodes inside an import component: vertical, horizontal (between levels)
def place(c, x0, y0):
    """Put the nodes of one import component on a level grid (level = depth in the import relation); returns (width, height) of the block."""
    L = {}
    for m in sorted(c, key=lambda m: (lev(m), m)): L.setdefault(lev(m), []).append(m)
    h = max(len(v) for v in L.values())
    for lv, ms in L.items():
        for i, m in enumerate(ms): pos[m] = (x0 + LX * lv, y0 + (h - len(ms)) / 2 * LS + i * LS)
    return max(L) * LX, (h - 1) * LS
y = 0.0
for c in linked[:2]:                                                # the two biggest components, stacked
    w, hh = place(c, 0.6, y); y += hh + LS * 0.95
x = 0.6
for c in linked[2:]:                                                # the small chains side by side in one row
    w, hh = place(c, x, y); x += w + 2.1
NCOL = 6; GX0 = 8.0; GDX = 1.72; GDY = 1.5
for i, m in enumerate(isolated): pos[m] = (GX0 + (i % NCOL) * GDX, (i // NCOL) * GDY)
H = max(max(p[1] for p in pos.values()) + 0.9, 4.6)
def wrap(m):
    parts = re.findall(r"[A-Z]+(?![a-z])|[A-Z][a-z0-9]*", m)
    lines, cur = [], ""
    for p_ in parts:
        if len(cur) + len(p_) > 9 and cur: lines.append(cur); cur = p_
        else: cur += p_
    lines.append(cur); return "\n".join(lines)
r = lambda m: 0.19 + 0.056 * np.sqrt(nthm[m])

fig = plt.figure(figsize=(TEXTW * 1.05, 4.75))
gs = fig.add_gridspec(3, 1, height_ratios=[3.3, 0.62, 0.5], hspace=0.05)
a = fig.add_subplot(gs[0]); a.set_aspect("equal"); a.axis("off")
for m in mods:
    for d in imports[m]:
        (x1, y1), (x2, y2) = pos[m], pos[d]
        a.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=7, color=GREY, lw=0.8, shrinkA=r(m) * 72 * 0.5, shrinkB=r(d) * 72 * 0.5, connectionstyle="arc3,rad=0.10", zorder=1))
for m in mods:
    x, y = pos[m]; c, lv = module_class(m)
    fc = (COLOR[c] if lv == "env" else "white") if c else "white"
    if lv == "first": fc = "white"
    a.add_patch(Circle((x, y), r(m), fc=fc, ec=(GOLD if own[m] == 0 else "#555555"), lw=(2.4 if own[m] == 0 else 0.7), ls=("-" if lv == "env" else "--"), zorder=3))
    if lv == "first":                                           # a small footprint-coloured dot inside the dashed disc: log of the author's own audit lines only
        a.add_patch(Circle((x, y), r(m) * 0.62, fc=COLOR[c], ec="none", alpha=0.55, zorder=3))
    a.text(x, y, str(nthm[m]), ha="center", va="center", fontsize=7.4, color=("white" if lv == "env" and c in ("propext, Classical.choice, Quot.sound", "propext, Quot.sound") else "#222222"), zorder=4, family="DejaVu Sans")
    a.text(x, y + r(m) + 0.07, wrap(m), ha="center", va="top", fontsize=5.2, color="#222222", linespacing=0.95, zorder=4, family="DejaVu Sans", path_effects=HALO)
a.set_xlim(-0.35, GX0 + NCOL * GDX - 0.5); a.set_ylim(H, -0.6)
leg = [Patch(fc=COLOR["propext, Classical.choice, Quot.sound"], ec="#555555", label="environment audit: the three standard axioms"),
       Patch(fc=COLOR["propext, Quot.sound"], ec="#555555", label="environment audit: propext, Quot.sound"),
       Patch(fc=COLOR["propext"], ec="#555555", label="environment audit: propext only"), Patch(fc=COLOR["none"], ec="#555555", label="environment audit: no axiom"),
       Patch(fc="white", ec="#555555", ls="--", label="dashed: no environment audit (tinted dot: author's own audit lines)"),
       Patch(fc="white", ec=GOLD, lw=2.2, label="gold ring: no #print axioms line in the source")]
lgax = fig.add_subplot(gs[1]); lgax.axis("off")
lgax.legend(handles=leg, loc="center", prop={"family": "DejaVu Sans", "size": 6.2}, frameon=False, ncol=2, handlelength=1.0, labelspacing=0.45, columnspacing=1.6)
panel(a, "a")

# (b) every theorem constant by footprint class ------------------------------------------------------------------------------------------
b = fig.add_subplot(gs[2])
counts = {}; n_env = 0
for m, au in audit.items():
    if not (au["exit"] == 0 and not au["errors"] and au.get("audit")): continue
    n_env += 1
    for t in au["theorems"]:
        if t["line"] < 0: continue                               # generated by Lean itself, no source position
        counts[cls(t["axioms"])] = counts.get(cls(t["axioms"]), 0) + 1
order = [k for k in ["none", "propext", "propext, Quot.sound", "propext, Classical.choice, Quot.sound", "a subset of the three", "other"] if counts.get(k)]
tot = sum(counts.values()); left = 0
for k in order:
    b.barh(0, counts[k], left=left, color=COLOR[k], ec="white", height=0.5)
    if counts[k] >= 0.04 * sum(counts.values()): b.text(left + counts[k] / 2, 0, str(counts[k]), ha="center", va="center", fontsize=7.4, color=("white" if k in ("propext, Classical.choice, Quot.sound", "propext, Quot.sound") else "#222222"), family="DejaVu Sans")
    ytxt = -0.36 - (0.42 if (counts[k] < 0.12 * sum(counts.values()) and order.index(k) % 2 == 1) else 0.0)        # a narrow segment: stagger its label so that neighbours do not overlap
    b.text(left + counts[k] / 2, ytxt, k.replace("propext, Classical.choice, Quot.sound", "the three standard axioms") + (f" ({counts[k]})" if counts[k] < 0.04 * sum(counts.values()) else ""), ha="center", va="top", fontsize=5.8, color="#333333", family="DejaVu Sans")
    left += counts[k]
b.set_xlim(0, max(tot, 1)); b.set_ylim(-1.3, 0.45); b.axis("off")
b.set_title(f"{tot} theorem constants of the {n_env} modules audited at environment level, by axioms used", fontsize=7.0, color=GREY, loc="left", pad=2, family="DejaVu Sans")
panel(b, "b")
save(fig, "ch10_library")
json.dump(dict(counts=counts, total=tot, audited_modules=sorted(audit)), open(here / "ch10_library_numbers.json", "w"), indent=1)
print(counts)
