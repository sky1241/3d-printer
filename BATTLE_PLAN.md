# ⚔️ BATTLE PLAN — Figurines Articulées
# Dernière mise à jour : 13 février 2026 (soir)
# Status: 7/9 étapes COMPLÉTÉES

---

## ÉTAT DES ÉTAPES

| # | Étape | Status | Commit | Risque |
|---|-------|--------|--------|--------|
| 1 | ✅ **Pin Joint Generator** | DONE | `b139e0f` | Zéro |
| 2 | ✅ **Body Splitter** | DONE | `f7976a9` | Faible |
| 3 | ✅ **Joint + Split combo** | DONE | `e06e8b3` | Moyen |
| 4 | ✅ **Pushrod Attach** | DONE | `9513f65` | Faible |
| 5 | ✅ **Pushrod Router** | DONE | `0cb6165` | Moyen |
| 6 | ✅ **Turtle Simple** (1 joint) | DONE | `7e440bd` | Élevé |
| 7 | ✅ **Turtle Walking** (6 joints) + 17 espèces | DONE | `43c1f51` | Élevé |
| 8 | 🟡 **Généralisation** | PARTIEL | — | Max |
| 9 | ❌ **Contraintes B10** | TODO | — | Moyen |

---

## CE QUI MARCHE MAINTENANT

### JointFactory (6 méthodes)
```python
JointFactory.create_pin_joint(d, length, clearance) → (pin, hole)
JointFactory.split_at_joint(mesh, point, normal, gap) → (fixed, mobile)
JointFactory.add_joint_to_split(fixed, mobile, pos, axis, d) → (fh, mh, pin)
JointFactory.calculate_pushrod_attach(pos, axis, R, dir) → (point, direction)
JointFactory.create_pushrod_socket(point, Ø, depth) → socket_mesh
JointFactory.create_pushrod(start, end, Ø, obstacles) → rod_mesh
JointFactory.calculate_amplitude(travel, arm) → degrees
JointFactory.pin_hole_diameter(d) → hole_d
```

### Pipeline articulé (dans generate())
- Post-processing après FigurineBuilder
- Guard: seulement si `_figurine_cfg` est défini (anciens presets intacts)
- Fuzzy matching: `leg_fl` → `fig_leg_0` automatique
- `_used_fig_parts` set pour éviter double-assignment

### Résultats par espèce
- turtle_simple: 1 pin (cou) ✅
- turtle_walking: 6 pins (cou, 4 hanches, queue) ✅
- chat: 2 pins, eagle: 4 pins, dragon: 4 pins, etc.
- 17/17 dynamiques: watertight ✅

---

## ÉTAPE 8 — Généralisation (PARTIEL)
**Déjà fait:** Le code d'articulation tourne sur TOUTES les 17 espèces via SceneBuilder.
Chaque espèce qui a des joints dans sa scene reçoit automatiquement des pin joints.

**Ce qui manque pour "complet":**
- Bridge part detection plus malin (pas juste fig_neck)
- Joint position basée sur les vrais contours du mesh (pas juste centroid)
- Trous de pin non visibles sur les petites pattes (volume fig_leg trop petit)
- Ball joints pour épaules multi-axes (P1)
- Living hinges pour mâchoires/nageoires (P1)

---

## ÉTAPE 9 — Contraintes B10 (TODO)
Nouveau bloc de checks pour les articulations:

| Check | Description | Seuil |
|-------|-------------|-------|
| JOINT_PIN_TOO_THIN | d_axe < 2mm | warning si < 3mm |
| JOINT_CLEARANCE_TIGHT | clearance < 0.1mm | warning |
| JOINT_CLEARANCE_LOOSE | clearance > 0.5mm | warning |
| JOINT_AMPLITUDE_EXCEEDED | θ > limites joint | error |
| PUSHROD_BUCKLING | d < seuil Euler | error |
| PUSHROD_COLLISION | intersecte fixed part | warning |
| MOBILE_COLLISION_AT_MAX | mobile touche fixed à θ_max | error |
| LIVING_HINGE_TOO_THIN | < 0.4mm | error |

---

## PRINCIPES DE TRAVAIL
1. **Brique par brique** — jamais 2 étapes en même temps
2. **Tests complets** après chaque modif (regression_test.py + regression_test_dynamic.py)
3. **Git commit + push** après chaque étape validée
4. **Fallback** — si ça casse, l'ancien mode marche toujours (guard `if fig_cfg`)
