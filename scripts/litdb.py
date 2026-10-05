#!/usr/bin/env python3
"""Local literature vector database for the quantum-fluids programme.

Layout (default root /mnt/data/home/xavkal/quantumfluids-data/litdb, override with $QF_LITDB; never inside the repo):
    manifests/<theme>.json   reviewer-written bibliographic manifests (papers + gaps), see docs/designs/LITDB.md
    pdfs/<id>.pdf            open PDFs fetched by `fetch` (arXiv, or a verified open URL)
    fetch_report.json        per-paper verification / download status
    chroma/                  persistent Chroma collection `qf_literature` (ONNX MiniLM-L6-v2 embeddings, cosine)

    litdb.py fetch                 verify every arXiv id against the arXiv API (title match), download PDFs politely
    litdb.py ingest                (re)build the collection: one 'card' per paper, one 'gap' per gap, 'chunk's of PDF text
    litdb.py query "text" [-n 8] [--kind card|chunk|gap] [--before YEAR] [--theme T]
    litdb.py stats

Run with the litdb venv:  $QF_LITDB/venv/bin/python scripts/litdb.py ...
A manifest entry whose arXiv id does not resolve, or resolves to a different title, is NOT downloaded and its card
is stored with verified = "MISMATCH"/"NOT_FOUND", so a fabricated or mistyped reference is visible, not silently used.
"""
from __future__ import annotations
import argparse, json, os, re, sys, time, hashlib
from pathlib import Path

ROOT = Path(os.environ.get("QF_LITDB", "/mnt/data/home/xavkal/quantumfluids-data/litdb"))
MAN, PDF, REPORT = ROOT / "manifests", ROOT / "pdfs", ROOT / "fetch_report.json"
UA = {"User-Agent": "qf-litdb/1.0 (research literature database; polite rate)"}


