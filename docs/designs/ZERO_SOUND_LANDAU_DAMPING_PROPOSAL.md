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

---

# Extension (2026-09-22) : boucle complète Théorie → Topologie → Physique → Expérience → Solveur → TDA → Théorie, Lean 4 en clé de voûte

Faits vérifiés avant d'écrire (pas de mémoire) : dépôt Bedrossian `Jacob24876/LandauDamping-Public`,
Lean **v4.29.1**, dépendance `AnalysisBase-Public`, « no sorry, no custom axioms », README : « the public
assembly results include hypotheses and some parameter restrictions beyond the source theorem ». Crates
Rust : `sundials-sys` 0.6.2 (bindings SUNDIALS : CVODE, ARKODE, IDA), `sundials` 0.4.1 (wrapper sûr),
`diffsol` 0.16.2 (ODE/DAE pur Rust, 100 k téléchargements). **Aucune crate « runux » ni
« rusty-sundials » n'existe sur crates.io** ; je suppose que « rusty sundials » désigne `sundials`/`sundials-sys`
et je ne devine pas ce que « runux » désigne — à préciser.

## 7. Étendre et formaliser les travaux de Villani en Lean 4, sur les épaules des grands projets IA

Trois codes sources, trois toolchains, trois usages différents :

| Source | Toolchain | Ce qu'on en prend | Comment |
|---|---|---|---|
| **Bedrossian, LandauDamping** (2026) | 4.29.1 (+ AnalysisBase) | normes de Gevrey sur l'espace des phases, bornes d'écho résonant et de Schur, résolvante de Volterra, scattering vers le transport libre | *construire dessus* : nos énoncés 2D Fermi doivent être formulés dans SES définitions (fond, normes, mode k) pour que « Penrose = Pomeranchuk » s'assemble avec son théorème. Coût : migration 4.29 → 4.34 ou pin de notre module à 4.29 ; à mesurer avant tout |
| **OpenAI NavierStokesAndEuler** | 4.34.0-rc2 (dépendance déjà en place) | vocabulaire tore/dérivées/Sobolev | inchangé (`MadelungNSE`) |
| **Anthropic FLT** | 4.33.1 | inversion de Fourier sur le tore à n dimensions, borne sup Sobolev sur un cube | port (deux fichiers, ~500 lignes), pour passer des modes de Fourier au champ δn(x, θ) |

