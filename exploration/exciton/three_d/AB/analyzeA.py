"""Analyse Experiment A records -> A_summary.json + printed markdown tables; crossover refinement."""
import json, sys, math
import numpy as np
from scipy.optimize import brentq
from lattsum import Kernel
from structures import references
from opt import energy

fn = sys.argv[1] if len(sys.argv) > 1 else 'A_records.jsonl'
refs = {}
starts = {}
for l in open(fn):
    d = json.loads(l)
    key = (d['kernel'], d['param'])
    if d.get('kind') == 'ref':
        refs[key] = d
    else:
        starts.setdefault(key, []).append(d)

R = references()
rows = []
for key in sorted(refs, key=lambda k: (k[0], k[1])):
    r = refs[key]
    E = np.array([s['E'] for s in starts[key]])
    EF, EB = r['E_FCC'], r['E_BCC']
    Eref = min(EF, EB)
    Emin = E[np.isfinite(E)].min()
    rel_below = (Eref - Emin) / abs(Eref)           # >0: found something lower than FCC/BCC
    hit = np.abs(E - Eref) <= 1e-9 * abs(Eref)
    deg = abs(EF - EB) <= 1e-9 * abs(Eref)
    # distinct converged minima (energies rounded to 1e-9 relative)
    uniq = sorted(set(np.round(E / abs(Eref) - 1, 9)))
    pas = rel_below <= 1e-9
    row = dict(kernel=key[0], param=key[1], s=(2 * key[1] if key[0] == 'riesz' else None),
               E_FCC=EF, E_BCC=EB, winner='FCC' if EF < EB else 'BCC', degenerate_1em9=bool(deg),
               rel_gap_FCC_BCC=(EF - EB) / abs(Eref), Emin_found=float(Emin), rel_below_ref=float(rel_below),
               frac_start_at_ref=float(hit.mean()), n_nonfinite=int((~np.isfinite(E)).sum()),
               n_distinct_minima=len(uniq), pass_point=bool(pas))
    if not pas:
        i = int(np.argmin(E))
        A = np.array(starts[key][i]['A'])
        row['non_lattice_winner_A'] = A.tolist()
        G = A @ A.T
        row['winner_gram'] = G.tolist()
    rows.append(row)

n = len(rows)
npass = sum(r['pass_point'] for r in rows)
summary = dict(n_points=n, n_pass=npass, frac=npass / n, gate_A1=bool(npass / n >= 0.95), rows=rows)
json.dump(summary, open('A_summary.json', 'w'), indent=1)

print('| kernel | param | E_FCC | E_BCC | lower | (E_F-E_B)/E | % starts at ref | pass |')
print('|---|---|---|---|---|---|---|---|')
for r in rows:
    p = f"s={int(r['s'])}" if r['s'] else f"{r['param']:.4g}"
    print(f"| {r['kernel']} | {p} | {r['E_FCC']:.10g} | {r['E_BCC']:.10g} | {r['winner']}{' (tie<1e-9)' if r['degenerate_1em9'] else ''} | "
          f"{r['rel_gap_FCC_BCC']:.3e} | {100*r['frac_start_at_ref']:.0f} | {'yes' if r['pass_point'] else 'NO'} |")
print(f"\nA1: {npass}/{n} = {100*npass/n:.1f}% -> {'PASS' if summary['gate_A1'] else 'FAIL'}")
fails = [r for r in rows if not r['pass_point']]
for r in fails:
    print('FAIL', r['kernel'], r['param'], 'Emin', r['Emin_found'], 'ref', min(r['E_FCC'], r['E_BCC']), 'below', r['rel_below_ref'])
    print('   gram', np.round(r['winner_gram'], 4).tolist())

# ---- crossover refinement (continuous parameter) ----
print('\nCrossovers:')
cr = {}
def dE(name, par):
    k = Kernel(name, par)
    return energy(k, *R['FCC'][:2]) - energy(k, *R['BCC'][:2])

for name in ('gauss', 'yukawa'):
    xs = np.logspace(-1, 1, 13)
    # scan finer
    xf = np.logspace(-1, 1, 201)
    vals = np.array([dE(name, x) for x in xf])
    # normalised
    roots = []
    for i in range(len(xf) - 1):
        if vals[i] * vals[i + 1] < 0:
            roots.append(brentq(lambda x: dE(name, x), xf[i], xf[i + 1], xtol=1e-14, rtol=1e-13))
    cr[name] = roots
    print(name, 'sign changes in [0.1,10]:', roots, ' signs at ends:', np.sign(vals[0]), np.sign(vals[-1]))
    # report where FCC - BCC is below machine-noise: sign unreliable
    dn = np.abs(vals) / np.array([abs(energy(Kernel(name, x), *R['FCC'][:2])) for x in xf])
    print('  min relative |E_F-E_B|/E on fine grid: %.2e at %.4g' % (dn.min(), xf[dn.argmin()]))

# Riesz in continuous s via scipy gammaincc recursion (independent of the numba engine)
from scipy import special
def gam_up(a, x):
    if a > 0:
        return special.gamma(a) * special.gammaincc(a, x)
    return (gam_up(a + 1, x) - x ** a * np.exp(-x)) / a
def riesz_lat(s, A0, tau=3.0, nr=8):
    A = A0 * (1.0 / abs(np.linalg.det(A0))) ** (1 / 3)
    m = s / 2
    nn = np.array(np.meshgrid(*[np.arange(-nr, nr + 1)] * 3, indexing='ij')).reshape(3, -1).T
    d = nn @ A
    r2 = (d * d).sum(1)
    nz = r2 > 1e-12
    Er = (special.gammaincc(m, tau * r2[nz]) / r2[nz] ** m).sum()
    Binv = np.linalg.inv(A)
    G = 2 * np.pi * nn @ Binv.T
    g2 = (G * G).sum(1)
    z = g2 > 1e-12
    h = np.pi ** 1.5 * (g2[z] / 4) ** (m - 1.5) * gam_up(1.5 - m, g2[z] / (4 * tau)) / special.gamma(m)
    h0 = np.pi ** 1.5 * tau ** (m - 1.5) / ((m - 1.5) * special.gamma(m))
    self0 = tau ** m / (m * special.gamma(m))
    return 0.5 * (Er + h.sum() + h0 - self0)
def dEs(s):
    return riesz_lat(s, R['FCC'][0]) - riesz_lat(s, R['BCC'][0])
ss = np.linspace(3.05, 30, 400)
v = np.array([dEs(s) for s in ss])
roots = [brentq(dEs, ss[i], ss[i + 1], xtol=1e-12) for i in range(len(ss) - 1) if v[i] * v[i + 1] < 0]
print('riesz: sign of E_FCC - E_BCC over s in [3.05, 30]:', set(np.sign(v)), 'roots', roots)
cr['riesz_s'] = roots
cr['riesz_sign_range'] = [float(x) for x in sorted(set(np.sign(v)))]
json.dump(cr, open('A_crossovers.json', 'w'), indent=1)
