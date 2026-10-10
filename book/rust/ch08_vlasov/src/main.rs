//! Chapter 8 driver for the crate qf-vlasov1d (collisionless Vlasov-Poisson, 1D1V, electrons on a neutralising
//! background:  df/dt + v df/dx - E df/dv = 0,  dE/dx = 1 - rho).
//!
//! Usage: ch08_vlasov OUTDIR
//! Every run perturbs a spatially uniform background f0(v) by a density wave,  f = f0 (1 + a cos(k x)).
//! Two backgrounds are used:
//!   Maxwell : f0 = exp(-v^2/2)/sqrt(2 pi)                       (unbounded support in v); the density is modulated,
//!             f = f0 (1 + a cos(k x))
//!   Fermi   : f0 ~ 1/(1 + exp((|v| - v0)/w)), normalised to unit density (a degenerate gas: a sea with two
//!             smeared edges at v = +-v0, the one-dimensional "Fermi surface"; v0 = 1, w = 0.1); the EDGES are
//!             displaced, v0 -> v0 (1 + a cos(k x)), so that the perturbation lives where a Fermi gas can have one
//!             (at the Fermi points) and the density is modulated by a factor 1 + a cos(k x) to first order
//!   (1) Maxwell, damping-rate scan: k in K_LIST, nv in {128, 256, 512}, a = 0.01, t_end = 40, dt = 0.1, nx = 32
//!   (2) Fermi, same scan for k in {0.3, 0.5, 0.8}, nv in {512, 1024}
//!   (3) free-streaming control (field off), Maxwell, k = 0.5, nv = 512
//!   (4) phase-space snapshots f(x, v) at selected times, k = 0.5, a = 0.05, nv = 512, both backgrounds
//!   (5) energy / mass bookkeeping for the k = 0.5 runs (series files)
use qf_vlasov1d::*;
use std::f64::consts::PI;
use std::fmt::Write as _;
use std::fs;

#[derive(Clone, Copy)]
enum Bg {
    Maxwell,
    Fermi { v0: f64, w: f64 },
}

fn background(g: &Grid, bg: Bg) -> Vec<f64> {
    let prof: Vec<f64> = (0..g.nv)
        .map(|j| {
            let v = g.v(j);
            match bg {
                Bg::Maxwell => maxwellian(v, 0.0),
                Bg::Fermi { v0, w } => 1.0 / (1.0 + ((v.abs() - v0) / w).exp()),
            }
        })
        .collect();
    let norm: f64 = match bg {
        Bg::Maxwell => 1.0,
        Bg::Fermi { .. } => prof.iter().sum::<f64>() * g.dv(),
    };
    (0..g.nx * g.nv).map(|idx| prof[idx % g.nv] / norm).collect()
}

/// Initial condition on the grid: Maxwell: f0 (1 + a cos(kx)); Fermi: edges displaced, v0 -> v0 (1 + a cos(kx)).
fn initial(g: &Grid, bg: Bg, a: f64) -> Vec<f64> {
    match bg {
        Bg::Maxwell => pulse(&background(g, bg), g, 1, a),
        Bg::Fermi { v0, w } => {
            // normalisation of the UNPERTURBED profile, so that the displaced edges change the density
            let z: f64 = (0..g.nv).map(|j| 1.0 / (1.0 + ((g.v(j).abs() - v0) / w).exp())).sum::<f64>() * g.dv();
            let mut out = vec![0.0; g.nx * g.nv];
            for i in 0..g.nx {
                let v0x = v0 * (1.0 + a * (2.0 * PI / g.l * g.x(i)).cos());
                for j in 0..g.nv {
                    out[i * g.nv + j] = 1.0 / (1.0 + ((g.v(j).abs() - v0x) / w).exp()) / z;
                }
            }
            out
        }
    }
}

struct Series {
    t: Vec<f64>,
    rho: Vec<f64>,
    e: Vec<f64>,
    en: Vec<f64>,
    mass: Vec<f64>,
    rho_re: Vec<f64>, // signed real part of the k-th density Fourier coefficient
    e_re: Vec<f64>,   // signed real part of the k-th field Fourier coefficient
}

fn tag(bg: Bg) -> &'static str {
    match bg {
        Bg::Maxwell => "maxwell",
        Bg::Fermi { .. } => "fermi",
    }
}

