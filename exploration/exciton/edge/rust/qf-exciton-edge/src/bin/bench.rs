use qf_exciton_edge::{geom, kernel, rng::SplitMix64, system::System};
use std::time::Instant;
fn main() {
    let n = 37;
    let sys = System::new(n, kernel::by_id("g3").unwrap(), geom::by_id("disk", n as f64 / 0.5, 0.0).unwrap(), 1e4);
    let mut rng = SplitMix64::new(1);
    let x: Vec<f64> = (0..n).flat_map(|_| { let (a, b) = sys.cont.sample(&mut rng); [a, b] }).collect();
    let mut f = vec![0.0; 2 * n];
    let t = Instant::now();
    for _ in 0..2000 { sys.force(&x, &mut f); }
    println!("force {:.1} us", t.elapsed().as_secs_f64() / 2000.0 * 1e6);
    let mut h = vec![0.0; 4 * n * n];
    let t = Instant::now();
    for _ in 0..200 { sys.hessian(&x, &mut h); }
    println!("hessian {:.1} us", t.elapsed().as_secs_f64() / 200.0 * 1e6);
}
