#!/usr/bin/env python3
"""Pack the source archive that accompanies the exciton-fluid technical note on Zenodo.

    python3 scripts/pack_exciton_note.py paper/exciton_fluid_note_sources.tar.gz

Contains the git-tracked files of: the note (tex, bib, generated numbers, PDF), the six exciton-fluid design/result documents and the
Lean alignment note, the whole `exploration/exciton/` tree (Lean files and verification reports, Python references and summarisers,
the Rust crate, the run records and results of both phases), and the Lean pins of the library. Run it after committing, so that the
archive and the repository agree; the commit hash is written to MANIFEST.txt inside the archive.
"""
import hashlib, io, subprocess, sys, tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREFIXES = [
    "paper/exciton_fluid_phase1.tex", "paper/exciton_fluid_phase1.pdf", "paper/exciton_numbers.tex",
    "paper/exciton_cases_table.tex", "paper/refs_exciton.bib",
    "docs/designs/EXCITON_FLUID_", "docs/designs/LEAN_TOOLCHAIN_ALIGNMENT_v4_34_1.md",
    "exploration/exciton/", "lean_src/lakefile.lean", "lean_src/lean-toolchain", "lean-toolchain",
    "scripts/pack_exciton_note.py",
]

def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, check=True).stdout

def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "paper/exciton_fluid_note_sources.tar.gz"
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
