# 🔍 AUDIT REPORT — automata_unified_v4.py
**Date**: 2026-02-12 | **Sessions**: 5-6 | **Commit base**: 6e17772

## RÉSUMÉ

| Catégorie | Critique 🔴 | Warning ⚠ | OK ✅ |
|-----------|:-----------:|:---------:|:-----:|
| Assemblage spatial | 3 | 1 | — |
| Sérialisation | 1 (FIXÉ) | — | 3 |
| Validation input | 2 (FIXÉ) | — | — |
| Export/Docs | — | 2 | 8 |
| Mécanique (cam) | — | — | 5 |
| Tests & CI | — | 1 | 6 |

---

## 🔴 CRITIQUES — Assemblage spatial (NON FIXÉ)

### BUG-S1: Shaft translate-then-rotate envoie l'arbre au mauvais endroit
- **Fichier**: `_make_shaft_and_drive()` ligne ~1648
- **Cause**: `translate([0,0,cz])` puis `rotate(π/2, X)` → (0,0,35) devient (0,-35,0)
- **Impact**: L'arbre atterrit à Y=-35,Z=0 au lieu de Y=0,Z=35
- **Fix**: Inverser l'ordre — `rotate()` d'abord, puis `translate()`
- **Complexité**: Moyenne — nécessite d'ajuster aussi le positionnement des cames

### BUG-S2: Cames à Z=0 au lieu de la hauteur d'arbre
- **Fichier**: `generate()` Step 5, ligne ~6024
- **Code**: `mesh.apply_translation([0, i*8.0, 0])` — aucun offset Z
- **Impact**: Les cames restent au niveau du sol, pas sur l'arbre (Z=0 vs Z≈35)
- **Fix**: Ajouter offset Z = cz + plate_thickness - cam_thickness/2

### BUG-S3: Murs orientés avec hauteur sur Y au lieu de Z
- **Fichier**: `create_bearing_wall()` ligne ~1522
- **Cause**: Le polygone 2D a X=épaisseur, Y=hauteur, extrudé en Z=profondeur.
  Après translation, la hauteur du mur est sur l'axe Y (horizontal) au lieu de Z (vertical).
- **Impact**: Les trous de roulement traversent sur le mauvais axe
- **Fix**: Rotation 90° autour de X après extrusion, ou refaire le polygone 2D
- **Complexité**: Élevée — touche tous les types de châssis (box, frame, central, flat)

### BUG-S4: Suiveurs à 45mm au-dessus des cames
- **Fichier**: `create_linear_follower_guide()` + `_add_follower_guides()`
- **Impact**: Follower guides à Z=50, cams à Z=5 → gap de 45mm, mécanisme inopérant
- **Note**: Conséquence directe de S2. Se fixera en cascade quand S2 sera corrigé.

> **⚠ NOTE**: Ces 4 bugs rendent l'`assembly.stl` mécaniquement impossible.
> Les pièces individuelles dans `parts/` sont correctes pour l'impression.
> L'assemblage physique par l'utilisateur fonctionne car les pièces ont les bons
> trous/alésages — c'est juste le positionnement 3D qui est incohérent.

---

## ✅ FIXÉ — Session courante

### BUG-F1: scene.json perd `_preset_name` au roundtrip (FIXÉ)
- `to_json()` n'incluait pas `preset_name` → `from_json()` ne le restaurait pas
- Impact: Figurines disparaissaient après export→reload (17 pièces → 8)
- Fix: Ajout sérialisation dans to_json/from_json
- Test: 5 presets vérifient roundtrip identique

### BUG-F2: FDM size check hardcodé à 250mm (FIXÉ session précédente)
- `validate_mesh_fdm()` ignorait les dimensions du lit par axe
- Fix: Check par axe vs `build_volume=(220,220,250)`

### BUG-F3: Validation input manquante (FIXÉ session précédente)
- Amplitude négative, zéro, RPM>30, tracks vides acceptés silencieusement
- Fix: Checks dans `AutomataScene.validate()`

---

## ⚠ WARNINGS — À améliorer

### WARN-1: Motor report manque le couple de décrochage
- `motor_report.md` mentionne le peak torque mais pas le stall torque du moteur
- Impact: L'utilisateur ne peut pas vérifier la marge moteur facilement

### WARN-2: ASSEMBLY.md ne couvre que ~40% des pièces
- nodding_bird: 7/17 pièces mentionnées
- drummer: 8/21 pièces mentionnées
- Les pièces figurine (fig_*) ne sont pas dans le guide d'assemblage

### WARN-3: BOM dit "Steel rod" mais ne dit pas "shaft/arbre"
- Le texte est correct techniquement mais pourrait être plus explicite

---

## ✅ TESTS PASSÉS (pas de bug trouvé)

| Test | Résultat |
|------|----------|
| 17 presets × 3 styles = 51 combos | Zero crash |
| Seed reproducibilité (3 runs MD5) | Identique |
| Seeds edge case (0, -1, MAX_INT) | OK |
| Text parser (10 inputs bizarres) | OK |
| Timing peak vs total_torque | Cohérent |
| Cam profil undercut (phi_max) | Tous < 30° |
| Print settings → parts mapping | 100% match |
| SVG timing valid XML | OK |
| HTML timing interactif | OK |
| Stability report | Présent et complet |
| Tolerance budget > medium > premium | Correct |
| Export fichiers complets | Tous présents |
| Concurrent export (3x same) | Identique |
| Unicode/special chars | OK |
| Determinism | OK |
| Flask GET / | 200 OK |
| Flask POST /generate | 200 OK (fallback default) |

---

## ARCHITECTURE — Coordinate system issue

```
Convention attendue:  X = largeur, Y = profondeur, Z = hauteur (vertical UP)
  base_plate:  ✅ Z=[0,3] — au sol
  figurine:    ✅ Z=[73,114] — debout sur la base
  wall_left:   ❌ hauteur sur Y=[-25,8], profondeur sur Z=[3,53]
  camshaft:    ❌ à Y=-35 Z=0 au lieu de Y=0 Z=35
  cam:         ❌ Z=[0,5] au lieu de Z≈35
  follower:    ⚠  Z=[50,55] — cohérent avec murs mais pas avec cames
```

La correction complète nécessite un refactoring de `create_bearing_wall()`,
`_make_shaft_and_drive()`, et le positionnement des cames dans `generate()`.
Estimation: ~200 lignes modifiées, touchant les 4 types de châssis.
