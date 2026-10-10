Inventory of ch01.tex (304 lines) and ch02.tex (563 lines). I read every line of both; no line is over 2000 characters, and I created and edited no files.

Notes on how to read this:
- **No number macros.** Neither chapter prints a value through a macro; every number is typed literally. The macros are for notation only (qfbook.sty l. 50–52):
  - `\dd` = `\mathrm{d}`, `\ii` = `\mathrm{i}`, `\ee` = `\mathrm{e}`
  - `\lean{x}` = `\texttt{x}`
  - `\Lthm{M}{n}` prints `QuantumFluids.M.n`
- **JSON keys.** Keys from figures/ch01_numbers.json and figures/ch02_numbers.json are given for cross-checking. Every value I compared agrees with its key.
- **Pipes in tables.** Inside table cells a `|` of the LaTeX source is written `\|` (the Markdown escape). The source's own `\|` (norm) occurs only at ch01 l. 175 and is quoted outside tables.
- **Spot-checks outside ch01/ch02.** These are grep only, not a reading, and are marked "spot-check" in section E.

## ch01 — A Tribute: The Bench, the Proof and the Solver
### A. Units and conventions
- **Neutron units.**
  - `$E=\hbar^2k^2/2m_n=(81.80\ \mathrm{meV\,\text{\AA}^2})/\lambda^2$` with `$k=2\pi/\lambda$` (l. 43).
  - Wavelengths are in Å, k and Q in `\AA$^{-1}$`, energies in meV, speeds in m/s (l. 43–66).
- **ħ²/2m_n.** `$\hbar^2/2m_n=2.072$~meV\,\AA$^2$` (l. 295). This is consistent with 81.80 = (2π)²·2.072.
- **meV and K side by side.**
  - "a maximum of 1.19~meV (13.8~K)", "the minimum of 0.741~meV (8.6~K)" (l. 47).
  - "costs 8.6~K" (l. 36); "costs 0.74~meV" (l. 43).
  - The meV↔K factor is never printed (JSON `bench.constants.meV_in_K` = 11.6045).
- **Other practical units.**
  - Photon: keV, mm (l. 43).
  - Cryogenic temperatures: `$100\,\mu$K`, `8~mK` (l. 21).
  - Cross section: barn at `2200~m/s`, "growing in inverse proportion to the speed" (l. 36).
  - Table rounding: `$5\times10^{-5}$~meV` (l. 51).
  - Phase velocity `$\varepsilon/\hbar Q$` in m/s, and as a fraction of c: `$0.24\,c$` (l. 66).
- **Landau chain.**
  - `\frac{E}{V}=\int\!\frac{\dd^3k}{(2\pi)^3}\,\frac{\varepsilon(k)}{e^{\varepsilon(k)/k_BT}-1},\qquad C_V=\frac{\partial E}{\partial T}` (l. 76). The measure is d³k/(2π)³ and the Bose factor uses an italic e.
  - `A=\frac{2\pi^2k_B^4V}{15\,\hbar^3c^3}` (l. 80) contains V. So "specific heat" C_V is in fact the heat capacity of volume V.
- **Lean statements carry no units.** For example `debyeEnergy (V kB hbar c I T : ℝ)` (l. 118).
  - Statement 2 writes the model without ħ: `$\varepsilon=ck(1+ak^2)$` (l. 136).
  - Elsewhere the dispersion is `$\varepsilon=\hbar ck\,(1+\alpha_2k^2+\dots+\alpha_6k^6)$` (l. 31, 82).
- **Phases.**
  - Principal interval `$(-\pi,\pi]$` (l. 163, 297); phase steps "in radians" (l. 224).
  - Windings are given in units of 2π (l. 239, 243, 259); circulation as `$\oint\mathbf v\cdot\mathrm d\mathbf l/\kappa$` (l. 245).
- **Circulation quantum.** "the quantum `$\kappa=h/m$`" (l. 163); "with `$\kappa=2\pi\hbar/m$`" (l. 245).
- **Dimensionless GP units.** "in units `$\hbar=m=g=1$` and with background density 1, so that the speed of sound `$c=1$` and the healing length `$\xi=1$` are the units of speed and length, and `$\xi/c$` the unit of time" (l. 186).
  - No formula for ξ or c is given anywhere in ch01.
- **Model equation.** `i\,\partial_t\psi=\mathcal P\Bigl[-\tfrac12\nabla^2\psi+|\psi|^2\psi\Bigr]` (l. 184).
  - No g appears, and the i is italic.
  - `\mathcal P` is the projector "on the Fourier modes below a cutoff"; the cutoff value is never given (l. 186).
- **Box and grid.**
  - "The box has side `$L=64\,\xi$` and `$128^2$` points" (l. 186); code comment `# 128^2 points, box 64 xi; g = 1` (l. 192).
  - The grid spacing is never stated. 0.5 ξ is implied (64/128; code l. 220 `int(round(x / 0.5))`).
  - The imprint positions (26,32) and (38,32) are in ξ (l. 186).
- **Time step.** Never stated in prose. `# 1000 RK4 steps in one call` for `s.run(c0, 10.0)` (l. 195) implies Δt = 0.01.
- **Speeds and momentum.**
  - "a budget of the speed in units of `$c$`" (l. 253).
  - "moves at `$1/d$` (in these units)" (l. 249).
  - "`$P\approx2\pi d$` (per unit density, in these units)" and "`$u=P/N$` (`$N$` the norm)" (l. 257).
- **Lengths in ξ.** Used throughout (l. 239, 245, 249, 259, 261), including `$(\xi/d)^2$` (l. 261).
- **Exercise 3.** "(units `$\hbar/m=1$`, density 1)" (l. 299).
- **Temperature of the sweep.** "the programme's own `$T=0$` sweep" (l. 259): classical-field runs at zero temperature.
- **Run metadata.** Wall-clock seconds and load averages (l. 224, 261), explicitly "not a benchmark".

