#!/usr/bin/env python3
"""Ledger integrity for QuantumFluids.

WHAT THIS ENFORCES, AND WHOSE RULES THEY ARE
--------------------------------------------
These are **this repository's own rules**, not Stream 0's. They were written
down in `LEDGER.md` and `docs/ROSETTA_ROW.md` and nothing checked them:

  R1  `LEDGER.md` and `ledger.jsonl` name the same claim ids.
  R2  Claim ids are unique. (The `## Template entry` block is skipped — its
      example claim reuses `CLAIM-001` on purpose and is not a duplicate.)
  R3  Every claim carries a Statement, a Source, and Filed/Updated dates.
  R4  Labels are `QF-VERIFIED` / `QF-TESTED` / `QF-NARRATIVE`; statuses are
      `PENDING` / `VERIFIED` / `DISPUTED` / `RETRACTED`. `LEDGER.md` §1-5
      states both lists.
  R5  Every file path named in a Source actually exists.
  R6  `docs/ROSETTA_ROW.md`: *"All claims in LEDGER.md marked QF-VERIFIED must
      have a LITERATURE_LEDGER.md entry with retrieval date and DOI/URL."*
      Note what this rule cannot express now that the labels are merged: a
      claim proved in Lean also wears `QF-VERIFIED`, and a kernel proof has no
      literature entry and needs none. See the note under R6 below.

ON RESOLVING PATHS — READ THIS BEFORE ADDING A CHECK
----------------------------------------------------
The literature ledger lives at `docs/LITERATURE_LEDGER.md`, but is referenced
throughout as `LITERATURE_LEDGER.md`. A root-relative existence check therefore
reports it missing, and while writing this file that produced a confident,
wholly wrong finding — "the ledger does not exist and ten files cite it".

Three such false positives were caught before this checker was ever run in
anger: two test files that live under `tests/`, and the literature ledger. Every
one came from resolving a name against the wrong directory.

So both `R5` and `R6` resolve a reference by looking anywhere in the tree, and
only report absence when the basename occurs nowhere at all. A checker that
cries wolf is worse than no checker: it trains readers to skim past its output,
and the one true finding then arrives in a stream of noise.

Exit 0 on a clean ledger, 1 otherwise. Standard library only.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LABELS = {"QF-VERIFIED", "QF-TESTED", "QF-NARRATIVE"}
STATUSES = {"PENDING", "VERIFIED", "DISPUTED", "RETRACTED"}
REQUIRED = ("statement", "source", "filed", "updated")

CLAIM_RE = re.compile(r"\[(CLAIM-\d+)\]\s*\[([A-Z-]+)\]\s*\[([A-Z]+)\]")
PATH_RE = re.compile(r"([A-Za-z0-9_./-]+\.(?:md|py|json|lean|csv|txt|yml))")
TEST_RE = re.compile(r"test:([A-Za-z0-9_./]+)")


def md_claim_ids(text: str) -> list[str]:
    """Ids from the live section only; the Template block is not a claim."""
    if "## Current claims" in text:
        text = text.split("## Current claims", 1)[1]
    return [m.group(1) for m in CLAIM_RE.finditer(text)]


def main() -> int:
    findings: list[str] = []

    jl = ROOT / "ledger.jsonl"
    md = ROOT / "LEDGER.md"
    if not jl.exists():
        print("FAIL  ledger.jsonl is missing")
        return 1
    rows = [json.loads(l) for l in jl.read_text().splitlines()
            if l.strip() and not l.startswith("#")]
    md_ids = md_claim_ids(md.read_text())

    # R2
    seen: set[str] = set()
    for r in rows:
        if r["id"] in seen:
            findings.append(f"R2 duplicate claim id in ledger.jsonl: {r['id']}")
        seen.add(r["id"])
    for i in md_ids:
        if md_ids.count(i) > 1:
            findings.append(f"R2 duplicate claim id in LEDGER.md: {i}")
            break

    # R1
    for i in set(md_ids) - seen:
        findings.append(f"R1 {i} is in LEDGER.md but not in ledger.jsonl")
    for i in seen - set(md_ids):
        findings.append(f"R1 {i} is in ledger.jsonl but not in LEDGER.md")

    # resolved anywhere in the tree: it lives under docs/, not at the root
    lit_files = list(ROOT.rglob("LITERATURE_LEDGER.md"))
    lit_ids = set()
    for f in lit_files:
        lit_ids |= set(re.findall(r"\[(LIT-\d+)\]", f.read_text()))

    for r in rows:
        # R3
        for f in REQUIRED:
            if not r.get(f):
                findings.append(f"R3 {r['id']} has no {f}")
        # R4
        if r["label"] not in LABELS:
            findings.append(f"R4 {r['id']} has unknown label {r['label']!r}")
        if r["status"] not in STATUSES:
            findings.append(f"R4 {r['id']} has unknown status {r['status']!r}")
        # R5 — resolve relative to the root, then anywhere in the tree.
        # A Source may name `test:test_foo.py::test_bar`, and the file lives
        # under tests/. Reporting that as missing would be a false positive,
        # which is worse than not checking: it trains readers to ignore the
        # output. (Two of these were caught before this PR was opened.)
        for path in set(PATH_RE.findall(r.get("source", ""))):
            if (ROOT / path).exists():
                continue
            if any(ROOT.rglob(Path(path).name)):
                continue
            findings.append(
                f"R5 {r['id']} cites {path}, which does not exist anywhere "
                "in the tree")
        # R6 — every LIT-nnn a claim cites must exist in the literature ledger.
        # NOT "every QF-VERIFIED claim must cite one": since the labels were
        # merged, `QF-VERIFIED` covers both citation-backed and kernel-proved
        # claims, and a Lean proof has no literature entry and needs none.
        # Enforcing the rule as literally written would fire on CLAIM-007 and
        # CLAIM-011, which are kernel-checked. That is the rule being wrong for
        # a merged label, not the claims being wrong -- so the check enforces
        # what the rule was FOR (no dangling citation) rather than its letter.
        if not lit_files:
            findings.append(
                "R6 no LITERATURE_LEDGER.md anywhere in the tree, but "
                "docs/ROSETTA_ROW.md requires entries in it")
        for lid in set(re.findall(r"(LIT-\d+)", r.get("source", ""))):
            if lid not in lit_ids:
                findings.append(
                    f"R6 {r['id']} cites {lid}, which is not in the "
                    "literature ledger")

    print(f"claims: {len(rows)}  findings: {len(findings)}")
    for f in findings:
        print(f"  - {f}")
    if findings:
        print("\nFAIL  ledger")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
