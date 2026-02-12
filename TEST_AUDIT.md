# 🌲 ARBRE DE COUVERTURE DES TESTS — AUDIT COMPLET

**Date**: 2026-02-12  
**Version**: automata_unified_v4.py (post commit `e070cf7`)  
**Verdict**: ⚠️ Les 94 tests "passent" mais **45% des checks sont du dead code** et les données réelles du générateur ne sont que partiellement injectées dans le moteur de contraintes.

---

## 1. ARCHITECTURE DU SYSTÈME DE TEST

```
test_master()
├── Phase 1: Generator (3 presets)           → Teste que generate() ne crash pas
│   ├── nodding_bird ✅                       → Pas de validation du contenu
│   ├── flapping_bird ✅                      → Pas de validation du contenu
│   └── walking_figure ✅                     → Pas de validation du contenu
│
├── Phase 2: Constraint Engine (9 blocks)    → Tests unitaires sur données SYNTHÉTIQUES
│   ├── test_block1: Fondations (24 asserts) → Severity, Violation, dataclass
│   ├── test_block2: Méca T1-T12 (24 asserts, 24 check_ calls)
│   ├── test_block3: Fabri T13-T27 (37 asserts, 32 check_ calls)
│   ├── test_block4: Exotic+Phys (43 asserts, 27 check_ calls)
│   ├── test_block5: Cam avancé (10 asserts, 8 check_ calls)
│   ├── test_block6: Levier/Linkage (10 asserts, 8 check_ calls)
│   ├── test_block7: Thermal/Fatigue (9 asserts, 8 check_ calls)
│   ├── test_block8: Safety/Integ (10 asserts, 8 check_ calls)
│   └── test_block9: B9 checks (0 asserts! custom helper, 33 check_ calls)
│
├── Phase 3: Junction (Gen → Constraints)    → ⚠️ AUCUNE ASSERTION, print seulement
│   ├── extract_design_data(scene, result)   → Données partielles/hardcodées
│   └── run_all_constraints(data)            → 48/94 checks appelés, 42 ignorés
│
├── Phase 4: Debug Tree                      → Teste diagnose() string output
│   ├── diagnose(report) ✅
│   └── diagnose_error() × 3 ✅
│
└── Phase 5: Sanity                          → ⚠️ REGEX uniquement
    ├── count(class Severity) == 1
    ├── count(class Violation) == 1
    └── count(def check_*) >= 90             → COMPTE LE CODE MORT
```

---

## 2. 🔴 PROBLÈME CRITIQUE #1 : 42 checks JAMAIS APPELÉS

`run_all_constraints()` n'appelle que **52/94 checks** (55%). Les 42 restants existent comme fonctions mais ne sont **jamais exécutés** sur les données réelles du générateur.

### Checks appelés (52) ✅
| Bloc | Trous | Checks |
|------|-------|--------|
| B2 | T1-T12 | 12 checks mécaniques |
| B5 | T28-T35 | 8 checks cam avancé |
| B6 | T36-T43 | 8 checks levier/linkage |
| B7 | T44-T51 | 8 checks thermal/fatigue |
| B8 | T52-T59 | 8 checks safety/intégration |
| B9 | T60-T63 | 4 checks (offset, gear×3 — en boucle sur gears[]) |
| **Total** | | **48 uniques + boucles** |

### Checks DEAD CODE (42) 🔴
| Catégorie | Checks | Impact |
|-----------|--------|--------|
| **Trous 13-27** (15) | shaft_retention, component_retention, assembly_order, cam_phasing, startup_torque, stall_protection, manual_crank, power_supply, print_orientation, print_supports, print_estimate, calibration, modularity, safety, bom_quality | Fabrication et assemblage non validés |
| **Trous 64-72** (9) | wear_rate, lubrication, hole_compensation, horizontal_hole, press_fit, motor_protection, battery_autonomy, shaft_deflection_v2, infill | B9 avancé non validé |
| **Exotic cas101-110** (10) | rotation_pure, large_stroke, fast_motion, many_cams, compound_motion, intermittent, asymmetric, external_load, inverted, scale | Cas extrêmes non validés |
| **Physics e1-e8** (8) | friction_wear, fatigue_v2, vibrations, tolerances_v2, assembly_v2, hertz, backlash, follower_jump | Physique avancée non validée |

