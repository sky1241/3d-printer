# 🐛 BUG TRACKER v2 — Automata Generator v4
# Dernière mise à jour : 13 février 2026
# Commit actuel : 0865043
# Tests : 17/17 builders ✅ | 9/9 presets ✅ | 13/13 debug ✅

---

## LÉGENDE
- ✅ CORRIGÉ — Vérifié par tests, pushé
- 🔴 OUVERT — À fixer (nécessite dual-shaft = deep research)
- ⬜ FUTUR — Phase ultérieure

---

## 🔴 BUGS OUVERTS — Nécessitent DUAL-SHAFT (deep research)

### BUG-012 : PLATE_OVERSIZED_XY — arbre trop long (6/17)
- **Impact** : spider(255mm), scorpion(316mm), crab(241mm), lobster(262mm), octopus(234mm), dragon(289mm)
- **Seuil** : 220mm (lit Ender-3)
- **Fix** : Dual-shaft split avec engrenage sync → DEEP RESEARCH
- **Note** : cam_spacing déjà réduit de 8→6mm pour >6 cames

### BUG-011 : SHAFT_DEFLECTION_TOO_HIGH (3/17)
- **Impact** : scorpion(0.48mm), lobster(0.34mm), dragon(0.43mm)
- **Seuil** : 0.3mm
- **Note** : Ø6mm auto-scale a fixé 8 espèces, les 3 restantes ont trop de cames
- **Fix** : Dual-shaft split (même fix que BUG-012)

### BUG-013 : MOTOR_OVERLOADED (3/17)
- **Impact** : scorpion(-40.8%), lobster(-19.2%), crab(-8.3%)
- **Note** : Couple dominé par spring_force constante (pas amplitude)
- **Fix** : Dual-shaft split le couple en 2 moteurs

---

## ✅ BUGS CORRIGÉS — Session 13 février 2026

| Bug | Description | Fix | Commit |
|-----|-------------|-----|--------|
| BUG-015 | Wall boss extent miscalculated → collisions reviennent avec Ø6mm | 2×boss_r au lieu de wall_thickness | `0865043` |
| BUG-010 | wall∩follower COLLISION 13/17 espèces | Guide spacing dans zone utile + auto-expand | `f946ed2` |
| BUG-009 | CAM_ROLLER_LARGE rf/Rb>0.35 | ratio 0.30, floor Rb | `7418f59` |
| BUG-008 | run_all_constraints crash AutomataScene | isinstance check | `521e5b7` |
| BUG-007 | A1_STRICT murs U-slots | CSG boolean | `1601960` |
| BUG-006 | Cames Rb>50mm | Cap + binary search | `0872f00` |
| BUG-005 | Leviers manquants | ALL lever_needed | `c33b092` |
| BUG-004 | Dead code snap | UNUSED tag | `bcb829f` |
| BUG-003 | Gap came→levier 1.5mm | +0.2mm FDM | `42b9af7` |
| BUG-002 | Figurine détachée | Pushrod+socket | `41162e6` |
| BUG-001 | Follower guide = box | U-channel OK | 🟡 Reclassé |
| Z-AXIS | Cames/murs/followers désalignés | Rotation+translation | Multiple |
| AUTO-1 | Shaft Ø4mm trop flexible >5 cames | Auto Ø6mm | `0865043` |
| AUTO-2 | Cam spacing trop large >6 cames | Auto 8→6mm | `0865043` |

---

## 📊 MATRICE ESPÈCE × ÉTAT

| Espèce | Parts | Shaft | Status |
|--------|-------|-------|--------|
| sunflower | 13 | Ø4mm | ✅ CLEAN |
| snake | 20 | Ø4mm | ✅ CLEAN |
| dolphin | 27 | Ø4mm | ✅ CLEAN |
| butterfly | 27 | Ø4mm | ✅ CLEAN |
| eagle | 34 | Ø4mm | ✅ CLEAN |
| centipede | 34 | Ø6mm | ✅ CLEAN |
| snail | 34 | Ø4mm | ✅ CLEAN |
| human | 41 | Ø4mm | ✅ CLEAN |
| t-rex | 41 | Ø6mm | ✅ CLEAN |
| chat | 48 | Ø6mm | ✅ CLEAN |
| ant | 55 | Ø6mm | ✅ CLEAN |
| octopus | 62 | Ø6mm | ❌ OVERSIZED |
| spider | 69 | Ø6mm | ❌ OVERSIZED |
| dragon | 69 | Ø6mm | ❌ SHAFT+OVER |
| crab | 76 | Ø6mm | ❌ OVER+MOTOR |
| lobster | 83 | Ø6mm | ❌ SHAFT+OVER+MOTOR |
| scorpion | 97 | Ø6mm | ❌ SHAFT+OVER+MOTOR |

**Score : 11/17 clean (65%) — was 2/17 (12%)**

---

## ⬜ AMÉLIORATIONS FUTURES

| ID | Description | Bloqué par |
|----|-------------|------------|
| FUTUR-001 | Dual-shaft >6 cames | Deep research |
| FUTUR-002 | Engrenages imprimés | Deep research |
| FUTUR-003 | Simulation cinématique | — |
| FUTUR-004 | STL export par espèce | — |
| FUTUR-005 | Instructions assemblage PDF | — |
| FUTUR-006 | BOM complet | — |
