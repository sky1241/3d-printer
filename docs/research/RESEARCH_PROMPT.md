# Prompt de Recherche — Automata Generator : Tous les Problèmes

## Contexte du Projet

Je développe un générateur procédural d'automates mécaniques imprimables en 3D (FDM). Le système prend une description de mouvement (ex: "un panda qui salue de la patte droite") et génère tous les fichiers STL nécessaires : châssis, arbre à cames, cames, leviers, followers, figurine.

Le moteur de came fonctionne mathématiquement (profils de came calculés correctement, lois de mouvement cycloïdales/polynomiales/harmoniques). Mais l'assemblage mécanique réel a des problèmes critiques qui empêchent l'impression et le fonctionnement.

**Stack technique :** Python, trimesh, numpy, shapely (extrusion 2D→3D), reportlab (PDF).  
**Impression cible :** FDM (PLA/PETG), buse 0.4mm, couche 0.2mm.  
**Arbre :** tige acier/laiton Ø3-4mm. Tout le reste est imprimé.

---

## PROBLÈME 1 : GAP de 16.7mm entre la came et le levier — ils ne se touchent pas

**Symptôme :** La came tourne dans le vide. Le bras du levier (input arm) est 16.7mm au-dessus du sommet de la came. Aucun contact mécanique = aucun mouvement transmis.

**Ce qui existe :** La came est à Z=[32.5→37.5] (centrée sur l'arbre à Z=35mm). Le levier pivote à Z=54mm avec son bras d'entrée qui descend jusqu'à Z=54.2mm minimum.

**Ce qui manque :** Un follower (galet ou patin plat) qui fait le pont entre le profil de came et le bras d'entrée du levier. Dans un vrai automate mécanique, le follower est la pièce qui touche la came et transmet la force au levier.

**Questions de recherche :**
- Quelle géométrie de follower (flat-faced vs roller vs knife-edge) est la plus adaptée pour une pièce FDM à buse 0.4mm ?
- Comment dimensionner le follower pour combler un gap vertical (came en bas, levier en haut) dans un châssis à murs latéraux ?
- Faut-il un ressort de rappel imprimé ou la gravité suffit-elle pour maintenir le contact came-follower ?
- Comment éviter l'usure du follower PLA sur le profil de came PLA (traitement de surface, orientation d'impression, matériau) ?

---

## PROBLÈME 2 : Les murs du châssis n'ont PAS de trou pour l'arbre

**Symptôme :** L'arbre à cames (Ø4mm) est censé traverser les deux murs latéraux, mais les murs sont des plaques pleines (Euler characteristic = 2, confirmé = pas de perçage). L'arbre flotte dans le vide sans support.

**Ce qui existe :** Les murs ont le metadata `joint_type=bearing_bore` avec les bonnes dimensions (bore Ø4.5mm, chamfer 0.5mm) mais ce sont juste des tags — la géométrie boolean (soustraire un cylindre du mur) n'est jamais exécutée.