---

## 3. 🔴 PROBLÈME CRITIQUE #2 : extract_design_data() hardcode/manque des données

### Données MANQUANTES (checks passent sur liste vide = 0 violations)
| Champ | Checks impactés | Effet |
|-------|-----------------|-------|
| `linkages` | T38 Grashof, T39 transmission_angle | Passent car `[]` |
| `worm_gears` | T41 worm_gear | Passe car `[]` |
| `genevas` | T43 geneva_timing | Passe car `[]` |
| `sliders` | T40 crank_slider | Passe car `[]` |
| `environment` | T44 thermal, T51 degradation | Reçoivent `{}` → defaults safe |
| `holes` | T66-T68 hole_compensation | Dead code + vide |
| `cam_profiles` | B5 avancés | Toujours `[]` |

### Données HARDCODÉES (valeurs fausses)
| Champ | Valeur hardcodée | Valeur réelle | Impact |
|-------|-------------------|---------------|--------|
| `cam.roller_radius_mm` | `5` | `3.0` (rf dans auto_design_cam) | T33 roller_sizing faux |
| `cam.z_min/z_max` | `i * 12` | mesh.bounds Z réel | T1 collision fausse |
| `cam.Rb_mm` default | `20` | 5-22mm réel | T29 Rb_min faux si cam_designs manque |
| `lever.arm_mm` | `30` | Devrait venir de la géométrie | T37 bending faux |
| `lever.pivot_diameter_mm` | `4.0` | Devrait venir du chassis | T36 pivot faux |
| `lever.force_N` | `1.0` | Devrait être calculé | T5 torque sous-estimé |
| `shaft.retention` | `'e-clip'` | Jamais spécifié dans scene | T13 dead code anyway |
| `transmission.type` | `'worm'` | Pas de transmission worm | T41 faux positif |
| `figurine.mass_g` | `5.0` | Devrait venir de mesh.volume × densité | T6 gravity faux |

---

## 4. 🔴 PROBLÈME CRITIQUE #3 : Phase 3 Junction ne FAIL jamais

```python
# ACTUEL — ne fail JAMAIS
n_err = sum(1 for v in report.violations if v.severity == Severity.ERROR)
status = "✅" if n_err == 0 else "⚠"  # ← juste un emoji!
print(f"  {status} {name}: {n_err} errors")
# PAS D'ASSERTION → test_master continue même avec 7 erreurs
```

**Preuve**: nodding_bird génère **7 ERRORS** (pression angle, Rb trop petit, Hertz, etc.) et le test passe quand même.

---

## 5. 🔴 PROBLÈME CRITIQUE #4 : test_master ignore les return values

```python
# ACTUEL — ignore le retour
for name, fn in block_tests:
    try:
        fn()          # ← return value ignoré
        print(f"  ✅ {name} PASS")   # ← PASS si pas d'exception
    except Exception as e:
        print(f"  ❌ {name} FAIL: {e}")
        all_ok = False
```

Si `test_block9()` retourne `False` (tests internes échoués), test_master dit quand même ✅.

---

## 6. 🔴 PROBLÈME CRITIQUE #5 : Phase 5 Sanity inutile

```python
n_checks = len(re.findall(r'^def check_', content, re.MULTILINE))
print(f"{'✅' if n_checks >= 90 else '❌'} def check_*: {n_checks} (expected ≥90)")
```

Compte 94 fonctions `check_*` dans le **code source**. Ne vérifie pas :
- Combien sont appelées dans `run_all_constraints`
- Combien reçoivent des données réelles
- Combien produisent des résultats significatifs

---

## 7. ARBRE DE DÉPENDANCES : Generator → Constraints

