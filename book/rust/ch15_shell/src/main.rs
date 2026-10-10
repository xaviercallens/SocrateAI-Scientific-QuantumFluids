//! Driver for the chapter "Quantum Turbulence: Cascades in a Quantum Fluid" (book file ch15).
//! The dyadic shell model, wavenumbers k_n = 2^n, shells n = 0..N, boundary values a_{-1} = a_{N+1} = 0.
//!
//! Subcommands (output is CSV or plain text; the figure scripts book/figures/ch15_*.py read it):
//!
//!   probe
//!       CVODE Adams on y' = -y, y(0) = 1, to t = 10 at rtol 1e-8, atol 1e-14.  The right-hand-side count must be
//!       below 5000; the first-order Adams of the builds before 2026-09-28 needs far more (book, appendix B).
//!
//!   forced N nu f tend nout rtol atol series.csv final.csv
//!       The REAL forced viscous dyadic model
//!           da_n/dt = k_{n-1} a_{n-1}^2 - k_n a_n a_{n+1} - nu k_n^2 a_n + f delta_{n0},
//!       integrated by CVODE (BDF, analytic tridiagonal Jacobian) from a = 0 to t = tend, output at nout equal steps.
//!       series.csv: t, E, Omega, injection f a_0, dissipation nu sum k^2 a^2, flux through seams 0 and N/2.
//!       final.csv : n, k_n, a_n, flux Pi_n = k_n a_n^2 a_{n+1}, dissipation in shells 0..n, residual da_n/dt.
//!
//!   crosscheck out.csv
//!       The nine (nu, profile) configurations of qf-shell-cascade's positive control (N = 8, D = 0, T = 10, real
//!       data): the crate's RK4 `integrate` and CVODE (BDF, analytic Jacobian) on the same model, both against the
//!       reference values that the crate's test file transcribes from MechanicaFluidorum's data/dyadic_omega_sup.csv.
//!
//!   conserv N D T nens seed mode trace_every trace.csv ens.csv
//!       The COMPLEXIFIED model of qf-shell-cascade (its `rhs`, nu = 0, dispersion D) from profile P3
//!       (|a_0| = 1, |a_1| = 1/2, all other shells 0).  mode = random: independent uniform phases on a_0 and a_1, one
//!       draw per ensemble member; mode = real: no phases (one member).  Classical RK4 with the crate's step rule
//!       dt = 0.1/(D k_N^2 + k_N).  Per member: H(0), the time averages of |a_n|^2 and of
//!       Omega_sum = (1/2) sum k_n^2 |a_n|^2 over [T/2, T], and the largest relative drift of the two invariants
//!           E = (1/2) sum |a_n|^2,     H = sum_n 2^-n [ D k_n^2 |a_n|^2 + k_n Im(conj(a_n)^2 a_{n+1}) ].
//!       trace.csv: member 0, every trace_every steps (t, |a_n|^2 for every n, E, H, Omega_sum, max |Im a_n|).
use cvode::{Cvode, DenseMat, Method, Task};
use num_complex::Complex64;
use nvector::SerialVector;
use qf_shell_cascade as qsc;
use std::f64::consts::PI;
use std::fmt::Write as _;
use std::fs;
use std::time::Instant;

fn kvec(n_max: usize) -> Vec<f64> {
    (0..=n_max).map(|n| 2f64.powi(n as i32)).collect()
}

// ------------------------------------------------------------------------------------------------ probe
fn probe() {
    let mut calls = 0usize;
    let rhs = |_t: f64, y: &[f64], yd: &mut [f64]| -> Result<(), String> {
        yd[0] = -y[0];
        Ok(())
    };
    let counted = |t: f64, y: &[f64], yd: &mut [f64]| -> Result<(), String> {
        calls += 1;
        rhs(t, y, yd)
    };
    let mut cv = Cvode::builder(Method::Adams).rtol(1e-8).atol(1e-14).max_steps(1_000_000)
        .build(counted, 0.0, SerialVector::from_slice(&[1.0])).expect("build");
    let (_, y) = cv.solve(10.0, Task::Normal).expect("solve");
    let y10 = y[0];
    let relerr = (y10 - (-10f64).exp()).abs() / (-10f64).exp();
    let steps = cv.num_steps();
    let nfe = cv.num_rhs_evals();
    drop(cv);
    println!("PROBE adams y'=-y t=10 rtol=1e-8 atol=1e-14 rhs_calls={calls} num_rhs_evals={nfe} steps={steps} relerr={relerr:.3e} pass={}",
             calls < 5000);
}

