# 🗺️ CODEMAP v4 — automata_unified_v4.py (18615 lignes)
# Dernière mise à jour: 13 février 2026 | Commit: b2d5a46
# 17/17 espèces clean | 95 checks | 7 auto-scaling rules

---

## ARCHITECTURE RAPIDE — ZONES DU FICHIER

```
L1-420        HEADER + IMPORTS + UTILS
L421-526      CAME: CamSegment, CamProfile, evaluate()
L527-874      MOTEUR: estimate_cam_torque, optimize_phases
L875-1090     CHECKS FONDAMENTAUX: motor_feasibility, undercut
L1091-1560    MÉCANISMES: CamDesignResult, FourBarSolution, GearStage, Geneva
L1563-1925    CHÂSSIS: ChassisConfig + 34 create_*() fonctions
L1926-2130    GÉNÉRATEURS CHÂSSIS: box, frame, central, flat, bom
L2136-2890    FDM: ToleranceProfile, JointConfig, tolerances
L2891-3184    ASSEMBLY: bearing_wall_with_joints, CollisionReport
L3185-3404    STABILITÉ: StabilityResult
L3405-4585    VALIDATION: ValidationResult + assembly_validate() [LE GROS CHECK]
L4587-5260    IMPRESSION: optimize_orientation, PrintOptimizer
L5262-5920    SCÈNES: MotionPrimitive, MotionTrack, AutomataScene, 9 presets
L5921-6686    CAMES: create_cam_disk_placeholder, cam synth functions
L6687-6932    FIGURINES: AccessoryDef, FigurineConfig, FigurineBuilder
L6933-7560    SCENEBUILDER: SceneBuilder (make_automaton dispatch)
L7561-8620    GENERATOR: AutomataGenerator.generate() [PIPELINE PRINCIPAL]
L8620-8690    ENUMS: Severity, Violation
L8692-8950    CONSTRAINTS: ConstraintReport, SAFETY dict, MotorSpec, PrinterProfile
L8950-9278    PHYSICS: shaft_deflection_point_load, hertz_contact, follower_jump
L9279-10870   CHECKS trou1-trou27 (27 vérifications fondamentales)
L10872-11230  CHECKS exotic cas101-cas110 (10 cas exotiques)
L11407-11970  CHECKS physics e1-e8 (8 physique avancée)
L11974-12750  CHECKS trou28-trou40 (came avancée + mécanismes)
L12795-13490  CHECKS trou41-trou50 (engrenages + matériaux)
L13491-14210  CHECKS trou51-trou59 (sécurité + impression + BOM)
L14213-15090  CHECKS trou60-trou72 (engrenages avancés + FDM)
L15090-16000  TESTS UNITAIRES INTÉGRÉS (test_*)
L16000-17928  run_all_constraints() + BLOCS B1-B9
L17929-18615  INVERSE SOLVER: InverseSolution, InverseSolver
```

---

## 🔧 PIPELINE generate() — L7561-8620

