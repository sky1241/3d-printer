# 🌲 ARBRE D'HIVER — Système de Validation Automata V4

**Date** : 12 février 2026
**Fichier audité** : `automata_unified_v4.py` (16 400+ lignes)
**Verdict** : Le système affiche "94 checks ALL PASS" mais **93/94 ne testent jamais la géométrie réelle**

---

## DIAGNOSTIC RACINE

```
"MASTER TEST: ALL PASS (94 checks)" 
        ↓
Phase 5 fait: grep -c "def check_" fichier.py → 94  ✅
        ↓
Ça compte les FONCTIONS, pas les EXÉCUTIONS sur données réelles
        ↓
Résultat: fausse confiance
```

---

## ARCHITECTURE ACTUELLE

```
generate()
  ├── Step 1: Parse scene         → pas de validation
  ├── Step 2: Build cam profiles  → pas de validation
  ├── Step 3: Optimize phases     → pas de validation
  ├── Step 4: Motor check         → ✅ check_motor_feasibility (SEUL CHECK RÉEL)
  ├── Step 5: Build geometry      → pas de validation
  ├── Step 6: Build chassis       → pas de validation
  └── Step 7: Export STL          → pas de validation

test_master()
  ├── Phase 1: test_block1()      → unit tests cam math (hardcoded input)
  ├── Phase 2: test_block2-3()    → unit tests checks trou1-27 (hardcoded dicts)
  ├── Phase 3: test_block4-8()    → unit tests exotic+physics (hardcoded dicts)
  ├── Phase 4: test_block9()      → diagnose_error() test
  └── Phase 5: Sanity Check       → GREP COUNT "def check_*" ≥ 90 → "ALL PASS"
```

### Ce que "ALL PASS" signifie VRAIMENT :
- ✅ Les 94 fonctions check_* **existent** dans le fichier
- ✅ Chaque fonction **fonctionne** avec des données hardcodées
- ❌ Aucune n'est exécutée sur la géométrie **réellement générée**
- ❌ Zéro validation de la qualité mesh
- ❌ Zéro validation spatiale sur des pièces assemblées

---

## ARBRE DES 94 CHECKS — PAR DOMAINE

### 🎯 CAM GEOMETRY (13 checks)
| Check | Testé sur données réelles ? | Input actuel |
|-------|---------------------------|--------------|
| check_undercut_roller | ❌ hardcoded | rho, rf |
| check_undercut_flat_faced | ❌ hardcoded | s, a, Rb |
| check_trou1_cam_collision | ❌ hardcoded | [{z_min, z_max, Rmax}] |
| check_trou3_pressure_angle | ❌ hardcoded | [{phi_max_deg}] |
| check_trou8_cumulative_lift | ❌ hardcoded | [{lift_mm}] |
| check_trou16_cam_phasing | ❌ hardcoded | [{phase_deg}] |
| check_trou28_motion_law | ❌ hardcoded | [{motion_type}] |
| check_trou29_Rb_min | ❌ hardcoded | [{Rb_mm, amplitude}] |
| check_trou31_cam_pv_product | ❌ hardcoded | [{pv_product}] |
| check_trou33_roller_sizing | ❌ hardcoded | [{roller_radius}] |
| check_trou34_cam_thickness | ❌ hardcoded | [{thickness_mm}] |
| check_trou35_dwell_angles | ❌ hardcoded | [{dwell_deg}] |
| check_trou_60_offset_pressure | ❌ hardcoded | [{offset, phi}] |

### ⚙️ SHAFT & DRIVE (16 checks)
| Check | Testé sur données réelles ? |
|-------|---------------------------|
| check_motor_feasibility | ✅ **SEUL CHECK RÉEL** (dans generate()) |
| check_trou2_shaft_length | ❌ hardcoded |
| check_trou5_torque_with_lever | ❌ hardcoded |
| check_trou11_shaft_deflection | ❌ hardcoded |
| check_trou12_transmission | ❌ hardcoded |
| check_trou13_shaft_retention | ❌ hardcoded |
| check_trou17_startup_torque | ❌ hardcoded |
| check_trou18_stall_protection | ❌ hardcoded |
| check_trou19_manual_crank | ❌ hardcoded |
| check_trou20_power_supply | ❌ hardcoded |
| check_trou32_bell_crank | ❌ hardcoded |
| check_trou39_transmission_angle | ❌ hardcoded |
| check_trou40_crank_slider | ❌ hardcoded |
| check_trou_69_motor_protection | ❌ hardcoded |
| check_trou_70_battery_autonomy | ❌ hardcoded |
| check_trou_71_shaft_deflection | ❌ hardcoded |

### 🖨️ FDM PRINTABILITY (8 checks)
| Check | Testé sur données réelles ? |
|-------|---------------------------|
| check_trou21_print_orientation | ❌ |
| check_trou22_print_supports | ❌ |
| check_trou23_print_estimate | ❌ |
| check_trou49_shrinkage | ❌ |
| check_trou57_print_plate | ❌ |
| check_trou_66_hole_compensation | ❌ |
| check_trou_67_horizontal_hole | ❌ |
| check_trou_72_infill | ❌ |

