# Exécuter le projet sur un serveur plus puissant (CPU/GPU modernes)

Plan du 2026-10-11, complément de `PROJET_DIMENSION_ET_FRUSTRATION_2026-10.md`. Le kit `deploy/` est **écrit mais non testé**
(aucune exécution sur un autre serveur n'a eu lieu).

## 1. Ce qui demande de la puissance, et de quel type

| Tâche | Goulot mesuré | Ressource utile | Remarque |
|---|---|---|---|
| Reconstruction du théorème amont (`openai/math`, 227 fichiers, 66 k lignes Lean) | CPU, mémoire (1.5-4 Go/processus), certains fichiers 900-1500 s | beaucoup de coeurs (32+), 128 Go RAM | parallélisable par DAG (`pbuild.py`) ; **pas de GPU** |
| `GatedKernel.lean`, kit Mathlib, `lake build` Mathlib | CPU | 8-16 coeurs | cache Mathlib (`lake exe cache get`) évite la recompilation |
| `dimlift` E1/E2 (L-BFGS, N=60, 6 formes x 2 noyaux x 4 méthodes x 30 tirages) | CPU, déjà parallèle par processus | 32+ coeurs | gain GPU faible (petites tailles) ; 100+ tirages devient possible |
| `mesh3d` E3 (N=216-432, Delaunay) | CPU (scipy) | coeurs | N 2000+ : Delaunay CPU, noyau CM en GPU (JAX/CuPy) possible |
| Krylov/ETD 64x64+ (FFT 2D, 3 champs) | FFT, GMRES | **GPU** (cuFFT) ou CPU rapide | 128x128 et 256x256 deviennent réalistes ; réécriture nécessaire (Rust+CUDA ou Python JAX) |
| E4 (S^3, 3D, N 1e3-1e4) | paires O(N^2) | **GPU** (JAX/CuPy) | noyau naïf O(N^2), listes de voisins ensuite |
| Flot Fenris L6 grandes tailles | CVODE dense jusqu'à 1500 libres | CPU ; au-delà : Krylov | l'engin actuel plafonne à 1500 nœuds |

## 2. Principes d'exécution

1. **Environnement reproductible** : Dockerfile (`deploy/Dockerfile`) fixant Lean 4.34.1 / Mathlib v4.34.1 (lake-manifest),
   Rust stable, Python 3.12 et dépendances ; versions épinglées dans `lean-toolchain`, `Cargo.lock`, `uv.lock`.
2. **Gestionnaire de tâches** : manifeste `deploy/jobs.tsv` (une ligne = une tâche, ressources, commande) et script
   Slurm (`deploy/slurm_array.sh`) ; sans Slurm, `make -j` (`deploy/Makefile`).
3. **Données/résultats** : les sorties vont dans `results/` du dossier de tâche ; seul le résumé (`summary.json`) revient au
   dépôt ; les gros états `.f64` restent sur le serveur et sont référencés par hachage.
4. **Sécurité** : aucun jeton dans l'image ni dans le dépôt ; les jetons Zenodo/GitHub restent sur la machine de
   publication ; le serveur de calcul n'a pas de droit de dépôt.
5. **Discipline scientifique inchangée** : pré-enregistrement commité avant les runs ; amendements datés ; le serveur ne
   change pas les critères ; un run qui échoue son contrôle est invalide ; vérification indépendante avant dépôt.

## 3. Ordre de migration proposé

1. Cloner le dépôt, construire l'image, exécuter `make smoke` (tests rapides : `lake env lean GatedKernel.lean`,
   `cargo test` de `qf-exciton-etd` et `qf-exciton-kr`, un tirage `dimlift`).
2. Reconstruire le théorème amont en parallèle (`make upstream`, 32 coeurs : ordre de grandeur 1-2 h au lieu de ~10 h) et
   exécuter `GatedKernelBridge.lean`.
3. Lancer E1/E2 avec 100 tirages et le noyau g3 sur les 6 formes (`make e12`).
4. Porter le noyau de paires en JAX/CuPy et lancer E4 (S^3) puis les grandes tailles de `mesh3d` (`make e4`, GPU).
5. Krylov 128x128 : réécriture FFT sur GPU, comparaison aux résultats 8-64 existants (critère d'accord 1e-8).

## 4. Dimensionnement indicatif (à confirmer par mesure)

* Un noeud 32-64 coeurs, 128-256 Go RAM, 1 GPU 24-80 Go : suffisant pour L0-L4 ; L6 (grilles 128-256) demande surtout du GPU.
* Stockage : 100-300 Go (olean Mathlib + amont ~ 30-40 Go ; états Krylov 64x64+).
* Coût : à estimer sur le prestataire retenu ; non évalué ici.

## 5. Risques

* Reproductibilité inter-machines des flottants (ordre des réductions) : fixer les graines, comparer à tolérance.
* Dérive de version de Mathlib si le cache est mis à jour : épingler le commit.
* Temps de GPU gaspillé sur des petites tailles : ne porter sur GPU que ce qui dépasse N ~ 1e3.
