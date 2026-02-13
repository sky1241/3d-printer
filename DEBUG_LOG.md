# 🔍 DEBUG LOG — Automata Generator v4
# Dernière mise à jour: 13 février 2026
# Commit: 0865043

---

## ÉTAT ACTUEL

```
9/9 preset regression:  ✅ ALL PASS
17/17 dynamic builders: ✅ ALL PASS (0 crash, all watertight)
13/13 debug_bugs:       ✅ ALL PASS
94/94 master tests:     ✅ ALL PASS
Espèces clean:          11/17 (65%)
Collisions spatiales:   0/17
```

### Espèces par état

| État | Espèces |
|------|---------|
| ✅ CLEAN (11) | sunflower, snake, dolphin, butterfly, eagle, centipede, snail, human, t-rex, chat, ant |
| ❌ OVERSIZED seulement (2) | octopus, spider |
| ❌ SHAFT+OVER (1) | dragon |
| ❌ OVER+MOTOR (1) | crab |
| ❌ SHAFT+OVER+MOTOR (2) | lobster, scorpion |

---

## BUGS FIXÉS CETTE SESSION

| # | Commit | Bug | Impact |
|---|--------|-----|--------|
| 30 | `0865043` | Auto Ø6mm + boss extent → 11/17 clean | +9 espèces clean |
| 29 | `f946ed2` | wall∩follower collisions éliminées | 13→0 collisions |
| 28 | `a7de852` | docs tracking update | — |
| 27 | `7418f59` | CAM_ROLLER ratio ≤0.27 | 17/17 ratio OK |
| 26 | `521e5b7` | run_all_constraints(AutomataScene) | 17/17 pipeline OK |
| 25 | `4d0aa53` | Deep research prompt v3 | — |
| 24 | `c20b395` | docs tracking update | — |

## PROGRESSION CLEAN

```
Début session:  2/17 clean (12%)  → sunflower, snake
Après BUG-010: 10/17 clean (59%) → +dolphin, butterfly, eagle, centipede, snail, human, t-rex, chat
Après Ø6mm:    11/17 clean (65%) → +ant
```

## PATTERN DE TRAVAIL

```
1. Identifier le bug (audit)
2. Fix dans automata_unified_v4.py  
3. python3 regression_test.py
4. python3 regression_test_dynamic.py
5. python3 debug_bugs.py
6. Si triple vert → git add + commit + push
7. Mettre à jour BUG_TRACKER_v2.md + ROADMAP.md + DEBUG_LOG.md
```
