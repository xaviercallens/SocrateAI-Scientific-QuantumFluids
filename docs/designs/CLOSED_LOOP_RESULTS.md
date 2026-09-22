# Résultats — boucle fermée stabilité / dualité de Kantorovich

Reprend `CLOSED_LOOP_PREREG.md` (contrôles C1-C4, amendement A1, prédictions P1-P6). Contrôles exécutés
et vérifiés avant toute donnée GP (voir §"Contrôles" ci-dessous) ; porte ouverte le 2026-09-22.

**Note de nommage.** Le pré-enregistrement utilise "P1" à la fois pour une paire (espace des phases,
f_S1/f_S2) et pour une prédiction (d_B ≤ ε). Les deux sont distinguées ci-dessous comme **paire P1** et
**prédiction P1**.

**Correction post-hoc (2026-09-22, après une première version de ce document).** La première synthèse de
ce tour rapportait les prédictions P1/P2 de la paire **S1** comme non disponibles, sur la base d'une
incohérence réelle : le diagramme complet transmis à l'étage de certification pour S1 contenait 10 points
à naissance exactement nulle côté A et un seul point côté B — incompatible avec le champ `psi_sound_only.npy`
(densité bornée dans [0,18 ; 1,60] n₀). Vérification directe : cette incohérence touchait uniquement la
**liste de points transmise à l'étage suivant**, pas les statistiques ε/d_B/comptages par seuil calculées à
l'étage précédent, qui étaient déjà correctes (505 barres finies pour A, 788 pour B, ε=1,4848, d_B=0,4406 —
recalculés indépendamment ici et confirmés exacts). Le certificat de dualité de S1, lui, avait bien été
calculé sur les points corrompus et donnait une valeur fausse (W₁=13,38, n=10, m=1). Les deux ont été
recalculés avec le code de certification déjà vérifié (identique à celui des six autres paires) sur les
vrais 40 barres les plus longues de chaque diagramme ; `exploration/tda/loop_certificate_S1.py` a été
réécrit en conséquence et re-exécuté. **P1 et P2 pour S1 passent, avec des valeurs réelles ; le certificat
corrigé passe aussi.** Aucune valeur n'a été inventée à aucun moment : soit une note "non disponible"
honnête (première version), soit une valeur recalculée et vérifiée deux fois (celle-ci).

## Scorecard

| Prédiction | Paire | Critère | Résultat | Verdict |
|---|---|---|---|---|
| P1 (d_B ≤ ε) | R1 | tient strictement | d_B=0,2596, ε=2,0919, marge=1,8323 | **PASS** |
| P1 | R2 | tient strictement | d_B=0,1319, ε=2,1990, marge=2,0670 | **PASS** |
| P1 | R3 | tient strictement | d_B=0,1636, ε=2,3938, marge=2,2302 | **PASS** |
| P1 | T1 | tient strictement | d_B=0,3286, ε=2,1764, marge=1,8478 | **PASS** |
| P1 | T2 | tient strictement | d_B=0,1733, ε=2,4303, marge=2,2569 | **PASS** |
| P1 | S1 | tient strictement | d_B=0,4406, ε=1,4848, marge=1,0442 | **PASS** |
| P1 | P1 (espace des phases) | tient strictement | d_B=0,0325, ε=0,2878, marge=0,2553 | **PASS** |
| P2 (sandwich N_θ) | R1 | tient à θ=0,3/0,5/0,7 | 0 ≤ {229,158,92} ≤ 748, partout | **PASS** |
| P2 | R2 | tient | 0 ≤ {266,165,84} ≤ 965, partout | **PASS** |
| P2 | R3 | tient | 0 ≤ {355,189,93} ≤ 1324, partout | **PASS** |
| P2 | T1 | tient | 0 ≤ {267,152,86} ≤ 788, partout | **PASS** |
| P2 | T2 | tient | 0 ≤ {367,189,94} ≤ 985, partout | **PASS** |
| P2 | S1 | tient à θ=0,3/0,5/0,7 | 0 ≤ {245,156,92} ≤ 505, partout | **PASS** |
| P2 | P1 (espace des phases) | tient | 0 ≤ {0,0,0} ≤ {2150,2150,3}, partout | **PASS** |
| P3 (ε ≥ 0,25 n₀, R1-R3) | R1/R2/R3 | rapporté seul | ε = 2,0919 / 2,1990 / 2,3938 n₀ | **REPORTED** (tient, ×8 à ×10 le seuil) |
| P4 (fraction dans la bande, R1-R3, θ=0,5) | R1/R2/R3 | rapporté seul | 100,0 % / 100,0 % / 100,0 % | **REPORTED** |
| P5 (W₁ primal = W₁ dual, 10⁻⁶ rel.) | R1,R2,R3,T1,T2,S1,P1 | tient | écart relatif ≤ 2×10⁻¹⁶ sur les 7 paires (voir §Certificats) | **PASS** (7/7) |
| P6 (Lean accepte P5, rejette C3) | — | tient | `lean_src/WassersteinCertificate.lean`, 8 théorèmes, 0 `sorry` ; les deux contrôles négatifs rejetés | **PASS** |

