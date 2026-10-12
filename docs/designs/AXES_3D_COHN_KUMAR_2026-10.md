# Axes de recherche pour le cas tridimensionnel (Cohn–Kumar, optimalité universelle) : dimensions supérieures, holographie, projection, T-dualité

Mémo du 2026-10-12, X. Callens avec assistance IA (Claude). Statut : réflexion et propositions, avec un test numérique
exécuté aujourd'hui (§2.2) et les résultats du tour 3D n°1 (`exploration/exciton/three_d/`, commit e528c18). Règles de la
série : rien n'est affirmé au-delà de ce qui est calculé ou cité ; les références marquées « (mémoire) » n'ont pas été relues
dans cette session et doivent être vérifiées avant toute citation dans un article.

## 0. Le cadrage qui change la question

**En dimension 3, l'optimalité universelle est fausse pour toute configuration.** Pour le noyau gaussien e^{-α r²} à densité 1,
la sommation de Poisson donne θ_L(α) = α^{-3/2} π^{3/2} θ_{L*}(π²/α) (réseaux unimodulaires), et le dual de FCC est BCC.
Au point auto-dual α = π les deux énergies sont donc **exactement** égales (vérifié aujourd'hui à 1e-16 ; notre expérience A
retrouve a* = π à 3e-14), BCC gagne pour α < π et FCC pour α > π. Aucune configuration ne peut minimiser pour tout α : la
conjecture de Cohn–Kumar n'a pas d'énoncé « à résoudre » en 3D. Cohn–Kumar 2007 le disent déjà (mémoire). Les questions
ouvertes en 3D sont donc autres :

