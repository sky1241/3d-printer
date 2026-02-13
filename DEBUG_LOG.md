# 🔍 DEBUG LOG — Automata Generator v4
# Pattern: fix → test → push → update ce fichier
# Dernière mise à jour: 13 février 2026
# Commit: 7418f59

---

## ÉTAT ACTUEL — post-session 13 fév

```
17/17 dynamic builders: ✅ ALL PASS (0 crash, all watertight)
9/9 preset regression:  ✅ ALL PASS
13/13 debug_bugs:       ✅ ALL PASS (A1+A1_STRICT included)
94/94 master tests:     ✅ ALL PASS
49/49 scene_builder:    ✅ ALL PASS
20/20 living_beings:    ✅ ALL PASS
```

### Détail par espèce (17 builders dynamiques)

| Espèce | Parts | WT | Violations assemblage | Constraint errors |
|--------|-------|-----|----------------------|-------------------|
| sunflower | 13 | 13 | 0 | 0 |
| snake | 20 | 20 | 0 | 0 |
| dolphin | 27 | 27 | 2 (collision) | 0 |
| butterfly | 27 | 27 | 0 | 3 (shaft+plate+integration) |
| eagle | 34 | 34 | 1 (dim-print) | 3 (shaft+plate+integration) |
| centipede | 34 | 34 | 2 (collision) | 0 |
| snail | 34 | 34 | 4 (collision) | 0 |
| human | 41 | 41 | 2 (collision) | 0 |
| t-rex | 41 | 41 | 2 (collision) | 3 (shaft+plate+integration) |
| chat | 48 | 48 | 2 (collision) | 3 (shaft+plate+integration) |
| ant | 55 | 55 | 2 (collision) | 3 (shaft+plate+integration) |
| octopus | 62 | 62 | 3 (collision+dim) | 3 (shaft+plate+integration) |
| spider | 69 | 69 | 3 (collision+dim) | 3 (shaft+plate+integration) |
| dragon | 69 | 69 | 3 (collision+dim) | 3 (shaft+plate+integration) |
| crab | 76 | 76 | 5 (collision+dim) | 3 (shaft+plate+integration) |
| lobster | 83 | 83 | 4 (collision+dim) | 3 (shaft+plate+integration) |
| scorpion | 97 | 97 | 3 (collision+dim) | 4 (shaft+plate+too_many+integration) |

---

## HISTORIQUE COMPLET DES PUSHES

### Session 13 février 2026 — Audit + Fixes

| # | Commit | Description | Régression | Résultat |
|---|--------|-------------|------------|----------|
| 28 | `7418f59` | FIX: CAM_ROLLER_LARGE — ratio ≤ 0.27 | ✅ | 17/17 + 9/9 |
| 27 | `521e5b7` | P0-FIX: run_all_constraints(AutomataScene) | ✅ | 17/17 + 9/9 |
| 26 | `f6153d3` | fix P0+CAM: 17 builders + Rb cap 50mm | ✅ | 17/17 + 9/9 |
| 25 | `0872f00` | fix CAM-1: Rb_max=50mm + binary search | ✅ | 9/9 |
| 24 | `1601960` | fix A1_STRICT: through-bores euler=0 | ✅ | 9/9 |
| 23 | `a930f82` | fix P0: run_all_constraints(Generator) | ✅ | 9/9 |
| 22 | `b20bdab` | docs: ROADMAP audit complet | ✅ | — |
| 21 | `e75cac6` | fix: levers + scale + pushrod + baselines | ✅ | 9/9 |

### Session 12 février — Blocs + Integration

| # | Commit | Description |
|---|--------|-------------|
| 20 | `f1efb7a` | BLOC-4: scene_builder v2 — 17 templates |
| 19 | `90fb493` | BLOC-3: living_beings_db — 118 espèces |
| 18 | `2641828` | BLOC-2: scene_builder.py — make_automaton() |
| 17 | `e286291` | BLOC-1: animal_db.py — 33 espèces, allométrie |

### Sessions 10-11 — Constraint Engine

| # | Commit | Description |
|---|--------|-------------|
| 16 | `1e43980` | P12: exotics + remaining (77/94) |
| 15 | `bc7a69e` | P11: physics + trou18/23 (59/94) |
| 14 | `652e86f` | P10: 8 more checks (51/94) |
| 13 | `83a962a` | P9: 6 dead-code checks (43/94) |
| 12 | `c532b2c` | P8: follower reach |
| 11 | `4e74d0a` | P7: lever brackets |
| 10 | `3092d45` | P6b: 11 more checks (37/94) |
| 9 | `83e1c68` | P6: 15 checks (26/94) |
| 8 | `d0c78b5` | P5: lever arms |
| 7 | `8998ac1` | P4: U-slot bore |
| 6 | `a2c047e` | P3: STL validation |

---

## BUGS FIXÉS — RÉSUMÉ

| ID | Bug | Fix | Impact |
|----|-----|-----|--------|
| BUG-009 | CAM_ROLLER_LARGE | ratio→0.30, floor Rb | 17/17 clean |
| BUG-008 | run_all_constraints crash | isinstance check | 17/17 pipeline |
| BUG-007 | A1_STRICT U-slots | CSG boolean | 17/17 euler=0 |
| BUG-006 | Rb>50mm | cap + binary search | 0 oversized |
| BUG-005 | Leviers manquants | ALL lever_needed | 13/13 leviers |
| BUG-004 | Dead code snap | UNUSED tag | Clean |
| BUG-003 | Gap came→levier | +0.2mm | 0.2mm FDM |
| BUG-002 | Figurine détachée | Pushrod+socket | 13/13 |
| Z-AXIS | Cames/murs/followers désalignés | Rotation+translation | 17/17 OK |

## BUGS OUVERTS

| ID | Bug | Espèces | Priorité |
|----|-----|---------|----------|
| BUG-010 | wall∩follower COLLISION | 13/17 | P1 — PROCHAIN |
| BUG-011 | SHAFT_DEFLECTION | 11/17 | P1 |
| BUG-012 | CAMSHAFT_OVERSIZED | 11/17 | P1 |
| BUG-013 | MOTOR_OVERLOADED | 3/17 | P2 |
| BUG-014 | TOO_MANY_CAMS | 1/17 | P2 |

---

## PATTERN DE TRAVAIL

```
1. Identifier le bug (audit ou rapport utilisateur)
2. Fix dans automata_unified_v4.py
3. python3 regression_test.py && python3 regression_test_dynamic.py
4. Si OK → git add + commit + push
5. Si REGRESSION → git checkout -- . (rollback)
6. Mettre à jour BUG_TRACKER_v2.md + DEBUG_LOG.md + ROADMAP.md
```
