"""Loader for Godfrin et al. (2021) arXiv ancillary dispersion-curve files.

Source: arXiv:2012.09067 (the preprint of Godfrin et al., Phys. Rev. B
103:104516 (2021) -- LITERATURE_LEDGER.md [LIT-002]), ancillary files at
https://arxiv.org/src/2012.09067v1/anc/. This is the paper's own published,
citable numerical dispersion curve at P=0 bar -- author-processed data, not
raw ILL numor/instrument counts, but a legitimate Tier-B substitute for the
still-pending raw-data access (M1-DATA-001; see M1_DATA_ACCESS_STRATEGY.md).

Format specifics (all verified against the retrieved file, not assumed):
  - ISO-8859-1 encoded (contains the literal 'Å' character; UTF-8 decoding
    fails on this file)
  - CRLF line endings
  - Tab-separated
  - Two header rows: column names ("k", "e", "err(e)"), then units
    ("Å-1", "meV", "meV")
  - Columns are (Q, E, dE) -- i.e. the dispersion curve omega(Q) directly,
    NOT an S(Q,omega) intensity map. This is denser and more directly
    usable for landau_model fitting than a raw intensity map would be.
  - "--" is a documented missing-value sentinel in the err(e) column
    (most rows have no individual error estimate; a sparse subset do).
    This is treated as NaN, not rejected -- unlike a NaN/non-numeric value
    in the Q or E columns, which IS still rejected (LL-2: an axis value
    being unreadable is a corruption signal; an uncertainty being absent
    is not).
"""

from dataclasses import dataclass, field

import numpy as np

from quantumfluids.adapters.ascii_sqw import SQwData


class GodfrinAncillaryFormatError(ValueError):
    """Raised when the ancillary file's structure doesn't match what was
    verified against the retrieved DispersionP0allRange.txt (see module
    docstring). A layout change upstream should fail loudly, not be
    silently reinterpreted."""


_EXPECTED_HEADER = ["k", "e", "err(e)"]
_MISSING_TOKENS = {"--"}


def load_godfrin_p0_dispersion(path: str, tier: str = "B") -> SQwData:
    with open(path, "r", encoding="iso-8859-1", newline="") as f:
        raw = f.read()

    lines = raw.splitlines()
    if len(lines) < 3:
        raise GodfrinAncillaryFormatError(
            f"{path}: expected header + units + >=1 data row, got {len(lines)} lines"
        )

    header = [c.strip() for c in lines[0].split("\t")]
    if header != _EXPECTED_HEADER:
        raise GodfrinAncillaryFormatError(
            f"{path}: header {header!r} does not match expected {_EXPECTED_HEADER!r} "
            f"-- file layout may have changed upstream"
        )

    Q_vals, E_vals, dE_vals = [], [], []
    for i, ln in enumerate(lines[2:], start=3):
        if not ln.strip():
            continue
        parts = [p.strip() for p in ln.split("\t")]
        if len(parts) != 3:
            raise GodfrinAncillaryFormatError(
                f"{path}: line {i} has {len(parts)} columns, expected 3: {ln!r}"
            )
        q_str, e_str, err_str = parts

        if q_str in _MISSING_TOKENS and e_str in _MISSING_TOKENS and err_str in _MISSING_TOKENS:
            # Documented gap-separator row (all three columns "--"), marking
            # a break between densely- and sparsely-sampled Q ranges in the
            # source file (observed once, near Q=3.44-3.45, in the retrieved
            # DispersionP0allRange.txt). Skipped, not an error.
            continue

        if q_str in _MISSING_TOKENS or e_str in _MISSING_TOKENS:
            raise GodfrinAncillaryFormatError(
                f"{path}: line {i} has a missing-value sentinel in Q or E "
                f"(the axis columns) alone -- this is a corruption signal, "
                f"distinct from the documented all-columns gap-separator row "
                f"or the err(e)-only sparsity: {ln!r}"
            )
        try:
            q = float(q_str)
            e = float(e_str)
        except ValueError as exc:
            raise GodfrinAncillaryFormatError(
                f"{path}: line {i} has non-numeric Q or E: {ln!r}"
            ) from exc

        err = np.nan if err_str in _MISSING_TOKENS else float(err_str)

        Q_vals.append(q)
        E_vals.append(e)
        dE_vals.append(err)

    Q = np.array(Q_vals, dtype=float)
    E = np.array(E_vals, dtype=float)
    dE = np.array(dE_vals, dtype=float)

    if np.any(~np.isfinite(Q)) or np.any(~np.isfinite(E)):
        raise GodfrinAncillaryFormatError(f"{path}: non-finite value survived parsing in Q or E")

    if not np.all(np.diff(Q) > 0):
        raise GodfrinAncillaryFormatError(
            f"{path}: Q column is not strictly increasing -- possible row corruption "
            f"or duplicate/out-of-order entries"
        )

    return SQwData(
        Q=Q,
        omega=E,
        S=np.full(len(Q), np.nan),
        dS=dE,
        source=path,
        tier=tier,
        meta={
            "n_rows": len(Q),
            "format": "Godfrin et al. 2021 arXiv:2012.09067 ancillary DispersionP0allRange.txt",
            "note": "omega(Q) dispersion curve directly, not S(Q,omega) intensity map",
        },
    )
