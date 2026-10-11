# L1 results (2026-10-11) — KK-tower evaluator, Python/NumPy prototype

Scripts: `kk_eval.py` (evaluators + mpmath reference), `main_acc.py` (accuracy), `main_time.py`, `main_time2.py` (timing).
Data: `accuracy.json` (first two parameter sets only; run cut by timeout), `timing.json`, `timing2.json`, `time.log`.

## Deviations from PREREG (disclosed)
* Reference: mpmath at 10 points per parameter set (20 digits); float64 modal sum is the reference elsewhere (mpmath at all
  160 points was too slow). Float64 modal vs mpmath: max relative error 7.8e-16 (sets 1, 2; sets 3, 4 not reached before the
  timeout). For r > l the hybrid is therefore compared with the modal sum itself (not independent there).
* First run used a reference whose loop stopped on a zero term (bug); discarded, not used.
* Accuracy run for sets 3, 4 and the registered 40-point grid for `accuracy.json` is incomplete; timing used 1e4 random r in [0.3 d, 6 l].
* Naive plain image truncation did **not** reach 1e-12 up to N = 6400 (tail ~ N^-2), so the "naive" speed ratio is only bounded
  below, not measured.

## Findings
* Images + Euler–Maclaurin tail (N = 60) reach 1e-12 only for r ≲ 1.1–1.9 l; beyond that the sum cancels to a value
  ~e^{-π r/l} and double precision loses relative accuracy (21–33 % of the random points pass).
* Modal K0 sum (adaptive truncation, binned in r): rel. error ≲ 1e-12 everywhere on r ≥ 0.3 d; hybrid (images N_min = 32–48
  for r ≤ l, modal above): max rel. error 3.4e-13 – 1.0e-12.
* Speed (1e4 evaluations): modal binned 0.028–0.036 s; images+EM(60) everywhere 0.148–0.191 s → 4.1–6.7× (≥5× on 2 of 4 sets);
  the baseline is only accurate for r ≲ l, so the comparison favours the modal sum on the whole range. Un-binned modal (M set
  by the smallest r) was *slower* than images+EM (0.2–0.6 s).
* The "hybrid" is not needed: the modal series alone on r ≥ 0.3 d is as fast as the hybrid.

## Gate verdict
G1 met (within the disclosed reference caveat). G2 against the registered fair baseline: partial (4.1–6.7×; the ≥2× stop
criterion is not triggered, the ≥5× target is met on 2 of 4 sets). Per PREREG the Rust crate is built only if both gates hold
→ **not built**. No claim beyond: the K0 mode sum is a ~5× cheaper evaluator than a tail-corrected image sum for r ≳ 0.3 d on
CPU/NumPy, and it is what `GatedKernel`'s Prop. 2 already states.