```
AutomataGenerator.__init__(scene, seed)
    │
generate()
    │
    ├── [1/8] VALIDATE             L7584   scene.validate()
    │
    ├── [2/8] COMPILE CAMS         L7596   compile_scene_to_cams()
    │
    ├── [3/8] OPTIMIZE PHASES      L7603   optimize_phases() → opt_peak torque
    │
    ├── [4/8] MOTOR CHECK          L7618   check_motor_feasibility()
    │   ├── ⚙ AUTO: >8 cams → N20 298:1 (stall 300 mN·m)     L7621-7624
    │   └── ⚙ AUTO: >6 cams → N20 150:1 (stall 200 mN·m)     L7626-7627
    │
    ├── [5/8] GEOMETRY             L7632
    │   ├── Pre-compute Rb_min per cam                          L7634-7660
    │   ├── ChassisConfig creation (width, depth, height)       L7649
    │   ├── ⚙ AUTO: >5 cams → Ø6mm shaft                      L7663-7667
    │   ├── ⚙ AUTO: >6 cams → cam_spacing 6mm                 L7668-7670
    │   ├── compute_camshaft_length()                           L7671
    │   ├── Generate cam meshes (Rb, roller, profile)           L7685-7810
    │   ├── Follower guide positioning                          L7830
    │   │   ├── Compute usable X zone (boss_r aware)            L7835-7845
    │   │   ├── ⚙ AUTO: chassis width expand if guides ≠ fit   L7850-7856
    │   │   └── Even spacing within zone                        L7860
    │   ├── generate_chassis()                                  L7865
    │   ├── ⚙ AUTO: mid-bearing wall if shaft > 180mm          L7870-7881
    │   ├── Lever arms generation                               L7890
    │   └── Figurine generation                                 L7930
    │
    ├── [5b] JOINT FEATURES        L8105   snap-fits, dovetails
    ├── [5c] STABILITY             L8126   center of gravity
    │
    ├── [6/8] FDM                  L8133   tolerance profiles
    │
    ├── [7/8] TIMING               L8144   timing diagram data
    │
    └── [8/8] ASSEMBLY VALIDATION  L8153
        ├── [8a] Geometry checks (collision, watertight)        L4405
        ├── [8b] Constraint engine (95 checks)                  L8158
        │   ├── trou11: shaft deflection                        L3742
        │   │   └── ⚙ AUTO: span/2 if mid-bearing present      L3757-3772
        │   ├── trou57: print plate fit                         L3778
        │   │   └── ⚙ FILTER: exclude camshaft (steel)         L3778-3781
        │   └── DIM-PRINT: total bounds                         L4491
        │       └── ⚙ FILTER: exclude camshaft (steel)         L4491-4495
        └── Report generation
```

---

## ⚙ AUTO-SCALING RULES — 7 RÈGLES

| # | Règle | Condition | Action | Ligne | Ajouté |
|---|-------|-----------|--------|-------|--------|
| R1 | Shaft Ø6mm | n_cams > 5 | camshaft_diameter = 6.0 | L7663 | 13 fév |
| R2 | Cam spacing | n_cams > 6 | cam_spacing = 6.0 (was 8.0) | L7668 | 13 fév |
| R3 | Motor 150:1 | n_cams > 6 | stall_torque = 200 mN·m | L7626 | 13 fév |
| R4 | Motor 298:1 | n_cams > 8 | stall_torque = 300 mN·m | L7621 | 13 fév |
| R5 | Chassis expand | guides don't fit | width auto-rounded to 5mm | L7850 | 13 fév |
| R6 | Mid-bearing | shaft > 180mm & >5 cams | mid_bearing_wall added | L7870 | 13 fév |
| R7 | Deflection /2 | mid-bearing present | span_mm = shaft/2, loads split | L3757 | 13 fév |

### Constantes révisées (research Feb 2026) :

| Constante | Avant | Après | Justification |
|-----------|-------|-------|---------------|
| PLA_HERTZ_MAX (dry) | 8 MPa | 15 MPa | Surface PLA = perimeters solid ~50 MPa, SF=3.3 |
| PLA_HERTZ_MAX (lub) | 10 MPa | 20 MPa | Idem + lubrification |
| PV_LIMIT (dry) | 0.05 | 0.10 | Toy <5 RPM, intermittent |
| PV_LIMIT (lub) | 0.15 | 0.20 | Idem + lubrification |
| BOM default | screws only | +power supply, +PTC 1A | Complétude |
| has_fuse_or_ptc | False | True | PTC 1A dans BOM standard |

### Cascade d'auto-scaling (ordre d'exécution) :

```
n_cams déterminé → [2/8]
    │
    ├── n > 8 → R4 motor 298:1 [4/8]
    ├── n > 6 → R3 motor 150:1 [4/8] + R2 spacing 6mm [5/8]
    ├── n > 5 → R1 Ø6mm shaft [5/8]
    │
    ├── compute_camshaft_length() → shaft_length
    │   ├── shaft > 180mm & n > 5 → R6 mid-bearing [5/8]
    │   └── mid-bearing present → R7 deflection/2 [8b]
    │
    └── guide positioning → usable X zone
        └── guides > zone → R5 chassis expand [5/8]
```

---

## 🚫 FILTRES D'EXCLUSION — 4 FILTRES

| # | Filtre | Quoi | Où | Ligne |
|---|--------|------|----|-------|
| F1 | _non_printed (trou57) | camshaft, shaft, pivot_pin | print plate check | L3778 |
| F2 | _non_printed_dim | camshaft, shaft, pivot_pin | DIM-PRINT bounds | L4491 |
| F3 | skip_pairs (42 paires) | Collisions attendues | Assembly validate | L4506 |
| F4 | mid_bearing skip | mid_bearing_wall ↔ shaft/cams/plate | Collision check | L4532 |

