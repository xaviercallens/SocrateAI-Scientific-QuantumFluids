"""ASCII S(Q,omega) reader.

Parses plain-text inelastic-scattering data: whitespace- or comma-delimited
columns of (Q, omega, S, dS), with optional '#'-prefixed comment/header lines.

This is the fallback adapter: it also loads WebPlotDigitizer-style CSV output
(Q, omega pairs digitized from a published figure) when only two columns are
present, for use as Tier-C steering data when raw instrument files are not
accessible (see M1_DATA_ACCESS_STRATEGY.md, Pathway 4).
"""

from dataclasses import dataclass, field
import csv
import io

import numpy as np


class AsciiFormatError(ValueError):
    """Raised when an ASCII S(Q,omega) file fails structural validation."""


@dataclass
class SQwData:
    """Loaded inelastic-scattering data.

    Q, omega, S are 1D arrays of equal length. dS is None if the source had
    no uncertainty column (e.g. digitized Tier-C data).
    """

    Q: np.ndarray
    omega: np.ndarray
    S: np.ndarray
    dS: np.ndarray | None
    source: str
    tier: str  # "B" (instrument data) or "C" (digitized/steering)
    meta: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        n = len(self.Q)
        if len(self.omega) != n or len(self.S) != n:
            raise AsciiFormatError(
                f"Column length mismatch: Q={len(self.Q)}, "
                f"omega={len(self.omega)}, S={len(self.S)}"
            )
        if self.dS is not None and len(self.dS) != n:
            raise AsciiFormatError(
                f"dS length {len(self.dS)} does not match Q length {n}"
            )


def _sniff_delimiter(sample: str) -> str:
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",\t ")
        return dialect.delimiter
    except csv.Error:
        return None  # fall back to whitespace splitting


def load_ascii_sqw(path: str, tier: str = "B") -> SQwData:
    """Load an ASCII S(Q,omega) file.

    Expected columns (order-sensitive, no header required): Q, omega, S[, dS].
    Lines starting with '#' are treated as comments and skipped, except a
    leading '# Q omega S dS' style header is ignored (not parsed for names).

    Negative controls enforced here (see LL-2):
      - fewer than 2 columns -> AsciiFormatError
      - ragged rows (inconsistent column count) -> AsciiFormatError
      - non-numeric data in Q/omega/S columns -> AsciiFormatError
      - NaN or inf anywhere in Q or omega -> AsciiFormatError (a NaN axis
        value is a corrupt-file symptom, not physically meaningful data)
      - S containing NaN is ALLOWED but flagged in meta['s_has_nan'], since
        detector dead-pixels legitimately produce missing intensity.
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()

    lines = [ln for ln in raw.splitlines() if ln.strip() and not ln.strip().startswith("#")]
    if not lines:
        raise AsciiFormatError(f"{path}: no data rows found (empty or all-comment file)")

    delim = _sniff_delimiter(lines[0])
    rows = []
    ncols = None
    for i, ln in enumerate(lines):
        parts = ln.split(delim) if delim else ln.split()
        parts = [p.strip() for p in parts if p.strip() != ""]
        if ncols is None:
            ncols = len(parts)
            if ncols < 2:
                raise AsciiFormatError(
                    f"{path}: line {i+1} has {ncols} column(s); need at least 2 (Q, omega)"
                )
        elif len(parts) != ncols:
            raise AsciiFormatError(
                f"{path}: line {i+1} has {len(parts)} columns, "
                f"expected {ncols} (ragged file)"
            )
        try:
            rows.append([float(p) for p in parts])
        except ValueError as e:
            raise AsciiFormatError(f"{path}: line {i+1} has non-numeric value: {e}") from e

    arr = np.array(rows, dtype=float)
    Q = arr[:, 0]
    omega = arr[:, 1]
    S = arr[:, 2] if ncols >= 3 else np.full(len(Q), np.nan)
    dS = arr[:, 3] if ncols >= 4 else None

    if np.any(~np.isfinite(Q)) or np.any(~np.isfinite(omega)):
        raise AsciiFormatError(
            f"{path}: non-finite value in Q or omega column (corrupt axis data)"
        )

    meta = {
        "n_columns": ncols,
        "n_rows": len(Q),
        "s_has_nan": bool(np.any(np.isnan(S))) if ncols >= 3 else None,
        "delimiter": repr(delim) if delim else "whitespace",
    }

    return SQwData(Q=Q, omega=omega, S=S, dS=dS, source=path, tier=tier, meta=meta)


def load_digitized_csv(path: str) -> SQwData:
    """Load a two-column (Q, omega) CSV as Tier-C digitized data.

    Thin wrapper around load_ascii_sqw with tier="C" and delimiter forced to
    comma (WebPlotDigitizer's default export format).
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    rows = []
    for i, ln in enumerate(raw.splitlines()):
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        parts = [p.strip() for p in ln.split(",") if p.strip() != ""]
        if len(parts) < 2:
            raise AsciiFormatError(
                f"{path}: line {i+1} has {len(parts)} column(s); need at least 2 (Q, omega)"
            )
        try:
            rows.append([float(parts[0]), float(parts[1])])
        except ValueError as e:
            raise AsciiFormatError(f"{path}: line {i+1} has non-numeric value: {e}") from e

    if not rows:
        raise AsciiFormatError(f"{path}: no data rows found")

    arr = np.array(rows, dtype=float)
    Q, omega = arr[:, 0], arr[:, 1]
    if np.any(~np.isfinite(Q)) or np.any(~np.isfinite(omega)):
        raise AsciiFormatError(f"{path}: non-finite value in digitized Q or omega")

    return SQwData(
        Q=Q,
        omega=omega,
        S=np.full(len(Q), np.nan),
        dS=None,
        source=path,
        tier="C",
        meta={"n_rows": len(Q), "note": "digitized from published figure; not raw instrument data"},
    )
