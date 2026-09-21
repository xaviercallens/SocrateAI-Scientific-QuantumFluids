"""K1 of docs/designs/KINETIC_TDA_PREREG.md: certified Landau roots, and the negative control."""
from flint import ctx
from quantumfluids.kinetic.dispersion import landau_root, certify

ctx.prec = 256
print("K1  certified least-damped Landau root, Maxwellian")
for k, g in [(0.3, 1.16 - 0.0126j), (0.4, 1.285 - 0.066j), (0.5, 1.4156 - 0.1533j)]:
    r = landau_root(k, g, radius=1e-40)
    print(f"  k={k}: certified={r.certified}  omega_r={r.omega.real.str(40)}  gamma={r.omega.imag.str(40)}")
r = landau_root(0.5, 1.4156 - 0.1533j, radius=1e-40)
ok = r.certified and round(r.omega_r, 4) == 1.4156 and round(r.gamma, 4) == -0.1534 or round(r.gamma, 4) == -0.1533
print("  midpoint rounds to:", round(r.omega_r, 4), round(r.gamma, 4), "(literature: 1.4156, -0.1533 / Canosa -0.15336)")
print("K1  negative control: ball radius 1e-3 about 1.4156-0.1433i must NOT certify")
n = certify(1.4156 - 0.1433j, 1e-3, 0.5)
print("  certified =", n.certified, "->", "PASS (rejected)" if not n.certified else "FAIL: control certified a root")
print("K1  positive sanity: same radius about the true root must certify")
p = certify(complex(r.omega_r, r.gamma), 1e-3, 0.5)
print("  certified =", p.certified)