// ------------------------------------------------------------------------------------------------ forced (CVODE BDF)
fn dyadic_rhs(k: &[f64], nu: f64, f: f64, y: &[f64], yd: &mut [f64]) {
    let m = y.len();
    for n in 0..m {
        let inflow = if n >= 1 { k[n - 1] * y[n - 1] * y[n - 1] } else { 0.0 };
        let outflow = if n + 1 < m { k[n] * y[n] * y[n + 1] } else { 0.0 };
        yd[n] = inflow - outflow - nu * k[n] * k[n] * y[n] + if n == 0 { f } else { 0.0 };
    }
}

fn dyadic_jac(k: &[f64], nu: f64, y: &[f64], jm: &mut DenseMat) {
    // column-major: jm.cols[j][i] = d f_i / d y_j
    let m = y.len();
    for col in 0..m {
        for row in 0..m {
            jm.cols[col][row] = 0.0;
        }
    }
    for n in 0..m {
        if n >= 1 {
            jm.cols[n - 1][n] = 2.0 * k[n - 1] * y[n - 1];
        }
        jm.cols[n][n] = -nu * k[n] * k[n] - if n + 1 < m { k[n] * y[n + 1] } else { 0.0 };
        if n + 1 < m {
            jm.cols[n + 1][n] = -k[n] * y[n];
        }
    }
}

fn forced(a: &[String]) {
    let n_max: usize = a[0].parse().unwrap();
    let nu: f64 = a[1].parse().unwrap();
    let f: f64 = a[2].parse().unwrap();
    let tend: f64 = a[3].parse().unwrap();
    let nout: usize = a[4].parse().unwrap();
    let rtol: f64 = a[5].parse().unwrap();
    let atol: f64 = a[6].parse().unwrap();
    let (series_out, final_out) = (&a[7], &a[8]);
    let k = kvec(n_max);
    let m = n_max + 1;
    let (k1, k2) = (k.clone(), k.clone());
    let rhs = move |_t: f64, y: &[f64], yd: &mut [f64]| -> Result<(), String> {
        dyadic_rhs(&k1, nu, f, y, yd);
        Ok(())
    };
    let jac = move |_t: f64, y: &[f64], jm: &mut DenseMat| -> Result<(), String> {
        dyadic_jac(&k2, nu, y, jm);
        Ok(())
    };
    let mut cv = Cvode::builder(Method::Bdf).rtol(rtol).atol(atol).max_steps(50_000_000).jacobian(jac)
        .build(rhs, 0.0, SerialVector::from_slice(&vec![0.0; m])).expect("build");
    let t0 = Instant::now();
    let mut csv = String::from("t,E,Omega,injection,dissipation,flux_seam0,flux_seam_mid\n");
    let mid = n_max / 2;
    let mut last = vec![0.0; m];
    for j in 1..=nout {
        let tout = tend * j as f64 / nout as f64;
        let (t, y) = cv.solve(tout, Task::Normal).unwrap_or_else(|e| panic!("solve to {tout}: {e:?}"));
        let e = 0.5 * y.iter().map(|x| x * x).sum::<f64>();
        let om = 0.5 * y.iter().zip(&k).map(|(x, kn)| kn * kn * x * x).sum::<f64>();
        let diss = nu * y.iter().zip(&k).map(|(x, kn)| kn * kn * x * x).sum::<f64>();
        let fl0 = k[0] * y[0] * y[0] * y[1];
        let flm = k[mid] * y[mid] * y[mid] * y[mid + 1];
        writeln!(csv, "{t:.6},{e:.15e},{om:.15e},{:.15e},{diss:.15e},{fl0:.15e},{flm:.15e}", f * y[0]).unwrap();
        last.copy_from_slice(y);
    }
    let wall = t0.elapsed().as_secs_f64();
    fs::write(series_out, csv).unwrap();
    let mut yd = vec![0.0; m];
    dyadic_rhs(&k, nu, f, &last, &mut yd);
    let mut fin = String::from("n,k,a,flux,diss_cum,residual\n");
    let mut cum = 0.0;
    for n in 0..m {
        cum += nu * k[n] * k[n] * last[n] * last[n];
        let flux = if n + 1 < m { k[n] * last[n] * last[n] * last[n + 1] } else { 0.0 };
        writeln!(fin, "{n},{:.1},{:.17e},{flux:.17e},{cum:.17e},{:.6e}", k[n], last[n], yd[n]).unwrap();
    }
    fs::write(final_out, fin).unwrap();
    let inj = f * last[0];
    let diss = nu * last.iter().zip(&k).map(|(x, kn)| kn * kn * x * x).sum::<f64>();
    let resid = yd.iter().map(|x| x.abs()).fold(0.0, f64::max);
    let dt_rk4 = 0.1 / (nu * k[n_max] * k[n_max] + k[n_max]);
    println!("FORCED N={n_max} nu={nu:e} f={f} tend={tend} rtol={rtol:e} atol={atol:e} steps={} rhs_evals={} wall_s={wall:.3} \
              injection={inj:.12e} dissipation={diss:.12e} max_residual={resid:.3e} rk4_rule_dt={dt_rk4:.3e} rk4_rule_steps={:.3e}",
             cv.num_steps(), cv.num_rhs_evals(), (tend / dt_rk4).ceil());
}

