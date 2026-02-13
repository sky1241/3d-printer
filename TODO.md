# 📋 TODO LIST — Automata Generator v4
# Dernière mise à jour : 13 février 2026 (nuit, post-audit)
# Commit: e81c284

---

## ✅ TOUT LE CRITIQUE EST FAIT

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

---

## 📊 AUDIT COMPLET 17 ESPÈCES (13 fév soir)

```
                cam  prt degen dim  coll shaft err
 chat            6   74    0   0   14    0    0  ✅
 human           5   41    0   0    0    0    0  ✅
 eagle           4   54    1   0   15    1    2  ⚠
 snake           2   28    0   0    2    0    0  ✅
 dolphin         3   37    0   0    1    0    0  ✅
 ant             7   78    1   0   19    2    3  ⚠
 butterfly       3   45    0   0    3    1    2  ⚠
 spider          9   91    0   1   21    2    3  ⚠
 scorpion       13  128    2   1   47    2    4  ⚠
 crab           10  102    2   1   28    2    3  ⚠
 lobster        11  113    3   1   36    2    3  ⚠
 centipede       4   48    0   0    4    1    2  ⚠
 octopus         8   80    0   1   22    2    3  ⚠
 snail           4   45    0   0   11    1    2  ⚠
 sunflower       1   20    0   0    0    0    0  ✅
 t-rex           5   64    1   0   12    1    2  ⚠
 dragon          9   99    2   1   26    2    3  ⚠

Clean: 5/17  |  Issues: 12/17 (all shaft deflection + collisions)
```

### Patterns identifiés

| Pattern | Espèces | Cause racine | Fix |
|---------|---------|-------------|-----|
| **SHAFT_DEFLECTION** | 12/17 | Arbre trop long (>4 cams) | Dual-shaft ou split |
| **Oversize >250mm** | 6/17 | >7 cams → chassis dépasse bed | Dual-shaft |
| **pushrod∩pushrod** | 11/17 | Pushrods parallèles sans offset Y | Stagger Y |
| **lever∩pushrod** | 11/17 | Levier voisin croise pushrod | Levier plus court |
| **mid_bearing∩pushrod** | 6/17 | Pushrod traverse mur milieu | Trou dans mur |
| **Degen meshes** | 7/17 | Boolean CSG sur fig_neck | **FIXED -80%** |

### Conclusion

Les 5 espèces clean (chat, human, snake, dolphin, sunflower) = ≤6 cams + géométrie simple.
Les 12 espèces avec erreurs = toutes SHAFT_DEFLECTION. 
**Un seul fix (dual-shaft) résoudrait 70% des issues.**

---

## 🟡 P1 — Prochaines features (par impact)

| # | Tâche | Impact | Espèces fixées |
|---|-------|--------|----------------|
| DUAL-001 | **Dual-shaft** (2 arbres ≤125mm chacun) | 🔴 Critique | 12/17 shaft + 6/17 oversize |
| STAG-001 | **Pushrod Y-stagger** (offset ±2mm) | 🟡 Moyen | 11/17 pushrod∩pushrod |
| WALL-001 | **Trous dans mid-bearing wall** | 🟡 Moyen | 6/17 mid_bearing∩pushrod |
| DEMO-001 | Preset ball joint (chat épaule) | 🟢 Validation | Pipeline ball |
| DEMO-002 | Preset living hinge (croco mâchoire) | 🟢 Validation | Pipeline hinge |
| ART-001i | Crank-slider miniature (walking) | 🟢 Feature | Pattes réalistes |

## 🟡 P2 — Améliorations

| # | Tâche |
|---|-------|
| SYS-002a | Crank handle ergonomie |
| LEVER-001 | Lever length optimization (éviter lever∩pushrod) |

## 🟢 FUT — Nice to have

- Subdivision surfaces, textures
- Réducteur épicycloïdal imprimé
- Guide assemblage PDF auto
- Print-in-place

---

## 📊 ÉTAT DU SYSTÈME

```
Code:         ~19,900 lignes
JointFactory: 9 méthodes (pin, ball, hinge + support)
Pipeline:     auto-dispatch pin/ball/hinge par Joint.mechanism
Part roles:   28 rôles (0 unknown)
Contraintes:  100 checks
Mesh repair:  auto-fix degenerate faces (-80%)
Tests:        9/9 blocks, 9/9 presets, 17/17 dynamic GREEN
Commit:       e81c284
```

## 🌳 ARBRE DE DÉCISION — Prochaine action

```
Est-ce que l'espèce a > 6 cames ?
├── OUI → DUAL-001 (dual-shaft) résout shaft + oversize + mid_bearing
│         Priorité: 🔴 CRITIQUE (12/17 espèces impactées)
│
└── NON → Est-ce qu'il y a des collisions pushrod∩pushrod ?
          ├── OUI → STAG-001 (Y-stagger) résout pushrod parallèles
          │         Priorité: 🟡 MOYEN
          │
          └── NON → Est-ce qu'il y a des collisions lever∩pushrod ?
                    ├── OUI → LEVER-001 (optimize lever length)
                    │
                    └── NON → CLEAN ✅ → DEMO presets ou features
```
