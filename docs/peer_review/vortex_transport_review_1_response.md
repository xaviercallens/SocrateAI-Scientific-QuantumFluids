# Response to peer review 1 (`vortex_transport_review_1.md`) — revision log

Started 2026-10-07 after recording the review verbatim. Every item is answered below with what changed in
`paper/vortex_transport.tex` (version 2). The review's recommendation was "major revisions".

| item | review | change |
|---|---|---|
| A | no figures | five figures added, all from data on disk (`paper/make_figures_vortex_transport.py`): Fig. 1 α and raw/corrected α′ against ρ_n/ρ; Fig. 2 residual MSD against lag, log–log, with the exponents; Fig. 3 stalled single pairs against zero-impulse pairs and the phonon-band momentum against the impulse shed; Fig. 4 the k-independent charge structure factor against the matched-pair polarisability; Fig. 5 the six L = 192 trajectories at the two windows (equilibration) |
| B | the L = 96 control must be run | **running**: L = 96 base state at the same temperature (quench to t = 4500, N = 192) followed by two single-pair runs of 4000 time units; the section is written with a red `[pending]` marker that will be replaced by the outcome, whatever it is, before publication of version 2. If the control cannot be completed the section will be truncated to a stated speculation, as the review asks |
| C | audit-log jargon; restructure | main text rewritten as a physics narrative (Introduction; Model, instrument and estimators; Friction/transverse/diffusion; Single pair in a closed box; Box-scale pair, equilibration, polarisability; Conclusions). Gate names, amendment labels and ledger numbers removed from the body; the full protocol, gate table and decision rules moved to Appendix A |
| D | justify the T = 0 baseline subtraction physically | a dedicated passage in Section 3: (i) the v_s of the motion equation is the actual local superfluid velocity, which on a torus includes the uniform flow set by the configuration's net impulse — the periodic Green function fixes that component by gauge, not by physics — and the normal fluid is at rest in the box frame, so the transverse force is the difference between the vortex velocity and v_s^WM + u; (ii) a finite pair is a Jones–Roberts solitary wave whose speed departs from 1/d at order (ξ/d)², a T = 0 property measured and tabulated (new Table 2) and subtracted. Both corrections are measured, not assumed; the box-frame values are kept in Table 1 so the reader sees the size of each |
| minor 1 | explicit imprint equations | Appendix B: the theta-function phase, its boundary jump, the compensating gradient, the Bernoulli amplitude, and the static checks |
| minor 2 | interpret the anomalous diffusion | Section 3, diffusion paragraph: T = 0 bounded residual (sound in the box); short-lag plateau from thermal jitter of the detected core with phonon correlation time; lags ≥ 100 Brownian at the two cooler temperatures; thermal-vortex drift at the warmest; a quasi-periodic orbit excluded by the growth of the MSD (theorem) and by the 1/f^0.5 spectrum; stated as the reason the rule quotes η only in the diffusive window |
| minor 3 | explain what Lean verified | two sentences in Section 2 and Appendix C: the kernel checks that the estimators and reduced equations follow from the model's equations with no hidden assumption; it does not check that the model describes the field |
| minor 4 | "R_yortex" typo; raw tables | the pipe tables were already LaTeX `tabular` in the committed file; all tables re-typeset with `booktabs`; no occurrence of the typo remains |
| minor 5 | undersold abstract | the sentence "No physics is claimed as new" is removed; the abstract states the results (α ∝ ρ_n with coefficient 0.24; α′ = 0 within 1 %, Iordanskii excluded at 18σ; diffusion 1.4–3× Einstein; the box-scale pair; the polarisability from pair sizes) and keeps the two negative results and the pending control explicit |

Not changed, with reason: the Einstein verdict stays "undecided by rule" — the review's own point (η is ill-posed where the
fluctuations are sub-diffusive) is the reason the rule was written, and relaxing it after the fact would be the kind of
move the protocol exists to prevent. The informal 1.4–3× statement is kept, labelled informal.

Status: version 2 published (10.5281/zenodo.23225101, record 23225101); the L = 96 control (item B) is reported, verdict REFUTED by the registered rule.
