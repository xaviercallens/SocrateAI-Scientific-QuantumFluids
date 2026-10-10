//! N points in a rectangular torus `lx × ly`, pair kernel `g(|Δ|²)`, periodic images summed (self-images included).
//!
//! Energy per particle (unordered pairs, the registered convention):
//! `E = (1/2N) Σ_{(i,j,m) ≠ (i,i,0)} g(|x_i − x_j + L∘m|²)  (+ tail)`.
//! `force` returns `−∇(N E)`; `hessian` returns the Hessian of `N E`, column-major `2N × 2N`.
use crate::kernel::Kernel;

#[derive(Clone)]
pub struct Torus {
    pub lx: f64,
    pub ly: f64,
    pub n: usize,
    pub kernel: Kernel,
    pub rc: f64,
    pub tail: f64,
    mx: i32,
    my: i32,
    self_const: f64,
}

impl Torus {
    pub fn new(lx: f64, ly: f64, n: usize, kernel: Kernel, rc: f64, tail: f64) -> Self {
        let mx = (rc / lx + 0.5).ceil() as i32;
        let my = (rc / ly + 0.5).ceil() as i32;
        let kx = (rc / lx).ceil() as i32 + 1;
        let ky = (rc / ly).ceil() as i32 + 1;
        let mut s = 0.0;
        for a in -kx..=kx {
            for b in -ky..=ky {
                if a == 0 && b == 0 {
                    continue;
                }
                let t = (a as f64 * lx).powi(2) + (b as f64 * ly).powi(2);
                if t <= rc * rc {
                    s += kernel.g(t);
                }
            }
        }
        Torus { lx, ly, n, kernel, rc, tail, mx, my, self_const: 0.5 * s }
    }

    #[inline]
    fn min_image(&self, dx: f64, dy: f64) -> (f64, f64) {
        (dx - self.lx * (dx / self.lx).round(), dy - self.ly * (dy / self.ly).round())
    }

    /// Energy per particle (tail included).
    pub fn energy(&self, x: &[f64]) -> f64 {
        let n = self.n;
        let rc2 = self.rc * self.rc;
        let mut e = 0.0;
        for i in 0..n {
            for j in (i + 1)..n {
                let (dx0, dy0) = self.min_image(x[2 * i] - x[2 * j], x[2 * i + 1] - x[2 * j + 1]);
                for ax in -self.mx..=self.mx {
                    let dx = dx0 + ax as f64 * self.lx;
                    for ay in -self.my..=self.my {
                        let dy = dy0 + ay as f64 * self.ly;
                        let t = dx * dx + dy * dy;
                        if t <= rc2 {
                            e += self.kernel.g(t);
                        }
                    }
                }
            }
        }
        e / n as f64 + self.self_const + self.tail
    }

    /// `f = −∇(N E)`
    pub fn force(&self, x: &[f64], f: &mut [f64]) {
        let n = self.n;
        let rc2 = self.rc * self.rc;
        for v in f.iter_mut() {
            *v = 0.0;
        }
        for i in 0..n {
            for j in (i + 1)..n {
                let (dx0, dy0) = self.min_image(x[2 * i] - x[2 * j], x[2 * i + 1] - x[2 * j + 1]);
                let (mut fx, mut fy) = (0.0, 0.0);
                for ax in -self.mx..=self.mx {
                    let dx = dx0 + ax as f64 * self.lx;
                    for ay in -self.my..=self.my {
                        let dy = dy0 + ay as f64 * self.ly;
                        let t = dx * dx + dy * dy;
                        if t <= rc2 {
                            let c = 2.0 * self.kernel.g1(t);
                            fx -= c * dx;
                            fy -= c * dy;
                        }
                    }
                }
                f[2 * i] += fx;
                f[2 * i + 1] += fy;
                f[2 * j] -= fx;
                f[2 * j + 1] -= fy;
            }
        }
    }

    /// Hessian of `N E`, column-major `(2N)×(2N)`: `h[c * 2N + r]`.
    pub fn hessian(&self, x: &[f64], h: &mut [f64]) {
        let n = self.n;
        let n2 = 2 * n;
        let rc2 = self.rc * self.rc;
        for v in h.iter_mut() {
            *v = 0.0;
        }
        for i in 0..n {
            for j in (i + 1)..n {
                let (dx0, dy0) = self.min_image(x[2 * i] - x[2 * j], x[2 * i + 1] - x[2 * j + 1]);
                let (mut hxx, mut hxy, mut hyy) = (0.0, 0.0, 0.0);
                for ax in -self.mx..=self.mx {
                    let dx = dx0 + ax as f64 * self.lx;
                    for ay in -self.my..=self.my {
                        let dy = dy0 + ay as f64 * self.ly;
                        let t = dx * dx + dy * dy;
                        if t <= rc2 {
                            let g1 = self.kernel.g1(t);
                            let g2 = self.kernel.g2(t);
                            hxx += 2.0 * g1 + 4.0 * g2 * dx * dx;
                            hxy += 4.0 * g2 * dx * dy;
                            hyy += 2.0 * g1 + 4.0 * g2 * dy * dy;
                        }
                    }
                }
                let (ix, iy, jx, jy) = (2 * i, 2 * i + 1, 2 * j, 2 * j + 1);
                let mut add = |r: usize, c: usize, v: f64| h[c * n2 + r] += v;
                add(ix, ix, hxx);
                add(ix, iy, hxy);
                add(iy, ix, hxy);
                add(iy, iy, hyy);
                add(jx, jx, hxx);
                add(jx, jy, hxy);
                add(jy, jx, hxy);
                add(jy, jy, hyy);
                add(ix, jx, -hxx);
                add(ix, jy, -hxy);
                add(iy, jx, -hxy);
                add(iy, jy, -hyy);
                add(jx, ix, -hxx);
                add(jx, iy, -hxy);
                add(jy, ix, -hxy);
                add(jy, iy, -hyy);
            }
        }
    }

    /// Reduce coordinates into the fundamental cell.
    pub fn wrap(&self, x: &mut [f64]) {
        for i in 0..self.n {
            x[2 * i] -= self.lx * (x[2 * i] / self.lx).floor();
            x[2 * i + 1] -= self.ly * (x[2 * i + 1] / self.ly).floor();
        }
    }

    /// Smallest minimum-image distance among all pairs (diagnostic).
    pub fn min_distance(&self, x: &[f64]) -> f64 {
        let mut m = f64::INFINITY;
        for i in 0..self.n {
            for j in (i + 1)..self.n {
                let (dx, dy) = self.min_image(x[2 * i] - x[2 * j], x[2 * i + 1] - x[2 * j + 1]);
                m = m.min((dx * dx + dy * dy).sqrt());
            }
        }
        m
    }
}
