# 🐛 BUG TRACKER v2 — Automata Generator v4
# Dernière mise à jour : 13 février 2026
# Commit: 1326b94
# 🎉 17/17 ESPÈCES CLEAN — ZÉRO BUGS OUVERTS

---

## ✅ TOUS LES BUGS CORRIGÉS

| Bug | Description | Fix | Commit |
|-----|-------------|-----|--------|
| BUG-013 | MOTOR_OVERLOADED 3/17 | Auto-upgrade N20 298:1 pour >8 cames | `1326b94` |
| BUG-012 | PLATE_OVERSIZED 6/17 | Exclu camshaft (acier) du check print | `b84ac1e` |
| BUG-011 | SHAFT_DEFLECTION 3/17 | Mid-bearing auto + Ø6mm + span/2 | `b84ac1e` |
| BUG-010 | wall∩follower 13/17 | Guide spacing zone utile + auto-expand | `f946ed2` |
| BUG-015 | Boss extent Ø6mm | 2×boss_r au lieu de wall_thickness | `0865043` |
| AUTO-1 | Shaft Ø4mm flexible | Auto Ø6mm >5 cames | `0865043` |
| AUTO-2 | Cam spacing large | Auto 8→6mm >6 cames | `0865043` |
| BUG-009 | CAM_ROLLER ratio | ratio ≤0.27 | `7418f59` |
| BUG-008 | run_all crash | isinstance check | `521e5b7` |
| BUG-007 | A1_STRICT U-slots | CSG boolean | `1601960` |
| BUG-006 | Cames Rb>50mm | Cap + binary search | `0872f00` |
| BUG-005 | Leviers manquants | ALL lever_needed | `c33b092` |
| BUG-004 | Dead code snap | UNUSED tag | `bcb829f` |
| BUG-003 | Gap came→levier | +0.2mm FDM | `42b9af7` |
| BUG-002 | Figurine détachée | Pushrod+socket | `41162e6` |

---

## 📊 MATRICE 17/17 — TOUT VERT

| Espèce | Parts | Shaft | Motor | Mid-bearing | Status |
|--------|-------|-------|-------|-------------|--------|
| sunflower | 13 | Ø4mm | N20 100:1 | — | ✅ |
| snake | 20 | Ø4mm | N20 100:1 | — | ✅ |
| dolphin | 27 | Ø4mm | N20 100:1 | — | ✅ |
| butterfly | 27 | Ø4mm | N20 100:1 | — | ✅ |
| eagle | 34 | Ø4mm | N20 100:1 | — | ✅ |
| centipede | 34 | Ø6mm | N20 150:1 | — | ✅ |
| snail | 34 | Ø4mm | N20 100:1 | — | ✅ |
| human | 41 | Ø4mm | N20 100:1 | — | ✅ |
| t-rex | 41 | Ø6mm | N20 150:1 | — | ✅ |
| chat | 48 | Ø6mm | N20 150:1 | — | ✅ |
| ant | 56 | Ø6mm | N20 150:1 | +MID | ✅ |
| octopus | 63 | Ø6mm | N20 150:1 | +MID | ✅ |
| spider | 70 | Ø6mm | N20 298:1 | +MID | ✅ |
| dragon | 70 | Ø6mm | N20 298:1 | +MID | ✅ |
| crab | 77 | Ø6mm | N20 298:1 | +MID | ✅ |
| lobster | 84 | Ø6mm | N20 298:1 | +MID | ✅ |
| scorpion | 98 | Ø6mm | N20 298:1 | +MID | ✅ |

---

## 📈 PROGRESSION SESSION 13 FÉVRIER

```
Début:     2/17 clean  (12%)
BUG-010:  10/17 clean  (59%)  — collisions éliminées
Ø6mm:     11/17 clean  (65%)  — deflection fixée
Mid-bear: 14/17 clean  (82%)  — false positives + deflection
Motor:    17/17 clean (100%)  — auto-upgrade moteur
```
