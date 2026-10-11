//! N points in a container, open geometry: `E_int = sum_{i<j} phi(r_ij)` (total, not per particle).
//! The flow is `x' = -grad(E_int + wall/trap)`.
use crate::geom::Cont;
use crate::kernel::Pair;

#[derive(Clone)]
pub struct System {
    pub n: usize,
    pub pair: Pair,
    pub cont: Cont,
    pub kappa: f64,
    /// planted bug for the checker only: 0 none, 1 ordered pairs (energy x2, force x2), 2 flip y force, 3 force x 1.01
    pub bug: u8,
}

impl System {
    pub fn new(n: usize, pair: Pair, cont: Cont, kappa: f64) -> Self {
        System { n, pair, cont, kappa, bug: 0 }
    }

    pub fn e_int(&self, x: &[f64]) -> f64 {
        let mut e = 0.0;
        for i in 0..self.n {
            for j in (i + 1)..self.n {
                let dx = x[2 * i] - x[2 * j];
                let dy = x[2 * i + 1] - x[2 * j + 1];
                e += self.pair.eval((dx * dx + dy * dy).sqrt()).0;
            }
        }
        if self.bug == 1 {
            e *= 2.0;
        }
        e
    }

    pub fn e_wall(&self, x: &[f64]) -> f64 {
        self.cont.energy(x, self.kappa)
    }

    pub fn e_total(&self, x: &[f64]) -> f64 {
        self.e_int(x) + self.e_wall(x)
    }

    /// `f = -grad E_total`
    pub fn force(&self, x: &[f64], f: &mut [f64]) {
        for v in f.iter_mut() {
            *v = 0.0;
        }
        for i in 0..self.n {
            for j in (i + 1)..self.n {
                let dx = x[2 * i] - x[2 * j];
                let dy = x[2 * i + 1] - x[2 * j + 1];
                let r = (dx * dx + dy * dy).sqrt();
                let p1 = self.pair.d1(r);
                let c = -p1 / r;
                f[2 * i] += c * dx;
                f[2 * i + 1] += c * dy;
                f[2 * j] -= c * dx;
                f[2 * j + 1] -= c * dy;
            }
        }
        match self.bug {
            1 => f.iter_mut().for_each(|v| *v *= 2.0),
            2 => (0..self.n).for_each(|i| f[2 * i + 1] = -f[2 * i + 1]),
            3 => f.iter_mut().for_each(|v| *v *= 1.01),
            _ => {}
        }
        self.cont.add_force(x, f, self.kappa);
    }

    /// Hessian of `E_total`, column-major `2n x 2n`
    pub fn hessian(&self, x: &[f64], h: &mut [f64]) {
        let n2 = 2 * self.n;
        for v in h.iter_mut() {
            *v = 0.0;
        }
        for i in 0..self.n {
            for j in (i + 1)..self.n {
                let dx = x[2 * i] - x[2 * j];
                let dy = x[2 * i + 1] - x[2 * j + 1];
                let r = (dx * dx + dy * dy).sqrt();
                let (_, p1, p2) = self.pair.eval(r);
                let (ux, uy) = (dx / r, dy / r);
                let q = p1 / r;
                let hxx = p2 * ux * ux + q * (1.0 - ux * ux);
                let hxy = p2 * ux * uy - q * ux * uy;
                let hyy = p2 * uy * uy + q * (1.0 - uy * uy);
                let (ix, iy, jx, jy) = (2 * i, 2 * i + 1, 2 * j, 2 * j + 1);
                let mut add = |r: usize, c: usize, v: f64| h[c * n2 + r] += v;
                for (a, b, v) in [(ix, ix, hxx), (ix, iy, hxy), (iy, ix, hxy), (iy, iy, hyy)] {
                    add(a, b, v);
                }
                for (a, b, v) in [(jx, jx, hxx), (jx, jy, hxy), (jy, jx, hxy), (jy, jy, hyy)] {
                    add(a, b, v);
                }
                for (a, b, v) in [(ix, jx, -hxx), (ix, jy, -hxy), (iy, jx, -hxy), (iy, jy, -hyy)] {
                    add(a, b, v);
                    add(b, a, v);
                }
            }
        }
        self.cont.add_hessian(x, h, self.kappa);
    }
}
