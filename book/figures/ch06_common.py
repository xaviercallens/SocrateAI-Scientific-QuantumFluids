"""Chapter-6 figure helpers (imported after figstyle).  Two fixes local to this chapter's scripts, the shared figstyle.py is left untouched:
  * EB Garamond has no U+2212 minus sign -> use the hyphen-minus in tick labels (axes.unicode_minus = False);
  * EB Garamond's default digits are old-style, which makes tick labels hard to read -> every Text created in these scripts asks for lining figures (OpenType 'lnum')."""
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.text as mtext

plt.rcParams["axes.unicode_minus"] = False
_orig_init = mtext.Text.__init__


def _init(self, *a, **k):
    _orig_init(self, *a, **k)
    try:
        self.set_fontfeatures(["lnum"])
    except Exception:
        pass


mtext.Text.__init__ = _init


def log_ticks_plain(ax, axis="x", ticks=None):
    """Plain decimal tick labels on a log axis, no minor labels."""
    from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter
    a = ax.xaxis if axis == "x" else ax.yaxis
    if ticks is not None:
        a.set_major_locator(FixedLocator(ticks))
    a.set_major_formatter(FuncFormatter(lambda v, p: ("%g" % v)))
    a.set_minor_formatter(NullFormatter())