**Ce qui manque :** Un vrai perçage (boolean difference d'un cylindre Ø4.5mm) dans chaque mur, avec chanfrein d'entrée pour faciliter l'insertion.

**Questions de recherche :**
- Quel jeu (clearance) pour un palier lisse imprimé FDM sur tige acier Ø3mm ou Ø4mm ? (j'ai lu 0.2-0.3mm par côté, à confirmer)
- Faut-il imprimer le palier horizontalement (trou dans l'axe Z d'impression) ou verticalement ? Impact sur la circularité du trou ?
- Faut-il un insert en bronze/PTFE ou le PLA/PETG glisse suffisamment sur l'acier ?
- Le chanfrein d'entrée : 45° × 0.5mm suffit, ou il faut plus pour guider l'insertion ?

---

## PROBLÈME 3 : Les snap-fit (attaches figurine) sont du metadata, pas de la géométrie

**Symptôme :** Les follower guides disent `joint_type=snap_hook` dans leur metadata et les pièces de figurine disent `joint_type=snap_pocket`, mais géométriquement le follower est une boîte rectangulaire de 16 vertices et la figurine n'a aucune cavité. Rien ne s'emboîte.

**Ce qui existe :** Les fonctions `make_snap_hook_3d()` et `make_snap_pocket_3d()` existent dans le code mais ne sont jamais appelées dans le flux de génération. Les paramètres sont définis (hook_width=4mm, lip_height=1.2mm, clearance=0.3mm).

**Ce qui manque :** L'union boolean du snap hook sur le follower guide et la soustraction boolean du snap pocket dans la base de la figurine.

**Questions de recherche :**
- Snap-fit cantilever pour FDM : quelles dimensions optimales (épaisseur de bras, longueur, angle de lip) pour PLA/PETG ?
- Existe-t-il une alternative plus fiable que le snap-fit pour l'assemblage figurine↔mécanisme ? (ex: tenon-mortaise, goupille, collage, vis M2)
- Le snap-fit imprimé en PLA supporte-t-il des assemblages/désassemblages répétés ou il casse après 2-3 fois ?
- Orientation d'impression optimale pour que le snap-fit ne casse pas au démoulage ?

---

## PROBLÈME 4 : Le levier ne transmet pas le mouvement sur l'axe Z (gauche↔droite)

**Symptôme :** Tous les leviers sont verticaux et ne convertissent que le mouvement de came (rotation arbre) en mouvement vertical (haut↔bas, axe X). Impossible de faire "tourner la tête" d'un personnage (rotation sur l'axe Z).

**Ce qui existe :** Levier simple (barre plate verticale) avec pivot, bracket en U, et goupille. Fonctionne pour axe X (monte/descend) et axe Y (avant/arrière).

**Ce qui manque :** Un bell-crank (renvoi d'angle à 90°) qui convertit le mouvement vertical du follower en rotation horizontale. C'est une pièce en L qui pivote dans le plan horizontal.

**Questions de recherche :**
- Bell-crank pour automate imprimé FDM : géométrie optimale, épaisseur minimale, ratio d'entrée/sortie ?
- Comment supporter le pivot du bell-crank ? (palier imprimé, vis, goupille)
- Le bell-crank doit-il être dans le châssis ou au-dessus, au niveau de la figurine ?
- Exemples de mécanismes d'automates en bois qui font la conversion vertical→horizontal — quelles solutions classiques ?

---

## PROBLÈME 5 : Pas de rotation continue 360° (engrenages)

**Symptôme :** Le bouton "Rotation" de l'UI ne peut pas fonctionner car une came ne produit qu'une oscillation (max ±60°). Pour une vraie rotation continue (roue qui tourne, hélice, manège), il faut un train d'engrenages.

**Ce qui existe :** Rien. Pas d'engrenages dans le code.

**Ce qui manque :** Un système d'engrenage simple (2 roues dentées) qui transmet la rotation de l'arbre moteur à un axe secondaire, éventuellement avec un ratio de réduction/multiplication.

**Questions de recherche :**
- Engrenages imprimés FDM : module minimum (0.5mm ? 1mm ?), nombre de dents minimum, jeu de flanc (backlash) ?
- Profil de dent : involute standard ou profil simplifié pour FDM (ex: GT2-like, S-shaped) ?
- Comment gérer l'axe de l'engrenage secondaire ? Perpendiculaire à l'arbre principal (renvoi d'angle) ou parallèle ?
- Engrenage PLA sur PLA : usure, bruit, lubrification nécessaire ?
- Alternatives simples : engrenage à friction, poulie + courroie imprimée, vis sans fin ?

---

## PROBLÈME 6 : Pas de scaling global (taille de pièce)

**Symptôme :** Le slider "Taille pièce" de l'UI (100%) ne fait rien. Toutes les dimensions sont hardcodées.

**Ce qui manque :** Un facteur d'échelle appliqué à toutes les dimensions géométriques SAUF les clearances et épaisseurs minimales de murs (qui restent fixes pour l'imprimabilité FDM).

**Questions de recherche :**
- Quand on scale un automate, quelles dimensions NE doivent PAS être scalées ? (clearances d'assemblage, diamètre d'arbre standardisé, épaisseur de mur minimum)
- Le scaling affecte-t-il les contraintes mécaniques ? (un levier 2× plus long a 2× plus de couple mais aussi 2× plus de déflection)
- Gamme de scaling raisonnable pour un automate FDM ? (50% à 200% ?)

---

