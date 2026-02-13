# 🔩 ROADMAP — ÉTAT RÉEL DU PROJET

> Dernière mise à jour: 2026-02-13
> Audit complet sur les 17 builders × 118 espèces

---

## 📊 ÉTAT DES LIEUX

### Ce qui MARCHE ✅
- 17 templates de génération (quadruped, biped, flapper, snake, swimmer, insect_6leg, insect_fly, arachnid, scorpion, crab, lobster, myriapod, octopus, snail, plant, dino_biped, dragon)
- 118 espèces dans la DB (animaux, insectes, fantasy, plantes)
- `make_automaton("chat")` → scène complète pour N'IMPORTE QUEL animal
- 17/17 builders génèrent sans crash, toutes pièces watertight
- Chaîne cinématique came→levier→pushrod→figurine fonctionnelle
- Moteur de contraintes (95 checks définis)
- Site web + Flask UI + Export STL
- 94/94 tests master, 49/49 scene_builder, 20/20 living_beings

### Ce qui est CASSÉ 🔴

**BUG P0: `run_all_constraints(gen)` crash sur make_automaton()**
- Les 9 presets hardcodés passent → mais `make_automaton("chat")` crash
- `'AutomataGenerator' object has no attribute 'get'`
- **AUCUN des 17 builders dynamiques n'est validé mécaniquement**

**COUVERTURE: 4/17 builders testés (23%)**
- Testés: quadruped, biped, flapper, swimmer
- ZÉRO coverage: snake, insect_6leg, insect_fly, arachnid, scorpion, crab, lobster, myriapod, octopus, snail, plant, dino_biped, dragon

**PROBLÈMES MÉCANIQUES (détectés sur les 17 builders):**

| Animal | Pièces | Status |
|--------|--------|--------|
| chat, human, eagle, snake, dolphin, ant, butterfly, centipede, sunflower, t-rex, snail | 13-55 | ✅ 0 erreurs |
| spider (69p), octopus (62p) | 62-69 | 🔴 Shaft deflection |
| crab (76p) | 76 | 🔴 Shaft + camshaft 222mm + motor -8% |
| lobster (83p) | 83 | 🔴 Shaft + camshaft 251mm + motor -19% |
| scorpion (97p) | 97 | 🔴 13 cames, shaft 2.3mm, 293mm, motor -40% |
| dragon (69p) | 69 | 🔴 Shaft 1.7mm + camshaft 310mm |

**BUGS SYSTÉMIQUES:**
1. SHAFT_DEFLECTION — arbre trop flexible quand >6 cames
2. CAMSHAFT_OVERSIZED — arbre trop long pour Ender-3 220mm
3. MOTOR_TORQUE — moteur insuffisant pour gros animaux
4. TOO_MANY_CAMS — scorpion 13 cames > max 12
5. ASSEMBLY_COLLISIONS — wall∩follower_guide partout (SPATIAL-1..4)
6. 47/95 contraintes mortes (jamais appelées)
7. A1_STRICT — murs U-slots au lieu de vrais trous
8. Cames surdimensionnées (waving_cat 141mm, blacksmith 125mm)
9. CAM_ROLLER_LARGE — r_galet/Rb > 0.35 sur TOUS les presets

---

## 🎯 PLAN D'ACTION

### P0 — BLOQUANT
- [ ] FIX `run_all_constraints()` pour accepter les builds dynamiques
- [ ] Étendre regression à 17 builders (1 animal par template)

### P1 — MÉCANIQUE
- [ ] DUAL-SHAFT pour >6 cames (engrenage sync) → **DEEP RESEARCH NÉCESSAIRE**
- [ ] MOTOR AUTO-SCALE: réduire amplitudes si torque > seuil
- [ ] SPATIAL FIX: décaler followers pour éviter collisions murs

### P2 — QUALITÉ
- [ ] A1_STRICT: vrais trous dans murs (boolean CSG)
- [ ] Capper Rb_max pendant auto-design came
- [ ] Activer les 47 checks morts
- [ ] Fix CAM_ROLLER_LARGE ratio

### P3 — FINITION
- [ ] STL Export pour les 17 builders
- [ ] Instructions assemblage PDF
- [ ] Profils slicer
- [ ] BOM complet

---

## 🔬 DEEP RESEARCH?

| Sujet | Research? | Raison |
|-------|-----------|--------|
| Dual-shaft >6 cames | **OUI** | Engrenages PLA imprimés, sync, tolérance |
| Tout le reste | NON | Bugs d'API, clamps, extensions de tests |

---

## 📈 MÉTRIQUES

```
Master tests:        94/94 ✅
Scene builder:       49/49 ✅
Living beings:       20/20 ✅
Regression:          9/9  ✅ (9 presets hardcodés seulement)
Debug:               12/13 ✅ (A1_STRICT seul failure)
Builders testés:     4/17 (23%)
Espèces testées:     9/118 (7.6%)
Constraint coverage: 48/95 (50.5%)
```
