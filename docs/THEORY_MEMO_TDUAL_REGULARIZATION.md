# Theory memo — T-dual regularization: what this stream established, constrained, and refuted

**Stream:** SocrateAI-Scientific-QuantumFluids · **Date:** 2026-08-15
**Purpose:** the retrofit input for Mathesis. Every statement is tagged with its
evidentiary status so the retrofit can place it at the right tier without re-deriving.
**Retrofit target:** `/home/xavkal/socrates-project/home` — **not present on this machine
as of writing**; path recorded, integration deferred until it exists.

Status tags: **[A]** kernel-checked · **[B]** deterministic, tested · **[C-num]** numerically
verified this stream, not formalised · **[open]** conjecture · **[refuted]** ruled out.

---

## 0. The claim in one paragraph

The four atomic principles (P1 self-dual bound, P2 Sym² lock, P3 discrete-pins-continuous,
P4 bounce) were expressed in a concrete cascade. **P1 stands and was already a theorem.**
**P4 is constrained, sharply**: in an energy-conserving cascade the "bounce" cannot be a
spatial reflection about the self-dual scale — every such seam leaks — and must instead be
local *phase rotation* at the cutoff, i.e. dispersive, GPE-like. **The dispersive/dissipative
distinction is a single complex phase.** Conservation then forces Liouville structure, which
forces thermalization, which is why amplitude observables cannot see the regulator's
mechanism. **P2 and P3 were not tested here.** No measurement-based claim survived; the
theory content is entirely structural.

---

## 1. What P4 can be — the seam theorem

**Setting.** Truncated dyadic model, complexified: $B_n = k_{n-1}v_{n-1}^2 - k_n\overline{v_n}v_{n+1}$.

**Theorem (seam characterisation) [A]** — `seam_conserves_iff`. A boundary value $w$ at
shell $N{+}1$ conserves the energy pairing **iff** $\mathrm{Re}(\overline{v_N}^2 w) = 0$,
i.e. iff $w \perp v_N^2$ under $\mathrm{Re}(\bar{x}y)$.

**Corollary [C-num, provable from the theorem].** Any seam that reads a *neighbouring*
shell — the geometric T-dual mirror $v_{N+1}=\pm v_{N-1}$, its conjugate, its $i$-rotation —
generically leaks (measured $|dE/dt|\sim10^2$–$10^3$). The conserving family is
$w = i\mu v_N^2$ [A, `seam_gpe_conserves`], dynamically a cubic self-phase-modulation
$-i\mu k_N|v_N|^2v_N$ at the cutoff.

**Reading for P4.** "Contraction reflects into dilation" is *not* realized as energy handed
back to mirror shells — that is in the class Prop. 4 (below) forbids. It is realized, if at
all, as phase rotation that keeps $|v_N|$ fixed. **This is the stream's principal
theoretical output.** It should be stated in Mathesis as the constraint on P4, alongside
`Reff_bounce`, which is the *scalar* geometry and remains true.

---

## 2. Dispersion vs dissipation is one complex phase

**Proposition (obstruction) [B, elementary].** In a real-amplitude model, every linear
regulator $-c(k)a_n$ with $c\in\mathbb R$ has $\frac{d}{dt}\tfrac12\sum a_n^2 = -\sum c(k_n)a_n^2$: dissipative if $c\ge0$, forcing if $c\le0$, never neutral. Dispersion is phase
rotation; a real amplitude has no phase.

**Consequence.** With complex amplitudes, $-\nu k^2 v$ (dissipative) and $-iDk^2 v$
(dispersive) are the *same* term with the coefficient rotated $90°$ in $\mathbb C$. The
dichotomy the T-dual programme cares about — absorb vs reflect — is literally
$\arg(\text{coefficient}) \in \{0, \pi/2\}$. Any Mathesis statement of "reflective
regulator" can be made precise as "regulator with purely imaginary coefficient".

**The complexification is not unique [B].** Other conjugation placements also conserve.
This one is selected because the reals are an *exactly* invariant subspace [A,
`shellBc_real`], which (i) makes it an extension of the real model, not a replacement, and
(ii) gave a bit-exact positive control (`0.00e+00`, 9 configs, 2.4M steps) [B].

---

## 3. Conservation ⇒ Liouville ⇒ thermalization

