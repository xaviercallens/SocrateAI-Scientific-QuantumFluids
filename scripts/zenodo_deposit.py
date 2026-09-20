#!/usr/bin/env python3
"""Deposit a tagged release on Zenodo.

    python3 scripts/zenodo_deposit.py --tag v1.2.0             # creates a DRAFT, prints its URL
    python3 scripts/zenodo_deposit.py --tag v1.2.0 --publish   # publishes: mints a PERMANENT DOI

Publishing cannot be undone, so it is never the default. The token is read from $ZENODO_TOKEN or
~/.zenodo_token and is never printed or logged.
"""
import argparse, json, os, subprocess, sys, tempfile
from pathlib import Path
import requests

API = "https://zenodo.org/api"
ROOT = Path(__file__).resolve().parent.parent

def token() -> str:
    t = os.environ.get("ZENODO_TOKEN")
    f = Path.home() / ".zenodo_token"
    if not t and f.exists():
        t = f.read_text().strip()
    if not t:
        sys.exit("no Zenodo token: set ZENODO_TOKEN or create ~/.zenodo_token")
    return t

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--publish", action="store_true")
    a = ap.parse_args()
    meta = json.loads((ROOT / "paper" / "zenodo_metadata.json").read_text())
    meta["metadata"]["version"] = a.tag
    auth = {"Authorization": f"Bearer {token()}"}

    with tempfile.TemporaryDirectory() as td:
        arc = Path(td) / f"SocrateAI-Scientific-QuantumFluids-{a.tag}.zip"
        subprocess.run(["git", "-C", str(ROOT), "archive", "--format=zip",
                        f"--prefix=QuantumFluids-{a.tag}/", "-o", str(arc), a.tag], check=True)
        files = [arc, ROOT / "paper" / "quantumfluids_lean4.pdf"]
        r = requests.post(f"{API}/deposit/depositions", json={}, headers=auth, timeout=60)
        r.raise_for_status()
        dep = r.json(); bucket = dep["links"]["bucket"]
        for f in files:
            with open(f, "rb") as fh:
                u = requests.put(f"{bucket}/{f.name}", data=fh, headers=auth, timeout=600)
                u.raise_for_status()
            print(f"uploaded {f.name} ({f.stat().st_size/1e6:.1f} MB)")
        r = requests.put(f"{API}/deposit/depositions/{dep['id']}", json=meta, headers=auth, timeout=60)
        if r.status_code >= 400:
            sys.exit(f"metadata rejected: {r.status_code} {r.text[:600]}")
        print("draft:", dep["links"]["html"])
        if a.publish:
            r = requests.post(f"{API}/deposit/depositions/{dep['id']}/actions/publish",
                              headers=auth, timeout=120)
            if r.status_code >= 400:
                sys.exit(f"publish failed: {r.status_code} {r.text[:600]}")
            j = r.json()
            print("PUBLISHED  DOI:", j.get("doi"), " ", j["links"].get("record_html", j["links"].get("html")))
            (ROOT / "paper" / "zenodo_record.json").write_text(json.dumps(
                {"doi": j.get("doi"), "conceptdoi": j.get("conceptdoi"), "id": j.get("id"),
                 "tag": a.tag}, indent=1) + "\n")

if __name__ == "__main__":
    main()
