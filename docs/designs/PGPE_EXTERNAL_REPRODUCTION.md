# External reproduction log — what the quantum-fluid solvers of this programme reproduce of other people's published results

Rule: an entry states the reference (DOI, licence), what was compared, with what scheme, the numbers, **and what did not agree**. Nothing here is a claim about a result that was not run.

## 1. Kwon & Shin, flow past a penetrable obstacle (Phys. Rev. Research 2026; Zenodo 10.5281/zenodo.20068724, CC-BY-4.0)

**Reference.** GPU code (CuPy, pseudo-spectral split-step with RK4 linear half-steps, complex64) and one complete run: V₀ = 0.9, σ = 20 ξ, obstacle at x = 100 ξ, flow v = 0.55 reached in 0.1 τ, box 500 × 250 ξ on 1000 × 500 points, dt = 0.01, absorbing layers (γ₀ = 0.1, widths 50 and 40 ξ), ψ snapshots at t = 0, 10, …, 50, the force on the obstacle every 0.1 τ to t = 100, vortex counts every 5 τ to t = 50.
**Model recovered from the code** (`QUANTUM_FLUID_DATASETS_SURVEY_2026-10-09.md`): ∂ₜψ = v(t)∂ₓψ − (i + Γ)[−½∇² + |ψ|² − 1]ψ − iVψ.
**Scheme here (independent of the reference):** explicit RK4 on the full right-hand side, spectral derivatives, double precision, dt = 0.01, **started from the reference's own t = 0 field** (so ground-state preparation is not tested). Implemented twice: numpy (`exploration/external/kwon_shin_reproduction.py`) and Rust (`qf-pgpe::flow`, example `kwon_shin`).

| comparison | result |
|---|---|
| force on the obstacle, t ≤ 0.3 | max \|F − F_ref\| = **1.13×10⁻⁶** (6×10⁻⁶ of max \|F\|), numpy and Rust identical |
| the same with `v` read at RK4 stage times instead of the reference's step-end convention | constant offset **3.5×10⁻³** created during the 0.1 τ ramp (an O(dt) artefact of the reference: Σ v(iΔt)Δt overshoots ∫v dt by 0.00275 ξ) |
| force, t ≤ 10 (numpy, 1000 steps) | max \|F − F_ref\| = **2.2×10⁻⁴** at t = 7.8 (4×10⁻⁵ of max \|F\| = 5.45), growing smoothly (5×10⁻⁶ at t = 1, 6×10⁻⁵ at t = 3, 1.5×10⁻⁴ at t = 5) and decreasing after t ≈ 8 |
| ψ(t = 10) against the reference snapshot (numpy) | relative L2 distance **2.2×10⁻⁴**, max \|Δψ\| = 1.2×10⁻³ |
| Rust at t = 10 (1000 steps, 1241 s on a loaded machine) | force max \|F − F_ref\| = **2.207×10⁻⁴** (4.1×10⁻⁵ of max \|F\|), ψ(10) relative L2 distance **2.175×10⁻⁴** — the same as numpy to the digits quoted, i.e. the two implementations of the scheme agree with each other far better than either agrees with the reference |