---

## 📦 PIÈCES GÉNÉRÉES — 34 create_*()

### Châssis (L1563-1925)
| Fonction | Pièce | Description |
|----------|-------|-------------|
| create_base_plate | base_plate | Plaque de base avec trous vis |
| create_bearing_wall | wall_left/right | Murs avec paliers arbre |
| create_camshaft_bracket | camshaft_bracket | Pont support arbre |
| create_motor_mount | motor_mount | Support moteur N20 |
| create_linear_follower_guide | follower_guide_N | Guide linéaire U-channel |
| **create_mid_bearing_wall** | **mid_bearing_wall** | **Palier intermédiaire (NEW)** |
| **create_shaft_coupler** | **shaft_coupler** | **Coupleur D-flat (NEW)** |
| create_crank_handle | crank_handle | Manivelle (mode crank) |
| create_printed_collar | collar_N | Collier axial |

### Mécanismes (L1624-1834)
| Fonction | Pièce | Description |
|----------|-------|-------------|
| create_lever_arm | lever_* | Bras de levier amplificateur |
| create_lever_bracket | bracket_lever_* | Support pivot levier |
| create_pivot_pin | pivot_pin_* | Axe pivot (acier) |
| create_collar | collar_lever_* | Collier levier |

### Figurines (L6687-6932)
| Classe | Pièce | Description |
|--------|-------|-------------|
| FigurineBuilder | fig_body, fig_head, etc. | Corps articulé |

---

## 🔍 CHECKS — 95 FONCTIONS EN 9 BLOCS

### Bloc B1 — Fondamentaux (L875-1090)
| Check | Trou | Quoi |
|-------|------|------|
| check_motor_feasibility | — | Peak torque vs motor stall |
| check_undercut_roller | — | Rayon de courbure min |
| check_undercut_flat_faced | — | Came plate-faced |

### Bloc B2 — Trous 1-10 (L9279-9750)
| Check | Quoi | Seuil |
|-------|------|-------|
| trou1 | Collision came/came | AABB overlap |
| trou2 | Longueur arbre | vs lit 220mm |
| trou3 | Angle de pression | φ < 30° |
| trou4 | Balayage levier | clearance 2mm |
| trou5 | Couple avec levier | vs motor safe |
| trou6 | Gravité/orientation | vertical OK |
| trou7 | Ressort retour | preload > 0 |
| trou8 | Lift cumulatif | < stroke max |
| trou9 | Châssis dimensions | vs printer vol |
| trou10 | Clearance figurine | > 2mm |

### Bloc B3 — Trous 11-20 (L9754-10370)
| Check | Quoi | Seuil |
|-------|------|-------|
| **trou11** | **Shaft deflection** | **< 0.30mm (÷2 si mid-bearing)** |
| trou12 | Transmission | ratio, efficiency |
| trou13 | Rétention arbre | e-clips, colliers |
| trou14 | Rétention composants | snap-fits |
| trou15 | Ordre assemblage | séquence logique |
| trou16 | Phasage cames | tolérance ±5° |
| trou17 | Couple démarrage | × 1.3 statique |
| trou18 | Protection calage | fusible/PTC |
| trou19 | Manivelle manuelle | ergonomie |
| trou20 | Alimentation | USB/pile |

### Bloc B4 — Trous 21-27 (L10373-10870)
| Check | Quoi |
|-------|------|
| trou21 | Orientation impression |
| trou22 | Supports nécessaires |
| trou23 | Estimation temps/poids |
| trou24 | Calibration |
| trou25 | Modularité |
| trou26 | Sécurité (EN71) |
| trou27 | Qualité BOM |

### Bloc B5 — Cas exotiques (L10872-11230)
cas101-cas110: rotation pure, grande course, mouvement rapide, many cams, compound, intermittent, asymmetric, external load, inverted, scale

### Bloc B6 — Physique (L11407-11970)
e1-e8: friction/usure, fatigue, vibrations, tolérances, assemblage, Hertz, backlash, follower jump

