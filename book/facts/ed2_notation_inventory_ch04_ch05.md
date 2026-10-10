Inventory for Appendix D: ch04 and ch05

Read-only task. No file was created, edited or deleted, and LaTeX was not run. I read every line of `book/chapters/ch04.tex` (621 lines) and `book/chapters/ch05.tex` (565 lines). The printed value behind each macro comes from `book/figures/ch04_numbers.tex` and `book/figures/ch05_numbers.tex`, which are generated from the two JSON files. I read `ch04_numbers.json` in full and the constants and features blocks of `ch05_numbers.json`. I also read the two tables that ch05 `\input`s: `figures/ch05_pressure_table.tex` and `figures/ch05_cvode_table.tex`.

Where the chapter text is silent I checked the scripts (`figures/ch04_common.py`, `figures/ch04_dispersion.py`, `figures/ch05_helium.py`, `figures/ch05_numbers.py`). Anything taken from a script is marked "script:".

"Lxx" means line xx of the chapter file. Pipes inside table cells are escaped as `\|`.

---

## ch04 — The Specific Heat of Helium-4 and Godfrin's Series

### A. Units and conventions
- **Unit macros (L3–5):** `\providecommand{\cfkB}{k_{\mathrm B}}`, `\providecommand{\cfAng}{\text{\AA}}`, `\providecommand{\cfK}{\,\mathrm{K}}`. Temperatures are always typeset as `\cfK`; wave numbers are in `\cfAng^{-1}`.
- **Specific heat is molar:** `\cfv{cv-0.2}\ \mathrm{J\,K^{-1}mol^{-1}}` (L11). The physics is per mole: "a mole of liquid of molar volume $V$ holds … $(V/2\pi^2)\,k^2\,\mathrm dk$ modes" (L44).
- **C_V/T³ and A:** `\cfv{cvT3-0.5}\ \mathrm{J\,mol^{-1}K^{-4}}` (L13); `$A=\cfv{A-val}\ \mathrm{J\,mol^{-1}K^{-4}}$` (L57). The unit is written in a different order from L11 (K⁻¹mol⁻¹ there, mol⁻¹K⁻⁴ here).
- **UNITS ERROR, series coefficients:** L111 says "(units `$\mathrm{J\,mol^{-1}K^{-p}}$`, `$p$` the power of `$T$`" and L342 says "`$c_{10}$` … `$c_{11}$` … (in `$\mathrm{J\,mol^{-1}K^{-p}}$`)". Since C_V is in J K⁻¹ mol⁻¹, the coefficient of T^p must be in J mol⁻¹ K^-(p+1). L13 and L57 confirm this: they give A (p = 3) in K⁻⁴.
- **Provenance of the C_V numbers:** "These numbers are not calorimeter readings: the paper *integrates the measured dispersion relation*" (L18).
- **Material inputs (mixed units, cm³ rather than m³):** `$c=\cfv{c}\ \mathrm{m\,s^{-1}}$ and $V=\cfv{V}\ \mathrm{cm^3\,mol^{-1}}$` (L57).
- **Wave-number grid:** "for `$k$` from `$0$` to `$3.6\ \cfAng^{-1}$`, spaced by `$0.002\ \cfAng^{-1}$` up to `\cfv{grid-until}` … below `$0.15\ \cfAng^{-1}$` the energies are ultrasound-based" (L23). The state is saturated vapour pressure, "(`$T<0.1\cfK$`)" (L66).
- **Converting temperature to wave number:**
  - "The natural unit of wavevector at temperature `$T$` is the thermal wavevector `$\cfkB T/\hbar c$`" (L60).
  - "`$\hbar c/\cfkB=\cfv{theta}\ \mathrm{K\,\cfAng}$`, so a kelvin corresponds to `$\cfv{kT}\ \cfAng^{-1}$`" (L61). These are 18.20 K Å and 0.0549 Å⁻¹ per K.
  - No symbol θ or k_T appears in the text. Only the code name `cc.THETA` appears (L441–442).
- **Energies are converted to kelvin by dividing by k_B:**
  - `$\varepsilon/\cfkB=\cfv{roton-K}\cfK$` (L66).
  - `$\hbar c|u_c|/\cfkB=\cfv{uc-K}\cfK$` (L552).
  - Maxon and roton are quoted as ε/k_B in K (L557).
  - The meV→K factor is never printed. Script: `MEV_K = 1e-3*C.e/C.k` with exact SI-2019 values from scipy.constants (`figures/ch04_common.py` L3, L24), i.e. 11.6045 K/meV.
- **Small energies in μeV:** `\cfv{rms-ueV}\ \mu$eV` (L66, L76). Wavelengths are in Å: "longer than `$\cfv{lambda-0.1}\ \cfAng$`" (L62).
- **Dimensions of α_j:** "`$\alpha_j$` has the dimension of length`$^j$`" (L74). They are quoted in Å², Å³, Å⁴ (L75).
- **Energy as a wave number:** "`$u=\varepsilon/\hbar c$`, which has the dimension of an inverse length" (L84).
- **Dimensionless energy variables:**
  - "the substitution `$x=\hbar ck/\cfkB T$`" (L50).
  - The Bose-integral variable t (L111, L149).
  - "phonons of energy about `$m\,\cfkB T$`" (L420).
- **Lean statements carry no units.** `energyTerm (V kB hbar c g : ℝ) (n : ℕ) (I T : ℝ)` (L222) and `phonon_specific_heat (V kB hbar c a2 a3 a4 a5 a6 z7 z9 T : ℝ)` (L225) take every quantity as a plain real. The chapter calls the result "a statement about mathematics, not about helium" (L37). The odd zeta values enter "as real parameters `z7`, `z9`" (L249).
- **Truncation convention in Lean:** "*Equal up to `$O(e^8)$`* is stated as an identity in an arbitrary commutative ring `$R$` with an element `$e$` such that `$e^8=0$`" (L173).
- **Solver normalisations:**
  - "Scaling by `$m!$` makes all six components of order one (`$y_m\to\zeta(m+1)$`)" (L391).
  - "atol `$=10^{-2}$`rtol" (L407).
  - The specific-heat ODE is normalised to the proved Debye law: "absolute `$10^{-14}$` in units of `$A\,T^3$`" (L448; also L471, L501).
  - Cutoff `$k_{\max}=2.5\ \cfAng^{-1}$` (L433).
  - Code: `xp = cc.THETA*cc.u_poly(k)/T_all  # eps/k_B T`; `cc.PREF = V k_B/(2 pi^2),  fT(T) = A T^3` (L441–444).
- **Other units:** the heat-map weight is "per unit `$\ln k$`" (L508); `$1/(\hbar c|u_c|/\cfkB)=\cfv{uc-inv}\ \mathrm{K^{-1}}$` (L553); `$b=\cfv{fit-b}\cfK$` (L556).

