#!/usr/bin/env python3
"""Give every figure of the book a short caption for the List of Figures (editor's tool, 2026-10-10).

The full captions are paragraphs (they carry the provenance of every panel); in the List of Figures they ran to about
fifteen pages.  This script inserts `\\caption[short]{...}` for each figure label listed in SHORT, taking the short title
from the caption's own opening phrase.  It only touches a \\caption that sits in the same figure environment as the label,
and leaves a caption that already has a short form alone.  Re-runnable; prints what it did and any figure without a short
title.

    python3 book/facts/short_captions.py            # apply
    python3 book/facts/short_captions.py --check    # only report figures without a short caption
"""
import re, sys
from pathlib import Path

BOOK = Path(__file__).resolve().parents[1]
SHORT = {
    "ch01:fig-timeline": "The landmarks this book revisits",
    "ch01:fig-bench": "The curve the neutron has to find",
    "ch01:fig-triptych": "One vortex pair seen by the solver and the proof",
    "ch01:fig-budget": "Where the speed of the pair comes from",
    "ch02:fig-stab": "Regions of absolute stability of the Adams and BDF formulas",
    "ch02:fig-workprec": "CVODE on problems with closed-form solutions",
    "ch02:fig-plane": "The exact plane wave against three integrators",
    "ch02:fig-bridge": "The same equation in the two languages",
    "ch02:fig-rates": "Theorems and engine, in rates and in time",
    "ch03:fig-phasefield": "One wave function, three faces",
    "ch03:fig-circ": "Counting quanta on the solver field",
    "ch03:fig-energy": "Where the energy of a vortex sits",
    "ch03:fig-speed": "The speed of a vortex pair in the periodic box",
    "ch03:fig-leap": "Two vortex pairs leapfrog",
    "ch04:fig-dispersion": "The phonon branch of superfluid helium-4 measured by neutron scattering",
    "ch04:fig-bose": "The six Bose integrals of the Lean statement, computed by CVODE",
    "ch04:fig-ladder": "The solver against the proved series",
    "ch04:fig-heatmap": "Which excitations carry the heat?",
    "ch04:fig-budget": "Eq.~(22) against the integral of the measured dispersion",
    "ch04:fig-asymptotic": "The series is asymptotic, not convergent",
    "ch05:fig-curve": "The dispersion relation of superfluid helium-4 at saturated vapour pressure",
    "ch05:fig-thresholds": "Where the three-phonon channel closes",
    "ch05:fig-solver": "The solver measures Bogoliubov's dispersion relation",
    "ch05:fig-universal": "A spectrometer map of the simulated fluid, and the universal curve",
    "ch05:fig-rings": "A dispersive ring wave",
    "ch06:fig-coulomb": "The logarithmic interaction of vortices in the solver",
    "ch06:fig-portrait": "The Kosterlitz flow, integrated with CVODE",
    "ch06:fig-jump": "The universal jump, the finite box and the essential singularity",
    "ch06:fig-field": "The simulated Bose field near the transition",
    "ch06:fig-screening": "The two Lean statements about vortex positions, tested on the solver's configurations",
    "ch07:fig-dipole": "CVODE against the Lean statements on dissipative vortex pairs",
    "ch07:fig-imprint": "A zero-temperature control of the vortex imprint",
    "ch07:fig-fields": "Two antiparallel vortex pairs in a thermal projected Gross--Pitaevskii field",
    "ch07:fig-friction": "The friction in the field",
    "ch07:fig-failures": "Two theorems that were true and did not describe what they were applied to",
    "ch08:fig-zerosound": "The zero-sound root and what it carries",
    "ch08:fig-timedomain": "CVODE against the closed forms of the kinetic equation",
    "ch08:fig-fermisurface": "The Fermi circle as the dynamical variable",
    "ch08:fig-vlasov": "Vlasov--Poisson: the same density wave on two backgrounds",
    "ch08:fig-window": "The $(q,\\omega)$ plane in free-gas units",
    "ch09:fig-wake": "The wake at $t=50\\,\\tau$",
    "ch09:fig-mach": "The flow is locally supersonic long before the first vortex",
    "ch09:fig-force": "The force on the obstacle",
    "ch09:fig-census": "How many vortices?",
    "ch09:fig-birth": "The first vortex pair",
    "ch10:fig-estimator": "The energy estimator of the friction fails a known-answer test",
    "ch10:fig-library": "The library as audited for this book",
    "ch10:fig-verdicts": "Every criterion the ledger records, by campaign",
    "ch10:fig-bench": "Time per step of the projected Gross--Pitaevskii integrator in several engines",
}


def figures(src):
    """Yield (start, end) of every figure environment (figure or figure*)."""
    for m in re.finditer(r"\\begin\{figure\*?\}", src):
        e = src.find("\\end{figure", m.end())
        if e > 0:
            yield m.start(), e


def main(check_only=False):
    missing, done = [], 0
    # chapter 7 is generated from templates by figures/ch07_build_tex.py: patch the templates too, so a rebuild keeps the short titles
    for tex in sorted((BOOK / "chapters").glob("ch[0-9][0-9].tex")) + sorted((BOOK / "figures").glob("ch07_template_p*.tex")):
        src = tex.read_text(); changed = False
        out, last = [], 0
        for a, b in figures(src):
            env = src[a:b]
            lab = re.search(r"\\label\{([^}]*)\}", env)
            cap = re.search(r"\\caption(\[)?", env)
            if not cap:
                continue
            label = lab.group(1) if lab else "?"
            if cap.group(1):          # already has a short caption
                continue
            if label not in SHORT:
                missing.append(f"{tex.name}: {label}")
                continue
            if check_only:
                continue
            k = a + cap.end()
            out.append(src[last:k]); out.append("[" + SHORT[label] + "]"); last = k
            changed = True; done += 1
        if changed:
            out.append(src[last:]); tex.write_text("".join(out))
    print(f"inserted {done} short captions")
    for m in missing:
        print("NO SHORT CAPTION:", m)
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main("--check" in sys.argv))
