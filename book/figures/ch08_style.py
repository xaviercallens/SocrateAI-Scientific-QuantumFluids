"""Chapter-8 figure helper: a thin shim over book/figstyle.py.
Since the editor's fix of figstyle.py (2026-10-10: per-glyph font fallback for the minus sign, OpenType lining figures on every
Text) nothing local is needed; the shim only keeps the name `save8` used by the chapter-8 scripts.
Remaining rule for this chapter: mathtext strings are laid out by matplotlib's own engine and ignore the 'lnum' request, so
digits that sit inside a string containing '$...$' are written inside the math."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figstyle import *

save8 = save