### B. Symbols
| symbol (LaTeX as in source) | meaning in this chapter | units / convention | line(s) where defined or first used | remarks |
|---|---|---|---|---|
| `\lambda`, `\lambda_i` | neutron wavelength; incident wavelength | Å | 43, 51, 64, 295 | cross-chapter: λ is an eigenvalue / stiffness parameter in ch02 |
| `k` | (a) neutron wave number `$k=2\pi/\lambda$`; (b) wave number of an excitation in `\varepsilon(k)` and in the Landau chain | Å⁻¹ | (a) 43; (b) 31, 76–82, 136 | (i) same letter for the neutron and the excitation; Lean `k : ℝ` in `phononDisp` (130), `k : V` (a vector) in `energy` (169) |
| `\mathbf k_i`, `\mathbf k_f`; `k_i`, `k_f` | incident and final neutron wave vectors and their magnitudes | Å⁻¹ | 45, 55, 59, 175, 295 | Lean `ki kf : V` (171) |
| `\mathbf Q`, `Q` | wave-vector transfer `$\mathbf Q=\mathbf k_i-\mathbf k_f$` and its magnitude | Å⁻¹ | 45, 47, 55–66, 175 | standard neutron usage; ε(Q) at l. 45 and ε(k) at l. 31 name the same curve; cross-chapter: Q is a quartic sum in ch02 |
| `Q_0`, `\varepsilon_0` | roton wave number and energy | Å⁻¹, meV | 295 | 1.92 Å⁻¹, 0.741 meV |
| `E`, `E_i`, `E_f` | neutron kinetic energy (incident, final) | meV | 43, 45, 55, 57, 64, 175, 295 | (i) E is also the energy of the excitation gas (76) and the T⁷ coefficient (31, 82) |
| `E` in `\frac{E}{V}`, `\partial E/\partial T` | energy of the excitation gas in volume V | energy | 74–76 | (i) see the row above |
| `m_n` | neutron mass | via `\hbar^2/2m_n=2.072` meV Å² | 43, 57–61, 295 | l. 175 and Lean Statement 5 (169–172) write plain `m` for the neutron mass |
| `\hbar\omega`, `\omega` | energy transfer `$\hbar\omega=E_i-E_f$`; ω is its angular frequency | meV | 45 | cross-chapter: in ch02, ω_k = ½\|k\|² |
| `S(\mathbf Q,\omega)` | dynamic structure factor | — | 45 | — |
| `\varepsilon`, `\varepsilon(k)`, `\varepsilon(Q)` | excitation energy, the dispersion relation | meV (also K) | 31, 45, 47, 55–66, 76–82, 136 | the Statement 2 model `$\varepsilon=ck(1+ak^2)$` has no ħ (136) |
| `v_n` | neutron speed | m/s | 61, 64 | eq. `ch01:eq-vmin` |
| `c` | speed of sound: the He-4 value extrapolated from the table (51, 64, 66, 286); the phonon velocity in `\varepsilon=\hbar ck` (31, 78–82); equal to 1 in GP units (186) | m/s, or 1 in GP units | 31, 51, 64, 66, 78–82, 186, 286 | Lean parameter `c` (118, 130); (i) the Python variables `c`, `c0` are the engine state (194–195) |
| `a` | (a) coefficient of the fit `$\varepsilon/\hbar Q=c(1+aQ^2)$` on 0<Q≤0.2 Å⁻¹; (b) cubic coefficient of the model `phononDisp c a k` = ck(1+ak²) | not stated | (a) 51; (b) 130–136 | plays the role of α₂; phonon decay is open iff a ≥ 0 (133); Lean `pdiff (a b : ℝ)` uses a and b as plain arguments (148) |
| `\alpha_n` (`\alpha_1`…`\alpha_6`) | coefficients of the dispersion series, with `$\alpha_1=0$` | not stated | 31, 82 | (ii) α is a dispersion coefficient here, not a friction or fine-structure constant |
| `C_V` | "specific heat", `C_V=\partial E/\partial T` | energy/temperature; ∝ V | 31, 74–82 | (ii) a total heat capacity, since A ∝ V, though called specific heat |
| `A` | T³ coefficient, `A=\frac{2\pi^2k_B^4V}{15\,\hbar^3c^3}` | — | 31, 80, 82, 126 | (i) A is also loop A in the triptych figure (239, 243) |
| `C`, `D`, `E`, `K`, `L` | coefficients of T⁵, T⁶, T⁷, T⁸, T⁹ in Eq. (22) | — | 31, 82, 126 | (ii) C is not a heat capacity, E not an energy, K not kelvin, L not a length. (i) L is also the box side (186, 259, 299); K is also the kelvin unit (36, 47); C and D are also loop labels (239, 243); E is also an energy. The letters are as printed: no B (no T⁴ term) and F–J unused. ζ(7) and ζ(9) appear only in D and K (82) |
| `T` | temperature | K | 74–82; "`$T=0$`" at 259 | — |
| `V` | volume | — | 74, 80; Lean `V : ℝ` at 118 | (i) in Statement 5, `V : Type*` with `[NormedAddCommGroup V]` is the space of wave vectors (167–171) |
| `k_B` | Boltzmann constant | value not printed | 76, 80, 126; Lean `kB` at 118 | — |
| `\hbar`, `h` | reduced Planck constant; Planck constant | ħ = 1 in GP units (186) | ħ from 43; h at 163 | Lean `hbar` (118, 169); (i) in the Python code `h` is the half-side of a loop (208–213) |
| `I` (Lean only) | value of the Bose integral passed to `debyeEnergy`, set to `π ^ 4 / 15` | — | 118–122, 126 | — |
| `t` | (a) integration variable of the Bose integral; (b) time | (b) in units of ξ/c | (a) 78; (b) from 180 | (i) |
| `\zeta(n)` | Riemann zeta values ζ(4)…ζ(10) | — | 82 | — |
| `k_1`, `k_2` (Lean `k₁ k₂`) | wave numbers of the two phonons in a collinear decay | — | 132–136 | — |
| `F` (Lean `F : ℝ`) | the single Landau parameter of the 2D collisionless kinetic equation | dimensionless | 140–144, 272 | (ii) not a free energy or force; it carries no index here (spot-check: ch08 l. 59 defines F ≡ F_0^s) |
| `s` | zero-sound phase velocity in units of v_F; root `$s=(1+F)/\sqrt{1+2F}$` | dimensionless | 141, 144 | (ii) not entropy or spin; the mode is undamped for s>1; (i) the Python `s` is the engine object (192) |
| `v_F` | Fermi velocity | — | 144 | — |
| `v_L` | Landau critical velocity, the minimum of ε/ħQ | m/s | 66, 286 | — |
| `\theta_i` (Lean `θ : ℕ → ℝ`) | phases of the field at the points of a closed loop | rad | 150–163, 297 | `θ n = θ 0` closes the loop |
| `pdiff` / `\mathrm{pdiff}` | principal value in (−π,π] of the phase step b−a (`toIocMod two_pi_pos (-π) (b - a)`) | rad | 148, 163, 297 | Python version at 205 |
| Lean `n : ℕ`, `m : ℤ` | number of steps of the loop; the integer m with sum = m·2π | — | 150–152 | (i) m is a mass elsewhere (163, 169, 180); n is a density or winding elsewhere (259) |
| `\kappa` | quantum of circulation, `$\kappa=h/m$` = `$2\pi\hbar/m$` | equals 2π in GP units, though ch01 does not say so | 163, 245 | — |
| `m` | mass of the Bose particle | 1 in GP units | 163, 180, 186, 299 | (i) also the neutron mass in Statement 5 (169–175) and the Lean integer (151) |
| `\psi(\mathbf r,t)` | complex field of the Bose-condensate model | GP units | 180, 184 | — |
| `\mathbf v`, `v_y` | superfluid velocity `$\mathbf v=(\hbar/m)\nabla\arg\psi$` and its y-component | units of c | 180, 245, 259, 299 | (i) compare v_n, v_F, v_L |
| `\arg\psi` | phase of ψ | rad | 180, 239 | — |
| `\mathcal P` | projector on the Fourier modes below a cutoff | cutoff not given | 184, 186 | cross-chapter: ch02 writes a plain P; in ch01, P is a momentum |
| `g` | contact coupling, set to 1 | GP units | 186, 192 | not written in the equation at 184 |
| `\xi` | healing length, equal to 1 and the unit of length | — | 186, 239, 245, 249, 259, 261 | no formula in ch01; ξ = 1 requires ξ = ħ/√(mgn) = ħ/(mc) (see E) |
| `\xi/c` | unit of time | — | 186 | — |
| `L` | side of the periodic box, 64 ξ | ξ | 186, 239, 259, 299 | (i) L is also the T⁹ coefficient |
| `d` | vortex–antivortex separation | ξ | 249–261, 299 | — |
| `P` | momentum of the pair or of the field, `$P\approx2\pi d$` per unit density | GP units | 253, 257 | not the same as `\mathcal P`; cross-chapter: ch02 uses P for the projector |
| `N` | the norm of the field (4096 = L² × density 1 here) | GP units | 257 | cross-chapter: in ch02, N is the grid size |
| `u` | mean velocity of the whole fluid, `$u=P/N$` | units of c | 253, 257, 259 | — |
| `n_{\rm in}`, `n_{\rm out}`, `n(x)` | phase windings (integers) along vertical cycles inside and outside the pair; at abscissa x | integers | 259, 299 | (i) n is also the density (259) |
| `n` | density of the field ("the density `$n$` is not uniform") | background density 1 | 259 | (i) |
| `x`, `y`, `\mathbf r` | box coordinates (the pair moves along y); position | ξ | 180, 253, 259, 299 | — |

**Lean-only notation**
- **Statement 1:**
  - `debyeEnergy (V kB hbar c I T : ℝ)` = `V / (2 * π ^ 2) * (kB * T) ^ 4 / (hbar * c) ^ 3 * I`
  - `debye_specific_heat` (118–123)
- **Statement 2:** `phononDisp (c a k : ℝ)`, `three_phonon_open_iff {c a k₁ k₂ : ℝ}` (130–133).
- **Statement 3:** `zero_sound_2d_iff (F : ℝ)` with `∃ s` (140–141).
- **Statement 4:** `pdiff`, `loop_sum_eq_mul (θ : ℕ → ℝ) (n : ℕ) (hclosed : θ n = θ 0)`, `∃ m : ℤ`, `toIocMod`/`toIocDiv two_pi_pos (-π)` (148–160).
- **Statement 5:**
  - `variable {V : Type*} [NormedAddCommGroup V]`
  - `energy (hbar m : ℝ) (k : V)` = `hbar ^ 2 * ‖k‖ ^ 2 / (2 * m)`
  - `min_incident_wavevector (hbar m : ℝ) (hbar0 : 0 < hbar) (hm : 0 < m) (ki kf : V) (hQ : 0 < ‖ki - kf‖)` (167–172)
  - The text writes `$Q=\|\mathbf k_i-\mathbf k_f\|>0$` and `$Q/2+m(E_i-E_f)/\hbar^2Q$` (l. 175).
- **Named but not shown:**
  - `\Lthm{BoseIntegral}{mellin_bose_four}`, `\Lthm{PhononSpecificHeat}{phonon_specific_heat}`, module `PhononSeries` (126)
  - module `HeliumKinematics` (136)
  - `\Lthm{VortexWinding}{pdiff_eq}`, `\Lthm{QuantizedCirculation}{circulation_quantized}`, `\Lthm{VortexWinding}{pdiff_add_rev_eq_two_pi_iff}`, module `ContinuumWinding` (163)
  - `\Lthm{VortexWinding}{loop_sum_eq_mul}` (297, 299)

