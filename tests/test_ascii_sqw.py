"""Tests for adapters.ascii_sqw — happy path + negative controls (LL-2)."""

import numpy as np
import pytest

from quantumfluids.adapters.ascii_sqw import (
    AsciiFormatError,
    load_ascii_sqw,
    load_digitized_csv,
)


def write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


# --- Happy path ---------------------------------------------------------

def test_load_valid_four_column(tmp_path):
    path = write(
        tmp_path, "valid.txt",
        "# Q omega S dS\n0.1 0.24 1.2 0.1\n0.2 0.48 1.1 0.1\n0.3 0.72 1.0 0.1\n",
    )
    data = load_ascii_sqw(path)
    assert np.allclose(data.Q, [0.1, 0.2, 0.3])
    assert np.allclose(data.omega, [0.24, 0.48, 0.72])
    assert np.allclose(data.S, [1.2, 1.1, 1.0])
    assert data.dS is not None
    assert np.allclose(data.dS, [0.1, 0.1, 0.1])
    assert data.tier == "B"
    assert data.meta["n_rows"] == 3


def test_load_valid_two_column_no_intensity(tmp_path):
    path = write(tmp_path, "twocol.txt", "0.1 0.24\n0.2 0.48\n")
    data = load_ascii_sqw(path)
    assert np.allclose(data.Q, [0.1, 0.2])
    assert np.all(np.isnan(data.S))
    assert data.dS is None


def test_load_comma_delimited(tmp_path):
    path = write(tmp_path, "csv.txt", "0.1,0.24,1.2\n0.2,0.48,1.1\n")
    data = load_ascii_sqw(path)
    assert np.allclose(data.Q, [0.1, 0.2])


def test_s_nan_allowed_and_flagged(tmp_path):
    path = write(tmp_path, "deadpixel.txt", "0.1 0.24 nan\n0.2 0.48 1.1\n")
    data = load_ascii_sqw(path)
    assert np.isnan(data.S[0])
    assert data.meta["s_has_nan"] is True


# --- Negative controls (LL-2: mandatory, not optional) ------------------

def test_rejects_single_column(tmp_path):
    path = write(tmp_path, "onecol.txt", "0.1\n0.2\n")
    with pytest.raises(AsciiFormatError, match="at least 2"):
        load_ascii_sqw(path)


def test_rejects_ragged_rows(tmp_path):
    path = write(tmp_path, "ragged.txt", "0.1 0.24 1.2\n0.2 0.48\n")
    with pytest.raises(AsciiFormatError, match="ragged"):
        load_ascii_sqw(path)


def test_rejects_non_numeric_value(tmp_path):
    path = write(tmp_path, "corrupt.txt", "0.1 0.24 1.2\nABC 0.48 1.1\n")
    with pytest.raises(AsciiFormatError, match="non-numeric"):
        load_ascii_sqw(path)


def test_rejects_nan_in_q_axis(tmp_path):
    path = write(tmp_path, "nanq.txt", "0.1 0.24 1.2\nnan 0.48 1.1\n")
    with pytest.raises(AsciiFormatError, match="non-finite"):
        load_ascii_sqw(path)


def test_rejects_inf_in_omega_axis(tmp_path):
    path = write(tmp_path, "infw.txt", "0.1 0.24 1.2\n0.2 inf 1.1\n")
    with pytest.raises(AsciiFormatError, match="non-finite"):
        load_ascii_sqw(path)


def test_rejects_empty_file(tmp_path):
    path = write(tmp_path, "empty.txt", "# just a comment\n")
    with pytest.raises(AsciiFormatError, match="no data rows"):
        load_ascii_sqw(path)


# --- Digitized CSV (Tier C fallback) ------------------------------------

def test_load_digitized_csv_happy_path(tmp_path):
    path = write(tmp_path, "digitized.csv", "0.5,1.2\n1.0,2.3\n1.9,8.6\n")
    data = load_digitized_csv(path)
    assert data.tier == "C"
    assert np.allclose(data.Q, [0.5, 1.0, 1.9])
    assert "digitized" in data.meta["note"]


def test_digitized_csv_rejects_single_column(tmp_path):
    path = write(tmp_path, "bad_digitized.csv", "0.5\n1.0\n")
    with pytest.raises(AsciiFormatError, match="at least 2"):
        load_digitized_csv(path)


def test_digitized_csv_rejects_non_numeric(tmp_path):
    path = write(tmp_path, "bad_digitized2.csv", "0.5,1.2\nQ,W\n")
    with pytest.raises(AsciiFormatError, match="non-numeric"):
        load_digitized_csv(path)
