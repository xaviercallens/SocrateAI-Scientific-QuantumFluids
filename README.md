# SocrateAI-Scientific-QuantumFluids

**Quantum Fluids as the Realized Instance of Dual-Scale Regularization**

[![Status](https://img.shields.io/badge/M0--M2-complete-brightgreen)]() [![Tests](https://img.shields.io/badge/tests-130%20passing-brightgreen)]() [![Lean](https://img.shields.io/badge/Lean-kernel--checked-blue)]() [![Mathesis Dependent](https://img.shields.io/badge/Depends%20on-Mathesis%20Stream%200-blue)]()

---

## Overview

This stream expresses established quantum-fluid physics in the dual-scale regularization
language (Tier A/B, citation-verified) and was to run the W4 pre-registered experiment
(three regulators, one instrument).

**M1 succeeded**: the Landau dispersion fit reproduces Godfrin et al. (2021)'s own
published data to 0.2–0.33%, well inside the ±5% / ±10% targets.

**M2 returned a negative finding:** all three of E1 §4's regulators are *energy-conserving*,
so none has an attractor, so `sup_t Ω` degenerates to the truncation ceiling — the W4
measurement is not well-posed as designed.

**M3 relaunched the measurement four times and closed without a quantitative result.** The
final round established why: the observables are single trajectories of a **chaotic** system
with 72–105% fixed-parameter scatter, and the effect sought is below that resolution. Several
earlier results were retracted as a consequence, each with its reason recorded.

**What stands** is the structural work: a model validated bit-for-bit against
MechanicaFluidorum, eight kernel-checked Lean theorems (energy conservation, the invariant
real subspace, and the **Liouville property** — the complexified flow preserves phase-space
volume where the real Katz–Pavlović model does not), the conserving-seam condition, and the
identification of the whole phenomenon as absolute-equilibrium thermalization against ten
verified citations — with novelty explicitly withdrawn, since prior art exists for shell
models.

**Key documents:**
- **[SPEC.md](SPEC.md)** — Specification and contract (pinned from Mathesis Stream 0)
- **[PLAN.md](PLAN.md)** — Milestones M0–M4 with tasks and definitions of done
- **[LEDGER.md](LEDGER.md)** — Claim inventory (Tier A/B/C tracking)
- **[LL.md](LL.md)** — Lessons learned (inheritance + new insights)

---

## Quick start

```bash
# Run everything: 130 tests + Lean kernel check with axiom audit
bash scripts/verify.sh

# Tests only (no Lean toolchain needed)
python3 -m pytest tests/ -q

# Optional: h5py for the NeXus adapter's tests (otherwise 1 test skips).
# This system's python3-venv is absent and `sudo` is unavailable in-session,
# but `uv` sidesteps both -- it builds a venv without ensurepip:
uv venv .venv && uv pip install --python .venv/bin/python numpy scipy matplotlib h5py pytest
.venv/bin/python -m pytest tests/ -q

# Reproduce the M1 dispersion fit against Godfrin et al.'s published data
PYTHONPATH=src python3 -c "
from quantumfluids.adapters.godfrin_ancillary import load_godfrin_p0_dispersion
from quantumfluids.dispersion_fit.fit_dispersion import run_dispersion_fit, compare_to_literature
d = load_godfrin_p0_dispersion('data/external/godfrin_2021_arxiv_ancillary/DispersionP0allRange.txt')
r = run_dispersion_fit(d, phonon_q_max=0.05, roton_q_center=1.9, roton_half_width=0.2)
print(compare_to_literature(r, 'godfrin_2021'))"

# Lean (first time: downloads ~7GB of prebuilt Mathlib)
cd lean_src && lake update && lake exe cache get && lake build QuantumFluidsShell
```

**Reading order for someone picking this up:** `M2_REPORT.md` (the headline finding and
how it was reached) → `LL.md` (the transferable lessons, several of them corrections to
my own earlier work) → `LEDGER.md` (every claim, including the retracted ones).

---

## Repository structure

```
.
├── SPEC.md                          # Contract (pinned from Mathesis)
├── PLAN.md                          # Milestones & task list
├── LEDGER.md                        # Claim inventory (Tier A/B/C)
├── LL.md                            # Lessons learned
├── docs/
│   ├── EXPRESSION_MEMO_E1.md        # Dictionary (dual-scale language)
│   ├── ROSETTA_ROW.md               # Term sync with Mathesis
│   ├── LITERATURE_LEDGER.md         # Citation registry (retrieval-verified)
│   ├── GODFRIN_CORRESPONDENCE.md    # Outreach log
│   └── narrative/                   # Dark-matter speculation (Tier C, quarantined)
├── M1_REPORT.md                     # M1 result (dispersion fit)
├── M2_REPORT.md                     # M2 result -- the negative finding
├── docs/designs/                    # Design memos (audit-gated, per E-1)
├── exploration/                     # Tier C scripts + archived run outputs
├── lean_src/                        # Lean: complexification's conservation (Tier A)
├── src/quantumfluids/
│   ├── adapters/                    # Data readers (numor, .nxs, ASCII S(Q,ω))
│   ├── w4_shell_model/              # Dispersive shell model (quantum pressure)
│   └── dispersion_fit/              # Phonon-roton fit tools (Landau 2-param)
├── data/
│   ├── external/                    # Cached open datasets (FAIR licensed)
│   │   └── *.meta                   # Provenance (DOI, retrieval date, checksum)
│   └── derived/                     # Reductions from this stream
├── tests/                           # Tier-B harnesses (negative controls mandatory)
└── scripts/verify.sh                # Gate 1 (pytest) + Gate 2 (Lean build + axiom audit)
```

---

## Key constraints

- **No well-posedness claims about Navier–Stokes** (quarantined under MF obstruction O5)
- **ξ→0 limit not claimed solved** (mathematical difficulty recognized)
- **Dark matter only in named experimental programs** (speculation confined to docs/narrative/)
- **All Tier-A claims citation-verified** (LITERATURE_LEDGER.md is authoritative)

---

## Milestones

| Milestone | Status | Outcome |
|-----------|--------|---------|
| **M0** | ✅ complete | All 10 literature entries retrieved and verified; repo, Lean and Mathesis integration bootstrapped |
| **M1** | ✅ complete | Landau fit reproduced on Godfrin et al.'s own published data: **c within 0.20%, Δ within 0.03–0.33%** of six independent determinations (targets were ±5% / ±10%). See `M1_REPORT.md` |
| **M2** | ✅ complete | **Negative finding**: an energy-conserving regulator admits no well-posed peak-enstrophy observable, and all three of E1 §4's regulators are conservative. Model validated bit-for-bit against MechanicaFluidorum; Tier A Lean formalisation landed. See `M2_REPORT.md` |
| **M3** | ✅ closed, no quantitative result | Four measurement rounds, all failed. The fourth invalidated the first three: **single trajectories of a chaotic system**, effect smaller than the 72–105% fixed-parameter scatter. Durable output is methodological (CLAIM-014). See `M3_REPORT.md` |
| **M4** | ⏸ open | Godfrin outreach drafted (`docs/GODFRIN_CORRESPONDENCE.md`), not yet sent |

**Verification:** `bash scripts/verify.sh` — Gate 1 (143 pytest tests, 0 skipped) and Gate 2
(Lean build + axiom audit; requires `lake`, see `lean_src/`).

---

## Getting help

- **What was actually found?** [M2_REPORT.md](M2_REPORT.md) — the finding, the seven
  observables tried, and §6a on why it covers the whole experiment
- **Questions about this stream?** Check [PLAN.md](PLAN.md) §"Decision points requiring owner approval"
- **Literature retrieval stuck?** See [LITERATURE_LEDGER.md](docs/LITERATURE_LEDGER.md#retrieval-summary-m0-progress)
- **Outreach strategy?** Read [GODFRIN_CORRESPONDENCE.md](docs/GODFRIN_CORRESPONDENCE.md)

---

## References

**Key literature:**

- Godfrin & Krotscheck (2022). "The Dynamics of Quantum Fluids." arXiv:2206.06039 [LIT-001]
- Godfrin et al. (2021). "Dispersion relation of Landau elementary excitations in superfluid helium by inelastic neutron scattering." Phys. Rev. B 103, 104516. [LIT-002]
- Hirschel et al. (2024). "Superfluid helium ultralight dark matter detector." Phys. Rev. D 109, 095011. [LIT-003]

See [LITERATURE_LEDGER.md](docs/LITERATURE_LEDGER.md) for the full registry.

---

**Stream coordinator:** (TBD)  
**Last updated:** 2026-08-14  
**License:** See SocrateAI-Scientific-Mathesis for license terms.