### C. Physical constants and material values quoted
| quantity | value as printed in the text (and units) | source the chapter itself gives | line | remarks |
|---|---|---|---|---|
| base temperature of the group's dilution refrigerators | `8~mK` | "the institute's own pages" (l. 18); no \cite | 21 | a capability of the lab, not the temperature of an experiment |
| nuclear adiabatic-demagnetization cryostats | "reach about `$100\,\mu$K`" | same | 21 | same |
| ³He neutron absorption cross section | `5333~barn` at `2200~m/s`, ∝ 1/speed | `\cite{Sears1992}` | 36 | — |
| roton energy | `8.6~K` (36); `0.74~meV` (43); `0.741~meV (8.6~K)` at `$Q=1.92$~\AA$^{-1}$` (47); `$Q_0=1.92$`, `$\varepsilon_0=0.741$~meV` (295) | the authors' table, an ancillary file of the arXiv version of `\cite{Godfrin2021}` (47); figure script `figures/ch01_bench.py` (51) | 36, 43, 47, 295 | JSON `bench.roton`: 0.7413 meV, 8.602 K, Q0 1.92; file `data/external/godfrin_2021_arxiv_ancillary/DispersionP0allRange.txt` |
| maxon | `1.19~meV (13.8~K)` at `$Q=1.11$~\AA$^{-1}$` | same table | 47 | `bench.maxon`: 1.1914 meV, 13.826 K, Q 1.114 |
| the dispersion table | 1727 rows, Q = 0 to 3.6 Å⁻¹, an uncertainty given for 34 of them; superfluid ⁴He at saturated vapour pressure; "author-processed values, not raw counts" | `\cite{Godfrin2021}` ancillary file | 31, 47, 51 | `bench.table` |
| table rounding | `$5\times10^{-5}$~meV` | — | 51 | `bench.symmetric_split.table_rounding_meV` |
| neutron energy vs wavelength | `$E=\hbar^2k^2/2m_n=(81.80\ \mathrm{meV\,\text{\AA}^2})/\lambda^2$` | no source given (ħ and m_n are not printed) | 43 | `bench.constants.E_over_lambda2_meV_A2` = 81.804 |
| ħ²/2m_n | `2.072`~meV Å² | no source given | 295 | `bench.constants.hbar2_over_2m_neutron_meV_A2` = 2.07212 |
| a 5 Å neutron | `3.27~meV`, `791~m/s` | computed | 43 | `bench.photon_at_5A`: 3.2722 meV, 791.21 m/s; v·λ = 3956.03 m/s·Å is in the JSON only (`bench.constants.neutron_v_times_lambda_ms_A`) |
| roton energy as a share of the 5 Å neutron's energy | "23 per cent" | computed | 43 | 0.7413/3.272 |
| a 5 Å photon | `2.48~keV`, "about 760\,000 times more"; a photon with the neutron's energy has a wavelength of `0.38~mm` | computed | 43 | JSON: 2.4797 keV, ratio 757 811, 0.3789 mm |
| threshold to create the roton | `663~m/s`, `$\lambda_i\le5.97$~\AA`, `$E_i\ge2.30$~meV` | computed from eq. `ch01:eq-vmin` on the table | 64 | `bench.roton`: 663.10, 5.966, 2.298 |
| reaching Q = 3.6 Å⁻¹, Q = 3 Å⁻¹, and Q→0 | `$\lambda_i\le3.30$`, `$\lambda_i\le3.88$`, `$\lambda_i\le16.6$`~Å; ε at 3 Å⁻¹ = `1.478~meV` (295) | computed | 64, 295 | `bench.end_of_table` 3.2997; `bench.at_Q3` 3.8811 and 1.4784; `bench.lam_max_at_Q_to_zero_A` 16.573 |
| kinematic-limit curves drawn in the figure | `$\lambda_i=6$, 5 or 4~\AA` | the figure's choice | 51 | "limits of kinematics, not instrument settings" |
| IN5 incident wavelengths | `$1.8$ to 20~\AA` | `\cite{ILLIN5}` | 64 | — |
| spectrometers | IN6 (2012 measurement), IN5 (2021), both at the ILL | `\cite{Godfrin2012}`, `\cite{Godfrin2021}`, `\cite{ILLIN5}` | 27, 31, 45 | the temperatures of the two measurements are not given in ch01 |
| speed of sound, ⁴He at SVP | `239~m/s`; `$c\approx239$~m/s` | "our extrapolation" (286), from the fit of l. 51; `figures/ch01_bench.py` | 66, 286 | `bench.sound.c_fit_ms` = 238.70; this is not a quoted literature value |
| phase-velocity maximum | `251~m/s` at `$Q=0.35$~\AA$^{-1}$`, a rise of 5.3 per cent; back through c at `$0.57$~\AA$^{-1}$` | computed | 66 | `bench.sound`: 251.25, Q 0.348, 5.25 %; `bench.vph_back_to_c_Q` 0.566 |
| Landau critical velocity | `57.9~m/s`, `$0.24\,c$`, at `$Q=1.97$~\AA$^{-1}$` | computed | 66 | `bench.landau`: 57.888, 0.2425, Q_L 1.966 |
| symmetric split ε(k) ≥ 2ε(k/2) | holds for `$0.10\le k<0.45$~\AA$^{-1}$` | computed on a cubic spline of the table | 51, 136 | `bench.symmetric_split.first_negative_k` 0.4528 |
| Bose integral | `$\int_0^\infty t^3/(e^t-1)\,\dd t=\pi^4/15$` | Lean `\Lthm{BoseIntegral}{mellin_bose_four}` | 78, 126 | — |
| 2D zero-sound root | `$s=(1+F)/\sqrt{1+2F}$` | the Lean proof in `ZeroSound`; `\cite{BaymPethick1991}` | 144 | — |
| Lean library and toolchain | "indexes 310 theorems"; Lean 4.34.0-rc2, Mathlib v4.34.0-rc2 | `\cite{Callens2026lib}` | 114, 285 | — |
| simulation set-up (GP units) | `$L=64\,\xi$`, `$128^2$` points, charge +1 at (26,32) and −1 at (38,32), run to t = 10 ("1000 RK4 steps") | the code box; `figures/ch01_triptych.py` | 186, 192–195, 239 | `triptych.N` 128, `L` 64, `imprint` |
| invariants of the run | energy `2069.113131399` → `2069.113131436`; norm `4096.000000000` → `4096.000000033`. Relative drifts over 10 time units: energy `$1.8\times10^{-11}$`, norm `$8.0\times10^{-12}$`, momentum `$2.0\times10^{-11}$`. Over 60 time units: `$8.6\times10^{-11}$`, `$4.3\times10^{-11}$`, `$5.5\times10^{-11}$` | output of the code box | 226–227, 247 | JSON `snippet.output`, `triptych.*_rel_drift`, `budget.*_rel_drift_60` |
| vortex positions and separation at t = 10 | `[[26.123, 32.902], [37.877, 32.902]]`; `$11.75\,\xi$` | the code box | 228, 239 | — |
| largest phase step | `0.216~rad`, `$0.07\,\pi$`; the sums are integers to within `$1.4\times10^{-16}$` | `figures/ch01_triptych.py` | 243 | `triptych.max_abs_pdiff_step_over_pi` 0.0688 |
| loop circulations | exact: `+1.000000000000`, `-1.000000000000`, `$-5.30\times10^{-17}$`, `$-1.44\times10^{-17}$`; trapezoid rule: 0.9966, 0.9977, 0.9987, 0.9994 for half-sides 2, 2.5, 3.5 and 4.5 ξ | computed | 245 | `triptych.loops`; `triptych.trapezoid_loop_A_by_half_side_xi` |
| pair speed | measured `0.0932` (fits 0.0936, 0.0932, 0.0928; uncertainty 0.4 %); planar `0.0850` at `$d=11.76\,\xi$` (s.d. 0.02); torus `0.0757`; "23 per cent more" | `figures/ch01_budget.py`; torus formula from `\cite{WeissMcWilliams1991}` | 249 | `budget.fits`; ratio 1.2312 |
| mean flow | `$u=0.0177$` (P/N) gives a prediction of 0.0934, −0.3 % from the measurement; `$u=2\pi\,11.75/L^2=0.0180$` from the windings; difference 1.6 per cent; cycle integers within `$5.2\times10^{-14}$` | computed | 257–261 | `budget.u_mean_flow_P_over_N`, `u_from_windings`, `u_P_over_u_windings` |
| density at the vortex cores | falls to `0.016` | computed | 259 | `triptych.min_density` 0.0159 |
| the programme's T = 0 sweep | ratio to the torus formula 1.06 (d = 6ξ) to 1.49 (d = 16ξ) in the box frame; 1.004–1.005 for d = 8–16 ξ once the mean flow is subtracted | `\cite{Callens2026a}` | 259 | — |
| finite-size correction | `$+0.4$` per cent for `$d\ge8\,\xi$`, of order `$(\xi/d)^2$` | the programme's own T = 0 runs (for the solitary-wave family, `\cite{JonesRoberts1982}`) | 261 | — |
| run metadata | 9.4 s wall time (5.0 s CPU), load average 18.5; 181 s, load average 20.2 | — | 224, 261 | "not a benchmark" |

