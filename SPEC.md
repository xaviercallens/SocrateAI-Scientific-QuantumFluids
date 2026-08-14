# SPECIFICATION: SocrateAI-Scientific-QuantumFluids

**Stream:** QuantumFluids (Stream 1)  
**Depends on:** SocrateAI-Scientific-Mathesis (Stream 0 — verification/formalization/notation, per contract)  
**Date pinned:** 2026-08-14

## Contract Summary

This stream realizes the dual-scale regularization framework in the domain of quantum-fluid physics. All Tier-A claims must be citation-verified against published experimental or theoretical work. All formal theorems must be sourced from or depend on imports from Stream 0 (Mathesis).

### Key constraints

- **No well-posedness claims about Navier–Stokes:** The GPE–NS connection question is quarantined under MechanicaFluidorum obstruction O5. This stream does not attempt to resolve it.
- **ξ→0 limit:** The limit's mathematical difficulty is recognized but not claimed as solved by this stream.
- **Dark-matter speculation:** Any speculation beyond named, live experimental programmes is confined to `docs/narrative/` and clearly marked as non-verifiable.
- **Naming:** Per RES-1 (OP-7 §0), "Poly-Algebraic Calculus" is exclusively reserved for the PIVP/differentially-algebraic solver stream. This stream uses "QuantumFluids" to avoid the two-definitions-under-one-name defect.

## Pinned dependencies

- Mathesis contract (Stream-0 R3.2)
- Mathesis.Duality (Lean import, specific tag TBD)
- Mathesis.Scale.Reff (Lean import, specific tag TBD)

---

*For full Mathesis specification, see SocrateAI-Scientific-Mathesis/SPEC.md*
