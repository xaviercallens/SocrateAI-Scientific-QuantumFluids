# Peer review 1 of `paper/vortex_transport.tex` (received 2026-10-07; recorded verbatim before any change)

Source: external reviewer, pasted by the owner. Reproduced verbatim below; the response and the changes made are in
`docs/peer_review/vortex_transport_review_1_response.md`.

---

Here is a comprehensive peer review report for the manuscript.

### **Peer Review Report**

**Title:** Vortex transport and screening in a closed two-dimensional Bose field
**Author:** Xavier Callens
**Recommendation:** Major Revisions

---

### **1. Summary of the Manuscript**

The manuscript presents a rigorous computational investigation into the transport properties (mutual friction $\alpha$, transverse force $\alpha'$, and diffusion $\eta$) and screening behaviors of quantized vortices in a two-dimensional thermal Bose gas. Utilizing a microcanonical, energy-conserving projected Gross-Pitaevskii equation (PGPE), the author extracts these coefficients natively without introducing phenomenological damping or noise.

Methodologically, this paper is highly unique and groundbreaking: it applies clinical-trial-style pre-registration, automated gate-checking, and formal theorem proving (via Lean 4) to computationally verify point-vortex identities. Key physical findings include an empirical scaling relation $\alpha \approx 0.24 \rho_n/\rho$, a robust refutation of the Iordanskii transverse force (finding $\alpha' \approx 0$ after correcting for the $T=0$ fluid frame momentum), the diagnosis of anomalous finite-size stiffness as the artifact of a single unscreened box-scale pair, and a proposed "phonon wind" mechanism to explain vortex stalling.

---

### **2. Major Strengths**

* **Unprecedented Methodological Rigor:** The use of strict pre-registration, transparent reporting of failed controls (gates) and withdrawn claims, and the application of Lean 4 to formally verify analytical estimators sets a remarkable new gold standard for computational physics. This level of epistemic discipline directly combats the parameter-tuning biases that frequently plague numerical simulations.
* **Resolution of the Transverse Force Controversy:** The author's careful subtraction of the $T=0$ kinematic baseline (the compressible pair speed and torus frame velocity) to accurately measure $\alpha'$ is physically astute. Demonstrating that the raw negative $\alpha'$ values are finite-size kinematic artifacts—and that the true value is zero within 1%—provides exceptionally clean support for Thouless over Iordanskii in this regime.
* **Identification of Imprint Artifacts:** Discovering that the standard vortex phase imprint used by the numerical community introduces a $1/r^2$ tail—leading to spurious acoustic radiation and pair drift—is a profound technical contribution that will immediately benefit other PGPE modelers.
* **Diagnosis of Finite-Size Anomalies:** The deduction that depressed superfluid fractions in finite boxes stem from a single, long-lived, unscreened box-scale pair (decaying on a highly extended timescale) rather than thermodynamic Onsager clustering successfully resolves significant confusion in the existing literature.

---

### **3. Major Weaknesses and Required Revisions**

* **A. Complete Absence of Figures:**
The manuscript contains no figures and makes no reference to any. In computational physics, visualizing the data is strictly necessary for readers to evaluate the claims. The author must include standard plots, such as:
* A plot of $\alpha$ and raw/corrected $\alpha'$ versus temperature ($T/T_{BKT}$) or $\rho_n/\rho$.
* A log-log plot of the tracking residuals (mean-square displacement) versus lag time to visually justify the quoted scaling exponents for diffusion (0.71, 0.82, 1.28).
* A plot of vortex separation $d$ vs. time demonstrating the "stalled pair" dynamics discussed in Section 4.
* The static structure factor $\langle\vert{}\rho_q(k)\vert{}^2\rangle/k^2$ demonstrating the $k$-independent plateau matching the KT polarizability (Section 6).


* **B. The Unrun "Decisive Control" (Section 4):**
The author proposes a fascinating "phonon wind stall" mechanism to explain why shrinking vortex pairs stop annihilating in closed boxes, noting that the shed impulse creates a counterflow. However, the text explicitly states: *"The decisive box-size control [the $L=96$ box] is not run; the hypothesis is unresolved."*
In a numerical study, proposing a testable physical mechanism but choosing not to run the decisive simulation is unacceptable for a full research article. The author must run the $L=96$ control to confirm or refute the hypothesis. If compute resources are strictly exhausted, this section must be heavily truncated and framed explicitly as speculation for future work.
* **C. Narrative Flow and Bureaucratic Jargon:**
While the commitment to open science is applauded, the manuscript currently reads less like a standard scientific paper and more like a software audit log. The heavy reliance on internal compliance jargon (e.g., "G1 passes", "amendment A1.2", "LEDGER CLAIM-078", "E1 pass (6/6)") severely obscures the underlying physics for a general audience.
* *Action:* The author should heavily restructure the manuscript. The rigorous accounting of "gates," pre-registrations, and amendments should be compiled into a dedicated "Methods and Open Science Protocol" section or an Appendix. The main text must flow as a continuous physics narrative.


* **D. Justification of the $T=0$ Baseline Correction (Section 3):**
The conclusion that $\alpha' \approx 0$ rests entirely on subtracting the fluid's mean velocity ($u = P/nL^2$) and the Jones-Roberts compressible correction. Because this directly refutes the Iordanskii value ($\rho_n/\rho$), the author must explicitly justify the physics of this subtraction in the main text. Explain *why* the proper definition of the normal-fluid transverse force requires evaluating it in this specific Galilean frame.

---

### **4. Minor Comments & Suggestions**

* **Explicit Equations for the Corrected Imprint (Section 2):** Because fixing the $1/r^2$ tail artifact in the standard vortex imprint is such an important technical achievement, please provide the exact mathematical formulas for the corrected "periodic phase and a Bernoulli amplitude" (imprint_v2) in the text or an appendix so others can easily implement it.
* **Anomalous Diffusion and the Einstein Relation (Section 3):** The Einstein relation is deemed "inconclusive by rule" because the scaling exponents of the displacement fluctuate ($0.71 \to 0.82 \to 1.28$). Extracting a standard diffusion constant $\eta$ when dynamics are sub-diffusive (0.71) is mathematically ill-posed. The author should provide a brief physical interpretation of *why* this anomalous diffusion occurs at short lags (e.g., is the sub-diffusion a result of the vortex temporarily interacting with its own acoustic radiation?).
* **Context for Lean 4 (Section 2):** Mentioning Lean 4 highlights the paper's rigor, but many physicists will not understand its significance. Please add 1-2 sentences explaining exactly *what* Lean 4 verified (e.g., formally proving that the discrete estimators algebraically match the continuous point-vortex Hamiltonian identities).
* **Formatting Typo (Section 5):** The column header "$R_{\text{yortex}}$" in the table contains a typo ("y" instead of "v"). Additionally, the raw Markdown tables (using `|` pipes) should be properly typeset according to standard journal formatting guidelines.
* **Underselling the Results (Abstract):** The abstract concludes with: *"No physics is claimed as new; the numbers, the refutations and the method are."* This is an unnecessary undersell. Establishing the relation $\alpha \approx 0.24 \rho_n/\rho$, resolving finite-size stiffness anomalies, and definitively refuting the Iordanskii prediction in a closed Bose field *are* new physics contributions. The author should revise this to accurately reflect the scientific merit of the paper.