**Not printed anywhere in ch01:**
- numerical values of ħ, h, k_B and m_n;
- the masses of ⁴He and ³He;
- the density or molar volume of ⁴He;
- the meV↔K conversion factor;
- the temperatures of the 2012 and 2021 measurements.

### D. Glossary terms introduced in this chapter
| term | one-line definition in the chapter's own sense | line of first introduction/definition |
|---|---|---|
| bench, proof, solver | the three instruments: the experiment ("a number about nature together with the procedure and the error bar"), a statement about a model checked in Lean, and the integration of a model with rusty-SUNDIALS | 7 (table 92–105) |
| dispersion relation | the energy of an excitation as a function of its wave number; "the one curve from which the rest follows" | 5 |
| phonon, maxon, roton | the three regions of Landau's spectrum: the phonon branch at small Q, the maxon maximum (1.19 meV at 1.11 Å⁻¹), and the roton minimum (0.741 meV at 1.92 Å⁻¹); "roton-like minimum" for the 2D ³He mode | 47 (3) |
| wave-vector transfer; dynamic structure factor | Q = k_i − k_f and ħω = E_i − E_f; S(Q,ω) is the space–time Fourier transform of the density–density correlation function, and a well-defined excitation is a ridge at ħω = ε(Q) | 45 |
| time-of-flight spectrometer | a direct-geometry instrument for cold neutrons whose choppers define the incident pulses; it sorts the scattered neutrons by flight time and direction, recording the ridge for many Q at once | 45 |
| kinematic limit | ε ≤ (ħ²/2m_n)(2k_iQ − Q²), a downward parabola with apex E_i at Q = k_i; equivalently v_n ≥ ħQ/2m_n + ε/ħQ (only the necessary direction is formalized) | 55–64, 175 |
| phase velocity | ε/ħQ; it tends to c at small Q and is the second term of eq-vmin | 64, 66 |
| anomalous dispersion | the rise of ε/ħQ above c at small Q in ⁴He at low pressure; its kinematic consequence is that a phonon may decay into two | 66, 136 |
| Landau critical velocity | the minimum of ε/ħQ (v_L); below it no excitation can be created; "the bound of an idealized argument and not a measured threshold" | 66 |
| Landau's chain (T³ law) | from ε(k), through the Bose-gas energy integral, to C_V = ∂E/∂T; for phonons C_V = AT³, and corrections to the dispersion give the higher powers of Eq. (22) | 73–82 |
| zero sound (2D) | collective mode of Landau's collisionless kinetic equation with a single parameter F, phase velocity s·v_F with 1+F(1−s/√(s²−1)) = 0; undamped when s > 1, outside the particle–hole continuum; it exists iff F > 0 | 34, 144 |
| Lean 4 (kernel) | a programming language and proof assistant; a statement is accepted only if a small kernel has checked a complete proof of it | 114 |
| pdiff / computed winding number | the principal value in (−π,π] of a phase step; the sum around a closed loop is an integer multiple of 2π, and this fails only if a step is exactly π | 163 |
| quantum of circulation | κ = h/m = 2πħ/m; the circulation around a closed loop is an integer multiple of κ | 163, 245 |
| vortex | a zero of ψ around which the phase winds by ±2π | 180 |
| projected Gross–Pitaevskii equation | iψ_t = 𝒫[−½∇²ψ + \|ψ\|²ψ], with 𝒫 the projector on the Fourier modes below a cutoff, in GP units | 182–186 |
| Weiss–McWilliams sum | "the standard formula for point vortices on a torus", which includes the periodic images | 249 |
| mean flow (of a periodic box) | u = P/N: the pair's momentum cannot leave a periodic box, so the whole fluid moves; the winding integers force \|⟨v_y⟩\| ≥ 2πd/L² | 257–259 |
| LL-15 | rule: before a finding is carried over to another system, name the property it depends on and check that the other system has it | 107 |
| literature gate | the check of open sources made before any code; the zero-sound proposal "stopped at the literature gate, before any code, because the numbers it needed were not to be found in open sources" | 109, 272 |

Also briefly explained, but not in the table above:
- integrating-factor RK4 of qf-pgpe ("the linear part exactly and the cubic term by RK4", 186);
- the Jones–Roberts family ("a solitary wave of a compressible field", 261);
- the 'dual length' `$\varepsilon^2/(\hbar^2c^2k^3)$`, a withdrawn finding (99, 109);
- the four rules of the method (107) and the five rules of the handover (274–281).

**Used but not defined here:**
- **Units and scales:** healing length (only "ξ = 1", 186); speed of sound in GP units (186).
- **Solver:** CVODE (186, 247; ch02 introduces it).
- **Lean:**
  - `sorry` (175); Mathlib (114);
  - the standard axioms propext, Classical.choice and Quot.sound (175, 285).
- **Physics:**
  - Fermi liquid and Fermi wave number (3, 27);
  - particle–hole band or continuum (3, 27, 144);
  - Landau parameter (144); Bogoliubov spectrum (99, 109); Onsager's inequality (109);
  - density of states (82, 126); Mellin transform (126);
  - Debye-type energy (285); classical-field model (287).
- **Programme records:**
  - imprint and imprint transient (109, 186, 249);
  - ledger and CLAIM-nnn (109, 259, 289);
  - RETRACTIONS.md R2 (109);
  - the honest box (environment at 284).
- **Experiment:**
  - saturated vapour pressure (47); cold vs thermal neutrons (36, 45);
  - dilution refrigerator and nuclear adiabatic demagnetization (21).
- **Numerics and geometry:**
  - Gauss–Legendre quadrature and "band-limited field" (245);
  - non-contractible cycles of the torus (259);
  - "Green function of zero mean" (257).

## ch02 — Two Languages: Lean 4 and rusty-SUNDIALS
### A. Units and conventions
- **Units.** "In units `$\hbar=m=1$`, on a periodic box of side `$L$`" (l. 136–137).
  - The equation keeps g: `\ii\,\partial_t\psi \;=\; P\Bigl[-\tfrac12\nabla^2\psi+g\,|\psi|^2\psi\Bigr]` (l. 139).
  - g = 1 in every run (l. 375, 383). i and e are upright (`\ii`, `\ee`).
- **Projector.**
  - "`$P$` keeps the Fourier modes with `$|k|\le k_{\rm cut}$`" (l. 141).
  - In the engine, "the projector is a sharp circle at `$k_{\rm cut}=k_{\max}/2$`" (l. 318), which is "the engine's default cutoff" (l. 480–481).
  - k_max is "the largest wave number" (l. 10), the edge of the "Nyquist box" (l. 487).
  - The output prints the cutoffs as fractions, "cutoff 0.500 / 0.667" (l. 470–472).
- **Fourier convention.**
  - "`$\psi(x,t)=\sum_{k\in\Lambda}a_k(t)\,\ee^{\ii k\cdot x}$` with `$k=2\pi n/L$`, `$n\in\mathbb Z^2$`" (l. 141).
  - `\omega_k=\tfrac12|k|^2` (l. 144).
  - In the Lean module the group elements are the integer vectors n, and "the factor `$2\pi/L$` sits in `$\omega$`" (l. 148).
- **Engine conventions.**
  - Arrays "follow numpy's FFT conventions" (l. 318–319); the linear part `$-\ii k^2/2$` is applied exactly (l. 318).
  - Lean-unit amplitudes from engine amplitudes: "`$a=c/N^2$` for the unnormalized FFT convention of the engine" (l. 434; code l. 462–466).
- **Index units.** "a disc of radius `$R$` (in index units)" (l. 479–480); "(answer in index units)" (l. 553).
- **Grids.** N is the number of points per side ("an `$N\times N$` grid", l. 430). The grid spacing is never stated.
  - N=64, L=32 (l. 12, 403).
  - N=32, L=16 (l. 375, 383, 474, 509).
  - 16×16 with 49 modes and n=98 (l. 323–324, 415); L=16 per the JSON.
- **Time.**
  - "in `$20$` time units" (l. 6); no time unit or length unit is defined in ch02.
  - Time steps: Δt = 0.005 and 0.01 (l. 13); 0.02, 0.01, 0.005 (l. 401); 0.04…0.0025 (l. 415).
- **Energy.** "a random state of energy `$3$` per particle" (l. 12); "energy `$0.6$` per particle" (l. 509). The energy functional is never written.
- **Density.** "density `$1$`" (l. 375); code comment `# one mode, density 1` (l. 388).
- **How errors and drifts are normalised.**
  - "relative to the amplitude of the occupied mode" (l. 402).
  - "relative to the largest value of `$N_k$`" (l. 479).
  - Rates are "relative to the sum of the moduli of the terms" (l. 493), i.e. `$|\sum_k\mathrm{Im}(\overline{\psi_k}G_k)|\big/\sum_k|\overline{\psi_k}G_k|$`, with momentum weight `$p(k)=k_x$` (l. 504).
  - Momentum drift is "relative to `$\sum_k|k||c_k|^2$`" (l. 510).
