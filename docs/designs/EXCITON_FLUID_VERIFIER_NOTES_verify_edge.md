# Verification of package 'edge' (hostile verifier)

Verdict: accept_with_fixes.

## Independently re-checked (own code, scratchpad/v/recheck.py and ad hoc)
- All 65 best configurations (min over runs, runs_aligned, runs_extra polished records) re-evaluated with my own image-series
  (period 2D) / polygon / disk / trap code: E_int agrees with recorded values to 4e-16..2.5e-15 (dip); g10 to 3e-9 and g3 to
  4e-7 only because MY series was truncated at |n|<=3000 (tail error shown by comparison with n<=1e5 and the K0 series:
  agreement 1e-9 relative). E_wall agrees to <=7e-11 relative. Worker's kernel is correct.
- e_lat(0.5): dip 1.3349250 (R=200..400 with continuum tail), g3 0.3860642, g10 1.0231922 equal the worker's values. E_edge arithmetic
  reproduced for all 65 cases (my first dip offset of 0.0039/particle was MY tail bug: half-weight; worker's tail is right).
- LDA reference (trap): independent profile integration gives E_LDA within 0.1% (dip, my cutoff 1e-3 density) and 1e-7 (g3). E_edge^trap
  numbers (~-2.07 sqrt N dip; ~-1.04 g3) stand.
- Fits (gamma, c, gamma_P spread 1.12 dip / 1.045 g3), aspect-ratio monotonicity (dip all N; g3 N=37,61; g3 N=19 non-monotone)
  and E-e count 58/65, E-c 0/55 halved detection: all match summary.json/cases.md and the worker's text.
- Gates: ea.txt/eb_bug*.json show E-a, E-a2, E-b pass and bugs 1-4 fail E-b as stated.
- Prereg integrity: PREREG committed 10:31:13, tables 10:32, gates 10:32-10:34, first production file 10:34:25; diff of PREREG
  from first commit to HEAD removes only 2 lines (interior definition replaced per A1, '(none yet)'). Gates sections 5-8 unchanged.

## Problems
MAJOR
1. No results write-up exists in the repo. The assigned docs/designs/EXCITON_FLUID_EDGE_PREREG.md / _RESULTS.md and ob.rs do not
   exist; files live in exploration/exciton/edge/ (outside the assigned paths; a new crate qf-exciton-edge). The findings
   (aspect tables, 'perimeter law', hexagon defect story, limits) exist only in the worker's message. REPORT.md was not written.
2. The hexagon 'relaxed perfect patch lies 0.16%, 1.2%, 0.36% above the best at N=37,61,91' claim is not backed by any file or
   script (grep 'perfect' finds nothing in outputs; screened runs carry no coordinates). I could not reproduce those numbers: the
   lowest aligned-stage polished states in dip hex are 0.037%, 0.032%, 0.016% above best, and none of the six lowest polished
   states at N=37,61,91 is defect-free. Treat as unverified; either supply the script/output or drop it.
3. Amendments A4/A5 are stamped 10:48/10:54 but were committed at 11:05, after the aligned stage for N<=37 had already run
   (runs_aligned files 10:54:09). Statement 'before any aligned start was run' cannot be confirmed from git. A5 was also motivated
   by looking at success rates (disclosed). Register as a weakness, not fraud.
4. 'perimeter law holds roughly' rests on 2-parameter fits to 4 (dip) or 3 (g3, one dof) points with a large positive c (+15 dip)
   and E_edge/sqrt(N) not constant; gamma_P spread of 5-12% is a description, not a test of a boundary law.
MINOR
5. 'upper bounds on the ground state' is imprecise: E_p is the penalised energy (<= hard-wall energy of the same configuration);
   numerically immaterial (E_wall ~1e-6), but the wording should say 'penalised energy'.
6. E-c has no teeth (disclosed); E-c numbers should not be cited as validation. E-b/E-a are the real gates.
7. Delaunay defect counts flagged irreg (0.3-1.0 in several cases, e.g. dip rect21 N=37 0.77, g3 square N=19 1.00) are unreliable.
8. Untracked logs and Cargo.lock not committed; larger N under-searched (success 0.00-0.05); g3/g10 N=91 NOT RUN.
