#!/usr/bin/env python3
"""Pack the sources of the book into one archive for deposit next to the PDF.

    python3 book/make_source_archive.py [OUT.tar.gz]

The archive holds everything needed to rebuild and audit the book: the LaTeX sources and style, the
bibliographies, every figure script with its PDF and its numbers file, the book's own Lean files, the
Rust crate of Chapter 8, the per-chapter fact reports and the Lean audit logs, and a copy of the Lean
library `QuantumFluids` (lean_src/*.lean plus the toolchain and the Mathlib pin) that the chapters
quote. Build products (aux, log, toc, pycache, Rust target directories) and scratch files are left out.
"""
import subprocess, sys, tarfile
from pathlib import Path

BOOK = Path(__file__).resolve().parent
ROOT = BOOK.parent
PREFIX = "quantum-fluids-in-lean4-book"


def book_files():
    """Every file of book/ that git tracks or would track (book/.gitignore excludes build products, scratch and superseded
    stubs), so that the archive holds exactly the files of the commit."""
    out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "--", "."],
                         cwd=BOOK, capture_output=True, text=True, check=True).stdout.split("\n")
    for rel in sorted(x for x in out if x):
        f = BOOK / rel
        if f.is_file() and not rel.startswith("dist/") and rel != "quantum_fluids_book.pdf":   # the PDF is deposited beside the archive
            yield f, f"{PREFIX}/book/{rel}"


def library_files():
    lib = ROOT / "lean_src"
    for f in sorted(lib.glob("*.lean")):
        if not f.name.startswith("_tmp"):
            yield f, f"{PREFIX}/lean_src/{f.name}"
    for name in ["lakefile.lean", "lean-toolchain", "lake-manifest.json"]:
        if (lib / name).exists():
            yield lib / name, f"{PREFIX}/lean_src/{name}"
    for name in ["LICENSE", "LICENSE-MIT", "LICENSE-APACHE"]:
        yield ROOT / name, f"{PREFIX}/{name}"


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else BOOK / "dist" / f"{PREFIX}-sources.tar.gz"
    out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with tarfile.open(out, "w:gz") as tar:
        for src, arc in list(book_files()) + list(library_files()):
            tar.add(src, arcname=arc, recursive=False)
            n += 1
    print(f"{n} files -> {out} ({out.stat().st_size / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