def norm(s: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", (s or "").lower())) - {"the", "a", "an", "of", "in", "and", "for", "on", "to", "with"}


def title_match(a: str, b: str) -> float:
    A, B = norm(a), norm(b)
    return len(A & B) / max(1, min(len(A), len(B)))


def safe(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s)


def load_manifests():
    out = []
    for f in sorted(MAN.glob("*.json")):
        try:
            m = json.loads(f.read_text())
        except Exception as e:                      # a reviewer may still be writing; report, do not crash
            print(f"SKIP {f.name}: {e}", file=sys.stderr); continue
        out.append((f.stem, m))
    return out


def arxiv_titles(ids: list[str]) -> tuple[dict[str, str], set[str]]:
    """Titles from the arXiv API for the ids it knows, and the set of ids whose batch was actually answered
    (an unanswered batch -- rate limit, network -- leaves its ids UNCHECKED, never NOT_FOUND)."""
    import requests
    res, answered = {}, set()
    for i in range(0, len(ids), 25):
        batch = ids[i:i + 25]
        url = f"https://export.arxiv.org/api/query?id_list={','.join(batch)}&max_results={len(batch)}"
        r = None
        for attempt in range(6):
            try:
                r = requests.get(url, headers=UA, timeout=90)
                if r.status_code == 200 and "<feed" in r.text:
                    break
            except Exception:
                pass
            r = None
            time.sleep(20 * (attempt + 1))                      # arXiv asks for patience after a 429
        if r is None:
            continue
        answered.update(batch)
        for e in r.text.split("<entry>")[1:]:
            idm = re.search(r"<id>https?://arxiv.org/abs/(.*?)</id>", e); tm = re.search(r"<title>(.*?)</title>", e, re.S)
            if idm and tm:
                res[re.sub(r"v\d+$", "", idm.group(1))] = re.sub(r"\s+", " ", tm.group(1)).strip()
        time.sleep(4)
    return res, answered


def download(url: str, dest: Path) -> str:
    import requests
    if dest.exists() and dest.stat().st_size > 10_000:
        return "have"
    r = None
    for attempt in range(4):
        try:
            r = requests.get(url, headers=UA, timeout=120, allow_redirects=True)
        except Exception as e:
            return f"error:{type(e).__name__}"
        if r.status_code not in (429, 503):
            break
        time.sleep(30 * (attempt + 1))
    if r.status_code != 200 or not r.content.startswith(b"%PDF"):
        return f"not_pdf:{r.status_code}"
    dest.write_bytes(r.content)
    return "downloaded"


def cmd_fetch(a):
    PDF.mkdir(parents=True, exist_ok=True)
    report = json.loads(REPORT.read_text()) if REPORT.exists() else {}
    mans = load_manifests()
    ids = sorted({re.sub(r"v\d+$", "", p["arxiv_id"].strip()) for _, m in mans for p in m.get("papers", []) if p.get("arxiv_id")})
    todo = [i for i in ids if report.get(i, {}).get("status") not in ("verified", "MISMATCH")]
    print(f"{len(ids)} distinct arXiv ids, {len(todo)} to verify")
    api, answered = arxiv_titles(todo)
    for theme, m in mans:
        for p in m.get("papers", []):
            aid = re.sub(r"v\d+$", "", p["arxiv_id"].strip()) if p.get("arxiv_id") else None
            if aid:
                rec = report.setdefault(aid, {})
                if rec.get("status") not in ("verified", "MISMATCH"):
                    if aid not in answered:
                        rec.update(status="UNCHECKED", manifest_title=p.get("title"))
                    elif aid not in api:
                        rec.update(status="NOT_FOUND", manifest_title=p.get("title"))
                    else:
                        s = title_match(p.get("title", ""), api[aid])
                        rec.update(status="verified" if s >= 0.6 else "MISMATCH", api_title=api[aid], manifest_title=p.get("title"), match=round(s, 2))
                if rec["status"] == "verified" and not a.no_download:
                    dest = PDF / f"{safe(aid)}.pdf"
                    st = download(f"https://arxiv.org/pdf/{aid}", dest)
                    rec["pdf"] = st
                    if st == "downloaded":
                        time.sleep(3)
            elif p.get("open_pdf_url") and not a.no_download:
                k = "url:" + hashlib.sha1(p["open_pdf_url"].encode()).hexdigest()[:12]
                rec = report.setdefault(k, {"status": "open_url", "manifest_title": p.get("title"), "url": p["open_pdf_url"]})
                if rec.get("pdf") not in ("have", "downloaded"):
                    rec["pdf"] = download(p["open_pdf_url"], PDF / f"{safe(p['key'])}_{k[4:]}.pdf")
                    time.sleep(2)
        REPORT.write_text(json.dumps(report, indent=1))
    from collections import Counter
    print("status:", dict(Counter(r["status"] for r in report.values())), " pdf:", dict(Counter(r.get("pdf", "-") for r in report.values())))
    for k, r in report.items():
        if r["status"] in ("MISMATCH", "NOT_FOUND"):
            print(f"  {r['status']} {k}: manifest '{r.get('manifest_title')}' vs arXiv '{r.get('api_title')}'")


def collection():
    import chromadb
    return chromadb.PersistentClient(path=str(ROOT / "chroma")).get_or_create_collection("qf_literature", metadata={"hnsw:space": "cosine"})


def chunks(text: str, size=1200, overlap=200):
    text = re.sub(r"[ \t]+", " ", text)
    i = 0
    while i < len(text):
        yield text[i:i + size]
        i += size - overlap


def cmd_ingest(a):
    import pymupdf
    col = collection(); report = json.loads(REPORT.read_text()) if REPORT.exists() else {}
    ids, docs, metas = [], [], []

    def flush(force=False):
        """Cards and gaps are always re-written (cheap, and their text may change); PDF chunks already in the
        collection are skipped, so a re-run only embeds what is new."""
        if ids and (force or len(ids) >= 256):
            ch = [i for i in ids if i.startswith("chunk:")]
            have = set(col.get(ids=ch, include=[])["ids"]) if ch and not a.rebuild else set()
            keep = [j for j, i in enumerate(ids) if i not in have]
            if keep:
                col.upsert(ids=[ids[j] for j in keep], documents=[docs[j] for j in keep], metadatas=[metas[j] for j in keep])
            ids.clear(); docs.clear(); metas.clear()

    seen_pdf = set(); n_card = n_gap = n_chunk = 0; no_text = []
    for theme, m in load_manifests():
        for p in m.get("papers", []):
            aid = re.sub(r"v\d+$", "", p["arxiv_id"].strip()) if p.get("arxiv_id") else ""
            ver = report.get(aid, {}).get("status", "no_arxiv") if aid else p.get("verified_how", "unverified")
            base = {"key": p.get("key", ""), "theme": theme, "year": int(p.get("year") or 0), "title": p.get("title", "")[:300],
                    "authors": ", ".join(p.get("authors", []))[:300], "venue": (p.get("venue") or "")[:200], "arxiv_id": aid,
                    "doi": p.get("doi") or "", "verified": ver, "read_depth": p.get("read_depth", "")}
            card = (f"{p.get('title')} — {base['authors']} ({base['year']}) {base['venue']}\nSUMMARY: {p.get('summary', '')}\n"
                    f"KEY NUMBERS: {'; '.join(p.get('key_numbers', []) or [])}\nOPEN QUESTIONS: {'; '.join(p.get('open_questions', []) or [])}\n"
                    f"RELEVANCE: {p.get('relevance', '')}")
            ids.append(f"card:{theme}:{p.get('key')}"); docs.append(card); metas.append({**base, "kind": "card"}); n_card += 1
            pdfs = [PDF / f"{safe(aid)}.pdf"] if aid else sorted(PDF.glob(f"{safe(p.get('key', '_'))}_*.pdf"))
            for pdf in pdfs:
                if not pdf.exists() or pdf.name in seen_pdf or ver in ("MISMATCH", "NOT_FOUND"):
                    continue
                seen_pdf.add(pdf.name)
                try:
                    doc = pymupdf.open(pdf)
                except Exception:
                    continue
                got = 0
                for pg, page in enumerate(doc):
                    for j, ch in enumerate(chunks(page.get_text())):
                        if len(ch.strip()) < 200:
                            continue
                        ids.append(f"chunk:{pdf.stem}:{pg}:{j}"); docs.append(ch); metas.append({**base, "kind": "chunk", "page": pg + 1}); got += 1
                    flush()
                n_chunk += got
                if got == 0:
                    no_text.append(pdf.name)
        for g_i, g in enumerate(m.get("gaps", [])):
            txt = f"GAP: {g.get('gap')}\nWHAT WE COULD DO: {g.get('what_we_could_do', '')}\nRISK ALREADY DONE: {g.get('risk_already_done', '')}\nSUPPORT: {', '.join(g.get('supporting_keys', []))}"
            ids.append(f"gap:{theme}:{g_i}"); docs.append(txt); metas.append({"kind": "gap", "theme": theme, "year": 0, "key": f"gap{g_i}", "title": (g.get("gap") or "")[:300]}); n_gap += 1
        flush(force=True)
    print(f"ingested: {n_card} cards, {n_gap} gaps, {n_chunk} chunks from {len(seen_pdf)} PDFs; collection size {col.count()}")
    if no_text:
        print("PDFs without a text layer (scans):", no_text)


def cmd_query(a):
    col = collection(); conds = []
    if a.kind: conds.append({"kind": a.kind})
    if a.theme: conds.append({"theme": a.theme})
    if a.before: conds.append({"year": {"$lt": a.before}}); conds.append({"year": {"$gt": 0}})
    where = None if not conds else conds[0] if len(conds) == 1 else {"$and": conds}
    r = col.query(query_texts=[a.text], n_results=a.n, where=where)
    for d, m, dist in zip(r["documents"][0], r["metadatas"][0], r["distances"][0]):
        head = f"[{m.get('kind')}] {m.get('key')} {m.get('year') or ''} {m.get('title', '')[:90]}" + (f" p.{m['page']}" if m.get("page") else "")
        print(f"--- {dist:.3f} {head} ({m.get('theme')}; {m.get('verified', '')})\n{d[:a.chars].strip()}\n")


def cmd_stats(a):
    from collections import Counter
    col = collection(); g = col.get(include=["metadatas"])
    kinds = Counter(m["kind"] for m in g["metadatas"]); print("collection:", col.count(), dict(kinds))
    cards = [m for m in g["metadatas"] if m["kind"] == "card"]
    print("cards per theme:", dict(Counter(m["theme"] for m in cards)))
    ys = [m["year"] for m in cards if m["year"]]
    print(f"years: min {min(ys)}, pre-1985 {sum(y < 1985 for y in ys)}, pre-2000 {sum(y < 2000 for y in ys)}, 2020+ {sum(y >= 2020 for y in ys)}; distinct titles {len({m['title'].lower() for m in cards})}")
    print("verification:", dict(Counter(m["verified"].split(':')[0] for m in cards)))
    print("PDF files:", len(list(PDF.glob('*.pdf'))), f"({sum(f.stat().st_size for f in PDF.glob('*.pdf')) / 1e6:.0f} MB)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch"); f.add_argument("--no-download", action="store_true"); f.set_defaults(fn=cmd_fetch)
    g = sub.add_parser("ingest"); g.add_argument("--rebuild", action="store_true", help="re-embed chunks already present"); g.set_defaults(fn=cmd_ingest)
    q = sub.add_parser("query"); q.add_argument("text"); q.add_argument("-n", type=int, default=8); q.add_argument("--kind"); q.add_argument("--theme")
    q.add_argument("--before", type=int); q.add_argument("--chars", type=int, default=700); q.set_defaults(fn=cmd_query)
    sub.add_parser("stats").set_defaults(fn=cmd_stats)
    a = ap.parse_args(); a.fn(a)
