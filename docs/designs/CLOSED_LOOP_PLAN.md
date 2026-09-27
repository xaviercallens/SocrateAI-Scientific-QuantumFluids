# Plan d'exécution de la boucle fermée — stabilité des diagrammes, dualité de Kantorovich, critère de résolution

**Statut : PLAN (2026-09-22), à exécuter par un workflow d'agents de bas niveau. Rien n'est implémenté
ici. Ce document est le cahier des charges ; la pré-enregistrement (§5) doit être commité avant le
premier nombre, comme toujours dans ce projet.**

Objet : une seule boucle, exécutable avec ce que le projet possède déjà.

```
Simulation (deux champs ρ₁, ρ₂ de GP 2D, même grille)
   → TDA (diagrammes H₀ de sous-niveaux, GUDHI)
   → Théorie (théorème de stabilité : d_B ≤ ‖ρ₁ − ρ₂‖∞ — réponse connue, jamais testée ici)
   → Dualité (W₁ entre diagrammes, certifiée par couplage + potentiels de Kantorovich–Rubinstein)
   → Lean 4 (vérification décidable des certificats)
   → Physique (critère quantitatif de résolution pour toute détection par seuil de profondeur)
   → retour à la simulation (quelle résolution suffit, et pourquoi)
```

Chaque flèche transporte un nombre qu'un autre maillon connaît. Personne ne découvre rien ; la boucle
est fermée quand tous rendent la même valeur.

---

## 1. Expérience de pensée — à la main, huit points, tout en rationnels

C'est le cœur du document : un exemple assez petit pour être vérifié sans machine, assez riche pour
contenir le mécanisme exact qui a réfuté D1 (`KINETIC_TDA_RESULTS.md`). Il devient ensuite **le premier
contrôle à réponse connue** du pipeline (§4, C1–C2) et **le premier cas de test des théorèmes Lean** (§6).

### 1.1 Un champ sur un cycle

