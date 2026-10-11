//! ETDRK4 / Lawson-RK4 integrators for the driven-dissipative exciton GPE of
//! `docs/designs/EXCITON_FLUID_PHASE3_PREREG.md` (model of `qf-exciton-p1/src/bin/dd.rs`), see
//! `docs/designs/EXCITON_FLUID_ETD_PREREG.md`. Pure Rust, own radix-2 FFT. CVODE (pinned) only as a comparator.
use std::f64::consts::PI;

// ---------------------------------------------------------------- RNG (SplitMix64, as qf-exciton-p1::rng)
pub struct SplitMix64(pub u64);
impl SplitMix64 {
    pub fn next_u64(&mut self) -> u64 {
        self.0 = self.0.wrapping_add(0x9E37_79B9_7F4A_7C15);
        let mut z = self.0;
        z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
        z ^ (z >> 31)
    }
    pub fn uniform(&mut self) -> f64 {
        (self.next_u64() >> 11) as f64 / (1u64 << 53) as f64
    }
}

// ---------------------------------------------------------------- FFT
pub struct Fft {
    pub m: usize,
    rev: Vec<usize>,
    cs: Vec<f64>,
    sn: Vec<f64>,
}

impl Fft {
    pub fn new(m: usize) -> Fft {
        assert!(m.is_power_of_two() && m >= 2);
        let bits = m.trailing_zeros();
        let rev = (0..m).map(|i| ((i as u32).reverse_bits() >> (32 - bits)) as usize).collect();
        let cs = (0..m / 2).map(|j| (2.0 * PI * j as f64 / m as f64).cos()).collect();
        let sn = (0..m / 2).map(|j| -(2.0 * PI * j as f64 / m as f64).sin()).collect(); // forward e^{-i}
        Fft { m, rev, cs, sn }
    }
    /// 1D in place, unnormalised; forward e^{-i}, inverse e^{+i}
    pub fn line(&self, re: &mut [f64], im: &mut [f64], inverse: bool) {
        let m = self.m;
        for i in 0..m {
            let j = self.rev[i];
            if j > i {
                re.swap(i, j);
                im.swap(i, j);
            }
        }
        let sg = if inverse { -1.0 } else { 1.0 };
        let mut len = 2;
        while len <= m {
            let step = m / len;
            let half = len / 2;
            for k in (0..m).step_by(len) {
                for j in 0..half {
                    let wr = self.cs[j * step];
                    let wi = sg * self.sn[j * step];
                    let (a, b) = (k + j, k + j + half);
                    let tr = re[b] * wr - im[b] * wi;
                    let ti = re[b] * wi + im[b] * wr;
                    re[b] = re[a] - tr;
                    im[b] = im[a] - ti;
                    re[a] += tr;
                    im[a] += ti;
                }
            }
            len <<= 1;
        }
    }
    /// 2D in place on row-major m x m arrays; inverse is normalised by 1/m^2.
    pub fn fft2(&self, re: &mut [f64], im: &mut [f64], inverse: bool, br: &mut [f64], bi: &mut [f64]) {
        let m = self.m;
        for x in 0..m {
            self.line(&mut re[x * m..(x + 1) * m], &mut im[x * m..(x + 1) * m], inverse);
        }
        for y in 0..m {
            for x in 0..m {
                br[x] = re[x * m + y];
                bi[x] = im[x * m + y];
            }
            self.line(&mut br[..m], &mut bi[..m], inverse);
            for x in 0..m {
                re[x * m + y] = br[x];
                im[x * m + y] = bi[x];
            }
        }
        if inverse {
            let f = 1.0 / (m * m) as f64;
            re.iter_mut().for_each(|v| *v *= f);
            im.iter_mut().for_each(|v| *v *= f);
        }
    }
}

/// Naive 2D DFT (test only), forward e^{-i}, inverse normalised.
pub fn dft2_naive(m: usize, re: &[f64], im: &[f64], inverse: bool) -> (Vec<f64>, Vec<f64>) {
    let sg = if inverse { 1.0 } else { -1.0 };
    let mut or = vec![0.0; m * m];
    let mut oi = vec![0.0; m * m];
    for kx in 0..m {
        for ky in 0..m {
            let (mut sr, mut si) = (0.0, 0.0);
            for x in 0..m {
                for y in 0..m {
                    let a = sg * 2.0 * PI * (((kx * x + ky * y) % m) as f64) / m as f64;
                    let (c, s) = (a.cos(), a.sin());
                    sr += re[x * m + y] * c - im[x * m + y] * s;
                    si += re[x * m + y] * s + im[x * m + y] * c;
                }
            }
            or[kx * m + ky] = sr;
            oi[kx * m + ky] = si;
        }
    }
    if inverse {
        let f = 1.0 / (m * m) as f64;
        or.iter_mut().for_each(|v| *v *= f);
        oi.iter_mut().for_each(|v| *v *= f);
    }
    (or, oi)
}