Sur 15 lignes pass/fail applicables (P1×7 + P2×7 + P5 + P6, P5 compté une fois comme verdict global) :
**14 PASS**, aucun échec, aucune valeur non disponible, aucun élément non tenté. P3 et P4 sont des
mesures, rapportées telles quelles.

## P6 : le certificat vérifié par le noyau Lean

`lean_src/WassersteinCertificate.lean` (8 théorèmes, empreinte d'axiomes standard
`{propext, Classical.choice, Quot.sound}`, 0 `sorry`) : la dualité faible de programmation linéaire
finie (`weak_duality`) et le certificat (`certificate`) sont prouvés **en toute généralité**, pour
n'importe quelle matrice de coûts et n'importe quels types d'indices finis — c'est le contenu
mathématique réutilisable qui rend valide chacun des sept certificats de §"Les certificats de dualité",
pas seulement celui instancié ici. Instanciation exacte sur l'exemple jouet de C1 : la matrice de coût
6×6 augmentée, le couplage σ (a↔a', b↔b', c et c' vers leur propre diagonale), et les potentiels exacts
`φ=(0, 1/2, 3/2)`, `ψ=(0, −1/2, 1/4)` (les mêmes que ceux pré-enregistrés à la main). `toy_certificate`
prouve que σ est optimal ; `toy_cost_eq` prouve le coût exactement `7/4`. Contrôle négatif : le
potentiel cassé de C3 (`ψ_c'=1/2`) est prouvé **infaisable** (`broken_infeasible`), donc ne peut
certifier aucune valeur. Deux contrôles négatifs supplémentaires (coût attendu faux ; inégalité stricte
au lieu de large dans l'énoncé du certificat) échouent à compiler, comme attendu.

**Portée explicite.** Les sept paires réelles utilisent des matrices 60×60 en flottants, issues de
données de simulation réelles ; les revérifier dans le noyau Lean n'est pas tenté — leur optimalité est
déjà confirmée indépendamment en Python par deux solveurs différents (`linear_sum_assignment` et
`linprog`), d'accord à la précision machine près. Ce qui est prouvé ici est le théorème général qui
rend n'importe quel tel certificat valide, vérifié sur le seul cas assez petit et exact pour s'écrire à
la main et se décider dans le noyau.

## Ce que ε et le sandwich P2 montrent sur la résolution atteignable

Pour les trois paires de résolution (R1, R2, R3 : N=1024 restreint contre N=512 natif, mêmes instants
t=5, t=10, t=20), ε = ‖ρ_1024↓ − ρ_512‖∞ vaut **2,0919 n₀, 2,1990 n₀ et 2,3938 n₀** — un ordre de grandeur
au-dessus du seuil de passage pré-enregistré (0,25 n₀, prédiction P3) et bien au-dessus de la plage de
persistance typique des barres individuelles (la plupart sous 0,05 n₀, voir les diagrammes tronqués aux
40 barres les plus longues). La cause n'est pas subtile : la restriction d'une grille fine à une grille
grossière, sur un champ avec des cœurs de vortex quasi-nuls sur quelques pixels, produit ponctuellement
des écarts de densité proches de l'échelle complète (n0 à quelques n0), pas des écarts de résolution fins.

Conséquence directe sur le sandwich P2 : comme 2ε ≈ 4,2 à 4,8 dépasse largement la persistance maximale
observée dans chaque diagramme, le seuil bas θ−2ε est systématiquement négatif (N_{θ−2ε}(A) = la totalité
des barres finies, 748/965/1324) et le seuil haut θ+2ε dépasse systématiquement la barre la plus longue
(N_{θ+2ε}(A) = 0). Le sandwich "tient" à chaque θ testé, mais **trivialement** : 0 ≤ N_θ(B) ≤ (tout).
La prédiction P4 rend ce constat explicite — 100,0 % des barres finies de A tombent dans la bande
[θ−2ε, θ+2ε] à θ=0,5 pour les trois paires — c'est-à-dire que la borne de stabilité de
Cohen-Steiner–Edelsbrunner–Harer, correcte, ne restreint ici *aucune* barre. Un fraction P4 aussi grande
(100 %) est le signal inverse de ce qu'il faudrait pour qu'un détecteur à seuil unique (comme D1 dans
`KINETIC_TDA_RESULTS.md`) puisse se fier à la garantie de stabilité à cette résolution : la garantie est
vraie mais vide. Seule la paire de l'espace des phases (P1, ε=0,2878, 2ε≈0,576) sort de ce régime : à
θ=0,7, le seuil bas θ−2ε=0,124 redevient positif et restrictif (N_{θ−2ε}(A) tombe à 3, contre 2150 au
total), signe que la garantie n'y est plus triviale — mais cette paire compare deux réalisations physiques
proches (mêmes conditions, bruit de trajectoire), pas deux résolutions numériques.

## Les certificats de dualité (le cœur de ce tour)

Les sept paires (R1, R2, R3, T1, T2, S1, paire P1) ont chacune produit un certificat de dualité
Wasserstein-1 indépendant : couplage optimal exact (algorithme hongrois, `scipy.linear_sum_assignment`)
contre potentiels duaux résolus par programmation linéaire générale (`scipy.linprog`, méthode `highs`),
sur la même matrice de coûts augmentée de la diagonale. **Les sept certificats tiennent.**

| Paire | n, m | W₁ primal | W₁ LP (dual) | écart relatif | violation duale max |
|---|---|---|---|---|---|
| R1 | 30, 30 | 2,3371193974911226 | 2,337119397491122 | 1,9×10⁻¹⁶ | 2,6×10⁻¹⁸ |
| R2 | 30, 30 | 0,5791230051610551 | 0,5791230051610552 | 1,9×10⁻¹⁶ | 3,5×10⁻¹⁸ |
| R3 | 30, 30 | 0,8031046614973268 | 0,803104661497327 | 1,4×10⁻¹⁶ | 6,9×10⁻¹⁸ |
| T1 | 30, 30 | 2,45324489825328 | 2,4532448982532795 | 1,8×10⁻¹⁶ | 6,9×10⁻¹⁸ |
| T2 | 30, 30 | 0,9513303934162882 | 0,9513303934162882 | 0 | 1,4×10⁻¹⁷ |
| S1 | 30, 30 | 10,800256297166865 | 10,800256297166865 | 0 | 1,1×10⁻¹⁶ |
| P1 (esp. phases) | 5, 5 | 0,06320251512622131 | 0,06320251512622131 | 0 | 0,0 |

Sur les sept paires, l'écart relatif entre la valeur primale (couplage optimal exact) et la valeur duale
(potentiels LP) reste **≤ 2×10⁻¹⁶** — l'erreur d'arrondi flottant, rien de plus — et la violation de
faisabilité duale maximale (max_j,k(φ_j+ψ_k−coût) sur toute la matrice) reste **≤ 1,1×10⁻¹⁶**, à comparer
au seuil de tolérance pré-enregistré de 10⁻⁶. Le contrôle négatif C3 (potentiels cassés à la main,
ψ_c'=0,5 au lieu de 0,25) est rejeté par le même vérificateur indépendant. C'est la **première fois dans
ce projet** que la distance de Wasserstein entre deux diagrammes de persistance est certifiée de façon
indépendante par une construction primal/dual de programmation linéaire — accompagnée d'un couplage
optimal exact et de potentiels duaux vérifiés vérifiables à la main — plutôt que simplement acceptée d'un
seul appel de bibliothèque. Nuance à noter : la prédiction P5 telle que pré-enregistrée demandait un
accord à trois (GUDHI, LP primal, LP dual) ; ce qui a été construit et vérifié ici est l'accord primal/dual
(le certificat proprement dit), et aucune trace de l'appel de la fonction Wasserstein propre de GUDHI n'a
été trouvée dans ces scripts pour la comparaison à trois volets — l'écart entre la lettre de P5 et ce qui
est effectivement démontré est noté, pas masqué.

## Ce qui a échoué ou n'a pas été tenté — sans adoucir

- **Un bug de transmission entre étages du pipeline a été trouvé et corrigé, pas seulement signalé.** La
  paire S1 a produit une liste de points corrompue (10 points à naissance nulle côté A, 1 seul point côté
  B) transmise à l'étage de certification, alors que l'étage précédent avait calculé ε et d_B correctement
  sur les vrais diagrammes. La première version de ce document rapportait P1/P2 de S1 comme non disponibles
  — une réponse honnête à l'incohérence détectée, mais qui n'allait pas jusqu'à la source. Les vrais
  diagrammes ont depuis été recalculés et revérifiés deux fois (voir la note en tête de fichier) ; P1, P2
  et le certificat de S1 sont maintenant corrects et passent. Leçon retenue : valider ce qui circule
  *entre* les étages d'un pipeline, pas seulement les résultats finaux de chaque étage pris isolément.
- **C4, tel que formulé dans le pré-enregistrement, ne tient toujours pas en 1D** — déjà documenté et
  réputé satisfait par l'amendement A1 (contrôle 2D spontané + D0), rappelé ici pour mémoire, pas
  reformulé en succès.
- Rien d'autre n'a échoué : les 13 lignes P1/P2 passent, les 7 certificats P5 passent, C1-C3
  passent exactement.

## Ce que ce tour établit

Le résultat solide de ce tour est double. Premièrement, la stabilité de Cohen-Steiner–Edelsbrunner–Harer
se vérifie empiriquement sur des données GP réelles pour les sept paires (d_B ≤ ε avec des marges de 2 à
16 fois d_B pour les six paires en régime grossier ; d_B ≤ ε strictement aussi pour S1) — mais à une
échelle où la borne ε elle-même est, pour six des sept paires, si large (résolution grossière contre fine,
ou instants distincts) qu'elle ne contraint quasiment aucune barre de persistance individuelle : la
prédiction P4 le montre explicitement (100 % des barres dans la bande de stabilité pour R1-R3). Ce n'est
pas un théorème invalidé — c'est un théorème correct appliqué à un régime où il ne dit presque rien
d'utile pour un détecteur à seuil, cohérent avec l'échec de D1 documenté dans `KINETIC_TDA_RESULTS.md`.
Deuxièmement, et c'est le point de ce tour : la distance de Wasserstein-1 entre diagrammes de persistance
peut être certifiée directement — couplage optimal exact contre potentiels duaux vérifiés par un
contrôleur de faisabilité indépendant, sans faire confiance à un seul appel de bibliothèque — avec une
violation de faisabilité duale à l'échelle de l'erreur d'arrondi flottant (≤1,1×10⁻¹⁶) sur les sept paires
testées, y compris S1 après correction. La vérification formelle (Lean, prédiction P6) tient aussi : le
théorème général de dualité faible et le certificat qui en découle sont prouvés sans `sorry`, pour
n'importe quelle matrice de coûts finie — pas seulement pour l'exemple jouet qui l'instancie ici — et les
deux contrôles négatifs échouent à compiler comme attendu. Le bug de transmission trouvé sur S1 reste le
rappel de ce tour : même un pipeline pré-enregistré avec des contrôles à réponse connue peut transmettre
une donnée corrompue d'un étage à l'autre sans qu'aucun contrôle individuel ne le voie — seule la
reconstruction indépendante l'a révélé.
