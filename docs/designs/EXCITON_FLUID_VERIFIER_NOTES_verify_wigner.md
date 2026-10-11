# Verify: wigner package
Verdict: accept_with_fixes. No blocking problem found.
Independent recompute (own code, real-space image series instead of Laplace integral, own BZ sum): c=0.534241 (matches 0.53424),
16 gated/ungated gamma_h values on the registered grid match gated_scan.json to 5 digits. Without Richardson N=64/128 gives 0.5329/0.5336 -> extrapolates to 0.5343 (O(1/N) confirmed).
Literature re-read (arXiv PDFs): S1 290(30), 0.230(6), 4.446, gamma=sqrt<(r-rc)^2>/a_L; S3 r_QM=18+-4, T=0.014, N=36,90, Tm~0.09; S4 d_c=9.1 a_B*, a_B*=hbar^2/(e^2 m_qe), m_X=m_qe+m_qh, m_h/m_e=2.46, finite T; S5 d_c 29 vs 35 (~20%), gamma_c~0.3. All confirmed.
Arithmetic: Lambda_min 48.7 (46.4-51.5 anchors; 83 under A), 1.4% shift at D/d=5, window edges at Lambda=300, mapping 4.2 and 1.1-19, d~12 nm: all reproduce.
Prereg: docs committed 10:15, A1 10:17:57 before runs (10:18:39+), A2 10:33 after scan, disclosed. Scripts/results only committed at 10:48 (docs-before-run satisfied, code not).
Issues: (1) P1 refutation / 0.230 vs 0.263 depends on S1's <(r-rc)^2> being the full 2D displacement; not checked, ambiguity (factor sqrt2) would flip it. Worker admits it in report but prereg asserts "same definition". (2) 20% transfer error borrowed from S5 where it is on gate distance, not on n_c (n_c ~ gamma^-8). (3) analysis_summary.txt untracked; scan/refine logs ignored. (4) A1 says no number computed while lattice code was being debugged.
