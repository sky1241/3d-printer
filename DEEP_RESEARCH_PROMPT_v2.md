# 🔬 Deep Research — Automata Generator : Audit Complet + Solutions

## Contexte

Je construis un **générateur procédural d'automates mécaniques imprimables en 3D** (FDM, buse 0.4mm, couche 0.2mm, PLA/PETG). Le système prend une description de mouvement (ex: "un panda qui salue") et génère automatiquement tous les fichiers STL : châssis, arbre à cames, cames profilées, leviers, followers, figurines.

**Stack :** Python + trimesh + numpy + shapely. Les profils de came sont calculés mathématiquement (5 lois de mouvement : POLY_4567, CYCLOIDAL, MODIFIED_TRAP, POLY_345, SIMPLE_HARMONIC). L'arbre est une tige acier/laiton Ø4mm, tout le reste est imprimé.

**Ce qui marche :** 240 pièces générées sur 9 presets, 100% watertight, 0 volume négatif. Les profils de came sont mathématiquement corrects. Le bore D-flat dans les cames est de la vraie géométrie (euler=0 confirmé). Un constraint engine avec 79 checks validés. Export STL + BOM + PDF.

**Ce qui est cassé :** 80 bugs trouvés, dont 31 CRITIQUES et 40 MAJEURS. **En résumé : les pièces s'impriment correctement mais ne s'assemblent pas et ne bougent pas.**

---

## 🔴 BUG CRITIQUE #1 — Gap de 16.7mm entre came et levier (13 instances sur 9 presets)

### Le problème
La came tourne dans le vide. Le follower/levier est 16.7mm au-dessus du sommet de la came. Zéro contact mécanique = zéro mouvement transmis.

