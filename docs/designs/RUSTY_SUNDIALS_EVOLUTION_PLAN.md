# Evolution plan for rusty-SUNDIALS as a quantum-fluid reference solver (2026-10-09)

Inputs: `QUANTUM_FLUID_DATASETS_SURVEY_2026-10-09.md` (what exists to reproduce), the software paper (doi:10.5281/zenodo.23266977; what is verified and measured), the first external reproduction (Kwon & Shin), and the owner's instruction: *reproduce the published solver results, improve the solver and the paper, and prepare GPU/TPU benchmarks later.*

## 0. Where the module stands (measured)

| axis | now | evidence |
|---|---|---|
| physics | homogeneous periodic square-grid projected GPE, vortex imprint/tracking, transport estimators, thermal states, wave scattering | software paper, ledger CLAIM-084…102 |
| verification | Rust ↔ Python to 1e-14…1e-11 on shared inputs; CVODE order 4.00; K1–K4 | `crates/qf-pgpe/tests/`, paper §3 |
| speed (1 thread, 2013 CPU, loaded) | 4.3 / 4.2 / 2.7 / 2.5 × numpy at N = 64…512; 3.2 … 1.5 × the best of scipy/torch; JAX-XLA-CPU now added (8.1 ms at N = 128, same checksum to 1e-12) | `data/generated/pgpe/bench/`, `bench_jax.py` |
| external validation | **none until this week**; first: Kwon–Shin force to 6 ppm with an independent scheme | `exploration/external/kwon_shin_reproduction.py` |

The module cannot reproduce most published solver runs because it lacks four generic things: **non-square grids, potentials (static and moving), a moving-frame term and absorbing layers, ground-state preparation**. Those four are also what any GPU/TPU port needs to be *benchmarked on something other than a toy*.

## 1. Gap analysis against the reference solvers

| capability | qf-pgpe now | Kwon–Shin code | PHOENIX (GPU) | GPUE (GPU) | PyGPE | W-SLDA | needed for |
|---|---|---|---|---|---|---|---|
| rectangular grid Nx ≠ Ny, Lx ≠ Ly | no | yes | yes | yes | yes | yes | A1 |
| static / moving potential V(x,y,t) | no | yes | yes | yes | yes | yes | A2 |
| moving-frame term v∂ₓ | no | yes | – | – | – | – | A2 |
| absorbing layers / damped GPE Γ(x,y) | no | yes | yes (gain–loss) | – | – | – | A3 |
| imaginary-time ground state | no | yes (pseudo-spectral) | – | yes | yes | yes | A4 |
| rotating frame −Ω L_z, harmonic trap | no | – | – | yes | yes | – | A5 |
| stochastic noise (SPGPE) | thermal *states* only | – | yes | – | – | – | A6 |
| generalized nonlinearity (LHY, 3-body) | no | – | polariton terms | – | – | – | A7 |
| multi-component / spinor | no | – | – | – | yes | – | later |
| 3D | no | – | – | yes | yes | yes | A8 |
| single precision | no (f64 only) | complex64 | yes | yes | – | – | C2 |
| GPU | no | CuPy | CUDA | CUDA | CuPy | CUDA+MPI | C |

## 2. Phases, deliverables and acceptance tests

### Phase A — CPU: make it able to reproduce (weeks 1–3)