// ------------------------------------------------------------------------------------------------ crosscheck
/// (nu, profile, MF sup_Omega_max, MF E_final), N = 8, D = 0, T = 10: transcribed from
/// qf-shell-cascade/tests/positive_control.rs, which transcribes MechanicaFluidorum's data/dyadic_omega_sup.csv.
const REFERENCE: &[(f64, qsc::Profile, f64, f64)] = &[
    (0.1, qsc::Profile::P1, 0.5416451354760369, 0.002382018155692759),
    (0.1, qsc::Profile::P2, 0.8753841785180844, 0.0022060904845584814),
    (0.1, qsc::Profile::P3, 0.9011104739704103, 0.0020975826698934026),
    (0.01, qsc::Profile::P1, 6.662633302097537, 0.01146406572793716),
    (0.01, qsc::Profile::P2, 7.865239231572015, 0.010697621299224658),
    (0.01, qsc::Profile::P3, 9.804893760201573, 0.010343502262071154),
    (0.001, qsc::Profile::P1, 70.87959161476942, 0.017540018047529218),
    (0.001, qsc::Profile::P2, 73.51748113068476, 0.016451811179123255),
    (0.001, qsc::Profile::P3, 115.75863351411745, 0.01595711295041411),
];

fn crosscheck(a: &[String]) {
    let out = &a[0];
    let n_max = 8usize;
    let k = kvec(n_max);
    let mut csv = String::from("nu,profile,ref_sup_omega_max,ref_E_final,crate_sup_omega_max,crate_E_final,crate_steps,crate_wall_s,\
                                cvode_sup_omega_max_sampled,cvode_E_final,cvode_steps,cvode_rhs_evals,cvode_wall_s\n");
    for &(nu, prof, ref_om, ref_e) in REFERENCE {
        let t0 = Instant::now();
        let run = qsc::integrate(n_max, nu, 0.0, prof, 10.0, None, None, None, None).expect("crate integrate");
        let crate_wall = t0.elapsed().as_secs_f64();
        // CVODE BDF on the same (real, unforced) model
        let y0 = qsc::make_profile(prof, n_max);
        let (k1, k2) = (k.clone(), k.clone());
        let rhs = move |_t: f64, y: &[f64], yd: &mut [f64]| -> Result<(), String> {
            dyadic_rhs(&k1, nu, 0.0, y, yd);
            Ok(())
        };
        let jac = move |_t: f64, y: &[f64], jm: &mut DenseMat| -> Result<(), String> {
            dyadic_jac(&k2, nu, y, jm);
            Ok(())
        };
        let mut cv = Cvode::builder(Method::Bdf).rtol(1e-11).atol(1e-15).max_steps(50_000_000).jacobian(jac)
            .build(rhs, 0.0, SerialVector::from_slice(&y0)).expect("build");
        let t1 = Instant::now();
        let omax = |y: &[f64]| y.iter().zip(&k).map(|(x, kn)| 0.5 * kn * kn * x * x).fold(f64::NEG_INFINITY, f64::max);
        let mut sup_om = omax(&y0);
        let nsamp = 20_000;
        let mut e_final = 0.0;
        for j in 1..=nsamp {
            let tout = 10.0 * j as f64 / nsamp as f64;
            let (_, y) = cv.solve(tout, Task::Normal).expect("cvode solve");
            sup_om = sup_om.max(omax(y));
            if j == nsamp {
                e_final = 0.5 * y.iter().map(|x| x * x).sum::<f64>();
            }
        }
        let cv_wall = t1.elapsed().as_secs_f64();
        writeln!(csv, "{nu},{prof:?},{ref_om:.17e},{ref_e:.17e},{:.17e},{:.17e},{},{crate_wall:.3},{sup_om:.17e},{e_final:.17e},{},{},{cv_wall:.3}",
                 run.sup_enstrophy_max, run.energy_final, run.steps, cv.num_steps(), cv.num_rhs_evals()).unwrap();
        println!("CROSS nu={nu} {prof:?}: crate sup_om rel {:.2e} E rel {:.2e} ({} steps) | cvode sup_om(sampled) rel {:.2e} E rel {:.2e} ({} steps)",
                 (run.sup_enstrophy_max - ref_om).abs() / ref_om, (run.energy_final - ref_e).abs() / ref_e, run.steps,
                 (sup_om - ref_om).abs() / ref_om, (e_final - ref_e).abs() / ref_e, cv.num_steps());
    }
    fs::write(out, csv).unwrap();
}