## PROBLÈME 7 : Figurines 100% hardcodées, pas procédurales

**Symptôme :** Il existe 10 fonctions `generate_figurine_xxx()` hardcodées. Pour un "panda", il faudrait en écrire une 11ème manuellement. L'UI ne peut pas générer une figurine arbitraire.

**Ce qui existe :** Les Links et Joints définis dans la scène (torso, leg_left, shoulder_right...) ne sont PAS utilisés pour la géométrie de la figurine. La figurine est construite avec des primitives trimesh (sphères, cylindres, ellipsoïdes) placées à la main.

**Ce qui manque :** Un système qui prend une description de figurine (liste de parties corporelles avec dimensions et positions relatives) et génère automatiquement la géométrie 3D correspondante. C'est essentiellement un "robot avatariste" paramétrique.

**Note :** Ce problème est le MOINS prioritaire car un LLM peut facilement générer le code de placement de primitives géométriques. Le vrai problème c'est que les autres pièces (mécaniques) doivent fonctionner physiquement.

**Questions de recherche :**
- Approches existantes pour la génération procédurale de personnages 3D à partir de primitives (capsules, sphères, cylindres) ?
- Comment attacher mécaniquement une figurine procédurale au mécanisme en dessous ? (points d'attache standardisés)
- Épaisseur minimale des parties de figurine pour l'impression FDM ? (bras fins, oreilles, queue)

---

## PROBLÈME 8 : Les 4 types de socle n'existent pas

**Symptôme :** Il n'y a qu'un seul type de châssis : boîte rectangulaire ouverte (base_plate + 2 murs + bracket). L'UI devrait proposer plusieurs styles.

**Types de socle nécessaires :**
1. **Rectangulaire ouvert** (✅ existe) — mécanisme visible
2. **Boîte fermée** — avec couvercle, mécanisme caché, seulement la figurine dépasse
3. **Cylindrique** — socle rond pour figurine tournante
4. **Piédestal** — colonne haute, mécanisme invisible en dessous

**Questions de recherche :**
- Comment adapter la disposition interne (arbre, cames, murs) à un châssis cylindrique ?
- Un châssis fermé nécessite-t-il des ouvertures d'accès pour l'assemblage ? Où les placer ?
- Comment le socle affecte-t-il la résonance/vibration du mécanisme lors du fonctionnement ?

---

## RÉSUMÉ DES PRIORITÉS

| # | Problème | Impact | Difficulté |
|---|----------|--------|------------|
| 1 | Gap came↔levier (pas de follower réel) | 🔴 Critique — rien ne bouge | 🟡 Moyen |
| 2 | Murs sans trou pour l'arbre | 🔴 Critique — pas assemblable | 🟢 Facile |
| 3 | Snap-fit = metadata pas géométrie | 🟠 Majeur — figurine pas attachée | 🟡 Moyen |
| 4 | Pas d'axe Z (bell-crank) | 🟠 Majeur — 3/14 animations bloquées | 🟡 Moyen |
| 5 | Pas d'engrenages (rotation 360°) | 🟡 Important — rotation impossible | 🔴 Gros |
| 6 | Pas de scaling | 🟡 Important — taille fixe | 🟢 Facile |
| 7 | Figurines hardcodées | 🟢 Mineur — LLM peut générer | 🟡 Moyen |
| 8 | 1 seul type de socle | 🟢 Mineur — esthétique | 🟡 Moyen |

**Les problèmes 1 et 2 sont des show-stoppers : même si on imprime les pièces, rien ne bouge et rien ne s'assemble.**

---

## CE QUI FONCTIONNE (ne pas casser)

- ✅ Profils de came mathématiquement corrects (5 lois de mouvement)
- ✅ Phases, amplitudes, vitesses paramétrables
- ✅ Bore D-flat dans les cames (géométrie réelle, euler=0)
- ✅ Moteur prend N tracks arbitraires → génère N cames automatiquement
- ✅ Constraint engine avec 79 checks (pression angle, undercut, fatigue, etc.)
- ✅ Export STL + BOM + assembly guide PDF
- ✅ 100% watertight sur toutes les pièces
- ✅ 9 presets fonctionnels (géométrie OK, juste l'assemblage qui manque)