- **A1 rectangular grids.** `ComplexField2D` generalised to `(nx, ny, lx, ly)` with square as the special case; the existing 27 tests and the bit-identical checksums must pass unchanged on the square case. *Acceptance:* K1–K4 on a 2:1 grid; the plane-wave exact solution along either axis.
- **A2 potentials and the moving frame.** An optional real-space potential `V(x,y)` (static) and a velocity `v(t)` entering the linear operator exactly, in the integrating factor (`exp(i(v kx − k²/2)dt)` is diagonal, so the frame term costs nothing). *Acceptance:* the Kwon–Shin force within 10⁻⁵ relative for t ≤ 10 from the reference's t = 0 field.
- **A3 absorbing layers.** The damped step `−(i+Γ)(…)` with position-dependent Γ(x,y); the part of the linear operator proportional to Γ∇² is not a Fourier multiplier, so it goes into the RK4 right-hand side (as the independent scheme in `kwon_shin_reproduction.py` does, which already works); IF-RK4 with the remainder. *Acceptance:* energy and norm balance of an outgoing wave; same Kwon–Shin test through t = 50 (ψ snapshots).
- **A4 imaginary-time ground states.** Normalised-gradient-flow or the reference's exact imaginary-time nonlinear step (`ψ e^{−V'dτ}/√(1+|ψ|²(1−e^{−2V'dτ})/V')`), convergence criterion `∫|Δψ|² < ε dτ`. *Acceptance:* reproduces the reference's t = 0 field (`psi_time_0.0.npy`) to 10⁻⁴.
- **A5 rotation and trap.** `−Ω L_z` in real space; harmonic V. *Acceptance:* vortex-lattice density of a rotating condensate (Feynman: n_v = 2Ω/κ); the GPUE example.
- **A6 SPGPE noise** (growth/noise terms). *Acceptance:* thermalisation to the temperature set by (μ, T) in the equipartition thermometer, to be compared with the vortex-lattice-melting data (20728008).
- **A7/A8** generalized nonlinearity (Suchorowski) and a 3D crate for the Polanco field and 3D vortex lines — later, after A1–A4.
- **A9 I/O.** `.npy`/HDF5 snapshots with a JSON manifest (grid, parameters, checksum), so a run is a file the Python and JAX engines can read.

### Phase B — a reproduction suite that is part of CI (weeks 2–4)

A crate `qf-bench` with a **registry**: for each external record the DOI, files, SHA-256, licence, the *metric*, the tolerance and the status; a downloader with retries (Zenodo gateway timeouts are routine), a runner producing a JSON report, and a CI job that runs only the small cases (Kwon–Shin t ≤ 10, a few MB). Entries, in order: Kwon–Shin (force, ψ(t), vortex count); the programme's own known answers; Suchorowski ground state; vortex-lattice melting (when A5/A6 exist); Gauthier/Sunami as *measurement* checks of the observables on experimental data. Each entry states what **failed** to reproduce, as in the programme's registered gates.

### Phase C — GPU and TPU (when hardware is available)

Design before hardware, so that the first run is a measurement rather than a port:

1. **One problem specification, three implementations that must agree.** The benchmark problem of `bench_engines.py` (N×N, L = N/2, g = 1, dt = 0.01, cutoff k_max/2, fixed initial state) is already implemented in Rust (`bench_step`), numpy/scipy/torch (`bench_engines.py`) and **JAX (`bench_jax.py`, same checksum to 1e-12)**. Every new device/engine must reproduce the checksum to 1e-10 before a time is accepted.
2. **TPU via XLA.** TPUs are reached through JAX or PyTorch/XLA, not through Rust; so JAX is the TPU path and the differential-testing oracle for any hand-written GPU kernel. `bench_jax.py` takes `JAX_PLATFORMS=cpu|cuda|tpu` and records the device. Known constraints to measure: TPU FFT dtype support (complex64 first; float64 emulated and slow), padding to the 8×128 tile (N = 128 is the first natural size), host↔device transfer for per-sample observables.
3. **GPU via CUDA from Rust.** `cudarc` + cuFFT (and a `wgpu` portable variant only if cuFFT proves insufficient); the pruned-FFT optimisation of the CPU path has an analogue (batched 1D transforms over active rows). Single precision is a requirement (the Kwon–Shin reference is complex64): the reproduction suite of Phase B defines the tolerance at which complex64 is acceptable (e.g. force within 10⁻³ for t ≤ 50).
4. **Baselines on the same machine:** torch CUDA (`bench_engines.py` already has the CPU rows), CuPy, **PHOENIX**, **GPUE**, and the **Kwon–Shin CuPy code** itself, run on the same problem or on the reproduced case; report time per step, steps per second per watt, and memory per grid point.
5. **Metrics.** Time per step (best of n, device-synchronised), throughput of independent runs, accuracy against the f64 CPU engine, and *time to reproduce a published result* (Kwon–Shin t = 50 end to end) — the number a user cares about.
6. **Hardware request:** one NVIDIA GPU (any Ampere or later) and one TPU v-slice (even a free-tier Colab TPU runs `bench_jax.py` unchanged).

### Phase D — the software paper

The published version (v1) stays as is. A v2 adds: (i) the survey and the external-reproduction section (Kwon–Shin: scheme-independent agreement, the ramp-convention finding); (ii) the JAX-XLA CPU row; (iii) the plan above as a short "roadmap" paragraph, not as claims; (iv) GPU/TPU rows when measured. It should not claim a "best solver": the comparison set grows by JAX now and by PHOENIX/GPUE/torch-CUDA/TPU later, and only measured rows are reported.

## 3. Risks

- Zenodo gateway timeouts (504/502) are frequent: the downloader must verify size and checksum and retry; CI should use a cached copy of the small datasets.
- Reference codes are single precision with a different discretisation (finite difference in parts); agreement criteria must come from the *physics* observables (force, Strouhal number, vortex counts) beyond a short time, since the wake is unstable and chaotic after shedding sets in (vortices appear at t ≈ 25 in the reference run).
- The Kwon–Shin comparison uses *their* t = 0 field, so it validates the dynamics, not the ground-state solver (A4 is a separate test).
- GPU/TPU numbers will depend on the vendor FFT; a result should always state the library version and the problem size relative to the device's cache/tile.

## 4. This week

1. Finish the Kwon–Shin comparison to t = 50 with the independent scheme (running) and write `PGPE_EXTERNAL_REPRODUCTION.md` with every number, including what does not agree.
2. Implement A1–A3 in a branch of rusty-SUNDIALS (rectangular grid, V, v∂ₓ, Γ) and reproduce the same case in Rust; compare Rust vs numpy-independent scheme vs reference.
3. Run `bench_jax.py` for all N and add the JAX row to the benchmark data.
4. Request the GPU/TPU access and fix the problem specification (§2, C1).
