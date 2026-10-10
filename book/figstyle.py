"""Shared matplotlib style of the book.  Every figure script does:
    import sys; sys.path.insert(0, str(Path(__file__).resolve().parents[1])); from figstyle import *
and ends with  save(fig, "ch03_name")   which writes book/figures/ch03_name.pdf (+ .png preview, 200 dpi)."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager as _fm

FIG = Path(__file__).resolve().parent / "figures"; FIG.mkdir(exist_ok=True)
ROOT = Path(__file__).resolve().parents[1]
# palette identical to qfbook.sty
BLUE, TEAL, ORANGE, RED, GREY, GOLD, PAPER = "#1F4E79", "#2A7F7F", "#C8731A", "#A23B2A", "#5A5A5A", "#B8902F", "#FAF7F0"
CYCLE = [BLUE, ORANGE, TEAL, RED, GOLD, GREY]
TEXTW = 5.6          # inches: width of the text block; use figsize=(TEXTW, h) or (TEXTW*0.48, h) for half width
_serif = [f.name for f in _fm.fontManager.ttflist if f.name in ("EB Garamond", "EB Garamond 12")]
plt.rcParams.update({
    "font.family": "serif", "font.serif": (_serif[:1] or []) + ["DejaVu Serif"], "mathtext.fontset": "dejavuserif",
    "font.size": 9.5, "axes.labelsize": 10, "axes.titlesize": 10, "legend.fontsize": 8.5, "xtick.labelsize": 8.5, "ytick.labelsize": 8.5,
    "axes.prop_cycle": plt.cycler(color=CYCLE), "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.7,
    "axes.edgecolor": GREY, "axes.labelcolor": "#222222", "xtick.color": GREY, "ytick.color": GREY, "grid.color": "#DDDDDD", "grid.linewidth": 0.5,
    "legend.frameon": False, "figure.dpi": 150, "savefig.bbox": "tight", "savefig.pad_inches": 0.04, "pdf.fonttype": 42, "lines.linewidth": 1.4,
})

# Editor's fix (2026-10-10).  EB Garamond has no U+2212 MINUS SIGN, so negative tick labels printed as an empty box, and
# its default digits are old-style (a zero looks like the letter o on an axis).  (1) List the families explicitly so that
# matplotlib falls back glyph by glyph to DejaVu Serif for the minus sign (and any other missing glyph); (2) ask every
# Text for OpenType lining figures ('lnum').  Checked: no "Glyph missing" warning, true minus signs, lining digits.
if _serif:
    plt.rcParams["font.family"] = [_serif[0], "DejaVu Serif"]
import matplotlib.text as _mtext
if not getattr(_mtext.Text, "_qf_lnum", False):
    _text_init = _mtext.Text.__init__
    def _text_init_lnum(self, *a, **k):
        _text_init(self, *a, **k)
        try:
            self.set_fontfeatures(["lnum"])
        except Exception:
            pass
    _mtext.Text.__init__ = _text_init_lnum
    _mtext.Text._qf_lnum = True

def save(fig, name):
    fig.savefig(FIG / f"{name}.pdf"); fig.savefig(FIG / f"{name}.png", dpi=200); plt.close(fig); print("wrote", FIG / f"{name}.pdf")

def panel(ax, letter):
    ax.text(-0.12, 1.04, letter, transform=ax.transAxes, fontsize=11, fontweight="bold", color=BLUE)

def vortex_cmap():
    from matplotlib.colors import LinearSegmentedColormap
    return LinearSegmentedColormap.from_list("qfphase", [BLUE, "#9EC1DD", PAPER, "#E8B07A", RED, BLUE], N=256)