// ------------------------------------------------------------------------------------------------ conserv (crate rhs, RK4)
struct Xorshift64(u64);
impl Xorshift64 {
    fn new(seed: u64) -> Self {
        Xorshift64(seed ^ 0x2545F4914F6CDD1D)
    }
    fn next_u64(&mut self) -> u64 {
        let mut x = self.0;
        x ^= x << 13;
        x ^= x >> 7;
        x ^= x << 17;
        self.0 = x;
        x.wrapping_mul(0x2545F4914F6CDD1D)
    }
    fn uniform(&mut self) -> f64 {
        (self.next_u64() >> 11) as f64 / (1u64 << 53) as f64
    }
}

fn invariants(a: &[Complex64], k: &[f64], d: f64) -> (f64, f64, f64) {
    let e = qsc::energy(a);
    let mut h = 0.0;
    for n in 0..a.len() {
        let w = 0.5f64.powi(n as i32);
        h += w * d * k[n] * k[n] * a[n].norm_sqr();
        if n + 1 < a.len() {
            h += w * k[n] * (a[n].conj() * a[n].conj() * a[n + 1]).im;
        }
    }
    (e, h, qsc::enstrophy_sum(a, k))
}

fn rk4_step(a: &mut [Complex64], k: &[f64], d: f64, h: f64) {
    let k1 = qsc::rhs(a, k, 0.0, d);
    let a2: Vec<Complex64> = a.iter().zip(&k1).map(|(x, y)| x + 0.5 * h * y).collect();
    let k2 = qsc::rhs(&a2, k, 0.0, d);
    let a3: Vec<Complex64> = a.iter().zip(&k2).map(|(x, y)| x + 0.5 * h * y).collect();
    let k3 = qsc::rhs(&a3, k, 0.0, d);
    let a4: Vec<Complex64> = a.iter().zip(&k3).map(|(x, y)| x + h * y).collect();
    let k4 = qsc::rhs(&a4, k, 0.0, d);
    for n in 0..a.len() {
        a[n] += (h / 6.0) * (k1[n] + 2.0 * k2[n] + 2.0 * k3[n] + k4[n]);
    }
}

