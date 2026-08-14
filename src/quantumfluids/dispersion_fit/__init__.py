"""Dispersion-relation fitting tools for quantum fluids.

Implements the M1 workflow (PLAN.md, M1_CHECKLIST.md):
  landau_model   - phonon (linear) and roton (parabolic) dispersion forms,
                   fit via scipy.optimize.curve_fit
  fit_dispersion - end-to-end: load SQwData -> select regions -> fit both
                   branches -> compare to literature (c within +/-5%,
                   Delta within +/-10%)
  plotting       - E(Q) + fit + residuals figure, matches M1 Phase 3.3
"""

from .fit_dispersion import (
    DispersionFitReport,
    compare_to_literature,
    run_dispersion_fit,
    select_phonon_region,
    select_roton_region,
)
from .landau_model import (
    PhononFitResult,
    RotonFitResult,
    fit_phonon_branch,
    fit_roton_branch,
    phonon_branch,
    roton_branch,
)

__all__ = [
    "DispersionFitReport",
    "compare_to_literature",
    "run_dispersion_fit",
    "select_phonon_region",
    "select_roton_region",
    "PhononFitResult",
    "RotonFitResult",
    "fit_phonon_branch",
    "fit_roton_branch",
    "phonon_branch",
    "roton_branch",
]