**Reading.** The smooth, monotone growth of the difference is what a systematic discretisation difference looks like (the reference's splitting is second order and its arithmetic single precision; ours is fourth order in time and double): it is not the chaotic divergence of a shedding wake, which in the reference sets in later (vortices first counted at t = 25). Agreement at the 10⁻⁴ level in ψ over 10 τ, for two different schemes, supports the recovered model and the reference run.
**Not tested / not agreeing.** (i) t > 10: ψ snapshots at 20–50 and the vortex counts (0, 0, 0, 0, 0, 2, 3, 2, 4, 6, 7 at t = 0…50) are not yet compared; the wake becomes unstable, so a pass criterion must be statistical (counts, first-shedding time), not pointwise. (ii) The ground state (imaginary-time) is not reproduced. (iii) **Speed:** the Rust engine is not faster than numpy on this 1000 × 500 problem (≈ 0.8 against ≈ 0.9 s per RK4 step single-threaded, both on a loaded machine); the advantage of the square power-of-two engine does not carry over. This size is the natural first GPU/TPU target.

### 1b. Ground-state preparation (the reference's `psi_time_0.0.npy`) — reproduced, and what it shows

**Scheme** (re-implemented from `imag_time_evolv.py` and `run_shedding.py`, v_init = 0, `init = "imaginary"`): Thomas–Fermi start √(1−V), then repeated first-order splitting — heat kernel exp(−k²δτ/2) in Fourier space, then the exact solution of ∂τψ = −(V′+|ψ|²)ψ with V′ = V − 1 — until γ = ∫|ψ_new − ψ_old|² dx dy (trapezoid rule) < ε δτ with ε = N_x N_y·10⁻⁹, δτ = 0.04, at most 25 000 steps; then the seeded noise 10⁻⁴(integers in [−5, 5) + i·integers) from `default_rng(2026)`. Implemented in numpy (`exploration/external/kwon_shin_ground_state.py`) and in Rust (`FlowSolver::ground_state`, example `kwon_shin_ground`; the noise is added in Python because the numpy random stream is not reproduced in Rust).

| comparison with the stored `psi_time_0.0.npy` | relative L2 | max \|Δψ\| |
|---|---|---|
| numpy, without the noise | 4.1×10⁻⁴ (= the rms of the noise) | 7.1×10⁻⁴ |
| **numpy, with the seeded noise** | **2.84×10⁻⁸** | 6.0×10⁻⁸ |
| **Rust, with the seeded noise** | **2.84×10⁻⁸** (same digits) | 6.0×10⁻⁸ |

2.8×10⁻⁸ is single-precision round-off: the stored field (complex64) is reproduced to its representation, including the noise realisation. The algorithm is therefore read correctly.

**What it shows about the reference.** With the reference's tolerance the stopping criterion is met **at the first imaginary-time step** (γ(1) = 1.395×10⁻⁵ < ε δτ = 2×10⁻⁵; both implementations stop after one step, τ = 0.04). The stored initial field is thus the Thomas–Fermi field after a single step of the imaginary-time operator plus noise, not a relaxed stationary state of the penetrable-obstacle problem. (Our unit test shows the opposite regime: with a tight tolerance the loop converges to a state whose stationary-equation residual is first order in δτ.) This is a statement about the data deposited, not a criticism of the published analysis, whose observables are measured at late times; but anyone using `psi_time_0.0.npy` as a ground state should know that the early-time force contains the relaxation of that initial state through the first few τ (the absorbing layers remove the radiated sound). It is also the reason why the reference's F(t) at t ≲ 5 is not a stationary-flow quantity.

### 1c. Engine timings (JAX/XLA added to the comparison; CPU only)

JAX 0.11.2 (XLA CPU, complex128, `jit` + `fori_loop`, default thread pool), best of 5, against the single-threaded Rust step, same minutes, machine shared with other jobs (8 cores, load ≈ 7: timings vary up to 2× between runs):

| N | steps | Rust (µs/step) | JAX-CPU (µs/step) | checksum difference |
|---|---|---|---|---|
| 64 | 400 | 600 | 1133 | 5×10⁻¹⁴ |
| 128 | 100 | 2859 | 4914 | 1×10⁻¹³ |
| 256 | 25 | 27 159 | 13 560 | 1×10⁻¹⁴ |
| 512 | 10 | 123 467 | 73 605 | 7×10⁻¹⁴ |

The checksum agreement (limited by the 13 digits printed by the Rust example) holds at all sizes. **Reading:** below N = 128 the single-threaded Rust engine is 1.7–1.9× faster than JAX; at N = 256 and 512 the multi-threaded XLA engine is 1.8–2× *faster* than single-threaded Rust. The earlier Rust "parallel" variant (rayon over rows) gave no speed-up and was removed; the cause was never investigated. **Pinned to one core** (`taskset`, two different cores, best of 5, same minutes) the order reverses: Rust 3.0–3.5 ms / 27.6–30.3 ms / 149–160 ms against JAX 5.4–5.8 / 33.6–33.8 / 155–172 ms at N = 128 / 256 / 512, i.e. Rust is 1.1–1.8× faster per core at every size. The XLA advantage at N ≥ 256 is therefore **threading, not a better algorithm**, and the missing piece of the Rust engine is a working intra-step parallelism (serial transposes and element-wise loops are the suspects; the earlier attempt parallelised only the row pass; none of this is measured yet). The honest summary for the software paper is that the Rust engine wins at small sizes and loses at large ones until its intra-step parallelism works — a defect to fix before any GPU comparison, not a result to hide (data: `data/generated/pgpe/bench/jax_cpu.json`).

### 1d. Intra-step threading in Rust (`parallel` feature) — first measurement, machine not idle

The suspected causes of the earlier failure (serial transposes and element-wise loops around a parallel row pass) were removed: the row FFT passes, the in-place transposes (disjoint tile pairs) and all element-wise loops now run on a rayon pool, behind the cargo feature `parallel` and `ComplexField2D::with_threads(t)`. The unit test asserts bit-identical results for 1, 2 and 5 threads; the benchmark checksums are identical for every thread count. Best of 5, µs per step, **with the machine at load average ≈ 7** (the scaling is therefore a lower bound; to be repeated on an idle machine):

| N | 1 thread | 2 | 4 | 8 | JAX-CPU (default threads) |
|---|---|---|---|---|---|
| 128 | 3340 | 4260 | 3994 | 5153 | 4914 |
| 256 | 30 650 | 23 826 | 19 094 | 18 949 | 13 560 |
| 512 | 159 595 | 119 715 | 87 824 | 67 761 | 73 605 |

N = 512: 2.4× at 8 threads (Rust 68 ms against 74 ms for XLA); N = 256: 1.6×, still slower than XLA (19 against 14 ms); N = 128: threading is slower than serial and must stay off. Two things remain: the measurement on an idle machine, and the remaining serial work (the copy into the scratch buffer, the plan scratch allocation per row block).