// ---------------------------------------------------------------- model
#[derive(Clone, Copy, Debug)]
pub struct Par {
    pub g: f64,
    pub gr: f64,
    pub gamma: f64,
    pub gamma_r: f64,
    pub r: f64,
    pub r_psi: f64, // R as seen by the psi equation (== r unless a bug is planted)
    pub p: f64,
}
impl Par {
    pub fn reg() -> Par {
        Par { g: 0.04, gr: 1.0, gamma: 0.1, gamma_r: 200.0, r: 1.0, r_psi: 1.0, p: 21.0 }
    }
}

pub fn mfreq(i: usize, m: usize) -> i32 {
    if i > m / 2 {
        i as i32 - m as i32
    } else {
        i as i32
    }
}

pub struct Model {
    pub m: usize,
    pub nn: usize,
    pub dx: f64,
    pub k2: Vec<f64>,
    pub v: Vec<f64>,
    pub par: Par,
    pub om: f64,
    pub fft: Fft,
}

pub fn gate(m: usize, dx: f64, v0: f64, sigma: f64) -> Vec<f64> {
    let mut v = vec![0.0; m * m];
    let mf = m as f64;
    for x in 0..m {
        for y in 0..m {
            let ax = (x as f64 - mf / 2.0).abs();
            let ay = (y as f64 - mf / 2.0).abs();
            let dxl = ax.min(mf - ax) * dx;
            let dyl = ay.min(mf - ay) * dx;
            v[x * m + y] = v0 * (-(dxl * dxl + dyl * dyl) / (2.0 * sigma * sigma)).exp();
        }
    }
    v
}

pub fn state_uniform(m: usize, n: f64, nr: f64, noise: f64, seed: u64) -> Vec<f64> {
    let nn = m * m;
    let mut rng = SplitMix64(seed);
    let mut y = vec![0.0; 3 * nn];
    for i in 0..nn {
        y[i] = n.sqrt() * (1.0 + noise * (2.0 * rng.uniform() - 1.0));
    }
    for i in 0..nn {
        y[nn + i] = n.sqrt() * noise * (2.0 * rng.uniform() - 1.0);
    }
    for i in 0..nn {
        y[2 * nn + i] = nr;
    }
    y
}

impl Model {
    pub fn new(m: usize, dx: f64, par: Par, v: Vec<f64>, om: f64) -> Model {
        let nn = m * m;
        let l = m as f64 * dx;
        let mut k2 = vec![0.0; nn];
        for i in 0..m {
            for j in 0..m {
                let kx = 2.0 * PI * mfreq(i, m) as f64 / l;
                let ky = 2.0 * PI * mfreq(j, m) as f64 / l;
                k2[i * m + j] = kx * kx + ky * ky;
            }
        }
        Model { m, nn, dx, k2, v, par, om, fft: Fft::new(m) }
    }
    pub fn kin(&self, re: &[f64], im: &[f64]) -> (Vec<f64>, Vec<f64>) {
        let nn = self.nn;
        let mut pr = re.to_vec();
        let mut pi = im.to_vec();
        let (mut br, mut bi) = (vec![0.0; self.m], vec![0.0; self.m]);
        self.fft.fft2(&mut pr, &mut pi, false, &mut br, &mut bi);
        for i in 0..nn {
            pr[i] *= 0.5 * self.k2[i];
            pi[i] *= 0.5 * self.k2[i];
        }
        self.fft.fft2(&mut pr, &mut pi, true, &mut br, &mut bi);
        (pr, pi)
    }
    /// dd.rs right-hand side in real variables (re psi, im psi, n_R), frame rotating at `om`.
    pub fn rhs_real(&self, y: &[f64], yd: &mut [f64], om: f64, with_decay: bool) {
        let nn = self.nn;
        let p = &self.par;
        let (re, rest) = y.split_at(nn);
        let (im, nr) = rest.split_at(nn);
        let (kr, ki) = self.kin(re, im);
        for i in 0..nn {
            let n = re[i] * re[i] + im[i] * im[i];
            let w = self.v[i] + p.g * n + p.gr * nr[i];
            let hr = kr[i] + w * re[i];
            let hi = ki[i] + w * im[i];
            let gain = 0.5 * (p.r_psi * nr[i] - p.gamma);
            yd[i] = hi + gain * re[i] - om * im[i];
            yd[nn + i] = -hr + gain * im[i] + om * re[i];
            let decay = if with_decay { p.gamma_r } else { 0.0 };
            yd[2 * nn + i] = p.p - (decay + p.r * n) * nr[i];
        }
    }
}

