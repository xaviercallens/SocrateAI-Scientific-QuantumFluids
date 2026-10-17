#!/usr/bin/env python3
"""Pack the source archive that accompanies the fifth paper (paper/exciton_fluid_gated_V.tex) on Zenodo.

    python3 scripts/pack_exciton_gated_V.py paper/exciton_fluid_gated_V_sources.tar.gz

Contains the git-tracked files of: the paper (tex, generated numbers and results, figures, PDF), the exciton-fluid design/result/review
documents, and the whole `exploration/exciton/` tree (including three_d/: pre-registrations, rounds 1 and 2, all records,
logs and RESULTS files; kk/; the figure scripts). Run it after committing, so that the
archive and the repository agree; the commit hash is written to MANIFEST.txt inside the archive.
"""
import hashlib, io, subprocess, sys, tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREFIXES = [
    "paper/exciton_fluid_gated_V.tex", "paper/exciton_fluid_gated_V_round2.tex", "paper/exciton_fluid_gated_V_h1pp.tex", "paper/exciton_fluid_gated_V.pdf",
    "paper/figs_companion5/",
    "docs/designs/EXCITON_FLUID_", "docs/designs/AXES_3D_COHN_KUMAR_2026-10.md", "exploration/exciton/", "lean-toolchain",
    "scripts/pack_exciton_gated_V.py",
]

def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, check=True).stdout

def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "paper/exciton_fluid_gated_V_sources.tar.gz"
    files = [f for f in git("ls-files").splitlines() if any(f == p or f.startswith(p) for p in PREFIXES)]
    head = git("rev-parse", "HEAD").strip()
    dirty = git("status", "--short", "--", *PREFIXES).strip()
    lines = [f"repository: https://github.com/xaviercallens/SocrateAI-Scientific-QuantumFluids", f"commit: {head}",
             f"files: {len(files)}", ""]
    for f in files:
        data = (ROOT / f).read_bytes()
        lines.append(f"{hashlib.sha256(data).hexdigest()}  {f}")
    if dirty:
        lines += ["", "WARNING: uncommitted changes in the packed paths at packing time:", dirty]
    manifest = "\n".join(lines) + "\n"
    with tarfile.open(out, "w:gz") as tar:
        ti = tarfile.TarInfo("MANIFEST.txt"); ti.size = len(manifest.encode()); ti.mtime = 0
        tar.addfile(ti, io.BytesIO(manifest.encode()))
        for f in files:
            tar.add(ROOT / f, arcname=f, recursive=False)
    print(f"{out}: {len(files)} files, {out.stat().st_size / 1e6:.2f} MB, commit {head[:12]}" + (" (DIRTY)" if dirty else ""))

if __name__ == "__main__":
    main()
