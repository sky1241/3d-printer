# 🔍 DEBUG LOG — Automata Generator v4
# Pattern: fix → test → push → update ce fichier
# Dernière mise à jour: 13 février 2026
# Commit: f946ed2

---

## ÉTAT ACTUEL

```
17/17 dynamic builders: ✅ ALL PASS
9/9 preset regression:  ✅ NO REGRESSION
13/13 debug_bugs:       ✅ ALL PASS
94/94 master tests:     ✅ ALL PASS
Espèces 100% clean:    7/17 (sunflower, snake, butterfly, eagle, human, centipede, chat)
```

---

## HISTORIQUE COMPLET DES PUSHES

### Session 13 février 2026

| # | Commit | Description | Résultat |
|---|--------|-------------|----------|
| 30 | `f946ed2` | FIX BUG-010: wall∩follower collisions (13→0) | 9/9 ✅ 17/17 ✅ 13/13 ✅ |
| 29 | `4d0aa53` | docs: prompt deep research v3 | — |
| 28 | `c20b395` | docs: tracking complet (9 fixés, 5 ouverts) | — |
| 27 | `7418f59` | FIX: CAM_ROLLER_LARGE ratio ≤ 0.27 | 9/9 ✅ 17/17 ✅ |
| 26 | `521e5b7` | P0-FIX: run_all_constraints(AutomataScene) | 17/17 ✅ |
| 25 | `f6153d3` | fix P0+CAM: 17 builders + Rb cap 50mm | 17/17 ✅ |
| 24 | `0872f00` | fix CAM-1: Rb_max=50mm + binary search | 9/9 ✅ |
| 23 | `1601960` | fix A1_STRICT: through-bores euler=0 | 9/9 ✅ |

### Sessions précédentes

| # | Commit | Description |
|---|--------|-------------|
| 22 | `a930f82` | fix P0: run_all_constraints(Generator) |
| 21 | `e75cac6` | fix: levers + scale + pushrod + baselines |
| 20 | `f1efb7a` | BLOC-4: scene_builder v2 — 17 templates |
| 19 | `90fb493` | BLOC-3: living_beings_db — 118 espèces |
| 18 | `2641828` | BLOC-2: scene_builder.py — make_automaton() |
| 17 | `e286291` | BLOC-1: animal_db.py — 33 espèces, allométrie |
| 16 | `1e43980` | P12: exotics + remaining (77/94) |
| 15 | `bc7a69e` | P11: physics (59/94) |
| 14 | `652e86f` | P10: 8 more checks (51/94) |
| 13 | `83a962a` | P9: 6 dead-code checks (43/94) |
| 1-12 | various | P1-P8: constraint engine build-out |

---

## BUGS FIXÉS vs OUVERTS

| ID | Bug | Status | Commit |
|----|-----|--------|--------|
| BUG-010 | wall∩follower COLLISION (13/17) | ✅ FIXÉ | `f946ed2` |
| BUG-009 | CAM_ROLLER_LARGE | ✅ FIXÉ | `7418f59` |
| BUG-008 | run_all_constraints crash | ✅ FIXÉ | `521e5b7` |
| BUG-007 | A1_STRICT U-slots | ✅ FIXÉ | `1601960` |
| BUG-006 | Rb>50mm | ✅ FIXÉ | `0872f00` |
| BUG-011 | SHAFT_DEFLECTION (7/17) | 🔴 OUVERT | Deep research |
| BUG-012 | PLATE_OVERSIZED (5/17) | 🔴 OUVERT | Deep research |
| BUG-013 | MOTOR_OVERLOADED (3/17) | 🔴 OUVERT | P2 |
| BUG-015 | guide∩pin/collar (5/17) | 🔴 OUVERT | P3 |

---

## PATTERN DE TRAVAIL

```
1. Fix dans automata_unified_v4.py
2. python3 regression_test.py        (9 presets)
3. python3 regression_test_dynamic.py (17 builders)
4. python3 debug_bugs.py             (13 tests)
5. Si TOUT OK → git add + commit + push
6. Mettre à jour BUG_TRACKER_v2.md + DEBUG_LOG.md + ROADMAP.md
```
