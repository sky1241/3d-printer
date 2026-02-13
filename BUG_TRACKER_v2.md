# 🐛 BUG TRACKER v2 — Automata Generator v4
# Dernière mise à jour : 13 février 2026
# Commit actuel : f946ed2
# Tests : 17/17 builders ✅ | 9/9 presets ✅ | 13/13 debug ✅

---

## LÉGENDE
- ✅ CORRIGÉ — Vérifié par tests, pushé
- 🔴 OUVERT — À fixer
- ⬜ FUTUR — Phase ultérieure

---

## 🔴 BUGS OUVERTS

### BUG-011 : SHAFT_DEFLECTION_TOO_HIGH (7/17 espèces)
- **Sévérité** : P1
- **Impact** : ant, spider, scorpion, crab, lobster, octopus, dragon
- **Cause** : Arbre Ø4mm trop flexible quand >6 cames. Flèche max: 7.3mm (scorpion)
- **Fix** : Dual-shaft ou arbre Ø6mm — **DEEP RESEARCH en cours**

### BUG-012 : PLATE_OVERSIZED_XY (5/17 espèces)
- **Sévérité** : P1
- **Impact** : spider, scorpion, crab, lobster, octopus, dragon
- **Pires cas** : dragon 332mm, scorpion 434mm (lit=220mm)
- **Fix** : Dual-shaft split — lié à BUG-011

### BUG-013 : MOTOR_OVERLOADED (3/17 espèces)
- **Sévérité** : P2
- **Impact** : scorpion (-40.8%), lobster (-19.2%), crab (-8.3%)
- **Fix** : Auto-réduction amplitudes ou engrenage réduction

### BUG-015 : COLLISION guide∩pin/collar (5/17 espèces)
- **Sévérité** : P3
- **Impact** : dolphin, crab, lobster, snail, t-rex
- **Cause** : Pins/collars (2-8mm) overlap léger avec guides
- **Fix** : Décaler pins ou réduire rayon collars

---

## ✅ BUGS CORRIGÉS

| Bug | Description | Fix | Commit | Impact |
|-----|-------------|-----|--------|--------|
| **BUG-010** | **wall∩follower COLLISION 13/17** | **Guides espacés dans zone utile X** | **`f946ed2`** | **13→0 collisions, 2→7 espèces clean** |
| BUG-009 | CAM_ROLLER_LARGE rf/Rb>0.35 | ratio→0.30, floor Rb≥rf/0.35 | `7418f59` | 17/17 clean |
| BUG-008 | run_all_constraints crash | isinstance check | `521e5b7` | 17/17 pipeline |
| BUG-007 | A1_STRICT U-slots | Boolean CSG | `1601960` | euler=0 |
| BUG-006 | Rb>50mm oversized | Cap 50mm + binary search | `0872f00` | 0 oversized |
| BUG-005 | Leviers manquants | ALL lever_needed | `c33b092` | 13/13 |
| BUG-004 | Dead code snap | UNUSED tag | `bcb829f` | Clean |
| BUG-003 | Gap came→levier | +0.2mm FDM | `42b9af7` | 0.2mm |
| BUG-002 | Figurine détachée | Pushrod+socket | `41162e6` | 13/13 |
| BUG-001 | Follower guide = box | U-channel OK | N/A | 🟡 |
| Z-AXIS | Cames/murs/followers | Rotation+translation | Multiple | 17/17 |

---

## 📊 MATRICE ESPÈCE × BUG (post BUG-010 fix)

| Espèce | Parts | Shaft | Plate | Motor | Minor | Clean? |
|--------|-------|-------|-------|-------|-------|--------|
| sunflower | 13 | — | — | — | — | ✅ |
| snake | 20 | — | — | — | — | ✅ |
| butterfly | 27 | — | — | — | — | ✅ |
| eagle | 34 | — | — | — | — | ✅ |
| human | 41 | — | — | — | — | ✅ |
| centipede | 34 | — | — | — | — | ✅ |
| chat | 48 | — | — | — | — | ✅ |
| dolphin | 27 | — | — | — | pin | ❌ |
| snail | 34 | — | — | — | pin | ❌ |
| t-rex | 41 | — | — | — | pin | ❌ |
| ant | 55 | ⚠ | — | — | — | ❌ |
| octopus | 62 | ⚠ | ⚠ | — | — | ❌ |
| spider | 69 | ⚠ | ⚠ | — | — | ❌ |
| dragon | 69 | ⚠ | ⚠ | — | — | ❌ |
| crab | 76 | ⚠ | ⚠ | ⚠ | pin | ❌ |
| lobster | 83 | ⚠ | ⚠ | ⚠ | pin | ❌ |
| scorpion | 97 | ⚠ | ⚠ | ⚠ | — | ❌ |

**Score : 7/17 clean (était 2/17)**

---

## ⬜ AMÉLIORATIONS FUTURES

| ID | Description | Difficulté |
|----|-------------|------------|
| FUTUR-001 | Bell-crank mouvement horizontal | Moyenne |
| FUTUR-002 | Engrenages imprimés rotation 360° | Haute |
| FUTUR-003 | Simulation cinématique 0→360° | Moyenne |
| FUTUR-004 | Scaling global 50-200% | Faible |
| FUTUR-005 | STL export par espèce | Faible |
| FUTUR-006 | Instructions assemblage PDF | Moyenne |
| FUTUR-007 | Profils slicer | Faible |
| FUTUR-008 | BOM complet | Faible |
