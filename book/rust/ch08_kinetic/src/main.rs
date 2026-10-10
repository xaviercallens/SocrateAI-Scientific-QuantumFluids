//! Chapter 8 driver: CVODE (crate `cvode` of rusty-SUNDIALS) on two problems.
//!
//!   kin   the collisionless Landau kinetic equation of a 2D Fermi liquid with ONE Landau parameter F,
//!         linearised about the ground state, at one wave vector q (units: a = q v_F = 1):
//!             d nu(theta,t)/dt = -i cos(theta) [ nu(theta,t) + F <nu>(t) ],      <nu> = (1/2pi) int nu dtheta,
//!         discretised on N midpoint nodes theta_j = (j + 1/2) pi / N of the half circle (nu is even in theta),
//!         state y = (Re nu_j, Im nu_j), analytic Jacobian.
//!   cont  continuation of the zero-sound root s(F) along ln F (Davidenko ODE), 2D and 3D.
//!
//! Usage:
//!   ch08_kinetic kin  F ic N method rtol atol tend dt out.csv [snap_times_comma_separated snap_out.csv]
//!        ic = uniform (nu = 1) | kick (nu = cos theta);   method = bdf | adams
//!   ch08_kinetic cont dim w0 Fmin Fmax npts rtol atol out.csv        (dim = 2 or 3; w0 = ln(s-1) at Fmin)
use cvode::{Cvode, DenseMat, Method, Task};
use nvector::SerialVector;
use std::fmt::Write as _;
use std::fs;
use std::f64::consts::PI;

fn method_of(s: &str) -> Method {
    match s { "bdf" => Method::Bdf, "adams" => Method::Adams, _ => panic!("method must be bdf or adams") }
}

fn kin(args: &[String]) {
    let f: f64 = args[0].parse().unwrap();
    let ic = args[1].as_str();
    let n: usize = args[2].parse().unwrap();
    let method = method_of(&args[3]);
    let rtol: f64 = args[4].parse().unwrap();
    let atol: f64 = args[5].parse().unwrap();
    let tend: f64 = args[6].parse().unwrap();
    let dt: f64 = args[7].parse().unwrap();
    let out = &args[8];
    let snaps: Vec<f64> = if args.len() > 10 { args[9].split(',').map(|x| x.parse().unwrap()).collect() } else { vec![] };
    let snap_out = if args.len() > 10 { Some(args[10].clone()) } else { None };

    let c: Vec<f64> = (0..n).map(|j| ((j as f64 + 0.5) * PI / n as f64).cos()).collect();
    let nf = n as f64;
    let c_rhs = c.clone();
    let rhs = move |_t: f64, y: &[f64], yd: &mut [f64]| -> Result<(), String> {
        let mr = y[..n].iter().sum::<f64>() / nf;
        let mi = y[n..].iter().sum::<f64>() / nf;
        for j in 0..n {
            yd[j] = c_rhs[j] * (y[n + j] + f * mi);
            yd[n + j] = -c_rhs[j] * (y[j] + f * mr);
        }
        Ok(())
    };
    // J = [[0, A], [-A, 0]],  A_ij = c_i delta_ij + (F/N) c_i ; column-major cols[col][row]
    let c_jac = c.clone();
    let jac = move |_t: f64, _y: &[f64], jm: &mut DenseMat| -> Result<(), String> {
        for col in 0..2 * n { for row in 0..2 * n { jm.cols[col][row] = 0.0; } }
        for i in 0..n {
            for j in 0..n {
                let a = if i == j { c_jac[i] } else { 0.0 } + f / nf * c_jac[i];
                jm.cols[n + j][i] = a;      // d(dRe_i)/d(Im_j)
                jm.cols[j][n + i] = -a;     // d(dIm_i)/d(Re_j)
            }
        }
        Ok(())
    };
    let mut y0 = vec![0.0; 2 * n];
    for j in 0..n { y0[j] = if ic == "kick" { c[j] } else { 1.0 }; }
    let builder = Cvode::builder(method).rtol(rtol).atol(atol).max_steps(5_000_000);
    // CH08_NOJAC=1 : let CVODE difference the Jacobian itself (used once, to test the Adams method; see the chapter)
    let builder = if std::env::var("CH08_NOJAC").is_ok() { builder } else { builder.jacobian(jac) };
    let mut cv = builder.build(rhs, 0.0, SerialVector::from_slice(&y0)).expect("build");
    let t_start = std::time::Instant::now();
    let nout = (tend / dt).round() as usize;
    let mut csv = String::from("t,re_m,im_m,norm2\n");
    let mut snap_csv = String::from("t,j,theta,re,im\n");
    let mut snap_todo = snaps.clone();
    let record = |t: f64, y: &[f64], csv: &mut String, snap_csv: &mut String, snap_todo: &mut Vec<f64>| {
        let mr = y[..n].iter().sum::<f64>() / nf;
        let mi = y[n..].iter().sum::<f64>() / nf;
        let n2 = (0..n).map(|j| y[j] * y[j] + y[n + j] * y[n + j]).sum::<f64>() / nf;
        writeln!(csv, "{:.6},{:.15e},{:.15e},{:.15e}", t, mr, mi, n2).unwrap();
        if let Some(p) = snap_todo.iter().position(|&ts| (ts - t).abs() < 0.5 * dt) {
            snap_todo.remove(p);
            for j in 0..n {
                writeln!(snap_csv, "{:.6},{},{:.15e},{:.15e},{:.15e}", t, j, (j as f64 + 0.5) * PI / nf, y[j], y[n + j]).unwrap();
            }
        }
    };
    record(0.0, &y0, &mut csv, &mut snap_csv, &mut snap_todo);
    for k in 1..=nout {
        let tout = k as f64 * dt;
        let (t, y) = cv.solve(tout, Task::Normal).unwrap_or_else(|e| panic!("solve to {tout}: {e:?}"));
        let yv = y.to_vec();
        record(t, &yv, &mut csv, &mut snap_csv, &mut snap_todo);
    }
    fs::write(out, csv).unwrap();
    if let Some(p) = snap_out { fs::write(p, snap_csv).unwrap(); }
    println!("STATS F={f} ic={ic} N={n} method={} rtol={rtol:e} atol={atol:e} tend={tend} steps={} rhs_evals={} wall_s={:.3}",
             args[3], cv.num_steps(), cv.num_rhs_evals(), t_start.elapsed().as_secs_f64());
}

