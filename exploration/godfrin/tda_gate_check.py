"""Check behind docs/designs/TDA_DISPERSION_GATE.md: is 0-dim persistence of the roton
just its topographic prominence?  Answer: yes, to the digit."""
import sys; sys.path.insert(0, "src")
import numpy as np
from scipy.signal import find_peaks, peak_prominences
from quantumfluids.adapters.godfrin_ancillary import load_godfrin_p0_dispersion

d = load_godfrin_p0_dispersion("data/external/godfrin_2021_arxiv_ancillary/DispersionP0allRange.txt")
Q = np.asarray(d.Q).ravel(); E = np.asarray(d.omega).ravel()
m = Q > 0.05; Q, E = Q[m], E[m]
pk, _ = find_peaks(-E); prom = peak_prominences(-E, pk)[0]
i = pk[np.argmax(prom)]
sel = (Q > 0.9) & (Q < 1.4); DM = E[sel].max(); kM = Q[sel][np.argmax(E[sel])]
print(f"roton   k={Q[i]:.3f} A^-1  Delta_R={E[i]:.4f} meV")
print(f"maxon   k={kM:.3f} A^-1  Delta_M={DM:.4f} meV")
print(f"persistence (scipy prominence of -eps) = {prom.max():.4f} meV")
print(f"Delta_M - Delta_R                      = {DM - E[i]:.4f} meV")
print(f"difference                             = {abs(prom.max() - (DM - E[i])):.2e} meV")
print(f"\nsecondary features above the 0.0013 meV error bar: {(prom > 0.0013).sum()} of {len(prom)}")
