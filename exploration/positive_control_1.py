#!/usr/bin/env python3
"""Positive Control #1 -- docs/designs/M2_W4_DISPERSIVE_SHELL.md section 6.

  "at D = 0 with real initial data, the complexified model must reproduce
   exploration/dyadic_cascade.py's numbers bit-for-bit up to integrator
   round-off, because section 2b showed the reduction is exact."

Compares this repo's complexified integrator against MechanicaFluidorum's
independently-written reference implementation (numba index loops vs. our
vectorised numpy), using that repo's own published CSV as the reference.

Runtime ~10 min (pure numpy, ~2.4M RK4 steps). Not a pytest test for that
reason; the fast structural pieces of the same claim ARE unit-tested, in
tests/test_shell_dynamics.py (exact reduction, exact reality-invariance)
and tests/test_integrate.py (step-size rule agreement).

Run:  PYTHONPATH=src python3 exploration/positive_control_1.py
Last run 2026-08-14: PASS, worst relative difference 0.00e+00 on all 9
configurations, for both sup_Omega and E_final. Output archived alongside
this file as positive_control_1.out.
"""

import csv
import os
import sys

MF_CSV = os.environ.get(
    "MF_CSV",
    "/home/xavkal/xdev/SocrateAI-Scientific-MechanicaFluidorum/data/dyadic_omega_sup.csv",
)

# We compare against sup_Omega as MechanicaFluidorum's _simulate actually
# computes it -- the MAX convention, not the sum its docstring defines.
# See docs/DEFECT_REPORT_MF_ENSTROPHY.md. Audit ruling O1 is why we have
# both conventions available to make this comparison at all.
CONVENTION = "max"

# N=8 only: N>=12 requires 1.7e7+ RK4 steps, which is a numba-scale run.
# N=8 exercises every code path and is sufficient to validate the claim.
N_LIMIT = 8


def main() -> int:
    from quantumfluids.w4_shell_model.integrate import integrate

    if not os.path.exists(MF_CSV):
        print(f"reference CSV not found: {MF_CSV}", file=sys.stderr)
        print("set MF_CSV to MechanicaFluidorum's data/dyadic_omega_sup.csv", file=sys.stderr)
        return 2

    with open(MF_CSV) as f:
        ref = {
            (int(r["N"]), float(r["nu"]), r["profile"]): r
            for r in csv.DictReader(f)
            if r["status"] == "OK" and int(r["N"]) == N_LIMIT
        }

    if not ref:
        print(f"no usable OK rows at N={N_LIMIT} in {MF_CSV}", file=sys.stderr)
        return 2

    print("POSITIVE CONTROL #1  (memo section 6): D=0, real data, "
          f"N={N_LIMIT}, {CONVENTION.upper()} convention")
    print(f"Reference: {MF_CSV}")
    print()
    print(f"{'nu':>7} {'prof':>5} {'MF sup_Omega':>16} {'ours':>16} "
          f"{'rel.diff':>11}   {'E_final rel.diff':>16}")
    print("-" * 90)

    worst_om = worst_e = 0.0
    for (N, nu, prof), r in sorted(ref.items()):
        run = integrate(N=N, nu=nu, D=0.0, profile=prof)
        ours = run.sup_enstrophy_max if CONVENTION == "max" else run.sup_enstrophy_sum
        mf_om, mf_e = float(r["sup_Omega"]), float(r["E_final"])
        d_om = abs(ours - mf_om) / abs(mf_om)
        d_e = abs(run.energy_final - mf_e) / abs(mf_e)
        worst_om, worst_e = max(worst_om, d_om), max(worst_e, d_e)
        print(f"{nu:>7} {prof:>5} {mf_om:>16.10f} {ours:>16.10f} "
              f"{d_om:>11.2e}   {d_e:>16.2e}")

    ok = worst_om < 1e-9 and worst_e < 1e-9
    print()
    print(f"worst relative difference: sup_Omega {worst_om:.3e}   E_final {worst_e:.3e}")
    print("POSITIVE CONTROL #1:", "PASS" if ok else "FAIL")
    print()
    print("Why the agreement is EXACT rather than merely close: k_n = 2^n are exact")
    print("powers of two, so multiplying by them only shifts the IEEE754 exponent and")
    print("leaves the mantissa untouched. The two implementations associate their")
    print("products differently -- (k*a)*a here, k*(a*a) there -- which for a generic")
    print("k would differ at ~1e-14, but for a power of two is bit-identical. A shell")
    print("model with spacing lambda != 2 would NOT reproduce exactly, and this")
    print("control would then need a tolerance rather than an equality.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
