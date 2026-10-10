"""Chapter 4: record the Lean runs made for this chapter (compile logs live in the session scratchpad; this script copies what the
chapter quotes into figures/).  Writes
  ch04_lean_runs.json         -- exit codes, seconds, `#print axioms` lines of the three library modules, of lean/Ch04_DosLink.lean and of the controls
  ch04_negctl_L54.txt         -- first lines of Lean's error for `density_of_states` with 55 replaced by 54 (paths shortened)
  ch04_negctl_D15121.txt      -- first lines of Lean's error for the capstone with 15120 replaced by 15121 (paths shortened)
Usage: ch04_lean_record.py <scratch_dir>   (the directory holding logs/ with BoseIntegral.log, ..., NegControlL54.log, DosLink*.log)"""
import json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SP = Path(sys.argv[1]) if len(sys.argv) > 1 else None
L = {}

def axioms(text):
    return re.findall(r"'(.+?)' depends on axioms: \[([^\]]*)\]", text)

def status(text):
    m = re.search(r"exit=(\d+) seconds=(\d+)", text)
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)

def shorten(text, name):
    """paths shortened; the dagger that Lean prints after inaccessible hypothesis names is dropped (it is not in the listing font's safe set)"""
    return re.sub(r"/[^\s:]*/" + name, name, text).replace("\u271d", "")

if SP:
    logs = SP/"logs"
    for mod in ("BoseIntegral", "PhononSeries", "PhononSpecificHeat"):
        t = (logs/f"{mod}.log").read_text()
        L[mod] = dict(errors=len(re.findall(r"error", t)), sorry=("sorry" in t), axioms={n: a for n, a in axioms(t)})
    summ = (logs/"summary.txt").read_text().splitlines()
    last = [l for l in summ if l.startswith(("BoseIntegral", "PhononSeries", "PhononSpecificHeat"))][-3:]
    for l in last:
        m = re.match(r"(\w+) exit=(\d+) seconds=(\d+)", l); L[m.group(1)]["exit"] = int(m.group(2)); L[m.group(1)]["seconds"] = int(m.group(3))
    for tag, fname, key in (("L54", "NegControlL54", "neg_L54"), ("D15121", "NegControlD15121", "neg_D15121")):
        f = logs/f"{fname}.log"
        if f.exists():
            t = f.read_text(); ex, sec = status(t)
            body = shorten(re.sub(r"\nexit=\d+ seconds=\d+\s*$", "", t), fname + ".lean")
            lines = body.splitlines()
            i0 = next(i for i, l in enumerate(lines) if ": error:" in l)
            if tag == "L54":
                keep = lines[i0:]                                   # the whole message (6 lines)
            else:
                keep = [lines[i0], "  [... %d more lines: the goal that `ring` could not close, a polynomial" % (len(lines) - i0 - 1),
                        "   identity in V, kB, T, hbar, c, pi, a2..a6, z7, z9 ...]"]
            (HERE/f"ch04_negctl_{tag}.txt").write_text("\n".join(keep) + "\n")
            L[key] = dict(exit=ex, seconds=sec, n_lines_total=len(lines), n_lines_shown=len(keep))
    for fname in ("DosLink2", "DosLink3", "DosLink4", "DosLink5"):
        f = logs/f"{fname}.log"
        if f.exists():
            t = f.read_text(); ex, sec = status(t)
            L[fname] = dict(exit=ex, seconds=sec, errors=len(re.findall(r": error", t)), warnings=len(re.findall(r": warning", t)), sorry=("sorry" in t), axioms={n: a for n, a in axioms(t)})
(HERE/"ch04_lean_runs.json").write_text(json.dumps(L, indent=1)); print(json.dumps(L, indent=1)[:3000])
