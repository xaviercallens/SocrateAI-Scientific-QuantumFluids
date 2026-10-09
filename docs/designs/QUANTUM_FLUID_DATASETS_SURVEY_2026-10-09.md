# Quantum-fluid datasets and reference solvers on Zenodo and Hugging Face — a survey for the evolution of rusty-SUNDIALS (2026-10-09)

**Purpose.** Find external numerical results that the quantum-fluids module of rusty-SUNDIALS (`qf-pgpe`) can be made to reproduce, rank them by what it would take, and find reference solvers for the GPU/TPU benchmarks planned later.
**Method.** Zenodo REST API (`/api/records`, types `dataset` and `software`, best-match, ≤ 8 hits per query, 21 queries: Gross–Pitaevskii simulation/code, projected GPE, stochastic GPE, quantum vortex dynamics, vortex dipole, quantum turbulence, BKT, mutual friction, c-field, vortex lattice melting, BEC vortex dataset); Hugging Face API (`/api/datasets|models|spaces`, 14 search terms, sorted by downloads).
**Limits.** A screen, not an inventory: best-match ranking, 8 hits per query, repeated 504 gateway timeouts from Zenodo (affected queries were retried), no search of arXiv ancillary files or GitHub. "Reproducible" below means *the record contains what is needed to attempt it*, not that it was attempted, except where stated.

## Hugging Face: essentially nothing

No dataset, model or space for Gross–Pitaevskii/superfluid/vortex simulation was found. The hits are (i) our own `callensxavier/socrateai-quantumfluids-causal-topology` (569 downloads), (ii) generic PDE benchmarks (`DabbyOWL/PDE_Inverse_Problem_Benchmarking`, `kmario23/standard-pde-benchmark`) that are not Gross–Pitaevskii, and (iii) unrelated name collisions ("gpe", "bec"). **Consequence:** Hugging Face is a place to *publish* quantum-fluid reference data (the field has none), not a source of it; a benchmark-data repository there would be the first of its kind for this equation.

## Zenodo: candidates, grouped by what they allow

### A. Reproduction of a published GPE solver run (code + data in the record)

| record | what it is | size | licence | what reproducing it needs from `qf-pgpe` |
|---|---|---|---|---|
| **20068724** Kwon & Shin, *Dynamic similarity of vortex shedding in a superfluid flowing past a penetrable obstacle* (PRR 2026) | complete GPU GPE code (CuPy, pseudo-spectral split-step), JSON input, an example run (ψ snapshots at t = 0…50, force F(t) every 0.1 τ to t = 100, vortex counts), processed data of the paper (Strouhal vs Reynolds, drag) | 18.7 MB | CC-BY-4.0 | rectangular grid (1000 × 500, 500 × 250 ξ), a static Gaussian obstacle, a moving-frame term v∂ₓψ, absorbing layers (position-dependent damping Γ(x,y)) |
| 20728008 *Classical field simulation of vortex lattice melting in a 2D fast-rotating Bose gas* | data of the phase diagram (correlation lengths, defect fractions vs T for Ω = 0.95…1.00 ω_r, 120 samples) | 0.03 MB | CC-BY-4.0 | harmonic trap, rotating frame, thermal sampling (SPGPE), pair-correlation and orientational-order observables |
| 17593677 / 20275167 Suchorowski et al., generalized GPE for 2D bosons with attractive interactions (PRL 2026) | Julia code (ground states, excited states, quench dynamics) + figure data | 0.0 / 228 MB | CC-BY-4.0 | imaginary-time ground states, a beyond-mean-field (LHY-type) nonlinearity, trap |
| 2548958 / 2667866 Gauthier et al., *Giant vortex clusters in a 2D quantum fluid* | simulation data (31 GB) and code of the Onsager-cluster study | 31 GB / 1.8 MB | CC-BY-4.0 | trap, dissipative GPE with noise (already used as external *experimental* data in the programme: `data/external/gauthier2019_zenodo_2548958`) |
| 8385524 Sunami et al., universal scaling of the dynamic BKT transition (already in `data/external`) | experimental and numerical data of the quenched 2D Bose gas | 4 MB | CC-BY-4.0 | a quench protocol on a thermal field (our engine can already prepare thermal states) |
| 5510351 Polanco et al., sample generalized GP data (already in `data/external`) | one 256³ complex field of a 3D GGPE simulation | 268 MB | CC-BY-4.0 | 3D (not in the module); useful as a *measurement* test of the vortex-line detection |
| 12581949 / 7019859 / 21388087 / 19129862 | 2D eGPE rotor code; dipolar-BEC vortex stripes; BEC dark matter vortex nucleation (751 MB); coherently coupled mixtures (GPE + BdG data) | small–751 MB | CC-BY | multi-component, dipolar, gravity — outside the near-term scope |

