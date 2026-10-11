//! Radix-2 FFT of any power-of-two length (generalises `fft16` of dd.rs); 2-D transform on row-major M x M arrays.
use std::f64::consts::PI;

pub struct Fft2 {
    pub m: usize,
    rev: Vec<usize>,
    wr: Vec<f64>, // cos(2 pi j / m), j < m/2
    wi: Vec<f64>, // sin(2 pi j / m)
}

impl Fft2 {
    pub fn new(m: usize) -> Fft2 {
        assert!(m.is_power_of_two() && m >= 2);
        let bits = m.trailing_zeros();
        let rev = (0..m).map(|i| if bits == 0 { 0 } else { (i as u32).reverse_bits() as usize >> (32 - bits) }).collect();
        let wr = (0..m / 2).map(|j| (2.0 * PI * j as f64 / m as f64).cos()).collect();
        let wi = (0..m / 2).map(|j| (2.0 * PI * j as f64 / m as f64).sin()).collect();
        Fft2 { m, rev, wr, wi }
    }

    /// in-place 1-D transform: forward `e^{-i}`, inverse `e^{+i}`, both unnormalised
    pub fn fft1(&self, re: &mut [f64], im: &mut [f64], inverse: bool) {
        let m = self.m;
        for i in 0..m {
            let j = self.rev[i];
            if j > i {
                re.swap(i, j);
                im.swap(i, j);
            }
        }
        let sgn = if inverse { 1.0 } else { -1.0 };
        let mut len = 2;
        while len <= m {
            let stride = m / len;
            let half = len / 2;
            for k in (0..m).step_by(len) {
                for j in 0..half {
                    let (c, s) = (self.wr[j * stride], sgn * self.wi[j * stride]);
                    let (a, b) = (k + j, k + j + half);
                    let tr = re[b] * c - im[b] * s;
                    let ti = re[b] * s + im[b] * c;
                    re[b] = re[a] - tr;
                    im[b] = im[a] - ti;
                    re[a] += tr;
                    im[a] += ti;
                }
            }
            len <<= 1;
        }
    }

    /// 2-D transform in place on row-major arrays (index `x*m + y`); the inverse is normalised by 1/m^2.
    pub fn fft2(&self, re: &mut [f64], im: &mut [f64], inverse: bool) {
        let m = self.m;
        for x in 0..m {
            self.fft1(&mut re[x * m..(x + 1) * m], &mut im[x * m..(x + 1) * m], inverse);
        }
        let mut cr = vec![0.0; m];
        let mut ci = vec![0.0; m];
        for y in 0..m {
            for x in 0..m {
                cr[x] = re[x * m + y];
                ci[x] = im[x * m + y];
            }
            self.fft1(&mut cr, &mut ci, inverse);
            for x in 0..m {
                re[x * m + y] = cr[x];
                im[x * m + y] = ci[x];
            }
        }
        if inverse {
            let f = 1.0 / (m * m) as f64;
            re.iter_mut().for_each(|v| *v *= f);
            im.iter_mut().for_each(|v| *v *= f);
        }
    }
}
