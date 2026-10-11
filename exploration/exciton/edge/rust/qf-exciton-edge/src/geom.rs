//! Containers.  Hard walls are a quadratic penalty `kappa/2 * violation^2` per half-plane (polygons) or per
//! particle (disk); the harmonic trap is `k/2 |x|^2`.  Area of the hard-wall containers is `N / rho`.
use crate::rng::SplitMix64;

#[derive(Clone, Debug)]
pub enum Cont {
    Circle { r: f64 },
    /// convex polygon as outward unit normals `n` and offsets `c`: inside iff `n.x <= c` for all
    Poly { nx: Vec<f64>, ny: Vec<f64>, c: Vec<f64>, half_w: f64, half_h: f64 },
    Trap { k: f64, rsample: f64 },
}

fn poly_from_vertices(v: &[(f64, f64)]) -> Cont {
    // vertices counter-clockwise, centroid at origin by construction
    let m = v.len();
    let (mut nx, mut ny, mut c) = (vec![], vec![], vec![]);
    let (mut hw, mut hh) = (0.0f64, 0.0f64);
    for i in 0..m {
        let (x0, y0) = v[i];
        let (x1, y1) = v[(i + 1) % m];
        let (dx, dy) = (x1 - x0, y1 - y0);
        let l = (dx * dx + dy * dy).sqrt();
        let (a, b) = (dy / l, -dx / l);
        nx.push(a);
        ny.push(b);
        c.push(a * x0 + b * y0);
        hw = hw.max(x0.abs());
        hh = hh.max(y0.abs());
    }
    Cont::Poly { nx, ny, c, half_w: hw, half_h: hh }
}

/// Container by id with area `area` (hard walls) or trap strength `k`.
/// ids: disk, square, rect32, rect21, rect31, tri, hex, trap
pub fn by_id(id: &str, area: f64, k: f64) -> Result<Cont, String> {
    let rect = |p: f64, q: f64| {
        let w = (area * p / q).sqrt();
        let h = area / w;
        poly_from_vertices(&[(-w / 2.0, -h / 2.0), (w / 2.0, -h / 2.0), (w / 2.0, h / 2.0), (-w / 2.0, h / 2.0)])
    };
    Ok(match id {
        "disk" => Cont::Circle { r: (area / std::f64::consts::PI).sqrt() },
        "square" => rect(1.0, 1.0),
        "rect32" => rect(3.0, 2.0),
        "rect21" => rect(2.0, 1.0),
        "rect31" => rect(3.0, 1.0),
        "tri" => {
            let s = (4.0 * area / 3.0f64.sqrt()).sqrt();
            let rc = s / 3.0f64.sqrt(); // circumradius
            let v: Vec<(f64, f64)> = (0..3)
                .map(|i| {
                    let a = std::f64::consts::FRAC_PI_2 + i as f64 * 2.0 * std::f64::consts::PI / 3.0;
                    (rc * a.cos(), rc * a.sin())
                })
                .collect();
            poly_from_vertices(&v)
        }
        "hex" => {
            let s = (2.0 * area / (3.0 * 3.0f64.sqrt())).sqrt(); // side = circumradius
            let v: Vec<(f64, f64)> = (0..6)
                .map(|i| {
                    let a = i as f64 * std::f64::consts::PI / 3.0;
                    (s * a.cos(), s * a.sin())
                })
                .collect();
            poly_from_vertices(&v)
        }
        "trap" => Cont::Trap { k, rsample: (area / std::f64::consts::PI).sqrt() },
        _ => return Err(format!("unknown container {id}")),
    })
}

impl Cont {
    /// penalty energy (hard wall) or trap energy
    pub fn energy(&self, x: &[f64], kappa: f64) -> f64 {
        let n = x.len() / 2;
        let mut e = 0.0;
        match self {
            Cont::Circle { r } => {
                for i in 0..n {
                    let s = (x[2 * i] * x[2 * i] + x[2 * i + 1] * x[2 * i + 1]).sqrt() - r;
                    if s > 0.0 {
                        e += 0.5 * kappa * s * s;
                    }
                }
            }
            Cont::Poly { nx, ny, c, .. } => {
                for i in 0..n {
                    for j in 0..c.len() {
                        let s = nx[j] * x[2 * i] + ny[j] * x[2 * i + 1] - c[j];
                        if s > 0.0 {
                            e += 0.5 * kappa * s * s;
                        }
                    }
                }
            }
            Cont::Trap { k, .. } => {
                for i in 0..n {
                    e += 0.5 * k * (x[2 * i] * x[2 * i] + x[2 * i + 1] * x[2 * i + 1]);
                }
            }
        }
        e
    }

