# 🧠 SESSION STATE — Audit Complet du Système de Tests
# À lire en PREMIER pour reprendre le travail sans perdre le contexte
# Date: 12 février 2026 | Fichier: automata_unified_v4.py (~16500 lignes)

---

## 1. LE PROBLÈME DÉCOUVERT

Le système affiche **"94 checks ALL PASS"** mais c'est FAUX.

### Comment ça marche (mal) :

```
test_master() → Phase 5 → grep -c "def check_" → 94 ≥ 90 → "ALL PASS" ✅
```

ÇA COMPTE QUE LES FONCTIONS **EXISTENT**, PAS QU'ELLES **TOURNENT SUR DES DONNÉES RÉELLES**.

### Preuve :

| Catégorie | Count | Détail |
|-----------|-------|--------|
| Appelé dans generate() | **1** | check_motor_feasibility uniquement |
| Appelé depuis run_block*_all (prod code) | 53 | Mais run_block*_all n'est appelé QUE depuis test_block* |
| Appelé UNIQUEMENT dans test_block* | 40 | Avec des dicts hardcodés |
| **Total "réellement validé" en production** | **1/94** | **1.1% de couverture** |

### Les test_block* utilisent des données FAKE :

```python
# Exemple test_block2 ligne 13160 :
cams_ok = [
    {"name": "cam_A", "z_min_mm": 0, "z_max_mm": 5, "Rmax_mm": 20},  # HARDCODÉ
    {"name": "cam_B", "z_min_mm": 6, "z_max_mm": 11, "Rmax_mm": 18},  # HARDCODÉ
]
v = check_trou1_cam_collision(cams_ok)  # Teste la LOGIQUE, pas la GÉOMÉTRIE RÉELLE
```

Conséquence : les checks valident que leur logique interne fonctionne, mais JAMAIS
que la géométrie réellement générée par generate() est correcte.

---

## 2. LES 94 CHECKS — CLASSIFICATION COMPLÈTE

### Par domaine :

| Domaine | Count | Exemples |
|---------|-------|----------|
| CAM_GEOMETRY | 13 | undercut, pressure_angle, collision, phasing, thickness |
| SHAFT_DRIVE | 16 | motor, torque, shaft_deflection, transmission, stall |
| FDM_PRINT | 8 | orientation, supports, estimate, shrinkage, infill |
| ASSEMBLY | 13 | chassis, clearance, retention, BOM, press_fit |
| MATERIALS | 13 | fatigue, creep, thermal, wear, lubrication, bearing |
| LINKAGE | 12 | grashof, lever, worm_gear, geneva, spring, gravity |
| EXOTIC | 10 | rotation_pure, large_stroke, fast_motion, compound |
| PHYSICS | 4 | vibrations, hertz, backlash, follower_jump |
| SAFETY | 4 | EN71, electrical, noise |
| Autre | 1 | min_teeth |

### Par appel :

- **Dans generate()** : `check_motor_feasibility` (ligne ~6208)
- **Dans run_block4_all** (18 checks) : exotic + physics → appelé uniquement par test_block4
- **Dans run_block5-8_all** (8 checks chacun) : cam/lever/thermal/safety → appelé uniquement par test_block5-8
- **Dans test_block2-3** (27 checks) : trou1-27 → données hardcodées directement

### CE QUI N'EXISTE PAS DU TOUT :

| Catégorie | Status | Impact |
|-----------|--------|--------|
| Spatial coherence (wall/shaft/cam/follower Z) | ✅ AJOUTÉ Session 12 | validate_assembly Step 8 |
| Mesh quality (watertight, volume, faces) | ✅ AJOUTÉ Session 12 | validate_assembly Step 8 |
| Collision AABB réelle | ✅ AJOUTÉ Session 12 | validate_assembly Step 8 |
| Dimensional (< 256mm) | ✅ AJOUTÉ Session 12 | validate_assembly Step 8 |
| STL export validation | ❌ MANQUANT | Pas de check fichier valide/non-vide |
| Min feature size > 1.2mm | ❌ MANQUANT | Sur mesh réel |
| Real wall thickness | ❌ MANQUANT | Sur mesh réel |
| Follower atteint la came | ❌ MANQUANT | Fonctionnel |
| Crank handle ne tape pas mur | ❌ MANQUANT | Fonctionnel |

