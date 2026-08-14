# W2 — the bounce regulator as the conserving seam family (DESIGN MEMO)

**Status: Tier C authoring, AWAITING HUMAN AUDIT. Nothing here may enter production code
until this memo is marked AUDITED in LEDGER.md.** An exploratory Tier C preview under
`exploration/` (clearly bannered) is permitted, consistent with house style.

## 1. What CLAIM-010 established

The Lean telescoping theorem gives the energy pairing as `−k_N·Re(conj(v_N)²·v_{N+1})`,
so a boundary seam conserves energy **iff** `v_{N+1}` is orthogonal to `v_N²` under
`Re(conj(x)y)`. On real data only truncation qualifies. In the complexified model there
is a one-parameter conserving family:

```
        v_{N+1} = i·μ·v_N²          (μ real)
```

## 2. What the seam actually is, dynamically

Substituting into shell N's outgoing term:

```
  −k_N conj(v_N)·v_{N+1} = −i·μ·k_N·|v_N|²·v_N
```

— a **cubic self-phase-modulation term at the cutoff shell**: an NLS/GPE-type
nonlinearity, amplitude-preserving, rotating the top shell's phase at rate `μk_N|v_N|²`.
Two remarks worth the auditor's attention:

- **Thematic resonance, to be treated with suspicion rather than celebration:** the only
  energy-conserving "bounce" available is GPE-like. This is elegant, and elegance is not
  evidence; the memo claims only the algebra.
- **Mechanism kinship with the dispersive regulator:** both act by phase rotation; the
  dispersive term at fixed rate `Dk²`, the seam at state-dependent rate `μk_N|v_N|²`,
  localized at the cutoff. The three-arm comparison is therefore: no rotation
  (truncation) / linear-in-k² rotation everywhere (W4) / cubic rotation at the seam (W2).

## 3. Properties already established

- **Energy conservation:** exact, by CLAIM-010's orthogonality (`i·μ·|v_N|⁴` is purely
  imaginary). Pinned numerically in `tests/test_shell_dynamics.py` (seam section).
- **Liouville:** the seam term's diagonal derivative splits into multiplication by
  `−2iμk_N|v_N|²` (purely imaginary ⇒ zero trace) plus a conj-linear part
  (zero trace by the same lemma as the nonlinearity) — the seam preserves phase-space
  volume. Derived by hand; to be verified numerically in the Tier C preview before any
  production use.
- **Consequence:** a conserving W2 inherits the M2 §6a obstruction for amplitude
  observables, exactly like the other two arms — its readout must be the round-3
  transient observable (τ_f), for which it is well-defined.

## 4. Proposed protocol (inherits round 3 wholesale)

Sweep μ over a pre-registered grid at ν = D = 0, same initial data, same τ_f observable,
same battery checks (B3′ on f, B4, B5′ ratio form). The α′-correspondence for μ is
UNRESOLVED (μ has dimensions 1/[v]² ~ 1/E — not a length²); as with O6, β_μ is reported
against μ itself, within-family only.

## 5. Kill criteria

- If the Tier C preview shows the seam's numerical divergence is NOT ~0, §3's hand
  derivation is wrong — kill and re-derive.
- If τ_f(μ) is non-monotonic or fails B3′/B4/B5′, the arm is excluded from comparison
  with its reasons reported.

## 6. What this memo does not do

No production code. No claim that this family is "the" bounce of E1's design — E1 never
specified one; this is *the conserving family that exists*, offered to the auditor as the
candidate.
