# Projet : dimension, frustration et noyaux complètement monotones, du 2D au 3D

Proposition du 2026-10-11, à relire et amender par X. Callens. Statut : plan de travail, rien n'est engagé au-delà de ce
qui est déjà réalisé (section 1). Règles de la série conservées : pré-enregistrement avant tout run, amendements datés,
vérificateur indépendant puis relecture hostile avant dépôt, résultats négatifs publiés, aucune affirmation qui s'appuie sur
le théorème de réseau planaire non arbitré sans le dire.

## 0. Idée directrice (reformulée après les tests)

L'idée « passer à 8D/24D et projeter en 3D » ne résout pas le 3D (aucun théorème ne transporte l'optimalité d'E8 ou de Leech
vers 3D, et la difficulté est celle des minima locaux, pas de la dimension). Ce qui survit est plus modeste et testable :

1. **la tour de Kaluza-Klein est réelle** : le noyau « gated » est une somme de K0(sqrt(lambda_m) r) à poids positifs, donc
   complètement monotone (théorème démontré, formalisé en Lean) ;
2. **la dualité de Poisson (« T-dualité » des réseaux) est de l'Ewald**, utile pour évaluer des sommes, pas pour la raideur ;
3. **« lever » une frustration passe par la courbure** (Nelson-Sadoc-Kléman : icosaédrique sur S^3), pas par une dimension plate ;
4. **les bords portent la frustration** (identité Q = 6 chi + somme (k_b - 3), vérifiée sur 1031 états) : agir sur le bord
   (murs mobiles, flambage) est plus prometteur qu'agir sur le volume.

## 1. Acquis (au 2026-10-11)

* Zenodo : article I 10.5281/zenodo.23294615, II 10.5281/zenodo.23297479, III 10.5281/zenodo.23298292.
* Note mathématique (5 p.) : noyau gated complètement monotone par noyau de la chaleur de Dirichlet ; proposition
  inconditionnelle : le réseau triangulaire minimise l'énergie parmi les réseaux de Bravais (Montgomery 1988).
* Lean : `GatedKernel.lean` (52 théorèmes, axiomes standard, vérifié indépendamment) ; kit Mathlib
  (`CompletelyMonotoneOn`, Laplace-type) compilé ; `GatedKernelBridge.lean` écrit, en attente de la reconstruction du
  théorème amont (build en cours, 182/227 fichiers).
* Expériences `dimlift` (pré-enregistrées) : E3 (maillage 3D périodique) terminée, E1/E2 en cours (carré, hexagone faits).
  **Résultats provisoires, à ne pas citer avant clôture** : relèvement dimensionnel sans bénéfice à calcul égal (carré,
  hexagone) ; mur mobile réduit le nombre de défauts sur le carré (-2.2 en moyenne, 30 tirages, erreur-type 1.5) ;
  E3 : gate **non atteinte** (CM bat CVT dans 3 cas sur 30 en 5e centile du rapport de rayons ; 0.634 contre 0.679 ;
  fraction de slivers égale).

## 2. Lots de travail