**Theorem (Liouville, shell blocks) [A]** — `shell_divergence_zero`: the diagonal derivative
blocks of the complexified flow have zero real trace. **Full-field divergence** $\approx
4\times10^{-9}$ [C-num]. **Real Katz–Pavlović: $\mathrm{div}=-\sum k_na_{n+1}\neq0$** [C-num,
verified to 4 decimals]. The complexification moves the model from a volume-contracting
class into a Liouville class.

**Consequence chain [B + literature].** Volume-preserving flow on a compact energy sphere ⇒
recurrence, no attractor ⇒ relaxation toward *absolute equilibrium* ⇒ $\sup_t\Omega \to
k_N^2E$ and $\beta\to-1$ against $\alpha'=4^{-N}$ (measured $-1.002$ at $T{=}32$) ⇒ **any
amplitude observable measures the truncation, not the regulator.** This is *known* — Lee
1952, Kraichnan 1973, Cichowlas et al. 2005; for shell models Thalabard–Turkington 2016
et al. — and is recorded as re-expression, novelty withdrawn (LIT-011–020, all verified).

**Reading for the theory.** The obstruction to measuring P4's *effect* is not accidental;
it is the same conservation that makes P4 well-defined. **A theory of T-dual regularization
must predict its signature in the pre-thermalization transient**, and must say so.

**[open]** Is the real model's volume contraction along cascade states mechanistically
tied to self-similar blowup attraction (Katz–Pavlović)? If yes, the complexification's
Liouville property is *why* it cannot blow up in the same way — a structural statement
about regularity, not just conservation. Not claimed; flagged as the most interesting open
item this stream leaves.

---

## 4. Empirical scaling from data we own (Option 2 result)

From Godfrin et al. 2021's all-pressure table (7 pressures, error bars, ~1050 Q points)
[B, deterministic weighted fits, P=0 cross-checks M1 to 0.05%]:

| P (bar) | Δ (meV) | Q_m (Å⁻¹) |
|---|---|---|
| 0 | 0.7438 | 1.9085 |
| 2.01 | 0.7338 | 1.9267 |
| 10.01 | 0.6963 | 1.9909 |
| 24.08 | 0.6185 | 2.1147 |

**Result.** Δ(P) and Q_m(P) are **not power laws** in P (windowed slopes disagree, $r^2\approx0.75$). The low-P regime is **linear**: $\Delta$ falls at $-0.67\%/\text{bar}$, $Q_m$ rises at $+0.475\%/\text{bar}$, constant across three independent points. **Guard for the theory:** any T-dual coupling law $m=|\mathrm{disc}|^{-s}$ (Mathesis CR-1, $s\in\{\tfrac12,1\}$ open) tested against these parameters must be stated in the physical variable (density, not P — not in the file, needs a separately-sourced EOS) and cannot be a pure power law in pressure. This is a *constraint the data imposes on CR-1's form*, not a measurement of $s$.

---

## 5. Refuted / withdrawn — so the theory doesn't rebuild on them

- **[refuted]** Any β distinguishing dispersive from dissipative regulators via
  $\sup_t\Omega$, first-peak, windowed-sup, or thermalization time. Four rounds; all failed
  their pre-registered criteria; root cause single-trajectory chaos (CV 23–49%; time
  averaging CV 25–84%). *Not* a statement that no effect exists — that it is below the
  resolution of anything spent.
- **[refuted]** "The regulator's signature is in the transient" *as measured*. Correct in
  principle by §3; unmeasured in practice.
- **[refuted]** Novelty of the thermalization observation.
- **[refuted]** That the geometric mirror is a viable conserving bounce (§1).

---

## 6. What Mathesis should absorb (retrofit list)

1. **P4 constraint theorem** — the seam characterisation [A]. New Tier A row.
2. **Dispersive = imaginary coefficient** — a *definition* Mathesis currently lacks.
3. **Liouville dichotomy** [A blocks + C-num field] as the structural companion of P4;
   the [open] blowup link as an explicit TARGET.
4. **CR-1 constraint** from §4: the coupling law's form must survive linear-in-P data.
5. **Measurement rule** (LL-14 / B8): ensemble scatter before any exponent, in any chaotic
   instance across all streams.
6. **Two withdrawals to record programme-wide**: E1's "W2 already exists in MF" (LL-9) and
   the OP2_LITE β=−2/3 "measured" mis-citation.

**Not** for Mathesis: any of §5.
