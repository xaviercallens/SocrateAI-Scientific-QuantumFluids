"""Plotting helpers for M1 dispersion-fit results.

Produces the figures required by M1_CHECKLIST.md Phase 3.3:
  - E(Q) data + fitted curve (phonon + roton branches)
  - Residuals (experiment - model)

No display side effects: every function takes an output path and saves
a PNG, so this is safe to call from a headless CI/test environment
(matplotlib Agg backend is forced at import time).
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from quantumfluids.adapters.ascii_sqw import SQwData
from quantumfluids.dispersion_fit.fit_dispersion import DispersionFitReport
from quantumfluids.dispersion_fit.landau_model import phonon_branch, roton_branch


def plot_dispersion_fit(
    data: SQwData,
    report: DispersionFitReport,
    out_path: str,
    phonon_q_max: float = 0.4,
    roton_q_center: float = 1.9,
    roton_half_width: float = 0.5,
) -> None:
    """Plot fit + residuals.

    phonon_q_max / roton_q_center / roton_half_width MUST match the values
    passed to run_dispersion_fit() for this report — the residual arrays
    inside `report` were computed against exactly those masks, and
    recomputing a different mask here would size-mismatch against them
    (this bit us once: see M1 commit history).
    """
    fig, (ax_fit, ax_res) = plt.subplots(2, 1, figsize=(7, 8), sharex=True,
                                          gridspec_kw={"height_ratios": [3, 1]})

    ax_fit.scatter(data.Q, data.omega, s=12, color="#4C72B0", alpha=0.6,
                    label=f"data ({data.source}, Tier {data.tier})")

    q_phonon = np.linspace(0, max(phonon_q_max, data.Q.min()), 100)
    ax_fit.plot(q_phonon, phonon_branch(q_phonon, report.phonon.c),
                color="#DD8452", lw=2, label=f"phonon fit: c={report.phonon.c:.3g}")

    q_roton = np.linspace(report.roton.q_m - roton_half_width, report.roton.q_m + roton_half_width, 100)
    ax_fit.plot(
        q_roton,
        roton_branch(q_roton, report.roton.delta, report.roton.q_m, report.roton.inv_two_mu),
        color="#55A868", lw=2,
        label=f"roton fit: Delta={report.roton.delta:.3g}, Q_m={report.roton.q_m:.3g}",
    )

    ax_fit.set_ylabel("E (meV)")
    ax_fit.legend(fontsize=8)
    ax_fit.set_title(f"Dispersion fit: {data.source}")

    # Must reselect using the same q_center used at fit time (select_roton_region),
    # NOT the fitted q_m — they can differ enough to flip a boundary point and
    # reproduce the exact size-mismatch this function was just fixed for.
    Qp = data.Q[data.Q < phonon_q_max]
    Qr = data.Q[np.abs(data.Q - roton_q_center) < roton_half_width]
    ax_res.scatter(Qp, report.phonon.residuals, s=10, color="#DD8452", label="phonon residual")
    ax_res.scatter(Qr, report.roton.residuals, s=10, color="#55A868", label="roton residual")
    ax_res.axhline(0, color="black", lw=0.8)
    ax_res.set_xlabel("Q (Angstrom^-1)")
    ax_res.set_ylabel("residual (meV)")
    ax_res.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