---

## 3. BUGS TROUVÉS ET CORRIGÉS (Session 12)

### BUG-1 : CAM↔CAM Collision — CORRIGÉ ✅ `56f1785`

**Cause** : Toutes les cames à Y = i*8.0mm (espacement fixe). Quand rayon > 4mm → overlap.
**Affectait** : walking_figure (6 collisions), flapping_bird (3), drummer (1), rocking_horse (1)
**Fix** : Espacement Y dynamique basé sur half-width réelle de chaque came + 2mm gap.
Plus auto-resize du chassis depth quand les cames dépassent 60mm.

**Code modifié** : `generate()` dans automata_unified_v4.py (~ligne 6170-6230)
- Supprimé : `mesh.apply_translation([0, i*8.0, cz - cam_thickness/2])`
- Ajouté : collecte des cam_half_widths, calcul de cam_y_positions, centrage sur Y=0
- Ajouté : auto-resize chassis depth (needed = 2*max_extent + 2*wall_t + 15mm, min 60mm)

### BUG-2 : BRACKET↔MOTOR Collision — CORRIGÉ ✅ `63fecf3`

**Cause** : camshaft_bracket à Z=cz-7.5=27.5, motor_mount top à Z=30 → overlap 2.5mm systématique.
**Affectait** : 9/9 presets (100%)
**Fix** : `bracket_z = max(cz-7.5, motor_top_z + 1.0)` → bracket à Z=31, motor top à Z=30.

**Code modifié** : `generate_chassis()` dans automata_unified_v4.py (ligne ~1745)
- Ajouté calcul motor_top_z = plate_thickness + 2 + motor_length
- bracket_z = max(cz-7.5, motor_top_z+1.0)

### BUG-3 : FIG↔CHASSIS Collision — CORRIGÉ ✅ `b3e7967`

**Cause** : Pattes/stands allaient de Z=0 à chassis_top, traversant tout le mécanisme.
**Affectait** : nodding_bird (7 collisions), swimming_fish (5), flapping_bird (7)
**Fix** : Piédestaux courts de 12mm posés SUR le chassis (Z=[base_z-12, base_z]).

**Code modifié** : 3 fonctions figurine :
- `generate_figurine_nodding_bird()` (ligne ~4764) : legs h=12mm au lieu de h=base_z
- `generate_figurine_flapping_bird()` (ligne ~4833) : idem
- `generate_figurine_fish()` (ligne ~5264) : stand h=12mm au lieu de h=base_z

### validate_assembly Step 8 — AJOUTÉ ✅ `fe9eb2e`

**Quoi** : `validate_assembly_post_generate(parts, chassis_config)` ajouté comme Step [8/8].
**Vérifie** : mesh quality, spatial (cam Z vs shaft), dimensional (<256mm), collision AABB.
**Exclut** (faux positifs) : cam↔shaft, fig↔fig joints, eye↔head, base↔wall.
**Résultat** : 9/9 presets → 0 violations.

---

## 4. COLLISIONS NON-BUGS (à ne PAS corriger)

| Type | Count | Raison |
|------|-------|--------|
| FIG↔FIG joints | 32 | Body↔neck, head↔neck, etc. = joints intentionnels (assemblage friction/colle) |
| EYE↔HEAD | 12 | Yeux sphériques dans la tête = boolean union à l'export |
| CAM↔SHAFT | ~9 | Came montée sur l'arbre = attendu |
| follower_guide↔fig_body | 1 | Liaison mécanique = attendu |

Ces paires sont dans la skip_list de validate_assembly_post_generate().

