# H1''' — larger-K V3 gate for the certified two-point LP bounds (pre-registration, 2026-10-16)

Directory `three_d/H1ppp/`. Successor of H1'' (`../H1pp/`, RESULTS.md, commits 301c2e3/25eecce): there V1a, V1b, V2
passed and **V3 (d = 3, α = π) failed** at K = 40: certified B = 0.2232177894732, 3.05e-8 below the published
(non-rigorous, 8-digit) 0.22321782, outside the registered 1e-8 window. H2/H4/H8 were gated. The cause was left
undetermined (K truncation is one untested candidate). This round tests the truncation candidate only.

## What changes, and what does not

- **Method, row grids, certificate steps (a)–(e), gcut = 1e-12, round cap 25, λ ladder, b values, void
  conditions: identical to `../H1pp/PREREG.md`.** Code `rig3.py` = `rig2.py` + checkpoint/resume only
  (`ckpt=`; assertion prune=False). Verified before registration on a non-gate toy case (d = 1, α = 2, b = 3/2,
  K = 10, reduced grids): an interrupted-and-resumed 4-round run gives bit-identical exact coefficients and
  history length to an uninterrupted run. No gate parameter was run in rig3.
- **K only:** K = 50 (K_eff = 49) and K = 60 (K_eff = 59).

## Runs (all launched in parallel, single-threaded; `launch.sh`, which skips cases with a record)

V3 at K = 50 (**gate**) and K = 60 (reported); H2, H4, H8 at K = 50 (reported; registered results only if the gate
passes, otherwise "gated"). b: V3 17/20, H2 106/79, H4 7/10, H8 29/99 (as H1'').

## Gate and reading

- **V3 gate (K = 50):** certified B >= 0.22321782 − 1e-8 (same window as H1'').
- Pass → H2/H4/H8 at K = 50 are registered results (G > 1e-3 reading as H1''). Prediction: V3 passes, G > 1e-3 at all
  three, B's within 1e-6 relative of the H1' numerical values.
- Fail at K = 50 with K = 60 pass → reported as K-dependence; the gate still counts as failed (K = 60 not a
  registered gate). Fail at both → truncation is not the (only) explanation; reported as such.
- Also reported: B(K=50) − B(K=40) for every case; monotone in K or not.
- A reboot/kill is handled by relaunching `launch.sh` (resumes from `records/ckpt/`); resumption changes nothing
  numerically and is disclosed in RESULTS.
