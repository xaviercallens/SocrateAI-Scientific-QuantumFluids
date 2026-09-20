# MANIFEST — Henri Godfrin, open-access papers 2021 – Sept 2026

Retrieval date for every file below: **2026-09-20**.
Scope: publications of H. Godfrin (CNRS / Institut Néel, Grenoble) dated 2021-01 to 2026-09.
Sources searched: arXiv API (`au:Godfrin_H`, `au:Godfrin`), HAL API (`authLastName_s:Godfrin`, 2021–2026),
OpenAlex (author A5023987623), Crossref (`query.author=Godfrin`, from 2021), Semantic Scholar (authors 7329367,
152648536, 91141639), DataCite, Google Scholar profile (user lQehceoAAAAJ, sorted by date), web searches.
All sources agree: only **two** publications fall in the window. (Other 2021–2026 "Godfrin" arXiv entries are
Clément Godfrin, imec, silicon spin qubits — a different person.)

Only legally open material was fetched (arXiv, CC BY 4.0). No paywalled PDF, no shadow library.

## Paper 1 — Godfrin et al., PRB 103, 104516 (2021)

H. Godfrin, K. Beauvois, A. Sultan, E. Krotscheck, J. Dawidowski, B. Fåk, J. Ollivier,
"Dispersion relation of Landau elementary excitations and thermodynamic properties of superfluid 4He",
Phys. Rev. B 103, 104516 (published 29 March 2021). DOI 10.1103/PhysRevB.103.104516.
arXiv:2012.09067v1 (16 Dec 2020). HAL: hal-03197514.

| File | Source URL | Licence | sha256 (first 16) |
|---|---|---|---|
| `2021_godfrin_landau-dispersion-thermo-he4.pdf` (35 pp.) | https://arxiv.org/pdf/2012.09067v1 | CC BY 4.0 (arXiv abs page) | 8edc7c459c1843a1 |
| `src_2012.09067.tar` (gzip'd tar, full arXiv source incl. 59 EPS figures) | https://arxiv.org/src/2012.09067v1 | CC BY 4.0 | 5ca3f8d6077b6aac |
| `2021_godfrin_landau-dispersion-thermo-he4_src/2020-Dispersion-paper-v6d.tex` | extracted from the source bundle above | CC BY 4.0 | 78a8214fe11b62b0 |

Ancillary files (arXiv `anc/` directory, https://arxiv.org/src/2012.09067v1/anc ), all CC BY 4.0,
in `2021_godfrin_landau-dispersion-thermo-he4_anc/`:

| File | Content | Encoding note | sha256 (first 16) |
|---|---|---|---|
| `DispersionP0allRange.txt` | eps(k) at P=0, T<0.1 K, k = 0 … 3.6 Å⁻¹, 0.002 Å⁻¹ grid (1727 rows), with err(eps); below 0.15 Å⁻¹ ultrasound-based, no error column | ISO-8859-1, CRLF, tab-separated, 2 header lines, `--` = no value | 59ca6ea78dd08880 |
| `DispersionAllPressures.txt` | eps(k) ± err at P = 0, 0.51, 1.02, 2.01, 5.01, 10.01, 24.08 bar, k from 0.150 Å⁻¹, 0.002 grid (~1050 rows) | **UTF-16 LE**, CRLF, tab-separated, 3 header lines | 15a56ccdd2f681de |
| `Cv-and-Entropy.txt` | T, Cv total, err, Cv phonons, Cv rotons, S total (J/(K·mol)), T = 0.01 … 1.3 K | ASCII, CRLF | 9aa7cff247bcbc31 |
| `ExcitationsNumberDensity.txt` | T, N_phonon/atom, N_roton/atom, N_exc/atom | ASCII, CRLF | eecd824f9e084b10 |
| `Supplemental-v2.tex` | Supplemental Material text: Debye/maxon comparison, extended Landau analytic model (inverse series, DOS series, E, Cv, S, F coefficient formulas A…L including alpha_1 terms), roton parameters incl. B_R, C_R, Tables I–III | LaTeX | e734a6d87fe41c69 |
| `kDebye-kMaxon.eps` | figure for the Supplemental | EPS | 508852083b1a9ef6 |

Not downloaded:
- HAL copy https://hal.science/hal-03197514/document — open (HTTP 200, application/pdf, 4.9 MB) but it is the same
  arXiv manuscript with a HAL cover page; skipped as a duplicate.
- Publisher version of record http://link.aps.org/pdf/10.1103/PhysRevB.103.104516 — flagged "bronze" by OpenAlex
  (free to read at the publisher, no open licence). Not gold OA, so not fetched. The APS Supplemental Material
  is the same content as the arXiv `anc/` files.

Note: `../godfrin_2021_arxiv_ancillary/` already held `DispersionAllPressures.txt` and `DispersionP0allRange.txt`;
they are byte-identical to the copies here. The other four ancillary files are new.

## Paper 2 — Godfrin & Krotscheck, review (2022 preprint; 2024 book chapter)

Henri Godfrin, Eckhard Krotscheck, "The Dynamics of Quantum Fluids",
in Encyclopedia of Condensed Matter Physics, 2nd ed. (Elsevier, 2024), vol. 1, pp. 946–958.
DOI 10.1016/B978-0-323-90800-9.00029-9. arXiv:2206.06039v1 (13 Jun 2022). HAL: hal-03741738 (metadata + arXiv link only).

| File | Source URL | Licence | sha256 (first 16) |
|---|---|---|---|
| `2022_godfrin_dynamics-of-quantum-fluids.pdf` (16 pp.) | https://arxiv.org/pdf/2206.06039v1 | CC BY 4.0 (arXiv abs page) | 3877e8f8e0818efb |
| `src_2206.06039.tar` (gzip'd tar, full arXiv source) | https://arxiv.org/src/2206.06039v1 | CC BY 4.0 | 7795a735382191e6 |
| `2022_godfrin_dynamics-of-quantum-fluids_src/QF-Encyclopedia-v4d.tex` | extracted from the source bundle above | CC BY 4.0 | 202b007f09e21669 |

No ancillary (`anc/`) files exist for arXiv:2206.06039.
The PDF is byte-identical to `../godfrin_krotscheck_2022_review/arxiv_2206.06039.pdf`.

Not downloaded: the Elsevier book-chapter version (paywalled).

## Housekeeping

`src_tmp1/` and `src_tmp2/` are plain extractions of the two source tarballs (≈25 MB of EPS figures), left over from
the download step; they duplicate the `.tar` files and can be deleted.
