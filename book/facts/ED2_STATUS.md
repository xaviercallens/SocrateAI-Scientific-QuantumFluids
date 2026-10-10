# Second edition: status when the work stopped (2026-10-10, ~07:55)

The first edition (ten chapters, 282 pages) is published: concept DOI 10.5281/zenodo.23272153, version
10.5281/zenodo.23272154, commits 6d4bc1c and 553cc7c on master. The second edition is NOT finished and NOT published.

Work stopped because the account reached its monthly spend limit (HTTP 429; the message gave 11:00 Europe/Paris as the
weekly reset). Eight background authors were killed in the middle of their tasks, none had delivered a chapter.

## What exists on this branch (all of it unverified, in progress)

| item | state |
|---|---|
| `quantum_fluids_book.tex`, `frontmatter_preface.tex`, `qfbook.sty` (\part), `chapters/appC.tex` | second-edition structure: five parts, chapters ch11-ch15 inserted in teaching order, App. C collects `solNN.tex`, App. D; preface describes 15 chapters. Builds only when the new chapters exist (a build now would print a preface that promises them) |
| `facts/make_appA.py`, `facts/make_appB.py`, `figures/ch01_timeline.py`, `chapters/ch01.tex` (caption), `chapters/appB.tex` | generators follow print order (read from the master file); timeline tags computed from citations |
| `facts/FACTS_ED2.md` | the second-edition briefing for authors (anchors, lessons of the first edition, solutions format) |
| `chapters/appD.tex`, `figures/appD_numbers.{py,json}`, `facts/appD_report.md` | Appendix D draft (constants part; notation table incomplete: the inventories of ch03/ch09 were never produced) |
| `facts/ed2_notation_inventory_*.md` | complete notation inventories of ch01-02, ch04-05, ch06-07 (raw material for the notation table) |
| `figures/sol0[1-6]_*`, `figures/sol_common.py`, `lean/Sol06_KTGeneralC.lean` | scripts and numbers for the solutions of chapters 1-6 (no `chapters/solNN.tex` written, the Lean file's compile state unknown) |
| `figures/ch11_*`, `ch12_db1998*`, `ch13_common.py`, `ch15_*`, `rust/ch15_shell` | helper scripts and raw data of the new chapters (ch15 shell-model runs: `figures/ch15_raw/`); no chapter text |

## To resume

1. `git checkout second-edition-wip`; read `facts/FACTS_ED2.md`.
2. Re-launch one author per new chapter (ch11-ch15) and two solution authors (ch01-05, ch06-10), each told to start from
   the files above instead of from scratch. Budget: the first edition took about 12 agent-hours for ten chapters.
3. Finish Appendix D; run `facts/make_appA.py`, `facts/make_appB.py`, `facts/short_captions.py`, `build_refs.py`;
   build; run the checks used for the first edition (0 errors, 0 undefined, 0 missing glyphs, citation check 0 problems).
4. Publish as a new VERSION of the existing record (`scripts/zenodo_deposit_paper.py --new-version-of 23272154 --extra ...`),
   same concept DOI; update `\BookConceptDOI` only if a different concept were used (it is not).