### 🔧 ASSEMBLY (13 checks) — all ❌ hardcoded
check_trou9_chassis, check_trou10_figure_clearance, check_trou14_component_retention,
check_trou15_assembly_order, check_trou24_calibration, check_trou25_modularity,
check_trou27_bom_quality, check_physics_e5_assembly, check_trou55_assembly,
check_trou56_bom, check_trou58_integration, check_trou59_documentation,
check_trou_68_press_fit

### 🧪 MATERIALS (13 checks) — all ❌ hardcoded
check_physics_e1_friction_wear, check_physics_e2_fatigue, check_physics_e4_tolerances,
check_trou44_thermal, check_trou45_creep, check_trou46_resonance, check_trou47_fatigue,
check_trou48_tolerance_stackup, check_trou50_bearing, check_trou51_degradation,
check_trou_63_gear_fatigue, check_trou_64_wear_rate, check_trou_65_lubrication

### 🔗 LINKAGE (12 checks) — all ❌ hardcoded
check_grashof, check_trou4_lever_sweep, check_trou6_gravity, check_trou7_spring,
check_trou30_return_spring, check_trou36_lever_pivot, check_trou37_lever_bending,
check_trou38_grashof, check_trou41_worm_gear, check_trou42_gear_efficiency,
check_trou43_geneva_timing, check_trou_61_gear_module

### 🌀 EXOTIC (10 checks) — all ❌ hardcoded
check_exotic_cas101 through cas110

### ⚡ PHYSICS (4 checks) — all ❌ hardcoded
check_physics_e3_vibrations, check_physics_e6_hertz, check_physics_e7_backlash,
check_physics_e8_follower_jump

### 🛡️ SAFETY (4 checks) — all ❌ hardcoded
check_trou26_safety, check_trou52_en71_safety, check_trou53_electrical, check_trou54_noise

### + 1 uncategorized: check_trou_62_min_teeth ❌

---

## CE QUI N'EXISTE PAS DU TOUT (0 checks)

### 🔴 SPATIAL COHERENCE — ZÉRO validation
- Wall Z contient shaft Z ?
- Cam Z centré sur shaft Z ?
- Follower Z au-dessus de la came ?
- Pièces ne se chevauchent pas ?
- Assembly rentre sur le plateau (256×256mm) ?
- Base plate couvre les murs ?
- Bore aligné avec axe shaft ?

### 🔴 MESH QUALITY — ZÉRO validation
- is_watertight ?
- is_volume ?
- Faces dégénérées ?
- Auto-intersections ?
- Volume > 0 ?
- Face count raisonnable ?

### 🔴 STL EXPORT — ZÉRO validation
- Fichier STL valide ?
- Fichier non vide ?
- Export individuel par pièce ?

### 🔴 DIMENSIONAL — ZÉRO validation sur mesh réel
- Feature size > 1.2mm ?
- Wall thickness réel > min_wall ?
- Total < 256mm ?

### 🔴 FUNCTIONAL POST-GEN — ZÉRO validation
- Came rentre dans le chassis ?
- Follower atteint la came ?
- Manivelle ne tape pas dans le mur ?
- Shaft ne dépasse pas du chassis ?

---

## RÉSUMÉ CHIFFRÉ

```
94 check functions existent
 1 exécutée sur données réelles (check_motor_feasibility)
93 testées UNIQUEMENT avec des dicts hardcodés dans test_block*
 0 checks de mesh quality
 0 checks de cohérence spatiale
 0 checks dimensionnels sur géométrie réelle
 0 checks d'export STL
```

### Score de couverture RÉELLE : **1.1%** (1/94)

---

## PLAN DE CORRECTION (par priorité)

### P0 — Post-generate() spatial validation (CRITIQUE)
Ajouter dans generate() après Step 7 :
```python
# Step 8: Validate assembly
violations = validate_assembly(self.all_parts, chassis_config)
```
Checks à implémenter :
1. `validate_spatial_coherence(parts, cz)` — shaft/cam/wall/follower Z alignment
2. `validate_no_collision(parts)` — pairwise AABB overlap
3. `validate_fits_build_plate(parts, max_xyz)` — total bounds < printer
4. `validate_mesh_quality(parts)` — watertight, volume>0, no degenerate

### P1 — Wire existing checks to real data (IMPORTANT)
Les 93 checks fonctionnent mais reçoivent des dicts hardcodés.
Solution : après generate(), extraire les paramètres réels et les passer aux checks existants.
```python
cam_data = [{'name': n, 'Rb_mm': d['Rb_mm'], 'phi_max_deg': d['phi_max_deg'], ...}
            for n, d in self._cam_designs.items()]
violations += check_trou1_cam_collision(cam_data)
violations += check_trou3_pressure_angle(cam_data)
# ... etc
```

### P2 — Fix test_master to report honestly (COSMETIC but trust-destroying)
- Phase 5 ne doit pas juste compter `def check_*`
- Doit exécuter `generate()` sur au moins 1 preset et compter les violations

---

## FICHIERS CONCERNÉS
- `automata_unified_v4.py` lignes 6050-6300 (generate method)
- `automata_unified_v4.py` lignes 7300-13100 (all check functions)
- `automata_unified_v4.py` lignes 13155-15800 (test blocks + test_master)