Prenons huit sites sur un cycle (le domaine périodique 1D, analogue minimal d'une grille périodique), avec
la « densité »

| site | v₀ | v₁ | v₂ | v₃ | v₄ | v₅ | v₆ | v₇ |
|---|---|---|---|---|---|---|---|---|
| f | **1** | 5 | **2** | 6 | **3** | 7 | **4** | 8 |

Quatre minima locaux (en gras), quatre maxima (les cols). H₀ des sous-niveaux, règle de l'aîné : chaque
minimum naît à sa valeur, et meurt au col le plus bas qui le relie à un bassin plus ancien (plus bas).

| minimum | né à | cols voisins | meurt à | barre | longueur (= proéminence) |
|---|---|---|---|---|---|
| v₀ = 1 | 1 | 5, 8 | jamais (classe essentielle) | (1, ∞) | ∞ |
| v₂ = 2 | 2 | 5, 6 | 5 (rejoint v₀) | (2, 5) | 3 |
| v₄ = 3 | 3 | 6, 7 | 6 (rejoint v₀∪v₂) | (3, 6) | 3 |
| v₆ = 4 | 4 | 7, 8 | 7 (rejoint le reste) | (4, 7) | 3 |

Dgm₀(f) = {(2,5), (3,6), (4,7)} plus l'essentielle (1, ∞).

### 1.2 La perturbation qui a tué D1 : le col descend, le cœur ne bouge pas

Ne touchons **pas** au minimum v₆ (le « cœur de vortex », valeur 4) ; abaissons seulement le col v₅ de 7 à
4,5 — un canal de basse densité s'ouvre entre deux cœurs, exactement ce que la turbulence compressible
faisait dans D1.

| site | v₀ | v₁ | v₂ | v₃ | v₄ | v₅ | v₆ | v₇ |
|---|---|---|---|---|---|---|---|---|
| g | 1 | 5 | 2 | 6 | 3 | **4,5** | 4 | 8 |

‖f − g‖∞ = 7 − 4,5 = **2,5**. Le site v₅ = 4,5 reste un maximum local (4,5 > 3 et > 4).

| minimum | né à | cols voisins | meurt à | barre | longueur |
|---|---|---|---|---|---|
| v₀ | 1 | 5, 8 | jamais | (1, ∞) | ∞ |
| v₂ | 2 | 5, 6 | 5 | (2, 5) | 3 |
| v₄ | 3 | 6, 4,5 | 6 (à 4,5 il *absorbe* v₆, il ne meurt pas) | (3, 6) | 3 |
| v₆ | 4 | 4,5, 8 | 4,5 (rejoint v₄, plus ancien) | (4, 4,5) | **0,5** |

Dgm₀(g) = {(2,5), (3,6), (4, 4,5)} plus (1, ∞). **La barre de v₆ est passée de longueur 3 à 0,5 sans que
v₆ ait changé.** Un détecteur « profondeur > 1 » — la règle de D1 — voit v₆ dans f et ne le voit plus dans
g. C'est le mécanisme, isolé, en quatre lignes.

### 1.3 Le théorème de stabilité, vérifié à la main

Le théorème de Cohen-Steiner–Edelsbrunner–Harer (Discrete Comput. Geom. 37, 103, 2007) dit :
d_B(Dgm f, Dgm g) ≤ ‖f − g‖∞. La distance goulot d_B est le coût du meilleur appariement partiel, où un
point (b, d) non apparié est envoyé sur la diagonale au coût (d − b)/2, et deux points appariés coûtent
leur distance ℓ∞ ; d_B est le **maximum** des coûts de l'appariement.

- (2,5) ↔ (2,5) : 0 ; (3,6) ↔ (3,6) : 0 ; (1,∞) ↔ (1,∞) : 0.
- Reste (4,7) et (4, 4,5). Les apparier coûte max(|4−4|, |7−4,5|) = 2,5. Les envoyer tous deux sur la
  diagonale coûte max(1,5 ; 0,25) = **1,5**. Ce dernier est meilleur.

**d_B = 1,5 ≤ 2,5 = ‖f − g‖∞.** Le théorème tient, avec une marge. Et la marge dit quelque chose de précis :

> **Corollaire pour les détecteurs à seuil (à pré-enregistrer, §5).** Si ‖f − g‖∞ ≤ ε, une barre de
> longueur L > 2ε ne peut pas aller sur la diagonale ; elle est appariée à une barre de longueur ≥ L − 2ε.
> Donc, pour tout seuil θ :
> N_{>θ+2ε}(f) ≤ N_{>θ}(g) ≤ N_{>θ−2ε}(f),
> où N_{>x} compte les barres finies de longueur > x. **Un comptage par seuil θ n'est stable sous une
> perturbation ε que si les barres près de θ sont rares dans la bande [θ − 2ε, θ + 2ε].** Ici ε = 2,5,
> θ = 1 : la bande est [−4, 6], elle contient tout ; le comptage n'était protégé par rien. C'est
> exactement ce qui manquait à D1 : personne n'avait mesuré ε entre deux résolutions.

Contre-exemple utile (**le cas serré**) : si l'on relève le cœur v₆ de 4 à 4,5 sans toucher aux cols,
‖f − g‖∞ = 0,5 et la barre (4,7) devient (4,5 ; 7) : d_B = 0,5 = ε. La borne est atteinte. Le pipeline
doit rendre l'égalité exacte sur ce cas (§4, C2).

### 1.4 La dualité : W₁ entre les deux diagrammes, certifié à la main

La distance de Wasserstein d'ordre 1 entre diagrammes (coût au sol ℓ∞, diagonale autorisée, c'est ce que
calcule `gudhi.wasserstein.wasserstein_distance` avec `order=1, internal_p=∞`) est la **somme** des coûts
du meilleur appariement, non plus le maximum. Points finis : X = {a=(2,5), b=(3,6), c=(4,7)},
Y = {a'=(2,5), b'=(3,6), c'=(4, 4,5)}.

Matrice des coûts ℓ∞, et coût vers la diagonale Δ (= (d−b)/2) :

| | a' | b' | c' | Δ |
|---|---|---|---|---|
| **a** | 0 | 1 | 2 | 1,5 |
| **b** | 1 | 0 | 1,5 | 1,5 |
| **c** | 2 | 1 | 2,5 | 1,5 |
| **Δ** | 1,5 | 1,5 | 0,25 | — |

**Borne supérieure (primal) — un couplage explicite** : a↔a' (0), b↔b' (0), c→Δ (1,5), c'→Δ (0,25) :
coût **1,75**. (Alternatives : c↔c' donne 2,5 ; c↔b', b↔c' donne 2,5 ; toutes les autres sont pires.)

**Borne inférieure (dual de Kantorovich–Rubinstein) — des potentiels explicites.** Cherchons
φ sur X, ψ sur Y tels que φ_x + ψ_y ≤ coût(x,y) pour tout couple, φ_x ≤ coût(x,Δ), ψ_y ≤ coût(y,Δ).
Pour **tout** couplage, son coût est ≥ Σφ + Σψ (chaque point figure exactement une fois, et on somme les
contraintes) — c'est la *direction facile* de la dualité, une inégalité entre sommes finies. Prenons :

| φ_a | φ_b | φ_c | ψ_a' | ψ_b' | ψ_c' | Σ |
|---|---|---|---|---|---|---|
| 0 | 0,5 | 1,5 | 0 | −0,5 | 0,25 | **1,75** |

Vérification des treize contraintes : φ_a+ψ_a' = 0 ≤ 0 ; φ_a+ψ_b' = −0,5 ≤ 1 ; φ_a+ψ_c' = 0,25 ≤ 2 ;
φ_b+ψ_a' = 0,5 ≤ 1 ; φ_b+ψ_b' = 0 ≤ 0 ; φ_b+ψ_c' = 0,75 ≤ 1,5 ; φ_c+ψ_a' = 1,5 ≤ 2 ; φ_c+ψ_b' = 1 ≤ 1 ;
φ_c+ψ_c' = 1,75 ≤ 2,5 ; φ_a = 0 ≤ 1,5 ; φ_b = 0,5 ≤ 1,5 ; φ_c = 1,5 ≤ 1,5 ; ψ_a' = 0 ≤ 1,5 ; ψ_b' = −0,5 ≤ 1,5 ;
ψ_c' = 0,25 ≤ 0,25. Toutes tiennent.

**Donc 1,75 ≤ W₁ ≤ 1,75 : W₁ = 7/4, certifié.** Un couplage et six nombres suffisent ; aucune
optimisation n'a besoin d'être refaite pour le vérifier. C'est ce que Lean vérifiera (§6) : pas le calcul,
le certificat. Et c'est ce que GUDHI doit rendre à 10⁻⁹ près (§4, C1).

**Ce que l'expérience de pensée établit** : (i) le mécanisme de D1 en quatre lignes ; (ii) que le
théorème de stabilité est une *inégalité testable* avec une marge informative ; (iii) que le comptage
par seuil a une condition de stabilité précise, N_{>θ+2ε} ≤ N_{>θ} ≤ N_{>θ−2ε} ; (iv) que W₁ — le
transport optimal de Villani — entre dans la TDA comme métrique certifiable, pas comme analogie.

---

## 2. Données en main, et ce qu'il faudra peut-être générer

| Donnée | Emplacement | Résolution | Usage |
|---|---|---|---|
| ψ(t = 5, 10, 20) GP 2D, 200 vortex initiaux | `data/generated/kinetic_tda/psi_t{5,10,20}.npy` | N = 1024, ξ/Δx = 8 | paires temporelles (même grille) |
| ψ « son seul » (0 vortex) | `data/generated/kinetic_tda/psi_sound_only.npy` | idem | contrôle : ε grand, diagramme pauvre |
| série de convergence GP | `exploration/gpe/` (`run_own_gpe_converge.py`, `conv.log`) | ξ/Δx = 4 et 8 **à inventorier** | paires de résolution |
| f_S1, f_S2 espace des phases (deux faisceaux) | `data/generated/kinetic_tda/f_S{1,2}_t80.npy` | N_x = 128, N_v = 512 | facultatif : même test en (x, v) |

**Phase 0 (inventaire)** : si la série de convergence n'a pas laissé deux champs *du même état* à deux
résolutions emboîtées (N et 2N, même L, même graine), les générer avec une variante de
`exploration/tda/make_gp_frames.py` — ξ/Δx = 4 (N = 512) et 8 (N = 1024), même graine 1, mêmes instants.

**Définition de la comparaison de résolution (fixée ici, pas après)** : le champ fin est *restreint* aux
points de la grille grossière (grilles emboîtées, N_fin = 2 N_gros) ; les deux diagrammes sont calculés sur
la grille grossière ; ε = max |ρ_fin|_gros − ρ_gros|. Ainsi les deux fonctions vivent sur le **même**
complexe et le théorème s'applique littéralement. Comparer le diagramme du champ fin *sur la grille fine*
à celui de sa restriction est un autre effet (échantillonnage), **exploratoire**, hors critères.

## 3. Les maillons, un par un, avec la réponse connue de chacun

| Maillon | Outil | Entrée | Sortie | Réponse connue |
|---|---|---|---|---|
| Simulation | existant (`run_own_gpe.py`, `make_gp_frames.py`) | graine, N, t | ρ = \|ψ\|²/⟨\|ψ\|²⟩ | — |
| TDA | `src/quantumfluids/tda/cubical.py` (`minima_with_depth`, construction T, périodique) | ρ sur grille | Dgm₀ (barres finies + essentielle) | D0 : T(ρ) ≡ V(−ρ) exactement (fait) |
| Théorie | `gudhi.bottleneck_distance` ; calcul de ε | deux ρ, deux Dgm | d_B, ε, N_{>x} | d_B ≤ ε (CSEH 2007) ; sandwich de §1.3 |
| Dualité | `gudhi.wasserstein.wasserstein_distance` (via POT) + extraction du plan (`matching=True`) + résolution du dual | deux Dgm (sous-échantillonnés, §4) | W₁, couplage, potentiels | primal = dual (§1.4) |
| Lean 4 | `lean_src/DiagramCertificates.lean` (§6) | certificats en rationnels | acceptation / rejet | contrôles négatifs |
| Physique | script de synthèse | ε par paire, N_{>θ} | tableau « ε vs seuil » | le sandwich borne les comptages |

## 4. Contrôles à réponse connue (avant toute donnée physique)

- **C1 — l'expérience de pensée** : f et g de §1 sur un cycle de 8 sites (en 2D : une grille 8×1
  périodique, ou une grille 8×8 constante selon y — préciser, les deux doivent donner le même diagramme
  H₀). Le pipeline doit rendre exactement Dgm₀(f) = {(2,5),(3,6),(4,7)}, Dgm₀(g) = {(2,5),(3,6),(4,4.5)},
  d_B = 1,5, ε = 2,5, W₁ = 1,75, et le couplage {a↔a', b↔b', c→Δ, c'→Δ}. Tolérance 10⁻⁹.
- **C2 — le cas serré** : g′ = f avec v₆ := 4,5 ; d_B = ε = 0,5 exactement.
- **C3 — contrôle négatif du certificat** : les potentiels de §1.4 avec ψ_c' := 0,5 (viole ψ_c' ≤ 0,25) ;
  le vérificateur (Python puis Lean) doit **rejeter**. Et un couplage au coût 2,5 (c↔c') ne doit pas être
  accepté comme optimal face aux potentiels (2,5 ≠ 1,75).
- **C4 — contrôle négatif de la construction** : recalculer C1 avec la construction V au lieu de T sur un
  seul des deux champs ; l'égalité D0 ne tient plus et le test doit le signaler (comme P-D0b).

Si C1–C4 ne passent pas, on n'ouvre pas les données GP.

## 5. Pré-enregistrement (à commiter avant le premier nombre sur les données GP)

Paires : (R) résolution, ξ/Δx = 4 contre 8 restreint, aux trois instants ; (T) temps, t = 5 contre 10,
10 contre 20, même grille N = 1024 ; (S) son seul contre t = 5 (ε grand, contrôle de non-informativité).
Seuil θ = 0,5 n₀ (celui de D1), et une grille θ ∈ {0,3 ; 0,5 ; 0,7} rapportée sans choix a posteriori.

| # | Prédiction | Critère de passage | Sens d'un échec |
|---|---|---|---|
| P1 | d_B ≤ ε pour **chaque** paire | tient, marge ≥ 0 | un échec est un **bug** (construction, périodicité, normalisation), jamais une découverte |
| P2 | sandwich N_{>θ+2ε}(ρ₁) ≤ N_{>θ}(ρ₂) ≤ N_{>θ−2ε}(ρ₁) | tient pour chaque paire et chaque θ | idem : bug |
| P3 | pour (R), ε ≥ 0,25 n₀ à ξ/Δx = 4 (la résolution grossière change la densité de plus d'un quart) | rapporté ; pas de passage/échec | c'est la mesure qui manquait à D1 |
| P4 | pour (R), la bande [θ − 2ε, θ + 2ε] contient ≥ 30 % des barres finies | rapporté | si oui, aucun seuil n'est stable à cette résolution — D1 était réfuté d'avance |
| P5 | W₁(GUDHI) = valeur certifiée (couplage + potentiels) à 10⁻⁹, sur les diagrammes sous-échantillonnés aux k = 30 barres les plus longues | tient | sinon, l'extraction du plan ou du dual est fausse |
| P6 | Lean accepte tous les certificats de P5 et rejette C3 | tient | — |

Sous-échantillonnage pour P5 : les diagrammes GP ont ~10³ points ; le certificat Lean grandit avec k².
On fixe k = 30 (barres les plus longues, les deux diagrammes) et on dit que le certificat porte sur cette
troncature, pas sur le diagramme complet. Le d_B de P1 porte lui sur les diagrammes complets.

**Arrêt** : P1 ou P2 en échec après vérification du pipeline sur C1–C4 → on cherche le bug, on ne
publie rien. P5 en échec → le maillon dualité est cassé, le reste tient seul.

## 6. Les théorèmes Lean visés (non écrits ; portée exacte)

Tout est **fini et décidable** ; rien n'est le théorème de stabilité général, qui reste cité.

| Nom | Énoncé | Difficulté | Contrôle négatif |
|---|---|---|---|
| `wasserstein_weak_duality` | pour deux listes finies de points, un coût, un couplage partiel M et des potentiels (φ, ψ) réalisables : Σφ + Σψ ≤ coût(M) | S (somme finie, réindexation) | — |
| `wasserstein_certificate` | si de plus coût(M) = Σφ + Σψ, alors W₁ (défini comme inf sur les couplages) = coût(M) | S | potentiels de C3 rejetés |
| `bottleneck_upper` | un couplage partiel dont chaque paire est à ℓ∞ ≤ ε et chaque point non apparié à longueur ≤ 2ε donne d_B ≤ ε | S | — |
| `threshold_sandwich` | de d_B ≤ ε : N_{>θ+2ε}(X) ≤ N_{>θ}(Y) ≤ N_{>θ−2ε}(X) | M (combinatoire de l'appariement) | 2ε remplacé par ε doit échouer |
| `toy_cycle_diagram` | Dgm₀ de f et g de §1 calculés par la règle de l'aîné sur un cycle de 8 = les tables de §1 | S/M (`decide` sur un cas fini) | f avec v₅ := 4,5 et v₆ := 4 donne (4, 4,5) et non (4, 7) |

Après Comparator, ces énoncés rejoignent la bibliothèque (161 → ~166). Ce que Lean **ne** fait **pas** :
prouver d_B ≤ ‖f−g‖∞ en général (CSEH 2007 est cité), ni calculer W₁ (GUDHI/POT le fait) — Lean vérifie
que ce qui a été calculé est ce qu'on croit.

## 7. Découpage pour un workflow d'agents de bas niveau

Chaque brief est autonome, avec une entrée, une sortie et un test de réception ; aucun agent ne décide
d'un seuil ou d'un critère (ils sont tous ici). Sept agents, séquence stricte, sauf 3a/3b en parallèle.

| # | Agent | Brief (résumé) | Réception |
|---|---|---|---|
| 0 | Inventaire | lister `data/generated/` et `exploration/gpe/` ; dire si une paire de résolutions emboîtées existe ; sinon écrire la commande exacte pour la générer (ne pas la lancer) | un tableau fichier → (N, ξ/Δx, t, graine) |
| 1 | Contrôles C1–C4 | implémenter `exploration/tda/loop_controls.py` reproduisant §1 et §4 avec `cubical.py` + GUDHI ; imprimer chaque valeur attendue à côté de la valeur obtenue | les huit nombres de C1, l'égalité de C2, les deux rejets de C3, le signal de C4 |
| 2 | Génération (si nécessaire) | exécuter la commande écrite par l'agent 0 | fichiers présents, tailles, checksums |
| 3a | Paires GP | `exploration/tda/loop_pairs.py` : pour chaque paire de §5, ε, Dgm₀, d_B, N_{>x} pour les trois θ et les bandes ; JSON | P1–P4 remplis, sans interprétation |
| 3b | Certificats | `exploration/tda/loop_certificates.py` : troncature k = 30, W₁ GUDHI avec plan, résolution du dual (LP, `scipy.optimize.linprog`), export des certificats en **rationnels** (fractions exactes des valeurs flottantes arrondies à 10⁻⁹) | P5 : égalité primal = dual à 10⁻⁹ ; fichiers `.json` par paire |
| 4 | Lean | `lean_src/DiagramCertificates.lean` avec les cinq énoncés de §6 ; importer les certificats de 3b comme littéraux ; Comparator ; contrôles négatifs | compile sans `sorry` ; P6 |
| 5 | Synthèse | tableau P1–P6, un paragraphe par ligne, sans adjectif ; mise à jour de `KINETIC_TDA_RESULTS.md` et du LEDGER | chaque prédiction a un verdict et une source |
| 6 | Revue adverse | contexte vierge : « qu'objecterait en dix minutes quelqu'un qui connaît la TDA / le transport optimal » | liste d'objections, chacune adressée ou reconnue |

Ce qui reste au propriétaire : le pré-enregistrement (§5) est commité **avant** l'agent 3a ; les
seuils et k ne changent plus ensuite ; toute déviation est une amende datée, jamais une réécriture.

## 8. À construire ensemble — les choix ouverts

1. **La paire de résolution** : 4 contre 8 (ce que le projet a déjà exploré) ou 8 contre 16 (plus proche de
   la convergence, plus coûteux : 2048², ~4× le temps de `make_gp_frames.py`) ?
2. **Le seuil θ** : garder 0,5 n₀ pour parler directement à D1, ou centrer la grille sur la prominence
   médiane des diagrammes (choisie *avant* de regarder les paires GP, sur le contrôle C1) ?
3. **k pour les certificats** : 30 est un compromis lisibilité/Lean ; 100 rendrait le certificat plus
   représentatif mais le fichier Lean lourd. Une seule paire à k = 100 en plus des autres à 30 ?
4. **L'espace des phases** : refaire le même test sur f_S1/f_S2 (le mécanisme de D3 est le même — deux trous
   dans une vallée commune) pour un coût marginal ? Je le recommande, en (S) supplémentaire.
5. **Le sens physique de ε** : rapporter ε en unités de n₀ *et* en fraction de la profondeur médiane des
   barres — c'est la seconde qui dit si un détecteur peut exister à cette résolution.

Le premier pas concret est l'agent 1 : si l'expérience de pensée de §1 ne sort pas du pipeline au chiffre
près, rien d'autre n'a de sens.
