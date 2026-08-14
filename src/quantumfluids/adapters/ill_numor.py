"""ILL numor reader — STATUS: PLACEHOLDER, NOT YET IMPLEMENTED.

The ILL numor format (raw TOF/spectrometer output) has instrument- and
cycle-dependent binary/text layout variants (see ILL Neutron Data Booklet).
Implementing a parser without a real sample file to validate against would
mean shipping untested format-guessing logic — exactly the failure mode
LL-2 warns against (an adapter that "passes on the happy path" but silently
corrupts data on a real file with a layout we didn't anticipate).

This module is intentionally a stub until M1-DATA-001 resolves (see
M1_DATA_ACCESS_STRATEGY.md) and a real numor file is available to write
against and regression-test.

If raw numor access is denied, M1 proceeds via:
  - ascii_sqw.load_digitized_csv() for Tier-C digitized Fig. 5 data, or
  - nexus_reader.load_nexus_sqw() if ILL provides pre-reduced .nxs output
    instead of raw numor (the more common path for shared/published data).
"""


class NumorNotImplementedError(NotImplementedError):
    """Raised by every entry point in this module until a real sample exists."""


def load_numor(path: str):  # noqa: ARG001 - signature kept stable for future impl
    raise NumorNotImplementedError(
        "ILL numor parsing is not implemented: no real sample file has been "
        "validated against (see M1_DATA_ACCESS_STRATEGY.md). Use "
        "nexus_reader.load_nexus_sqw() or ascii_sqw.load_digitized_csv() "
        "instead, or implement this once M1-DATA-001 provides a sample."
    )
