"""Chapter 12: extract the few measured helium-II numbers this chapter compares with, from the HTML edition of
R. J. Donnelly and C. F. Barenghi, "The observed properties of liquid helium at the saturated vapor pressure",
J. Phys. Chem. Ref. Data 27, 1217 (1998), as served at https://pages.uoregon.edu/rjd/vapor{N}.htm (retrieved 2026-10-10).

Usage (the HTML files are downloaded data: they are read as text only, never executed):
    python3 -I ch12_db1998_extract.py <dir with vapor2.htm vapor3.htm vapor4.htm vapor5.htm vapor7.htm>

Writes figures/ch12_db1998.json with, for T <= 1.40 K:
  * Table 4.1  second-sound velocity u2 (adopted database: key 1 Heiserman et al., 4 Peshkov, 5 Wang et al.);
  * Table 3.1  first-sound velocity u1 (adopted database);
  * Table 6.1  fourth-sound velocity u4 (adopted database: key 1 Heiserman et al.);
  * Table 2.1  superfluid density rho_s (adopted database; key 1 = the compilers' own Landau integration over an older
               dispersion curve, key 2 = Maynard, from u2 and u4);
  * Table 1.2  density and thermal-expansion coefficient (recommended values; below the density minimum these are
               calculated, not measured -- the compilation says so).
plus the sha256 of each HTML file.  Every table is a two-column layout (T, value, key | T, value, key); cells are read in
document order and grouped in triples; a triple whose first number is not a plausible temperature is reported and skipped.
"""
import hashlib, html, json, re, sys
from pathlib import Path

SRC = Path(sys.argv[1])
OUT = Path(__file__).resolve().parent / "ch12_db1998.json"
TMAX = 1.40


def text(name):
    raw = (SRC / name).read_bytes()
    s = raw.decode("latin-1")
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s)
    return s, hashlib.sha256(raw).hexdigest()


NUM = r"[-+]?\d*\.?\d+(?:E[-+]?\d+)?"


def triples(seg, nkey=True):
    """Numbers of a table segment in document order, grouped as (T, value, key)."""
    toks = re.findall(NUM, seg)
    vals = [float(t) for t in toks]
    out, bad, i = [], [], 0
    while i + 2 < len(vals):
        T, v, k = vals[i], vals[i + 1], vals[i + 2]
        if 0.0 <= T <= 2.2 and float(k).is_integer() and 1 <= k <= 9:
            out.append((T, v, int(k))); i += 3
        else:
            bad.append(toks[i:i + 3]); i += 1
    return out, bad


res = dict(source="R. J. Donnelly and C. F. Barenghi, J. Phys. Chem. Ref. Data 27, 1217 (1998); HTML edition "
                  "https://pages.uoregon.edu/rjd/ (retrieved 2026-10-10)", files={})

# ---- second sound, Table 4.1
s, h = text("vapor5.htm"); res["files"]["vapor5.htm"] = h
seg = s[s.index("Table 4.1. Adopted database"):]
seg = seg[seg.index("Key", seg.index("u 2")) + 3:]
seg = seg[:seg.index("Table 4.2")] if "Table 4.2" in seg else seg[:20000]
seg = seg.replace("Table 4.1. (Continued) T 90 (K) u 2 (m/s) Key T 90 u 2 (m/s) Key", " ")
tr, bad = triples(seg)
res["u2"] = sorted([t for t in tr if t[0] <= TMAX])
res["u2_skipped_cells"] = bad
res["u2_keys"] = {"1": "Heiserman et al. (resonance, 1.187-2.150 K, <0.2 %)", "4": "Peshkov (resonance, 0.5-1.15 K, 0.75 %)",
                  "5": "Wang et al. (resonance, 1.187-1.804 K, 0.07 %)"}

# ---- first sound, Table 3.1
s, h = text("vapor4.htm"); res["files"]["vapor4.htm"] = h
seg = s[s.index("Table 3.1. Adopted database"):]
seg = seg[seg.index("Key", seg.index("u 1")) + 3:]
seg = seg[:seg.index("Table 3.2")] if "Table 3.2" in seg else seg[:20000]
tr, bad = triples(seg)
res["u1"] = sorted([t for t in tr if t[0] <= TMAX and t[1] > 200.0])   # drops a header fragment ("T 90 ... 1")
res["u1_keys"] = {"3": "Whitney and Chase (pulse, 0.15-1.8 K)", "5": "Heiserman et al.", "6": "Tam and Ahlers"}

# ---- fourth sound, Table 6.1
s, h = text("vapor7.htm"); res["files"]["vapor7.htm"] = h
seg = s[s.index("Table 6.1. Adopted database"):]
seg = seg[seg.index("Key", seg.index("u 1")) + 3:]
seg = seg[:seg.index("Table 6.2")]
tr, bad = triples(seg)
res["u4"] = sorted([t for t in tr if t[0] <= TMAX])
res["u4_keys"] = {"1": "Heiserman et al.", "2": "Tam and Ahlers"}

# ---- superfluid density, Table 2.1
s, h = text("vapor3.htm"); res["files"]["vapor3.htm"] = h
seg = s[s.index("Table 2.1. The adopted database"):]
seg = seg[seg.index("key", seg.index("p s")) + 3:]
seg = seg[seg.index("key") + 3:]
seg = seg[:seg.index("Table 2.2")]
seg = seg.replace("0 0. 14514 1", "0 0.14514 1")          # the first cell is split in the HTML
tr, bad = triples(seg)
res["rho_s"] = sorted([t for t in tr if t[0] <= TMAX])
res["rho_s_keys"] = {"1": "Landau theory, integration over the compilers' dispersion curve (calculated, 0.1-1.25 K)",
                     "2": "Maynard, from u2 and u4 (1.2-2.15 K, <5 %)"}

# ---- density and expansion coefficient, Table 1.2 (columns: T, dielectric constant, rho [g/cm3], 1e3*alpha [1/K])
s, h = text("vapor2.htm"); res["files"]["vapor2.htm"] = h
seg = s[s.index("Table 1.2. Recommended values"):]
seg = seg[seg.index("(k -1 )", seg.index("(k -1 )") + 5) + 7:]
toks = re.findall(NUM, seg)[:400]
vals = [float(t) for t in toks]
rows, i = [], 0
while i + 3 < len(vals) and len(rows) < 120:
    T, eps, rho, a3 = vals[i:i + 4]
    if 0 <= T <= 5 and 1.0 < eps < 1.06 and 0.12 < rho < 0.15:
        rows.append((T, eps, rho, a3)); i += 4
    else:
        i += 1
res["density_alpha"] = sorted([r for r in rows if r[0] <= TMAX])
res["density_alpha_note"] = "alpha in units of 1e-3/K; below the density minimum the compilation's values are calculated (Niemela and Donnelly)"

OUT.write_text(json.dumps(res, indent=1))
print("u2", len(res["u2"]), res["u2"][:3], "...", res["u2"][-2:])
print("u2 skipped", res["u2_skipped_cells"][:5])
print("u1", res["u1"])
print("u4", res["u4"])
print("rho_s", res["rho_s"])
print("density_alpha", res["density_alpha"])
print("wrote", OUT)
