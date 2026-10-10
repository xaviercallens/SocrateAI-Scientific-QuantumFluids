"""Rendering helpers of the chapter-9 figures (matplotlib; the numerical helpers are in ch09_common.py)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import *
import numpy as np
import ch09_common as C

plt.rcParams["axes.unicode_minus"] = False        # EB Garamond has no U+2212: use the hyphen-minus in tick labels

# EB Garamond's default digits are old-style (hard to read on tick labels): every Text of this chapter's scripts asks for lining figures (OpenType 'lnum'),
# as in the chapter-6 scripts; the shared figstyle.py is left untouched.
import matplotlib.text as _mtext
_orig_text_init = _mtext.Text.__init__
def _text_init(self, *a, **k):
    _orig_text_init(self, *a, **k)
    try:
        self.set_fontfeatures(["lnum"])
    except Exception:
        pass
_mtext.Text.__init__ = _text_init

def logticks(ax, axis="y", ticks=None):
    """tick labels 10^k in mathtext (the default LogFormatter writes the exponent's minus sign with a glyph that EB Garamond lacks)"""
    from matplotlib.ticker import FuncFormatter, FixedLocator, NullFormatter
    a = ax.yaxis if axis == "y" else ax.xaxis
    if ticks is not None: a.set_major_locator(FixedLocator(ticks))
    a.set_major_formatter(FuncFormatter(lambda v, p: (r"$10^{%d}$" % int(round(np.log10(v)))) if v > 0 else ""))
    a.set_minor_formatter(NullFormatter())

POS_COL, NEG_COL = "#FFD36B", "#7FD6FF"            # vortex markers on the dark phase-density rendering: counter-clockwise (+) and clockwise (-)

def hue_density(z, gamma=0.5):
    """phase -> hue (the book's cyclic map), brightness = density^gamma (a hole in the fluid is black); z is a complex field"""
    n = np.clip(np.abs(z) ** 2, 0, 1.0)
    th = np.angle(z)
    col = vortex_cmap()((th + np.pi) / (2 * np.pi))[..., :3]
    return col * (n ** gamma)[..., None]

def obstacle_outline(ax, color="white", lw=0.8, ls=(0, (3, 2))):
    """the 1/e^2 circle of the Gaussian obstacle (radius sigma = 20 around x = 100)"""
    a = np.linspace(0, 2 * np.pi, 400)
    ax.plot(C.XOBS + C.SIGMA * np.cos(a), C.SIGMA * np.sin(a), color=color, lw=lw, ls=ls)

def charge_markers(ax, census, filled=True, size=26, lw=0.7, edge="black", zorder=5):
    """census = [(x, y, q), ...] (plaquette centres, counter-clockwise charge)"""
    for q, col in ((+1, POS_COL), (-1, NEG_COL)):
        pts = [(a, b) for a, b, c in census if c == q]
        if pts:
            ax.scatter(*zip(*pts), s=size, marker="o", facecolor=col if filled else "none", edgecolor=edge if filled else col, linewidths=lw, zorder=zorder)

def style_map(ax, xlim, ylim, xticks=None, yticks=None, xlabel=True, ylabel=True):
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect("equal")
    if xticks is not None: ax.set_xticks(xticks)
    if yticks is not None: ax.set_yticks(yticks)
    if xlabel: ax.set_xlabel(r"$x/\xi$")
    if ylabel: ax.set_ylabel(r"$y/\xi$")
    for s in ax.spines.values(): s.set_visible(True); s.set_linewidth(0.6)


def density_cmap():
    """dark navy (a hole in the fluid) -> the book's blue -> pale blue -> paper (bulk density)"""
    from matplotlib.colors import LinearSegmentedColormap
    return LinearSegmentedColormap.from_list("qfdens", ["#07172B", BLUE, "#9EC1DD", PAPER], N=256)
