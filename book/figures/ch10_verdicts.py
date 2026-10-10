"""Chapter 10, figure 'verdict map': every criterion that LEDGER.md records one by one for the programme's campaigns, coloured by its verdict.
Input: figures/ch10_verdicts.json (curated, each row names the ledger claims it is read from; this script CHECKS that the claims exist,
that the quoted phrase occurs in LEDGER.md and that the row date is a date of one of the claims).  Output: ch10_verdicts.{pdf,png},
ch10_verdicts_numbers.json (tallies quoted in the chapter).
Run:  .venv/bin/python book/figures/ch10_verdicts.py"""
import sys, json, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figstyle import *
from matplotlib.patches import FancyBboxPatch, Patch
import os
from matplotlib.font_manager import FontProperties
# The bold EB Garamond that matplotlib finds (EBGaramond12-Bold.ttf) has no 'lnum' feature, so a digit in a bold label stays old-style ('Round 4' reads as a descending figure).
# The OpenType bold that the book's LaTeX uses has it: take that file for the titles when it is installed.
_BOLD_OTF = "/usr/share/texlive/texmf-dist/fonts/opentype/public/ebgaramond/EBGaramond-Bold.otf"
TITLE_KW = dict(fontproperties=FontProperties(fname=_BOLD_OTF)) if os.path.exists(_BOLD_OTF) else dict(fontweight="bold")
if os.path.exists(_BOLD_OTF): plt.rcParams["pdf.fonttype"] = 3     # matplotlib embeds a CFF OpenType file as 'Type 42' (TrueType), which viewers flag as a mismatch; Type 3 (outlines) is valid for it

here = Path(__file__).resolve().parent
spec = json.load(open(here / "ch10_verdicts.json"))["rows"]
ledger = (ROOT / "LEDGER.md").read_text()

# ---- verification against the ledger -------------------------------------------------------------------------------------------
def claim_dates(cid):
    out = set()
    for ln in ledger.split("\n"):
        if re.match(r"\|\s*" + re.escape(cid) + r"\s*\|", ln):
            cols = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(cols) >= 3 and re.fullmatch(r"\d{4}-\d{2}-\d{2}|\d{4}-\d{2}", cols[2]): out.add(cols[2])
    return out
problems = []
for r in spec:
    for cid in r["claims"]:
        if not re.search(r"\b" + re.escape(cid) + r"\b", ledger): problems.append(f"{r['id']}: {cid} not in LEDGER.md")
    if r["check"] not in ledger: problems.append(f"{r['id']}: phrase not found: {r['check']!r}")
    ds = set().union(*[claim_dates(c) for c in r["claims"]])
    if r["date"] not in ds: problems.append(f"{r['id']}: date {r['date']} not among the ledger dates {sorted(ds)} of {r['claims']}")
print("ledger verification:", "OK" if not problems else problems)
assert not problems, problems

# ---- drawing -------------------------------------------------------------------------------------------------------------------
COL = {"P": BLUE, "F": RED, "M": GOLD, "V": GREY, "N": "#FFFFFF"}
SANS = "DejaVu Sans"
PER_LINE, CW, CG, RH, PAD = 14, 0.285, 0.030, 0.285, 0.105
LABW = 1.62
TXT_H = lambda r: 0.118 * (r["title"].count("\n") + 1) + 0.105
heights = [max(int(np.ceil(len(r["cells"]) / PER_LINE)) * (RH + CG), TXT_H(r)) for r in spec]
H = sum(heights) + PAD * (len(spec) + 1)
W = LABW + PER_LINE * (CW + CG)
EXTRA = 0.62
fig = plt.figure(figsize=(TEXTW, TEXTW * (H + EXTRA) / W))
ax = fig.add_axes([0, EXTRA / (H + EXTRA), 1, H / (H + EXTRA)]); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off")
y = PAD
tallies = {k: 0 for k in COL}; per_row = []
for r, h in zip(spec, heights):
    t = {k: 0 for k in COL}
    for k, c in enumerate(r["cells"]):
        i, j = divmod(k, PER_LINE)
        x0, y0 = LABW + j * (CW + CG), y + i * (RH + CG)
        v = c["v"]; t[v] += 1; tallies[v] += 1
        ax.add_patch(FancyBboxPatch((x0, y0), CW, RH, boxstyle="round,pad=0,rounding_size=0.045", fc=COL[v], ec=("#999999" if v == "N" else "white"),
                                    lw=0.8 if v != "N" else 0.7, ls="--" if v == "N" else "-", hatch="////" if v == "V" else None))
        if c["l"]:
            ax.text(x0 + CW / 2, y0 + RH / 2 + 0.004, c["l"], ha="center", va="center", fontsize=5.1 if len(c["l"]) <= 4 else 4.4, family=SANS,
                    color="#222222" if v == "N" else "white", fontweight="bold" if v != "N" else "normal")
    nl = r["title"].count("\n") + 1
    d = r["date"][5:]; mm = {"09": "Sep", "10": "Oct", "08": "Aug"}[d[:2]]
    ax.text(LABW - 0.08, y + 0.005, r["title"], ha="right", va="top", fontsize=6.9, color=BLUE, linespacing=1.12,
            **(TITLE_KW if (re.search(r"\d", r["title"]) and "\n" not in r["title"]) else dict(fontweight="bold")))     # the OpenType bold only where a digit needs lining figures (its line height differs)
    ax.text(LABW - 0.08, y + 0.118 * nl + 0.02, f"{mm} {int(d[3:])} \u00b7 " + ", ".join(c.replace("CLAIM-", "") for c in r["claims"]), ha="right", va="top", fontsize=5.0, color=GREY, family=SANS)
    if r.get("note"):
        last = len(r["cells"]) - 1; i, j = divmod(last, PER_LINE)
        ax.text(LABW + (j + 1) * (CW + CG) + 0.04, y + i * (RH + CG) + RH / 2, r["note"], ha="left", va="center", fontsize=5.6, color=GREY, style="italic")
    n = len(r["cells"]); per_row.append(dict(id=r["id"], n=n, **{k: v for k, v in t.items() if v}))
    y += h + PAD
ax.plot([LABW - 0.03] * 2, [0.03, H - 0.03], color="#DDDDDD", lw=0.6)
tot = sum(tallies.values())
leg = [Patch(fc=BLUE, label=f"met as registered ({tallies['P']})"), Patch(fc=RED, label=f"not met / refuted ({tallies['F']})"),
       Patch(fc=GOLD, label=f"mixed, partial, inconclusive ({tallies['M']})"), Patch(fc=GREY, hatch="////", ec="white", label=f"voided later ({tallies['V']})"),
       Patch(fc="white", ec="#999999", ls="--", label=f"not run ({tallies['N']})")]
fig.legend(handles=leg, loc="lower center", ncol=3, fontsize=6.6, frameon=False, bbox_to_anchor=(0.5, 0.0), handlelength=1.1, columnspacing=1.3, handletextpad=0.5)
save(fig, "ch10_verdicts")
json.dump(dict(total=tot, tallies=tallies, rows=per_row, n_rows=len(spec), source="LEDGER.md rows named in ch10_verdicts.json (verified by this script)"),
          open(here / "ch10_verdicts_numbers.json", "w"), indent=1)
print("cells:", tot, tallies)