- **Solver conventions.**
  - Tolerance weights `$1/(\mathrm{rtol}\,|y_i|+\mathrm{atol})$`; the tolerance controls the local error only (l. 266–267).
  - The cost is the number of calls of `rhs`, including the finite-difference Jacobian columns, and does not depend on machine load (l. 305–306, caption 352).
  - The engine exposes the right-hand side as `$2n_{\rm modes}$` real equations (l. 320).
  - The dense Jacobian costs n evaluations and n² numbers, with n = 2·n_modes; memory is given in MB (l. 322–323).
- **Stability analysis.** Test equation `$y'=\lambda y$`, `$z=h\lambda$` (l. 328–329); angles in degrees (l. 332, 341).
- **Floating point.** "`\lean{Float}` is the machine's double-precision number, the same 64-bit format as `\texttt{float64}` in numpy and `\texttt{f64}` in Rust" (l. 129).
  - The contrast with real numbers: "A theorem about `\lean{ℝ}` is a statement about mathematics; what a program returns is a statement about a finite machine" (l. 131).
- **Typography.** Lean identifiers are set with `\lean{...}` and `\Lthm{Module}{name}` (l. 52 ff.).
- **Absent from ch02.** ξ, the healing length, c = 1 in GP units, and any unit of length or time.

### B. Symbols
| symbol (LaTeX as in source) | meaning in this chapter | units / convention | line(s) where defined or first used | remarks |
|---|---|---|---|---|
| `K1`–`K4` | the registered controls: norm (K1), energy (K2, drift ∝ Δt⁴), momentum (K3), exact plane wave (K4) | — | 8, 188–189, 223, 403, 414, 522–525 | (i) K is also the T⁸ coefficient (17); (ii) not kelvin |
| `\Delta t` | time step | time units | 13, 401–403, 414–415, 423–424, 505, 509, 525 | — |
| `N` | grid points per side; Lean `N : ℕ` in `ZMod N` | — | 12, 239–242, 383, 403, 430–434, 474, 480–481, 552–553 | (i) `N_k` is the cubic term; cross-chapter: in ch01, N is the norm |
| `L` | side of the periodic box | dimensionless; no unit given | 12, 137, 141, 375, 383, 403, 474, 509 | (i) L is also the T⁹ coefficient (17) |
| `C_V`, `A`, `C`, `D`, `E`, `K`, `L`, `T` | the series `$C_V=AT^3+CT^5+DT^6+ET^7+KT^8+LT^9$` ("phonon specific heat"); T is temperature | — | 16–17 | (ii) letters used as coefficients; (i) A vs `A_q` (178) and "A-stable" (361); K vs K1–K4; L vs box side; T vs the Python `T = 20 * math.pi`, an end time (288) |
| `\varepsilon`, `\hbar`, `c`, `k`, `\alpha_n` | the He-4 dispersion `$\varepsilon=\hbar ck\,(1+\alpha_2k^2+\dots+\alpha_6k^6)$`, `$\alpha_1=0$`; c is the sound speed; k in Å⁻¹ (the table runs from 0 to 3.6 Å⁻¹) | Å⁻¹ | 24–25 | (i) α is also the BDF wedge angle (332); c also the engine amplitudes (434); k also the dimensionless wave vector (141) |
| Lean `p q : Prop`; `hp`, `hq`, `h` | propositions; names of hypotheses | — | 66, 72, 84, 97, 102 | (i) later p is the additive weight (231), q the density wave vector (177) and the method order (262), h the step size (261) |
| `R` (Lean `{R : Type*} [CommRing R]`) | a commutative ring | — | 71, 82, 89, 94 | (i) R is also a disc radius (479) |
| `e` (Lean `e : R`) | ring element with `e ^ 2 = 0` (nilpotent); `$e^3=0$` in Ex. 1; truncation as `e ^ 8 = 0` | — | 71–73, 82–87, 96–102, 546 | (ii) not Euler's number, which is the upright `\ee` (141, 408) |
| `\psi(x,t)`, `\psi_k` | the classical field; its amplitudes (the Lean name for `a_k`) | ħ = m = 1 | 136–141, 148, 154 ff. | — |
| `P` | the projector, which keeps \|k\| ≤ k_cut | — | 139, 141, 430, 497, 553 | cross-chapter: `\mathcal P` in ch01, ch03 and ch07; in ch01, P is a momentum; Python `s.P` indexes the retained modes (463) |
| `g` (Lean `g : ℝ`) | coupling constant, 1 in all runs | — | 139, 144, 163–167, 205–216, 224, 375–390 | — |
| `k_{\rm cut}`, `k_{\max}` | cutoff of the projector; largest (Nyquist) wave number of the grid | — | 141, 318, 480, 487, 510, 524, 526, 541, 552 | the default is k_cut = k_max/2; ⅔k_max is the pre-registered rule that proved wrong |
| `k` | wave vector `$k=2\pi n/L$` | dimensionless | 141, 144 | (i) k is also the wave number in Å⁻¹ (25); the Python `k = 2 * np.pi * m / L` (387) |
| `n` | integer vector `$n\in\mathbb Z^2$` labelling a mode | index units | 141, 148 | (i) n is also the dimension of the ODE system (264) |
| `a_k(t)` | Fourier amplitude of mode k | Lean units, `$a=c/N^2$` | 141–145, 434, 462–466, 497 | — |
| `\Lambda` (Lean `Λ : Finset G`; Python `Lam`) | the finite set of retained modes | — | 141, 147, 154–167, 440–457 | — |
| `\omega_k` (Lean `ω : G → ℝ`) | `\omega_k=\tfrac12\|k\|^2`; in Lean, an arbitrary real dispersion | — | 144, 148, 163, 198, 225 | (ii) the bare kinetic frequency, not a Bogoliubov frequency; (i) the Python `omega` is Ω (390); cross-chapter: in ch01, ħω is an energy transfer |
| `N_k(a)` (Lean `nl`) | the cubic term, summed over triples with `$k_1+k_3=k+k_2$` | — | 145, 154–156, 176, 430–432, 479 | (i) vs N, the grid size |
| `k_1`, `k_2`, `k_3` | the three wave vectors of a triple | — | 145, 177, 431, 479–481, 554 | (i) at l. 252, k_1 is the first component of k (`$p(k)=k_1$`); l. 504 writes k_x for the same thing |
| `G` (Lean `{G : Type*} [AddCommGroup G] [DecidableEq G]`) | additive commutative group of mode labels | — | 147, 152, 175, 246–254 | (i) see `G_k` |
| `G_k` | right-hand side in `$\ii\dot\psi_k=G_k$` | — | 180, 504, 553 | (i) |
| `Q` (Lean `pairing Λ ψ`) | quartic interaction sum `$Q=\sum_k\overline{\psi_k}N_k$` | — | 159, 177, 494 | cross-chapter: wave-vector transfer in ch01 |
| `A_q` (Lean `dens Λ ψ q`), `q` | `$A_q=\sum_{a-b=q}\psi_a\overline{\psi_b}$`, the Fourier transform of the density; q is a difference wave vector (`diffs Λ`) | — | 160, 177–178, 494 | (i) A vs the T³ coefficient; q vs the method order |
| `a_0` (`a₀`), `k_0` (`k0`), `\Omega` | amplitude and occupied mode of the plane wave; its frequency `$\Omega=\omega_{k_0}+g\|a_0\|^2$` | — | 198–216, 224, 376, 408 | Lean `planeWave`, `planeState`, `galerkinField` |
| `p` (Lean `p : G →+ ℝ`) | additive map, `$p(k+k')=p(k)+p(k')$`; momentum is `$\sum_k p(k)\,\|\psi_k\|^2$` | — | 231, 240, 246–256, 504 | (ii) a weight (a linear functional), not a momentum value; (i) p is also a Prop (66) |
| `S_a`, `S_b`, `S_c`, `S_d`; `a`, `b`, `c`, `d` | four-fold sums weighted by p(a)…p(d); dummy mode labels | — | 249–251 | (i) c is also the engine amplitudes and the sound speed |
| `\mathbb Z_N\times\mathbb Z_N` (Lean `ZMod N × ZMod N`) | the periodic grid of wave vectors (a torus group) | — | 239–242, 254, 500, 534 | — |
| `x` | position (141); grid point in `\sum_x` (497); Lean `x : ZMod N × ZMod N` (240); oscillator coordinate (283, 353, 355) | — | as listed | (i) four meanings |
| `y`, `f`, `t_0`, `y_0`, `y_i` | ODE state, right-hand side, initial time and value, component i | — | 261, 266 | — |
| `h`, `q` | step size; order of the multistep method | — | 261–262, 266, 329 | (i) see the rows above |
| `I-\gamma J` | the Newton matrix; J is the Jacobian, built by finite differences when not supplied; I is the identity | — | 264 | γ is not defined in ch02 (unclear); CVODE's own documentation uses γ = h·β₀, but the chapter does not say so |
| `n` | dimension of the ODE system (n = 2·n_modes; 98 for 49 modes) | — | 264, 320–324 | (i) |
| `n_{\rm modes}` | number of retained modes | — | 320, 323 | — |
| `\mathrm{rtol}`, `\mathrm{atol}` | relative and absolute tolerances | — | 266, 270, 291–292, 345–370, 409, 415–419, 424 | — |
| `\lambda` (Python `lam`) | eigenvalue in `$y'=\lambda y$`; stiffness parameter of Prothero–Robinson, `$y'=-\lambda(y-\cos t)-\sin t$` | — | 328–329, 354, 360–361, 548 | (i) sign flip: in Prothero–Robinson the eigenvalue is −λ with λ > 0; cross-chapter: the neutron wavelength in ch01 |
| `z` | `$z=h\lambda$` | complex | 329, 338 | — |
| `\alpha` | half-angle of the BDF stability wedge | degrees | 332, 341 | (i) vs `\alpha_n` (25) |
| `x`, `v` | oscillator position and velocity; amplitude `$\|(x,v)\|$` = 1 | — | 283, 353, 355 | — |
| `R` | radius of the disc containing the retained modes; the triple sums reach 3R | index units | 479–482, 554 | (i) vs the ring R (71) |
| `m` | (a) mass, = 1 (136); (b) integer wrap vector in `$k_1-k_2+k_3=k+Nm$`, `$m\ne0$` (431); (c) the Python mode index `m = 3` (383, 387) | — | 136, 383, 387, 431 | (i) three meanings |
| `c`, `c_k` | the engine's unnormalized FFT amplitudes; momentum scale `$\sum_k\|k\|\|c_k\|^2$` | engine units | 434, 464, 510 | (i) vs the sound speed (25) and the dummy c (249); the Python `c` is the engine state (389) |
| `k_x` | x-component of k (the momentum weight) | — | 504 | — |
| `\mathrm{FFT}` | fast Fourier transform on the grid | — | 33, 430, 497, 554 | — |