// ---------------------------------------------------------------- spectral state and phi-function coefficients
/// [psi_re, psi_im, nR_re, nR_im] in Fourier space, each length nn.
#[derive(Clone)]
pub struct Sp(pub [Vec<f64>; 4]);
impl Sp {
    pub fn zeros(nn: usize) -> Sp {
        Sp([vec![0.0; nn], vec![0.0; nn], vec![0.0; nn], vec![0.0; nn]])
    }
}

type Cx = (f64, f64);
#[inline]
fn cmul(a: Cx, b: Cx) -> Cx {
    (a.0 * b.0 - a.1 * b.1, a.0 * b.1 + a.1 * b.0)
}
#[inline]
fn cexp(a: Cx) -> Cx {
    let e = a.0.exp();
    (e * a.1.cos(), e * a.1.sin())
}
#[inline]
fn cdiv(a: Cx, b: Cx) -> Cx {
    let d = b.0 * b.0 + b.1 * b.1;
    ((a.0 * b.0 + a.1 * b.1) / d, (a.1 * b.0 - a.0 * b.1) / d)
}

/// e^z, e^{z/2} and the Kassam-Trefethen contour-integral means (32 points, radius 1) of
/// Q = h (e^{z/2}-1)/z, f1 = h (-4 - z + e^z(4 - 3z + z^2))/z^3, f2 = h (2 + z + e^z(-2 + z))/z^3,
/// f3 = h (-4 - 3z - z^2 + e^z(4 - z))/z^3, with z = hL.
#[derive(Clone, Copy, Debug)]
pub struct Phi {
    pub e: Cx,
    pub e2: Cx,
    pub q: Cx,
    pub f1: Cx,
    pub f2: Cx,
    pub f3: Cx,
    /// Krogstad coefficients (exploratory, amendment A1): p1h = (h/2) phi1(z/2), p2h = h phi2(z/2),
    /// p1 = h phi1(z), p2 = h phi2(z), p3 = h phi3(z)
    pub p1h: Cx,
    pub p2h: Cx,
    pub p1: Cx,
    pub p2: Cx,
    pub p3: Cx,
}

/// phi1, phi2, phi3 (z) by contour mean (32 points, radius 1)
fn phis_contour(z0: Cx) -> (Cx, Cx, Cx) {
    const NP: usize = 32;
    let (mut a, mut b, mut c) = ((0.0, 0.0), (0.0, 0.0), (0.0, 0.0));
    for j in 0..NP {
        let th = 2.0 * PI * (j as f64 + 0.5) / NP as f64;
        let z = (z0.0 + th.cos(), z0.1 + th.sin());
        let ez = cexp(z);
        let z2 = cmul(z, z);
        let z3 = cmul(z2, z);
        let t = cdiv((ez.0 - 1.0, ez.1), z);
        a = (a.0 + t.0, a.1 + t.1);
        let t = cdiv((ez.0 - 1.0 - z.0, ez.1 - z.1), z2);
        b = (b.0 + t.0, b.1 + t.1);
        let t = cdiv((ez.0 - 1.0 - z.0 - 0.5 * z2.0, ez.1 - z.1 - 0.5 * z2.1), z3);
        c = (c.0 + t.0, c.1 + t.1);
    }
    let s = 1.0 / NP as f64;
    ((a.0 * s, a.1 * s), (b.0 * s, b.1 * s), (c.0 * s, c.1 * s))
}

pub fn phi_contour(z0: Cx, h: f64) -> Phi {
    const NP: usize = 32;
    let (mut q, mut f1, mut f2, mut f3) = ((0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0));
    for j in 0..NP {
        let th = 2.0 * PI * (j as f64 + 0.5) / NP as f64;
        let z = (z0.0 + th.cos(), z0.1 + th.sin());
        let ez = cexp(z);
        let ezh = cexp((0.5 * z.0, 0.5 * z.1));
        let z2 = cmul(z, z);
        let z3 = cmul(z2, z);
        let t = cdiv((ezh.0 - 1.0, ezh.1), z);
        q = (q.0 + t.0, q.1 + t.1);
        // f1
        let a = cmul(ez, (4.0 - 3.0 * z.0 + z2.0, -3.0 * z.1 + z2.1));
        let t = cdiv((-4.0 - z.0 + a.0, -z.1 + a.1), z3);
        f1 = (f1.0 + t.0, f1.1 + t.1);
        let a = cmul(ez, (-2.0 + z.0, z.1));
        let t = cdiv((2.0 + z.0 + a.0, z.1 + a.1), z3);
        f2 = (f2.0 + t.0, f2.1 + t.1);
        let a = cmul(ez, (4.0 - z.0, -z.1));
        let t = cdiv((-4.0 - 3.0 * z.0 - z2.0 + a.0, -3.0 * z.1 - z2.1 + a.1), z3);
        f3 = (f3.0 + t.0, f3.1 + t.1);
    }
    let s = h / NP as f64;
    let (ph1h, ph2h, _) = phis_contour((0.5 * z0.0, 0.5 * z0.1));
    let (ph1, ph2, ph3) = phis_contour(z0);
    let sc = |a: Cx, f: f64| (a.0 * f, a.1 * f);
    Phi {
        e: cexp(z0),
        e2: cexp((0.5 * z0.0, 0.5 * z0.1)),
        q: (q.0 * s, q.1 * s),
        f1: (f1.0 * s, f1.1 * s),
        f2: (f2.0 * s, f2.1 * s),
        f3: (f3.0 * s, f3.1 * s),
        p1h: sc(ph1h, 0.5 * h),
        p2h: sc(ph2h, h),
        p1: sc(ph1, h),
        p2: sc(ph2, h),
        p3: sc(ph3, h),
    }
}

