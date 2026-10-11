# Hostile referee report: paper/exciton_fluid_gated_II.tex (companion paper II)
Line numbers refer to the .tex file. All numbers below were re-read from the committed files named; nothing edited.

## Overall
The numbers are almost all right (I re-derived ~60 of them from cases.md, summary.json, analysis.json, calibration.json,
ETD_RESULTS, hf REPORT, VERIFICATION_GatedKernel.md). The problems are (a) one wrong-direction statement, (b) one leaked
Krylov result, (c) uncommitted files the paper points to, (d) several claims worded stronger than the table behind them.
Recommendation: do not deposit until the BLOCKING items are fixed; the MAJOR items are cheap wording fixes.

## BLOCKING
B1. Krylov result is reported although the paper says none is (L271 vs L46-47, L278-282).
  L271: "(v) It was not faster than the Krylov solver's committed result on 16x16 (62 s against 125 s ...)". 62 s is
  ke.jsonl Ke_G16_V0.5_s1 cpu_s=62.48 (committed in 88839ce). L279-280 says "no Krylov result is claimed". The Krylov package
  has no verifier verdict, its heavy runs were "in progress" per commit message, and ke.jsonl in the working tree has since
  changed (+5 lines, uncommitted). Either delete item (v) (and "62 s against 125 s") or move it out of the "ETD worse than
  alternatives" list; the sentence at L280-281 "uses only its committed file as read-only context" is not true of (v), which
  is a headline comparison. Also L278/L281 "Both will be reported, with their failures" presupposes failures of unfinished,
  unverified work; say "with whatever they show".
B2. Files the paper cites as the source of every number are not all committed (L61-63, L310-315).
  untracked: exploration/exciton/python/companion_figures.py (cited L62 and L315; generates all 3 figures);
  exploration/exciton/results/wigner/analysis_summary.txt; edge driver logs and Cargo.lock. The paper itself says the Rust
  source of ETD/edge was committed with the results; make sure the figure script and tag are in the commit that is
  deposited. Also paper/figs_companion/ and the tex are untracked.
