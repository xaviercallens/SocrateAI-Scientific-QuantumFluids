# H1d — rigorous upper bounds on the Gaussian-energy two-point bound in R^3 (pre-registration, 2026-10-17)

Directory `three_d/H1d/`. Math, literature gate and development: `DESIGN.md` (read it first). Code frozen at this commit:
`dual.py` (float LP by HiGHS interior point + arb certificate), `run_h1d.py`, `launch.sh`, `evaluate.py`.

## Claim type

For the class 𝓗 of DESIGN.md (continuous radial h, ĥ ≥ 0, h ≤ e^{-α|x|²} off 0, decay |h|, |ĥ| ≤ C(1+|x|)^{-d-δ}), LP(α) =
sup ĥ(0) − h(0) at density 1. Each certified run gives UB with **LP(α) ≤ UB** (upper end of an arb ball). With H1'''/H1''
certified lower bounds B this gives the sandwich B ≤ LP(α) ≤ UB*. UB* < min(E_FCC, E_BCC) means: *no* function in 𝓗 gives a
two-point bound that reaches the best lattice energy at that α, so two-point bounds in 𝓗 cannot prove FCC/BCC optimality there.

## Runs (`launch.sh`, 3 in parallel, one record per (case, s, m); relaunch resumes)

- V1: d = 1, α = π; (s, m) ∈ {(2, 8), (4, 32), (8, 128)}.
- V2: d = 2, α = π; {(4, 32), (4, 48), (6, 72), (8, 96)}.
- D3pi, D3a2, D3a4, D3a8: d = 3, α = π, 2, 4, 8; {(4, 24), (5, 30), (6, 36), (5, 40), (6, 48), (8, 48)}.
ε = 1e-8 (μ ≥ ε in the float LP), λ rounded with denominators ≤ 2^64; UB* = min over the case's certified grids (each grid's UB
is a valid bound, so taking the minimum is not a selection effect).

## Gates (validation first; D3 results are registered only if V1 and V2 pass and no VOID)

- **VOID (bug)** in any case: a certified UB below the certified lower bound B of the same (d, α) (V1: H1'' V1b K40; V2: H1''
  V2 K40; D3: H1''' V3/H2/H4/H8 K50), or in V1 below E_Z(π)(1 − 1e-12).
- **V1 (tightness, d = 1, where the LP bound is sharp, CK Prop. 9.6 as cited by CdCI):** UB* ≤ E_Z(π)(1 + 1e-6).
- **V2 (consistency only):** no VOID. Tightness in d = 2 is reported, not gated (development: 0.3–0.8% above E_A2 at α = 2).

## Reading and prediction

Per D3 case: "UB* < min(FCC, BCC)" (certified: no two-point bound in 𝓗 reaches the best lattice) or "not shown at this
resolution". Also reported: sandwich width (UB* − B)/B, UB* by grid, and for α = π UB* − 0.23153532 (CdCI record).
Prediction: V1 and V2 pass; all four D3 cases give UB* < min(FCC, BCC), α = 2 with the smallest margin; D3pi UB* below the
CdCI record. If the prediction fails for α = 2 only, that is reported as resolution-limited, not as evidence for sharpness.
Not claimed: anything about functions outside 𝓗 (Prop. 2.2's wider class), three-point bounds, or the true minimal energy.
