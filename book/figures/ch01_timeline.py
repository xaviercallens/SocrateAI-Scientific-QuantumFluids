"""Chapter 1, timeline: the landmarks this book revisits.  Rows are in chronological order and equally spaced (the figure is NOT to scale
in time); the colour of the year says theory (blue), experiment (orange) or published data and code (teal); the two measurements of
Godfrin et al. that run through the book sit on a gold band.  Dates and attributions: book/facts/FACTS.md sections 2 and 3 and
book/refs.bib (the date of Landau's Fermi-liquid paper is that of the English translation cited there).  The grey tags are
COMPUTED (second edition): for each landmark, the printed numbers of the other chapters whose source cites one of its
bibliography keys, in the print order of quantum_fluids_book.tex.  A row whose keys no chapter cites is dropped.
Run:  .venv/bin/python book/figures/ch01_timeline.py   (after every chapter is final)"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figstyle import *
from matplotlib.patches import FancyBboxPatch

plt.rcParams["axes.unicode_minus"] = False
import re
BOOK = Path(__file__).resolve().parents[1]
# print order of the chapters, read from the master file (\IfCh{chNN}... lines in order)
ORDER = re.findall(r"\\IfCh\{(ch\d\d)\}", (BOOK / "quantum_fluids_book.tex").read_text())
PRINT = {c: i + 1 for i, c in enumerate(ORDER)}
CITES = {}
for c in ORDER:
    f = BOOK / "chapters" / f"{c}.tex"
    if f.exists():
        keys = set()
        for m in re.finditer(r"\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}", f.read_text()):
            keys.update(k.strip() for k in m.group(1).split(","))
        CITES[c] = keys

def cited_in(keys, here="ch01"):
    nums = sorted(PRINT[c] for c, ks in CITES.items() if c != here and ks & set(keys))
    return "ch. " + ", ".join(map(str, nums)) if nums else None

# (year, who, what, kind, bib keys, godfrin)    kind: T theory, E experiment, D published data and code
rows = [
    (1941, "Landau", "phonon–roton spectrum and the two-fluid picture", "T", ["Landau1941"], False),
    (1947, "Bogoliubov", "the weakly interacting Bose gas", "T", ["Bogoliubov1947"], False),
    (1949, "Onsager", "statistical hydrodynamics; quantized circulation", "T", ["Onsager1949"], False),
    (1955, "Feynman", "quantized vortex lines in helium II", "T", ["Feynman1955"], False),
    (1957, "Landau", "theory of the Fermi liquid", "T", ["Landau1957"], False),
    (1961, "Gross, Pitaevskii", "the condensate wave equation and its vortex", "T", ["Gross1961", "Pitaevskii1961"], False),
    (1966, "Abel, Anderson, Wheatley", "zero sound in liquid $^3$He", "E", ["AbelAndersonWheatley1966"], False),
    (1973, "Kosterlitz, Thouless", "vortex unbinding in two dimensions", "T", ["KosterlitzThouless1973"], False),
    (1978, "Bishop, Reppy", "superfluid transition of two-dimensional $^4$He films", "E", ["BishopReppy1978"], False),
    (2012, "Godfrin et al.", "roton-like mode of two-dimensional liquid $^3$He (ILL)", "E", ["Godfrin2012"], True),
    (2021, "Godfrin et al.", "$^4$He dispersion (ILL, IN5) and thermodynamics", "E", ["Godfrin2021"], True),
    (2026, "Kwon, Shin", "vortex shedding past an obstacle: data and code", "D", ["KwonShin2026prr", "KwonShin2026data", "KwonShin2026"], False),
]
ev = []
for yr, who, what, kind, keys, god in rows:
    tag = cited_in(keys)
    if tag:
        ev.append((yr, who, what, kind, tag, god))
n = len(ev)
fig, ax = plt.subplots(figsize=(TEXTW, 0.31 * len(ev) + 0.03))
col = {"T": BLUE, "E": ORANGE, "D": TEAL}
ax.set_xlim(-0.2, 5.8); ax.set_ylim(-(n - 0.45), 1.0); ax.axis("off")
ax.plot([0.35, 0.35], [0.45, -(n - 0.6)], color="#BBBBBB", lw=1.2, zorder=1)
for i, (yr, who, what, kind, ch, god) in enumerate(ev):
    y = -i
    c = col[kind]
    if god:
        ax.add_patch(FancyBboxPatch((-0.2, y - 0.43), 6.0, 0.86, boxstyle="round,pad=0,rounding_size=0.14", fc=GOLD, ec="none", alpha=0.17, zorder=0))
    ax.text(0.35, y, str(yr), ha="center", va="center", fontsize=8.6, fontweight="bold", color=c,
            bbox=dict(boxstyle="round,pad=0.22", fc="white", ec=c, lw=0.9), zorder=3)
    t = ax.text(0.78, y, who, ha="left", va="center", fontsize=8.5, fontweight="bold", color="#222222", zorder=2)
    fig.canvas.draw()
    bb = t.get_window_extent(fig.canvas.get_renderer()); x1 = ax.transData.inverted().transform((bb.x1, bb.y1))[0]
    ax.text(x1 + 0.09, y, "—  " + what, ha="left", va="center", fontsize=8.1, color="#333333", zorder=2)
    ax.text(5.76, y, ch, ha="right", va="center", fontsize=7.3, color=GREY, style="italic")
ax.text(0.78, 0.68, "theory", ha="left", va="center", fontsize=8.6, color=BLUE, style="italic")
ax.text(1.42, 0.68, "experiment", ha="left", va="center", fontsize=8.6, color=ORANGE, style="italic")
ax.text(2.35, 0.68, "published data and code", ha="left", va="center", fontsize=8.6, color=TEAL, style="italic")
ax.text(5.76, 0.68, "cited in", ha="right", va="center", fontsize=7.3, color=GREY, style="italic")
save(fig, "ch01_timeline")