**Positions mesurées (preset nodding_bird) :**
- Came `cam_neck` : Z = [32.5 → 37.5mm] (centrée sur l'arbre à Z=35mm)
- Levier `lever_neck` : Z = [54.2 → 71.6mm] (pivot à ~63mm)
- Gap = 54.2 - 37.5 = **16.7mm de vide**

### Ce qui existe dans les vrais automates
Dans un automate mécanique (bois ou impression 3D), la chaîne est : **Came → Follower → Tige/Levier → Figurine**. Le follower est la pièce qui touche physiquement la came. Il existe 3 types principaux :
- **Flat-faced follower** (patin plat) : simple, bonne surface de contact, usure répartie
- **Roller follower** (galet) : moins de friction, mais plus complexe à imprimer
- **Knife-edge follower** (pointe) : précis mais s'use vite, inadapté FDM

Pour les automates FDM, le flat-faced follower est le standard (source : Cabaret Mechanical Theatre, Dug North, Teaching Tech). La gravité maintient le contact came-follower quand la figurine est au-dessus.

### Questions de recherche
1. **Dimensionnement du follower FDM** : quelle largeur de patin pour un profil de came de rayon 15-45mm ? Quelle épaisseur minimum pour résister à la fatigue PLA ?
2. **Guide du follower** : la tige du follower doit coulisser dans un guide (bearing). Quel jeu pour un guidage lisse FDM ? Les sources indiquent 0.4-0.5mm de clearance totale pour FDM (0.2mm par côté). Est-ce suffisant pour un mouvement répétitif ?
3. **Contact came-follower PLA sur PLA** : usure, faut-il lubrifier (PTFE spray) ? Orientation d'impression du follower pour que les couches soient perpendiculaires au mouvement ?
4. **Ressort de rappel** : si la figurine est trop légère pour maintenir le contact par gravité, faut-il un ressort imprimé (cantilever spring) ou un élastique ? Quelle force de rappel pour une came de rayon max 45mm tournant à 30-60 RPM ?
5. **Design alternatif : hinged cam follower** (source: Dug North, Cabaret Mechanical Theatre) — un levier pivoté dont un bras touche la came et l'autre pousse la figurine. Avantage : élimine le besoin de guidage linéaire. Le levier actuel EST déjà presque ça, il manque juste que son bras d'entrée descende jusqu'à la came.

---

## 🔴 BUG CRITIQUE #2 — Murs du châssis sans trou pour l'arbre (18 instances)

### Le problème
Les 2 murs latéraux sont des plaques pleines. Euler characteristic = 2 = aucun perçage. L'arbre Ø4mm ne peut pas les traverser.

Le code a `metadata['joint_type'] = 'bearing_bore'` avec `bore_dia=4.5mm, chamfer=0.5mm` — mais la boolean difference n'est **jamais exécutée**. Même problème sur `camshaft_bracket`.

### Données techniques (sources web)
- **Clearance FDM palier lisse :** 0.2mm pour fit normal, 0.4mm pour fit libre (source: Prusa forum, UltiMaker community). Pour arbre Ø4mm → bore = Ø4.4-4.5mm.
- **Trous FDM toujours sous-dimensionnés** (source: 3DChimera) : STL approxime le cercle avec des triangles. Surdimensionner de +0.2mm.
- **Orientation :** trou horizontal (axe du trou ⊥ lit) = plus rond. Nos murs sont imprimés debout → le trou de l'arbre est dans le plan XY = OK.
- **Chanfrein :** 45° × 0.5-1mm pour guider l'insertion.
- **trimesh boolean** : `wall.difference(trimesh.creation.cylinder(...))` — le code a déjà 38 appels boolean ailleurs.

### Questions de recherche
1. **Insert bronze/PTFE** : pour arbre acier dans palier PLA, faut-il un insert ? À quelle vitesse (RPM) le PLA commence à fondre par friction ?
2. **Ovalisation du bore FDM** : tolérance à garder ? Post-process (alésoir Ø4.5mm) nécessaire ?
3. **Manifold3D vs Blender** pour booleans trimesh : lequel plus fiable pour bores cylindriques ?

---

## 🟠 BUG MAJEUR #3 — Leviers sans trou pivot (13 instances)

Chaque levier (euler=2) est un solide plein. Le levier ne peut pas tourner autour de sa goupille. Même pattern : metadata dit `pivot_pin` mais géométrie = barre pleine.

**Fix :** Boolean difference d'un cylindre Ø(pin_dia + 0.3mm) au point de pivot.

---

## 🟠 BUG MAJEUR #4 — Snap-fit = metadata, pas géométrie (25 instances)

### Le problème
- `follower_guide` : 16 vertices = boîte plate. Metadata dit `snap_hook` (hook_width=4mm, lip_height=1.2mm).
- Pièces `fig_*` : metadata dit `snap_pocket` mais aucune cavité.
- `make_snap_hook_3d()` existe mais **appelée 0 fois**. `make_snap_pocket_3d()` appelée 1 seule fois.

### Données techniques snap-fit FDM (sources web)
- **Épaisseur cantilever base :** ≥1mm (Protolabs, HP MJF handbook)
- **Clearance FDM :** 0.5mm (Clarwe)
- **Fillet base :** rayon ≥ 0.5× épaisseur (évite fracture)
- **Taper :** 100% base → 50% tip (distribution stress uniforme)
- **Orientation :** plan XY OBLIGATOIRE (Z-axis perd 50% résistance, source: Core77/Fictiv)
- **PLA = snap usage unique** (cassant). **PETG = snap réutilisable** (Mandarin3D)
- **Infill 100%** sur zones snap-fit
- **Alternative plus simple :** tenon cylindrique Ø3mm + friction fit (Ø3mm -0.1mm ↔ trou Ø3mm +0.2mm)

### Questions de recherche
1. **Snap-fit vs tenon vs vis M2 vs colle** : quel système pour figurine sur mécanisme vibrant à 30-60 RPM ?
2. **Cycles avant casse** : PLA snap → combien de montages ? PETG ?
3. **Force de rétention minimum** pour que la figurine ne se décroche pas pendant fonctionnement ?

---

## 🟡 BUG IMPORTANT #5 — Pas de mouvement axe Z / bell-crank

21 références "bell-crank" dans le code mais **zéro implémentation géométrique**.

### Bell-crank : la solution
Levier en L pivoté au coude, convertit mouvement vertical → horizontal à 90° (source: Wikipedia, DT Online, Rob Ives, MISUMI). Standard dans les automates pour mouvements latéraux.

- Bras entrée (vertical) ≈ bras sortie (horizontal) → ratio 1:1
- Pivot au coude : goupille Ø2-3mm
- Épaisseur minimum FDM : 3mm
- Placement : entre les murs du châssis OU au-dessus (au niveau figurine)

### Questions de recherche
1. **Bell-crank FDM** : épaisseur, orientation, jeu pivot ?
2. **Placement dans/sur le châssis** : avantages de chaque option ?
3. **Connexion follower vertical → entrée bell-crank** : pushrod ? Direct ?
4. **Exemples d'automates avec bell-crank** : plans, dimensions, retours d'expérience ?

---

## 🟡 BUG IMPORTANT #6 — Pas d'engrenages (rotation 360°)

### Données techniques engrenages FDM (sources web)
- **Module minimum FDM :** 0.625mm/11 dents testé OK (Prusa forum, FreeCAD). **Module 1mm recommandé** (buse 0.4mm).
- **Dents minimum :** 12 (interférence involute en dessous). 25 recommandé (usure réduite).
- **Profil :** involute, angle de pression 20°
- **Backlash FDM :** 0.2-0.5mm clearance entre dents
- **PLA OK** pour faible charge + PTFE spray. Nylon idéal mais difficile à imprimer.
- **Infill 100%**, orientation horizontale, couche 0.1-0.2mm
- **Diamètre minimum fonctionnel** : ~12mm OD (source: EngineerDog)

### Questions de recherche
1. **Bibliothèque Python** pour générer involute gear mesh (trimesh compatible) ?
2. **Train d'engrenages minimum** : nombre de pièces supplémentaires pour ratio 1:1 ?
3. **Renvoi d'angle** : bevel gear vs worm gear vs courroie ? Quelle option la plus facile en procédural ?
4. **Alternative :** friction wheel (2 cylindres qui se touchent) = beaucoup plus simple, fonctionne à faible charge ?

---

## 🟡 BUG IMPORTANT #7 — Pas de scaling global

0 référence à `scale_factor`. Toutes dimensions hardcodées.

**Contrainte FDM — ne PAS scaler :**
- Clearances assemblage (0.3-0.5mm)
- Diamètre arbre (Ø3/Ø4mm standard)
- Épaisseur mur minimum (1.2mm = 3 × 0.4mm)
- Épaisseur fond minimum (0.6mm = 3 × 0.2mm)

### Questions
1. **Scale range** : 50%-200% raisonnable ? Quelles dimensions cassent en premier en réduction ?
2. **Impact mécanique** : déflection proportionnelle à L³, comment compenser ?

---

## 🟡 BUG IMPORTANT #8 — 117 collisions AABB, aucun check

117 paires de pièces avec bounding boxes qui se chevauchent. 0 check de collision dans le code.

### Questions
1. **Collision detection trimesh** : `mesh_a.intersection(mesh_b).volume > 0` ?
2. **Clearance minimum FDM** entre pièces adjacentes sans contact ?

---

## 🟡 BUG IMPORTANT #9 — Pas de simulation cinématique

Pièces exportées en position statique (angle=0°). Pas de vérification que le mécanisme fonctionne.

### Questions
1. **Simulation Python** : pour chaque angle came 0→360° par 5°, calculer positions follower/levier/figurine, vérifier collisions ?
2. **Export animé** : GIF/vidéo du mécanisme en mouvement ? (trimesh scene animation → export)

---

## 🟠 BUG MAJEUR #10 — PDF d'assemblage incohérent

Le PDF dit "insérer l'arbre dans le bore du mur" mais les murs n'ont pas de bore.

---

## 📊 Résumé quantitatif

| ID | Bug | Sévérité | # | Impact |
|----|-----|----------|---|--------|
| A1 | Murs sans bore | 🔴 CRITIQUE | 18 | Pas assemblable |
| A2 | Gap 16.7mm came→levier | 🔴 CRITIQUE | 13 | Rien ne bouge |
| A3 | Leviers sans trou pivot | 🟠 MAJEUR | 13 | Levier bloqué |
| A4 | Snap-hook = metadata | 🟠 MAJEUR | 16 | Figurine pas attachée |
| A5 | Snap-pocket = metadata | 🟠 MAJEUR | 9 | Figurine pas attachée |
| B2 | Fonctions snap dead code | 🟠 MAJEUR | 1 | Code mort |
| B4 | Pas d'engrenages | 🟡 IMPORTANT | 1 | Rotation impossible |
| B6 | Pas de scaling | 🟡 IMPORTANT | 1 | Taille fixe |
| B9 | 0 collision check | 🟡 IMPORTANT | 1 | 117 collisions AABB |
| C1 | 0 simulation cinématique | 🟡 IMPORTANT | 1 | Pas de validation |
| C2 | PDF incohérent | 🟠 MAJEUR | 1 | Instructions fausses |

**Total : 80 bugs. 31 critiques + 40 majeurs = rien ne fonctionne en l'état.**

---

## ✅ Ce qui fonctionne (ne pas casser)

- 240/240 pièces watertight (100%), 0 volumes négatifs
- Profils de came mathématiquement corrects (5 lois)
- Bore D-flat dans les cames = vraie géométrie (euler=0)
- 38 appels boolean existants dans le code
- 79 checks constraint engine validés
- 9 presets fonctionnels (géométrie OK)
- Export STL + BOM + PDF fonctionnel
- Geneva drive partiellement référencé

---

## 🎯 Roadmap de fix

### Phase 1 — ASSEMBLABLE (les pièces se montent) ~2h
1. A1 : Boolean bore murs (Ø4.5mm + chanfrein)
2. A3 : Boolean bore leviers (Ø pin + 0.3mm)
3. A9 : Boolean bore bracket

### Phase 2 — FONCTIONNEL (ça bouge) ~4h
4. A2 : Follower physique OU rallonger le bras d'entrée du levier jusqu'à la came
5. Recalculer Z de toute la chaîne cinématique

### Phase 3 — ATTACHÉ (figurine tient) ~2h
6. A4+A5+B2 : Appeler les fonctions snap existantes OU implémenter tenon/friction-fit

### Phase 4 — ENRICHI (nouvelles features) ~1-2 semaines
7. Bell-crank (axe Z)
8. Collision check
9. Simulation cinématique
10. Scaling global
11. Engrenages (gros morceau)
