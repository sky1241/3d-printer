# 🔍 AUDIT COMPLET — automata_unified_v4.py
**Date**: 2026-02-12 | **Sessions**: 5-6 | **Commit**: 83ae210 | **Lignes**: 16 375

---

## RÉSUMÉ EXÉCUTIF

| Catégorie | Critique 🔴 | Warning ⚠ | Fixé ✅ |
|-----------|:-----------:|:---------:|:------:|
| Assemblage spatial | 4 | — | — |
| Moteur de cames | 1 | 1 | 1 |
| Constraint engine | — | 1 | 2 |
| Export / Documentation | — | 3 | — |
| Web UI | — | 3 | — |
| Code quality | — | — | 1 |
| **Total** | **5** | **8** | **4** |

94/94 tests internes passent. **Aucun** de ces bugs n'est détecté par la test suite.

---

## 🔴 CRITIQUES

### SPATIAL-1 : Shaft translate→rotate (assembly impossible)
- **Lieu** : `_make_shaft_and_drive()` L1648
- **Bug** : `translate([0,0,cz])` puis `rotate(π/2, X)` → arbre à Y=-35,Z=0 au lieu de Z=35
- **Impact** : L'arbre est 35mm sous le châssis et ne traverse pas les murs
- **Fix** : Inverser l'ordre — rotate d'abord, translate ensuite

### SPATIAL-2 : Cames au sol (Z=0) au lieu de hauteur d'arbre
- **Lieu** : `generate()` Step 5, L6024
- **Bug** : `mesh.apply_translation([0, i*8.0, 0])` — aucun offset Z vers la hauteur d'arbre
- **Impact** : Cames à Z=[0,5] alors que l'arbre devrait être à Z≈35

### SPATIAL-3 : Murs orientés avec hauteur sur Y au lieu de Z
- **Lieu** : `create_bearing_wall()` L1522
- **Bug** : Polygone 2D a X=épaisseur, Y=hauteur, extrudé en Z=profondeur. Pas de rotation post-extrusion.
- **Impact** : Trous de roulement traversent sur le mauvais axe
- **Touche** : `create_bearing_wall()`, `create_bearing_wall_with_joints()`, 4 types de châssis

### SPATIAL-4 : Suiveurs à 45mm des cames
- **Lieu** : `generate()` L6050, position hardcodée Z=50
- **Impact** : Gap de 45mm entre follower et cam — mécanisme inopérant
- **Note** : Se fixe en cascade avec SPATIAL-2

### CAM-1 : Cames surdimensionnées dépassent le châssis
- **Lieu** : `auto_design_cam()` + `generate()` Step 5
- **Mesuré** : nodding_bird cam = 95×95mm, châssis = 80×60mm
- **Impact** : Came dépasse du boîtier, collision avec les murs
- **La contrainte CAM_TOO_LARGE le détecte mais generate() ignore les erreurs**

### CAM-2 : ~~`MotionPrimitive.to_cam_segment()` — fallthrough silencieux~~ → FIXÉ ✅
- **Fix** : Ajouté support RISE/RETURN/DWELL + `raise ValueError` sur kind inconnu

### CE-1 : ~~`--diagnose` ne lance PAS le constraint engine~~ → FAUX POSITIF
- **Statut** : ✅ PAS un bug. `--diagnose` utilise `❌` au lieu de `🔴`, ce qui a faussé le comptage automatique. La contrainte engine tourne correctement.

### CE-2 : ~~`generate()` ignore les erreurs de `validate()`~~ → FIXÉ ✅
- **Fix** : `generate()` bloque maintenant sur erreurs critiques (amplitude négative, no tracks). Warnings restent non-bloquants.

---

## ⚠ WARNINGS

### CAM-W1 : Phase optimizer crash avec segments dict
- **Lieu** : `optimize_phases()` → `estimate_cam_torque()` → `evaluate()`
- **Bug** : `evaluate()` fait `seg.beta_deg` mais `MotionTrack.to_cam_segments()` retourne des dicts
- **Impact** : Le pipeline MotionTrack → CamProfile crash
- **Note** : compile_scene_to_cams() fonctionne car il convertit en CamSegment

### CE-W1 : 94 checks définis, seulement 21 tirent
- 73 checks (78%) ne tirent sur aucun des 10 presets standard
- Cause probable : configs non testées (crank, chassis_frame) + dead code

### DOC-W1 : `motor_report.md` manque le stall torque
### DOC-W2 : `ASSEMBLY.md` ne couvre que ~40% des pièces (7/17 nodding_bird, 8/21 drummer)
### DOC-W3 : BOM dit "Steel rod" mais pas "shaft" ni "bearing"

### UI-W1 : Web UI stub — pas de preset selector, pas de 3D viewer, pas de download
### UI-W2 : Flask POST /generate avec preset inconnu → 200 OK (devrait être 400)
### UI-W3 : Flask POST /generate sans body → 200 OK (devrait être 400)

### CODE-W1 : ~~4 fonctions dupliquées identiques~~ → FIXÉ ✅
- Supprimé les secondes occurrences de `_pv_product`, `_cam_surface_speed_m_s`, `_natural_frequency_hz`, `_stress_from_cam_force`

---

## ℹ INFO

### INFO-1 : InverseSolver.from_canvas fonctionne (9s, 2 cames, RMS=11mm)
### INFO-2 : Drummer eyes = 0.099mm³ (quasi-dégénérés, non imprimables)
### INFO-3 : timing_data manque safety_margin et motor_stall_mNm

---

## ✅ CE QUI FONCTIONNE BIEN

| Test | Résultat |
|------|----------|
| 51 combos preset×style | Zero crash |
| Seed reproducibilité | MD5 identique |
| Seeds edge (0, -1, MAX_INT) | OK |
| Free text parser | 5/5 textes parsés |
| Cam profile math | Amplitude, périodicité OK |
| 5 motion laws via presets | Profils différents |
| Print settings mapping | 100% |
| SVG/HTML timing | Valides |
| Stability report | Complet |
| Tolerance tiers | Ordonnés |
| Export complet | Tous fichiers présents |
| scene.json roundtrip | Parfait |
| STL mesh quality | Clean |
| validate() edge cases | Attrape neg amp, zero amp, RPM, no tracks |
| Crank mode | 19-24 parts |
| FigurineBuilder | 4 body types OK |
| --fix mode | Réduit Rb |

---

## PRIORITÉ DE FIX

| # | Bug | Effort | Impact |
|---|-----|--------|--------|
| 1 | SPATIAL-1,2,3,4 — assemblage | ~200 lignes | Assembly.stl inutilisable |
| 2 | CAM-2 — fallthrough silencieux | 5 min | API piège pour utilisateurs |
| 3 | CE-2 — validate non-bloquant | 10 min | Scènes invalides acceptées |
| 4 | CE-1 — diagnose sans constraints | 10 min | Faux sentiment de validité |
| 5 | CAM-1 — came > châssis | 30 min | Came sort du boîtier |
| 6 | CAM-W1 — dict/CamSegment compat | 10 min | Crash optimizer |
| 7 | DOC-W1,W2,W3 | 30 min | Docs incomplètes |
| 8 | UI-W1,W2,W3 | 1h | Flask stub |
| 9 | CODE-W1 — dead code | 5 min | Maintenance |
