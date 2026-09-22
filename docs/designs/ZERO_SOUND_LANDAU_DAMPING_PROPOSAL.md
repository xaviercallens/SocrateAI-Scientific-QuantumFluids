# Proposition : amortissement de Landau du son zéro dans l'hélium-3 bidimensionnel — un objet commun pour C. Villani et H. Godfrin

**Statut : PROPOSITION (2026-09-22). Rien n'est implémenté. Le hold sur tout contact reste en vigueur
(`docs/FOR_GODFRIN.md` §0).**

## 1. Pourquoi cet objet et pas un autre

Le point de rencontre n'est pas à inventer : l'équation cinétique de Landau pour un liquide de Fermi sans
collisions est une équation de type Vlasov (transport libre + champ moyen donné par les paramètres de
Landau F₀ˢ, F₁ˢ…), et l'amortissement de Landau du son zéro — le mode collectif qui entre dans le
continuum particule-trou — est exactement le phénomène de Mouhot–Villani, avec F₀ˢ à la place de 1/k².
Godfrin a mesuré ce mode par diffusion de neutrons dans une monocouche de ³He (Nature 483, 576, 2012) ;
Villani a démontré la version non linéaire du phénomène (Acta Math. 2011), formalisée en Lean par
Bedrossian (arXiv:2609.16801, fond petit, sans relation de dispersion ni critère de Penrose).

Ce qui rend le cas **bidimensionnel** singulier, et c'est le cœur de la proposition : la fonction de
Lindhard 2D est **algébrique** (Ω(s) = 1 − s/√(s²−1) hors continuum, 1 + i s/√(1−s²) dedans), alors qu'en
3D elle est logarithmique. Toute la théorie linéaire — racines, taux d'amortissement, seuil d'entrée dans
le continuum, critère de stabilité — se réduit à des équations polynomiales. *Sans approximation* n'est
donc pas un slogan : c'est le régime où Lean peut tout prouver et où une énumération certifiée est exacte.

## 2. Ce qui existe déjà et sert directement

| Actif | Réutilisation |
|---|---|
| `ZeroSound.lean` (6 thm.) : son zéro non amorti ⟺ F₀ˢ > 0, 2D et 3D, racine 2D explicite (1+F)/√(1+2F) | premier énoncé du programme ; à étendre à F₁ˢ et au continuum |
| `dispersion.py` : racines certifiées (Arb, Newton par intervalles) de relations de dispersion Vlasov | remplacer Z(ζ) par Ω₂(s) : le code est le même |
| `vlasov.py` : solveur 1D1V semi-lagrangien validé à 0,14 % contre une racine certifiée, échos et récurrence épinglés | remplacer v ∈ ℝ par θ ∈ S¹ (vitesse v_F(cos θ, sin θ)) et E par l'intégrale de Landau ∫ F(θ−θ′) δn(θ′) : même structure, même coût |
| `PhononSeries` : troncature comme nilpotence, certificats CAS vérifiés par le noyau | pour les développements en petit q / petit F |
| Ancillaires Godfrin (PRB 103, 104516) et méthode de comparaison à résolution instrumentale (`HeliumKinematics`) | convolution avec la résolution IN5 |
| Discipline : pré-enregistrement, contrôles négatifs, portes littérature, registre | obligatoire vu le bilan TDA (5 propositions, 5 réfutées) |

## 3. Programme, en quatre volets

**V1 — Théorie linéaire exacte, en Lean (Villani ↔ Godfrin, via la même équation).**
- `zero_sound_F1` : condition de son zéro avec F₀ˢ et F₁ˢ en 2D ; existence, unicité, position s(F₀,F₁)
  — tout algébrique.
- **« Pomeranchuk = Penrose »** : la stabilité de l'équation cinétique de Landau 2D (aucune racine à
  Im ω > 0) équivaut à F₀ˢ > −1. C'est le critère de Penrose spécialisé au fond de Fermi, prouvable sans
  transformée de Laplace précisément parce que tout est algébrique. Bedrossian écrit que ce volet manque
  à sa formalisation ; ce serait la première pièce de ce type.
- Taux d'amortissement de Landau dans le continuum : formule fermée, prouvée.
- Chaque énoncé avec contrôle négatif (F₀ˢ > −1 remplacé par ≥ −1 doit échouer) et Comparator.

