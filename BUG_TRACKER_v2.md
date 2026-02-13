# 🐛 BUG TRACKER v2 — Automata Generator v4
# Dernière mise à jour : 13 février 2026
# Commit actuel : 7418f59
# Tests : 17/17 builders ✅ | 9/9 presets ✅ | 13/13 debug ✅

---

## LÉGENDE
- ✅ CORRIGÉ — Vérifié par tests, pushé
- 🟡 RECLASSÉ — Pas un vrai bug / fonctionnel
- 🔴 OUVERT — À fixer
- ⬜ FUTUR — Phase ultérieure

---

## 🔴 BUGS OUVERTS — Triés par impact

### BUG-010 : COLLISION wall∩follower_guide (13/17 espèces)
- **Sévérité** : P1
- **Impact** : chat, human, dolphin, ant, spider, scorpion, crab, lobster, centipede, octopus, snail, t-rex, dragon
- **Clean** : eagle, snake, butterfly, sunflower (4/17)
- **Cause** : Les follower_guides sont placés trop près des murs. Le décalage X ne tient pas compte de la largeur du guide.
- **Fix proposé** : Décaler le follower_guide de ±(wall_thickness + guide_width/2 + clearance)
- **Difficulté** : Moyenne — spatial placement dans generate()

### BUG-011 : SHAFT_DEFLECTION_TOO_HIGH (11/17 espèces)
- **Sévérité** : P1
- **Impact** : chat, eagle, ant, butterfly, spider, scorpion, crab, lobster, octopus, t-rex, dragon
- **Clean** : human, snake, dolphin, centipede, snail, sunflower (6/17)
- **Cause** : Arbre Ø4mm trop flexible quand longueur > 150mm. Flèche max: 7.3mm (scorpion)
- **Fix** : Dual-shaft (>6 cames), palier intermédiaire, ou arbre Ø6mm
- **Difficulté** : Haute — nécessite deep research (engrenages PLA sync)

### BUG-012 : PLATE_OVERSIZED_XY — camshaft trop long (11/17)
- **Sévérité** : P1
- **Impact** : Même 11 espèces que BUG-011 (même root cause)
- **Pires cas** : dragon 491mm, scorpion 434mm, lobster 371mm (lit=220mm)
- **Cause** : Toutes les cames sur 1 seul arbre = longueur ∝ nombre de cames
- **Fix** : Dual-shaft split ou réduction du cam_spacing
- **Difficulté** : Haute — lié à BUG-011

### BUG-013 : MOTOR_OVERLOADED (3/17 espèces)
- **Sévérité** : P2
- **Impact** : scorpion (-40.8%), lobster (-19.2%), crab (-8.3%)
- **Cause** : Trop de cames simultanées > couple moteur 90mN·m
- **Fix** : Motor auto-scale (réduire amplitudes) ou réduction engrenage
- **Difficulté** : Moyenne

### BUG-014 : TOO_MANY_CAMS (1/17)
- **Sévérité** : P2
- **Impact** : scorpion (13 cames > max 12)
- **Fix** : Regrouper mouvements ou dual-shaft
- **Difficulté** : Liée à BUG-011

---

## ✅ BUGS CORRIGÉS — 13 février 2026

| Bug | Description | Fix | Commit | Vérification |
|-----|-------------|-----|--------|--------------|
| BUG-009 | CAM_ROLLER_LARGE rf/Rb>0.35 TOUTES espèces | ratio 0.38→0.30, floor Rb≥rf/0.35 | `7418f59` | ✅ 0 warnings, ratio=0.27 |
| BUG-008 | run_all_constraints() crash AutomataScene | isinstance(AutomataScene) check | `521e5b7` | ✅ 17/17 builders |
| BUG-007 | A1_STRICT murs U-slots au lieu de through-bores | Boolean CSG subtraction | `1601960` | ✅ euler=0 partout |
| BUG-006 | Cames oversized Rb>50mm | Cap Rb_max=50mm + binary search | `0872f00` | ✅ 0 Rb>50mm |

## ✅ BUGS CORRIGÉS — Sessions précédentes

| Bug | Description | Fix | Commit |
|-----|-------------|-----|--------|
| BUG-005 | Leviers manquants | create_lever ALL lever_needed | `c33b092` |
| BUG-004 | Dead code snap functions | Marquées UNUSED | `bcb829f` |
| BUG-003 | Gap came→levier 1.5mm | pivot_z +0.2mm FDM | `42b9af7` |
| BUG-002 | Figurine pas attachée | Pushrod+socket | `41162e6` |
| BUG-001 | Follower guide = box | U-channel OK | 🟡 Pas un bug |
| Z-AXIS | Cames Z=0 / murs inversés Y↔Z | Rotation+translation | Multiple ✅ |

---

## 📊 MATRICE ESPÈCE × BUG

| Espèce | Parts | Collision | Shaft | Oversized | Motor | Clean? |
|--------|-------|-----------|-------|-----------|-------|--------|
| sunflower | 13 | — | — | — | — | ✅ |
| snake | 20 | — | — | — | — | ✅ |
| butterfly | 27 | — | ⚠ | ⚠ | — | ❌ |
| eagle | 34 | — | ⚠ | ⚠ | — | ❌ |
| dolphin | 27 | ⚠ | — | — | — | ❌ |
| centipede | 34 | ⚠ | — | — | — | ❌ |
| snail | 34 | ⚠ | — | — | — | ❌ |
| human | 41 | ⚠ | — | — | — | ❌ |
| t-rex | 41 | ⚠ | ⚠ | ⚠ | — | ❌ |
| chat | 48 | ⚠ | ⚠ | ⚠ | — | ❌ |
| ant | 55 | ⚠ | ⚠ | ⚠ | — | ❌ |
| octopus | 62 | ⚠ | ⚠ | ⚠ | — | ❌ |
| spider | 69 | ⚠ | ⚠ | ⚠ | — | ❌ |
| dragon | 69 | ⚠ | ⚠ | ⚠ | — | ❌ |
| crab | 76 | ⚠ | ⚠ | ⚠ | ⚠ | ❌ |
| lobster | 83 | ⚠ | ⚠ | ⚠ | ⚠ | ❌ |
| scorpion | 97 | ⚠ | ⚠ | ⚠ | ⚠ | ❌ |

**Score : 2/17 clean, 15/17 ont ≥1 bug ouvert**

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