* **Q1 (conjecture du modèle de cœur gaussien en 3D)** : parmi *toutes* les configurations périodiques de densité 1, BCC
  minimise pour α < π et FCC pour α > π. Ouvert. Nos tests A/B (réseaux, puis cellules jusqu'à N = 16) n'ont rien trouvé en
  dessous, ce qui n'est qu'une absence de contre-exemple.
* **Q2 (cristallisation)** : montrer qu'un minimiseur est périodique. Résultats 3D connus seulement pour des potentiels proches
  des sphères dures avec termes angulaires (Flatley–Theil 2015, FCC/HCP ; mémoire).
* **Q3 (noyaux CM non gaussiens)** : par Bernstein, f(r²) = ∫ e^{-α r²} dμ(α). Si μ charge les deux côtés de π, les deux
  phases sont en compétition et **rien n'exclut qu'une structure non-Bravais gagne au point d'équilibre**. Nos expériences A/B
  n'ont testé que des noyaux purs (gaussien, Yukawa, Riesz). C'est le trou le plus simple à combler (§4, test T2).

Tout ce qui suit est lu à travers ce cadrage : « s'inspirer de 8D/24D » veut dire *importer les mécanismes de preuve*
(auto-dualité, interpolation de Fourier, bornes LP/SDP), pas *importer la réponse*.

## 1. Ce qui ne marche pas, et pourquoi (acquis des tours IV et 3D n°1)

| Idée | Forme testable qu'on lui a donnée | Résultat | Où |
|---|---|---|---|
| « Lever en dimension plus haute puis projeter » | recuit dimensionnel E1 (8 formes × 2 noyaux) | aucun gain à calcul égal, 6–17× plus cher | article IV |
| « Frontières = D-branes mobiles » | murs coulissants E2 puis L3 (Fenris) | −2 défauts sur 1/6 puis 0/6 formes | IV, L3_RESULTS |
| « Courbure (S³ → R³, Frank–Kasper) » | A15, C15 dans la recherche B | jamais sous min(FCC, BCC) pour les noyaux CM mono-espèce | three_d/AB |
| « Le 3D est dur » | 600-cell sur S³ (optimum **prouvé**) comme contrôle | retrouvé 46–50/50 pour Coulomb, log, gauss 0,5 ; 0/50 pour gauss 2, 6/50 pour gauss 4 ; gauss 1 non concluant (plafond d'itérations) | three_d/C |
| « Noyau CM comme mailleur 3D » | E3 puis hybride D | ≤ CVT à coût égal | IV, three_d/D |

Leçon stable : **la difficulté en 3D n'est pas la dimension, ce sont les minima locaux** — l'optimiseur échoue même là où
l'optimum est connu et prouvé (S³, gauss 2). Toute proposition sérieuse doit être jugée d'abord sur ce contrôle.

## 2. Axe T-dualité : la dualité de Poisson et la dualité formelle

### 2.1 Le contenu mathématique exact de l'analogie
En théorie des cordes, la T-dualité R ↔ 1/R est la symétrie du réseau de Narain (pair, unimodulaire, signature (d, d)) ; sur
un réseau euclidien elle devient L ↔ L* avec la sommation de Poisson. Les trois cas où l'optimalité universelle est connue ou
conjecturée (A₂ à similitude près, E₈, Λ₂₄) sont **auto-duaux** : le minimiseur est un point fixe de la dualité. En 3D le
point fixe de la dualité est ailleurs que le minimiseur : FCC et BCC sont échangés. La bonne question n'est donc pas « où est
le point auto-dual » mais « que vaut l'énergie *au* point auto-dual, et le réseau auto-dual y est-il bon ? ».

### 2.2 Test exécuté aujourd'hui (chemin de Bain, α = π)
Famille tétragonale centrée bct(t), c/a = t, densité 1 : t = 1 est BCC, t = √2 est FCC, et le dual de bct(t) est similaire
à bct(√2/t). Le point fixe t = 2^{1/4} est le réseau **isodual** de Conway–Sloane (« mean-centred cuboidal », le plus dense des
réseaux isoduaux de R³ ; mémoire, à vérifier). Calcul direct (`/mnt/data/xdev-cache/tmp/bain.py`, somme exacte à 1e-30) :

| α | E(BCC) | E(FCC) | E(isodual t = 2^{1/4}) | argmin sur le chemin | argmax |
|---|---|---|---|---|---|
| π | 0,231536266184 | 0,231536266184 | 0,231925337063 | t = √2 (= t = 1) | **t = 2^{1/4}** |
| 2,5 | 0,526007 | 0,527283 | 0,527031 | BCC | 1,32 |
| 4 | 0,078896 | 0,077968 | 0,078697 | FCC | 1,06 |

Symétrie t ↔ √2/t vérifiée à 1e-16. **Au point auto-dual, le réseau auto-dual est le maximum du chemin, pas le minimum.**
En 3D la symétrie de dualité est « spontanément brisée » : deux minima dégénérés échangés par la dualité, et le point
symétrique est instable. C'est l'inverse de 8D/24D. Conséquence : la T-dualité ne désigne pas de candidat en 3D ; elle
explique pourquoi il n'y en a pas d'universel.

### 2.3 Ce qui reste à faire sur cet axe (et qui est neuf pour nous)
* **T1 — dualité formelle au point auto-dual.** Cohn–Kumar–Schürmann (PRE 2009) et Cohn–Kumar–Reiher (2014) définissent
  des paires *formellement duales* de configurations périodiques non-réseaux (mémoire). Chercher, pour N ≤ 16 points par
  cellule, des configurations formellement auto-duales de R³ et comparer leur énergie à FCC/BCC exactement en α = π, où ces
  deux-là sont dégénérés. Un gain > 1e-8 relatif, revérifié indépendamment, serait une découverte ; l'attente est négative.
* **T2 — mélanges de deux gaussiennes de part et d'autre de π** (Q3 ci-dessus) : f = e^{-a₁ r²} + λ e^{-a₂ r²}, a₁ < π < a₂,
  balayer λ autour de l'équilibre FCC = BCC, recherche B (cellules N ≤ 16). Même critère.
* **T3 — limite α → 0 comme « empilement dual ».** Pour les réseaux, Poisson ramène α → 0 à la densité du dual, donc à
  Gauss 1831 (FCC dual ⇒ BCC) : c'est **démontrable aujourd'hui pour les réseaux** (lemme court, formalisable en Lean). Pour
  les configurations générales la limite α → 0 est le problème « stealthy » (facteur de structure nul sur la plus grande boule
  possible, Torquato–Stillinger, mémoire) ; aucun théorème, mais un énoncé précis à proposer.
* **Ce qui n'apporte rien** : la moyenne sur l'espace de Narain (Siegel–Weil, « holographie moyennée », Afkhami-Jeddi–Cotler–
  Hartman–Maloney 2020, mémoire) donne la *moyenne* de θ sur les réseaux unimodulaires (théorème de la valeur moyenne de
  Siegel : (π/α)^{3/2}, l'énergie du gaz de Poisson), jamais le minimum. À écarter explicitement.

## 3. Axe holographie : interpolation de Fourier et bornes LP/SDP

### 3.1 En quoi la preuve 8D/24D est « holographique »
Cohn–Kumar–Miller–Radchenko–Viazovska (2022) construisent la fonction magique par une **formule d'interpolation** : une
fonction radiale de Schwartz est entièrement déterminée par (f, f', f̂, f̂') aux rayons √(2n). Les « données au bord » (une
suite de nombres) reconstruisent la fonction (le « volume »). Le mécanisme vient des formes modulaires de niveau 1 attachées
aux réseaux pairs unimodulaires.

### 3.2 La question précise en 3D (non vérifiée dans la littérature)
Une fonction radiale de R³ correspond à une fonction **impaire** de la droite (r f(r) ↔ transformée en sinus). Les nœuds √n de
Radchenko–Viazovska (2019) correspondent aux normes de Z³, qui est auto-dual mais mauvais. **Existe-t-il une formule
d'interpolation de Fourier radiale en dimension 3 dont les nœuds de f sont les normes de FCC et ceux de f̂ les normes de BCC ?**
Les séries thêta de D₃ et D₃* sont des formes modulaires de poids 3/2 pour des sous-groupes de congruence de niveau 4 ou 8,
le cadre des généralisations de Bondarenko–Radchenko–Seip (mémoire). Si une telle formule existe, elle ne peut pas prouver
une optimalité universelle (fausse), mais elle pourrait **certifier FCC à un α donné** par la méthode LP. Question pour un
mathématicien du domaine (D. Radchenko, H. Cohn, L. Bétermin), pas pour nous.

### 3.3 Ce que nous pouvons calculer : l'écart LP en 3D
* **H1 — borne LP à deux points** (Cohn–Kumar) pour le gaussien en d = 3 à α ∈ {2, π, 4, 8}, ansatz polynôme × gaussienne
  comme Cohn–Elkies, solveur convexe. Rapporter l'écart relatif à min(FCC, BCC). Critère : écart < 1e-6 à un α ⇒ la méthode
  LP a une chance en 3D à cet α ; écart > 1e-3 ⇒ les méthodes à deux points sont mortes pour Q1. Attente : écart non nul
  (la borne LP de Cohn–Elkies pour l'empilement 3D n'est pas atteinte : ≈ 0,779 contre 0,7405 ; mémoire).
* **H2 — bornes à trois points (SDP)** (Cohn–de Laat–Salmon 2022, mémoire) si H1 laisse un espoir. Coûteux.

## 4. Axe dimensions supérieures → 3D : sections, laminations, projections

* Le relèvement d'un réseau est vacueux (énergie = fonction de la matrice de Gram). Mais les **sections** et **laminations** ne
  le sont pas : FCC = Λ₃ = A₃ = D₃ est une section de E₈ et de Λ₂₄ ; FCC/HCP sont deux empilements de Barlow. La réduction
  de dimension pour fonctions thêta (Bétermin–Petrache, J. Math. Phys. 2017, mémoire) est la version rigoureuse de « empiler
  des couches 2D optimales ». Le théorème 2D de Montgomery donne la couche ; le 3D se joue sur l'empilement, et c'est là que
  FCC/HCP se séparent à 1e-5 relatif (notre scan HCP/DHCP : jamais sous FCC/BCC de plus de 1e-9).
* **P1 — quasicristaux par coupe-et-projection** (Z⁶/D₆ → icosaédrique), approximants périodiques 1/1, 2/1, 3/2 à densité 1,
  énergie gaussienne autour de α = π où FCC/BCC sont dégénérés. C'est la seule forme falsifiable de « projeter depuis plus
  haut » pour des *particules*. Attente négative (les noyaux CM favorisent les réseaux), coût 2 jours, outillage disponible
  (coupe-et-projection, voir arXiv:2603.14590 pour la méthode).
* **P2 — sections 3D de E₈** engendrées par des triplets de racines, mises à densité 1 : toutes au-dessus de FCC/BCC ?
  Faible valeur (FCC en est une) ; à ne faire que si P1 surprend.

## 5. Axe « frustration » : l'obstacle réel et un banc d'essai qui a une réponse connue

* **F1 — homotopie en α** (pas en dimension) : partir de α petit (paysage presque convexe : l'énergie tend vers une forme
  quadratique du facteur de structure) et suivre le minimiseur jusqu'à l'α cible. Contrôle : S³, N = 120, gauss 2 et gauss 4,
  où l'optimum est prouvé (600-cell) et où l'optimiseur local échoue aujourd'hui (0/50 et 6/50). Critère : ≥ 45/50.
  Second contrôle : N = 24 sur S³, où le 24-cell **n'est pas** universellement optimal (Cohn–Conway–Elkies–Kumar 2007 ;
  mémoire, à relire) — un bon optimiseur doit battre le 24-cell pour les potentiels concernés. Coût : 1 jour. C'est le
  préalable à tout le reste : sans optimiseur fiable, T1/T2/P1 ne prouvent rien.
* **F2 — sauts informés par la dualité** (basin hopping dont les mouvements sont des remplacements locaux FCC ↔ BCC le long du
  chemin de Bain) : à ne faire qu'après F1.

## 6. Axe théorique à notre portée : optimalité locale certifiée

Sarnak–Strömbergsson (2006) prouvent que D₄, E₈, Λ₂₄ sont des minima locaux stricts de θ parmi les réseaux pour tout α ;
Joharian–Vallentin–Zimmermann (arXiv:2503.22895, lu aujourd'hui en partie : résumé et introduction) étendent l'analyse
locale aux réseaux modulaires via la hessienne exprimée en formes modulaires. En 3D l'énoncé analogue est nécessairement
**par morceaux** : « FCC est un minimum local strict de θ parmi les réseaux de densité 1 pour tout α > π, BCC pour tout
α < π ». Bétermin a des résultats d'optimalité locale des réseaux cubiques (Anal. Math. Phys. 2019, mémoire) ; l'énoncé
complet sur toute la demi-droite, **avec une preuve assistée par ordinateur (arithmétique d'intervalles sur la hessienne)
et vérifiée en Lean**, n'existe pas à notre connaissance (à vérifier). C'est l'axe où notre outillage (Lean, grand livre,
vérificateurs) est un avantage réel, et il ne dépend pas du théorème planaire non arbitré. Première brique : T3 (limite
α → 0 pour les réseaux via Gauss 1831), formalisable en quelques centaines de lignes.

## 7. Classement et décisions

| Priorité | Test | Coût | Issue attendue | Ce qu'on apprend si l'attente est démentie |
|---|---|---|---|---|
| 1 | F1 homotopie en α sur S³ (contrôle prouvé) | 1 j | ≥ 45/50 atteignable | si non : notre outillage ne peut rien dire du 3D, arrêter les recherches de structures |
| 2 | T2 mélanges de gaussiennes autour de π ; T1 auto-dualité formelle | 2–3 j | rien sous FCC/BCC | une structure non-Bravais pour un noyau CM : vrai résultat (à revérifier deux fois) |
| 3 | H1 écart LP en d = 3 | 3 j | écart ≫ 1e-6 | si petit : la méthode 8D/24D a une chance en 3D à α fixé ; transmettre à un spécialiste |
| 4 | P1 quasicristaux approximants | 2 j | au-dessus de FCC/BCC | sinon : première structure apériodique gagnante pour un noyau CM |
| 5 | T3 + §6 : lemme α → 0 (réseaux) en Lean, puis hessienne certifiée | semaines | faisable | — (c'est un livrable, pas un pari) |
| — | §3.2 interpolation de Fourier FCC/BCC | — | question ouverte | à poser à un mathématicien, avec le mémo |

Décisions demandées : (1) valider l'ordre 1 → 2 → 3 ; (2) autoriser que §6 devienne le lot Lean principal du trimestre à la
place du relèvement (clos négativement) ; (3) choisir à qui poser la question §3.2 (proposition : D. Radchenko ou
L. Bétermin, avec la note sur le noyau gated en pièce jointe, après relecture humaine).

## Annexe : rerun gauss1 (S³, N = 120), résolu
Plafond relevé à 150 000 (`three_d/C/polish_gauss1.py`) : les 50 départs convergent entre 1,5e-8 et 2,1e-8 relatif
au-dessus de E₆₀₀ ; les coordonnées de deux départs (`polish_gauss1_coords.py`) montrent une corde minimale de 0,50 contre
0,618 pour le 600-cell et un écart de spectre de distances de 0,22 : **ce sont de vrais minima locaux distincts**, pas le
600-cell mal convergé. gauss 1 passe de « non concluant » à « échec de recherche », avec un paysage si plat que les
meilleurs minima locaux sont à 2e-8 de l'optimum prouvé. Cela renforce la priorité 1 (homotopie en α avec contrôle prouvé).

## Compléments après lecture des sources (2026-10-12, après-midi)

Trois articles lus en entier ou en grande partie dans la session (textes arXiv) ; ils corrigent ou précisent le mémo.

* **Cohn–Kumar–Schürmann, « Ground states and formal duality relations in the Gaussian core model », arXiv:0911.2169 (2009-2010),
  lu en entier.** (i) Définition exacte de la dualité formelle : P (densité δ) et Q (densité 1/δ) sont formellement duaux si,
  pour toute fonction de Schwartz f, la *somme de paires moyenne* de f sur P vaut δ fois celle de f̂ sur Q ; la version radiale
  (seule utile ici) ne dépend que des corrélations de paires. (ii) **Proposition 1 : D_n^+ est formellement auto-dual pour n
  impair** ; en n = 3, D_3^+ = D_3 ∪ (D_3 + (½,½,½)) est la structure diamant. Il existe donc déjà une configuration non-réseau
  formellement auto-duale de R³, et notre recherche B l'a déjà classée : jamais sous FCC/BCC (elle est bien moins dense). Elle
  sert de **contrôle positif** au détecteur d'auto-dualité de T1. (iii) **Au point auto-dual ρ = 1 le fondamental 3D n'est pas un
  réseau pur mais une coexistence de phases D_3/D_3*** (construction de Maxwell, 0.99899854 ≤ ρ ≤ 1.00100312) ; énergie
  0.11576766 (leur normalisation ½ Σ V, V = e^{-π r²}), soit θ = 0.2315353 contre 0.2315363 pour le réseau pur : **4e-6 relatif
  sous FCC/BCC**, bien au-dessus du seuil 1e-8 de T2. Conséquence pour T2 : un approximant périodique de coexistence à grand N
  passerait la porte sans être une structure nouvelle ; le critère T2 doit vérifier la convexité de E(1/ρ) et exclure les
  approximants de coexistence. (iv) « Aucune preuve n'est connue » pour le fondamental 3D (Q1 confirmée ouverte) ; D_4
  probablement universellement optimal ; D_9^+ peut-être.
* **Cohn–Kumar, « Counterintuitive ground states in soft-core models », arXiv:0811.1236 (Phys. Rev. E 78, 061113, 2008), lu en
  entier.** En R³ tous les empilements « tight » sont des empilements de Barlow (couches triangulaires) et FCC minimise l'énergie
  parmi eux à basse densité ; en d = 5 et 7 des non-Bravais (Λ₅², Λ₇³) battent les réseaux. Cela borne l'axe « sections et
  laminations » (§4) : en 3D la lamination ne produit que Barlow, question close pour le gaussien à basse densité.
* **Cohn–Conway–Elkies–Kumar, « The D₄ root system is not universally optimal », Exp. Math. 16 (2007) 313–320, arXiv:math/0607447,
  lu en entier.** Confirmé : le 24-cell n'est pas universellement optimal sur S³ ; la famille C_θ le bat pour f = (1+t)^k,
  8 ≤ k ≤ 13 (et e^{6t}) ; pour f = (1−t)^{-1} les simulations convergent dans plus de 90 % des cas vers C_θ (668.19 contre 668) et
  non vers le 24-cell. **Notre expérience C retrouve ce comportement** (Coulomb : 5/50 au 24-cell, log : 6/50) avec un autre
  potentiel ; c'est un contrôle de plus pour F1. Les 24-cell est néanmoins un minimum local strict pour tout potentiel absolument
  monotone non polynomial de degré ≤ 5 (leur §6).
* **Radchenko–Viazovska, « Fourier interpolation on the real line », arXiv:1701.00265** : titre et résumé vérifiés (nœuds
  {0, ±√n}, formes faiblement holomorphes pour le groupe thêta) ; le reste du mémo §3.2 reste une question, non une affirmation.
* Les références encore « (mémoire) » : Conway–Sloane isodual (1994), Flatley–Theil (2015), Bétermin–Petrache (2017),
  Sarnak–Strömbergsson (2006), Bondarenko–Radchenko–Seip, Cohn–de Laat–Salmon (2022), Afkhami-Jeddi et al. (2020).
