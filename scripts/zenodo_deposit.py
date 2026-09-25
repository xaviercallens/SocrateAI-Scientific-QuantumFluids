#!/usr/bin/env python3
"""Deposit a tagged release on Zenodo.

    python3 scripts/zenodo_deposit.py --tag v1.4.0 --new-version-of 22855582   # DRAFT, same concept DOI
    python3 scripts/zenodo_deposit.py --tag v1.4.0 --new-version-of 22855582 --publish
    python3 scripts/zenodo_deposit.py --tag v1.8.0 --update-draft 22895282     # replace an UNPUBLISHED
                                                                               # draft's files + metadata in place

Zenodo allows one unpublished draft per record line; use --update-draft to refresh it rather than
--new-version-of, which would be refused while the draft exists.

ALWAYS pass --new-version-of <id of the latest published record> for a release that continues an
existing line. Without it Zenodo creates a SEPARATE record with its own concept DOI, and the two
releases are then unrelated as far as citation is concerned. That happened between v1.2.0
(concept 10.5281/zenodo.22853895) and v1.3.0 (concept 10.5281/zenodo.22855581); they are linked
after the fact by related identifiers, which is not the same as being versions of one record.

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
    ap.add_argument("--new-version-of", dest="prev", default=None,
                    help="record id of the latest published version; keeps the concept DOI")
    ap.add_argument("--update-draft", dest="draft", default=None,
                    help="deposition id of an existing UNPUBLISHED draft to refresh in place")
    a = ap.parse_args()
    if a.prev and a.draft:
        sys.exit("--new-version-of and --update-draft are mutually exclusive")
    meta = json.loads((ROOT / "paper" / "zenodo_metadata.json").read_text())
    meta["metadata"]["version"] = a.tag
    auth = {"Authorization": f"Bearer {token()}"}

    with tempfile.TemporaryDirectory() as td:
        arc = Path(td) / f"SocrateAI-Scientific-QuantumFluids-{a.tag}.zip"
        subprocess.run(["git", "-C", str(ROOT), "archive", "--format=zip",
                        f"--prefix=QuantumFluids-{a.tag}/", "-o", str(arc), a.tag], check=True)
        files = [arc, ROOT / "paper" / "quantumfluids_lean4.pdf", ROOT / "paper" / "kinetic_known_answers.pdf",
                 ROOT / "paper" / "villani_tribute.pdf", ROOT / "paper" / "closed_loop.pdf",
                 ROOT / "paper" / "wasserstein_slack.pdf", ROOT / "paper" / "causal_topology.pdf",
                 ROOT / "paper" / "astro_topological_measurement.pdf", ROOT / "paper" / "sector_temperature.pdf"]
        if a.draft:
            dep = requests.get(f"{API}/deposit/depositions/{a.draft}", headers=auth, timeout=60).json()
            if dep.get("submitted"):
                sys.exit(f"deposition {a.draft} is already published; use --new-version-of instead")
            for f in dep.get("files", []):        # drop the draft's current files
                requests.delete(f"{API}/deposit/depositions/{dep['id']}/files/{f['id']}",
                                headers=auth, timeout=60)
        elif a.prev:
            r = requests.post(f"{API}/deposit/depositions/{a.prev}/actions/newversion",
                              headers=auth, timeout=60)
            r.raise_for_status()
            draft_url = r.json()["links"]["latest_draft"]
            dep = requests.get(draft_url, headers=auth, timeout=60).json()
            for f in dep.get("files", []):        # drop the previous version's files
                requests.delete(f"{API}/deposit/depositions/{dep['id']}/files/{f['id']}",
                                headers=auth, timeout=60)
        else:
            r = requests.post(f"{API}/deposit/depositions", json={}, headers=auth, timeout=60)
            r.raise_for_status()
            dep = r.json()
        bucket = dep["links"]["bucket"]
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
