# 🎯 BATTLE PLAN — Automata Articulated Figurines
# Dernière mise à jour : 13 février 2026 (nuit)

---

## PHASE 1 — Pin Joints (COMPLÈTE ✅)

| Étape | Tâche | Status | Commit |
|-------|-------|--------|--------|
| 1 | Pin Joint Generator | ✅ | `b139e0f` |
| 2 | Body Splitter | ✅ | `f7976a9` |
| 3 | Joint + Split Combo | ✅ | `e06e8b3` |
| 4 | Pushrod Attach | ✅ | `9513f65` |
| 5 | Pushrod Router | ✅ | `0cb6165` |
| 6 | Turtle Simple Integration | ✅ | `7e440bd` |
| 7 | Turtle Walking + Fuzzy | ✅ | `43c1f51` |
| 8 | Généralisation 17 espèces | ✅ | (dans step 7) |
| 9 | Contraintes B10 | ✅ | `8001745` |

## PHASE 2 — Post-processing (COMPLÈTE ✅)

| Tâche | Status | Commit |
|-------|--------|--------|
| Collision fix (pushrod↔figurine) | ✅ | `ad321fa` |
| Assembly role annotations | ✅ | `2ff8b4c` |
| Return mechanism detection | ✅ | `4b6353f` |
| Codex audit SYS-001a→d | ✅ | `562c973`+`6514c98` |

## PHASE 3 — Joint Types (EN COURS 🔧)

| Tâche | Code | Pipeline | Tests |
|-------|------|----------|-------|
| Ball joint (rotule) | ✅ | ❌ pas intégré | ✅ isolé |
| Living hinge (charnière) | ✅ | ❌ pas intégré | ✅ isolé |
| Crank-slider (walking) | ❌ | ❌ | ❌ |

### Arbre de décision : quel joint utiliser ?

```
Joint sélection par mouvement:
│
├─ Rotation 1 axe (nod, flap, wag)
│   → PIN JOINT (Ø3-6mm, clearance 0.15mm)
│   → ✅ Implémenté, 100% automatique
│
├─ Rotation multi-axes (épaule, hanche libre)
│   → BALL JOINT (Ø6-10mm)
│   → ✅ Générateur prêt, pipeline TODO
│
├─ Flexion limitée <90° (mâchoire, nageoire, paupière)
│   → LIVING HINGE (0.4mm PLA, 20 cycles)
│   → ✅ Générateur prêt, pipeline TODO
│
├─ Translation (patte qui marche, piston)
│   → CRANK-SLIDER (4-bar linkage)
│   → ❌ TODO
│
└─ Return mechanism:
    ├─ Vertical pushrod + masse > 0.1g → GRAVITÉ ✅
    ├─ Horizontal / Z-rotation → RESSORT NÉCESSAIRE ⚠️
    └─ Faible couple gravité (<0.5 mNm) → FRICTION RISQUE ℹ️
```

## PHASE 4 — Future

- Pipeline auto: joint_type dans SceneJoint → auto-select pin/ball/hinge
- Crank-slider pour walking quadrupeds
- Print-in-place joints (assemblé à l'impression)
- Subdivision surfaces pour qualité visuelle
