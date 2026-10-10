//! Gate S0-b: CVODE order check on y' = -y (Adams and BDF) on the pinned build.
use cvode::{Cvode, Method, Task};
use nvector::SerialVector;

fn run(method: Method, rtol: f64) -> (f64, usize, usize) {
    let rhs = |_t: f64, y: &[f64], yd: &mut [f64]| -> Result<(), String> {
        yd[0] = -y[0];
        Ok(())
    };
    let mut s = Cvode::builder(method)
        .rtol(rtol)
        .atol(1e-14)
        .max_steps(5_000_000)
        .build(rhs, 0.0, SerialVector::from_slice(&[1.0]))
        .expect("build");
    let mut maxerr = 0.0f64;
    for k in 1..=10 {
        let (_, y) = s.solve(k as f64, Task::Normal).expect("solve");
        let ex = (-(k as f64)).exp();
        maxerr = maxerr.max(((y[0] - ex) / ex).abs());
    }
    (maxerr, s.num_rhs_evals(), s.num_steps())
}

fn main() {
    println!("{{\"gate\":\"S0-b\",\"build\":\"rusty-SUNDIALS tree 996aaf0706e1 (v11.6.0)\",\"rows\":[");
    let mut rows = Vec::new();
    let mut adams_1e10 = (0.0, 0, 0);
    let mut bdf_1e8 = (0.0, 0, 0);
    for (name, m) in [("adams", Method::Adams), ("bdf", Method::Bdf)] {
        for rtol in [1e-4, 1e-6, 1e-8, 1e-10] {
            let (err, nfe, nst) = run(m, rtol);
            if name == "adams" && rtol == 1e-10 {
                adams_1e10 = (err, nfe, nst);
            }
            if name == "bdf" && rtol == 1e-8 {
                bdf_1e8 = (err, nfe, nst);
            }
            rows.push(format!(
                "  {{\"method\":\"{name}\",\"rtol\":{rtol:e},\"max_rel_err\":{err:e},\"rhs_evals\":{nfe},\"steps\":{nst}}}"
            ));
        }
    }
    println!("{}", rows.join(",\n"));
    let pass_a = adams_1e10.1 <= 1000 && adams_1e10.0 <= 1e-8;
    let pass_b = bdf_1e8.0 <= 1e-5;
    println!("],\"adams_rtol1e-10\":{{\"rhs\":{},\"err\":{:e},\"pass\":{}}},\"bdf_rtol1e-8\":{{\"err\":{:e},\"pass\":{}}}}}",
        adams_1e10.1, adams_1e10.0, pass_a, bdf_1e8.0, pass_b);
}
