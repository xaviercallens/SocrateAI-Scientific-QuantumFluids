"""JAX/XLA engine for the projected-GPE benchmark (same problem as bench_engines.py / crates/qf-pgpe/examples/bench_step.rs): jit-compiled IF-RK4 step, `lax.fori_loop`.
Runs unchanged on CPU, GPU (CUDA) and TPU: select the device with JAX_PLATFORMS=cpu|cuda|tpu; the JSON line carries the device description, so the same file
produces the GPU/TPU rows of the paper's table later. Use a venv with a recent numpy (system numpy 1.26 cannot import jax 0.11):
    /mnt/data/xdev-cache/venv-jax-uv/bin/python exploration/pgpe/bench_jax.py --ns 64,128,256,512 --steps 100 --reps 5 [--dtype complex128|complex64]
"""
import argparse, json, os, sys, time
import numpy as np
import jax
import jax.numpy as jnp
from jax import lax

ap = argparse.ArgumentParser(); ap.add_argument("--ns", default="64,128,256,512"); ap.add_argument("--steps", type=int, default=100); ap.add_argument("--reps", type=int, default=5)
ap.add_argument("--dtype", default="complex128"); ap.add_argument("--out", default=None); ap.add_argument("--scale-steps", action="store_true"); a = ap.parse_args()
if a.dtype == "complex128":
    jax.config.update("jax_enable_x64", True)
CT = jnp.complex128 if a.dtype == "complex128" else jnp.complex64; RT = jnp.float64 if a.dtype == "complex128" else jnp.float32


def build(N, dt=0.01, g=1.0):
    L = N / 2.0; dx = L / N; k1 = 2 * np.pi * np.fft.fftfreq(N, d=dx); KX, KY = np.meshgrid(k1, k1, indexing="ij"); k2 = KX ** 2 + KY ** 2
    P = np.sqrt(k2) <= 0.5 * np.pi / dx; lin = -0.5j * k2
    E1 = jnp.asarray(np.exp(lin * dt / 2) * P, dtype=CT); E2 = jnp.asarray(np.exp(lin * dt) * P, dtype=CT); Pj = jnp.asarray(P)

    def nonlin(c):
        psi = jnp.fft.ifft2(c); return -1j * g * Pj * jnp.fft.fft2(jnp.abs(psi) ** 2 * psi)

    def step(c):
        a_ = nonlin(c); b = nonlin(E1 * (c + 0.5 * dt * a_)); cc = nonlin(E1 * c + 0.5 * dt * b); d = nonlin(E2 * c + dt * E1 * cc)
        return E2 * c + (dt / 6.0) * (E2 * a_ + 2.0 * E1 * (b + cc) + d)

    run = jax.jit(lambda c, n: lax.fori_loop(0, n, lambda i, x: step(x), c), static_argnums=())
    c0 = np.zeros((N, N), complex); c0[0, 0] = N * N; c0[0, 1] = 0.3 * N + 0.1j * N; c0[1, 0] = -0.2 * N + 0.2j * N
    c0 = np.fft.fft2(np.fft.ifft2(c0)) * P                       # projected, as in bench_step / bench_engines
    return run, jnp.asarray(c0, dtype=CT)


res = []
for N in [int(x) for x in a.ns.split(",")]:
    steps = max(10, int(a.steps * (128 / N) ** 2)) if a.scale_steps else a.steps
    run, c0 = build(N); n = jnp.int32(steps)
    run(c0, n).block_until_ready()                                    # compile + warm-up
    ts = []
    for _ in range(a.reps):
        t0 = time.perf_counter(); c = run(c0, n).block_until_ready(); ts.append((time.perf_counter() - t0) / steps)
    ts.sort(); cn = np.asarray(c); chk = float(np.abs(cn.real).sum() + np.abs(cn.imag).sum())
    row = dict(engine=f"jax-{jax.default_backend()}" + ("" if a.dtype == "complex128" else "-c64"), n=N, steps=steps, us_per_step_best=1e6 * ts[0], us_per_step_median=1e6 * ts[len(ts) // 2], checksum=chk,
               device=str(jax.devices()[0]), jax=jax.__version__, dtype=a.dtype)
    res.append(row); print(json.dumps(row), flush=True)
if a.out:
    json.dump(dict(date=time.strftime("%F %T"), results=res), open(a.out, "w"), indent=1)
