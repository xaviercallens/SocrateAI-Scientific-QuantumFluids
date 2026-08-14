"""NeXus (.nxs) reader for inelastic neutron-scattering data.

NeXus files are HDF5 with a semi-standardized entry layout. ILL's IN5
reduction pipeline (LAMP/Mantid) typically writes reduced S(Q,omega) under
one of a small number of conventional paths. This adapter tries a list of
known path templates and fails loudly (rather than guessing) if none match,
per LL-2: an adapter that silently reinterprets an unfamiliar layout is worse
than one that refuses to load.

Requires h5py (not in the base numpy/scipy/matplotlib stack). See
requirements.txt / M1_CHECKLIST.md for install notes.
"""

from dataclasses import dataclass, field

import numpy as np

try:
    import h5py
except ImportError as _e:  # pragma: no cover - exercised only when h5py absent
    h5py = None
    _H5PY_IMPORT_ERROR = _e


class NexusFormatError(ValueError):
    """Raised when a .nxs file's structure doesn't match a known layout."""


# Candidate (Q, omega, S, error) dataset path templates, checked in order.
# Populated from Mantid/LAMP conventions; NOT yet validated against a real
# Godfrin et al. 2021 file (see M1_DATA_ACCESS_STRATEGY.md). Extend this list
# once a real sample is in hand, and add a regression test that pins the
# exact layout observed.
_KNOWN_LAYOUTS = [
    {
        "name": "mantid_generic_2d",
        "Q": "mantid_workspace_1/workspace/axis2",
        "omega": "mantid_workspace_1/workspace/axis1",
        "S": "mantid_workspace_1/workspace/values",
        "dS": "mantid_workspace_1/workspace/errors",
    },
    {
        "name": "nxdata_generic",
        "Q": "entry0/data/Q",
        "omega": "entry0/data/omega",
        "S": "entry0/data/S",
        "dS": "entry0/data/S_error",
    },
]


@dataclass
class SQwData2D:
    """2D S(Q,omega) map: S has shape (len(Q), len(omega))."""

    Q: np.ndarray
    omega: np.ndarray
    S: np.ndarray
    dS: np.ndarray | None
    source: str
    tier: str
    meta: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.S.shape != (len(self.Q), len(self.omega)):
            raise NexusFormatError(
                f"S shape {self.S.shape} does not match "
                f"(len(Q), len(omega)) = ({len(self.Q)}, {len(self.omega)}). "
                f"This is the axis-swap failure mode flagged in LL-2 — "
                f"check whether Q and omega were read from swapped datasets."
            )


def _require_h5py() -> None:
    if h5py is None:
        raise ImportError(
            "h5py is required for nexus_reader but is not installed. "
            "Install with: pip install h5py (see M1_CHECKLIST.md)."
        ) from _H5PY_IMPORT_ERROR


def load_nexus_sqw(path: str, tier: str = "B") -> SQwData2D:
    """Load a NeXus file, trying each known layout until one matches.

    Raises NexusFormatError if no known layout's datasets are all present,
    or if any axis dataset contains non-finite values.
    """
    _require_h5py()

    with h5py.File(path, "r") as f:
        matched = None
        for layout in _KNOWN_LAYOUTS:
            if all(key in f for key in (layout["Q"], layout["omega"], layout["S"])):
                matched = layout
                break

        if matched is None:
            tried = ", ".join(layout["name"] for layout in _KNOWN_LAYOUTS)
            raise NexusFormatError(
                f"{path}: no known NeXus layout matched (tried: {tried}). "
                f"File structure: {list(f.keys())}. "
                f"This adapter refuses to guess at an unfamiliar layout — "
                f"add a new entry to _KNOWN_LAYOUTS after inspecting the file."
            )

        Q = np.asarray(f[matched["Q"]][()], dtype=float)
        omega = np.asarray(f[matched["omega"]][()], dtype=float)
        S = np.asarray(f[matched["S"]][()], dtype=float)
        dS = np.asarray(f[matched["dS"]][()], dtype=float) if matched["dS"] in f else None

    if np.any(~np.isfinite(Q)) or np.any(~np.isfinite(omega)):
        raise NexusFormatError(f"{path}: non-finite value in Q or omega axis")

    if not np.all(np.diff(Q) > 0) and not np.all(np.diff(Q) < 0):
        raise NexusFormatError(
            f"{path}: Q axis is not monotonic — likely axis-swap corruption "
            f"(Q and omega datasets read from wrong paths)"
        )

    meta = {
        "layout": matched["name"],
        "n_Q": len(Q),
        "n_omega": len(omega),
        "s_has_nan": bool(np.any(np.isnan(S))),
    }

    return SQwData2D(Q=Q, omega=omega, S=S, dS=dS, source=path, tier=tier, meta=meta)
