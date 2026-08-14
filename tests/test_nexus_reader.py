"""Tests for adapters.nexus_reader — happy path + negative controls (LL-2).

Skipped entirely if h5py is not installed (see M1_CHECKLIST.md dependency
notes). Synthesizes a minimal .nxs file matching the "nxdata_generic"
layout so the adapter can be exercised without a real ILL sample.
"""

import numpy as np
import pytest

h5py = pytest.importorskip("h5py")

from quantumfluids.adapters.nexus_reader import NexusFormatError, load_nexus_sqw


def write_nxdata_generic(path, Q, omega, S, dS=None):
    with h5py.File(path, "w") as f:
        grp = f.create_group("entry0/data")
        grp.create_dataset("Q", data=Q)
        grp.create_dataset("omega", data=omega)
        grp.create_dataset("S", data=S)
        if dS is not None:
            grp.create_dataset("S_error", data=dS)


# --- Happy path ---------------------------------------------------------

def test_load_valid_nxdata_generic(tmp_path):
    path = str(tmp_path / "valid.nxs")
    Q = np.array([0.1, 0.2, 0.3])
    omega = np.array([0.0, 1.0, 2.0])
    S = np.random.rand(3, 3)
    dS = np.full((3, 3), 0.1)
    write_nxdata_generic(path, Q, omega, S, dS)

    data = load_nexus_sqw(path)
    assert np.allclose(data.Q, Q)
    assert np.allclose(data.omega, omega)
    assert data.S.shape == (3, 3)
    assert data.meta["layout"] == "nxdata_generic"


def test_load_without_error_dataset(tmp_path):
    path = str(tmp_path / "no_err.nxs")
    Q = np.array([0.1, 0.2])
    omega = np.array([0.0, 1.0])
    S = np.random.rand(2, 2)
    write_nxdata_generic(path, Q, omega, S, dS=None)

    data = load_nexus_sqw(path)
    assert data.dS is None


# --- Negative controls (LL-2) --------------------------------------------

def test_rejects_unknown_layout(tmp_path):
    path = str(tmp_path / "unknown.nxs")
    with h5py.File(path, "w") as f:
        f.create_group("some/random/path").create_dataset("junk", data=[1, 2, 3])

    with pytest.raises(NexusFormatError, match="no known NeXus layout"):
        load_nexus_sqw(path)


def test_rejects_axis_swap_via_shape_mismatch(tmp_path):
    """The classic LL-2 failure mode: Q and omega datasets swapped.

    Swapping Q (len 3) and omega (len 5) makes S's shape inconsistent with
    (len(Q), len(omega)), which SQwData2D.__post_init__ must catch.
    """
    path = str(tmp_path / "swapped.nxs")
    with h5py.File(path, "w") as f:
        grp = f.create_group("entry0/data")
        # S has shape (3, 5) matching the CORRECT (Q, omega) order.
        # We deliberately write Q as the len-5 array and omega as len-3,
        # simulating an upstream swap.
        grp.create_dataset("Q", data=np.linspace(0, 1, 5))
        grp.create_dataset("omega", data=np.linspace(0, 1, 3))
        grp.create_dataset("S", data=np.random.rand(3, 5))

    with pytest.raises(NexusFormatError, match="does not match"):
        load_nexus_sqw(path)


def test_rejects_nan_in_q_axis(tmp_path):
    path = str(tmp_path / "nanq.nxs")
    with h5py.File(path, "w") as f:
        grp = f.create_group("entry0/data")
        grp.create_dataset("Q", data=[0.1, np.nan, 0.3])
        grp.create_dataset("omega", data=[0.0, 1.0])
        grp.create_dataset("S", data=np.random.rand(3, 2))

    with pytest.raises(NexusFormatError, match="non-finite"):
        load_nexus_sqw(path)


def test_rejects_non_monotonic_q_axis(tmp_path):
    """A shuffled Q axis is a strong signal of misread/corrupted data."""
    path = str(tmp_path / "nonmono.nxs")
    with h5py.File(path, "w") as f:
        grp = f.create_group("entry0/data")
        grp.create_dataset("Q", data=[0.1, 0.5, 0.2])  # not monotonic
        grp.create_dataset("omega", data=[0.0, 1.0])
        grp.create_dataset("S", data=np.random.rand(3, 2))

    with pytest.raises(NexusFormatError, match="monotonic"):
        load_nexus_sqw(path)
