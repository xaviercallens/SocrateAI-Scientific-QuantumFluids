#!/usr/bin/env python3
# TIER C - EXPLORATORY, NO CLAIMS
"""Pressure dependence of the roton gap Delta(P) and roton wavevector Q_m(P)
from Godfrin et al. 2021's all-pressure dispersion table (arXiv:2012.09067
ancillary DispersionAllPressures.txt) -- a DETERMINISTIC scaling test that is
immune to the single-trajectory problem that sank the shell-model
measurements.

Motivation (theory memo, item C): the programme's coupling law is
m = |disc|^{-s} with the exponent s in {1/2, 1} left OPEN (Mathesis CR-1).
The pressure dependence of the roton parameters is a free empirical probe of
a scaling exponent from author-published data.

Honesty label: this is a FIT to published data. It measures how Delta and
Q_m scale with P; it does NOT by itself connect P to |disc| or to any
T-dual quantity. That connection is a separate, theoretical step and is not
made here.

Method: per pressure, fit the roton branch to a parabola
E = Delta + A (Q - Q_m)^2 over |Q - 1.9| <= 0.2 (the window that gave the
0.04% M1 result at P=0), weighted by the file's own errE column. Then fit
log(Delta) vs log(P + P0) is ill-posed at P=0, so we report Delta(P) and
Q_m(P) directly and fit power laws to the FINITE-P points only, with the
P=0 point shown as the intercept.
"""
import sys
import numpy as np
from scipy.optimize import curve_fit
from scipy import stats

PATH = "data/external/godfrin_2021_arxiv_ancillary/DispersionAllPressures.txt"

def load():
    raw = open(PATH, "rb").read().decode("utf-16")
    lines = raw.splitlines()
    hdr = lines[2].split("\t")
    # columns: idx, Q, then pairs (E, errE) per pressure
    pressures = []
    for j in range(2, len(hdr), 2):
        p = hdr[j].replace("P=", "").replace(" bar", "").strip()
        pressures.append(float(p))
    Q, E, dE = [], [], []
    for l in lines[3:]:
        parts = l.split("\t")
        if len(parts) < 2 + 2*len(pressures): continue
        try: q = float(parts[1])
        except ValueError: continue
        row_e, row_d = [], []
        for j in range(len(pressures)):
            e, d = parts[2+2*j], parts[3+2*j]
            row_e.append(np.nan if e.strip().upper()=="NAN" else float(e))
            row_d.append(np.nan if d.strip().upper()=="NAN" else float(d))
        Q.append(q); E.append(row_e); dE.append(row_d)
    return np.array(pressures), np.array(Q), np.array(E), np.array(dE)

def parabola(q, delta, A, qm): return delta + A*(q-qm)**2

def main():
    P, Q, E, dE = load()
    print(f"Loaded {len(Q)} Q points x {len(P)} pressures: {P.tolist()} bar\n")
    print(f"{'P (bar)':>8} {'Delta (meV)':>14} {'Q_m (A^-1)':>14} {'A (meV A^2)':>12} {'n':>4}")
    print("-"*58)
    rows = []
    for j, p in enumerate(P):
        m = (np.abs(Q-1.9) <= 0.2) & np.isfinite(E[:,j]) & np.isfinite(dE[:,j]) & (dE[:,j]>0)
        if m.sum() < 8:
            print(f"{p:>8} {'--- too few points ---':>44}"); continue
        popt, pcov = curve_fit(parabola, Q[m], E[m,j], p0=[0.74, 3.0, 1.92],
                               sigma=dE[m,j], absolute_sigma=True)
        perr = np.sqrt(np.diag(pcov))
        rows.append((p, popt[0], perr[0], popt[2], perr[2], popt[1]))
        print(f"{p:>8} {popt[0]:>8.4f}+/-{perr[0]:.4f} {popt[2]:>8.4f}+/-{perr[2]:.4f} "
              f"{popt[1]:>12.3f} {m.sum():>4}")
    rows = np.array(rows)
    print()
    # Cross-check P=0 against the M1 single-pressure result
    p0 = rows[rows[:,0]==0.0]
    if len(p0):
        print(f"P=0 cross-check vs M1 (Delta=0.7442, Q_m=1.9074): "
              f"Delta={p0[0,1]:.4f}, Q_m={p0[0,3]:.4f}  "
              f"-> {'consistent' if abs(p0[0,1]-0.7442)<0.005 else 'DISCREPANT'}")
    # Power-law fits on finite P
    fin = rows[rows[:,0] > 0]
    print("\nPower-law fits over the FINITE pressures (P=0 excluded as log(0)):")
    for name, col, ecol in (("Delta", 1, 2), ("Q_m", 3, 4)):
        x, y, w = np.log(fin[:,0]), np.log(fin[:,col]), fin[:,col]/fin[:,ecol]
        r = stats.linregress(x, y)
        h = len(x)//2
        r_lo = stats.linregress(x[:h+1], y[:h+1]); r_hi = stats.linregress(x[h:], y[h:])
        print(f"  {name}(P) ~ P^beta :  beta = {r.slope:+.4f}  r^2 = {r.rvalue**2:.4f}  "
              f"windows[{r_lo.slope:+.4f}, {r_hi.slope:+.4f}]")
    # The physically cleaner statement: relative change per bar (linear regime)
    print("\nRelative sensitivities (finite-difference from P=0, low-P regime):")
    if len(p0):
        for name, col in (("Delta", 1), ("Q_m", 3)):
            d0 = p0[0,col]
            for row in fin[:3]:
                print(f"  {name}: P={row[0]:>5} bar -> {(row[col]-d0)/d0:+.3%}  "
                      f"({(row[col]-d0)/d0/row[0]:+.4%} per bar)")
    print("\nCAVEAT: fits are against P (bar), the variable the file provides. Density")
    print("rho(P) is the physical variable and is NOT in this file; converting requires")
    print("a separately-sourced equation of state and is not done here.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