B3. The committed Lean report contradicts the paper (L89, L57).
  exploration/exciton/lean/VERIFICATION_GatedKernel.md line 5-6: "No independent verifier has read this file yet ...
  an adversarial reviewer instance should read it before any deposit". The paper says the verifier accepted. The deposit
  will ship a report that says the opposite. Update the .md (verdict, date, verifier's 56 s compile, N=4000 recomputation)
  or the paper must not point to it as the verification record.

## MAJOR
M1. Edge: E_edge/P direction is wrong (L184-185). Paper: "E_edge and E_edge/P (perimeter) decrease monotonically with
  aspect ratio". summary.json aspect[].E_edge_over_P, dip N=37: -0.9247, -0.9153, -0.8946, -0.8501 for square, 3:2, 2:1, 3:1,
  i.e. E_edge/P INCREASES (|.| shrinks) while E_edge decreases. Same at N=19,61,91 and g3. The analysis flag is
  "monotone" in either direction. Say "E_edge decreases, E_edge/P increases monotonically". (Abstract L41-42 is fine: it
  speaks only of E_edge, with the g3 N=19 exception, which I confirm: -5.3286, -5.5151, -5.4882, -5.7884.)
M2. Edge: numbers of starts misreported (L169-172). Paper gives 16+6 at N=61 and 8+4 at N=91 as what was run. PREREG
  amendment A6/A6b (11:05, 11:42; A6b committed 12:04 with the results) added 44 (N=61) and 32 (N=91) extra random starts for
  the UNGATED kernel only (g3, g10 not extended) after seeing timing. So dip has 60+6 / 40+4 starts, g3/g10 16+6 only. The
  paper's "Process weaknesses" paragraph (L197-200) lists A4/A5 and omits A6/A6b, and the search-effort asymmetry bears on
  the gated/ungated ratio (L185) and on "monotone for dip at all N" (dip is better searched than g3).
M3. ETD: "ETD costs as much as BDF below ~1e-9" and the Fig. caption "about equal at ~2e-10" are not what the data show
  (L257-258, L268). ETD_RESULTS Sec. 6: ETD E=2.0e-10 costs 1.8 s; CVODE rtol 1e-10 costs 1.8-2.5 s but only reaches
  E=4.3e-9, 20x worse. At equal error ETD is cheaper everywhere in the table (E~2e-9: 0.76 s vs 1.8-2.5 s); the plotted
  curves (fig_etd_wp.png) do not cross. The honest statement is "CVODE was not run below 4e-9; ETD's step count relative to
  BDF grows (2.6x at 3e-9), so the advantage shrinks, extrapolated crossing not measured". Same fix for the source note.
M4. ETD: stiff-order-reduction attribution is stated as fact in places where the text elsewhere (L264-265) says it is
  weaker (abstract L44-45 "(stiff-order reduction)", table L244 "stiff-order reduction"). Also "order 2 -> 4" (L261-262) is
  wrong at the registered stiffness: ratios 2.2, 2.9 are order 1.1-1.5, ratio 7.2 order 2.85; at gamma_R=20, 7.6 -> 14.6 is
  order 2.9 -> 3.9. And the gamma_R=2 values 19.9, 17.3 are both flagged by the note itself as "at the reference floor"
  (the verifier's own were 19.97, 16.7, 15.9). Krogstad (stiff order 3) ratios 6.1, 4.2, 3.9, 6.0 are not 8 either: the
  mechanism is "consistent", not demonstrated; keep "consistent with" in the abstract and table.
M5. Cover panel (d) plots a "Krogstad variant" series that the text never mentions (fig_cover, L20; script L87-96).
  It is 5-15x more accurate than the headline scheme at the same h and also not order 4 (ETD_RESULTS Sec. 2, "exploratory").
  A reader sees a better integrator that the text omits. Describe it in one sentence (exploratory, not registered as a gate)
  or drop the series. The cover has no caption at all; panels (a) and (d) are never described; panel (d) is "t=10, G8" only
  in the axis label.
M6. HF gate: the factor 3.4 spread of "binding energies" mixes unlike quantities (L226-228). 0.161 eV is WSe2 1s in hBN/hBN
  (Stier), 0.55 eV is MoSe2 on bilayer graphene (Ugeda), and the interlayer exciton the model needs is 0.25-0.32 eV
  (Gillen, Torun; REPORT.md table). Spread of the relevant interlayer values is ~1.3, not 3.4. The conclusion (a ground-state
  model cannot supply E_b) survives; the quantity "which an input would have to resolve" does not. Also "metal-metal
  distances 6.42-6.51 A" is the worker's reading of figures (REPORT.md Step 3: "my reading of the figures"); L226 states it
  as fact. And G4 "published values" are uncited in the paper (they are Kormanyos et al. 2015, arXiv:1410.6666; G4 agrees
  with that PBE value by construction, so it is a code sanity check, not independent support).
M7. Abstract L34-35: "each pre-registered before its first run". Lean has no pre-registration (no document in repo; commit
  21de1a8 is the first artefact). HF: the one dataset file was opened before PREREG.md (REPORT.md, "Disclosure"); Wigner
  amendment A2 was written after the scan (verifier note) and its code was committed after the runs. State "pre-registered
  except Lean; deviations listed" and carry the HF/Wigner disclosures into their sections (currently only edge and ETD have
  process-weakness text).
M8. "Gates can only raise the threshold" (abstract L39-40; "Gates can only hurt", L134) is a statement on 8 sampled D/d values
  in a rigid-exciton harmonic model, measured as Lambda_min and lower window edge (analysis.json: 48.74 at D/d=20 vs 48.69
  ungated; 49.4 at 5; 64.8 at 2). Not a theorem and not general. Also 294 at "ungated" in L134 is the control value
  reproduced BY CONSTRUCTION (REPORT.md: "reproducing the 1/r^3 value by construction"); the paper does not say so.

## MINOR
m1. L184-185 / L185 "gated edge energy per sqrt N smaller by a factor of about 3.5-4": from cases.md I get 3.44-3.98 over
  disk/hex/rect/square/tri at N=19,37,61 (ratio grows with N: ~3.5, 3.65, 3.8). OK as written but say 3.4-4.0 and "hard
  walls, excluding the trap". g10 is only on disk, rect21, trap (3 shapes), which L157 does not say.
m2. E-e (L166-167): registered criterion is max|F|<1e-9 AND lambda_min>=-1e-6 (PREREG L184). Paper quotes only lambda_min;
  e.g. dip trap N=19 has lambda=-7.6e-17 and is among the 7 "no" via force.
m3. "perimeter coefficient" (L187-188) is never defined (gamma_P = gamma/(P/sqrt N) with shape factors, PREREG L62). Numbers
  12% and 4.5% reproduce (gamma_P max/min = 1.117 dip over 7 shapes; 1.045 g3); g10 (3.2%) omitted. A 12% spread across
  shapes is arguably evidence FOR approximate perimeter scaling; the paper calls it "no clean boundary law". The text is
  self-consistent (c is large, E/sqrtN drifts) but should say that the fit has 2 parameters on 3-4 points.
m4. Abstract L40: "both registered predictions on the control failed or were refuted" drops the failbox caveat (L142-144)
  that the P1 refutation hinges on the unchecked DMC displacement definition. Put "(depends on an estimator definition)".
m5. T-d(iii) "reviewer's digits" (L248, L272): which reviewer? The external review (source "not stated", per
  PEER_REVIEW_RESPONSE.md) supplied an independent solution; provenance is weak and "reviewer" collides with "verifier".
m6. Abstract L44: "29 times faster than dense BDF": one seed, 8x8, V0=0.5, machine load 4-11, CVODE rtol 1e-10 dense; say so.
m7. L284-300 "a Fourier-diagonal block preconditioner was chosen": that is a design from the response doc for an unfinished,
  unverified package; mild leak, rephrase as "proposed".
m8. L232-237 "CVODE comparisons use the pinned rusty-SUNDIALS tree": no citation (Hindmarsh 2005 is in paper I's list);
  Mathlib and Lean are uncited; Valenti entry lacks initials/title; Boening has no journal/title (arXiv only; fine); Cohn-Kumar
  title missing. Entries I could confirm from memory or verifier notes: Astrakharchik PRL 98 060405; Buechler PRL 98 060404;
  Gillen-Maultzsch PRB 97 165306; Torun PRB 97 245427; Stier PRL 120 057405; Ugeda Nat. Mater. 13 1091; Cox-Matthews JCP
  176 430; Hochbruck-Ostermann SIAM JNA 43 1069; Cohn-Kumar JAMS 20 99. arXiv:2501.16430 and arXiv:1101.1757 match the
  GATE.md source list. I could NOT confirm the OpenAI "family 090" locator beyond paper I's own bib.
m9. Authorship: one named human author while L47 says "Written by an AI system". Same as paper I; fine, but the verifier/
  worker roles (L55-58, "worker's first message" L192) are unexplained to an outside reader.

## Checked and correct (brief)
- Lean: 1083 lines, 52 theorems, 17 #print axioms (counted), no sorry/native_decide (grep), T1-T3 table matches the .md
  section 3, AdmissiblePotential claim, "0 is admissible"/uniqueness/Cohn-Kumar non-claims match section 5. The paper
  states correctly that the lattice-optimality theorem is NOT proved. The kernel theorem holds for all real z_e, z_h.
- Wigner: P0 4.4464 / 8e-5, 2.4e-8, gamma_h(290)=0.263, n_c^h=847 (690-1047), ratio 2.92, c=0.5342 (0.534241), 435/2600/2.6e4,
  Lambda_min 48.7, 52 (51.9), 65 (64.8), 104, 246, 1.4% at D/d=5 (<2% for >=5), Lambda=300 edges 294/419/944/2.7e3/6.7e3/1.6e4,
  mapping 4.2 (factor 11.6~12), 1.1-19, d~12 nm. P1/P2/P4 wording matches REPORT.md. Valenti 35 vs 29 / 20% matches GATE.md.
- Edge: 65 cases (32 dip + 24 g3 + 9 g10), 76 registered, 58/65 stationary, 0/55 halved detected, c +14.6..+18.7 (dip),
  gamma_P spreads, aspect monotonicity in E_edge (dip all N; g3 N=37,61; g3 N=19 exception), gates E-a/E-a2/E-b and bugs 1-4
  fail E-b (eb_bug*.json), hexagon claim correctly withdrawn.
- HF: G1-G5 table matches REPORT.md and verifier; U~(0)=4 pi d(1-d/D) I re-derived from the image/K0 series.
- ETD: T-a..T-f rows, 37x (0.64/0.01707), 0.0034 (5x below), 2-3.6x, shifts/n_c, 7.7 s vs 227 s (29x), residual floor 7e-9
  at h=0.05, h^3 scaling, ratios 2.2/2.9/4.5/7.2 (verifier reproduces 2.25/2.90/4.49/7.21), the not-done list (i)-(v).
- Krylov/Fenris: no Krylov/Fenris numbers other than item (v) above; Fenris is described by status only. Verifier verdict
  line (L57) matches the five verify_*.md files exactly (Lean accept; others accept with fixes); Krylov and Fenris are
  correctly not credited with verifier verdicts.
- Figures vs data: cover (c) values match cases.md (g3 square -1.2225/-1.4191/-1.5392; rect31 -1.328/-1.553/-1.698; dip
  square -4.39/-5.23/-5.86/-6.34, etc.; script computes e_total - n*e_lat); (b) = analysis.json Lambda_min_over_nu with
  "inf" plotted at 40 (stated in axis label); (d) = ETD_RESULTS Sec. 2 G8 rows (typed, as the paper says); work-precision
  rows match Sec. 6 (CVODE times are range midpoints, disclosed). fig_edge_aspect matches summary.json aspect[].
  Only problems are M3, M5 above.