fn conserv(a: &[String]) {
    let n_max: usize = a[0].parse().unwrap();
    let d: f64 = a[1].parse().unwrap();
    let t_end: f64 = a[2].parse().unwrap();
    let nens: usize = a[3].parse().unwrap();
    let seed: u64 = a[4].parse().unwrap();
    let mode = a[5].as_str();
    let trace_every: u64 = a[6].parse().unwrap();
    let (trace_out, ens_out) = (&a[7], &a[8]);
    let k = kvec(n_max);
    let m = n_max + 1;
    let dt = qsc::step_size(n_max, 0.0, d);
    let steps = (t_end / dt).ceil() as u64;
    let h = t_end / steps as f64;
    let mut rng = Xorshift64::new(seed);
    let mut trace = String::from("t");
    for n in 0..m {
        write!(trace, ",p{n}").unwrap();
    }
    trace.push_str(",E,H,Omega,max_abs_im\n");
    let mut ens = String::from("member,phi0,phi1,E0,H0");
    for n in 0..m {
        write!(ens, ",mean_p{n}").unwrap();
    }
    ens.push_str(",mean_Omega,max_rel_drift_E,max_abs_drift_H,max_abs_im\n");
    let t0 = Instant::now();
    let members = if mode == "real" { 1 } else { nens };
    for mem in 0..members {
        let (phi0, phi1) = if mode == "real" { (0.0, 0.0) } else { (2.0 * PI * rng.uniform(), 2.0 * PI * rng.uniform()) };
        let mut st = vec![Complex64::new(0.0, 0.0); m];
        st[0] = Complex64::from_polar(1.0, phi0);
        st[1] = Complex64::from_polar(0.5, phi1);
        let (e0, h0, om0) = invariants(&st, &k, d);
        let mut acc = vec![0.0; m];
        let mut acc_om = 0.0;
        let mut nacc = 0u64;
        let (mut de, mut dh) = (0.0f64, 0.0f64);
        let mut max_im = 0.0f64;
        if mem == 0 {
            write!(trace, "0").unwrap();
            for n in 0..m {
                write!(trace, ",{:.10e}", st[n].norm_sqr()).unwrap();
            }
            writeln!(trace, ",{e0:.15e},{h0:.15e},{om0:.10e},0").unwrap();
        }
        for s in 1..=steps {
            rk4_step(&mut st, &k, d, h);
            let t = s as f64 * h;
            let (e, hh, om) = invariants(&st, &k, d);
            de = de.max((e - e0).abs() / e0);
            dh = dh.max((hh - h0).abs());
            let im = st.iter().map(|z| z.im.abs()).fold(0.0, f64::max);
            max_im = max_im.max(im);
            if t >= 0.5 * t_end {
                for n in 0..m {
                    acc[n] += st[n].norm_sqr();
                }
                acc_om += om;
                nacc += 1;
            }
            if mem == 0 && s % trace_every == 0 {
                write!(trace, "{t:.6}").unwrap();
                for n in 0..m {
                    write!(trace, ",{:.10e}", st[n].norm_sqr()).unwrap();
                }
                writeln!(trace, ",{e:.15e},{hh:.15e},{om:.10e},{im:.3e}").unwrap();
            }
        }
        write!(ens, "{mem},{phi0:.12},{phi1:.12},{e0:.15e},{h0:.15e}").unwrap();
        for n in 0..m {
            write!(ens, ",{:.10e}", acc[n] / nacc as f64).unwrap();
        }
        writeln!(ens, ",{:.10e},{de:.3e},{dh:.3e},{max_im:.3e}", acc_om / nacc as f64).unwrap();
    }
    fs::write(trace_out, trace).unwrap();
    fs::write(ens_out, ens).unwrap();
    println!("CONSERV N={n_max} D={d} T={t_end} members={members} mode={mode} dt={h:.6e} steps_per_member={steps} wall_s={:.2}",
             t0.elapsed().as_secs_f64());
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    match a.get(1).map(|s| s.as_str()) {
        Some("probe") => probe(),
        Some("forced") => forced(&a[2..]),
        Some("crosscheck") => crosscheck(&a[2..]),
        Some("conserv") => conserv(&a[2..]),
        _ => eprintln!("usage: ch15_shell probe | forced ... | crosscheck out.csv | conserv ..."),
    }
}
