#!/usr/bin/env python3
"""autoresearch / prepare.py -- the FIXED part of the hypothesis-triage loop (the analogue of Karpathy's
prepare.py: data access, the time budget and the evaluation metric). READ-ONLY once hypotheses.json is
committed: probes.py may be edited between runs, this file and hypotheses.json may not.

Metric. A probe is a <= BUDGET_S second computation on data already on disk. It returns one number,
    D = |x_H - x_rival| / sigma,
the discriminating power of the probe: how many standard errors separate what the hypothesis predicts (or, for
a measurement hypothesis, the measured value) from what its declared rival/null predicts. The score is
    score = min(D, D_CAP)/D_CAP  *  novelty  *  reach/3  *  1/(1 + cost_days/COST_SCALE)
where novelty, reach and cost_days are fixed per hypothesis in hypotheses.json BEFORE any probe runs:
    novelty  1.0 not found by the literature gate | 0.6 partly known, our angle new | 0.3 known in another system | 0 done
    reach    3 answers an open question stated in a cited paper | 2 a number comparable with other groups/experiments
             | 1 methodological note
    cost_days   compute + analysis days to the full pre-registered test on this machine.
Only D comes from the run. A probe that crashes, times out or returns a non-finite D scores 0 ('crash'). A probe
whose outcome contradicts its hypothesis' own sharp prediction by more than 3 sigma, or whose built-in known-answer
check fails, reports consistent = False and scores 0 ('discard'): a five-minute refutation is recorded, not pursued.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
PG = ROOT / "data/generated/pgpe"; R3 = PG / "r3"
BUDGET_S = 300            # wall-clock seconds per probe, as in Karpathy's loop
HARD_KILL_S = 600         # a probe still running at twice the budget is killed and logged as a crash
D_CAP = 5.0
COST_SCALE = 5.0
KEEP_TOP = 3


def score(D: float, novelty: float, reach: int, cost_days: float) -> float:
    if not np.isfinite(D) or D < 0:
        return 0.0
    return float(min(D, D_CAP) / D_CAP * novelty * reach / 3.0 / (1.0 + cost_days / COST_SCALE))


# ---- data access (existing runs only; nothing here launches a simulation) ---------------------------------------
PARTS = {"C": ("C_L128", 128.0, 256), "C2": ("C2_L128", 128.0, 256), "C3": ("C3_L192", 192.0, 384)}


def run_names(part: str) -> list[str]:
    tag = PARTS[part][0]
    return sorted(f.stem for f in R3.glob(f"{tag}_e*_s??.json"))


def record(name: str) -> dict:
    """Run-level record: T, n_s/n, K = 2 pi n_s / T, R_L, R_T, eta, class ('A' if n_s/n < 0 else 'N')."""
    d = json.loads((R3 / f"{name}.json").read_text()); B = d["blocks"]
    T = float(np.mean([b["T"] for b in B])); JL = float(np.mean([b["JL"] for b in B])); JT = float(np.mean([b["JT"] for b in B]))
    ns = 1 - JT / JL; eta = float(np.nanmean([b["eta"] for b in B]))
    return {"name": name, "e": float(d["e"]), "L": float(d["L"]), "T": T, "ns_over_n": ns, "K": 2 * np.pi * ns / T,
            "R_L": JL / (T * d["L"] ** 2), "R_T": JT / (T * d["L"] ** 2), "eta": eta, "class": "A" if ns < 0 else "N",
            "cond": float(np.mean([b["cond"] for b in B])), "n_v": float(np.mean([b["n_v"] for b in B]))}


def positions(name: str):
    """(t, [pos_i (n_i, 2)], [q_i (n_i,)]) for the 100 saved samples of a run."""
    z = np.load(R3 / f"{name}_samples.npz", allow_pickle=True)
    return z["t"], z["pos"], z["q"]


def snapshot_times(name: str) -> list[float]:
    return sorted(float(f.name.split("_sample_t")[1][:-4]) for f in R3.glob(f"{name}_sample_t*.raw"))


def snapshot(name: str, t: float, N: int = 384) -> np.ndarray:
    """Real-space field psi(x) of an L = 192 run at time t (complex128, N x N). Only Part C3 has these."""
    return np.fromfile(R3 / f"{name}_sample_t{t:07.1f}.raw", dtype=np.complex128).reshape(N, N)


def emit(D: float, **detail) -> None:
    """The one line engine.py parses."""
    print("PROBE_RESULT " + json.dumps({"D": float(D), **detail}, default=float))