/// Davidenko continuation: along u = ln F, w = ln(s-1) obeys dw/du = G(w).
fn cont(args: &[String]) {
    let dim: usize = args[0].parse().unwrap();
    let w0: f64 = args[1].parse().unwrap();
    let fmin: f64 = args[2].parse().unwrap();
    let fmax: f64 = args[3].parse().unwrap();
    let npts: usize = args[4].parse().unwrap();
    let rtol: f64 = args[5].parse().unwrap();
    let atol: f64 = args[6].parse().unwrap();
    let out = &args[7];
    let rhs = move |_u: f64, y: &[f64], yd: &mut [f64]| -> Result<(), String> {
        let sm1 = y[0].exp();
        let s = 1.0 + sm1;
        yd[0] = if dim == 2 {
            let r = (sm1 * (s + 1.0)).sqrt();
            (s + 1.0) / (s + r)
        } else {
            let l = (2.0 / sm1).ln_1p();
            let gp = 0.5 * l - s / (sm1 * (s + 1.0));
            let g = 0.5 * s * l - 1.0;
            -g / gp / sm1
        };
        Ok(())
    };
    let mut cv = Cvode::builder(Method::Bdf).rtol(rtol).atol(atol).max_steps(1_000_000)
        .build(rhs, fmin.ln(), SerialVector::from_slice(&[w0])).expect("build");
    let t_start = std::time::Instant::now();
    let mut csv = String::from("F,w,s\n");
    writeln!(csv, "{:.15e},{:.15e},{:.15e}", fmin, w0, 1.0 + w0.exp()).unwrap();
    for k in 1..npts {
        let u = fmin.ln() + (fmax.ln() - fmin.ln()) * k as f64 / (npts - 1) as f64;
        let (_, y) = cv.solve(u, Task::Normal).unwrap_or_else(|e| panic!("cont solve u={u}: {e:?}"));
        writeln!(csv, "{:.15e},{:.15e},{:.15e}", u.exp(), y[0], 1.0 + y[0].exp()).unwrap();
    }
    fs::write(out, csv).unwrap();
    println!("STATS cont dim={dim} npts={npts} rtol={rtol:e} atol={atol:e} steps={} rhs_evals={} wall_s={:.4}", cv.num_steps(), cv.num_rhs_evals(), t_start.elapsed().as_secs_f64());
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    match a.get(1).map(|s| s.as_str()) {
        Some("kin") => kin(&a[2..]),
        Some("cont") => cont(&a[2..]),
        _ => eprintln!("usage: ch08_kinetic kin|cont ..."),
    }
}
