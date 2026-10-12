# Adversarial review: 3D round 2 (T2, T1, H1, F1 prose), paper V round-2 text (2026-10-12)

Reviewer: an independent agent that did not write any of the reviewed material. No existing file was edited. Python checks
were run single-threaded (OMP_NUM_THREADS=1), at most one process at a time, each under 10 min. The F1 background job was
not touched. Scratch scripts are in the session scratchpad and are not part of the repository.

Scope: `exploration/exciton/three_d/PREREG_round2.md` (51a85b1), `T12/RESULTS.md`, `H1/RESULTS.md`, the records, logs and
scripts in those directories, `paper/exciton_fluid_gated_V_round2.tex`, and the F1 prose that does not depend on placeholders
(checked against `F1/records_N120.jsonl` seeds 0-5 and `F1/records_N24.jsonl`).

Timeline check: commit 51a85b1 (08:17:37) adds only `PREREG_round2.md`. Every round-2 record or log has a later mtime:
T2 08:23-08:44, F1 from 08:22, H1 08:36-08:53, T1 08:51-09:32. The pre-registration does predate the results.

CKS 2009 (arXiv:0911.2169v2) was read for this review through alphaXiv (full text returned). Quotations below come only from
that text.

---

## Blocking (must fix before deposit)

**B1. The T2 claim "lowest energy equals the best reference to ≤ 2e-15 in every cell" is false.**
`paper/exciton_fluid_gated_V_round2.tex:48-49` ("in every cell the lowest energy found equals the best reference lattice to
$\le2\times10^{-15}$") and `T12/RESULTS.md:70` ("<= 2e-15 relative"). I recomputed (E_min − min(E_FCC, E_BCC, E_HCP))/E for
all 75 cells from `T2_records.jsonl` (5 100 records) and `T2_refs.json`. The most negative value is −1.9e-15, which is what
the RESULTS verdict row says. But **14 cells have E_min above the reference by more than 2e-15**, up to **+3.7e-13**. All
of them are pair 2 (π/4, 4π) with N ≥ 8: idx 10 N=16 +3.7e-13; idx 12 N=16 +2.8e-13; idx 14 N=16 +1.7e-13; idx 11 N=16
+9.8e-14; and so on. `T2_analysis.txt` already shows this (for example `+1.497e-14` for idx 10 N=8). The gate verdict does
not change: no cell is below the reference, and every cell has hits at 1e-8. The sentence should read something like
"never below the best reference by more than 2e-15, and within 4e-13 above it (pair 2, N ≥ 8)".

**B2. The F1 prose contains two numerical claims that no file in the repository supports.**
- `tex:31` "A separate check with 40 fresh seeds gives 12/40." I searched the repository with grep for this check and found
  no script, record or log for it. The value is plausible: the per-run success rate of the F1b restarts at a=4 is 226/699
  = 0.32 in seeds 0-5. But it cannot go into a deposit without its record.
- `tex:25-26` "already at $a_0=0.25$ the converged state is $3\times10^{-11}$ above $E_{600}$ **without being the
  600-cell**". The energy part is confirmed: rung-0 excess 2.3e-11 to 3.9e-11 across all 27 ladders and 2.3-3.7e-11 in seeds
  0-5. The structural part ("not the 600-cell") is not. The rung records carry no chord or coordinates. The script written
  for this purpose, `F1/supp_rung_chords.py`, writes `supp_rung_chords_s*.json`, and no such file exists anywhere on disk.
  At a=0.25 the rung stops on the relative-reduction test with gmax ≈ 1.4e-6. An excess of 1e-7 absolute (3e-11 relative)
  is therefore also compatible with an incompletely converged 600-cell on a very flat landscape. Either run
  `supp_rung_chords.py` and commit its output, or weaken the claim to an energy statement. (Smooth growth of the excess along
  the ladder is indirect evidence for a separate branch. It is not a chord measurement.)

**B3. The explanation for pair 2's λ* deviation is wrong by about three orders of magnitude.**
`tex:46-47` says "limited by the $10^{-9}$ size of the $a_2=4\pi$ contribution". `T12/RESULTS.md:41-42` says "the a2 = 4pi
component contributes only ~1e-9 to the energy (E(4π) ~ 1e-9 for FCC/BCC)". An independent brute-force lattice sum
(half-sum convention, unit density) gives **E_FCC(4π) = 7.98e-7 and E_BCC(4π) = 1.28e-6**, with dE(a2) = E_FCC − E_BCC =
**−4.8e-7**. The `T2_refs.json` splittings imply the same value: (E_FCC − E_BCC) at λ*·0.9 = 3.85e-7 = 0.8·|dE|. The real
precision limit is cancellation. The total energy is about 3.5 (ulp about 4e-16), and it is divided by dE ≈ 5e-7, so λ* is
resolved to about 1e-9 absolute, which is about 2e-10 relative. My own brute-force closed form gives λ* = 8.0000000018,
deviating in the opposite direction, which confirms that this is double-precision noise. The "2.3e-10 relative" figure is
correct; only the stated cause is wrong.

**B4. A cited fact is stated more firmly than the source states it (main file, carried into round 2).**
`paper/exciton_fluid_gated_V.tex:72-73` says "at $\alpha=\pi$ itself **the ground state is** a Maxwell coexistence ...
~\cite{CKS09}". CKS Table I is captioned "Lowest known energies in dimension n when ρ = 1. The third column specifies the
**putative** ground state, with 'pc1' ... standing for phase coexistence between D3 and D3*". The text body says "This
appears to give a complete description of the phase transition from D3 to D3*". Both numbers are quoted correctly from the
source: 0.11576766... (n=3, pc1) and "0.99899854 . . . ≤ ρ ≤ 1.00100312 . . .". Write "the lowest known state (putative
ground state) is ...". Round-2 `tex:52` ("coexistence that CKS report") is fine.