#[derive(Clone, Copy, PartialEq, Debug)]
pub enum Scheme {
    Etd,
    Law,
    /// Krogstad's ETDRK4 (exploratory, amendment A1)
    Krog,
}

#[derive(Clone, Copy, Debug)]
pub struct Opts {
    pub scheme: Scheme,
    /// true: the reservoir decay -gamma_R is in the exponential part; false: it stays in N (kinetic-only variants)
    pub lin_decay: bool,
    /// planted bugs: 0 none, 2 final combination uses f2 where f3 belongs, 3 kinetic factor 1/4 instead of 1/2 in L only
    pub bug: u8,
}

impl Opts {
    pub fn etd() -> Opts {
        Opts { scheme: Scheme::Etd, lin_decay: true, bug: 0 }
    }
    pub fn law() -> Opts {
        Opts { scheme: Scheme::Law, lin_decay: true, bug: 0 }
    }
    pub fn lawk() -> Opts {
        Opts { scheme: Scheme::Law, lin_decay: false, bug: 0 }
    }
    pub fn etdk() -> Opts {
        Opts { scheme: Scheme::Etd, lin_decay: false, bug: 0 }
    }
    pub fn by_name(s: &str) -> Opts {
        match s {
            "etd" => Opts::etd(),
            "law" => Opts::law(),
            "lawk" => Opts::lawk(),
            "etdk" => Opts::etdk(),
            "krog" => Opts { scheme: Scheme::Krog, lin_decay: true, bug: 0 },
            _ => panic!("scheme name {s}"),
        }
    }
}

struct Coefs {
    psi: Vec<Phi>,
    nr: Vec<Phi>,
}

pub struct Stepper<'a> {
    pub model: &'a Model,
    pub opts: Opts,
    pub h: f64,
    c: Coefs,
    // work
    wr: [Vec<f64>; 4],
    bufr: Vec<f64>,
    bufi: Vec<f64>,
    n0: Sp,
    na: Sp,
    nb: Sp,
    nc: Sp,
    sa: Sp,
    sb: Sp,
    sc: Sp,
}