### B. Fermionic superfluid (time-dependent SLDA) — an HPC reference, not a GPE reproduction

15084263 (mutual friction and vortex Hall angle in a strongly interacting Fermi superfluid, Nat. Commun. 2025; reproducibility packs + figure data), 15639651 (*Quantum vortex dipole as a probe of the normal component distribution*, NJP 2025; 1.9 GB of raw data), 17412051 (impurity-controlled vortex mobility, 0.5 GB), 8355244 (*Fermionic quantum turbulence: pushing the limits of high-performance computing*, PNAS Nexus 2024; **84 GB**, includes `ufg_gpe` GPE runs next to the SLDA ones). All use the **W-SLDA Toolkit** (GPU + MPI). They are not reproducible with a Gross–Pitaevskii engine, but they are (i) the experimental/theory comparison for the friction and the transverse (Hall-angle) coefficient that our programme measures in the classical field, and (ii) the reference for large-scale GPU performance.

### C. GPU/accelerated GPE codes — baselines for the GPU/TPU phase

| record | solver | notes |
|---|---|---|
| 15908044 **PHOENIX** (Paderborn, MIT) | GPU solver for the 2D nonlinear Schrödinger/GP equation, published as high-performance and energy-efficient | best direct GPU comparison; polariton-oriented terms |
| 58081 **GPUE** (BSD-3) | GPU GPE solver for rapidly rotating BECs (CUDA, split-step FFT) | rotating frame, vortex lattices |
| 5700325 GpuDecGpe (DEC-based, GPU) | discrete exterior calculus GP solver | different discretisation (not FFT) |
| 10578040 **PyGPE** (MIT) | scalar, two-component, spin-1, spin-2 GPE in Python | CPU/GPU array backends; multi-component reference |
| Kwon–Shin code (20068724) | CuPy split-step | the only one with a *published run* we can compare numbers with |

### D. Experimental data relevant to the physics results of the programme

Gauthier 2019 and Sunami 2023 (already in use), the Hall-angle/mutual-friction data of Grani 2025 (B), Christodoulou 2021 (first/second sound, already in use).

## Ranking for the first reproduction targets

1. **Kwon & Shin (20068724)** — complete, small, CC-BY, with a deterministic reference run; needs four generic features (rectangular grids, potentials, moving-frame term, absorbing layers) that every later target also needs. *Attempted: see below.*
2. Suchorowski GGPE (17593677) — ground states and quench dynamics with a modified nonlinearity; tests imaginary-time and the generalized term.
3. Vortex-lattice melting (20728008) — rotating trapped thermal field; tests the SPGPE and observables; needs the trap+rotation features.
4. W-SLDA packs (15084263/15639651) — comparison of *physics* (α, α′ of a vortex dipole vs temperature) not of numbers.
5. Polanco 3D field — measurement test only.

## First attempt on target 1 (2026-10-09, independent scheme)

Method: the reference code was read and the model recovered (damped, moving-frame GP with absorbing layers: ∂ₜψ = v(t)∂ₓψ − (i + Γ)[−½∇² + |ψ|² − 1]ψ − iVψ, V = V₀exp(−2((x−100)²+y²)/σ²), V₀ = 0.9, σ = 20 ξ, v ramped 0 → 0.55 in 0.1 τ). Starting from the reference's own t = 0 wave function, **an independent scheme — explicit RK4 on the full right-hand side with spectral derivatives, double precision, dt = 0.01 — was run and the force on the obstacle compared with the reference's `force_x(t)`:**

| convention for the velocity ramp | max |F_ours − F_ref| for t ≤ 1 | relative to max |F| |
|---|---|---|
| v evaluated at RK4 stage times (the natural reading) | 3.5×10⁻³ | 5.3×10⁻³ — a *constant* offset created during the 0.1 τ ramp |
| v held at the **end** of each step, as the reference does (`time_evolv(tt)`, tt = i dt) | **1.1×10⁻⁶ (t ≤ 0.3)** | **6×10⁻⁶** |

The offset is the reference's own O(dt) ramp discretisation (Σ v(iΔt)Δt overshoots ∫v dt by 0.00275 ξ); once reproduced, the two independent implementations agree to a few ppm. Longer comparison (ψ snapshots to t = 50, vortex counts) in progress; results are in `PGPE_EXTERNAL_REPRODUCTION.md` when complete.