**Mise à jour (2026-09-22).** Une revue séparée et plus large de tous les travaux de Villani 2025–2026
et de ses cours librement accessibles (13 PDF, dont ses deux articles seuls-auteur de 2025/2026 et
Mouhot–Villani, hypocoercivité, Lott–Villani) a été faite pour répondre à la demande explicite d'une
formalisation-hommage. Elle a identifié `lean_src/Villani.lean` comme cible **réalisée cette session**,
au lieu de l'item 1 ci-dessous, pour deux raisons : (a) l'item 1 exige d'abord de porter nos définitions
dans le cadre exact de Bedrossian (fond, normes de Gevrey) — un préalable non mesuré ; (b) la revue a
trouvé un résultat **co-écrit par Villani lui-même**, auto-contenu, sans dette envers Mathlib manquant :
Ollivier–Villani, *A curved Brunn–Minkowski inequality on the discrete hypercube*, arXiv:1011.4779,
Théorème 1 au cas K=0 — `#A·#B ≤ (#M)²` pour l'ensemble des points milieux M de A,B dans le cube de
Hamming, prouvé intégralement (injection A×B ↪ M×M par codage de « crossover », sans `sorry`) — plus un
corollaire de trois lignes de la propre inégalité de traitement des données de Mathlib
(`klDiv_comp_right_le`), squelette discret des méthodes d'entropie que Villani passe en revue dans
*H-theorem and beyond*. Le Théorème 1 complet (terme de courbure K=1/(2N)) reste un item ouvert : il
exige la concentration de mesure dans le groupe symétrique (Lemme 4 et Proposition 5 de l'article),
non tentée. Les items 1 à 4 ci-dessous restent le programme pour la suite du volet Landau damping/Fermi
liquide proprement dit.

**Cibles, par ordre de faisabilité, chacune avec ce qui manque à Bedrossian selon son propre README :**

1. **Critère de Penrose et relation de dispersion, cas algébrique 2D Fermi** (V1 ci-dessus). Absent de sa
   formalisation (« fond petit », pas de Laplace). Le cas 2D évite l'analyse complexe : c'est le *seul*
   endroit où l'on peut fermer ce trou aujourd'hui. Nouveau et modeste.
2. **Fond de Fermi–Dirac au lieu du fond « petit ».** Son théorème est énoncé pour un fond de faible
   amplitude ; le fond physique (Fermi–Dirac à T > 0, analytique) ne l'est pas. Première marche :
   prouver que le fond de Fermi–Dirac satisfait ses hypothèses de régularité Gevrey (c'est un calcul de
   normes, pas un théorème nouveau) ; seconde marche : le cas F₀ˢ petit mais fond d'amplitude 1, qui est
   exactement le régime « liquide de Fermi faiblement interagissant ». Kill : si ses hypothèses encodent
   « petit » de façon inséparable de la régularité, le dire.
3. **Échos non linéaires de son zéro** : ses bornes d'écho (Schur) instanciées avec F(θ−θ′) à la place
   du noyau de Poisson — une *application* de ses lemmes, pas un théorème nouveau ; c'est ce qui borne
   V3 rigoureusement.
4. **Plus loin, hors de portée immédiate, dit tel quel** : hypocoercivité (Villani, Memoirs AMS 2009) —
   Mathlib n'a ni Fokker–Planck ni les espaces fonctionnels ; théorème H de Boltzmann — pas d'entropie
   cinétique dans Mathlib ; transport optimal/Wasserstein — programme de plusieurs années. À ne pas
   promettre.

Porte avant tout : recherche d'antériorité sur (1) et (2), et construction de son dépôt en local pour
lire les énoncés réels (le README prévient que la portée est restreinte).

## 8. Solveur certifié et optimisé : Python de référence, Rust de production, SUNDIALS pour le raide

Trois niveaux, chacun validé contre le précédent et contre la racine certifiée Arb :

| Niveau | Rôle | Validation |
|---|---|---|
| **Python** (`vlasov.py` étendu à δn(x, θ)) | référence lisible, 1 page | racine certifiée à 1 % ; écho/récurrence champ coupé exacts |
| **Rust** (crate `qf-kinetic`) : transport en Fourier (`rustfft`), semi-lagrangien angulaire, parallélisme `rayon`, FFI vers Python (`pyo3`) | production : x-θ à 512×1024 en minutes, balayage des pressions et des paramètres de Landau | bit-à-bit égal à Python sur les cas de test aux erreurs d'arrondi près ; mêmes contrôles |
| **SUNDIALS via `sundials-sys`/`sundials`** : CVODE (BDF) pour la variante *avec* collisions (Landau–Boltzmann linéarisé, raide : temps de relaxation τ ∝ T⁻²), ARKODE (IMEX) pour transport + collisions | c'est le passage Vlasov → cinétique complète, indispensable pour comparer aux mesures à T > 0 (largeur collisionnelle ∝ T²) | limite sans collisions → niveau Rust ; solution de Chapman–Enskog en limite hydrodynamique (premier son, réponse connue) |

« Certifié » a un sens précis et limité ici : (a) les racines et seuils sont des enclos Arb, prouvés ;
(b) les schémas sont validés contre ces enclos et contre des formules fermées ; (c) les propriétés
structurelles du schéma (conservation discrète de la masse, antisymétrie du transport en Fourier) sont
des énoncés candidats pour Lean sur le schéma *discret* (finis, décidables) — pas une preuve du code
Rust. Ne pas écrire « solveur prouvé ».

`diffsol` (pur Rust, DAE) est l'alternative si les bindings SUNDIALS posent problème à la compilation.

## 9. Topologie et TDA : fermer la boucle, avec le bilan honnête

Bilan : cinq propositions TDA, cinq réfutées ; mécanisme identifié pour les deux dernières
(persistance = profondeur jusqu'au col de connexion). Le TDA ne revient donc **qu'en instrument à
réponse connue**, et chaque usage ci-dessous nomme sa réponse connue et son contrôle.

| Maillon | Usage TDA (GUDHI) | Réponse connue / contrôle | Retour vers la théorie (Lean) |
|---|---|---|---|
| **Solveur → TDA** : filamentation sur le cercle de Fermi | persistance H₀ des sous-niveaux de δn(x₀, θ, t) (complexe cubique périodique en θ) ; nombre de barres = nombre de filaments | transport libre : δn = cos(kθ·… − kv_F t cos θ) a un nombre de barres calculable exactement à chaque t ; le solveur doit le reproduire *champ coupé* | **`persistence_cos` en Lean** : la persistance H₀ de θ ↦ cos(nθ) sur S¹ est exactement n barres de longueur 2 (énoncé fini, décidable via l'elder rule sur un graphe cycle) — le premier théorème TDA du dépôt qui ne soit pas un simple lemme de 1-squelette |
| **TDA → Théorie** : dualité | contrôle D0 (déjà exact sur données GP) | théorème de symétrie CSEH 2009 | **`symmetry_1d` en Lean** : version discrète 1D du théorème de symétrie (H₀ de f vs H₀ de −f sur un cycle) — clé de voûte : ce que GUDHI calcule est ce que Lean prouve |
| **Physique → TDA** : entrée dans le continuum | diagramme H₀ de la *relation de dispersion* Im D(s, q) : le bar né en q_c est le seuil | q_c certifié par Arb (V2) ; la barre doit naître à q_c ± l'enclos | rien à prouver : c'est un test que le pipeline lit bien un seuil certifié |
| **Expérience → TDA** | proéminence des pics de S(q, ω) mesuré vs modèle nul (V4) | déjà fait pour ε(k) : 0,4501 = 0,4501 meV (c'est la proéminence, et on le dit) | — |

Ce que la boucle **ne** fait pas : découvrir une structure. Chaque flèche transporte une quantité dont
la valeur est connue à l'avance par au moins un autre maillon ; la boucle est fermée quand chaque
maillon rend la même valeur, et Lean est la clé de voûte parce que c'est le seul maillon dont la sortie
ne peut pas être ajustée.

## 10. Plan et workflow (pour approbation)

Sept agents maximum, portes dures, tout pré-enregistré et commité avant le premier nombre.

| Phase | Agents | Livrable | Porte |
|---|---|---|---|
| 0. Antériorité | 2 (Lean/Villani ; solveur/TDA) | mémo : (1) et (2) de §7 sont-ils faits ? paramètres de Landau 2D sourcés ? | tout item déjà fait est rayé |
| 1. Pré-enregistrement | — (moi, revu par le propriétaire) | critères, tolérances, contrôles négatifs, réponses connues | commit horodaté |
| 2. Lean noyau | 1 | `zero_sound_F1`, `pomeranchuk_penrose`, `persistence_cos`, `symmetry_1d` ; Comparator | contrôles négatifs échouent |
| 3. Enclos certifiés | 1 | Arb : racines, q_c, Γ(q) par pression | boule décalée rejetée |
| 4. Solveurs | 2 (Python+Rust ; SUNDIALS) | δn(x,θ,t) validé ; variante collisionnelle | racine certifiée à 1 % ; échos champ coupé exacts |
| 5. TDA | 1 | filamentation vs transport libre ; D0 ; q_c lu | réponses connues reproduites |
| 6. Modèle nul vs expérience | 1 | S(q,ω) Landau 2D convolué IN5, écart en σ par q | — (résultat, quel qu'il soit) |
| 7. Revue adverse | 1, contexte vierge | « qu'objecterait un cinéticien / un neutronicien en dix minutes » | décision du propriétaire sur tout contact |

Dépôt cible : **ce dépôt** pour Lean, Arb, Python et TDA (registre, Comparator, tests déjà là) ;
**Physique-Cinétique** reçoit le solveur Rust/SUNDIALS et devient le dépôt « cinétique haute
performance », relié à celui-ci par une dépendance déclarée — pas par copie. Première PR là-bas : ce
plan, la CI déplacée à la racine, LICENSE laissée au propriétaire.

---

## 11. Résultat de la porte d'antériorité (§5) pour V1 et V2 — 2026-09-22, avant tout code

Recherche faite avant d'écrire une seule ligne de Lean ou d'Arb, comme prévu au §5. Résultat : **arrêt**,
sur les propres critères d'arrêt du §5.

### V1 (« Pomeranchuk = Penrose ») — NE PAS TENTER tel que formulé

Le critère de Pomeranchuk `F₀ˢ > −1` est standard et bien sourcé comme critère **thermodynamique**
(positivité d'une susceptibilité), pas nativement comme critère **dynamique** (absence de racine à
Im ω > 0 de l'équation cinétique linéarisée). L'équivalence entre les deux — ce que V1 devait formaliser —
n'est PAS un théorème nommé et établi dans la littérature pour le cas visé. La référence la plus proche
(Kolomeitsev & Voskresensky, Eur. Phys. J. A 52, 362 (2016), arXiv:1610.09748) fait bien une analyse de
dispersion dynamique et trouve exactement le comportement attendu (mode non amorti pour f₀>0, amorti pour
−1<f₀≤0, croissant pour f₀<−1) — mais pour un système 3D à interaction scalaire différent, jamais nommé
« Penrose », et pas pour le cas 2D visé ici. Formaliser V1 tel qu'énoncé exigerait donc de **refaire cette
analyse en 2D** — un travail de dérivation originale, pas une formalisation d'un résultat existant. C'est
précisément ce que la discipline de ce projet exclut (formaliser l'existant, ne pas produire de nouvelle
physique). **Arrêt, sur le critère « porte (1) » du §5.**

Piste de repli non retenue ici : formaliser seulement le critère thermodynamique nu (`F₀ˢ > −1` comme
définition de la stabilité via une compressibilité) — mais sans la dérivation compressibilité↔F₀ˢ à
disposition et vérifiée, l'énoncé serait quasi définitionnel, sans contenu mathématique réel à prouver.

### V2 (enclos certifiés) — exécutable seulement en partie

- **³He massif (3D)** : valeurs trouvées (F₀ˢ≈9,3, F₁ˢ≈5,4 à SVP ; F₀ˢ≈88–94 près de la fusion, sourcées
  via Greywall 1983, Phys. Rev. B 27, 2747) mais **seulement via des citations secondaires** — la table
  primaire de Greywall est derrière un péage et n'a pas été vérifiée directement. Construire un enclos
  Arb à 40 chiffres sur une entrée physique non vérifiée à la source serait un décalage de rigueur : la
  certification porterait sur le mauvais nombre si la citation secondaire est fautive.
- **Monocouche 2D** (le système mesuré par Godfrin et al., Nature 483, 576, 2012) : **aucune valeur
  numérique de F₀ˢ en fonction de la densité surfacique n'a été trouvée** dans le budget de recherche —
  l'article Nature est verrouillé, et les articles compagnons (Casey, Nyéki, Saunders) n'ont pas livré
  de table exploitable. **Arrêt, sur le critère « paramètres 2D non disponibles » du §5.**

### Décision

Le programme V1/V2 tel que conçu s'arrête ici. Rien n'est implémenté. Pas de contact Godfrin/Villani basé
sur ce volet (le hold en §4 du dossier Godfrin reste de toute façon en vigueur). Reprise possible
seulement si : (a) quelqu'un avec accès institutionnel vérifie la table Greywall et les valeurs 2D de
Casey/Nyéki/Saunders — ce qui débloquerait V2 en 3D et potentiellement en 2D ; (b) une analyse dynamique
2D publiée est trouvée ou faite par quelqu'un d'autre — ce qui reformulerait V1 en formalisation légitime.

---

## 12. Recherche de données élargie — 2026-09-22, second passage, toujours pas de code

Sur demande explicite (« look for more data »), une recherche plus large que la porte du §11 a été
faite. Elle **confirme** le résultat du §11 (V2, branche 2D) plutôt que de le débloquer, et trouve des
pistes concrètes pour la suite.

### He-3 2D — toujours pas de table numérique en accès libre, mais trois pistes nommées

- `arXiv:2206.06039` (Godfrin & Krotscheck, revue) lu directement : confirmé, **aucune table F₀ˢ/F₀ᵃ**,
  juste une phrase qualitative renvoyant à une référence non reproduite.
- Boronat, Casulleras, Grau, Krotscheck, Springer, arXiv:cond-mat/0307493 : donne **m\*/m** en fonction
  de la densité surfacique par QMC (singularité ≈0,048 Å⁻², gel 0,052–0,063 Å⁻²) — utile mais **pas de
  F₀ˢ/F₀ᵃ**.
- Plusieurs articles Casey/Nyéki/Saunders/Hallock donnant F₀ᵃ, F₁ˢ (Ho & Hallock PRL 87, 135301, 2001 ;
  PRB 73, 012507, 2006 ; Casey et al. PRL 90, 115301, 2003) : **payants, aucun miroir arXiv/HAL trouvé**.
- **Piste la plus prometteuse, non exploitée** : Godfrin, Meschke, Lauter, Böhm, Krotscheck, Panholzer,
  *Observation of Zero-Sound at Atomic Wave-Vectors in a Monolayer of Liquid ³He*, J. Low Temp. Phys.
  158, 147 (2010) — même équipe, même substrat (graphite prépollué ⁴He) que l'article Nature 2012 visé
  par ce projet. Vraisemblablement la source réelle du F₀ˢ utilisé pour prédire le son zéro dans CE
  système. Payant chez Springer, pas de PDF ouvert trouvé.
- Deux thèses (Dann 2000, Casey 2001, sur OSTI) dont le résumé mentionne explicitement l'inférence de
  paramètres de Landau — accès OSTI en échec technique cette session, valeurs **non vérifiées**.
- **Mise en garde structurelle, si ces pistes aboutissent** : le système de Casey/Nyéki/Saunders
  (Royal Holloway, substrat bicouche HD) et celui de Godfrin (Grenoble, substrat monocouche ⁴He) sont
  **différents**. Transférer un F₀ᵃ(n) de l'un à l'autre exigerait une justification explicite, pas une
  substitution gratuite.

**Verdict : deuxième résultat nul indépendant — renforce la confiance que le manque est réel, pas un
artefact de budget de recherche.**

### Jeux de données quantiques — HuggingFace essentiellement inutile, Zenodo sans changement

- **HuggingFace : taux de faux positifs proche de 100 %.** « vortex » → 30 résultats, 29 sont des noms de
  modèles/LLM ; le seul jeu de données physique réel est de la CFD classique (cylindre, Re=100), pas
  quantique. « BEC », « helium », « condensate », « superfluid » → collisions d'acronymes/noms, aucun
  résultat pertinent. « quantum fluid », « Gross-Pitaevskii », « cold atom », « Bose-Einstein condensate »,
  « neutron scattering » → **zéro résultat**. HuggingFace n'a rien pour ce domaine.
- **Zenodo** : `PolancoData` (256³, déjà utilisé par ce projet) confirmé toujours seul de son genre.
  **Un nouveau jeu trouvé** : Kwon & Shin (Seoul National University), données et scripts pour
  *Dynamic similarity of vortex shedding in a superfluid flowing past a penetrable obstacle*, Zenodo, mai
  2026, CC-BY-4.0, DOI 10.5281/zenodo.20068724 — observables traités et paramètres de simulation, **pas**
  les champs bruts (explicitement exclus pour l'espace disque). Utile en validation croisée d'observables,
  pas comme nouveau jeu de champs à haute résolution.
- **Deux questions restées sans réponse** (budget de recherche web de la session épuisé, 200/200, avant
  et après une nouvelle tentative) : un jeu de données S(Q,ω) de ⁴He superfluide lisible par machine
  existe-t-il ailleurs que dans les tables ancillaires de Godfrin et al. PRB 103, 104516 (déjà en main) ?
  Une donnée BEC diluée dépassant ξ/Δx = 2,26 est-elle apparue depuis le relevé du 2026-09-20 ? **Non
  vérifié, pas faux — juste pas atteint.**

**Verdict : rien de mieux que ce que le projet a déjà.** `PolancoData` reste la référence ; le nouveau
jeu Kwon & Shin est noté pour une validation future d'observables, pas comme remplacement.
