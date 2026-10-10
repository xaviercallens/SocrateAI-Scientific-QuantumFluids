"""Chapter 10, benchmark panel: time per IF-RK4 step of the PGPE problem (N x N, L = N/2, g = 1, dt = 0.01, cutoff kmax/2)
for Rust (1 thread), Rust with the `parallel` feature (1,2,4,8 threads), JAX-CPU, numpy (+ scipy, torch for the left panel).
Sources (all measured on ONE shared machine, load ~7, see caption):
  data/generated/pgpe/bench/engines.json  (best of two sessions)   jax_cpu.json   threads_rust.json
Run:  .venv/bin/python book/figures/ch10_bench.py"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figstyle import *
import matplotlib.ticker
plt.rcParams["axes.unicode_minus"] = False

B = ROOT / "data/generated/pgpe/bench"
eng = json.load(open(B / "engines.json"))["results"]
jax = json.load(open(B / "jax_cpu.json"))["results"]
thr = json.load(open(B / "threads_rust.json"))
Ns = [64, 128, 256, 512]
def series(name): return np.array([[r["us_per_step_best"] for r in eng if r["engine"] == name and r["n"] == n][0] for n in Ns]) / 1e3  # ms
rust, npy, sp1, to1, to4 = (series(k) for k in ("rust", "numpy", "scipy-1", "torch-1", "torch-4"))
jx = np.array([[r["us_per_step_best"] for r in jax if r["n"] == n][0] for n in Ns]) / 1e3
jx_rust_same = np.array([[r["rust_us_per_step_same_session"] for r in jax if r["n"] == n][0] for n in Ns]) / 1e3
tt = thr["us_per_step_best"]                       # {"128": {"1":..}, ...} in us
thr_ms = {int(n): {int(t): v / 1e3 for t, v in d.items()} for n, d in tt.items()}

fig, ax = plt.subplots(1, 3, figsize=(TEXTW * 1.18, 2.9), gridspec_kw=dict(width_ratios=[1.15, 1, 1.0], wspace=0.42))
# (a) time per step
a = ax[0]
a.plot(Ns, npy, "o-", color=GREY, label="numpy")
a.plot(Ns, sp1, "s--", color=GOLD, ms=3.5, lw=1.0, label="scipy (1 worker)")
a.plot(Ns, to4, "^--", color=TEAL, ms=3.5, lw=1.0, label="torch CPU (4 thr.)")
a.plot(Ns, rust, "o-", color=BLUE, label="Rust, 1 thread")
a.plot(Ns, jx, "D-", color=ORANGE, ms=4, label="JAX/XLA CPU")
nn = [128, 256, 512]
a.plot(nn, [thr_ms[n][8] for n in nn], "v-", color=RED, ms=4, label="Rust, 8 threads")
a.set_xscale("log", base=2); a.set_yscale("log"); a.set_xticks(Ns); a.set_xticklabels([str(n) for n in Ns])
a.set_yticks([1, 10, 100, 1000]); a.set_yticklabels(["1", "10", "100", "1000"]); a.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())   # plain labels: no \mathdefault, so the lining figures apply
a.set_xlabel("grid size $N$"); a.set_ylabel("ms per step (best of $n$)"); a.legend(fontsize=6.6, loc="upper left", handlelength=1.6, labelspacing=0.25); a.set_ylim(0.4, 3000); a.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
panel(a, "a")
# (b) time relative to the single-thread Rust step OF THE SAME SESSION (>1 means slower than serial Rust)
b = ax[1]
r_np = npy / rust                                        # engines session (Rust and numpy measured together)
r_jx = jx / jx_rust_same                                 # JAX session (Rust re-measured in it)
r_t8 = np.array([thr_ms[n][8] / thr_ms[n][1] if n in thr_ms else np.nan for n in Ns])   # threads session
b.axhspan(0.25, 1.0, color=BLUE, alpha=0.06, lw=0); b.axhline(1, color=BLUE, lw=1.0)
b.text(0.03, 1.07, "slower than 1-thread Rust", color=GREY, fontsize=6.6, transform=b.get_yaxis_transform(), va="bottom")
b.text(0.03, 0.93, "faster than 1-thread Rust", color=BLUE, fontsize=6.6, transform=b.get_yaxis_transform(), va="top")
x = np.arange(4)
series_b = ((r_np, GREY, "o", "numpy"), (r_jx, ORANGE, "D", "JAX/XLA"), (r_t8, RED, "v", "Rust, 8 thr."))
for y, col, mk, lab in series_b:
    b.plot(x, y, mk + "-", color=col, ms=4.5, lw=1.2)
    # two single-line texts, not one two-line text: matplotlib passes the font features (lining figures) to the backend for single-line texts only
    b.annotate(lab, (x[-1], y[-1]), textcoords="offset points", xytext=(7, 4), va="center", fontsize=6.6, color=col)
    b.annotate(f"{y[-1]:.2f}", (x[-1], y[-1]), textcoords="offset points", xytext=(7, -5), va="center", fontsize=6.6, color=col)
b.set_yscale("log"); b.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter()); b.set_xticks(x); b.set_xticklabels([str(n) for n in Ns]); b.set_ylim(0.3, 7)
b.set_xlim(-0.25, 4.0)
b.set_yticks([0.5, 1, 2, 4]); b.set_yticklabels(["0.5", "1", "2", "4"])
b.set_xlabel("grid size $N$"); b.set_ylabel("time / 1-thread Rust (same session)");
panel(b, "b")
# (c) thread scaling of the Rust step, relative to its own 1-thread time (same session)
c = ax[2]
for n, col in zip((128, 256, 512), (TEAL, GOLD, RED)):
    t = sorted(thr_ms[n]); c.plot(t, [thr_ms[n][1] / thr_ms[n][k] for k in t], "o-", color=col, label=f"$N={n}$")
c.plot([1, 8], [1, 8], ":", color=GREY, lw=0.8); c.text(4.3, 5.6, "ideal", color=GREY, fontsize=7, rotation=24)
c.axhline(1, color=GREY, lw=0.6); c.set_xlabel("threads"); c.set_ylabel("speed-up vs 1 thread"); c.set_xscale("log", base=2)
c.set_xticks([1, 2, 4, 8]); c.set_xticklabels(["1", "2", "4", "8"]); c.set_ylim(0.5, 8.5); c.legend(fontsize=7, loc="upper left", bbox_to_anchor=(0.0, 0.98))
c.text(0.97, 0.40, "$N=512$: ${:.1f}\\times$".format(thr_ms[512][1] / thr_ms[512][8]), transform=c.transAxes, ha="right", fontsize=7.2, color=RED)
c.text(0.97, 0.355, "at 8 threads", transform=c.transAxes, ha="right", va="top", fontsize=6.4, color=RED)      # plain text on its own line: a string with $...$ is set by mathtext, which ignores the lining-figure feature
panel(c, "c")
fig.text(0.5, -0.07, "Machine: Intel Core i7-4930MX (2013, 4 cores / 8 threads), shared, load average about 7 while measuring, no GPU/TPU.", ha="center", va="top", fontsize=6.8, color=GREY)
fig.text(0.5, -0.115, "Absolute times are pessimistic and thread scaling a lower bound; the same JAX case varied 8.8 vs 4.9 ms between sessions. GPU/TPU: not measured.", ha="center", va="top", fontsize=6.8, color=GREY)
save(fig, "ch10_bench")

out = dict(
    N=Ns, rust_ms=rust.round(3).tolist(), numpy_ms=npy.round(3).tolist(), jax_cpu_ms=jx.round(3).tolist(),
    speedup_rust_over_numpy=(npy / rust).round(2).tolist(), jax_time_over_rust_same_session=r_jx.round(2).tolist(), rust8_time_over_rust1_threads_session=[None if np.isnan(v) else round(float(v),2) for v in r_t8],
    jax_vs_rust_same_session_ms=dict(jax=jx.round(2).tolist(), rust=jx_rust_same.round(2).tolist()),
    threads_ms={str(n): {str(k): round(v, 2) for k, v in d.items()} for n, d in thr_ms.items()},
    thread_speedup_512_at_8=round(thr_ms[512][1] / thr_ms[512][8], 2), thread_speedup_256_at_8=round(thr_ms[256][1] / thr_ms[256][8], 2),
    thread_128_slower_than_serial=bool(thr_ms[128][8] > thr_ms[128][1]),
    jax_checksum_max_rel_diff=max(r["rel_diff_vs_rust"] for r in jax), jax_version=jax[0]["jax"], gpu_tpu_measured=False)
json.dump(out, open(Path(__file__).with_name("ch10_bench_numbers.json"), "w"), indent=1)
print(json.dumps(out)[:900])
