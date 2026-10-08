"""Apply the window fixed in amendment FL-A1 (before the arm was read) to the k_cut = 2pi, T = 0.173 arm.
H-T: alpha_E in [0.0084, 0.0104]; rho_n-law at c = 0.096: [0.0067, 0.0087]; overlap [0.0084, 0.0087] inconclusive."""
import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
subprocess.run([sys.executable, str(ROOT / "exploration/pgpe/analyze_friction_law.py")], cwd=ROOT, capture_output=True, text=True)
r = json.loads((ROOT / "data/generated/pgpe/transport/fl/friction_law_results.json").read_text())
a = next((x for x in r["arms"] if x["label"] == "2pi, T=0.173"), None)
if a is None:
    sys.exit("arm not available (fewer than 2 runs)")
v = a["alpha_energy"]; e = a["alpha_energy_se"]
inH, inR = 0.0084 <= v <= 0.0104, 0.0067 <= v <= 0.0087
verdict = "INCONCLUSIVE (overlap)" if inH and inR else ("SUPPORTS H-T" if inH else ("SUPPORTS rho_n-law at c=0.096" if inR else "OUTSIDE BOTH WINDOWS"))
print(f"2pi, T=0.173: n={a['n_runs']} alpha_E = {v:.5f} +- {e:.5f}  (H-T 0.0094, rho_n-law 0.0077)  -> {verdict}")
print(f"  c = {a['c_energy']:.3f} +- {a['c_energy_se']:.3f};  alpha/T = {a['alpha_energy_over_T']:.4f} +- {a['alpha_energy_over_T_se']:.4f};  alpha' = {a['alpha_prime']:+.4f}")
print(f"  all arms: alpha/T = {r['H_T']['a']:.4f} +- {r['H_T']['se']:.4f}, chi2 {r['H_T']['chi2']:.2f}/{r['H_T']['dof']};  one-c chi2 {r['one_c']['chi2']:.1f}/{r['one_c']['dof']};  FL2 spread {r['FL2']['spread']:.2f}")
