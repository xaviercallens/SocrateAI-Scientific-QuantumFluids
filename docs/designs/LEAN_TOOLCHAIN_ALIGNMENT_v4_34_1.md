# Lean toolchain alignment: v4.34.0-rc2 → v4.34.1 (2026-10-11)

Owner instruction (2026-10-10, mid-session): "use the second disk and lean tool chain the second disk and align to the last
lean toolchain version". Upstream `openai/math` and the LeanMaster contributions are on Lean v4.34.1 / Mathlib tag v4.34.1
(commit `d13f23b7`); this library was on v4.34.0-rc2 / Mathlib `85e3a25` since 2026-09-19.

## What was done

1. A dedicated environment on the second disk: `/mnt/data/xdev-cache/lean-env/qfenv` (`lakefile.toml`: Mathlib v4.34.1; built
   oleans via the cache), `ELAN_HOME=/mnt/data/home/xavkal/.elan`, toolchain `leanprover/lean4:v4.34.1`
   (commit `5045d0056413266e57c625dcd7c365b10e377c52`).
2. The audited library was built **without any source change** from a copy of `lean_src/*.lean` with only the pins changed
   (`/mnt/data/xdev-cache/lean-env/qf_lib`): `lake build` → "Build completed successfully (8999 jobs)", including
   `MadelungNSE` and its dependency, the OpenAI NavierStokesAndEuler tree at `8937a8f4` (which itself stays on rc2).
3. A per-module audit (each module compiled by `lake env lean`, output kept): 38 modules, exit 0, no error, no `sorry`;
   257 `#print axioms` statements, every one within `{propext, Classical.choice, Quot.sound}` (the same count as the README's
   "257 theorems").
4. Repository pins changed in a separate commit: `lean-toolchain`, `lean_src/lean-toolchain`, `lean_src/lakefile.lean`
   (`require mathlib … @ "v4.34.1"`, declared last as Lake advises), `README.md` (badge, import comment, build comment,
   alignment sentence). `lean_src/lake-manifest.json` is **not tracked** (git-ignored); the manifest produced by the
   successful build is kept at `/mnt/data/xdev-cache/lean-env/lake-manifest.v4.34.1.json`. The local, untracked
   `lean_src/lake-manifest.json` was overwritten with it by mistake for a few minutes and then **reconstructed** from the
   revisions of the packages of the rc2 workspace (all 12 revisions matched the old file's printed prefixes; byte format may
   differ); `lake` regenerates it anyway.
5. The new exploration files (`exploration/exciton/lean/`) are compiled against the same pin.

## What was not done / caveats

* **The Comparator runs recorded in the repository were made under rc2 and were not repeated under v4.34.1** (the tool and its
  sandbox were not exercised in this session; `scripts/install_comparator_tools.sh` still defaults to tag v4.34.0-rc2).
  Until they are repeated, "Comparator: two kernels" refers to the rc2 runs.
* The existing local workspace `lean_src/.lake` is a symlink to `/mnt/data/home/xavkal/xavkal-tools/qf-lake`, which holds the
  rc2 build. It was **not touched**. With the new manifest, `cd lean_src && lake build` will try to move that workspace to
  Mathlib v4.34.1 (network and several GB). To use the already built tree instead, run the build in
  `/mnt/data/xdev-cache/lean-env/qf_lib` (it holds copies of the module files; re-copy after edits) or repoint the symlink.
* Two workspaces must not share one `packagesDir`: during this session a `lake update` in `qf_lib` (whose `packagesDir` pointed
  at `qfenv`) briefly broke an independent verifier's first run. The `packagesDir` line is a local hack of `qf_lib`, not in the
  repository.
* Published records (the book, paper v2.1, software bundles up to v1.20.0) state rc2; they are tied to their tags and remain
  true of those tags.
* The `book/` chapters' Lean files are checked against "the OpenAI tree's Mathlib" (rc2) by their own scripts and were not
  re-run.

## Evidence

`/mnt/data/xdev-cache/lean-env/qf_lib_audit/{progress.log, <Module>.log}` (outside the repository: logs are large);
build log `/mnt/data/xdev-cache/lean-env/qf_lib_build2.log`.