**Lean-only notation and API names**
- **Primer (60–87):**
  - `#check`, `example … := rfl`, `and_swap' (p q : Prop) (hp : p) (hq : q)`, `two_add_two` (proved by `norm_num`)
  - `one_add_nilpotent_inv {R : Type*} [CommRing R] (e : R) (h : e ^ 2 = 0)`, proved by `linear_combination (-1 : R) * h` and `ring`
- **Audit and programs:**
  - `#print axioms`, `sorryAx` (105–115)
  - `#eval`, `Float` (117–132)
- **GPGalerkin (150–186):**
  - definitions: `nl`, `pairing`, `diffs`, `dens`
  - theorems: `pairing_eq_sum`, `pairing_nonneg`, `pairing_im_zero`, `mass_rate_zero`, `energy_rate_zero`, `grad_identity`
  - notation: `starRingEnd ℂ` = complex conjugation; `.im` = imaginary part; `(ω k : ℂ)` = a real regarded as complex
- **Ch02_Galerkin (193–257):**
  - plane wave: `planeWave`, `planeState`, `galerkinField`, `planeState_solves_galerkin`, `nl_single`, `HasDerivAt`
  - momentum: `momentum_rate_zero`, `no_momentum_on_torus`, `no_additive_wavenumber`, `Finset.sum_comm`
- **Elsewhere:** `PhononSeries.kPow2_eq` (86).
- **Python and Rust API:**
  - `CvodeSolver(method, rtol, atol, max_steps)`, `solve(rhs, t0, y0, t_out)`, `rhs(t, y)` (270)
  - `Method::Adams` (309); `rhs`, `pack`, `unpack` (320)
  - `qf_pgpe.Pgpe(N, L, g, 0.01)`, commented "grid, box, coupling, time step" (384); `engine.run`, `engine.modes`, `engine.psi` (389–392)
  - `lean_nl(Lam, A)`, with `B = 3 * int(np.abs(Lam).max()) + 1` (440–457); `s.P`, `s.nonlin(c)` (463–466); `bridge_case` (475)

### C. Physical constants and material values quoted
ch02 prints no physical constants: no ħ, k_B, masses, sound speeds or densities. The only material data are the range of the Godfrin table and the bibliographic data of Godfrin2021 (the authors, IN5 at the ILL, PRB 103, 104516 (2021); l. 22–24). The other values quoted are numerical results.

