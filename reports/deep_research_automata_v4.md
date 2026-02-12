# Deep Research Report — Automata V4 Spatial Assembly Fix

## Executive Summary

Le fichier `automata_unified_v4.py` (16 375 lignes) génère des automates mécaniques 3D imprimables. L'assembly STL était mécaniquement impossible : pièces individuelles OK mais positionnement incohérent. Convention visée : X=largeur, Y=profondeur, Z=hauteur (UP).

**4 bugs spatiaux critiques identifiés, 3 corrigés, 1 restant :**

| Bug | Description | Statut | Commit |
|-----|-------------|--------|--------|
| SPATIAL-1 | Shaft translate→rotate inversé | ✅ Fixé (session précédente) | pré-audit |
| SPATIAL-2 | Cames au sol (Z=0) | ✅ Fixé | `f94d3ac` |
| SPATIAL-3 | Murs Y/Z swappés | ✅ Fixé (bore partiel) | `bd6f574` |
| SPATIAL-4 | Followers Z=50 hardcodé | ✅ Fixé | `f94d3ac` |
| CAM-1 | Came surdimensionnée (95>80mm) | 🔴 Ouvert | — |

**Bugs mineurs (tous fixés cette session) :**

| Bug | Commit |
|-----|--------|
| CAM-W1: dict→CamSegment crash | `6295d82` |
| UI-W2/W3: Flask 400 manquant | `cba4482` |
| INFO-2: drummer eyes 0.099mm³ | `ea18b5b` |
| INFO-3: timing_data champs manquants | `d6aef24` |

---

## Internet Findings