### B. Symbols
| symbol (LaTeX as in source) | meaning in this chapter | units / convention | line(s) | remarks |
|---|---|---|---|---|
| `C_V` | molar heat capacity, called "specific heat" | J K⁻¹ mol⁻¹ | L11, L25, L48 (`C_V=\frac{\mathrm dE}{\mathrm dT}`) | (i) C is also the T⁵ coefficient, and Lean `C` is Polynomial.C (L267). The text alternates "specific heat" (L10) and "heat capacity" (L62). |
| `T` | temperature | K | L10 | ch05 uses T for a simulation duration |
| `\varepsilon(k)`, `\varepsilon` | energy of an excitation of wavevector k (dispersion relation) | data in meV (unit not stated in ch04); shown as ε/k_B in K (L66); residuals in μeV | L20, L26, L47 | ch04 uses only `\varepsilon`, never `\epsilon` |
| `k` | magnitude of the excitation's wavevector; always called "wavevector" | Å⁻¹ | L20, L23, L44 | ch05 calls the same k "wave number" |
| `\hbar`, `\cfkB` (`k_{\mathrm B}`) | reduced Planck constant, Boltzmann constant | SI (values never printed) | L26, L47 | — |
| `c` | speed of sound at saturated vapour pressure | m s⁻¹ (238.3) | L26, L31, L57 | Do not confuse with `c_p`, `c_{10}`, `c_{11}` below |
| `V` | molar volume | cm³ mol⁻¹ (27.5793) | L31, L44, L57 | ch05: `\mathbf V` is a velocity and `V(k)` an interaction |
| `\alpha_j`, `\alpha_1`…`\alpha_6` | coefficients of ε = ħck(1+α_2k²+…+α_6k⁶); α_1 = 0 | length^j (Å^j) | L26, L72–75 | ch07 uses α, α′ for mutual friction; ch05 uses α_k for a mode amplitude |
| `E(T)` | thermal energy of the phonon gas | J mol⁻¹ (implied) | L47, L103 | (i) E is also the T⁷ coefficient |
| `A` | T³ coefficient, `A=\frac{2\pi^2\cfkB^4V}{15\,\hbar^3c^3}` | J mol⁻¹ K⁻⁴ (L57) | L25, L54, L126 | also the normalisation unit "in units of `$A\,T^3$`" (L448) |
| `C` | T⁵ coefficient | J mol⁻¹ K⁻⁶ by dimension (text says K^-p) | L25, L127 | (i) clashes with C_V and Lean `C` |
| `D` | T⁶ coefficient | J mol⁻¹ K⁻⁷ | L25, L128 | ch05 D is a flight distance |
| `E` | T⁷ coefficient | J mol⁻¹ K⁻⁸ | L25, L129 | (i) clashes with E(T) |
| `K` | T⁸ coefficient | J mol⁻¹ K⁻⁹ | L25, L130 | (i) clashes with the unit kelvin: "`$K\,T^8$`" sits next to "`$0.1\cfK$`"; ch05 also has the label "K5" |
| `L` | T⁹ coefficient | J mol⁻¹ K⁻¹⁰ | L25, L131 | ch05 L is the box size |
| `B\,T^4`, `B` | T⁴ coefficient, absent when α_1 = 0. Exercise 1: `B=-240\,\zeta(5)\,\alpha_1\,V\cfkB^5/(\pi^2\hbar^4c^4)` | J mol⁻¹ K⁻⁵ | L107, L201, L596 | (i) clashes with the Bernoulli numbers `B_6,B_8,B_{10}` (L247) |
| `x` | four uses: (a) `x=\hbar ck/\cfkB T` (L50); (b) the ODE variable (dimensionless energy) in `y'=x^m/(e^x-1)` (L390, L396); (c) argument of f(x) (L433); (d) Exercise 3: `x=T/\cfv{uc-K}\cfK` (L610) | dimensionless | L50 | (i) ch05 uses x for k/k_* and for position |
| `x_{\rm poly}`, `x_{\rm D}` | ε/k_BT for the polynomial and for the Debye dispersion | dimensionless | L431 | — |
| `f(x)` | `f(x)=x^2e^x/(e^x-1)^2`, the heat-capacity weight (not named in the text) | dimensionless | L433, L508 | a generic `f` also appears in "`mellin f s`" (L164) |
| `u`, `u(k)` | `u=\varepsilon/\hbar c`; the polynomial `u(k)=k(1+\alpha_2k^2+…)` | Å⁻¹ ("inverse length") | L84, L552 | (i) ch05 u is a Bogoliubov amplitude |
| `k(u)` | inverse series | Å⁻¹ | L86 | — |
| `\eta` | u⁷ coefficient of k(u): `\eta=-12\alpha_2^3+8\alpha_2\alpha_4+4\alpha_3^2-\alpha_6` | length⁶ by dimension (not stated) | L86–88 | (ii) η usually means viscosity; ch05 η is a pulse amplitude |
| `\omega/c` | "through `$(\omega/c)^7$`": the paper's expansion variable | unclear; never defined in ch04 (context suggests it equals u) | L199, L336 | undefined symbol |
| `g_n` (and `g_3`) | density-of-states coefficients, `k^2\,\mathrm dk/\mathrm du=\sum_n g_n u^n`; g_3 = 0 | length^(n−2) by dimension (not stated) | L90–95, L107 | ch05 g is the GP coupling and also an energy balance |
| `g` | coefficient of the monomial `g\,u^n`; Lean `energyTerm … g` | — | L217, L222 | — |
| `n` | power index of g_n uⁿ; "`n\ge1`" in the Bose integral (L149) | — | L90 | ch05 n is a density |
| `m` | three uses: exponent in the Bose integral (L99); components `y_m`, m = 3,5,6,7,8,9 (L390, L401); "energy about `$m\,\cfkB T$`" (L420) | — | L99 | ch05 m is a mass |
| `\zeta` | Riemann zeta; ζ(7), ζ(9) odd with no closed form | — | L31, L99, L124 | — |
| `I_n`, `I` | Bose integral `\int_0^\infty t^{n+1}/(e^t-1)\,\mathrm dt=(n+1)!\,\zeta(n+2)` | dimensionless | L111, L217 | Index conventions shift: L99 uses u^m → m!ζ(m+1), L111 uses t^{n+1}, L149 uses tⁿ → n!ζ(n+1) |
| `t` | dimensionless integration variable (energy/k_BT) | — | L111, L149, L164 | ch05 t is time |
| `s` | (a) Mellin variable: `mellin f s`, `\Gamma(s)\zeta(s)`, "`$s=4,6,7,8,9,10$`" (L164, L167, L566); (b) fitted exponent in `a\,T^s e^{-b/T}`, s = −3.7 (L556) | dimensionless | L164, L556 | (i) two meanings |
| `\Gamma(s)` | Gamma function | — | L167 | — |
| `B_6,B_8,B_{10}` | Bernoulli numbers 1/42, −1/30, 5/66 | — | L247 | (i) clashes with B |
| `p` | power of T | — | L111 | — |
| `c_p`, `c_q`, `c_{10}`, `c_{11}` | coefficient of T^p in C_V (c_3 = A, c_5 = C, …) | text says J mol⁻¹K⁻ᵖ (L342); should be K^-(p+1) | L342, L455, L478, L542 | (ii) c_p is the standard symbol for isobaric specific heat; (i) clashes with sound speed c |
| `\hat c_p(T)` | estimator `(C_V-\sum_{q<p}c_qT^q)/T^p` | as c_p | L455, L478 | — |
| `q` | index, q < p | — | L455 | ch05 q is a wave number |
| `R` | (a) arbitrary commutative ring, Lean `R : Type*` (L173, L178); (b) distance from the origin to the nearest singularity of g(u) (L551) | (b) Å⁻¹ | L173, L551 | (i) two meanings; ch05 subscript R means roton |
| `e` | (a) Euler's number in `e^x`, `e^t`; (b) Lean's name for the series variable u, with e⁸ = 0 or e⁹ = 0 (L173, L181–203; the honesty box writes u⁸, u⁹, L567); (c) code `e = np.expm1(x)` (L399) | — | L47, L173, L399 | (i) three meanings |
| `r` | certificate in `linear\_combination (r) * h` | — | L202–203 | — |
| `N` | the power N = 8 or 9 | — | L203 | — |
| `h` | text gives "`$h:\ e^8=0$`" (L202); the quoted theorems use `h : e ^ 9 = 0` (L188, L206) | — | L188, L202 | minor mismatch (e⁸ for the kPow steps, e⁹ in density_of_states and kSq0_eq) |
| `X` | (a) indeterminate of `ℝ[X]` (L266–305); (b) upper ODE limit, "value at `$x=X$`", X = 80 (L390, L403) | — | L266, L390 | (i) two meanings |
| `k'` | formal derivative of k (`derivative`) | — | L569 | — |
| `y`, `y_m` | ODE solutions; `y'=-y` is the decay probe | — | L385, L390–391 | — |
| `rtol`, `atol` | relative and absolute solver tolerances | — | L384, L402, L407 | — |
| `k_{\max}` | upper limit of the model k-integral, 2.5 Å⁻¹ | Å⁻¹ | L433 | ch05 k_max is the grid cutoff |
| `k_M` | maxon wavevector (maximum of the table's ε(k)), 1.114 Å⁻¹ | Å⁻¹ | L500 | ch05 has no maxon symbol |
| `w(k,T)` | distribution of C_V over k, per unit ln k | dimensionless | L508 | — |
| `k_0` | threshold wavevectors 0.25 and 0.5 Å⁻¹ in the heat-map figure, panel (b) | Å⁻¹ | L508 | (ii) k_0 often denotes the roton wave number; ch02 L224 uses k_0 for a plane-wave mode |
| `k_c` | complex critical points of u(k), where du/dk = 0 | Å⁻¹ | L552 | — |
| `u_c`, `\|u_c\|` | critical value of u(k); `\|u_c\|` = 0.247 | Å⁻¹ | L552 | — |
| `p^\ast` | optimal truncation order, ≈ `\hbar c\|u_c\|/\cfkB T` | — | L555 | — |
| `a`, `b` | (a) `a` in "`$ck(1+ak^2)$`", the Lean HeliumKinematics coefficient (equals α_2) (L80); (b) a and b in the fit `a\,T^s e^{-b/T}`, b in K (L556) | b in K | L80, L556 | (i) a has two meanings here, three in ch05 |
| (no symbol) | ħc/k_B (θ) and the thermal wavevector k_BT/ħc | K Å; Å⁻¹ per K | L60–61 | numbers keys `theta`, `kT` |
| Python code names | `T_all` (68 temperatures), `cc.THETA` (=ħc/k_B), `cc.u_poly` (u(k)), `cc.bose_weight` (f), `cc.PREF` (=V k_B/2π²), `fT` (=A T³), `cc.KMAX_MODEL`, `ms=[3,5,6,7,8,9]`, `fact` | — | L396–446 | — |
| Lean `bose (t : ℝ) : ℂ` | Bose factor 1/(eᵗ−1), complex-valued | — | L155 | — |
| Lean `mellin f s`, `mellin bose (n + 1)`, `riemannZeta`, `Nat.factorial` | Mellin transform ∫₀^∞ t^{s−1} f(t) dt; ζ; n! | — | L158, L164 | — |
| Lean `a2 a3 a4 a5 a6` | α_2…α_6 | — | L181 | Written `$a_2$` in L358 ("`$-3a_2^3e^8$`"). ch05's Lean uses `a`, `α₂ α₃ α₄` and `alpha2` instead |
| Lean `kInv0`, `kInv`, `kInv0Deriv`, `kSq0` | inverse series for α_1 = 0 and for general α_1; its typed-in derivative; truncated k² | — | L181, L185, L199, L206 | — |
| Lean `energyTerm (V kB hbar c g : ℝ) (n : ℕ) (I T : ℝ)` | `V / (2 * π ^ 2) * g * I * kB ^ (n + 2) / (hbar * c) ^ (n + 1) * T ^ (n + 2)` | unit-free | L222–223 | — |
| Lean `z7`, `z9`; `hh`, `hc`, `hc0` | stand-ins for ζ(7), ζ(9); hypotheses ħ ≠ 0, c ≠ 0 | — | L225, L249, L286 | — |
| Lean `π` | Real.pi; needs `open Real`, otherwise Lean auto-binds a fresh variable | — | L223, L585 | — |
| Lean `kPoly`, `C`, `X`, `derivative`, `dosPoly`, `.coeff`, `ℝ[X]` | polynomial versions; `C` is the constant-polynomial map | — | L266–283 | (i) `C` clashes with the coefficient C and with C_V |
| Lean `energyMonomial`, `HasDerivAt` | energy of g uⁿ as a Mellin integral; derivative statement | — | L309, L226 | — |

### C. Physical constants and material values quoted
| quantity | value as printed (units) | source the chapter gives | line | numbers key → printed (raw) | remarks |
|---|---|---|---|---|---|
| C_V at 0.2 K | 6.513×10⁻⁴ J K⁻¹ mol⁻¹ | "the table that accompanies the 2021 paper of Godfrin and his collaborators \cite{Godfrin2021}"; computed by the paper from the measured dispersion, "an open ancillary file" (L18) | L11 | `cv-0.2` → `6.513\times10^{-4}` (0.0006513) | not calorimetry. Script: the file is `Cv-and-Entropy.txt` (not named in the text). |
| C_V at 0.1 K | 8.260×10⁻⁵ J K⁻¹ mol⁻¹ | same | L11 | `cv-0.1` → `8.260\times10^{-5}` | — |
| C_V(0.2 K)/C_V(0.1 K) | 7.88, 1.4 % below 8 | derived from the table | L12 | `cv-ratio` 7.88 (7.88499); `cv-ratio-dev` 1.4 | — |
| C_V/T³ | 0.0826 (0.1 K) → 0.0780 J mol⁻¹K⁻⁴ (0.5 K) | same table | L13 | `cvT3-0.1` 0.0826; `cvT3-0.5` 0.0780 (0.078048) | 0.0780 is the **total** column (phonon + roton; rotons are 1.5 % of C_V at 0.5 K). The phonon-only value, 0.0769 (key `cvT3-ph-0.5`), exists but is not used. L14–15 attribute the whole drift to the bending of the dispersion. |
| Spectrometer | IN5, ILL; inelastic neutron scattering | \cite{Godfrin2021} | L23 | — | — |
| Dispersion table | 1727 rows, 34 with an uncertainty; k from 0 to 3.6 Å⁻¹; step 0.002 up to 3.44, "0.05 beyond"; ultrasound-based below 0.15 Å⁻¹; SVP, T < 0.1 K | "open ancillary data of the paper", CC BY 4.0 (L66) | L23, L66 | `n-rows` 1727; `n-err-rows` 34; `grid-until` 3.44 (3.444); `grid-coarse` 0.05 | JSON: the 4 non-0.002 steps are one of 0.006 and three of 0.05, so "by 0.05 beyond" is slightly loose; ch05 L14 is exact |
| Sound speed c | 238.3 m s⁻¹ | "the values quoted in the paper for saturated vapour pressure" (L57); "For saturated vapour pressure it quotes" (L75) | L57, L75 | `c` 238.3 (`constants.c_m_per_s`) | no uncertainty printed (script for ch05: ±0.1) |
| Molar volume V | 27.5793 cm³ mol⁻¹ | same as c (L57) | L57 | `V` 27.5793 | N_A/V = 0.021836 Å⁻³, the same as ch05's script density (not printed) |
| α_2, α_3, α_4, α_5 = α_6 | 1.55 Å², −4.04 Å³, 2.30 Å⁴, 0 | the paper quotes this set for SVP and says it "describes the measured dispersion for k < 0.5 Å⁻¹" | L75 | `a2` 1.55, `a3` −4.04, `a4` 2.30 | Exact fractions 31/20, −101/25, 23/10 (L340). ch04 does not cite Rugar–Foster; ch05 does. |
| A | computed 0.083091; printed 0.0831 J mol⁻¹K⁻⁴ | computed from c and V (`figures/ch04_common.py`, SI-2019 constants); printed value from Godfrin2021 | L57, L115 | `A-val` 0.083091; `A-pr` 0.0831 | — |
| C, D, E, K, L | computed −0.054809, 0.065345, 0.060370, −0.26247, 0.14086; printed −0.0548, 0.0653, 0.0603, −0.262, 0.141 | Table caption: closed forms "evaluated with the coefficient set of the paper (… values from `figures/ch04_common.py`), and the number printed in the paper" | L111, L116–120 | `C-val`/`C-pr` … `L-val`/`L-pr` | units printed as K^-p; correct is K^-(p+1) |
| largest printed-vs-computed difference | 0.18 % | — | L136 | `coef-maxdiff` 0.18 (0.0017978) | — |
| ħc/k_B | 18.20 K Å | "With the numbers above" | L61 | `theta` 18.20 (18.2019082) | no symbol in the text |
| thermal wave number per kelvin | 0.0549 Å⁻¹ | same | L61 | `kT` 0.0549 (0.0549393) | no symbol in the text |
| median k of C_V at 0.1 K; wavelength | 0.024 Å⁻¹; longer than 257 Å | computed from the measured table | L62, L513 | `med-k-0.1` 0.024; `lambda-0.1` 257 | — |
| 90 % k at 0.1 K; median and 90 % at 0.5 K | 0.043; 0.119; 0.211 Å⁻¹ | same | L513 | `q90-k-0.1`, `med-k-0.5`, `q90-k-0.5` | — |
| maxon wavevector | k = 1.114 Å⁻¹ (`k_M`) | ancillary table of \cite{Godfrin2021}; "the maximum of the table's ε(k)" | L66, L500 | `maxon-k` 1.114 | ch05 prints "near 1.1". Script: the paper's Table III fit is 1.103(2) Å⁻¹ (not printed anywhere). |
| maxon energy | ε/k_B = 13.8 K | "measured dispersion has a real maxon at" | L557 | `maxon-K` 13.8 (13.8256 from 1.1914 meV) | ch05 prints 1.19 meV |
| roton minimum | k = 1.92 Å⁻¹, ε/k_B = 8.6 K "in this table" | Godfrin2021 ancillary table | L66, L515, L557 | `roton-k` 1.92; `roton-K` 8.6 (8.6024 from 0.7413 meV) | ch05 prints 0.741 meV and 8.60 K |
| polynomial vs table, 0.15 ≤ k ≤ 0.5 Å⁻¹ | 0.67 μeV rms, 2.2 μeV max; 7.6 % above the data at k = 1 Å⁻¹ | computed | L66, L76 | `rms-ueV` 0.67; `maxdev-ueV` 2.2; `poly-dev-1` 7.6 | — |
| Bose integrals | π⁴/15, 8π⁶/63, 720ζ(7), 8π⁸/15, 40320ζ(9), 128π¹⁰/33 | proved in Lean (`bose_integral_values`) | L111–120, L246 | — | mathematical constants |
| Bernoulli numbers and even zeta values | B_6 = 1/42, B_8 = −1/30, B_10 = 5/66; ζ(6) = π⁶/945, ζ(8) = π⁸/9450, ζ(10) = π¹⁰/93555 | Lean library | L247 | — | — |
| g_n at the paper's α | g_4 = −31/4, g_5 = 606/25, g_6 = 5117/100, g_7 = −56358/125, g_8 = 3527061/8000 | `figures/ch04_series_ext.py` | L340 | JSON `exact_rational.g_n` | — |
| c_10, c_11 | 1.039, −2.585 ("J mol⁻¹K⁻ᵖ") | exact rational arithmetic | L342 | `c10` 1.039; `c11` −2.585 | units should be K^-(p+1) |
| c_p/A for p = 5…14 | −0.66, 0.79, 0.73, −3.16, 1.70; 13, −31, −29, 313, −399 | same | L542 | `rA-5` … `rA-14` | these carry units K^(3−p), not stated |
| paper's C_V table | 0.01–1.3 K; columns total, phonon, roton; four significant digits | open ancillary files | L499, L503 | — | — |
| uncertainty column of the paper's table | 0.13 % (0.1 K), 0.26 % (0.3 K), 0.38 % (0.5 K), 0.86 % (0.7 K) | "the table's own uncertainty column" | L503, L533 | `paper-unc-0.1/0.3/0.5/0.7` | — |
| phonon/roton crossover | roton part overtakes phonon at 0.77 K; median k jumps to the roton at about 0.8 K | "in my integration" | L508, L515 | `T-cross` 0.77 (0.769) | — |
| share of C_V from k > 0.5 Å⁻¹ | 0.00015 / 1.5 / 33.5 / 82.4 % at 0.3 / 0.5 / 0.7 / 1 K | computed from the table | L517 | `share05-*` | — |
| phonon dominance | "Below about half a kelvin … overwhelmingly phonons" | — | L43 | — | — |
| complex critical points of the polynomial | k_c = −0.134 ± 0.316i Å⁻¹; u_c = −0.084 ± 0.233i Å⁻¹; `\|u_c\|` = 0.247 Å⁻¹; ħc`\|u_c\|`/k_B = 4.50 K; inverse 0.222 K⁻¹ | computed; "a property of the *polynomial* … not of helium" (L557) | L552–553 | `uc-k-re/im`, `uc-u-re/im`, `uc-abs`, `uc-K`, `uc-inv` | — |
| model cutoff | k_max = 2.5 Å⁻¹ (the Debye integrand beyond it is < 10⁻¹⁴ of AT³ for T ≤ 1 K) | — | L433 | JSON `model_cvode.KMAX` 2.5 | — |
| B (T⁴ coefficient) | `-240\,\zeta(5)\,\alpha_1\,V\cfkB^5/(\pi^2\hbar^4c^4)` | "agrees with the B printed for α_1 ≠ 0 in the Supplemental Material of the arXiv version" | L596, L598 | — | — |
| other computed numbers (not material constants) | error budget (L529–532), best truncations (L544), root test (L554), envelope fit b = 4.47 K, s = −3.7 (L556), solver errors | computed | — | `bud-*`, `best-*`, `root-*`, `fit-*` | listed for completeness only |
| **not quoted in ch04** | numerical ħ, k_B, N_A; 1 meV in K; ħc in meV Å; atomic mass; number or mass density; roton gap in meV; μ_R; Landau velocity; λ-point temperature; spectrometer resolution; any Donnelly–Barenghi value | — | — | JSON `dispersion.hbarc_meV_A_paper_constant` 1.56851443 (= 0.0065821·c, "the constant printed in the paper's ε(k) formula", `ch04_dispersion.py` L14) vs `hbarc_meV_A_from_SI` 1.5685191 (the value actually used, L13 there); `roton_meV` 0.7413; `maxon_meV` 1.1914 | Script: SI-2019 constants via scipy.constants; 11.6045 K/meV |

### D. Glossary terms introduced in this chapter
| term | one-line definition in the chapter's sense | line |
|---|---|---|
| T³ law (Debye law) | for linear dispersion C_V = A T³, so C_V/T³ is nearly constant at low T | L14, L50–58 |
| gas of phonons | below about 0.5 K the thermal excitations; their number is not conserved (no chemical potential); (V/2π²)k²dk modes per mole | L42–44 |
| Debye dispersion | the linear ε = ħck | L50 |
| dispersion relation (thermodynamic reading) | ε(k), "how much energy an excitation of wavevector k carries"; C_V is "a thermodynamic window onto the shape of ε(k)" | L20 |
| thermal wavevector | k_BT/ħc, the natural unit of wavevector at temperature T | L60–61 |
| bending / dispersion series | ε = ħck(1+α_2k²+…+α_6k⁶) with α_1 = 0; α_j of dimension length^j | L69–75 |
| anomalous dispersion | α_2 > 0: energy above the Debye line, fewer thermal phonons, C_V/T³ falls as T rises; keeps the collinear 1→2 phonon decay open | L78–80 |
| inverse series | k(u), the series inverse of u = k(1+α_2k²+…), through u⁷ (coefficient η) | L83–89 |
| density of states (in u) | k² dk/du = Σ g_n uⁿ | L90–96 |
| Bose integral and Bose factor | ∫₀^∞ u^m/(e^{ħcu/k_BT}−1)du = (k_BT/ħc)^{m+1} m! ζ(m+1); factor 1/(eᵗ−1) = Σ e^{−(m+1)t} | L97–100, L149, L154, L167 |
| Mellin transform | Mathlib's `mellin f s` = ∫₀^∞ t^{s−1}f(t)dt | L164 |
| truncation as a ring identity | "equal up to O(e⁸)" is stated as an identity in a commutative ring with e⁸ = 0 | L171–174 |
| certificate | polynomial r such that (lhs − rhs) − r·e^N vanishes identically; "checked, not trusted" | L202–203, L212 |
| negative control | deliberately wrong statements fed to the checker, which must reject them | L350–360 |
| rule LL-15 | "name the property a claim depends on, and check that property rather than a neighbour of it" | L347 |
| outcome rule | fix before a check what each outcome will be called (mismatch = candidate misprint; match = confirmation, "not to be dressed up as a finding") | L363–366 |
| error budget (truncation error vs model error) | series vs exact integral of the polynomial, and polynomial vs measured table | L526–528 |
| asymptotic (non-convergent) expansion | partial sums improve, then diverge; the best truncation depends on T | L541–546 |
| optimal truncation p* | p* ≈ ħc`\|u_c\|`/k_BT; best accuracy is exp(−ħc`\|u_c\|`/k_BT) times a power of T | L555, L607–610 |
| critical value, branch point, root test | k(u) has a branch point at each critical value of u(k); (`\|c_p\|`/p!)^{1/p} → 1/(ħc`\|u_c\|`/k_B) | L551–553 |

Used but not defined here: roton and maxon (L23, L43, L66; defined in ch05); "Landau excitations (phonon–maxon–roton)" (L23); saturated vapour pressure; inelastic neutron scattering; ultrasound; calorimetry; molar volume; speed of sound; chemical potential (L44); Riemann zeta; Bernoulli numbers; Gamma function; the three-phonon or collinear decay (L80, deferred to ch05); "positive phonon dispersion" (title of Phillips 1970, L19, a synonym of anomalous); CVODE, Adams–Moulton, BDF, non-stiff; cubic spline; sympy and mpmath; `sorry` and axioms (ch02); the `linear_combination`, `field_simp` and `ring` tactics; Lagrange inversion (Exercise 2); Stirling's formula (Exercise 3).

---

## ch05 — Phonons, Rotons and the Dispersion Relation

### A. Units and conventions
- **Wave number and momentum:** `\providecommand{\cfiveAng}{\text{\AA}}` (L4). "a definite momentum transfer `$\hbar k$`" (L11); the dispersion relation is "the energy of the one-excitation states as a function of their **wave number**" (L13).
- **Helium energies:**
  - In meV: "maximum of about `\cfiveV{maxonE}` meV", "minimum of `\cfiveV{rotonE}` meV --- `\cfiveV{rotonGapK}` kelvin" (L33–34). The conversion factor is never printed. Script: `K_PER_MEV = MEV/KB`, SI-2019, giving 11.6045 K/meV (`ch05_numbers.json` `K_per_meV` = 11.60451812155008).
  - In μeV, written out as "micro-electronvolts" (L66, L101, L189).
  - "uncertainties of `$0.001$` to `$0.002$` meV" (L48); resolution "`\cfiveV{resFWHM}` meV (full width at half maximum)" (L67).
- **Velocities:**
  - `$c=\cfiveV{c}\ \mathrm{m\,s^{-1}}$` (L20, L292); `\cfiveV{landauV}\ \mathrm{m\,s^{-1}}` (L24).
  - Elsewhere written "m/s" (L101, L109, L407, L519, L541): the notation is mixed.
  - Landau line slope "`$\hbar v_{\mathrm L}$`" (L20); "`$\varepsilon/(\hbar ck)-1$` in per cent" (L26).
  - "the table fixes `$c$` only to a few tenths of a per cent" (the first rows are rounded to 0.1 μeV) (L101).
- **Time of flight:** `$\varepsilon=\tfrac12 m_n D^2\,[\,(t_{\rm el}-t_s)^{-2}-(t_{\rm in}-t_s)^{-2}]$`, `$E_i=\tfrac12 m_nv_i^2$` (L60).
- **Calibration and scale invariance:** the energy scale is calibrated at one point, `$\Delta_{\rm R}=0.7418\pm0.001$` meV (L62). "changing `$E_i$` by a factor `$\lambda$` changes every `$\varepsilon$` by the same factor" (L63); "whatever one concludes … that does not change when `$\varepsilon\to\lambda\varepsilon$` is immune to the largest systematic uncertainty" (L73). The symmetric-split threshold is "homogeneous of degree one in the energy scale" (L194).
- **Roton mass is dimensionless (a ratio to m_4):** `$\varepsilon\simeq\Delta_{\rm R}+\hbar^2(k-k_{\rm R})^2/2\mu_{\rm R}m_4$` (L106); `$a=\hbar^2/2\mu_{\rm R}m_4$`, "`$\hbar^2/2m_4=\cfiveV{h2m4}$` meV\,`\cfiveAng^2`" (L537–539).
- **Pressure:** in bar; Δ_R in meV, k_R in Å⁻¹, c and v_L in m/s (L109; pressure table header).
- **Dispersion coefficients:** `$\alpha_2=1.55\pm0.01\ \cfiveAng^{2}$`, α_3 in Å³, α_4 in Å⁴ (L127).
- **Lean (HeliumKinematics) uses ħ = 1:** "With `$\varepsilon=\hbar ck(1+ak^2)$`, `$\hbar=1$`, the library has" (L133). `phononDisp`, `seriesDisp` and `bogEps` have no ħ (L137, L166, L252).
- **UNITS SLIP, L158 (eq. `ch05:eq-split`):**
  - `\varepsilon(k)-2\varepsilon(k/2) &= c\,k^{3}(…)` has no ħ on the right-hand side. The left side is an energy; the right side is a frequency.
  - Lines L156–157 divide by ħ, and L153 writes ε with ħ.
  - Correct form: ħck³(¾α_2 + ⅞α_3k + 15/16 α_4k²). The Lean version is in ħ = 1 units.
- **Gross–Pitaevskii units and the dimensional dictionary:**
  - "Take the Gross–Pitaevskii equation with `$\hbar=m=1$`" (L209).
  - Dimensional form: `$\varepsilon(k)=\sqrt{c^2\hbar^2k^2+(\hbar^2k^2/2m)^2},\quad c^2=\frac{gn}{m}$` (L218).
  - "with `$\xi=\hbar/mc$`, the convention of the solver, `$k_\ast\xi=2$`" (L225).
  - "`$\varepsilon^2=\tfrac12k^2(\tfrac12k^2+2gn)$` when `$c^2=gn$` and `$m=1$`" (L238).
- **Solver units:** "Units are `$\hbar=m=n_0=1$` and `$g=1$`, so that `$c=1$`, `$\xi=\hbar/mc=1$` and `$k_\ast=2$`" (L316). The box is "`$L=64\,\xi$`", retaining modes with `\|k\|` ≤ π/ξ (L317). Time is in GP units: "evolve for `$T=\cfiveV{Tmain}$`; every `$0.4$` time units" (L321).
- **Wave numbers in solver figures:** "the wave number is in units of `$1/\xi=mc/\hbar$`" (L382); "Gaussian of width `$0.03/\xi$`" (L404); "`$k=\cfiveV{ampK2}/\xi$`" (L487). Deviations are in ppm (L382, L390).
- **Universal coordinates:** "`$x=k/k_\ast$`, `$k_\ast=2mc/\hbar$`" (L407); "`$y=\omega/(ck)$`" (L412). For helium: "with the bare atomic mass and `$c=238.3$` m/s in `$k_\ast$`" (L407). The atomic mass is never printed.
- **Group velocity:** "`$v_{\rm g}=\mathrm d\omega/\mathrm dk=(k+k^3/2)/\omega$` (units `$c=m=\hbar=1$`)" (L435).
- **Mixed convention, L304:** `$\omega^2=\epsilon_k(\epsilon_k+2nV(k))$` with `$\epsilon_k=\hbar^2k^2/2m$` uses ω as an energy (ħ = 1) next to an explicit ħ. Exercise 3 sets `$\epsilon_k=k^2/2$` (`$\hbar=m=1$`) and `$nV(0)=c^2=1$` (L550).
- **UNITS SLIP, L529:** "the dimensionless ratio `$\ell(k)=\varepsilon^2/(\hbar^2c^2k^3)$`" is not dimensionless. ε²/(ħ²c²k³) = v_ph²/(c²k) has the dimension of a length (it is dimensionless only once k is expressed in a chosen unit).
- **Code scaling:** `y = (Re c, Im c) / N^2` (L457); `2n_modes` real unknowns (L449).

### B. Symbols
| symbol (LaTeX as in source) | meaning in this chapter | units / convention | line(s) | remarks |
|---|---|---|---|---|
| `\varepsilon`, `\varepsilon(k)` | energy of the one-excitation state; energy lost by the neutron | meV, μeV, K | L11, L13 | (i) distinct from `\epsilon` (L304, L486) |
| `k`, `\hbar k`, `\mathbf k` | wave number; momentum transfer; wave vector | Å⁻¹ for helium, 1/ξ for the solver | L11, L13, L88 | ch04 calls k "wavevector"; `Q` (L416) is the same quantity |
| `c` | ultrasonic sound speed, 238.3 m/s; c = 1 in solver units; c² = gn/m | m s⁻¹ | L20, L32, L218, L316 | (i) clashes with the mode amplitudes `c_k(t)`, `c_0` and the code array `c` |
| `v_{\rm L}`, `v_{\rm L}^{\rm table}` | Landau critical velocity, `\min_{k>0}\varepsilon(k)/\hbar k` | m s⁻¹ | L20, L92, L103 | — |
| `E_i`, `E_f` | incident and final neutron energy | meV (implied) | L53, L340 | ch04 E is a coefficient |
| `t_{\rm el}`, `t_{\rm in}`, `t_s` | arrival time of elastic neutrons; of the helium peak; moment the neutron reaches the sample | s | L54–55 | — |
| `m_n`, `D`, `v_i` | neutron mass; flight distance (D = v_i(t_el−t_s), i.e. sample to detector); incident neutron speed | SI | L60 | ch04 D is the T⁶ coefficient |
| `\lambda` | factor of a proportional rescaling of the energy scale | dimensionless | L63, L73 | not the λ point |
| `\Delta_{\rm R}`, `\Delta` | roton gap: 0.7418 ± 0.001 meV (calibration) or 0.741 meV (table minimum); written without subscript in Exercise 1 | meV | L62, L106, L109, L537 | inconsistent subscript; Δt is a time step (L385) |
| `\mathbf V`, `V` | velocity of a heavy body (Landau argument) | m/s | L87–89 | (i) clashes with `V(k)` (L304); ch04 V is molar volume |
| `v` | a speed in "for every `$v>0$`" (Lean statement) | — | L98 | (i) v is also a Bogoliubov amplitude (L215) |
| `a` | (a) coefficient of the parabolic dispersion a k² in `landau_velocity_parabolic_zero` (L98); (b) curvature coefficient in ε = ħck(1+ak²), Lean `phononDisp c a k`, equal to α_2 (L133, L137, L146); (c) `$a=\hbar^2/2\mu_{\rm R}m_4$` (L537) | (c) meV Å² | L98, L133, L537 | (i) three meanings |
| `m` | particle mass (free particle, Bogoliubov); m = 1 in GP units; for helium "the bare mass of the ⁴He atom" | kg | L97, L209, L218, L292 | value never printed (script: 4.0026032 u) |
| `m_4` | mass of the ⁴He atom | kg or u | L106, L537, L539 | — |
| `\mu_{\rm R}` | roton effective mass in units of m_4 | dimensionless (0.141) | L106, L537, L539 | (ii) often quoted in kg or as μ_R/m_4; (i) clashes with the chemical potential μ |
| `k_{\rm R}` | roton wave number | Å⁻¹ | L106, L109, L200, L537 | values 1.92 (L34), 1.920 (pressure table), 1.918 (Exercise 1) |
| `\alpha_1`…`\alpha_4` | series coefficients, α_1 = 0 | Å², Å³, Å⁴ | L124–127 | (i) clashes with the mode amplitude α_k (L324); ch07 α is friction |
| `\gamma` | the paper's notation, α_2 = −γ | Å² | L128 | — |
| `k_1`, `k_2`, `q` | wave numbers of the decay products; the soft-phonon wave number in k → q + (k−q) | Å⁻¹ | L131, L161, L183 | ch04 q is an index |
| `v_{\rm ph}`, `v_{\rm g}` | phase velocity ε/ħk; group velocity dε/ħdk (dω/dk) | m/s, or units of c | L160, L161, L182, L435 | Fig. thresholds uses a ±0.07 Å⁻¹ fit window (L181). The landmarks at L431/L443 use ±0.06 per `ch05_numbers.py` L93–95; that window is not stated in the text. |
| `k_{\rm g}`, `k_{\rm sym}`, `k_{\rm ph}` | thresholds where v_g = c, where the symmetric-split excess is zero, where v_ph = c | Å⁻¹ | L176 | — |
| `g` | (a) energy balance g = ε(k) − ε(q) − ε(k−q) (L183); (b) Gross–Pitaevskii contact coupling (L211) | (a) μeV | L183, L211 | (i) two meanings; ch04 uses g_n |
| `\psi`, `\psi_0`, `\delta` | GP field; uniform solution √n e^{−iμt}; small perturbation | — | L211–214 | — |
| `n`, `n_0` | condensate density; n_0 = 1 in the solver | — | L213, L316, L335 | the same quantity under two notations; ch04 n is an index |
| `\mu` | chemical potential, μ = gn (= gn_0) | GP energy | L213, L335 | (i) clashes with μ_R |
| `u`, `v` | Bogoliubov amplitudes in δ = u e^{i(kx−ωt)} + v* e^{−i(kx−ωt)} | — | L215 | ch04 u = ε/ħc |
| `x` | (a) position (L215, L486); (b) universal coordinate x = k/k_* (L407, L412) | — | L215, L407 | (i) two meanings |
| `\omega`, `\omega_k`, `\omega_{\rm Bog}` | angular frequency of a mode; Bogoliubov frequency | GP time⁻¹ (used as an energy in L304) | L215, L217, L324, L382 | — |
| `k_\ast` | crossover wave number 2mc/ħ | 3.00 Å⁻¹ for He; 2 in the solver | L223, L293, L316 | — |
| `\xi` | healing length, ξ = ħ/mc, "the convention of the solver" | 1 in solver units | L225, L316 | (ii) the common convention is ħ/√(2mgn). The code variable `xi` (L352) is a random Gaussian array, not ξ. |
| `\alpha_2^{\rm Bog}` | Bogoliubov curvature coefficient, 1/(2k_*²) = ħ²/(8m²c²) | Å² | L244, L293 | Lean `alpha2 c m` = 1/(8m²c²) with ħ = 1 |
| `S`, `\rho` | phase and density in ψ = √ρ e^{iS} | — | L232 | (i) clashes with S(k) |
| `S(k)` | static structure factor | dimensionless | L300, L420 | — |
| `S(Q,\omega)`, `Q` | dynamic structure factor; momentum transfer | — | L416 | not defined; Q is the same quantity as k |
| `V(k)`, `nV(k)` | Fourier transform of a non-local interaction | energy | L304, L550 | (i) clashes with `\mathbf V` |
| `\epsilon_k` | free-particle energy ħ²k²/2m (k²/2 in GP units) | — | L304, L550 | (i) `\epsilon` vs `\varepsilon` |
| `P` | projector onto modes below k_cut | — | L314 | (i) P is pressure in the pressure table |
| `k_{\rm cut}`, `k_{\max}` | sharp circular cutoff k_cut = k_max/2; k_max is the grid maximum | 1/ξ | L314 | ch04 k_max = 2.5 Å⁻¹ is an integration limit |
| `L` | box size 64ξ | ξ | L317 | ch04 L is the T⁹ coefficient |
| `\eta` | amplitude of the random pulse: 10⁻⁶ (10⁻⁴ in the CVODE table) | dimensionless | L321, L485 | ch04 η is an inverse-series coefficient |
| `T` | duration of the record: T = 300 (T = 4 and 20 in the CVODE tables) | GP time | L321 | (ii) elsewhere T is temperature |
| `t` | time; also the auxiliary t = α_2k² in the Lean bound (L248, L277) | — | L213, L248 | (i) two meanings |
| `c_k(t)`, `c_0` | amplitude of mode k; amplitude of the k = 0 mode | — | L321, L332 | (i) clashes with c |
| `s_k(t)` | record in the condensate frame, s_k = c_k c_0*/`\|c_0\|` | — | L324, L332 | (i) clashes with s(k) (L546) |
| `\alpha_k`, `\beta_k` | the two complex amplitudes of the normal modes | — | L324 | (i) clashes with α_2… |
| `\Delta t` | time step | GP time | L385 | — |
| `y` | y = ω/(ck) (L412); in code, y = (Re c, Im c)/N² (L457) | — | L412, L457 | — |
| `r`, `k_s`, `\delta\rho` | radius; stationary-phase wave number; density deviation | ξ; 1/ξ | L428–430 | — |
| `n_{\rm modes}` | number of retained modes | — | L449 | — |
| `\epsilon` | amplitude of the standing wave ψ = 1 + ε cos kx | — | L486–489 | (i) a second meaning of `\epsilon` |
| `\ell(k)` | ε²/(ħ²c²k³) = v_ph²/(c²k) (the retracted R2 hypothesis) | called "dimensionless" but actually a length | L529 | units slip |
| `k_{\rm L}` | wave number at which ε/ħk is minimal | Å⁻¹ | L538 | — |
| `s(k)` | √(c² + k²/4m²), the Bogoliubov phase velocity | velocity | L546 | (i) |
| K5, R2 | labels: the Bogoliubov known answer; retraction R2 | — | L238, L333, L529 | K5 sits next to K (coefficient, kelvin) |
| Lean defs | `phononDisp (c a k : ℝ) := c * k * (1 + a * k ^ 2)`; `seriesDisp (c α₂ α₃ α₄ k : ℝ)`; `bogEps (c m k : ℝ) := Real.sqrt (c ^ 2 * k ^ 2 + (k ^ 2 / (2 * m)) ^ 2)`; `alpha2 (c m : ℝ) := 1 / (8 * m ^ 2 * c ^ 2)` | ħ = 1 | L137, L166, L252, L254 | α_2 is named `a`, `α₂` or `alpha2` in different modules (`a2` in ch04) |
| Lean theorems and hypotheses | `three_phonon_open_iff {c a k₁ k₂}` (`hc`, `h₁`, `h₂`); `symmetric_split_excess`; `abs_bogEps_sub_phononDisp_le {c m k}` (`hc`, `hm`, `hk`); `landau_velocity_eq` (`IsGLB ((fun k => bogEps c m k / k) '' Set.Ioi 0) c`); `bogEps_le_phononDisp` (`ha`, `eps_arg`) | — | L139, L168, L256, L259, L271–282 | — |
| Lean theorems named in the text | `tof_eq12_eq_eq13`, `tofEnergy_rescale`, `landau_velocity_parabolic_zero`, `landau_velocity_ge_of_above_sound_line`, `three_phonon_excess`, `phase_velocity_excess`, `group_velocity_excess`, `two_roton_momentum_le`, `two_roton_parallel`, `two_roton_antiparallel`, `phase_velocity_universal`, `bogEps_sq_gp`, `bogEps_strictMonoOn`, `bogEps_superadditive`, `bogEps_sub_sound_strictMonoOn`, `alpha2_limit`, `sound_lt_phase_velocity` | — | L61, L63, L98, L99, L146, L160, L161, L201, L230, L238, L241–243, L265 | — |
| Python code names | `eta`; `N`; `L`; `g`; `dt`; `0.5` (= k_cut/k_max); `mask`; `xi` (random array); `ph` (conj(c00)/`\|c00\|`, the condensate phase); `scale` (= N²); `py` (the numpy engine); `dts`; `ns` | — | L346–371, L453–465 | — |

### C. Physical constants and material values quoted
| quantity | value as printed (units) | source the chapter gives | line | numbers key → printed (raw) | remarks |
|---|---|---|---|---|---|
| measurement conditions | below a tenth of a kelvin; saturated vapour pressure | — | L10, L19 | — | — |
| spectrometer | IN5 time-of-flight spectrometer, ILL | \cite{Godfrin2021} | L14, L40 | — | — |
| dispersion table | 1 727 rows (34 with an uncertainty); every 0.002 Å⁻¹ up to 3.44, then four sparser entries out to 3.6 Å⁻¹ | "the authors' processed curve … open table" \cite{Godfrin2021} (arXiv ancillary file, L19) | L14 | `tableRows` 1\,727; `nErrRows` 34; `kDense` 3.44; `kmax` 3.6 | Script: file `DispersionP0allRange.txt` (not named in the text) |
| table composition | below 0.15 Å⁻¹ ultrasound; 0.15–0.3 combined; above 0.3 neutron | "the caption of the table in the arXiv version" | L22, L47 | — | — |
| printed uncertainties | 0.001 to 0.002 meV for 0.2 ≤ k ≤ 2 Å⁻¹ | "The printed version of the table" | L48 | — | — |
| sound speed c | 238.3 m s⁻¹ | "the sound speed c that ultrasonics measures" (L32); pressure-table caption: "the ultrasonic sound velocity quoted in the paper" | L20, L292, L407 | `c` 238.3 (typed literally at L407) | ±0.1 not printed (script: 238.3 ± 0.1) |
| c from the table at 0.01 Å⁻¹ | 238.5 m/s | the table itself | L101 | `vphLow` 238.5 (238.525) | — |
| maxon | maximum of about 1.19 meV near 1.1 Å⁻¹ | table | L33 | `maxonE` 1.19 (1.1914); `maxonKshort` 1.1 (1.114) | Script: the paper's Table III gives 1.191 meV at 1.103 Å⁻¹ (not printed) |
| roton minimum | 0.741 meV = 8.60 kelvin, at 1.92 Å⁻¹ | table | L34, L72 | `rotonE` 0.741 (0.7413); `rotonGapK` 8.60 (8.6024); `rotonKshort` 1.92 | ch04 prints 8.6 K |
| roton gap used for calibration | Δ_R = 0.7418 ± 0.001 meV | "that a triple-axis spectrometer had given" (no \cite) | L62, L72 | literal | Script: Stirling, triple-axis |
| Landau velocity | 57.9 m s⁻¹ at 1.97 Å⁻¹, = 0.243 c | table | L24, L103, L519 | `landauV` 57.9 (57.888); `landauK` 1.97 (1.966); `landauOverC` 0.243 | — |
| maximum phase velocity | 5.4 % above c near 0.35 Å⁻¹ (5.3 % if normalised to 238.5) | table | L27, L101, L294 | `phaseMaxPct` 5.4; `phaseMaxK` 0.35 (0.348); `phaseMaxPctAlt` 5.3 | — |
| roton mass μ_R | 0.141 | L106: no source stated (script: a quartic fit to the table, 0.14121). L539: no source stated (script: the paper's Table III) | L106, L539 | `rotonMass` 0.141 | in units of m_4; the two values only coincide at 3 digits |
| v_L from Landau's quadratic roton | 57.9 m s⁻¹, within 0.01 % of the table value | computed | L106 | `landauQuad` 57.9; `landauQuadPct` 0.01 | — |
| pressure dependence | at 24.08 bar: Δ_R 0.626 meV, k_R 2.05 Å⁻¹, c 362 m/s (+52 %); v_L falls 57.9 → 46.1 m/s; v_L/c falls 0.243 → 0.127 | "The seven-pressure table that accompanies the paper" | L108–109 | `pP24`, `pRoton24`, `pKR24`, `pCrise`, `pC24`, `pLandau0/24`, `pRatio0/24` | — |
| pressure table (`figures/ch05_pressure_table.tex` L5–11, `\input` at L111) | P = 0.00/0.51/1.02/2.01/5.01/10.01/24.08 bar; c = 238.3/242.6/246.5/253.9/274.0/302.3/361.9 m/s; Δ_R = 0.7413/0.7381/0.7357/0.7301/0.7138/0.6882/0.6256 meV; k_R = 1.920/1.924/1.920/1.932/1.966/1.982/2.048 Å⁻¹; v_L = 57.9/57.5/57.2/56.5/54.8/52.0/46.1 m/s; v_L/c = 0.243/0.237/0.232/0.223/0.200/0.172/0.127 | caption: c is "the ultrasonic sound velocity quoted in the paper"; Δ_R and k_R "are the minimum of the tabulated curve"; neutron data from 0.15 to about 2.2 Å⁻¹ | table L4–13 | `pKmaxRange` 2.2; `pCrise` 52 | — |
| α_2 (ultrasonic) | 1.55 ± 0.01 Å², with α_1 taken to vanish | Rugar and Foster \cite{RugarFoster1984} | L127 | literal | — |
| series coefficient set | α_2 = 1.55 Å², α_3 = −4.04 Å³, α_4 = 2.30 Å⁴, for k < 0.5 Å⁻¹ | "the paper uses" \cite{Godfrin2021} | L127 | literal (ch04 prints the same set through macros) | — |
| bending at k = 0.3 Å⁻¹ | 23 μeV above the sound line | table | L66 | `bend03ueV` 23 | — |
| maximum symmetric-split excess | 14.5 μeV at 0.31 Å⁻¹, about 3 % of ε | table | L66, L189 | `symMax` 14.5; `symMaxK` 0.31 | — |
| energy resolution | 0.07 meV FWHM "at the incident energy used for the low wave numbers" | "according to the paper" \cite{Godfrin2021} | L67 | `resFWHM` 0.07 | E_i not printed (script: 3.52 meV) |
| table uncertainty near 0.3 Å⁻¹ | 1.0 μeV | table | L67 | `err03ueV` 1.0 (row k = 0.298) | — |
| detector and averaging | 384 tubes × 241 pixels; more than 70 values per bin; Gaussian resolution function | "both stated in the paper" | L68 | `nPixBin` 70 | — |
| pressure of normal dispersion | α_2 ≤ 0 at about 20 bar | \cite{Godfrin2021} | L147 | literal | Script: 20.4 bar in the DMBT-corrected analysis (not printed) |
| three-phonon thresholds | k_g = 0.404, k_sym = 0.455, k_ph = 0.566 Å⁻¹ (the other roots are near 1 Å⁻¹) | from the series coefficients | L176, L182 | `kGroup`, `kSym`, `kPhase` | — |
| symmetric split from the table | 0.453 Å⁻¹ | table | L189 | `kSymTable` 0.453 | — |
| series vs table | at most 2.2 μeV for 0.25 ≤ k ≤ 0.5 Å⁻¹ | computed | L189 | `seriesDevMax` 2.2 | ch04's 2.2 μeV is for the range 0.15–0.5 |
| relative systematic uncertainty of the energy scale | 2.1×10⁻³ | "that the paper quotes" | L195 | `relSys` `2.1\times10^{-3}` | resulting shifts ≤ 0.002 (k_g) and 0.005 Å⁻¹ (k_ph): `shiftG`, `shiftP` |
| Bogoliubov k_* for helium | 3.00 Å⁻¹ | "the bare mass of the ⁴He atom and c = 238.3 m s⁻¹" | L293 | `kstar` 3.00 (3.0038) | mass not printed (script: 4.0026032 u) |
| α_2^Bog | 0.055 Å², against the measured 1.55; ratio 28 | computed | L293 | `alphaBog` 0.055 (0.05542); `alphaRatio` 28 (27.97) | — |
| helium in universal coordinates | leaves √(1+x²) at x ≈ 0.1; rises to 1.054; falls to 0.25 at the roton | table | L407, L413 | `phaseMaxRatio` 1.054; `rotonYat` 0.25 | — |
| helium group velocity | 1.08 c (8.5 % above c) near 0.27 Å⁻¹; equals c at 0.40 Å⁻¹; zero at the maxon (1.10 Å⁻¹); −0.57 c at 1.63 Å⁻¹ | table, local linear fit | L431, L443–444 | `vgMax` 1.08, `vgMaxPct` 8.5, `vgMaxK` 0.27, `vgCrossK` 0.40, `vgZeroK` 1.10, `vgMin` −0.57, `vgMinK` 1.63 | 1.08 vs 8.5 % is rounding of 1.085 |
| ħ²/2m_4 | 0.522 meV Å² | not attributed | L539 | `h2m4` 0.522 (0.52218) | computed with m_4 = 4.0026032 u and SI constants |
| Exercise 1 roton parameters | Δ = 0.7418 meV, k_R = 1.918 Å⁻¹, μ_R = 0.141; result 58.0 m/s | not attributed in the text (script: the paper's Table III, arXiv v1) | L539, L541 | `exLandau` 58.0 | the table-derived value is 57.9 |
| ℓ(k) violation at the roton | a factor of about twenty at SVP | programme retraction R2 | L529 | — | — |
| solver parameters (not helium) | ħ = m = n_0 = g = 1, so c = ξ = 1 and k_* = 2; L = 64ξ; 128² grid; 3209 modes; η = 10⁻⁶; T = 300; Δt = 0.02; mode (16,0) with k = 1.571, ω = 1.9974; Exercise 3 extrema 0.350/0.304, min ω/k = 0.349 | — | L316–321, L337, L398, L554 | `nmodesRetained`, `Tmain`, `labK`, `labOmega`, `mf*` | GP units |
| **not quoted in ch05** | atomic-mass value (only "bare atomic mass" or m_4: L25, L292, L407, L413, L521); number density, mass density, molar volume; ħ and k_B values; 1 meV in K; ħc; λ-point temperature; E_i; uncertainty of c | — | — | script `ch05_helium.py`: m_4 = 4.0026032 u ("paper: 4.0026032 g/mol"), n = 0.021836 Å⁻³, ħc = 1.5685191 meV Å, 11.6045 K/meV | — |

### D. Glossary terms introduced in this chapter
| term | one-line definition in the chapter's own sense | line |
|---|---|---|
| dispersion relation | energy of the one-excitation states as a function of their wave number; the thin bright line of neutron counts in the (k, ε) plane | L12–13 |
| phonon | the small-k straight part, ε = ħck, with the ultrasonic sound speed | L32 |
| maxon | the maximum of the curve near 1.1 Å⁻¹ (about 1.19 meV) | L33 |
| roton | the minimum (0.741 meV at 1.92 Å⁻¹); "the name is historical: no rotation"; a sign of incipient short-range order | L34–36 |
| time-of-flight energy formula | ε = E_i[1 − ((t_el−t_s)/(t_in−t_s))²] (Eq. 13 of the arXiv paper; equivalent to its Eq. 12) | L51–60 |
| one-point energy calibration and rescaling invariance | energies fixed at the roton gap; conclusions invariant under ε → λε are immune to the largest systematic uncertainty | L62–63, L71–74 |
| kinematic statement | a consequence of the shape of the curve ε(k) alone | L42, L76–78 |
| Landau criterion, critical velocity | a heavy body at V can create an excitation only if V ≥ ε/ħk; v_L = min ε/ħk, "the smallest value of the phase velocity" | L87–95 |
| phase velocity, sound line, Landau line | ε/ħk; the line ħck; the chord from the origin touching the curve from below | L20, L23, L95, L105 |
| anomalous vs normal dispersion | α_2 > 0 means the curve bends upward away from the sound line; normal means α_2 ≤ 0 | L128, L147 |
| three-phonon (collinear) decay | k_1+k_2 → k_1 + k_2 is allowed only if ε(k_1+k_2) ≥ ε(k_1)+ε(k_2); for ε = ck(1+ak²) it is open iff a ≥ 0 | L131–147 |
| Cherenkov condition (soft emission) | a phonon can emit a very soft phonon only while its group velocity exceeds c | L161 |
| symmetric split | k → k/2 + k/2; the last channel to change sign | L162 |
| group velocity (from a snapshot) | dε/ħdk; stationary phase puts wave number k at radius r = v_g(k)t | L157, L424–435 |
| Pitaevskii plateau | the shoulder above the roton, the energy at which one excitation can decay into two rotons; at most 2k_R in the collinear case | L199–200 |
| Gross–Pitaevskii equation | i∂_tψ = −½∇²ψ + g`\|ψ\|`²ψ with ħ = m = 1 | L209–211 |
| Bogoliubov dispersion and k_* | ε = √(c²ħ²k² + (ħ²k²/2m)²), c² = gn/m; a phonon below k_* = 2mc/ħ, a free particle above | L216–230 |
| healing length | ξ = ħ/mc (the solver's convention), so k_*ξ = 2 | L225 |
| Feynman bound, static structure factor | ε ≤ ħ²k²/2mS(k); the roton sits where S(k) peaks; weak coupling saturates the bound | L300–301 |
| mean-field (dipolar) roton | a roton produced by a window where V(k) < 0 in k-space: ω² = ε_k(ε_k + 2nV(k)) | L303–306 |
| projected GPE, condensate frame, known answer K5 | GPE with projector P and cutoff k_cut = k_max/2; records taken as s_k = c_k c_0*/`\|c_0\|` to remove e^{−iμt}; K5 is the pre-registered Bogoliubov test | L312–341 |

Used but not defined here: saturated vapour pressure; ultrasound/ultrasonics; inelastic neutron scattering; triple-axis spectrometer; FWHM and energy resolution (named only); Beliaev damping (only its "kinematic precondition", L242); dynamic structure factor S(Q,ω) (L416); chemical potential; superfluid; ideal Bose gas; Bijl–Feynman spectrum; vortex nucleation; integrating-factor RK4; aliasing; CVODE/Adams; golden-section search; linear prediction; analytic signal; Hamiltonian problem; inner-product space and triangle inequality; superadditivity and IsGLB (Lean names).

---

### E. Cross-chapter notes
1. **k vs q vs Q.**
   - ch04 calls k a "wavevector" (L20, L44, L60, L500, L508, "thermal wavevector"); ch05 calls it a "wave number" (L13–14) with "momentum transfer ħk" (L11).
   - ch05 also uses Q in S(Q,ω) (L416), and q as a decay-product wave number (L161); in ch04 q is an index (L455).
   - Helium values are in Å⁻¹; solver values are in 1/ξ (ch05 L382).
2. **c.**
   - 238.3 m s⁻¹ in both chapters (ch04 L57/L75 via `\cfv{c}`; ch05 L20/L292 via `\cfiveV{c}`, and typed literally at L407).
   - c = 1 in GP units (ch05 L316; also ch01 L186, ch03 L41, ch06 L383, ch07 L189, ch09 L25).
   - ch04's `c_p` (coefficient of T^p) collides with the standard isobaric specific heat. ch05's `c_k(t)`, `c_0` are mode amplitudes.
3. **Roton and maxon values (Δ_R, k_R).** ch04 never uses Δ; it quotes the roton as ε/k_B = 8.6 K at 1.92 Å⁻¹ (L66, L557). ch05 uses Δ_R (L62, L106, L109) and bare Δ (L537–539). Three value sets coexist:
   - Calibration and Table III: 0.7418 ± 0.001 meV, k_R = 1.918, μ_R = 0.141 (ch05 L62, L539).
   - Table minimum: 0.741 (0.7413) meV at 1.92 (1.920) Å⁻¹; 8.60 K in ch05, 8.6 K in ch04.
   - Pressure-table P = 0 row: 0.7413 meV at 1.920 Å⁻¹.
   - Maxon: 1.114 Å⁻¹ and 13.8 K (ch04), "near 1.1 Å⁻¹, ~1.19 meV" (ch05 L33), 1.10 Å⁻¹ from the v_g zero (ch05 L431); script-only Table III value 1.191 meV at 1.103 Å⁻¹.
   - The Landau velocity is 57.9 m/s from the table but 58.0 m/s in Exercise 1.
   - Appendix D should say which set it lists.
4. **μ.** μ_R (dimensionless roton mass in units of m_4, ch05 L106) vs the chemical potential μ (ch05 L213, L335; ch09 L25 uses μ as the energy unit). ch04 mentions the chemical potential only in words (L44). μ also appears as the unit prefix in μeV (ch04 L66).
5. **α.**
   - Dispersion coefficients α_1…α_6 in both chapters. ch05 also has α_k (a mode amplitude, L324) and α_2^Bog. ch07 has the mutual-friction α and α′ (ch07 L8–L125).
   - The Lean name for α_2 differs by module: `a2` (PhononSeries, ch04 L181), `a` (`phononDisp`, ch04 L80 and ch05 L137), `α₂` (`seriesDisp`, ch05 L166), `alpha2 c m` (a function, ch05 L254).
6. **Atomic mass.**
   - Neither chapter prints a value. ch05 says "bare atomic mass" and m_4.
   - ch05's scripts use 4.0026032 u (`figures/ch05_helium.py` L7, L20, labelled both "u" and "paper: 4.0026032 g/mol"). That value underlies ħ²/2m_4 = 0.522 meV Å², k_* = 3.00 Å⁻¹ and α_2^Bog = 0.055 Å².
   - ch03 (`figures/ch03_compute.py` L45; printed through macro `mHeU` = 4.002603254) and ch06 (`figures/ch06_constants.py` L14) use the NIST value 4.00260325413 u.
   - The relative difference, 1.4×10⁻⁸, does not show at any printed digit. `figures/appD_numbers.py` (L139, L170–173, L217) already records this split.
   - ch04 uses no atomic mass, only V = 27.5793 cm³/mol. N_A/V = 0.021836 Å⁻³, which matches the density in ch05's script.
7. **Fundamental constants and conversions.**
   - Both chapters' scripts use exact SI-2019 constants (scipy.constants). Neither prints ħ, k_B or the meV→K factor (11.6045 K/meV; `K_per_meV` = 11.60451812155008).
   - ħc for c = 238.3 m/s is 1.5685191 meV Å from SI, which is the value used. The paper's printed prefactor gives 0.0065821·c = 1.56851443 meV Å (ch04_numbers.json `dispersion.hbarc_meV_A_paper_constant`). The relative difference is 3×10⁻⁶; neither value is printed in the text.
8. **Notation style to unify in Appendix D.**
   - "J K⁻¹ mol⁻¹" (ch04 L11) vs "J mol⁻¹ K⁻⁴" (L13); "m s⁻¹" vs "m/s" (ch05 mixes both); "μeV" (ch04) vs "micro-electronvolts" (ch05); `\cfK` vs "kelvin" spelled out (ch05 L34); "1727" (ch04) vs "1\,727" (ch05).
   - **Units errors:** ch04 L111/L342 (K^-p should be K^-(p+1)), ch05 L158 (missing ħ), ch05 L304 (ω used as an energy), ch05 L529 (ℓ called "dimensionless").
9. **Healing length.** ch05 ξ = ħ/mc (L225, L316) is consistent with ch03 L41 (ħ/√(mgn_0)) and ch09 L25 (ħ/√(mμ)); ch01, ch06 and ch07 just set ξ = 1. It differs by √2 from the common ħ/√(2mgn), so Appendix D should state the book's convention.
10. **Density.** n (ch05 L213), n_0 (ch05 L316, L335; ch03 L41), "mean density n" (ch06 L383, ch07 L189) and ρ (ch05 L232) all denote the same quantity.
11. **Letters reused across the two chapters.**
    - T: temperature (ch04) vs record duration (ch05 L321; T = 4 and 20 in the CVODE tables).
    - V: molar volume vs body velocity and V(k).
    - The coefficients A, C, D, E, K, L (ch04) vs D (flight distance), E_i (incident energy), K5 (label) and L (box size) in ch05.
    - g: ch04 g_n vs ch05 GP coupling and energy balance.
    - η: inverse-series coefficient vs pulse amplitude.
    - u: ε/ħc vs Bogoliubov amplitude. x: ħck/k_BT and others vs k/k_* and position.
    - n: index vs density. m: exponent vs mass.
    - s: Mellin variable or fit exponent vs s_k(t) and s(k).
    - R: ring or radius vs the roton subscript.
    - k_max: 2.5 Å⁻¹ integration limit vs grid maximum.
    - k_0: threshold wave numbers in ch04, a plane-wave mode in ch02 L224; in neither case the roton.
12. **ε vs E.** ch04 uses only `\varepsilon` (excitation energy), and E for both the thermal energy E(T) and the T⁷ coefficient. ch05 uses `\varepsilon` (excitation energy) and `\epsilon` with two meanings (free-particle ε_k at L304/L550, wave amplitude at L486–489).
13. **Shared data source.** Both chapters read the same open table (Godfrin 2021 arXiv ancillary `DispersionP0allRange.txt`, named only in scripts). Its grid is described loosely in ch04 L23 ("0.05 beyond"; the first step is actually 0.006) and exactly in ch05 L14. ch04's C_V/T³ = 0.0780 at 0.5 K is the total including rotons.
14. **Attribution of α_2 = 1.55 Å².** ch04 credits only the paper (L75); ch05 credits Rugar & Foster for 1.55 ± 0.01 (L127) and the paper for the full set. Synonyms in use: "positive phonon dispersion" (Phillips 1970 title, ch04 L19) = "anomalous" (ch04 L80, ch05 L128); the paper writes γ = −α_2 (ch05 L128). Both chapters spell it "saturated vapour pressure".
15. **Not quoted by either chapter:** the λ-point temperature, mass density, the numerical atomic mass, and any Donnelly–Barenghi value (Donnelly1991 is cited in ch04 L615 only as a textbook).