| quantity | value as printed in the text (and units) | source the chapter itself gives | line | remarks |
|---|---|---|---|---|
| range of the Godfrin 2021 table | "from `$0$` to `$3.6\,\text{\AA}^{-1}$`" | `\cite{Godfrin2021}` | 24 | — |
| Lean library | 37 modules with 310 theorems and lemmas (413 declarations), Lean 4.34.0-rc2 with the matching Mathlib; GPGalerkin has "thirteen theorems", all on the three standard axioms | `lean_src/` | 53, 181 | — |
| first run of the controls (Amendment A1, 2026-09-22) | momentum drift `$8.54$` in `$20$` time units ("one per cent"), the same at two time steps. Footnote: `$N=64$`, `$L=32$`, energy `$3$` per particle, `$t=20$`, drift `$8.5358$` at `$\Delta t=0.005$` and at `$0.01$`. Norm `$4.2\times10^{-10}$`; plane wave `$7.0\times10^{-10}$` | `docs/designs/PGPE_BKT_PREREG.md` and `data/generated/pgpe/known_answers.json` ("quoted from those files, not recomputed") | 5–13, 522–524 | — |
| oscillator snippet | rtol 1e-8, atol 1e-10, max_steps 100000, T = 20π: Adams `1549` calls, error `3.76e-07`; BDF `5217` calls, `2.53e-06` | `figures/ch02_snippets.py` | 288–307 | JSON `B_cvode.oscillator` |
| work-precision on the oscillator | 19 tolerances from 1e-3 to 1e-12. Cheapest run with error below 1e-8: Adams `$1\,880$` evaluations, BDF `$12\,769$`. Adams at rtol 1e-5: `$704$` evaluations, error `$4.1\times10^{-5}$`; at 1e-6: `$3\,327$`, `$5.0\times10^{-4}$` | `figures/ch02_workprecision.py`, key `B_cvode` | 345–348, 357 | matches the JSON |
| amplitude bias | BDF −1.1 % (rtol 1e-3) and −0.043 % (1e-5), below 1 in all 19 runs; Adams +4.9 % and +0.004 %, negative in 11 of 19 | same | 365–366 | matches the JSON |
| Prothero–Robinson | rtol 1e-6 (atol 1e-8 in Ex. 2). λ=1: Adams `$255$`, BDF `$470$`. λ=1e5: `$5\,565$` vs `$418$`. Ex. 2, λ=1e4: `$5\,270$` and `$431$`; with max_steps 300, Adams stops with "maximum steps exceeded (300) at t=1.77" | `\cite{ProtheroRobinson1974}`; key `B_cvode` | 354, 360–361, 548–550 | matches the JSON |
| Adams defect and build | old module: the error falls by `$10^{0.5}$` per decade; at rtol 1e-10 it needs `$2.2\times10^{6}$` evaluations for an error of `$6.9\times10^{-5}$`; the current build needs `$616$` for `$1.7\times10^{-9}$`. The old Adams path fails after about `$10^6$` evaluations; the script refuses a module that needs more than `$5\,000$` on y′=−y. Repair dated 2026-09-28; stale module built 26 September; commit `5db8041`, release line v11.6.0 | rusty-SUNDIALS `docs/CVODE_ADAMS_FIX.md`; key `B_cvode` | 309–315, 369–371 | JSON `env.adams_fix_probe_nfe` 511 |
| speed-up of the Rust step over numpy | `$4.3$`, `$4.2$`, `$2.7$`, `$2.5$` at N = 64, 128, 256, 512 (a shared 2013 four-core laptop) | `\cite{Callens2026sw}` (quoted, not repeated) | 321–322 | — |
| memory of the dense Jacobian | a `$128^2$` grid has ≈`$3\,200$` modes, about `$330$`\,MB; the CVODE referee grid is `$16\times16$` (`$49$` modes, `$n=98$`) | computed | 322–324 | — |
| Adams–Moulton intercepts on the real axis | `$-6.00$`, `$-3.00$`, `$-1.84$`, `$-1.18$` (orders 3–6) | "computed here, not copied"; `figures/ch02_stability.py` | 330–331, 341 | JSON `F_stability.am_real_axis_left_end` |
| BDF wedge half-angles | `$90^\circ,90^\circ,86.0^\circ,73.4^\circ,51.8^\circ$` (orders 1–5); a boundary-locus check gives `$86.03^\circ$`, `$73.35^\circ$`, `$51.84^\circ$` | same | 332, 341 | JSON `F_stability.bdf_A_alpha_angle_deg_measured` |
| plane-wave test | `$L=16$`, `$g=1$`, density `$1$`, `$k=2\pi\cdot3/L=1.178$`, `$\Omega=k^2/2+g=1.694$`, t = 10, N = 32 | `figures/ch02_snippets.py` | 375–376, 383 | JSON `C_planewave` |
| plane-wave errors | snippet `1.12e-08` at Δt = 0.01. At Δt = 0.02, 0.01, 0.005: `$1.8\times10^{-7}$`, `$1.1\times10^{-8}$`, `$7.0\times10^{-10}$`, ratios 15.9 and 16.0. numpy and Rust final states differ by ≤ `$4\times10^{-14}$` relative to the occupied-mode amplitude. Norm change `$7\times10^{-12}$`. K4 (`$N=64$`, `$L=32$`, `$\Delta t=0.005$`, t=10, acceptance `$10^{-9}$`): `$7.0\times10^{-10}$`. With g = 0: `$1.1\times10^{-14}$` | `figures/ch02_planewave.py`, key `C_planewave` | 397, 401–404 | JSON `rust_minus_numpy_final` 4.17e-11 is absolute; divided by N² = 1024 it gives the printed 4×10⁻¹⁴ |
| order test | 16×16, 49 modes; CVODE Adams at rtol 1e-12, atol 1e-14: `$482$` evaluations in `$95$` steps. Engine error `$1.2\times10^{-4}$` → `$1.8\times10^{-9}$` for Δt = 0.04…0.0025, successive ratios 15.99, 16.00, 16.00, 15.97. Fitted order 3.999 (Rust) and 3.997 (Python/numpy); the two routes agree to 0.8 % | key `A_order` (stored file `data/generated/pgpe/bench/cvode_order.json`) | 409–410, 414–416, 536 | — |
| CVODE on the 16×16 plane wave | Adams at rtol 1e-4, 1e-6, 1e-8, 1e-10: 1 530, 788, 701, 1 143 evaluations; errors 1.3e-3, 2.5e-4, 1.8e-6, 2.0e-8. BDF at 1e-8: 2 364 for 2.9e-5. The engine needs ≈3 400 evaluations for 2e-8 | key `C_planewave` | 418–420 | — |
| norm drift on an interacting state (t = 5) | IF-RK4: −1.5e-9, −9.8e-11, −6.3e-12. CVODE-Adams: +1.2e-6, −3.4e-8, +3.3e-10, −1.2e-12. BDF: −1.2e-5, −2.3e-7, −7.9e-9, −1.9e-10 | key `D_invariants` | 423–425 | — |
| aliasing bridge | N = 32, L = 16. Cutoff 0.500, 197 modes: `7.85e-16` with 0 differing (four extreme modes empty); `1.15e-03` with 4 differing (all modes filled). Cutoff 0.667, 357 modes: `1.53e-01` with 348 differing | `figures/ch02_compute.py` (`lean_nl`, `bridge_case`); key `E_bridge` | 470–474, 478–479 | — |
| pairing identity | `$Q=1.403114631989707$` against `$\sum_q\|A_q\|^2=1.4031146319897068$`, imaginary part `$2.8\times10^{-17}$` | key `E_bridge` | 494 | — |
| rates | literal definition: below `$10^{-17}$`. Engine mass rate ≤ `$1.1\times10^{-17}$`. Engine momentum rate: `$1.6\times10^{-17}$`, `$2.3\times10^{-5}$`, `$4.1\times10^{-3}$` | key `E_bridge` | 493, 499, 522–524 | — |
| drift in time | N = 32, L = 16, energy 0.6 per particle, seed 3, Δt = 0.01. At t = 10: norm `$3.7\times10^{-10}$` and energy `$2.3\times10^{-9}$` at both cutoffs; momentum `$6.0\times10^{-10}$` (½k_max) and `$4.2\times10^{-7}$` (⅔k_max). At t = 20: momentum `$2.2\times10^{-8}$` and `$2.4\times10^{-6}$`; norm `$4.2\times10^{-10}$` and energy `$2.5\times10^{-9}$` | key `E_bridge.drift` | 509–511 | — |
| aliased modes at 4R = N | `$\pm(N/4,0)$`, `$\pm(0,N/4)$`; the triple `$k_1=k_3=-k_2=(N/4,0)$` feeds (−N/4, 0) | geometry and data | 481 | Ex. 3 uses N = 16, with modes (±4,0) and (0,±4) |
| Float demonstration | `0.300000`; `false` for `0.1 + 0.2 == 0.3` | Lean `#eval` | 124–128 | — |

### D. Glossary terms introduced in this chapter
| term | one-line definition in the chapter's own sense | line of first introduction/definition |
|---|---|---|
| projected Gross–Pitaevskii equation (PGPE) | "the classical-field description of a Bose fluid used throughout the programme": iψ_t = P[−½∇²ψ + g\|ψ\|²ψ], with P keeping \|k\| ≤ k_cut | 5, 136–141 |
| registered controls K1–K4 | the pre-registered checks of the solver: norm, energy, momentum, and an exact plane wave | 5–13 |
| aliasing (the one-half vs two-thirds rule) | on the grid a wave vector is a class modulo N, so wrapped triples (k₁−k₂+k₃ = k+Nm, m≠0) add to the same mode. The cubic term is alias-free for every state iff 4R < N (k_cut < k_max/2); the two-thirds rule (3R ≤ N) holds for quadratic terms only | 10–11, 430–432, 479–482 |
| Galerkin system | the mode ODEs iȧ_k = ω_k a_k + g N_k(a) on a finite set Λ, with the exact (non-wrapping) convolution; the Lean module GPGalerkin states it over any additive group | 32, 141–148 |
| type, term, kernel | a statement is a type and a proof is a term of that type; the kernel is the small program that checks the term; the kernel and the axioms are what a reader must trust | 49–52 |
| tactic | a procedure that builds a proof (e.g. `norm_num`); it is not trusted, because the kernel re-checks its result | 51, 80 |
| certificate (`linear_combination`) | coefficients supplied from outside such that the goal minus coefficient × hypothesis is a ring identity, which `ring` then checks | 83–87 |
| axiom audit (`#print axioms`) | lists the axioms a proof ultimately depends on; the standard foundation is propext, Classical.choice and Quot.sound | 105–112 |
| `sorry` / `sorryAx` | a placeholder for an incomplete proof; it shows up as the extra axiom `sorryAx` in the audit | 113–115 |
| Float | the machine's 64-bit double; in it 0.1 + 0.2 ≠ 0.3, unlike in ℝ | 129–132 |
| additive map | p : G →+ ℝ with p(k+k′) = p(k)+p(k′); the momentum is Σ p(k)\|ψ_k\|²; on Z_N × Z_N every additive map is zero | 246–257 |
| CVODE | integrates y′ = f(t,y) by linear multistep methods, changing the step h and the order q as it runs | 261–262 |
| Adams–Moulton methods | implicit multistep family of orders 1–12, for smooth non-stiff problems | 262 |
| BDF | backward differentiation formulas of orders 1–5, for stiff problems | 262–263 |
| local error control (rtol, atol) | the error of each step is estimated and weighted by 1/(rtol\|y_i\|+atol); this controls the local error, not the global error | 265–267 |
| cost | the number of calls of the user's right-hand side, including the finite-difference Jacobian columns; independent of machine load | 305–306 |
| IF-RK4 (qf-pgpe) | integrating-factor RK4: the linear part −ik²/2 exactly in Fourier space, the cubic part by classical RK4, with a sharp circular projector at k_max/2 | 317–318 |
| region of absolute stability | the set of z = hλ for which the amplification factors of the formula with frozen step do not grow | 328–329 |
| stiff | a problem whose eigenvalues have large negative real parts, so that a step resolving the solution puts hλ far outside an Adams lobe | 333–334 |
| Prothero–Robinson problem | y′ = −λ(y − cos t) − sin t, which has the smooth solution cos t for every λ and a stiffness that grows with λ | 354, 360 |

Also briefly explained, but not in the table above:
- Nordsieck array ("scaled derivatives", 265);
- the Adams defect: `Method::Adams` was stuck at order 1, i.e. implicit Euler, until 2026-09-28 (309–315);
- rusty-SUNDIALS, a Rust translation of the SUNDIALS C code, where "verified" means agreement with reference answers (269–273);
- Mathlib ("the community library of mathematics", 52);
- the exact plane wave as a known answer (223–226).

