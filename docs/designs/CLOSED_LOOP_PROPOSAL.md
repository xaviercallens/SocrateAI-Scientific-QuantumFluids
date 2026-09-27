# Proposition : une boucle fermée Lean 4 → Topologie → Dualité → Physique → TDA → Solveur → Simulation → Lean 4, et de nouveaux liens Godfrin ↔ Villani

**Statut : PROPOSITION (2026-09-22). Rien n'est implémenté. Rien n'est promis.** Écrite après la
formalisation `Villani.lean`, l'arrêt de V1/V2 aux portes de littérature (`ZERO_SOUND_LANDAU_DAMPING_PROPOSAL.md`
§11–12) et le bilan TDA du projet : **cinq propositions topologiques, cinq réfutées**. Ce bilan dicte la
règle de ce document : la TDA n'entre dans la boucle que là où **un théorème lui fournit une réponse
connue à l'avance**, et chaque flèche de la boucle transporte une quantité qu'un autre maillon connaît
déjà. La boucle est fermée quand chaque maillon rend la même valeur — jamais quand un maillon « découvre ».

Le budget de recherche web de cette session est épuisé : les références marquées **[à vérifier]** n'ont
pas été confirmées contre Crossref ou la source et doivent l'être en porte 0, avant tout code.

---

## 1. Ce qui relie réellement Godfrin et Villani — une carte, pas une intuition

