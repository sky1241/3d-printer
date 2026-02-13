# 📋 TODO LIST — Automata Generator v4
# Dernière mise à jour : 13 février 2026 (nuit)
# Commit: 4b6353f+

---

## ✅ ART-001 — Module Figurine Articulée — COMPLET

| Commit | Description |
|--------|-------------|
| `b139e0f`→`0cb6165` | JointFactory: pin, split, combo, attach, router |
| `7e440bd`+`43c1f51` | Pipeline intégré + fuzzy matching (17 espèces) |
| `8001745` | Contraintes B10 (4 checks articulation) |
| `ad321fa`+`2ff8b4c` | Collision fix + assembly annotations |
| `4b6353f` | ART-001f: Return mechanism (gravity vs spring) |
| *pending* | ART-001g: Ball joint generator (rotule Ø6/8/10) |
| *pending* | ART-001h: Living hinge generator (charnière mince) |

## ✅ SYS — Issues codex audit — RÉSOLUES

| # | Issue | Status | Commit |
|---|-------|--------|--------|
| SYS-001a | `--validate` crash | ✅ | Fixé en passant |
| SYS-001b | Unknown roles | ✅ | `562c973` |
| SYS-001c | BOM incomplet | ✅ | `6514c98` |
| SYS-001d | Missing optimizers | ✅ | Faux positif |

---

## 🟡 P1 — Prochaines features

| # | Tâche | Status |
|---|-------|--------|
| ART-001f | Return mechanism detection | ✅ DONE |
| ART-001g | Ball joint generator | ✅ DONE (code, pas encore dans pipeline) |
| ART-001h | Living hinge generator | ✅ DONE (code, pas encore dans pipeline) |
| ART-001i | Crank-slider miniature (walking) | ❌ TODO |
| PIPE-001 | Intégrer ball/hinge dans pipeline auto | ❌ TODO |

---

## 🟡 P2 — Améliorations

| # | Tâche |
|---|-------|
| SYS-002a | Crank handle ergonomie |
| SYS-003a | 26 collisions structurelles restantes |

---

## 🟢 FUT — Nice to have

- Subdivision surfaces, textures, carapace hexagonale
- Multi-shaft, réducteur épicycloïdal
- Guide assemblage PDF auto, slicer profiles
- Print-in-place pré-assemblé

---

## 📊 ÉTAT DU SYSTÈME

```
Code:        ~19,600 lignes
Presets:     11 (9 originaux + 2 tortues)
Espèces:     17 dynamiques (chat → dragon)
Contraintes: 100 checks (94 base + 6 B10 articulation)
Part roles:  26 rôles (0 unknown)
JointFactory: 9 méthodes (pin, split, combo, attach, socket, pushrod,
              amplitude, ball_joint, living_hinge)
Tests:       9/9 blocks, 9/9 presets, 17/17 dynamic GREEN
```