**Used but not defined here:**
- **Lean:** elaborator (51); `rfl` beyond "reflexivity" (78).
- **Programme records:** pre-registration and amendment (5, 10, 188; points to a file); the honest box (environment at 531).
- **Numerics:**
  - FFT (33); Newton iteration and dense LU factorization (263);
  - integrating factor (317); classical RK4 (318);
  - Nyquist box (487); A-stable (361); trapezoidal rule and implicit Euler (331);
  - Parseval on the grid (495);
  - order conditions, root test, boundary locus (338–341);
  - seed (474, 509).
- **Physics:** Hamiltonian equation (365); energy per particle (12, 509; the functional is never written).
- **Absent altogether:** the healing length, ξ and c = 1 do not appear in ch02.

### E. Cross-chapter notes
1. **Healing length.**
   - ch01 l. 186 makes ξ = 1 in units ħ = m = g = 1 with background density 1, but gives no formula. That is true only for ξ = ħ/√(mgn) = ħ/(mc).
   - Spot-checks agree with ch01:
     - ch03 l. 41 defines `$\xi=\hbar/\sqrt{mgn_0}$` and `$c=\sqrt{gn_0/m}$`, with time unit ξ/c and κ = 2π.
     - ch05 l. 225 and l. 316 write `$\xi=\hbar/mc$`, "the convention of the solver".
     - ch07 l. 189 also has ξ = 1 and c = 1.
     - ch09 l. 25 writes `$\xi=\hbar/\sqrt{m\mu}$` with time unit `$\tau=\hbar/\mu$`.
   - The book is consistent with itself, but differs by a factor √2 from the other common convention ξ = ħ/√(2mgn), used for example by Pitaevskii and Stringari, whom ch01 l. 304 cites.
   - Appendix D should state ξ = ħ/(mc) = ħ/√(mgn) explicitly.
   - The density symbol varies: no symbol and then n (ch01 l. 186, 259), n_0 (ch03), n (ch07), and μ instead of gn (ch09).
2. **Time and length units.** ch01 gives ξ/c (l. 186). ch02 gives neither a time unit ("time units", l. 6) nor a length unit; ch09 uses τ = ħ/μ. These agree when ħ = m = g = n = 1, but ch02's L = 16 and 32 and its "energy per particle" can be read only through the convention of ch01 and ch03.
3. **κ.** κ = h/m (ch01 l. 163) = 2πħ/m (l. 245), which is 2π in GP units (spot-check: ch03 l. 41, ch07 l. 28). Windings are reported in units of 2π.
4. **Projector and momentum letters.**
   - ch01 writes `\mathcal P` (l. 184, 186), as do ch03 and ch07 l. 189 (spot-check); ch02 writes a plain `P` (l. 139 ff.).
   - ch01 also uses P for the momentum (l. 253, 257).
   - On the cutoff, ch01 says only "below a cutoff". ch02 gives \|k\| ≤ k_cut with the engine default k_cut = k_max/2 (l. 318, 480–481). ch03 l. 332 (spot-check) writes `$k_{\rm cut}=\pi/\xi$` at 128² with L = 64ξ, which equals k_max/2 at Δx = ξ/2.
5. **Typography of i, e and d.**
   - The imaginary unit is italic `i` in the PGPE of ch01 (l. 184) and ch07 (l. 189), but upright `\ii` in ch02 (l. 139).
   - The Bose factor in ch01 uses an italic `e^{…}` (l. 76, 78); ch02 uses the upright `\ee` (l. 141, 224, 408).
   - ch01 mixes `\dd` (l. 76–82) and `\mathrm d` (l. 245, 299); the output is identical.
   - ch01's PGPE omits g (l. 184); ch02 (l. 139) and ch07 keep it.
6. **N.** N is the norm in ch01 (l. 257) and in ch03 l. 216 (spot-check). It is the number of grid points per side in ch02, and in ch01's own numbers file (`triptych.N` = 128). ch02 also has N_k for the cubic term.
7. **Q.** The wave-vector transfer in ch01; the quartic interaction sum in ch02 (l. 177).
8. **λ.** The neutron wavelength in ch01; in ch02 the eigenvalue of the test equation and the Prothero–Robinson stiffness parameter, whose eigenvalue is −λ.
9. **ω vs ε.** In ch01 the dispersion is an energy ε(Q) in meV, and ħω is the energy transfer. In ch02 the dispersion is a dimensionless frequency ω_k = ½\|k\|², Ω is the plane-wave frequency, and the Python `omega` is Ω.
10. **k and Q units.** Å⁻¹ for helium and neutron material (ch01; ch02 l. 24–25). In ch02's PGPE sections, k = 2πn/L is dimensionless, and n is in "index units".
11. **C_V coefficients.**
    - A, C, D, E, K, L (ch01 l. 31, 82; ch02 l. 17) are as printed in Godfrin2021 Eq. (22): there is no B, and F–J are skipped.
    - These letters clash with: the loop labels A–D (ch01 l. 239); A_q and "A-stable" (ch02 l. 178, 361); C_V itself; E for energy; K for kelvin and the controls K1–K4; and L for the box side in both chapters.
    - Both chapters call C_V a "specific heat" (ch01 l. 31, 74; ch02 l. 16), yet A contains V (ch01 l. 80), so it is the heat capacity of volume V.
12. **α and its neighbours.**
    - α_n are dispersion coefficients (ch01 l. 31, 82; ch02 l. 25); α is the BDF wedge half-angle in ch02 (l. 332).
    - ch01 writes `a` for the cubic coefficient (l. 51, 130–136). Its Statement 2 has ε = ck(1+ak²) without ħ (l. 136), while l. 31 and l. 82 write ħck.
    - Spot-check: ch10 (l. 21, 49–62) uses α and α′ for mutual friction, η for vortex diffusion, and `\boldsymbol\xi_i` for unit white noise, which clashes with ξ the healing length.
    - ch10 l. 88 also uses γ, which in ch02 l. 264 (`I-\gamma J`) is never defined.
13. **m.**
    - The boson mass in both chapters. The neutron mass is m_n, but plain m in ch01 l. 169–175.
    - Integer uses: the Lean integer m (ch01 l. 151), the wrap vector m (ch02 l. 431), and the Python mode index m = 3 (ch02 l. 383).
14. **n.**
    - In ch01: the density (l. 259), the windings n_in, n_out, n(x) (l. 259, 299), and the length of the Lean loop (l. 150).
    - In ch02: the integer mode vector (l. 141) and the dimension of the ODE system (l. 264).
15. **c.**
    - The sound speed in both chapters (239 m/s, or 1).
    - In ch02 also the engine's FFT amplitudes c and c_k (l. 434, 464, 510), and a dummy mode label (l. 249–251).
    - The Python engine state is `c` in both chapters (ch01 l. 194–195; ch02 l. 389).
16. **s and F.**
    - s is the zero-sound velocity over v_F in ch01 (l. 144), but `s` is the Python engine object in ch01 l. 192 and ch02 l. 463–466.
    - F has no index in ch01 (l. 140–144); ch08 l. 59 (spot-check) gives F ≡ F_0^s, which Appendix D can adopt.
17. **q.** In ch02 a density wave vector (l. 177) and the method order (l. 262). Spot-check: ch07 l. 28 and ch10 l. 49 use q and q_i for the vortex charge.
18. **The GP energy functional** is written in neither chapter. ch01 prints E = 2069.113… and ch02 gives energies "per particle", so its normalization (e.g. ½g\|ψ\|⁴ vs g\|ψ\|⁴, and whether μ is subtracted) cannot be fixed from these two chapters.
19. **Grid spacing, time step and FFT normalization.**
    - The grid spacing is never stated in prose. Δx = 0.5ξ is implied in ch01 (l. 186, 220); spot-check: ch03 l. 346 speaks of "the same `$\Delta x$`".
    - ch01's Δt = 0.01 is implied by "1000 RK4 steps" over t = 10 (l. 195); ch02 states Δt explicitly.
    - ch02's FFT normalization is a = c/N² (l. 434).
20. **Constants never printed in ch01 or ch02:**
    - ħ, h, k_B, m_n and the ⁴He and ³He masses;
    - the density and molar volume of ⁴He;
    - the meV↔K factor.

    The numbers file has 11.6045 K/meV, ħ²/2m_n = 2.0721 meV Å² and v·λ = 3956.03 m/s·Å. The 239 m/s sound speed is the chapter's extrapolation of the Godfrin table, not a literature value.
21. **Honest-box categories differ between chapters.**
    - ch01 (l. 285–289): Proved / Measured / Simulated / Only an analogy / Failed or corrected.
    - ch02 (l. 533–542): Proved / Measured or simulated / Not established / An analogy, not a result / What failed.
    - A glossary entry for "honest box" needs to allow for both.
22. **Lean library count.** "indexes 310 theorems" (ch01 l. 114) vs "37 modules with 310 theorems and lemmas (413 declarations in all)" (ch02 l. 53): the same number in different words.