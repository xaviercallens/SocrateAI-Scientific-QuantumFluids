"""Data adapters for ILL instrument formats.

Status (2026-08-14):
  ascii_sqw    - IMPLEMENTED (plain-text and digitized-CSV readers)
  nexus_reader - IMPLEMENTED (requires h5py; layout list not yet validated
                 against a real Godfrin et al. 2021 file)
  ill_numor    - PLACEHOLDER (raises NumorNotImplementedError; see module
                 docstring and M1_DATA_ACCESS_STRATEGY.md)

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
from .ill_numor import NumorNotImplementedError, load_numor
from .nexus_reader import NexusFormatError, SQwData2D, load_nexus_sqw

__all__ = [
    "AsciiFormatError",
    "SQwData",
    "load_ascii_sqw",
    "load_digitized_csv",
    "NumorNotImplementedError",
    "load_numor",
    "NexusFormatError",
    "SQwData2D",
    "load_nexus_sqw",
]