### 1. `trimesh.creation.extrude_polygon` — toujours en Z
- **Source** : [trimesh docs](https://trimesh.org/trimesh.creation.html#trimesh.creation.extrude_polygon)
- Extrude TOUJOURS le long de Z. Pas de paramètre `direction`.
- Paramètre `transform` applique une matrice 4×4 APRÈS construction.
- **Conclusion** : rotation post-extrusion nécessaire pour murs verticaux.

### 2. trimesh boolean `difference()` — fiabilité
- **Source** : [trimesh boolean docs](https://trimesh.org/trimesh.boolean.html)
- Backends : `manifold3d` (recommandé), `blender`, `scad`
- `manifold3d` non installé dans l'env → booleans 3D indisponibles
- **Conclusion** : bore 2D via shapely uniquement. Quand bore > mur, skip et annoter.

### 3. Mur vertical + bore horizontal — best practice
- Extrude mur en Z (2D shapely) → rotate pour mettre hauteur sur Z
- Le bore shapely (cercle 2D) devient un cylindre le long de Y après rotation +π/2 X
- Si bore_diameter > wall_thickness : le polygone se split → `ensure_polygon` garde un fragment
- **Solution adoptée** : skip bore 2D, stocker en metadata. Alternative future : `manifold3d` CSG.

### 4. Transform math après rotation +π/2 autour de X
- Rotation +π/2 X : (x,y,z) → (x, -z, y)
- Mesh avant : X∈[0,t], Y∈[0,h], Z∈[0,d-10]
- Mesh après : X∈[0,t], Y∈[-(d-10),0], Z∈[0,h]
- Translation pour centrer Y : ajouter +(d/2-5) en Y
- **Vérifié** : wall_left Y=[-25,25]=50mm depth, Z=[3,73]=70mm height ✅

### 5. Réduction taille came — méthodes
- Augmenter φ_max (angle de pression) : métal=30°, PLA peut tolérer 35-40°
- Levier démultiplicateur : ratio 2:1 → amplitude came /2 → Rb /2
- Came à gorge (groove cam) : élimine spring, permet Rb plus petit
- Follower à fond plat : réduit Rb mais augmente friction
- **Recommandation** : levier démultiplicateur + φ_max=35° pour PLA

---

## Fix-by-Fix Changelog

### Fix 1: CAM-W1 — `6295d82`
- `to_cam_segments()` retournait des dicts, `CamProfile.evaluate()` attendait des CamSegment
- Conversion dict→CamSegment avec split rise_return en rise+return
- `compile_scene_to_cams()` gère les deux types (dict et CamSegment)

### Fix 2: UI-W2/W3 — `cba4482`
- Flask POST `/generate` sans body ou prompt vide → 200 OK (silencieux)
- Ajout validation : retourne 400 avec message d'erreur

### Fix 3: INFO-2 — `ea18b5b`
- `_make_eyes()` : min eye_radius=1.0mm, pupil_radius=0.7mm
- Drummer eyes : 0.099mm³ → 1.25mm³

### Fix 4: INFO-3 — `d6aef24`
- `timing_data` enrichi avec `motor_stall_mNm` et `safety_margin`

### Fix 5: SPATIAL-2+4 — `f94d3ac`
- `ChassisConfig.shaft_center_z` property ajoutée (formule par type chassis)
- Cames : `mesh.apply_translation([0, i*8.0, cz - cam_thickness/2])`
- Followers : Z dynamique = `cz + amplitude + 10`
- Résultat : cames Z=[32.5,37.5], shaft Z=[33,37] → alignés ✅

### Fix 6: SPATIAL-3 — `bd6f574`
- `create_bearing_wall()` : rotation +π/2 X post-extrusion
- Translation recalculée pour centrer depth en Y
- Bore : skip 2D quand bore_diameter ≥ wall_thickness × 0.95
- `create_bearing_wall_with_joints()` : même fix
- Résultat : murs Y=50mm(depth), Z=70mm(height) ✅

---

## Validation Results

```
$ python automata_unified_v4.py --test
🎉 MASTER TEST: ALL PASS (94 checks)

$ All 9 presets generate OK:
✅ nodding_bird: 17 parts
✅ walking_figure: 24 parts
✅ drummer: 21 parts
✅ swimming_fish: 18 parts
✅ waving_cat: 18 parts
✅ flapping_bird: 22 parts
✅ blacksmith: 17 parts
✅ bobbing_duck: 16 parts
✅ rocking_horse: 22 parts

Spatial alignment (nodding_bird):
  base_plate:  Y=[-30,30]=60mm  Z=[0,3]=3mm      ✅
  wall_left:   Y=[-25,25]=50mm  Z=[3,73]=70mm     ✅ (was Y=70,Z=50)
  wall_right:  Y=[-25,25]=50mm  Z=[3,73]=70mm     ✅
  camshaft:    Y=[-12,12]=24mm  Z=[33,37]=4mm      ✅
  cam_neck:    Z=[32.5,37.5]                        ✅ (was Z=[0,5])
  follower_0:  Z=[70,75]                            ✅ (was Z=[50,55])
```

---

## Remaining Risks & Next Actions

### 🔴 CAM-1: Came surdimensionnée
- nodding_bird cam_neck: 95×95mm bbox, chassis 80×60mm
- Rb=42mm pour amplitude=25mm → diamètre ~134mm
- **Action** : implémenter clamp Rb ≤ chassis_max/2, ou levier démultiplicateur, ou auto-resize chassis
- **Besoin** : deep research sur formule Rb(amplitude, φ_max) par loi de mouvement

### ⚠ SPATIAL-3 bore incomplet
- Bore 2D skippé car Ø4.5mm > mur 3mm → wall metadata seulement
- **Options** :
  - A) `pip install manifold3d` → CSG 3D fiable
  - B) Épaissir le mur à 5mm (bore rentre)
  - C) Open cradle (U-slot) au lieu de trou fermé
- **Action** : deep research sur manifold3d availability et open cradle design

### ⚠ Bracket orientation
- `create_camshaft_bracket()` n'a PAS été rotaté (extrude en Z = épaisseur OK pour bracket horizontal)
- Mais sa position Y peut être off → vérifier

### ⚠ Collisions
- Les collisions détectées à l'audit (11 pour nodding_bird) ont probablement changé avec les fixes spatiaux
- **Action** : re-run collision detection post-fixes
