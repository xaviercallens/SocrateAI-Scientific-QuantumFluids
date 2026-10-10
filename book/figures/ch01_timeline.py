"""Chapter 1, timeline: the landmarks this book revisits.  Rows are in chronological order and equally spaced (the figure is NOT to scale
in time); the colour of the year says theory (blue), experiment (orange) or published data and code (teal); the two measurements of
Godfrin et al. that run through the book sit on a gold band.  Dates and attributions: book/facts/FACTS.md sections 2 and 3 and
book/refs.bib (the date of Landau's Fermi-liquid paper is that of the English translation cited there).  The grey tags say which
chapter of this book, by its title, takes the landmark up.
Run:  .venv/bin/python book/figures/ch01_timeline.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figstyle import *
from matplotlib.patches import FancyBboxPatch

plt.rcParams["axes.unicode_minus"] = False
# (year, who, what, kind, chapters, godfrin)    kind: T theory, E experiment, D published data and code
ev = [
    (1941, "Landau", "phonon–roton spectrum and the two-fluid picture", "T", "ch. 4, 5", False),
    (1947, "Bogoliubov", "the weakly interacting Bose gas", "T", "ch. 5", False),
    (1949, "Onsager", "quantized circulation", "T", "ch. 3", False),
    (1955, "Feynman", "quantized vortex lines in helium II", "T", "ch. 3", False),
    (1957, "Landau", "theory of the Fermi liquid", "T", "ch. 8", False),
    (1961, "Gross, Pitaevskii", "the condensate wave equation and its vortex", "T", "ch. 3, 9", False),
    (1966, "Abel, Anderson, Wheatley", "zero sound in liquid $^3$He", "E", "ch. 8", False),
    (1973, "Kosterlitz, Thouless", "vortex unbinding in two dimensions", "T", "ch. 6", False),
    (1978, "Bishop, Reppy", "superfluid transition of two-dimensional $^4$He films", "E", "ch. 6", False),
    (2012, "Godfrin et al.", "roton-like mode of two-dimensional liquid $^3$He (ILL)", "E", "ch. 8", True),
    (2021, "Godfrin et al.", "$^4$He dispersion (ILL, IN5) and thermodynamics", "E", "ch. 4, 5", True),
    (2026, "Kwon, Shin", "vortex shedding past an obstacle: data and code", "D", "ch. 9", False),
]
n = len(ev)
fig, ax = plt.subplots(figsize=(TEXTW, 3.75))
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
ax.text(5.76, 0.68, "taken up in", ha="right", va="center", fontsize=7.3, color=GREY, style="italic")
save(fig, "ch01_timeline")
