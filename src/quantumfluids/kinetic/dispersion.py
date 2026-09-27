"""Certified roots of the linearised Vlasov-Poisson dispersion relation (pre-registration K1).

Units: omega_p = v_th = lambda_D = 1.  For a sum of drifting unit-temperature Maxwellians with weights
w_j and drifts u_j,

    D(omega, k) = 1 + k^-2 * sum_j w_j [ 1 + zeta_j Z(zeta_j) ],   zeta_j = (omega/k - u_j)/sqrt(2),

with Z(zeta) = i sqrt(pi) exp(-zeta^2) erfc(-i zeta), an ENTIRE function, so the formula is already the
analytic continuation to Im(omega) < 0 (Landau's prescription) with no case split.  Z' = -2 (1 + zeta Z).

Certification is by the interval Newton operator in Arb ball arithmetic: for a ball B with midpoint m,

    N(B) = m - D(m) / D'(B).

If N(B) lies in the interior of B then D has exactly one zero in B (and it lies in N(B)).  D(m) is evaluated
on the exact midpoint, D'(B) on the whole ball; every rounding error is inside the balls Arb returns.
What is certified is a zero of THIS formula.  That the formula is the right one for the physics is not
something ball arithmetic can know; it is checked against an independent solver (vlasov.py).
"""
from __future__ import annotations

from dataclasses import dataclass

from flint import acb, arb, ctx

MAXWELLIAN = ((1.0, 0.0),)


def plasma_Z(zeta: acb) -> acb:
    return acb(0, 1) * arb.pi().sqrt() * (-(zeta * zeta)).exp() * (acb(0, -1) * zeta).erfc()


def dispersion(omega: acb, k, beams=MAXWELLIAN) -> acb:
    k = arb(k)
    s = acb(0)
    for w, u in beams:
        zeta = (omega / k - arb(u)) / arb(2).sqrt()
        s += arb(w) * (1 + zeta * plasma_Z(zeta))
    return 1 + s / (k * k)


def dispersion_prime(omega: acb, k, beams=MAXWELLIAN) -> acb:
    """dD/domega.  d/dzeta [1 + zeta Z] = Z + zeta Z' = Z - 2 zeta (1 + zeta Z)."""
    k = arb(k)
    s = acb(0)
    for w, u in beams:
        zeta = (omega / k - arb(u)) / arb(2).sqrt()
        Z = plasma_Z(zeta)
        s += arb(w) * (Z - 2 * zeta * (1 + zeta * Z))
    return s / (k * k) / (k * arb(2).sqrt())


def _ball(mid: acb, radius) -> acb:
    r = arb(0, radius)  # [-radius, radius]
    return acb(mid.real.mid() + r, mid.imag.mid() + r)


def newton_operator(ball: acb, k, beams=MAXWELLIAN) -> acb:
    m = acb(ball.real.mid(), ball.imag.mid())
    return m - dispersion(m, k, beams) / dispersion_prime(ball, k, beams)


def _strict(inner: acb, outer: acb) -> bool:
    # python-flint: a.contains_interior(b) <=> b lies in the interior of a
    return bool(outer.real.contains_interior(inner.real)) and bool(outer.imag.contains_interior(inner.imag))


@dataclass
class CertifiedRoot:
    k: float
    omega: acb          # a ball that provably contains exactly one zero of D
    radius: float       # radius of the ball on which the Newton test succeeded
    certified: bool

    @property
    def omega_r(self) -> float:
        return float(self.omega.real.mid())

    @property
    def gamma(self) -> float:
        return float(self.omega.imag.mid())


def certify(center: complex, radius: float, k, beams=MAXWELLIAN, prec: int = 256) -> CertifiedRoot:
    """Interval-Newton test on the square ball of half-width `radius` about `center`.  No refinement of
    `center` is done here: the caller's point is tested as given, so a wrong guess fails."""
    old = ctx.prec
    ctx.prec = prec
    try:
        B = _ball(acb(center.real, center.imag), radius)
        try:
            N = newton_operator(B, k, beams)
        except ZeroDivisionError:
            return CertifiedRoot(float(k), B, radius, False)
        ok = N.is_finite() and _strict(N, B)
        return CertifiedRoot(float(k), N if ok else B, radius, bool(ok))
    finally:
        ctx.prec = old


def refine(guess: complex, k, beams=MAXWELLIAN, prec: int = 256, steps: int = 60) -> acb:
    """Plain (uncertified) Newton iteration in high precision, to produce a centre worth certifying."""
    old = ctx.prec
    ctx.prec = prec
    try:
        w = acb(guess.real, guess.imag)
        for _ in range(steps):
            w = w - dispersion(w, k, beams) / dispersion_prime(w, k, beams)
            w = acb(w.real.mid(), w.imag.mid())
        return w
    finally:
        ctx.prec = old


def landau_root(k, guess: complex, beams=MAXWELLIAN, prec: int = 256, radius: float = 1e-40) -> CertifiedRoot:
    old = ctx.prec
    ctx.prec = prec
    try:
        w = refine(guess, k, beams, prec)
        B = _ball(w, radius)
        N = newton_operator(B, k, beams)
        ok = N.is_finite() and _strict(N, B)
        return CertifiedRoot(float(k), N if ok else B, radius, bool(ok))
    finally:
        ctx.prec = old
