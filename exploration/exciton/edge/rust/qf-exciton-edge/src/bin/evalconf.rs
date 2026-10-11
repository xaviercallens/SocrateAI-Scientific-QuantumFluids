//! Energies and forces of given configurations (instrument gate E-b; planted-bug controls E-d).
//!
//!     evalconf <configs.txt> <bug 0..3>      env QF_TABLE_DIR
//! line: `kernel container area kappa ktrap n x0 y0 x1 y1 ...`; output line: `e_int e_wall f0 f1 ...` (17 digits).
use qf_exciton_edge::{geom, kernel, system::System};
use std::io::Write;

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let text = std::fs::read_to_string(&a[1]).expect("read configs");
    let bug: u8 = a[2].parse().unwrap();
    let mut out = std::io::stdout().lock();
    for line in text.lines().filter(|l| !l.trim().is_empty()) {
        let t: Vec<&str> = line.split_whitespace().collect();
        let pair = kernel::by_id(t[0]).unwrap();
        let area: f64 = t[2].parse().unwrap();
        let kappa: f64 = t[3].parse().unwrap();
        let ktrap: f64 = t[4].parse().unwrap();
        let n: usize = t[5].parse().unwrap();
        let x: Vec<f64> = t[6..].iter().map(|s| s.parse().unwrap()).collect();
        assert_eq!(x.len(), 2 * n);
        let cont = geom::by_id(t[1], area, ktrap).unwrap();
        let mut sys = System::new(n, pair, cont, kappa);
        sys.bug = bug;
        let mut f = vec![0.0; 2 * n];
        sys.force(&x, &mut f);
        let mut s = format!("{:.17e} {:.17e}", sys.e_int(&x), sys.e_wall(&x));
        for v in &f {
            s.push_str(&format!(" {:.17e}", v));
        }
        writeln!(out, "{s}").unwrap();
        if a.get(3).map(|v| v == "hess").unwrap_or(false) {
            let mut h = vec![0.0; 4 * n * n];
            sys.hessian(&x, &mut h);
            let hs: Vec<String> = h.iter().map(|v| format!("{:.17e}", v)).collect();
            writeln!(out, "H {}", hs.join(" ")).unwrap();
        }
    }
}