### Bloc B7 — Came avancée (L11974-12750)
trou28-trou40: loi mouvement, Rb_min, ressort retour, PV product, bell crank, roller sizing, épaisseur, dwell angles, pivot, flexion levier, Grashof, angle transmission, crank-slider

### Bloc B8 — Engrenages + matériaux (L12795-14210)
trou41-trou59: worm gear, gear efficiency, Geneva, thermal, creep, resonance, fatigue, tolerance stackup, shrinkage, bearing, degradation, EN71, electrical, noise, assembly, BOM, **print plate**, integration, documentation

### Bloc B9 — FDM avancé (L14213-15090)
trou60-trou72: offset pressure angle, gear module, min teeth, gear fatigue, wear rate, lubrication, hole compensation, horizontal hole, press-fit, motor protection, battery, shaft deflection (v2), infill

---

## 🔢 SAFETY CONSTANTS — L8692-8870

### Dimensions imprimante
| Constante | Valeur | Usage |
|-----------|--------|-------|
| printer_build_volume_mm | 220×220×250 | Ender-3 / Prusa MK3 |
| nozzle_diameter_mm | 0.4 | Standard |
| layer_height_mm | 0.2 | Standard |

### Clearances critiques
| Constante | Valeur | Usage |
|-----------|--------|-------|
| clearance_tight_mm | 0.1 | Ajustement serré |
| clearance_free_mm | 0.2 | Ajustement libre |
| clearance_running_mm | 0.4 | Pivots |
| clearance_dynamic_mm | 0.8 | Pièces mobiles |

### Arbre & came
| Constante | Valeur | Usage |
|-----------|--------|-------|
| shaft_diameter_default_mm | 4.0 | Défaut (auto → 6.0 si >5 cams) |
| shaft_deflection_toy_mm | 0.30 | Seuil flèche jouet |
| shaft_max_span_no_mid | 65.0 | Span sans palier (ancien, R6 utilise 180) |
| cam_z_pitch_fixed_mm | 8.0 | Défaut (auto → 6.0 si >6 cams) |
| phi_max_translating_deg | 30.0 | Angle pression max |
| cam_Rb_max_no_lever_mm | 35.0 | Rayon base max sans levier |

### Moteur
| Constante | Valeur | Usage |
|-----------|--------|-------|
| motor_stall_torque_mNm | 150 | N20 100:1 défaut (auto → 200/300) |
| safety_factor | 0.6 | 60% du stall = safe continu |
| motor_exploit_ratio_stall | 0.25 | Ratio exploitation nominal |

### Matériaux PLA
| Constante | Valeur | Usage |
|-----------|--------|-------|
| pla_modulus_gpa | 3.5 | Young's modulus |
| pla_tensile_mpa | 50 | Résistance traction |
| pla_compressive_mpa | 60 | Résistance compression |
| pla_cof_static_vs_steel | 0.30 | Friction statique |

---

## 🌳 ARBRE DE DÉCISION DEBUG