| Lot | Contenu | Livrable | Critère de réussite | Critère d'arrêt |
|---|---|---|---|---|
| **L0 Fondations** | clore le build amont, `#print axioms` du théorème amont, compiler le pont ; lecture humaine du texte (Legoll) ; PR Mathlib A (`CompletelyMonotoneOn`) puis B | pont Lean machine-vérifié ; note relue ; PR ouverte | pont compile, axiomes standard ; au moins un retour humain écrit | amont ne compile pas : rapporter tel quel |
| **L1 Tour KK** | évaluateur de noyau par modes/images (bascule selon r) pour dalles et diélectriques en couches ; lemme Lean `yukawa_admissible` et noyau gated dans `triangular-universal-optimality-lean` | crate Rust + module Lean | erreur relative < 1e-12, vitesse >= 5x les images seules à r > 0.3 d | gain de vitesse < 2x |
| **L2 Relèvement** | clore E1 (6 formes, 2 noyaux) ; E4 : plongement sur S^3 (3D, noyau CM) avec décroissance de courbure, comparaison au 3D direct ; test de référence particules (pas réseaux : le relèvement d'un réseau est vacueux car l'énergie ne dépend que de la matrice de Gram) | rapport pré-enregistré | gain d'énergie moyenne > 2 erreurs-types **et** survit au contrôle à calcul égal | pas de gain : publier le négatif |
| **L3 Bords mobiles** | clore E2 ; fonction « nœuds de mur coulissants » dans `rusty-Fenris-CMRR` (+ balayage de l'espacement de mur, rejeu w=1 avec départs RSA que le vérificateur a demandé) ; flambage 3D de la feuille (Gauss-Bonnet) | PR Fenris + rapport | diminution du nombre de défauts >= 2 sur >= 3 formes, Q conservé là où k_b l'est | effet nul |
| **L4 Maillage 3D** | E3 est négative pour CM seul ; tester CM + CVT hybride et la prise en compte d'un bord CAO (pas de conformité revendiquée) | rapport | rapport de rayons 5e centile >= CVT | pas de gain : arrêter |
| **L5 Expérience** | suivre la diffusion du protocole L1 (pente de blueshift vs séparation de grilles) auprès d'un groupe d'excitons dipolaires ; réponse aux retours | note de protocole v2 | un retour d'un groupe expérimental | silence : relancer une fois |
| **L6 Outils** | publier le solveur Newton-Krylov (SDIRK2+GMRES) et l'ETDRK4 comme crate pour `rusty-SUNDIALS` ; croiser avec l'ETD-RK4 de LeanFlow (SocrateAI-Numeric-DualScale-Solver) sur un cas commun | PR + comparatif | accord à 1e-8 sur un cas commun | écart non expliqué : rapport |

Les dépôts MechanicaFluidorum, DualScaleSimulator et DualScaleTopologicalUniverseModel servent d'infrastructure
d'exigence (grand livre de revendications, tiers épistémiques, vérificateurs) et de solveurs ; **aucun lien physique n'est
affirmé** entre la dualité T des lois de rayon effectif et la dualité de Poisson des réseaux (analogie seulement).

## 3. Calendrier indicatif (12 semaines)

* S1-2 : L0 (pont, relecture, PR Mathlib A), clôture E1/E2, relecture hostile, article IV (« relèvement dimensionnel et murs mobiles »).
* S3-5 : L1 (évaluateur KK + Lean), L3 (murs coulissants dans Fenris).
* S6-8 : L2 (E4 sur S^3), L6 (crate Krylov/ETD).
* S9-10 : L4 (hybride CM+CVT), L5 (retours expérimentaux).
* S11-12 : consolidation, article V si au moins deux lots atteignent leurs critères, sinon note de résultats négatifs.

## 4. Ressources et risques

* Calcul : machine partagée à 8 coeurs ; le build amont (66 k lignes Lean) et les runs se disputent le CPU ; prévoir de
  les séquencer. Aucun GPU requis.
* Risque principal : sur-interprétation (« 8D/24D résout le 3D »). Parade : seuls les critères ci-dessus font foi.
* Risque épistémique : le théorème amont est généré par IA et non arbitré ; la lecture humaine du texte de l'énoncé (cinq
  définitions) est le goulot, pas la preuve (vérifiée par le noyau Lean).
* Risque de crédit : l'IA ne peut être auteur ; déclarer l'assistance (arXiv, revues, Mathlib).

## 5. Décisions demandées

1. Valider l'ordre L0 -> L3 -> L2 (ce qui a déjà un effet mesuré d'abord).
2. Autoriser le dépôt d'un article IV (relèvement + murs mobiles, négatifs inclus) quand E1/E2 sont closes et relues.
3. Choisir l'invité humain pour la relecture de l'énoncé amont (cinq définitions Lean) en plus de F. Legoll.