impl<'a> Stepper<'a> {
    pub fn new(model: &'a Model, opts: Opts, h: f64) -> Stepper<'a> {
        let nn = model.nn;
        let kf = if opts.bug == 3 { 0.25 } else { 0.5 };
        let mut psi = Vec::with_capacity(nn);
        let mut nr = Vec::with_capacity(nn);
        for i in 0..nn {
            psi.push(phi_contour((0.0, h * (-kf * model.k2[i] + model.om)), h));
            let lr = if opts.lin_decay { -model.par.gamma_r } else { 0.0 };
            nr.push(phi_contour((h * lr, 0.0), h));
        }
        Stepper {
            model,
            opts,
            h,
            c: Coefs { psi, nr },
            wr: [vec![0.0; nn], vec![0.0; nn], vec![0.0; nn], vec![0.0; nn]],
            bufr: vec![0.0; model.m],
            bufi: vec![0.0; model.m],
            n0: Sp::zeros(nn),
            na: Sp::zeros(nn),
            nb: Sp::zeros(nn),
            nc: Sp::zeros(nn),
            sa: Sp::zeros(nn),
            sb: Sp::zeros(nn),
            sc: Sp::zeros(nn),
        }
    }

    /// Nonlinear part in Fourier space. The linear part not in the exponential (the -i omega frame is, the decay is
    /// only when `lin_decay`).
    fn nonlin(model: &Model, lin_decay: bool, u: &Sp, out: &mut Sp, w: &mut [Vec<f64>; 4], br: &mut [f64], bi: &mut [f64]) {
        let nn = model.nn;
        let p = &model.par;
        for c in 0..4 {
            w[c].copy_from_slice(&u.0[c]);
        }
        {
            let (a, b) = w.split_at_mut(2);
            let (ar, ai) = a.split_at_mut(1);
            let (brr, bii) = b.split_at_mut(1);
            model.fft.fft2(&mut ar[0], &mut ai[0], true, br, bi);
            model.fft.fft2(&mut brr[0], &mut bii[0], true, br, bi);
        }
        let dec = if lin_decay { 0.0 } else { p.gamma_r };
        for i in 0..nn {
            let (pr, pi, nrv) = (w[0][i], w[1][i], w[2][i]);
            let n = pr * pr + pi * pi;
            let wp = model.v[i] + p.g * n + p.gr * nrv;
            let gain = 0.5 * (p.r_psi * nrv - p.gamma);
            w[0][i] = pr * gain + pi * wp;
            w[1][i] = pi * gain - pr * wp;
            w[2][i] = p.p - (dec + p.r * n) * nrv;
            w[3][i] = 0.0;
        }
        {
            let (a, b) = w.split_at_mut(2);
            let (ar, ai) = a.split_at_mut(1);
            let (brr, bii) = b.split_at_mut(1);
            model.fft.fft2(&mut ar[0], &mut ai[0], false, br, bi);
            model.fft.fft2(&mut brr[0], &mut bii[0], false, br, bi);
        }
        for c in 0..4 {
            out.0[c].copy_from_slice(&w[c]);
        }
    }

    /// One step u -> out.
    pub fn step(&mut self, u: &Sp, out: &mut Sp) {
        let model = self.model;
        let nn = model.nn;
        let h = self.h;
        let ld = self.opts.lin_decay;
        let Stepper { c, wr, bufr, bufi, n0, na, nb, nc, sa, sb, sc, opts, .. } = self;
        Self::nonlin(model, ld, u, n0, wr, bufr, bufi);
        match opts.scheme {
            Scheme::Etd => {
                // a = E2 u + Q N(u)
                for comp in 0..2 {
                    let ph = if comp == 0 { &c.psi } else { &c.nr };
                    let (ir, ii) = (2 * comp, 2 * comp + 1);
                    for i in 0..nn {
                        let uu = (u.0[ir][i], u.0[ii][i]);
                        let nn0 = (n0.0[ir][i], n0.0[ii][i]);
                        let p = &ph[i];
                        let e2u = cmul(p.e2, uu);
                        let qn = cmul(p.q, nn0);
                        sa.0[ir][i] = e2u.0 + qn.0;
                        sa.0[ii][i] = e2u.1 + qn.1;
                    }
                }
                Self::nonlin(model, ld, sa, na, wr, bufr, bufi);
                for comp in 0..2 {
                    let ph = if comp == 0 { &c.psi } else { &c.nr };
                    let (ir, ii) = (2 * comp, 2 * comp + 1);
                    for i in 0..nn {
                        let uu = (u.0[ir][i], u.0[ii][i]);
                        let nna = (na.0[ir][i], na.0[ii][i]);
                        let p = &ph[i];
                        let e2u = cmul(p.e2, uu);
                        let qn = cmul(p.q, nna);
                        sb.0[ir][i] = e2u.0 + qn.0;
                        sb.0[ii][i] = e2u.1 + qn.1;
                    }
                }
                Self::nonlin(model, ld, sb, nb, wr, bufr, bufi);
                for comp in 0..2 {
                    let ph = if comp == 0 { &c.psi } else { &c.nr };
                    let (ir, ii) = (2 * comp, 2 * comp + 1);
                    for i in 0..nn {
                        let a = (sa.0[ir][i], sa.0[ii][i]);
                        let t = (2.0 * nb.0[ir][i] - n0.0[ir][i], 2.0 * nb.0[ii][i] - n0.0[ii][i]);
                        let p = &ph[i];
                        let e2a = cmul(p.e2, a);
                        let qt = cmul(p.q, t);
                        sc.0[ir][i] = e2a.0 + qt.0;
                        sc.0[ii][i] = e2a.1 + qt.1;
                    }
                }
                Self::nonlin(model, ld, sc, nc, wr, bufr, bufi);
                for comp in 0..2 {
                    let ph = if comp == 0 { &c.psi } else { &c.nr };
                    let (ir, ii) = (2 * comp, 2 * comp + 1);
                    for i in 0..nn {
                        let p = &ph[i];
                        let uu = (u.0[ir][i], u.0[ii][i]);
                        let eu = cmul(p.e, uu);
                        let t1 = cmul(p.f1, (n0.0[ir][i], n0.0[ii][i]));
                        let s = (na.0[ir][i] + nb.0[ir][i], na.0[ii][i] + nb.0[ii][i]);
                        let t2 = cmul(p.f2, s);
                        let last = if opts.bug == 2 { p.f2 } else { p.f3 };
                        let t3 = cmul(last, (nc.0[ir][i], nc.0[ii][i]));
                        out.0[ir][i] = eu.0 + t1.0 + 2.0 * t2.0 + t3.0;
                        out.0[ii][i] = eu.1 + t1.1 + 2.0 * t2.1 + t3.1;
                    }
                }
            }
            Scheme::Krog => {
                // a = E2 u + p1h N0
                for comp in 0..2 {
                    let ph = if comp == 0 { &c.psi } else { &c.nr };
                    let (ir, ii) = (2 * comp, 2 * comp + 1);
                    for i in 0..nn {
                        let p = &ph[i];
                        let e2u = cmul(p.e2, (u.0[ir][i], u.0[ii][i]));
                        let t = cmul(p.p1h, (n0.0[ir][i], n0.0[ii][i]));
                        sa.0[ir][i] = e2u.0 + t.0;
                        sa.0[ii][i] = e2u.1 + t.1;
                    }
                }
                Self::nonlin(model, ld, sa, na, wr, bufr, bufi);
                // b = a-stage base + p2h (Na - N0)  (base = E2 u + p1h N0 = sa)
                for comp in 0..2 {
                    let ph = if comp == 0 { &c.psi } else { &c.nr };
                    let (ir, ii) = (2 * comp, 2 * comp + 1);
                    for i in 0..nn {
                        let p = &ph[i];
                        let d = (na.0[ir][i] - n0.0[ir][i], na.0[ii][i] - n0.0[ii][i]);
                        let t = cmul(p.p2h, d);
                        sb.0[ir][i] = sa.0[ir][i] + t.0;
                        sb.0[ii][i] = sa.0[ii][i] + t.1;
                    }
                }
                Self::nonlin(model, ld, sb, nb, wr, bufr, bufi);
                // c = E u + p1 N0 + 2 p2 (Nb - N0)
                for comp in 0..2 {
                    let ph = if comp == 0 { &c.psi } else { &c.nr };
                    let (ir, ii) = (2 * comp, 2 * comp + 1);
                    for i in 0..nn {
                        let p = &ph[i];
                        let eu = cmul(p.e, (u.0[ir][i], u.0[ii][i]));
                        let t1 = cmul(p.p1, (n0.0[ir][i], n0.0[ii][i]));
                        let d = (nb.0[ir][i] - n0.0[ir][i], nb.0[ii][i] - n0.0[ii][i]);
                        let t2 = cmul(p.p2, d);
                        sc.0[ir][i] = eu.0 + t1.0 + 2.0 * t2.0;
                        sc.0[ii][i] = eu.1 + t1.1 + 2.0 * t2.1;
                    }
                }
                Self::nonlin(model, ld, sc, nc, wr, bufr, bufi);
                for comp in 0..2 {
                    let ph = if comp == 0 { &c.psi } else { &c.nr };
                    let (ir, ii) = (2 * comp, 2 * comp + 1);
                    for i in 0..nn {
                        let p = &ph[i];
                        let eu = cmul(p.e, (u.0[ir][i], u.0[ii][i]));
                        let n0v = (n0.0[ir][i], n0.0[ii][i]);
                        let sab = (na.0[ir][i] + nb.0[ir][i], na.0[ii][i] + nb.0[ii][i]);
                        let ncv = (nc.0[ir][i], nc.0[ii][i]);
                        let t1 = cmul(p.p1, n0v);
                        let w2 = (-3.0 * n0v.0 + 2.0 * sab.0 - ncv.0, -3.0 * n0v.1 + 2.0 * sab.1 - ncv.1);
                        let t2 = cmul(p.p2, w2);
                        let w3 = (4.0 * (n0v.0 - sab.0 + ncv.0), 4.0 * (n0v.1 - sab.1 + ncv.1));
                        let t3 = cmul(p.p3, w3);
                        out.0[ir][i] = eu.0 + t1.0 + t2.0 + t3.0;
                        out.0[ii][i] = eu.1 + t1.1 + t2.1 + t3.1;
                    }
                }
            }
            Scheme::Law => {
                // k1 = N0; v2 = E2 (u + h/2 k1)
                for comp in 0..2 {
                    let ph = if comp == 0 { &c.psi } else { &c.nr };
                    let (ir, ii) = (2 * comp, 2 * comp + 1);
                    for i in 0..nn {
                        let t = (u.0[ir][i] + 0.5 * h * n0.0[ir][i], u.0[ii][i] + 0.5 * h * n0.0[ii][i]);
                        let v = cmul(ph[i].e2, t);
                        sa.0[ir][i] = v.0;
                        sa.0[ii][i] = v.1;
                    }
                }
                Self::nonlin(model, ld, sa, na, wr, bufr, bufi); // k2
                for comp in 0..2 {
                    let ph = if comp == 0 { &c.psi } else { &c.nr };
                    let (ir, ii) = (2 * comp, 2 * comp + 1);
                    for i in 0..nn {
                        let e2u = cmul(ph[i].e2, (u.0[ir][i], u.0[ii][i]));
                        sb.0[ir][i] = e2u.0 + 0.5 * h * na.0[ir][i];
                        sb.0[ii][i] = e2u.1 + 0.5 * h * na.0[ii][i];
                    }
                }
                Self::nonlin(model, ld, sb, nb, wr, bufr, bufi); // k3
                for comp in 0..2 {
                    let ph = if comp == 0 { &c.psi } else { &c.nr };
                    let (ir, ii) = (2 * comp, 2 * comp + 1);
                    for i in 0..nn {
                        let eu = cmul(ph[i].e, (u.0[ir][i], u.0[ii][i]));
                        let e2k = cmul(ph[i].e2, (nb.0[ir][i], nb.0[ii][i]));
                        sc.0[ir][i] = eu.0 + h * e2k.0;
                        sc.0[ii][i] = eu.1 + h * e2k.1;
                    }
                }
                Self::nonlin(model, ld, sc, nc, wr, bufr, bufi); // k4
                for comp in 0..2 {
                    let ph = if comp == 0 { &c.psi } else { &c.nr };
                    let (ir, ii) = (2 * comp, 2 * comp + 1);
                    for i in 0..nn {
                        let p = &ph[i];
                        let eu = cmul(p.e, (u.0[ir][i], u.0[ii][i]));
                        let ek1 = cmul(p.e, (n0.0[ir][i], n0.0[ii][i]));
                        let s = (na.0[ir][i] + nb.0[ir][i], na.0[ii][i] + nb.0[ii][i]);
                        let e2s = cmul(p.e2, s);
                        out.0[ir][i] = eu.0 + h / 6.0 * (ek1.0 + 2.0 * e2s.0 + nc.0[ir][i]);
                        out.0[ii][i] = eu.1 + h / 6.0 * (ek1.1 + 2.0 * e2s.1 + nc.0[ii][i]);
                    }
                }
            }
        }
    }

    /// Advance the spectral state by `nsteps` steps.
    pub fn advance(&mut self, model_u: &mut Sp, nsteps: usize) {
        let nn = self.model.nn;
        let mut tmp = Sp::zeros(nn);
        for _ in 0..nsteps {
            self.step(model_u, &mut tmp);
            std::mem::swap(model_u, &mut tmp);
        }
    }
}

impl Model {
    pub fn to_spec(&self, y: &[f64]) -> Sp {
        let nn = self.nn;
        let mut s = Sp::zeros(nn);
        let (mut br, mut bi) = (vec![0.0; self.m], vec![0.0; self.m]);
        s.0[0].copy_from_slice(&y[..nn]);
        s.0[1].copy_from_slice(&y[nn..2 * nn]);
        s.0[2].copy_from_slice(&y[2 * nn..3 * nn]);
        {
            let (a, b) = s.0.split_at_mut(2);
            let (ar, ai) = a.split_at_mut(1);
            let (brr, bii) = b.split_at_mut(1);
            self.fft.fft2(&mut ar[0], &mut ai[0], false, &mut br, &mut bi);
            self.fft.fft2(&mut brr[0], &mut bii[0], false, &mut br, &mut bi);
        }
        s
    }
    pub fn to_real(&self, u: &Sp) -> Vec<f64> {
        let nn = self.nn;
        let mut s = u.clone();
        let (mut br, mut bi) = (vec![0.0; self.m], vec![0.0; self.m]);
        {
            let (a, b) = s.0.split_at_mut(2);
            let (ar, ai) = a.split_at_mut(1);
            let (brr, bii) = b.split_at_mut(1);
            self.fft.fft2(&mut ar[0], &mut ai[0], true, &mut br, &mut bi);
            self.fft.fft2(&mut brr[0], &mut bii[0], true, &mut br, &mut bi);
        }
        let mut y = vec![0.0; 3 * nn];
        y[..nn].copy_from_slice(&s.0[0]);
        y[nn..2 * nn].copy_from_slice(&s.0[1]);
        y[2 * nn..].copy_from_slice(&s.0[2]);
        y
    }
}

// ---------------------------------------------------------------- observables (dd.rs `observe`, without max_j)
#[derive(Clone, Debug)]
pub struct Obs {
    pub mean_n: f64,
    pub mean_nr: f64,
    pub std_n: f64,
    pub omega: f64,
    pub resid: f64,
    pub norm2: f64,
    pub budget_rel: f64,
    pub n_center: f64,
    pub n_corner: f64,
    pub max_psi: f64,
    pub finite: bool,
}

pub fn observe(model: &Model, y: &[f64]) -> Obs {
    let nn = model.nn;
    let m = model.m;
    let finite = y.iter().all(|v| v.is_finite());
    let mut yd = vec![0.0; 3 * nn];
    model.rhs_real(y, &mut yd, 0.0, true);
    let (re, rest) = y.split_at(nn);
    let (im, nr) = rest.split_at(nn);
    let n: Vec<f64> = (0..nn).map(|i| re[i] * re[i] + im[i] * im[i]).collect();
    let norm2: f64 = n.iter().sum();
    let mean_n = norm2 / nn as f64;
    let mean_nr = nr.iter().sum::<f64>() / nn as f64;
    let std_n = (n.iter().map(|v| (v - mean_n) * (v - mean_n)).sum::<f64>() / nn as f64).sqrt();
    let im_ov: f64 = (0..nn).map(|i| re[i] * yd[nn + i] - im[i] * yd[i]).sum();
    let omega = -im_ov / norm2;
    let mut r2 = 0.0;
    for i in 0..nn {
        let a = yd[i] - omega * im[i];
        let b = yd[nn + i] + omega * re[i];
        r2 += a * a + b * b;
    }
    let p = &model.par;
    let gain_budget = nn as f64 * p.p;
    let loss: f64 = (0..nn).map(|i| p.gamma_r * nr[i] + p.gamma * n[i]).sum();
    Obs {
        mean_n,
        mean_nr,
        std_n,
        omega,
        resid: r2.sqrt() / norm2.sqrt(),
        norm2,
        budget_rel: (gain_budget - loss).abs() / gain_budget,
        n_center: n[(m / 2) * m + m / 2],
        n_corner: n[0],
        max_psi: n.iter().cloned().fold(0.0f64, f64::max).sqrt(),
        finite,
    }
}

pub fn obs_json(o: &Obs) -> String {
    format!(
        "\"mean_n\":{:.17e},\"mean_nr\":{:.17e},\"std_n\":{:.6e},\"omega\":{:.17e},\"resid_rel\":{:.6e},\"norm2\":{:.17e},\"budget_rel\":{:.6e},\"n_center\":{:.12e},\"n_corner\":{:.12e},\"max_psi\":{:.6e}",
        o.mean_n, o.mean_nr, o.std_n, o.omega, o.resid, o.norm2, o.budget_rel, o.n_center, o.n_corner, o.max_psi
    )
}

// ---------------------------------------------------------------- helpers
/// E = max|y - ref| / ||ref||_2 (the dd.rs D-e metric)
pub fn err_max_rel(a: &[f64], b: &[f64]) -> f64 {
    let d = a.iter().zip(b).map(|(x, y)| (x - y).abs()).fold(0.0f64, |m, v| if v.is_nan() { f64::INFINITY } else { m.max(v) });
    let nb = b.iter().map(|x| x * x).sum::<f64>().sqrt();
    d / nb
}

/// Run a fixed-step integrator to `t_end` from real-layout `y0`; returns the final real state.
pub fn run_fixed(model: &Model, opts: Opts, h: f64, y0: &[f64], t_end: f64) -> Vec<f64> {
    let mut st = Stepper::new(model, opts, h);
    let mut u = model.to_spec(y0);
    let n = (t_end / h).round() as usize;
    st.advance(&mut u, n);
    model.to_real(&u)
}

pub struct CvFlow {
    pub y: Vec<f64>,
    pub steps: usize,
    pub error: Option<String>,
    pub seconds: f64,
}

/// CVODE (BDF, dense) flow in the rotating frame model.om, chunked at `chunk` time units; `cb` is called after each chunk
/// with (t, y) and may return true to stop.
pub fn cvode_flow(model: &std::sync::Arc<Model>, y0: &[f64], t_end: f64, rtol: f64, atol: f64, chunk: f64, mut cb: impl FnMut(f64, &[f64]) -> bool) -> CvFlow {
    use cvode::{Cvode, Method, Task};
    use nvector::SerialVector;
    let t0 = std::time::Instant::now();
    let md = std::sync::Arc::clone(model);
    let rhs = move |_t: f64, y: &[f64], yd: &mut [f64]| -> Result<(), String> {
        md.rhs_real(y, yd, md.om, true);
        Ok(())
    };
    let mut s = match Cvode::builder(Method::Bdf).rtol(rtol).atol(atol).max_steps(5_000_000).build(rhs, 0.0, SerialVector::from_slice(y0)) {
        Ok(s) => s,
        Err(e) => return CvFlow { y: y0.to_vec(), steps: 0, error: Some(format!("build: {e:?}")), seconds: 0.0 },
    };
    let mut t = 0.0;
    let mut y = y0.to_vec();
    while t < t_end - 1e-12 {
        t = (t + chunk).min(t_end);
        match s.solve(t, Task::Normal) {
            Ok((_, v)) => y = v.to_vec(),
            Err(e) => return CvFlow { y, steps: s.num_steps(), error: Some(format!("solve at t={t}: {e:?}")), seconds: t0.elapsed().as_secs_f64() },
        }
        if cb(t, &y) {
            break;
        }
    }
    CvFlow { y, steps: s.num_steps(), error: None, seconds: t0.elapsed().as_secs_f64() }
}
