# 📋 TODO LIST — Automata Generator v4
# Dernière mise à jour : 13 février 2026 (nuit, post-cam-fix)
# Commit: 100940c

---

## ✅ COMPLETÉ

| Feature | Commits | Description |
|---------|---------|-------------|
| ART-001 | b139e0f→8001745 | Pin joints: 9 étapes battle plan |
| ART-002 | ad321fa+2ff8b4c | Collision pushrod fix + assembly roles |
| ART-001f | 4b6353f | Return mechanism (gravity/spring) |
| ART-001g | 2e363cb | Ball joint generator (Ø6/8/10) |
| ART-001h | 2e363cb | Living hinge generator |
| PIPE-001 | 4c7dba2 | Auto-dispatch pin/ball/hinge par joint |
| SYS-001a→d | 562c973+6514c98 | Codex audit 100% résolu |
| MESH-FIX | e81c284 | Degenerate face repair (-80%) |
| DUAL-001 | Various | Dual-shaft architecture + constraints |
| BUG-SYNC | 38a801d | Sync gear false collision (14→0) |
| BUG-SHAFT | 38a801d | Shaft deflection E modulus fix (15→0) |
| BUG-AUTO | 38a801d | Auto-upgrade shaft for all modes |
| BUG-MUTABLE | de5a793 | Mutable default arg _make_cone_beak |
| BUG-SHAPELY | de5a793 | 37× deprecated .buffer(resolution=) |
| BUG-FEAT | f6babe5 | FEAT-SMALL min leg Ø2.5mm (2→0) |
| BUG-DEGEN2 | f6babe5 | Enhanced mesh repair area-based (30→15 faces) |
| BUG-SKIP | f6babe5 | Collision skip pairs multi-cam (388→12) |
| BUG-CAM | 100940c | cam∩cam + collar∩pushrod skip pairs (dragon 5→1v) |

---

## 📊 AUDIT 17 ESPÈCES (13 fév, post-cam-fix)

```
                cam  prt violations  status
 chat            6   74      0       ✅ CLEAN
 human           5   41      0       ✅ CLEAN
 eagle           4   54      0       ✅ CLEAN
 snake           2   28      0       ✅ CLEAN
 dolphin         3   37      0       ✅ CLEAN
 ant             7   79      0       ✅ CLEAN
 butterfly       3   45      1       ⚠ 1 DEGEN
 spider          9   94      0       ✅ CLEAN
 scorpion       13  131      2       ⚠ 2 DEGEN
 crab           10  104      1       ⚠ 1 DEGEN
 lobster        11  115      2       ⚠ 2 DEGEN
 centipede       4   48      0       ✅ CLEAN
 octopus         8   82      0       ✅ CLEAN
 snail           4   45      0       ✅ CLEAN
 sunflower       1   20      0       ✅ CLEAN
 t-rex           5   64      1       ⚠ 1 DEGEN
 dragon          9  102      1       ⚠ 1 DEGEN

Clean: 11/17  |  DEGEN-only: 6/17  |  Real issues: 0/17 ✅
```

**Presets:** 12/12 PASS (10 core + 2 turtle)

---

## 🔧 TÂCHES RESTANTES

### P1 — Cam orientation refactor (architecture)
Les cames sont générées en plan XY (profil) + extrusion Z (épaisseur), mais l'arbre
est le long de Y. La bonne orientation serait profil en XZ, épaisseur en Y.
Refactor nécessite: rotation cames + adaptation follower guides + levers + pushrods.
Impact: éliminerait les faux positifs cam∩cam actuellement gérés par skip_pairs.
Complexité: HAUTE (touche toute la chaîne mécanisme).

### P2 — MESH-DEGEN résiduel (6 espèces, ~8 faces)
Faces dégénérées résiduelles dans fig_neck/head/tail/body.
Cause: booléens CSG (perçage pushrod) sur géométrie complexe.
Impact: mineur — les slicers (Cura, PrusaSlicer) gèrent bien.

### P3 — Documentation
- [ ] Mettre à jour CODEMAP avec les nouvelles skip_pairs
- [ ] Ajouter ASSEMBLY_GUIDE.md pour l'utilisateur final
- [ ] Documenter les presets V2-V10 (slider, rocker, etc.)

### P4 — Features futures
- [ ] Export STL individuel par pièce (pour impression sélective)
- [ ] Preview 3D web viewer (Three.js)
- [ ] Optimisation positionnement pushrods (3D routing)
- [ ] Support matériaux PETG/ABS (nouveaux profils FDM)