**V2 — Énumération certifiée, en Arb.** Pour chaque pression mesurée par Godfrin (densité surfacique →
v_F, m*, F₀ˢ, F₁ˢ tirés de la littérature, sources à fixer avant tout calcul) : boule certifiée
contenant la racine, seuil q_c d'entrée dans le continuum, largeur d'amortissement Γ(q). Contrôle négatif :
une boule décalée doit être rejetée.

**V3 — Solveur cinétique de Landau 2D, haute performance.** δn(x, θ, t) sur un tore : transport exact
en Fourier, champ moyen par convolution angulaire, splitting de Strang. Validation : taux linéaire dans
la boule certifiée de V2 (ce que nous avons fait pour Vlasov), récurrence et écho **champ coupé** où ils
sont exacts. Puis la question que seul le solveur pose : **le scénario de Mouhot–Villani (amortissement
non linéaire, retour vers le transport libre) tient-il pour les paramètres de Landau réels du ³He 2D ?**
Et la variante Fermi-liquide de l'écho à deux impulsions — un écho de son zéro — a-t-elle une signature
observable ? (Question ouverte ; kill : si l'amplitude prédite est sous le bruit de toute mesure
envisageable, on le dit et on arrête.)

**V4 — Confrontation à l'expérience, comme modèle nul certifié.** Le résultat de Nature 2012 est
justement que le mode mesuré (type roton) *n'est pas* décrit par la théorie de Landau/RPA : il faut les
fluctuations de paires (Krotscheck, Böhm, Panholzer). Notre apport n'est donc pas de retrouver le mode,
mais de fournir **la référence exacte** dont la mesure s'écarte : S(q, ω) de Landau 2D, sans aucune
approximation numérique, convolué avec la résolution instrumentale, avec l'écart quantifié en σ par q.
Un écart certifié est plus informatif qu'un accord approché ; c'est ce qu'un expérimentateur peut
utiliser, et c'est la première chose à lui montrer.

## 4. Ce que chacun y trouve

- **Villani** : le critère de Penrose et la relation de dispersion formalisés dans le seul cas où c'est
  algébrique, sur une équation physique réelle ; un solveur validé contre des racines certifiées pour
  explorer numériquement l'amortissement non linéaire hors du régime « fond petit » du théorème.
- **Godfrin** : un modèle nul exact de son zéro 2D à ses pressions, avec résolution instrumentale, et la
  liste certifiée des seuils q_c ; plus la confirmation déjà acquise de son Éq. (22) (PRB 2021).
- **Le point commun** : l'objet est un seul, l'équation de Landau–Vlasov, et les deux lectures — théorème
  d'un côté, spectre de l'autre — sont reliées par un calcul sans approximation.

## 5. Ce que cela ne fait pas, et critères d'arrêt

- Aucune nouvelle physique n'est promise. V1 et V2 sont de la physique de manuel rendue exacte ; V4 est
  un modèle nul. Le seul élément potentiellement nouveau (V3, non linéaire) est une question, pas un résultat.
- Rien sur les fluctuations de paires ni sur le mode roton lui-même : hors de portée d'un traitement exact.
- **Portes avant tout code** : (1) recherche d'antériorité — Penrose/Pomeranchuk en 2D a-t-il déjà été
  formalisé ou traité comme tel ? amortissement non linéaire en liquide de Fermi (Bedrossian a-t-il des
  fonds Fermi-Dirac ?) ; (2) sources fixées pour F₀ˢ, F₁ˢ, m* du ³He 2D par densité ; (3)
  pré-enregistrement commité avant le premier nombre, cette fois sans exception.
- **Arrêt** si : la porte (1) montre que V1 est fait ; les paramètres de Landau 2D ne sont pas
  disponibles avec incertitudes ; le solveur ne reproduit pas la racine certifiée à 1 %.

## 6. Première étape concrète (une semaine)

Portes (1)–(2), puis V1 « Pomeranchuk = Penrose » en Lean et V2 pour une seule pression. Si V1 passe
Comparator et V2 donne une boule certifiée, on a de quoi écrire une page à chacun — après levée du hold,
et sur décision du propriétaire.
