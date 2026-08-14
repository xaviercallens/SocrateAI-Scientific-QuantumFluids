"""Tests for adapters.godfrin_ancillary — happy path + negative controls (LL-2)."""

import pytest

from quantumfluids.adapters.godfrin_ancillary import (
    GodfrinAncillaryFormatError,
    load_godfrin_p0_dispersion,
)


def write_iso(tmp_path, name, content):
    p = tmp_path / name
    p.write_bytes(content.encode("iso-8859-1"))
    return str(p)


VALID = "k\te\terr(e)\r\nÅ-1\tmeV\tmeV\r\n0.000\t0.0000\t--\r\n0.100\t0.1150\t0.0020\r\n0.200\t0.2300\t--\r\n"


# --- Happy path ---------------------------------------------------------

def test_load_valid_file(tmp_path):
    path = write_iso(tmp_path, "valid.txt", VALID)
    data = load_godfrin_p0_dispersion(path)
    assert list(data.Q) == [0.0, 0.1, 0.2]
    assert list(data.omega) == [0.0, 0.115, 0.23]
    assert data.dS[1] == pytest.approx(0.002)
    import numpy as np
    assert np.isnan(data.dS[0])
    assert np.isnan(data.dS[2])
    assert data.tier == "B"


def test_load_skips_all_missing_gap_separator_row(tmp_path):
    """A row where Q, E, AND err are all '--' is a documented gap-separator
    (observed once in the real file, near Q=3.44-3.45) and should be
    silently skipped -- distinct from a partial-missing row (tested below),
    which must still raise."""
    content = (
        "k\te\terr(e)\r\nÅ-1\tmeV\tmeV\r\n"
        "0.000\t0.0000\t--\r\n"
        "--\t--\t--\r\n"
        "0.100\t0.1150\t--\r\n"
    )
    path = write_iso(tmp_path, "gap.txt", content)
    data = load_godfrin_p0_dispersion(path)
    assert list(data.Q) == [0.0, 0.1]


def test_load_all_missing_errors(tmp_path):
    content = "k\te\terr(e)\r\nÅ-1\tmeV\tmeV\r\n0.000\t0.0000\t--\r\n0.100\t0.1150\t--\r\n"
    path = write_iso(tmp_path, "no_err.txt", content)
    data = load_godfrin_p0_dispersion(path)
    import numpy as np
    assert np.all(np.isnan(data.dS))


# --- Negative controls (LL-2) --------------------------------------------

def test_rejects_wrong_header(tmp_path):
    content = "Q\tE\terr\r\nÅ-1\tmeV\tmeV\r\n0.000\t0.0000\t--\r\n"
    path = write_iso(tmp_path, "badheader.txt", content)
    with pytest.raises(GodfrinAncillaryFormatError, match="does not match expected"):
        load_godfrin_p0_dispersion(path)


def test_rejects_missing_value_in_q_column(tmp_path):
    content = "k\te\terr(e)\r\nÅ-1\tmeV\tmeV\r\n--\t0.0000\t--\r\n0.100\t0.1150\t--\r\n"
    path = write_iso(tmp_path, "badq.txt", content)
    with pytest.raises(GodfrinAncillaryFormatError, match="corruption signal"):
        load_godfrin_p0_dispersion(path)


def test_rejects_missing_value_in_e_column(tmp_path):
    content = "k\te\terr(e)\r\nÅ-1\tmeV\tmeV\r\n0.000\t--\t--\r\n0.100\t0.1150\t--\r\n"
    path = write_iso(tmp_path, "bade.txt", content)
    with pytest.raises(GodfrinAncillaryFormatError, match="corruption signal"):
        load_godfrin_p0_dispersion(path)


def test_rejects_wrong_column_count(tmp_path):
    content = "k\te\terr(e)\r\nÅ-1\tmeV\tmeV\r\n0.000\t0.0000\r\n"
    path = write_iso(tmp_path, "ragged.txt", content)
    with pytest.raises(GodfrinAncillaryFormatError, match="expected 3"):
        load_godfrin_p0_dispersion(path)


def test_rejects_non_numeric_q_or_e(tmp_path):
    content = "k\te\terr(e)\r\nÅ-1\tmeV\tmeV\r\nABC\t0.0000\t--\r\n"
    path = write_iso(tmp_path, "nonnum.txt", content)
    with pytest.raises(GodfrinAncillaryFormatError, match="non-numeric"):
        load_godfrin_p0_dispersion(path)


def test_rejects_non_monotonic_q(tmp_path):
    content = "k\te\terr(e)\r\nÅ-1\tmeV\tmeV\r\n0.200\t0.2300\t--\r\n0.100\t0.1150\t--\r\n"
    path = write_iso(tmp_path, "nonmono.txt", content)
    with pytest.raises(GodfrinAncillaryFormatError, match="strictly increasing"):
        load_godfrin_p0_dispersion(path)


def test_rejects_too_short_file(tmp_path):
    path = write_iso(tmp_path, "tooshort.txt", "k\te\terr(e)\r\n")
    with pytest.raises(GodfrinAncillaryFormatError, match="expected header"):
        load_godfrin_p0_dispersion(path)
