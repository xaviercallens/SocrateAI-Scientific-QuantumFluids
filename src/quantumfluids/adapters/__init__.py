"""Data adapters for ILL instrument formats and published ancillary data.

Status (2026-08-14):
  ascii_sqw          - IMPLEMENTED (plain-text and digitized-CSV readers)
  nexus_reader       - IMPLEMENTED (requires h5py; layout list not yet
                       validated against a real Godfrin et al. 2021 file)
  godfrin_ancillary  - IMPLEMENTED (Tier B: Godfrin et al. 2021's own
                       published dispersion-curve tables from arXiv
                       ancillary files, see M1_DATA_ACCESS_STRATEGY.md)
  ill_numor          - PLACEHOLDER (raises NumorNotImplementedError; see
                       module docstring)

All adapters raise a module-specific *FormatError (or NotImplementedError
for ill_numor) rather than silently reinterpreting malformed input, per
LL-2 (negative controls are mandatory, not optional).
"""

from .ascii_sqw import (
    AsciiFormatError,
    SQwData,
    load_ascii_sqw,
    load_digitized_csv,
)
from .godfrin_ancillary import GodfrinAncillaryFormatError, load_godfrin_p0_dispersion
from .ill_numor import NumorNotImplementedError, load_numor
from .nexus_reader import NexusFormatError, SQwData2D, load_nexus_sqw

__all__ = [
    "AsciiFormatError",
    "SQwData",
    "load_ascii_sqw",
    "load_digitized_csv",
    "GodfrinAncillaryFormatError",
    "load_godfrin_p0_dispersion",
    "NumorNotImplementedError",
    "load_numor",
    "NexusFormatError",
    "SQwData2D",
    "load_nexus_sqw",
]