#[allow(clippy::too_many_arguments)]
fn evolve(k: f64, nv: usize, a: f64, t_end: f64, dt: f64, field_on: bool, bg: Bg, snaps: &[f64], outdir: &str) -> (Grid, Series) {
    let g = Grid::new(2.0 * PI / k, 32, nv, 6.0);
    let f0 = initial(&g, bg, a);
    let mut s = Series { t: vec![], rho: vec![], e: vec![], en: vec![], mass: vec![], rho_re: vec![], e_re: vec![] };
    let mut snap_todo: Vec<f64> = snaps.to_vec();
    let observe = |t: f64, f: &[f64]| {
        s.t.push(t);
        let (c_rho, c_e) = (mode_amplitude(&density(f, &g), 1), mode_amplitude(&field_from(f, &g), 1));
        s.rho.push(c_rho.norm());
        s.e.push(c_e.norm());
        s.rho_re.push(c_rho.re);
        s.e_re.push(c_e.re);
        s.en.push(energy(f, &g));
        s.mass.push(mass(f, &g));
        if let Some(pos) = snap_todo.iter().position(|&ts| (ts - t).abs() < 0.5 * dt) {
            let ts = snap_todo.remove(pos);
            let bytes: Vec<u8> = f.iter().flat_map(|x| x.to_le_bytes()).collect();
            fs::write(format!("{outdir}/snap_{}_k{k}_nv{nv}_t{ts}.f64", tag(bg)), bytes).unwrap();
        }
    };
    run(f0, &g, dt, t_end, observe, field_on, Vec::<(f64, fn(&[f64]) -> Vec<f64>)>::new());
    (g, s)
}

/// Fit window: from t = 5 to the last time at which |E_1| is still above 3e-5 of its maximum (noise floor guard).
fn fit_window(s: &Series) -> f64 {
    let emax = s.e.iter().cloned().fold(0.0, f64::max);
    let mut t_last = 5.0;
    for i in 0..s.t.len() {
        if s.e[i] > 3e-5 * emax { t_last = s.t[i]; }
    }
    t_last
}

fn write_series(path: &str, s: &Series) {
    let mut csv = String::from("t,rho1,E1,energy,mass,rho1re,E1re\n");
    for i in 0..s.t.len() {
        writeln!(csv, "{:.4},{:.12e},{:.12e},{:.12e},{:.12e},{:.12e},{:.12e}", s.t[i], s.rho[i], s.e[i], s.en[i], s.mass[i], s.rho_re[i], s.e_re[i]).unwrap();
    }
    fs::write(path, csv).unwrap();
}

fn main() {
    let outdir = std::env::args().nth(1).expect("outdir");
    fs::create_dir_all(&outdir).unwrap();
    let fermi = Bg::Fermi { v0: 1.0, w: 0.1 };

    // (1) and (2): rate scans
    for (bg, ks, nvs) in [
        (Bg::Maxwell, vec![0.3, 0.4, 0.5, 0.6, 0.7, 0.8], vec![128usize, 256, 512]),
        (fermi, vec![0.3, 0.5, 0.8], vec![512usize, 1024]),
    ] {
        let mut summary = String::from("k,nv,rate,omega,n_peaks,t_fit_end,wall_s\n");
        for &nv in &nvs {
            for &k in &ks {
                let t0 = std::time::Instant::now();
                let (_g, s) = evolve(k, nv, 0.01, 40.0, 0.1, true, bg, &[], &outdir);
                let t_fit = fit_window(&s);
                let (rate, omega, peaks) = peak_fit(&s.t, &s.e, 5.0, t_fit);
                let wall = t0.elapsed().as_secs_f64();
                writeln!(summary, "{k},{nv},{rate:.9},{omega:.9},{},{t_fit:.1},{wall:.3}", peaks.len()).unwrap();
                if (k - 0.5).abs() < 1e-12 && nv == 512 {
                    write_series(&format!("{outdir}/series_{}_k0.5_nv512.csv", tag(bg)), &s);
                }
                write_series(&format!("{outdir}/scan_{}_k{k}_nv{nv}.csv", tag(bg)), &s);
            }
        }
        fs::write(format!("{outdir}/rates_{}.csv", tag(bg)), summary).unwrap();
    }

    // (3) free-streaming control: field off
    let (g, s) = evolve(0.5, 512, 0.01, 40.0, 0.1, false, Bg::Maxwell, &[], &outdir);
    let mut csv = String::from("t,rho1\n");
    for i in 0..s.t.len() { writeln!(csv, "{:.4},{:.15e}", s.t[i], s.rho[i]).unwrap(); }
    fs::write(format!("{outdir}/series_free_k0.5_nv512.csv"), csv).unwrap();
    println!("recurrence time k=0.5 nv=512: {}", g.recurrence_time(1));

    // (4) snapshots, larger amplitude for the picture
    let snaps = [0.0, 5.0, 10.0, 20.0, 30.0];
    for bg in [Bg::Maxwell, fermi] {
        let (g, s) = evolve(0.5, 512, 0.05, 30.0, 0.1, true, bg, &snaps, &outdir);
        let t_fit = fit_window(&s);
        let (rate, omega, _) = peak_fit(&s.t, &s.e, 5.0, t_fit);
        println!("{} a=0.05 snapshot run: rate {rate:.6} omega {omega:.6}; grid nx {} nv {} L {} vmax {}", tag(bg), g.nx, g.nv, g.l, g.vmax);
        write_series(&format!("{outdir}/series_{}_a0.05_k0.5_nv512.csv", tag(bg)), &s);
    }
}
