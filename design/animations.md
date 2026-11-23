# Animations — Garnier Cycles (site de démonstration)

Techno : GSAP 3 + ScrollTrigger (`src/main.js`). Deux mécaniques de scroll seulement : **vue éclatée** et **compteurs**.
Caractère du mouvement : mécanique et sec, comme un assemblage. Easings `power3.inOut` / `power2.in` / `steps()`, jamais de `back`, `elastic` ou `bounce`.

## Recherche Inspo

`find_reference_components` renvoie un index (68 archétypes) sans entrée « exploded view » ni « number counter » animés. J'ai lu le source (`get_reference_jsx`) des 4 composants les plus proches. Ce sont des composants statiques : j'en ai repris des **idées** (structure, rythme, comportement), pas le code.

| Composant Inspo | Idée retenue | Où sur le site |
|---|---|---|
| `stat / row` (Stat row) | Chiffres en `tabular-nums` pour que les chiffres ne « dansent » pas pendant le comptage ; libellé en capitales sous le chiffre. | Compteurs : planche 02 (40 / 312) et planche 07 (fiche client). |
| `stat / annotated` (Stats + footnotes) | Chaque chiffre porte un appel de note en exposant qui renvoie à sa méthode de mesure ; les notes sont regroupées sous la grille. Transposé en **nomenclature numérotée 01–06** pour les pièces de la vue éclatée. | Fiche client (¹ ² ³ sous la grille) ; numéros + poids de chaque pièce dans la vue éclatée ; compteur « 00 / 06 · Nomenclature ». |
| `features / bento` (Bento) | Tuile principale en 2 × 2, tuiles secondaires plus petites ; l'ordre de lecture part de la tuile principale. Repris comme **ordre de révélation** : la tuile principale d'abord, puis les autres en cascade. | Révélation de toutes les grilles bento (atelier, matériaux, modèles, options, fiche, avis, étude, contact). |
| `faq / accordion` (Native details) | `<details>` natif, une seule réponse ouverte à la fois, signe « + » typographique qui pivote de 45°. | FAQ (planche 10). |

## Détail des mouvements

### 1. Vue éclatée (hero épinglé) — desktop ≥ 900 px
- **Déclencheur** : `ScrollTrigger` épingle le hero (`pin: true`) sur +430 % de hauteur d'écran, `scrub: 0.3` (presque direct, sans glisse).
- **Chorégraphie** :
  1. Le texte du hero se retire d'un bloc (`y: -24`, `power2.in`, 0,45) ; le nom descend ; les cotes jaunes s'éteignent.
  2. Démontage, une pièce par cran : selle → cockpit → fourche → roues (les deux ensemble) → groupe. Chaque pièce suit son propre axe (`power3.inOut`, durée 1, pas de dépassement).
  3. Dès qu'une pièce est à l'arrêt : sa ligne de rappel et son étiquette apparaissent (glissé de 10 px, `power2.out`, 0,3). Étiquette : n°, poids, matériau, rôle.
  4. Le cadre ne bouge pas : il passe en jaune pendant son annotation (c'est lui qui porte les cotes du client).
  5. Pause, puis **remontage** dans l'ordre inverse (décalage de 0,09 s par pièce), et le texte du hero revient.
- **Rythme « à crans »** : `snap: 'labelsDirectional'` sans inertie. Le scroll s'arrête sur chaque pièce comme une clé qui s'enclenche (0,12 à 0,35 s, `power2.inOut`).
- **Compteur de nomenclature** : `00 / 06` → `06 / 06`, mis à jour par étape.

### 1 bis. Vue éclatée — mobile < 900 px (version allégée)
- Les pièces s'écartent **uniquement à la verticale**, en **4 étapes** : selle + cockpit, roues, fourche + groupe, cadre.
- Une seule légende en bas de l'écran (1 ou 2 fiches côte à côte), remplacée à chaque étape. Pas de lignes de rappel.
- Épinglage plus court (+300 %).

### 2. Compteurs
- **Déclencheur** : la grille qui contient les chiffres entre à 75 % de l'écran (une seule fois).
- **Rythme** : `ease: steps(26)` sur 1,3 s, décalage de 0,12 s entre chiffres. Les valeurs avancent **par crans**, comme un compteur à rouleaux, sans glissé continu.
- Format français (`Intl.NumberFormat('fr-FR')`) : espace fine pour les milliers, virgule décimale (71,0°).
- Valeurs : angle de direction 71,0°, angle de selle 74,0°, cadre 1 640 g, vélo 8 620 g, 46 h de fabrication, 23 cordons de soudure, 40 vélos/an, 312 vélos livrés.

### Révélation des bento (complément discret, pas une mécanique de scroll)
- `clip-path: inset(0 0 100% 0)` → `inset(0)` : chaque tuile se découvre de haut en bas comme un volet, 0,6 s, `power3.inOut`, cascade de 0,07 s. Une seule fois.

## Accessibilité et repli
- `prefers-reduced-motion: reduce` : aucun épinglage ni tween. Le vélo est assemblé et statique (cadrage serré) ; la nomenclature s'affiche en grille sous le hero ; les compteurs montrent directement leur valeur finale.
- Sans JavaScript : même rendu que reduced-motion (le HTML contient déjà toutes les valeurs finales et la nomenclature).
- Le cadrage du dessin est choisi par un petit script en `<head>` avant le premier affichage, pour éviter un saut.

## Interdits respectés
Pas de scroll horizontal, pas de carrousel, pas de texte révélé mot à mot, pas d'image qui grandit, pas de schéma sticky, pas de changement d'univers progressif (le fond vert reste fixe pendant tout l'éclaté), pas de tracé SVG de plans (les lignes de rappel apparaissent d'un coup, elles ne se dessinent pas).
