# Option C — ν-floor cross-check (pre-registered 2026-08-14, before running)

**Status: conducted per owner instruction (2026-08-14) as an INDEPENDENT CROSS-CHECK of
the round-3 transient measurement — not as the primary experiment.** The review
deprecated C as a primary (it changes E1 §4's question and adds a free parameter), but as
a second, methodologically different route to "does the dispersive mechanism differ from
bare dissipation?", agreement between C and round 3 is stronger evidence than either
alone; disagreement is itself informative.

## Protocol (fixed before any run)

- **Idea:** a small viscous floor gives every arm an attractor, so the ORIGINAL
  observable `sup_t Ω` becomes well-posed (it converged within T ≈ 2–4 for every viscous
  case previously measured).
- **Arms:** sweep D ∈ {0.2, 0.15, 0.1, 0.07, 0.05, 0.035, 0.025, 0.018} at fixed floor
  ν; comparator is the pure-viscous sweep (same values as ν, D = 0).
- **The floor is a free parameter and gets its own stability check:**
  ν_floor ∈ {0.01, 0.02} (2× range). β_D must agree across floors within |Δβ| ≤ 0.05
  (B3′ metric); if it does not, the floor-dependence IS the reported result.
- **B1 spot-check:** at each floor, two configurations re-run at 2T must change sup_t Ω
  by < 1%.
- **Grid:** N = 5. **Initial data:** same complexified P3 as round 3.
- **Observable:** sup_t Ω, both conventions (B7); fits with windowed-slope stability
  (no t-CIs — deterministic sweeps).
- **Interpretation, fixed in advance:** measures dispersion-ON-TOP-OF-dissipation, a
  DIFFERENT question from E1 §4's. Consistency statement to make afterwards: does the
  sign/ordering of the C effect agree with round 3's transient-delay measurement?

---

## RESULT (2026-08-15) — the pre-registered floor-stability criterion FAILS, which is the result

Full output: `exploration/run_nu_floor.out`.

- **B1 passed perfectly** (0.000% change at 2T, both floors, both spot points): the floor
  does create an attractor and `sup_t Ω` is genuinely well-posed here. The mechanism
  diagnosis behind M2 §6a is thereby confirmed from the other side.
- **Floor stability FAILED decisively**: β_D = −0.380 → −0.192 [sum] as ν goes
  0.01 → 0.02 (|Δβ| = 0.19 ≫ 0.05); [max] worse (−0.305 → −0.012, r² collapsing to 0.008).
  The within-fit windows disagree as well ([sum] at ν=0.01: −0.53 large-D half vs −0.16
  small-D half) — not a clean power law even at fixed floor.
- Pure viscous comparator: β_ν = −0.869 [sum], r² = 0.993 — the instrument is fine; the
  ν-floor *question* is the problem.

**Verdict, per the pre-registered interpretation:** dispersion-on-top-of-dissipation has
**no floor-independent exponent** — the dispersive effect on peak enstrophy halves when
the floor doubles. The old §7 recommendation (ν-floor as the W4 reformulation) would
never have produced a clean number; this is now measured rather than suspected, which is
what conducting C alongside A bought.

**What C *does* contribute to triangulation:** the **sign** is consistent and real at both
floors — larger D ⇒ smaller peak enstrophy, i.e. dispersion suppresses/delays the
cascade's build-up, agreeing in direction with the round-3 hypothesis ([LIT-016]'s
dispersive bottleneck). C corroborates the direction of the effect while demonstrating
that this formulation cannot quantify it cleanly.