| Concept chez Villani | Observable chez Godfrin | Pont mathématique exact | État |
|---|---|---|---|
| Amortissement de Landau (Mouhot–Villani) | Son zéro dans le ³He 2D (Nature 2012) et 3D | l'équation cinétique de Landau *est* une équation de Vlasov ; F₀ˢ joue le rôle de 1/k² | `ZeroSound.lean` fait ; V1 2D arrêté (pas de théorème dynamique 2D) ; **V1 3D possible** (§2.1) |
| **Hypocoercivité** (Memoirs AMS 2009) | **croisement son zéro → premier son** dans le ³He massif : vitesse c₀ → c₁ et pic d'atténuation à ωτ ≈ 1 | l'équation cinétique de Landau *avec collisions* relaxe vers l'équilibre local ; l'hypocoercivité est la mathématique de ce taux (∝ T²) | **jamais exploré ici** — le pont le plus solide de cette table (§2.2) |
| Transport optimal, W₁, dualité de Kantorovich | distance de Wasserstein / goulot **entre diagrammes de persistance** — c'est la métrique standard de la TDA | W₁ sur un ensemble fini = programme linéaire ; la dualité de Kantorovich–Rubinstein en certifie la valeur exacte (couplage + fonction 1-lipschitzienne) | c'est le maillon **Dualité** de la boucle (§3) |
| Courbure de Ricci grossière (Ollivier–Villani, §2.1 de l'article déjà formalisé en partie) | — | κ(x,y) = 2/(N+1) sur l'hypercube : valeur exacte, finie, calculable | continuation naturelle de `Villani.lean` (§2.3) |
| Information de Fisher (Villani 2025, Imbert–Silvestre–Villani, Invent. Math. 2025) | l'incertitude statistique des paramètres ajustés sur S(Q,ω) est une information de Fisher au sens statistique | même fonctionnelle I(f) = ∫\|∇log f\|² f pour une famille de translation ; Cramér–Rao | cible Lean réelle (trou Mathlib), pas d'expérience honnête faute de comptages bruts (§2.4) |
| Théorème H, méthodes d'entropie | règles de somme de S(Q,ω) (f-sum, compressibilité) que la théorie dynamique à N corps de Krotscheck–Godfrin satisfait exactement | identités intégrales exactes ; borne variationnelle de Feynman–Bijl ε(k) ≤ ħ²k²/(2m S(k)) | expérience à réponse connue sur les tables de Godfrin **si** un S(k) tabulé existe (§2.5) |
| Fokker–Planck cinétique en géométrie courbe (2026), Lott–Villani–Sturm | — | — | hors de portée, dit tel quel |

Les trois premières lignes forment un tout : Landau, collisions, transport. C'est là que je propose de
concentrer l'effort.

## 2. Directions de recherche, chacune avec sa réponse connue et son critère d'arrêt

### 2.1 V1 recentré sur le 3D : formaliser la classification de stabilité de Kolomeitsev–Voskresensky

La porte de §11 a établi que l'équivalence « Pomeranchuk = Penrose » n'est pas un théorème publié en
2D, mais que Kolomeitsev & Voskresensky (Eur. Phys. J. A 52, 362, 2016) l'**obtiennent par analyse de
dispersion explicite en 3D** pour un paramètre scalaire f₀ : mode non amorti pour f₀ > 0, seulement amorti
pour −1 < f₀ ≤ 0, mode croissant pour f₀ < −1. C'est un résultat existant : le formaliser est dans la
discipline du projet, contrairement au 2D.

- **Lean** : `stability_trichotomy_3d` sur la fonction de Lindhard logarithmique déjà dans `ZeroSound.lean`
  (les racines réelles s > 1 sont faites ; il manque « aucune racine avec Im ω > 0 pour −1 < F < 0 » et
  « une racine croissante pour F < −1 »). Difficulté M : l'analyse complexe de log((s+1)/(s−1)) hors de
  l'axe réel n'est pas dans Mathlib sous forme directement utilisable ; kill si la continuation analytique
  exige plus qu'une demi-journée de lemmes auxiliaires.
- **Porte 0** : relire K–V pour vérifier que leur modèle scalaire *est* l'équation cinétique de Landau à
  F₀ˢ seul (le rapport de porte le dit « fonctionnellement », pas « identiquement ») — sinon, arrêt.
- **Contrôle négatif** : remplacer −1 par −1/2 doit échouer.
- **Ce que Villani y trouve** : Penrose formalisé pour un liquide de Fermi, ce que Bedrossian dit ne pas
  couvrir. **Ce que Godfrin y trouve** : rien directement — c'est le 3D massif.

### 2.2 Le croisement son zéro → premier son : hypocoercivité, solveur BGK, expérience historique

Le pont le plus riche et le moins exploré. Dans le ³He massif, quand ωτ passe de ≫ 1 à ≪ 1 (τ ∝ T⁻²), la
vitesse du son passe de c₀ (son zéro) à c₁ (premier son) et l'atténuation passe par un maximum à ωτ ≈ 1 —
mesuré par Abel, Anderson & Wheatley (PRL 17, 74, 1966) **[à vérifier]**. Deux réponses connues :

- **algébriques** : c₁² = (v_F²/3)(1 + F₀ˢ)(1 + F₁ˢ/3) (limite hydrodynamique, Baym–Pethick) et c₀ > c₁
  (le son zéro est plus rapide que le premier son) ;
- **dynamiques** : la position du maximum d'atténuation, ωτ ≈ 1, et la forme de la courbe c(ωτ).

Le programme :
- **Lean** : `first_sound_sq` (identité algébrique, S) et `zero_sound_faster` : s₀² > (1+F)/3 pour la racine
  s₀ de 1 + F·Ω(s) = 0 (M — trivial pour F < 2 puisque s₀ > 1 ; pour F grand il faut une borne inférieure
  sur s₀ tirée du log ; kill si cette borne demande un développement asymptotique formalisé).
- **Solveur** : V3 de la proposition précédente (δn(x, θ, t) sur le cercle de Fermi, transport de Fourier
  exact + champ moyen de Landau) **plus un terme de collision BGK** −(δn − δn_loc)/τ. C'est exactement le
  système où l'hypocoercivité de Villani s'applique (transport + relaxation dégénérée). Validation à réponse
  connue : à τ → ∞ retrouver c₀ dans l'enclos Arb ; à τ → 0 retrouver c₁ de la formule ; entre les deux,
  le pic d'atténuation à ωτ ≈ 1.
- **Expérience numérique contre l'expérience physique** : superposer c(ωτ) et l'atténuation calculées à la
  courbe d'Abel–Anderson–Wheatley (à numériser depuis la figure, incertitude déclarée). Pré-enregistrer :
  position du pic à ±20 % de ωτ = 1 ; c₀/c₁ à ±5 % de la valeur des paramètres de Landau. Ce sont des
  mesures, pas des prédictions nouvelles — le solveur est l'objet testé.
- **Données** : F₀ˢ, F₁ˢ, m\*, v_F du ³He massif à la pression de la mesure. Greywall 1983 n'est cité
  qu'indirectement (§11) : **c'est la question à ajouter à la demande faite à Godfrin** — il connaît ces
  tables mieux que quiconque, et une confirmation orale vaut la table primaire.
- **Ce que chacun y trouve** : Villani, l'hypocoercivité sur une équation cinétique réelle avec ses
  constantes mesurées ; Godfrin, un solveur validé sur la physique de son laboratoire.
- **Kill** : si la porte 0 ne trouve pas de courbe expérimentale numérisable, on garde Lean + solveur et
  on retire le mot « expérience ».

### 2.3 Continuer `Villani.lean` : la courbure de Ricci grossière de l'hypercube, certifiée

L'article d'Ollivier–Villani calcule au §2.1 (lu dans le PDF, pas de mémoire) W₁(μ_x, μ_y) = 1 − 2/(N+1) pour
x, y voisins, donc κ(x, y) = 2/(N+1). Valeur finie et exacte, dans le même article que le théorème déjà
formalisé — et c'est **la dualité de Kantorovich–Rubinstein en acte** : la borne supérieure est un couplage
explicite (N+1 points, deux restent en place, N−1 bougent de 1), la borne inférieure est une fonction
1-lipschitzienne (la distance à x). Pas besoin de la dualité complète : la direction facile
(∫f dμ − ∫f dν ≤ ∫d dπ pour tout couplage π et toute f 1-lipschitzienne) suffit à **certifier** la valeur.
- **Lean** : `coarseRicci_hypercube_neighbours : κ = 2/(N+1)`, purement fini (S/M). Contrôle négatif :
  2/N doit échouer.
- **Lien TDA réel** : la courbure d'Ollivier–Ricci sur graphes est un outil standard d'analyse de réseaux ;
  il existe un paquet Python (`GraphRicciCurvature`) **[à vérifier]**. Test d'instrument à réponse connue :
  lui faire calculer l'hypercube et comparer à 2/(N+1) certifié — exactement ce que D0 a fait pour la
  dualité cubique. Pas d'application à un graphe physique tant qu'aucune réponse connue n'existe pour lui.

### 2.4 Information de Fisher : tensorisation et Cramér–Rao, en Lean

Continuation tribut depuis le papier le plus récent de Villani. I(f ⊗ g) = I(f) + I(g) (sa Prop. 7.2) et
Var ≥ 1/I sont des trous réels de Mathlib (aucune « FisherInformation » dans le checkout épinglé, vérifié
par grep). Difficulté M (intégration par parties sur ℝᵈ présente). **Pas d'expérience** : la seule
application honnête côté Godfrin exigerait ses comptages bruts. Cible Lean seule, clairement dite telle.

### 2.5 Règles de somme et borne de Feynman–Bijl sur les tables de Godfrin

ε(k) ≤ ħ²k²/(2m S(k)) est une borne variationnelle exacte (Rayleigh–Ritz). Les ancillaires de PRB 103,
104516 donnent ε(k) à sept pressions ; il manque S(k). **Porte 0** : existe-t-il un S(k) tabulé du ⁴He à
SVP (Svensson et al., PRB 21, 3638, 1980 **[à vérifier]**) ? Si oui : test à réponse connue (l'inégalité
doit tenir partout, avec un écart maximal au roton), Lean pour le principe variationnel en dimension finie
(S). Si non : arrêt, comme pour V2.

## 3. La boucle fermée — une seule, exécutable, chaque flèche avec sa réponse connue

```
      Lean 4 ──────────────── Topologie ──────────── Dualité
   (théorèmes finis :        (H₀ des sous-niveaux    (Cohen-Steiner : T ↔ V,
    stabilité, KR facile,     de ρ = |ψ|² ; barres    fait, exact ; Kantorovich–
    κ = 2/(N+1))              = proéminence)          Rubinstein sur diagrammes)
        ▲                                                   │
        │                                                   ▼
   Simulation ◄──────────── Solveur ◄──────────── Physique / Expérience
   (GP 2D à deux            (V3 : Landau cinétique   (ρ(t) ; c₀ → c₁ ; tables
    résolutions ; BGK)       + BGK ; Vlasov validé)   de Godfrin)
        │                                                   ▲
        └──────────────── TDA (GUDHI) ──────────────────────┘
                 (d_B et W₁ entre diagrammes ; stabilité)
```

**Le tour complet, concrètement :**

1. **Simulation** : deux champs ρ₁, ρ₂ = |ψ|² de GP 2D — même état, deux résolutions (ξ/Δx = 4 et 8 ;
   la série de convergence existe déjà), ou deux instants proches.
2. **TDA** : diagrammes H₀ de sous-niveaux (D0 garantit que H₁ superniveau dit la même chose — donc un
   seul diagramme suffit, c'est un résultat de ce projet). GUDHI donne d_B(Dgm ρ₁, Dgm ρ₂) et W₁.
3. **Théorie (réponse connue)** : le théorème de stabilité de Cohen-Steiner–Edelsbrunner–Harer (2007)
   impose d_B ≤ ‖ρ₁ − ρ₂‖∞. **Jamais testé dans ce projet.** C'est un test d'instrument parfait : une
   inégalité qui doit tenir, et dont la marge dit *combien* du diagramme est un artefact de résolution —
   la question exacte qui a tué D1.
4. **Dualité** : la valeur W₁ rendue par GUDHI (un programme linéaire) est **certifiée** par la direction
   facile de Kantorovich–Rubinstein : un couplage explicite (borne sup) et une fonction 1-lipschitzienne
   (borne inf), tous deux vérifiables en Lean sur un diagramme de taille modeste (arithmétique rationnelle,
   `norm_num`/`decide`). Là, Villani (transport optimal) entre dans la TDA par la porte principale, pas
   par analogie.
5. **Lean 4** : `wasserstein_certificate` (couplage + Lipschitz ⇒ encadrement de W₁), `stability_1d` (la
   version finie du théorème de stabilité pour H₀ d'une fonction sur un cycle — énoncé fini, décidable ;
   M/L, c'est la pièce la plus risquée), et les théorèmes de §2.
6. **Retour à la physique** : la marge d_B/‖Δρ‖∞ à deux résolutions devient un critère *quantitatif* de
   résolution pour toute future détection de vortex par densité — ce que D1 n'avait pas. Puis le solveur
   BGK (§2.2) reprend la boucle du côté ³He.

**Ce que la boucle ne fait pas** : découvrir une structure. Chaque nombre est connu par au moins un autre
maillon avant d'être calculé. Lean est la clé de voûte parce que c'est le seul maillon dont la sortie ne
peut pas être ajustée après coup.

## 4. Ordre, portes, arrêts

| Phase | Contenu | Porte / kill |
|---|---|---|
| 0 | Vérifier les **[à vérifier]** (Abel–Anderson–Wheatley ; Svensson S(k) ; `GraphRicciCurvature` ; le modèle de K–V = Landau à F₀ seul) — avec un budget de recherche neuf | tout item non confirmé est rayé |
| 1 | Pré-enregistrement commité : critères, tolérances, contrôles négatifs pour §3 et §2.2 | avant le premier nombre |
| 2 | §3 étapes 1–3 (données GP existantes, GUDHI, test de stabilité) | l'inégalité doit tenir ; si elle est violée, c'est un bug de pipeline, pas une découverte |
| 3 | Lean : `coarseRicci_hypercube`, `wasserstein_certificate`, `first_sound_sq` ; Comparator | contrôles négatifs |
| 4 | §2.2 solveur BGK ; validation c₀/c₁ ; comparaison à la courbe historique | ±20 % sur ωτ du pic |
| 5 | §2.1 si la porte 0 confirme le modèle ; §2.5 si S(k) existe | — |
| 6 | Revue adverse à contexte vierge ; décision du propriétaire sur tout contact | — |

**Recommandation** : phases 0–2 d'abord. Elles ne demandent aucune donnée nouvelle, ferment la boucle
une première fois sur ce que le projet possède déjà, et donnent au premier échange avec Godfrin une
quatrième question précise (les paramètres de Landau du ³He massif, §2.2) qui a une suite concrète.
