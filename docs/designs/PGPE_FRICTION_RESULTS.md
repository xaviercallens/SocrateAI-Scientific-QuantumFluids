# Results: friction known-answer gate (KA) — PASS, narrowly, with a size dependence the design did not expect

Pre-registration `PGPE_FRICTION_PREREG.md` (c9cc4c1, disclosure b17c887). Base `sweep/e0.60_s11_t4000`
(T = 0.115, `T/T_BKT ≈ 0.14`, no thermal vortices), tracker `exploration/pgpe/dipole_decay.py`, coarse-graining
σ = 1.5. Data `data/generated/pgpe/dipole_ka/`. Date 2026-10-05. Energy drift ≤ 2.1×10⁻⁷ on all runs.

| run | d₀ | ended | t_end | α = −slope(d²)/4 | counts for the gate |
|---|---|---|---|---|---|
| d8, placement 1 | 8 | annihilated | 760 | 0.0093 | yes |
| d8, placement 2 | 8 | track lost | 1448 | 0.0062 | yes |
| d12, placement 2 | 12 | t_max (not annihilated) | 4002 | 0.0028 | yes |
| d12, placement 1, tracking radius 8 | 12 | annihilated | 3458 | 0.0022 | yes (the registered rerun) |
| d12, placement 1, tracking radius 3 | 12 | track lost | 92 | (−0.063) | no — excluded in the pre-registration as a tracking failure |

**Gate: median α over the four counting runs = 0.0045, inside the pre-registered window [0.004, 0.045]; four
fits (≥ 3 required). KA PASSES** — at the lower edge: the window was a factor 3 around 0.013 (Shukla, Brachet &
Pandit 2014 interpolated to `T/T̃_BKT = 0.14`), and we sit a factor ≈ 3 below that centre.

**Observed, not predicted.** α is not one number at this temperature: 0.006–0.009 at `d₀ = 8` against
0.002–0.003 at `d₀ = 12`; the lifetime ratio between the two annihilated runs is 4.6 where `d₀²` gives 2.25
(log–log slope ≈ 3.7, outside criterion F1's window [1.5, 2.5]). Two placements per size is not a measurement of
that exponent, but it is the opposite of the mobility *growing* with pair size (`ln d`, Nam et al. 2012;
`d^{2η}`, Groszek & Billam 2026) and is what imprint radiation (a product-ansatz dipole is not a solitary wave:
Rorai, Sreenivasan & Fisher 2013) or a size-dependent effective friction would produce.

**Consequences for the production design (to be fixed in an amendment before any production run).**
1. Use the torus motion law (Zhu 2023), not the plane law: `d₀/L` reaches 0.19 here and 0.25 in the design.
2. Remove imprint transients: fit after a settling time, or prepare the dipole by an imprint followed by a short
   imaginary-time relaxation of the core structure at fixed vortex positions.
3. Make the size dependence a registered question (α(d) at fixed T) instead of an assumption of F1.
4. Save vortex positions (not only the separation), so that the same runs give α′ (pair translation speed) and
   the diffusion needed for the Einstein-relation test — hypotheses H03 and H02 of
   `AUTORESEARCH_SELECTION_2026-10.md`.