```
AutomataGenerator.generate()
│
├── CamProfile objects ──────────────── ─┐
├── auto_design_cam() → CamDesignResult  │  extract_design_data()
├── Meshes (all_parts)                   ├──────────────────────────┐
├── timing_data                          │                          │
├── motor_check                          │                          ▼
└── scene (tracks, rpm, motor)       ────┘               run_all_constraints()
                                                          │
                    DONNÉES QUI PASSENT ✅                │  DONNÉES PERDUES 🔴
                    ─────────────────────                 │  ─────────────────
                    cam.name                              │  cam.roller_radius (hardcodé 5)
                    cam.lift_mm                           │  cam.z_min/z_max (hardcodé i*12)
                    cam.Rb_mm (si cam_designs)            │  lever.arm_mm (hardcodé 30)
                    cam.phi_max_deg (si cam_designs)      │  lever.force_N (hardcodé 1)
                    cam.segments                          │  figurine.mass_g (hardcodé 5)
                    timing.rpm                            │  shaft.retention (hardcodé e-clip)
                    timing.peak_torque                    │  transmission.type (hardcodé worm)
                    motor.stall_torque                    │  cam_profiles (toujours [])
                    parts (mesh metadata)                 │  linkages/genevas/sliders (MISSING)
                                                          │  environment (MISSING)
                                                          │  amp_scale/lever_needed (PERDU!)
```

---

## 8. PLAN DE CORRECTION — par priorité

### P0 — Corrections structurelles (test_master menteur)
| # | Action | Effort |
|---|--------|--------|
| P0-1 | Phase 3: `assert n_err == 0` ou whitelist des erreurs attendues | 5 min |
| P0-2 | test_master: vérifier return value des block tests | 5 min |
| P0-3 | Phase 5: compter checks APPELÉS dans runner, pas dans source | 10 min |

### P1 — Intégrer les 42 checks dead code dans run_all_constraints
| # | Action | Effort |
|---|--------|--------|
| P1-1 | Trous 13-27: ajouter appels dans runner | 30 min |
| P1-2 | Trous 64-72: ajouter appels dans runner | 20 min |
| P1-3 | Exotic cas101-110: ajouter appels + extract data | 40 min |
| P1-4 | Physics e1-e8: ajouter appels + extract data | 30 min |

### P2 — Corriger extract_design_data() (données fausses)
| # | Action | Effort |
|---|--------|--------|
| P2-1 | cam.roller_radius_mm ← rf réel (3.0) | 5 min |
| P2-2 | cam.z_min/z_max ← mesh bounds réels | 10 min |
| P2-3 | lever données ← calcul depuis géométrie | 20 min |
| P2-4 | figurine.mass_g ← mesh volume × densité PLA | 10 min |
| P2-5 | Peupler linkages/genevas/sliders si present dans scene | 15 min |
| P2-6 | environment ← defaults raisonnables | 5 min |
| P2-7 | amp_scale / lever_needed ← cam_designs metadata | 5 min |

### P3 — Faire passer les vrais tests
| # | Action | Effort |
|---|--------|--------|
| P3-1 | Résoudre les 7 erreurs de nodding_bird (Rb, φ_max, Hertz) | 30 min |
| P3-2 | Résoudre les erreurs des 8 autres presets | 60 min |
| P3-3 | Ajouter presets manquants dans Phase 1 (actuellement 3/9) | 10 min |

---

## 9. MÉTRIQUES DE COUVERTURE RÉELLE

| Métrique | Annoncé | Réel |
|----------|---------|------|
| "94 tests passent" | 94 | **52 checks appelés, 42 dead code** |
| "Toutes les contraintes validées" | 94 | **48 sur données réelles** |
| "Generator → Constraints junction" | ✅ | **Pas d'assertion, 7 erreurs ignorées** |
| "9 presets validés" | ✅ | **3 testés, contenu non validé** |
| "Données réelles" | ✅ | **12+ champs hardcodés** |

**Score de confiance réel : ~30%** — le système est une coquille qui donne l'illusion de validation sans vérifier les données critiques.
