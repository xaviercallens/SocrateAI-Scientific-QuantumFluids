"""Development only (amendment A1): one certification at non-gate parameters."""
import sys, json
from fractions import Fraction
import certify as C
d, alpha, b, K = int(sys.argv[1]), Fraction(sys.argv[2]), Fraction(sys.argv[3]), int(sys.argv[4])
out = C.certify_one(d, alpha, b, K, lp_kw=dict(rounds=6, n_fine=100000))
out.pop("coeffs_exact", None)
print(json.dumps(out, indent=1, default=str))
