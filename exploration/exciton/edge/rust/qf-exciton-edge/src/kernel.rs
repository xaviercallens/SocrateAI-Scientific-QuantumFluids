//! Radial pair energies `phi(r)` (unordered-pair energy) with first and second derivatives in `r`.
use std::fs;

#[derive(Clone, Debug)]
pub struct Table {
    pub d: f64,
    pub big_d: f64,
    pub rmax: f64,
    pub width: f64,
    pub deg: usize,
    c0: Vec<f64>, // value coefficients, (deg+1) per interval
    c1: Vec<f64>, // first derivative coefficients (deg per interval, padded to deg+1)
    c2: Vec<f64>,
}

#[derive(Clone, Debug)]
pub enum Pair {
    /// `2/r - 2/sqrt(r^2+d^2)` (ungated bilayer dipole, the phase-1 `Bilayer` kernel with eps = 0)
    Dipole { d: f64 },
    /// `c / r^3` (test kernel for the known answers)
    Riesz3 { c: f64 },
    /// gated: `2/r - 2/sqrt(r^2+d^2) + W(r)`, `W` piecewise Chebyshev, zero beyond `rmax`
    Gated(Table),
}

fn cheb_der(c: &[f64]) -> Vec<f64> {
    let n = c.len() - 1;
    let mut cc = c.to_vec();
    let mut der = vec![0.0; c.len()];
    if n == 0 {
        return der;
    }
    let mut j = n;
    while j > 2 {
        der[j - 1] = 2.0 * j as f64 * cc[j];
        cc[j - 2] += (j as f64 * cc[j]) / (j as f64 - 2.0);
        j -= 1;
    }
    if n > 1 {
        der[1] = 4.0 * cc[2];
    }
    der[0] = cc[1];
    der
}

fn clenshaw(c: &[f64], x: f64) -> f64 {
    let mut b1 = 0.0;
    let mut b2 = 0.0;
    for k in (1..c.len()).rev() {
        let b0 = c[k] + 2.0 * x * b1 - b2;
        b2 = b1;
        b1 = b0;
    }
    c[0] + x * b1 - b2
}

impl Table {
    pub fn load(path: &str) -> Result<Table, String> {
        let text = fs::read_to_string(path).map_err(|e| format!("{path}: {e}"))?;
        let mut lines = text.lines().filter(|l| !l.starts_with('#') && !l.trim().is_empty());
        let head: Vec<&str> = lines.next().ok_or("empty table")?.split_whitespace().collect();
        let big_d: f64 = head[0].parse().map_err(|e| format!("{e}"))?;
        let d: f64 = head[1].parse().map_err(|e| format!("{e}"))?;
        let rmax: f64 = head[2].parse().map_err(|e| format!("{e}"))?;
        let width: f64 = head[3].parse().map_err(|e| format!("{e}"))?;
        let deg: usize = head[4].parse().map_err(|e| format!("{e}"))?;
        let (mut c0, mut c1, mut c2) = (Vec::new(), Vec::new(), Vec::new());
        for l in lines {
            let row: Vec<f64> = l.split_whitespace().map(|s| s.parse::<f64>().unwrap()).collect();
            assert_eq!(row.len(), deg + 1);
            let d1 = cheb_der(&row);
            let d2 = cheb_der(&d1);
            c0.extend_from_slice(&row);
            c1.extend_from_slice(&d1);
            c2.extend_from_slice(&d2);
        }
        Ok(Table { d, big_d, rmax, width, deg, c0, c1, c2 })
    }

    /// `W'` only (the force)
    pub fn w1(&self, r: f64) -> f64 {
        let nint = self.c0.len() / (self.deg + 1);
        let i = ((r / self.width) as usize).min(nint - 1);
        let x = (r - (i as f64 + 0.5) * self.width) / (0.5 * self.width);
        let m = self.deg + 1;
        (2.0 / self.width) * clenshaw(&self.c1[i * m..i * m + m], x)
    }

    /// `(W, W', W'')` at `r < rmax`
    pub fn w(&self, r: f64) -> (f64, f64, f64) {
        let nint = self.c0.len() / (self.deg + 1);
        let i = ((r / self.width) as usize).min(nint - 1);
        let x = (r - (i as f64 + 0.5) * self.width) / (0.5 * self.width);
        let s = 2.0 / self.width;
        let m = self.deg + 1;
        let (a, b, c) = (i * m, i * m + m, 0);
        let _ = c;
        (
            clenshaw(&self.c0[a..b], x),
            s * clenshaw(&self.c1[a..b], x),
            s * s * clenshaw(&self.c2[a..b], x),
        )
    }
}

impl Pair {
    /// `phi'(r)` only (same value as `eval(r).1`)
    pub fn d1(&self, r: f64) -> f64 {
        match self {
            Pair::Riesz3 { c } => -3.0 * c / (r * r * r * r),
            Pair::Dipole { d } => dipole_d1(r, *d),
            Pair::Gated(t) => {
                if r >= t.rmax {
                    0.0
                } else {
                    dipole_d1(r, t.d) + t.w1(r)
                }
            }
        }
    }
    /// `(phi, phi', phi'')`
    pub fn eval(&self, r: f64) -> (f64, f64, f64) {
        match self {
            Pair::Riesz3 { c } => (c / (r * r * r), -3.0 * c / (r * r * r * r), 12.0 * c / (r * r * r * r * r)),
            Pair::Dipole { d } => dipole(r, *d),
            Pair::Gated(t) => {
                if r >= t.rmax {
                    return (0.0, 0.0, 0.0);
                }
                let (p, p1, p2) = dipole(r, t.d);
                let (w, w1, w2) = t.w(r);
                (p + w, p1 + w1, p2 + w2)
            }
        }
    }
}

fn dipole_d1(r: f64, d: f64) -> f64 {
    let s2 = r * r + d * d;
    -2.0 / (r * r) + 2.0 * r / (s2 * s2.sqrt())
}

fn dipole(r: f64, d: f64) -> (f64, f64, f64) {
    let s2 = r * r + d * d;
    let s = s2.sqrt();
    // 2/r - 2/s = 2 d^2 / (r s (s + r))  (no cancellation)
    let p = 2.0 * d * d / (r * s * (s + r));
    let p1 = -2.0 / (r * r) + 2.0 * r / (s2 * s);
    let p2 = 4.0 / (r * r * r) + 2.0 / (s2 * s) - 6.0 * r * r / (s2 * s2 * s);
    (p, p1, p2)
}

/// Kernel by id: `dip`, `r3`, `g3`, `g10` (gated D/d = 3, 10; table in `$QF_TABLE_DIR/table_D<D>.txt`).
pub fn by_id(id: &str) -> Result<Pair, String> {
    match id {
        "dip" => Ok(Pair::Dipole { d: 1.0 }),
        "r3" => Ok(Pair::Riesz3 { c: 1.0 }),
        "g3" | "g10" => {
            let dir = std::env::var("QF_TABLE_DIR").map_err(|_| "QF_TABLE_DIR not set".to_string())?;
            let mut dd = &id[1..];
            if std::env::var("QF_PLANT_TABLE_SWAP").is_ok() {
                dd = if dd == "3" { "10" } else { "3" }; // planted bug (E-d): wrong gate separation
            }
            Ok(Pair::Gated(Table::load(&format!("{dir}/table_D{dd}.txt"))?))
        }
        _ => Err(format!("unknown kernel {id}")),
    }
}