    /// `f -= grad`
    pub fn add_force(&self, x: &[f64], f: &mut [f64], kappa: f64) {
        let n = x.len() / 2;
        match self {
            Cont::Circle { r } => {
                for i in 0..n {
                    let rr = (x[2 * i] * x[2 * i] + x[2 * i + 1] * x[2 * i + 1]).sqrt();
                    let s = rr - r;
                    if s > 0.0 {
                        f[2 * i] -= kappa * s * x[2 * i] / rr;
                        f[2 * i + 1] -= kappa * s * x[2 * i + 1] / rr;
                    }
                }
            }
            Cont::Poly { nx, ny, c, .. } => {
                for i in 0..n {
                    for j in 0..c.len() {
                        let s = nx[j] * x[2 * i] + ny[j] * x[2 * i + 1] - c[j];
                        if s > 0.0 {
                            f[2 * i] -= kappa * s * nx[j];
                            f[2 * i + 1] -= kappa * s * ny[j];
                        }
                    }
                }
            }
            Cont::Trap { k, .. } => {
                for i in 0..n {
                    f[2 * i] -= k * x[2 * i];
                    f[2 * i + 1] -= k * x[2 * i + 1];
                }
            }
        }
    }

    /// `h += Hessian`, column-major `2n x 2n`
    pub fn add_hessian(&self, x: &[f64], h: &mut [f64], kappa: f64) {
        let n = x.len() / 2;
        let n2 = 2 * n;
        match self {
            Cont::Circle { r } => {
                for i in 0..n {
                    let rr = (x[2 * i] * x[2 * i] + x[2 * i + 1] * x[2 * i + 1]).sqrt();
                    let s = rr - r;
                    if s > 0.0 {
                        let (ux, uy) = (x[2 * i] / rr, x[2 * i + 1] / rr);
                        let q = kappa * s / rr; // tangential part
                        let (a, b, d) = (
                            kappa * ux * ux + q * (1.0 - ux * ux),
                            kappa * ux * uy - q * ux * uy,
                            kappa * uy * uy + q * (1.0 - uy * uy),
                        );
                        h[(2 * i) * n2 + 2 * i] += a;
                        h[(2 * i + 1) * n2 + 2 * i] += b;
                        h[(2 * i) * n2 + 2 * i + 1] += b;
                        h[(2 * i + 1) * n2 + 2 * i + 1] += d;
                    }
                }
            }
            Cont::Poly { nx, ny, c, .. } => {
                for i in 0..n {
                    for j in 0..c.len() {
                        let s = nx[j] * x[2 * i] + ny[j] * x[2 * i + 1] - c[j];
                        if s > 0.0 {
                            h[(2 * i) * n2 + 2 * i] += kappa * nx[j] * nx[j];
                            h[(2 * i + 1) * n2 + 2 * i] += kappa * nx[j] * ny[j];
                            h[(2 * i) * n2 + 2 * i + 1] += kappa * nx[j] * ny[j];
                            h[(2 * i + 1) * n2 + 2 * i + 1] += kappa * ny[j] * ny[j];
                        }
                    }
                }
            }
            Cont::Trap { k, .. } => {
                for i in 0..n {
                    h[(2 * i) * n2 + 2 * i] += k;
                    h[(2 * i + 1) * n2 + 2 * i + 1] += k;
                }
            }
        }
    }

    /// depth inside (positive inside; larger = deeper); trap: minus the distance from the origin
    pub fn depth(&self, x: f64, y: f64) -> f64 {
        match self {
            Cont::Circle { r } => r - (x * x + y * y).sqrt(),
            Cont::Poly { nx, ny, c, .. } => {
                let mut m = f64::INFINITY;
                for j in 0..c.len() {
                    m = m.min(c[j] - (nx[j] * x + ny[j] * y));
                }
                m
            }
            Cont::Trap { .. } => -(x * x + y * y).sqrt(),
        }
    }

    pub fn is_wall(&self) -> bool {
        !matches!(self, Cont::Trap { .. })
    }

    /// largest violation (>= 0) over all particles: how far the penalty configuration sits outside the wall
    pub fn max_violation(&self, x: &[f64]) -> f64 {
        if !self.is_wall() {
            return 0.0;
        }
        let mut m = 0.0f64;
        for i in 0..x.len() / 2 {
            m = m.max(-self.depth(x[2 * i], x[2 * i + 1]));
        }
        m
    }

    /// bounding half-extent for sampling
    fn bbox(&self) -> (f64, f64) {
        match self {
            Cont::Circle { r } => (*r, *r),
            Cont::Poly { half_w, half_h, .. } => (*half_w, *half_h),
            Cont::Trap { rsample, .. } => (*rsample, *rsample),
        }
    }

    /// uniform point inside (trap: inside the sampling disk), by rejection
    pub fn sample(&self, rng: &mut SplitMix64) -> (f64, f64) {
        let (hw, hh) = self.bbox();
        loop {
            let x = (2.0 * rng.uniform() - 1.0) * hw;
            let y = (2.0 * rng.uniform() - 1.0) * hh;
            let ok = match self {
                Cont::Trap { rsample, .. } => x * x + y * y <= rsample * rsample,
                _ => self.depth(x, y) >= 0.0,
            };
            if ok {
                return (x, y);
            }
        }
    }
}
