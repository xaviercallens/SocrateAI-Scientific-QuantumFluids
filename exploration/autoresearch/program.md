# autoresearch — hypothesis triage for the quantum-fluids programme

Adapted from Andrej Karpathy's `autoresearch` (March 2026; copy in
`SocrateAI-Scientific-Agora-LeanMaster/autoresearch`) and from this group's `leanautoresearch`. Karpathy's loop
gives an agent one mutable file, a fixed five-minute budget and one scalar metric, and lets it keep what improves
the metric. Here the same loop selects **which hypotheses deserve a full pre-registered test**.

| | Karpathy `autoresearch` | this directory |
|---|---|---|
| fixed, read-only | `prepare.py` (data, tokenizer, `evaluate_bpb`) | `prepare.py` (data access, budget, `score`) and `hypotheses.json` (novelty, reach, cost) |
| mutable | `train.py` | `probes.py` (one probe per hypothesis) |
| budget | 5 minutes of training | 300 s wall clock per probe, one thread (killed at 600 s) |
| metric | `val_bpb`, lower is better | `score = min(D,5)/5 · novelty · reach/3 · 1/(1 + cost_days/5)`, higher is better |
| decision | keep if `val_bpb` improved, else discard | keep if the score enters the running top 3, else discard; `crash` on failure |
| log | `results.tsv`, untracked | `results.tsv` (tracked here: it is the record of the selection) |

What is **not** the same, stated plainly: Karpathy's metric is an objective loss; ours has three judgement terms
(novelty, reach, cost). They are fixed in `hypotheses.json` and committed **before** any probe runs, each tied to
entries of the literature database (`scripts/litdb.py`), so that only `D` — a number computed from data — can move
the ranking afterwards. The leaderboard is also reported under `D` alone and under the priors alone, to show what
drives the selection.

## Rules

1. `hypotheses.json` and `prepare.py` are frozen at the commit that precedes the first engine run.
2. A probe uses data already on disk, or a simulation that fits in the budget. It returns
   `D = |x_H − x_rival| / σ` and `consistent`. A probe whose own outcome contradicts its hypothesis by more than
   3σ, or whose known-answer check fails, scores 0: a five-minute refutation is recorded and not pursued.
3. A crash caused by a trivial bug may be fixed in `probes.py` and the probe re-run; both rows stay in
   `results.tsv`, the last one counts. The estimator of a probe is **not** changed after its first valid result.
4. The three hypotheses that end in the top 3 get a full pre-registration (`docs/designs/`), a known-answer gate,
   and a Lean companion statement; the others are listed with their probe outcome and left.
5. Known bias of this procedure: it favours hypotheses that can be probed on existing data. Hypotheses whose first
   evidence needs days of new simulation score low on `D` regardless of merit; that is recorded, not corrected.

## Run

    .venv/bin/python exploration/autoresearch/engine.py