---

## Should fix

**S1. T1 basin test: at small ε the perturbed start already satisfies the surrogate.** `T1_basin.jsonl` records only the end
state. I reran draw 0 of `basinT1.py` (diamond, ε = 1e-3, rng 4242). My end values are bit-identical to the record
(M = 1.0299803030e-15, shell mismatch 30.1407). **The unminimised perturbed start already has surrogate M = 3.6e-11, below
the 1e-10 level the failbox uses, and shell mismatch 30.49.** So "the minimiser ends at surrogate ≤ 1e-10 in 50/50 cases"
(`tex:68-69`, `RESULTS.md:144-145`) is not an achievement of the minimiser at small ε. It shows that a 1e-10 surrogate level
cannot resolve a 1e-3 displacement from diamond. This supports reading (i), non-identification, more than reading (ii),
"cannot return". The conclusion "uninformative" stands. Rephrase (ii) and report the start M and start mismatch, at least
for ε = 1e-3.

**S2. T1 detector: the stated mechanism of the discontinuity is incomplete.** `tex:70-71` ("any splitting of a degenerate
shell misaligns") and `RESULTS.md:147-148`. On the reproduced ε=1e-3 end state, both measures split diamond's first shell
(0.866, ×4) into four sub-shells, so splitting alone does not misalign them. What misaligns them is that ν gains **near-extinct
reflections**: shells at r ≈ 0.9985, 0.9998, 1.0017 with weights below 5e-5. These are diamond's systematic absences
(|S|² = 0 exactly at the control). Their weights now exceed the floor `wmin = 1e-8` in `selfdual.shells`, so they are counted
as shells. μ has no counterpart, so every later ν index is shifted by 3 and the mismatch becomes ~30. The detector is still
correct on the controls, and the end state is genuinely not self-dual: at α = 30 the relative residual is 1.5e-5 and the CDF
distance is 0.022. The "uninformative" reading therefore survives. Correct the explanation, and disclose that the grouping
tolerance (1e-6) and the weight floor (1e-8) are implementation choices that were not registered.

**S3. T1 (i): "does not identify" should be stated as a numerical claim.** `tex:66-67` says "the Gaussian identity on a
finite range of exponents does not identify formal self-duality". Θ_μ(α) − Θ_ν(α) is analytic in α. Exact vanishing on an
interval therefore forces μ = ν, as the docstring at `selfdual.py:18-19` itself states. What was shown is numerical: 40
sampled exponents with relative residuals of about 1e-8 (M ≈ 1e-15) admit configurations whose measures differ at O(1). I
confirmed this on the best N = 2 record: the relative residual is 0.3% at α = 30 and 1.2e-10 at α = 0.3. RESULTS.md says
"ill-conditioned", which is right; the tex should say the same.

**S4. H1: "H0 failed" rests on a tolerance that was not registered. The tex headline hides this.** The registered H0 text is
"the code must reproduce E_Z(α) to 1e-8 at α ∈ {1, π}" (`PREREG_round2.md:55-56`). At α = π the three full-setting LP values
are 0.08643481138486, 0.08643481137720 and 0.08643481149488 (`run.log`), that is **+1.6e-10 to +2.8e-10** from
E_Z(π) = 0.08643481121331. They fail only `VIOL_FULL = 5e-9` in `run_h1.py:25`, which is not in the pre-registration
(violations 2.1e-8, 4.6e-8, 4.1e-8). Deviation 1 discloses this, and stopping is the conservative choice. But
`tex:83` "**H0 failed; H1 was stopped as registered**" reads as if the failure criterion were registered. Suggested wording:
"H0 failed under the code's admissibility tolerance (fixed before the run, not in the pre-registration); the stop then
followed the registered rule."
Provenance of the tolerance: **only file mtimes support it, not a commit.** No commit precedes the run; the first is a693b54
at 09:36. `run_h1.py` mtime is 08:36:51. The run start is inferred at about 08:36:57: `solutions/d1_alpha1.json` mtime
08:42:54 minus the logged 357 s, and `summary.json` "date": "08:36". `run_h1.py` was not modified afterwards. Also,
`H1/__pycache__/lp_bound.cpython-312.pyc` was compiled at 08:34:05 from a source with mtime 08:33:56. That means `lp_bound`
was imported about 3 min before the run, possibly in a pilot whose output is not kept. The text should say "fixed in code
before the run (file timestamps; no commit)" rather than imply a commit-level guarantee.

**S5. H1 RESULTS gives a wrong number for the coarse-scan offset.** `H1/RESULTS.md:108` says the coarse solutions "lie 4e-8
*above* E_Z(π)". From `run.log` the eight coarse bounds are 0.08643514955-0.08643524232, which is **+3.4e-7 to +4.3e-7**
above E_Z(π), ten times larger. Also, `RESULTS.md:99` "+2e-10 to +3e-10" should be +1.6e-10 to +2.8e-10.

**S6. H1: `lp_bound.py` was edited while the run was in progress.** Its mtime is 08:38:16, about 80 s after the run started.
I compared the code objects of the cached bytecode with the current file: they are identical except for the module
docstring. Deviation 4 ("no code was changed") therefore holds for executable code, but the edit should be disclosed in one
line, because a referee checking mtimes will see it.

**S7. H1: no evidence that the bound was transcribed from the source.** The pre-registration requires the "Exact statement
to be transcribed from Cohn–Kumar 2007 Prop. 9.3 / CKMRV 2022 §1 before coding" (`PREREG_round2.md:45-46`). `H1/RESULTS.md`
§1 gives a self-contained proposition and proof sketch. I checked the sketch and it is correct: Poisson normalisation with
|Λ| = N, dropping y ≠ 0 terms, adding back N·f(0)/N. But nothing shows a transcription from CK07, and `tex:76` has no
\cite. Add \cite{CK07} and either the transcription or a note that the statement was derived and checked rather than
transcribed (a deviation).

**S8. F1 rung-cap count.** `tex:28-29` says "Eight to nine of the 17 rungs stop at C's 8 000-iteration cap". a=4 seeds 0-5
give 8, 9, 8, 8, **7**, 8 capped rungs; all 8 current a=4 ladders give 7-9 (mean 8.1). It should read "seven to nine".

**S9. F1 N = 24: "a different minimum chord" overstates.** `tex:34-35`. The six a = 1 runs that miss the chord test have
min chord 0.9999981-0.9999989, that is 1.1-1.9e-6 from 1, just over the 1e-6 threshold, at the 24-cell energy to 1e-8. This
is consistent with incomplete convergence on a soft kernel, not a different configuration. Write "a minimum chord 1-2e-6
from 1 (just outside the 1e-6 tolerance)". Everything else in the paragraph checks out: 50/50 E-only at every a; 44/50 with
chord at a = 1; C plain 25, 7, 0; F1b plain 50, 47, 27; never below the 24-cell.

**S10. F1 deviation missing from the tex.** `run_F1.py:27-29` replaces C's energy/gradient evaluator with a Gram-matrix
version ("deviation 1" in its docstring; `check_evaluator` asserts agreement to 1e-12). The tex "Round 2 deviations"
paragraph (`tex:87-96`) does not list it. Add it.

**S11. F1 p-value: name the test.** `tex:31-32` gives "two-sided p≈0.002 against the pooled rate". With seeds 0-5 the
pooled per-run rate is 226/699 = 0.323. A binomial two-sided test of 6/50 against 0.323 gives p = 0.0013; Fisher's exact test
of 6/50 against 226/699 gives 0.0023; Fisher's test of 6/50 against 12/40 alone gives **0.061**. State which test is meant
and recompute it when F1 finishes. Note also a small survivorship effect: per-run rates count only completed runs, and the
budget-truncated last run of each seed is dropped (`analyse_F1.py:84`). Truncated runs are more likely to be the slow,
trapped ones.

**S12. T1 controls table: stale surrogate values.** `T12/RESULTS.md:103-109`, "surrogate M" column, against
`T1_controls.json`:

| Control | RESULTS.md | T1_controls.json |
|---|---|---|
| diamond | 4.8e-30 | 2.55e-29 |
| HCP | 4.4e-6 | **8.13e-5** |
| FCC | 3.7e-6 | **7.06e-5** |
| SC | 1.9e-30 | 3.5e-29 |
| bct | 1.4e-29 | 1.40e-29 (matches) |

The HCP and FCC values in RESULTS.md look like run-1 (absolute-residual) numbers. The shell-mismatch column matches the
JSON.

**S13. Stale comment in `selfdual.py`.** `selfdual.py:135-138` says "Run 2 final choice: alpha = pi s, s in [0.1, 1]
(exponents 0.31-3.14)", but the defaults are `smin=0.3` (exponents 0.94-10.5). Run 3 reproduces run 2 bit for bit with these
defaults: 20/20 N = 8 records identical in M and mismatch, checked. Deviation 5 corrects the stale comment in `expT1.py` only.
Mention this one too.

**S14. T2 coexistence remark is argued, not shown.** `RESULTS.md:81-82` says "no coexistence approximant appeared in T2
**and none could have**", and `tex:51-53` says "cannot represent". The bulk-energy gain (4e-6) against interface cost is a
physical argument, not a demonstration. Write "is not expected to" or give the estimate.

---

## Minor

- `T12/RESULTS.md:74` says hit fractions away from λ* are "0.33-0.6", but its own table and the tex say up to 0.72. I
  recomputed 0.325-0.725.
- `T12/RESULTS.md:75` "pair 3 at lambda*/1.1" should be λ*·1.1: idx 24, fac 1.1 gives FCC 0.53328095, HCP 0.53336458,
  BCC 0.53336865.
- λ* for pair 1: the bisection gives 2.82842712475167 against exact 2√2 = 2.82842712474619, a difference of 5.5e-12
  (1.9e-12 relative). The tex's "recovers 2√2" is fine; give the figure for symmetry with pair 2.
- `tex:62` quotes the pre-polish minimum mismatches (19.8, 7.7, 1.26). The polish stage lowered N = 8 to 0.30
  (`T1_polish.log`); mention it for completeness.
- H1: the d = 1 LP bound is sharp in the space of all admissible f. That does not guarantee that the K = 30 Gaussian ×
  polynomial ansatz reaches 1e-8. The H0 failure may be partly an ansatz limitation and not only a certification issue.
  RESULTS says "with K = 30", but the tex does not.
- H1: the α = 1 "pass" bound is itself 2.0e-9 *above* E_Z, so it is invalid by value. Its worst violation,
  f − g = 9.9e-10 at r ≈ 7.0, accounts for this. The text says so. It is worth stating that the 1e-8 registered
  tolerance and the 5e-9 code tolerance therefore measure the same discretisation error from two sides.

---

## Verified (recomputed and matched)

T2
- 75 cells, 5 100 restarts, restart counts 100/100/60/40/40, 0 candidates; most negative relative excess −1.884e-15.
- Hit fractions: 0.75-1.00 at λ* and 0.325-0.725 elsewhere (tex 0.33-0.72).
- λ*: an independent brute-force lattice sum (my own code) gives 2.828427124750, 8.0000000018 and 2.016585262761, against
  JSON 2.82842712475167, 7.999999998137 and 2.01658526276015. Closed form (π/a1)^{3/2} = 2√2 and 8 confirmed analytically:
  for a1·a2 = π² the 3D transform of e^{−a1 r²} is (π/a1)^{3/2} e^{−a2 r²}, so f̂ = f.
- `engine_check.json`: worst relative deviation against the stored round-1 references is 0.0.
- E_FCC(π) = E_BCC(π) = 0.115768133092074 (half-sum, my brute force), E_SC(π) = 0.141181557930, both matching RESULTS.
  2E = 0.231536266184 equals the registered threshold. (0.115768133 − 0.11576766)/0.115768133 = 4.1e-6, correct.

T1
- `T1_summary.json`: 60/60/40 starts, 0 accepted, minimum mismatch 19.85/7.69/1.26, minimum M 3.8e-15/6.4e-15/7.4e-13.
- Controls: diamond 1.05e-26, FCC↔BCC 0, SC 0, bct 8.8e-30, HCP 3.2e3, FCC/FCC 3.5e4.
- The surrogate is computed correctly. Engine residuals agree with direct sums over `pair_measure`/`sf_measure` to 2e-15
  on the best N = 2 and N = 4 records, on diamond, and on perturbed diamond. The engine and `selfdual.py` both use the
  row-basis convention (x = S @ A; the dual basis is inv(A).T, so the phase 2π m·s is correct), so there is no
  transpose bug. Note that the controls use symmetric cells and could not have revealed one.
- The diamond cell in `basinT1.py` and `diagW1T1.py` (FCC with cube side 2, offset (¼, ¼, ¼) in the primitive basis = (½, ½, ½)
  Cartesian) is D3+ at unit density, which is CKS's D3+ (det D3 = 2, two cosets). The SC_2pt cell diag(2, 1, 1) with points
  0 and (½, 0, 0) is Z³ at unit density.
- The |S|²/N² weight is confirmed by CKS Sec. VI: "N/vol(R^n/Λ) Σ f̂(y) |(1/N) Σ_j e^{2πi⟨v_j,y⟩}|²", with N/vol = density
  = 1. The CKS definition matches selfdual.py's docstring and the tex: "P and Q are formal duals if for every Schwartz
  function f, the average pair sum of f over P is δ times that for f̂ over Q", with the average pair sum including j = k,
  x = 0. "Proposition 1. The D+n structure is formally self-dual when n is odd ..." supports the diamond positive control.
  CKS's remark that "radial symmetry erases the distinction between formal self-duality and formal isoduality" supports the
  bct (isodual) control reading 0.
- CDF L1 distances: 1.391, 2.404, 0.697 for the best N = 2/4/8 records, and 0 for diamond, all matching. The best N = 2
  record's first shells match RESULTS.md:137-139.
- `T1_basin.jsonl`: 50 records, 0 accepted, maximum end M 9.0e-11, shell mismatch 28.38-72.68. Draw 0 at ε = 1e-3 was
  reproduced bit for bit.
- Run 3 against run 2: 20/20 N = 8 records bit-identical in M and shell mismatch. Run 2 started at about 08:56:20, after
  the last edit of `selfdual.py` (08:56:12), so N = 2 and 4 used the same code.

H1
- `summary.json` and `run.log`: α = 1 bound 0.7726372068320 against E_Z 0.7726372048267, +2.005e-9; β_best 0.13316;
  violations 9.9e-10 / 1.7e-11; α = π has no admissible full solution, violations as in the tex (2-5e-8). H0 pass = false,
  and the run stopped.
- The proof sketch in RESULTS §1 is correct (convention, Poisson factor 1/|Λ|, |Λ| = N, sign check with f = g).
- Runtimes: α = 1 357 s; α = π about 10.4 min; total about 16.3 min.

F1 (prose only, seeds 0-5 of N = 120 plus N = 24)
- F1a has 6 misses at every a after seeds 0-5, as stated in `tex:89-90`.
- Excess at a=1: 1.75-2.24e-8. At a=2: 7.2-7.6e-6. At a=4: 1.05-1.09e-3. These match C's trapped plain runs at the same
  seeds (2.3-2.7e-8, 6.9-7.5e-6, 1.01-1.11e-3).
- Gradient evaluations: 6.7-7.3e4 at a=1, 8.5-9.5e4 at a=2, 8.7-9.5e4 at a=4. This is consistent with "≈7-9.5×10⁴"
  (the a=1 minimum is 6.7e4).
- The F1b plain runs at a=4 hit the 600-cell in 6/6 seeds; 226 of 699 completed restart runs hit it.
- N = 24: verified as listed in S9.