```
PROBLÈME ?
│
├── 🔴 CRASH / ERREUR
│   ├── "AutomataScene has no attribute" → scene_builder.py (make_automaton)
│   ├── "generate() failed" → L7561 AutomataGenerator.generate()
│   ├── "compile_scene_to_cams" → L5378 AutomataScene.compile_cam_program()
│   └── "Violation / constraint" → run_all_constraints() L16000+
│
├── 🟡 COLLISION SPATIALE
│   ├── wall∩follower_guide → L7830 guide X positioning
│   │   └── Vérifier: _wall_extent = max(wall_t, 2*boss_r)    L7838
│   ├── guide∩guide → L7850 auto-expand chassis
│   │   └── Vérifier: _min_gap = _guide_total + 1.0           L7854
│   ├── motor_mount∩mid_bearing → L4532 skip_pairs
│   │   └── Ajouter paire si nouveau type de collision attendue
│   └── camshaft_bracket∩camshaft → skip_pairs L4512
│
├── 🟡 SHAFT_DEFLECTION_TOO_HIGH
│   ├── Ø arbre ? → L7663 (auto Ø6 si >5 cams)
│   ├── Mid-bearing ? → L7870 (auto si shaft > 180mm)
│   ├── Span effectif ? → L3757 (÷2 si mid-bearing)
│   └── Charge par came ? → L3739 (1.5N par défaut)
│
├── 🟡 PLATE_OVERSIZED_XY
│   ├── Quelle pièce ? → L13930 check_trou57
│   ├── C'est le camshaft ? → FAUX POSITIF (acier, pas imprimé)
│   │   └── Vérifier filtre L3778 _non_printed
│   └── Pièce imprimée ? → Réduire dimensions ou split
│
├── 🟡 MOTOR_OVERLOADED (DANGER)
│   ├── Combien de cames ? → n_cams
│   │   ├── >8 → devrait être N20 298:1 (L7621)
│   │   ├── >6 → devrait être N20 150:1 (L7626)
│   │   └── ≤6 → N20 100:1 (défaut 150 mN·m stall)
│   ├── Peak torque ? → L7618 opt_peak
│   ├── Safe = stall × 0.6 → L881
│   └── Optimisation phases ? → L555 optimize_phases()
│
├── 🟡 CAM_ROLLER_LARGE (rf/Rb > ratio)
│   ├── Rb trop petit ? → L7634 pre-compute Rb_min
│   └── Ratio cap ? → chercher "roller_ratio" ou "0.30"
│
├── 🟡 PRESSURE_ANGLE > 30°
│   ├── Rb_min ? → compute_Rb_min_translating_roller
│   ├── Amplitude trop grande ? → cam.segments[].height
│   └── Levier nécessaire ? → cd['lever_needed']
│
├── 🟢 REGRESSION TEST FAIL
│   ├── Preset (9) → regression_test.py BASELINES L18-26
│   ├── Dynamic (17) → regression_test_dynamic.py DYNAMIC_BASELINES L7-24
│   ├── Debug (13) → debug_bugs.py
│   └── Part count changed ? → Mettre à jour baseline si justifié
│
└── 🟢 NOUVEAU TEMPLATE / ESPÈCE
    ├── scene_builder.py → make_automaton() dispatch
    ├── living_beings_db.py → species database (118 entries)
    └── animal_db.py → template mapping
```

---

## 📂 FICHIERS DU PROJET

| Fichier | Lignes | Rôle |
|---------|--------|------|
| automata_unified_v4.py | 18615 | Code principal (tout) |
| scene_builder.py | ~2800 | make_automaton() + SceneBuilder |
| living_beings_db.py | ~2000 | Database 118 espèces |
| animal_db.py | ~600 | Template animal → motions |
| regression_test.py | ~150 | 9 presets regression |
| regression_test_dynamic.py | ~80 | 17 dynamic regression |
| debug_bugs.py | ~500 | 13 bug-specific tests |

---

## 🔗 RÉFÉRENCES CROISÉES

| Concept | Défini à | Utilisé à | Modifié par |
|---------|----------|-----------|-------------|
| camshaft_diameter | L1568 (ChassisConfig) | L7663, L1782, L2002 | R1 auto Ø6mm |
| cam_spacing | L1568 (ChassisConfig) | L7668, L1595 | R2 auto 6mm |
| motor_stall_torque | L5376 (AutomataScene) | L7620, L875 | R3/R4 auto-upgrade |
| chassis width | L1568 (ChassisConfig) | L7850, L1741 | R5 auto-expand |
| mid_bearing_wall | L1854 (create_) | L7870, L4532, L3757 | R6 auto-add |
| shaft_deflection | L9754 (check_trou11) | L3742 | R7 span/2 |
| _non_printed | L3778 | L3781, L4491, L4495 | F1/F2 filter |
| skip_pairs | L4506 | L4558 | F3/F4 42 paires |

---

## 📜 HISTORIQUE SESSION 13 FÉVRIER

| Commit | Description | Impact |
|--------|-------------|--------|
| `b2d5a46` | Hertz/PV + BOM + PTC | HERTZ 16→0, BOM 9→0, FUSE 9→0 |
| `d8ae7f6` | CODEMAP_v4 | — |
| `820c93d` | Docs 17/17 | — |
| `1326b94` | Motor auto-upgrade | 14→17/17 |
| `b84ac1e` | Mid-bearing + print filter | 11→14/17 |
| `80140ea` | Deep research saved | — |
| `0865043` | Ø6mm + boss extent | 10→11/17 |
| `f946ed2` | BUG-010 collisions | 2→10/17 |
| `7418f59` | CAM_ROLLER ratio | — |
| `521e5b7` | P0 crash fix | — |
