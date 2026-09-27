#!/usr/bin/env python3
"""Deposit a STANDALONE paper on Zenodo, with its own dedicated concept DOI.

Unlike zenodo_deposit.py (which bundles the whole software repository + every paper PDF into one
software-type record, and is always run with --new-version-of to keep continuing that one line),
this script is for a single paper that deserves to be citable on its own -- e.g. a foundational
paper meant for arXiv, distinct from the software archive it grew out of. It always creates a
NEW, separate Zenodo record with its OWN concept DOI (never --new-version-of another record),
uploads exactly one PDF, and takes upload_type "publication" metadata rather than "software".

    python3 scripts/zenodo_deposit_paper.py --meta paper/zenodo_metadata_sector_thesis.json \
        --pdf paper/sector_thesis.pdf --record-out paper/zenodo_record_sector_thesis.json
    python3 scripts/zenodo_deposit_paper.py --meta paper/zenodo_metadata_sector_thesis.json \
        --pdf paper/sector_thesis.pdf --record-out paper/zenodo_record_sector_thesis.json --publish

To publish a NEW VERSION of a paper already deposited this way (e.g. a revised edition), pass
--new-version-of <record id from the previous record-out file> -- this is the one case where this
script does keep an existing concept DOI, exactly mirroring zenodo_deposit.py's own convention.

Publishing cannot be undone, so it is never the default. The token is read from $ZENODO_TOKEN or
~/.zenodo_token and is never printed or logged.
"""
import argparse, json, os, sys
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
    ap.add_argument("--meta", required=True, help="path to this paper's zenodo metadata JSON")
    ap.add_argument("--pdf", required=True, help="path to the paper PDF to upload")
    ap.add_argument("--record-out", required=True,
                     help="path to write {doi, conceptdoi, id} after a successful publish")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--new-version-of", dest="prev", default=None,
                     help="record id of a PREVIOUS version of this same standalone paper (rare)")
    a = ap.parse_args()

    meta = json.loads((ROOT / a.meta).read_text())
    pdf = ROOT / a.pdf
    if not pdf.exists():
        sys.exit(f"no such file: {pdf}")
    auth = {"Authorization": f"Bearer {token()}"}

    if a.prev:
        r = requests.post(f"{API}/deposit/depositions/{a.prev}/actions/newversion", headers=auth, timeout=60)
        r.raise_for_status()
        draft_url = r.json()["links"]["latest_draft"]
        dep = requests.get(draft_url, headers=auth, timeout=60).json()
        for f in dep.get("files", []):
            requests.delete(f"{API}/deposit/depositions/{dep['id']}/files/{f['id']}", headers=auth, timeout=60)
    else:
        r = requests.post(f"{API}/deposit/depositions", json={}, headers=auth, timeout=60)
        r.raise_for_status()
        dep = r.json()

    bucket = dep["links"]["bucket"]
    with open(pdf, "rb") as fh:
        u = requests.put(f"{bucket}/{pdf.name}", data=fh, headers=auth, timeout=600)
        u.raise_for_status()
    print(f"uploaded {pdf.name} ({pdf.stat().st_size / 1e6:.2f} MB)")

    r = requests.put(f"{API}/deposit/depositions/{dep['id']}", json=meta, headers=auth, timeout=60)
    if r.status_code >= 400:
        sys.exit(f"metadata rejected: {r.status_code} {r.text[:800]}")
    print("draft:", dep["links"]["html"])

    if a.publish:
        r = requests.post(f"{API}/deposit/depositions/{dep['id']}/actions/publish", headers=auth, timeout=120)
        if r.status_code >= 400:
            sys.exit(f"publish failed: {r.status_code} {r.text[:800]}")
        j = r.json()
        print("PUBLISHED  DOI:", j.get("doi"), " ", j["links"].get("record_html", j["links"].get("html")))
        (ROOT / a.record_out).write_text(json.dumps(
            {"doi": j.get("doi"), "conceptdoi": j.get("conceptdoi"), "id": j.get("id")}, indent=1) + "\n")


if __name__ == "__main__":
    main()