---

## 5. CE QUI RESTE À FAIRE (par priorité)

### P1 — Brancher les 93 checks existants sur données réelles (IMPORTANT)
**Quoi** : Les 93 checks fonctionnent avec des dicts hardcodés. Il faut extraire les
paramètres réels de generate() et les passer aux checks.
**Comment** :
```python
# Après generate(), extraire:
cam_data = [{'name': n, 'Rb_mm': d['Rb_mm'], 'phi_max_deg': d['phi_max_deg'],
             'z_min_mm': mesh.bounds[0][2], 'z_max_mm': mesh.bounds[1][2], ...}
            for n, d in self._cam_designs.items()]
violations += check_trou1_cam_collision(cam_data)
violations += check_trou3_pressure_angle(cam_data)
# ... etc pour les 93 checks
```
**Effort** : Moyen — il faut mapper les clés de chaque check aux données réelles.
**Impact** : Couverture 15% → ~80%

### P2 — Rendre test_master honnête (COSMÉTIQUE mais confiance)
**Quoi** : Phase 5 ne doit pas juste compter `def check_*`.
**Comment** : Exécuter generate() sur 1 preset + compter les violations réelles.
**Effort** : Facile

### P3 — Checks manquants (NICE TO HAVE)
- STL export validation (fichier valide, non vide)
- Min feature size > 1.2mm sur mesh réel
- Follower reach validation
- Crank handle clearance

### P4 — Bore issue (EXISTANT depuis session 10-11)
Quand bore Ø > wall thickness, le bore est skippé en 2D (stocké metadata seulement).
Options : manifold3d CSG, mur 5mm, open cradle (U-slot).

### P5 — Lever mechanisms (13/16 cams)
13 cames ont amp_scale < 1.0 → lever_needed=true avec ratio exact dans metadata.
Le design physique du levier n'est pas encore implémenté.

---

## 6. ARCHITECTURE generate() APRÈS SESSION 12

```
generate()
  ├── [1/8] Validation scène
  ├── [2/8] Compilation mouvement → cames (cam profiles)
  ├── [3/8] Optimisation phases
  ├── [4/8] Moteur ← check_motor_feasibility ✅
  ├── [5/8] Géométrie
  │     ├── Cam meshes (dynamic Y spacing, auto-resize chassis)
  │     ├── Chassis (bracket above motor, walls sized for cams)
  │     ├── Figurine (pedestals, not through-chassis)
  │     └── Joint features
  ├── [6/8] Validation FDM
  ├── [7/8] Timing diagram
  └── [8/8] Validation assemblage ← validate_assembly_post_generate ✅ NEW
             ├── Mesh quality (volume, faces, degenerate)
             ├── Spatial coherence (cam Z vs shaft)
             ├── Dimensional (< 256mm)
             └── Collision AABB (skip expected pairs)
```

---

## 7. FICHIERS MODIFIÉS / CRÉÉS

| Fichier | Lignes | Quoi |
|---------|--------|------|
| automata_unified_v4.py | ~16500 | BUG-1,2,3 fixes + validate_assembly + Step 8 |
| WINTER_TREE_TESTS.md | 223 | Arbre d'hiver des 94 checks |
| SESSION_STATE.md | CE FICHIER | État complet de la session |
| reports/DAILY_2026-02-12.md | ~130 | Rapport journalier bugs |

## 8. COMMITS SESSION 12

| Hash | Message |
|------|---------|
| `56f1785` | fix(BUG-1): cam↔cam collision — dynamic Y spacing + chassis auto-resize |
| `63fecf3` | fix(BUG-2): bracket↔motor collision — bracket Z above motor_mount |
| `b3e7967` | fix(BUG-3): figure↔chassis collisions — legs/stand as short pedestals |
| `fe9eb2e` | feat: validate_assembly Step 8 in generate() + daily report update |
| `[ce push]` | docs: SESSION_STATE.md — comprehensive session state for continuity |
