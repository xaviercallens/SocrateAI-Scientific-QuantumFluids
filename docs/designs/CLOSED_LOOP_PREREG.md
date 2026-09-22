# Pré-enregistrement — boucle fermée stabilité / dualité de Kantorovich (2026-09-22)

**Committé avant tout calcul sur les données GP.** Reprend `CLOSED_LOOP_PLAN.md` §4–§5 avec les choix
tranchés (§8 de ce même document) : paire de résolution ξ/Δx = 4 contre 8, seuil θ = 0,5 n₀, paire
d'espace des phases f_S1/f_S2 incluse. Aucun critère ne sera modifié après avoir vu un résultat ; tout
amendement sera daté et motivé, jamais réécrit en place.

## Paires testées

| # | Type | A | B | Grille de comparaison |
|---|---|---|---|---|
| R1 | résolution | ψ(t=5), N=1024 (ξ/Δx=8), restreint | ψ(t=5), N=512 (ξ/Δx=4), natif | N=512 |
| R2 | résolution | ψ(t=10), idem | idem | N=512 |
| R3 | résolution | ψ(t=20), idem | idem | N=512 |
| T1 | temps | ψ(t=5), N=1024 | ψ(t=10), N=1024 | N=1024 |
| T2 | temps | ψ(t=10), N=1024 | ψ(t=20), N=1024 | N=1024 |
| S1 | son seul | ψ_son, N=1024 | ψ(t=5), N=1024 | N=1024 |
| P1 | espace des phases | f_S1(t=80) | f_S2(t=80) | natif (128×512) |

Restriction résolution→résolution : grilles emboîtées (dx_1024 = dx_512 / 2), on garde un point sur
deux du champ fin. ρ = \|ψ\|² / ⟨\|ψ\|²⟩ partout (normalisation par la moyenne, comme dans D0/D1).

## Contrôles à réponse connue (§4 du plan) — doivent passer avant d'ouvrir les paires GP

- **C1** : cycle à 8 points, f = (1,5,2,6,3,7,4,8), g = f avec v₅ := 4,5. Attendu, exact :
  Dgm₀(f) = {(2,5), (3,6), (4,7)} + essentielle (1,∞) ; Dgm₀(g) = {(2,5), (3,6), (4, 4,5)} + (1,∞) ;
  d_B = 1,5 ; ε = ‖f−g‖∞ = 2,5 ; W₁ = 1,75, couplage {a↔a′, b↔b′, c→Δ, c′→Δ}, potentiels
  φ=(0 ; 0,5 ; 1,5), ψ=(0 ; −0,5 ; 0,25). Tolérance 10⁻⁹.
- **C2** : g′ = f avec v₆ := 4,5 seul. Attendu, exact : d_B = ε = 0,5.
- **C3** (négatif) : potentiels avec ψ_c′ := 0,5 doivent être **rejetés** (violent φ_c+ψ_c′ ≤ coût(c,c′)) ;
  le couplage c↔c′ (coût 2,5) ne doit **pas** être accepté comme optimal (2,5 ≠ 1,75).
- **C4** (négatif) : recalcul de C1 avec construction V au lieu de T sur un seul champ — l'égalité de
  dualité D0 (`duality_defect`) ne doit **plus** tenir.

**Arrêt** : si C1–C4 ne reproduisent pas ces valeurs exactement, on cherche le bug du pipeline ; aucune
donnée GP n'est ouverte tant que ce n'est pas résolu.

## Prédictions sur les données GP (grille θ ∈ {0,3 ; 0,5 ; 0,7} n₀, θ principal = 0,5)

| # | Énoncé | Critère de passage |
|---|---|---|
| P1 | d_B ≤ ε pour **chaque** paire (R, T, S, P) | tient strictement, marge rapportée |
| P2 | N_{>θ+2ε}(A) ≤ N_{>θ}(B) ≤ N_{>θ−2ε}(A) pour chaque paire et chaque θ de la grille | tient |
| P3 | pour R1–R3, ε ≥ 0,25 n₀ | rapporté seul, sans seuil pass/fail |
| P4 | pour R1–R3, part des barres finies de A dans la bande [θ−2ε, θ+2ε] à θ=0,5 | rapporté seul |
| P5 | pour chaque paire, W₁ (GUDHI, k=30 barres les plus longues par diagramme) = valeur du LP primal =
      valeur du LP dual, à 10⁻⁶ près relative | tient |
| P6 | Lean accepte tous les certificats de P5 et rejette la variante C3 | tient |

Un échec de P1 ou P2 après C1–C4 validés est un bug du pipeline sur les données réelles (périodicité,
normalisation), signalé comme tel, jamais reformulé en résultat. P3–P4 sont des mesures, pas des tests.

## Ce que la boucle ne teste pas

Le théorème de stabilité de Cohen-Steiner–Edelsbrunner–Harer (2007) lui-même n'est pas démontré ici — il
est cité et vérifié empiriquement sur des cas connus (P1). Aucune affirmation nouvelle sur les vortex
n'est faite : c'est un test d'instrument, pas une mesure physique.
