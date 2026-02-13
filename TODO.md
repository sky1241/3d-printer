# 📋 TODO LIST — Automata Generator v4
# Dernière mise à jour : 13 février 2026 (soir)
# Commit: 6514c98

---

## ✅ ART-001 — Module Figurine Articulée — COMPLET

| Commit | Description |
|--------|-------------|
| `b139e0f`→`0cb6165` | JointFactory: 5 briques isolées (pin, split, combo, attach, router) |
| `7e440bd` | Pipeline intégré turtle_simple (1 pin joint) |
| `43c1f51` | Fuzzy matching + turtle_walking (6 pins) + 17 espèces |
| `8001745` | Contraintes B10 (4 checks articulation) |
| `ad321fa` | ART-002: Collision pushrod fix (trous percés dans figurine) |
| `2ff8b4c` | Assembly role annotations (fixed/mobile/pin_joint) |

---

## ✅ SYS — Issues codex audit — RÉSOLUES

| # | Issue | Status | Commit/Note |
|---|-------|--------|-------------|
| SYS-001a | `--validate` crash | ✅ RÉSOLU | Plus de crash (fixé en passant) |
| SYS-001b | Unknown roles print_settings | ✅ RÉSOLU | `562c973` — 8 nouveaux rôles |
| SYS-001c | BOM incomplet crank | ✅ RÉSOLU | `6514c98` — steel rod + CA glue |
| SYS-001d | Missing DE/L-BFGS-B | ✅ FAUX POSITIF | Présents L19084 (inverse cam) |
| SYS-002a | Crank handle ergonomie | 🟡 P2 | Non bloquant |
| SYS-003a | 26 collisions structurelles | 🟡 P2 | mid_bearing_wall, non-figurine |

---

## 🟡 P1 — Prochaines features

| # | Tâche | Impact | Difficulté |
|---|-------|--------|------------|
| ART-001f | Return mechanism (gravité/ressort) | Moyen | Faible |
| ART-001g | Ball joint generator (rotule) | Épaules multi-axe | Moyen |
| ART-001h | Living hinge generator | Mâchoire, nageoire | Moyen |
| ART-001i | Crank-slider miniature (patte) | Walking réaliste | Élevé |

---

## 🟢 FUT — Nice to have

- Subdivision surfaces, carapace hexagonale, textures
- Multi-shaft, réducteur épicycloïdal
- Guide assemblage PDF auto, slicer profiles
- Print-in-place assemblé

---

## 📊 ÉTAT DU SYSTÈME

```
Code:        ~19,500 lignes
Presets:     11 (9 originaux + 2 tortues)
Espèces:     17 dynamiques (chat → dragon)
Contraintes: 98 checks (94 base + 4 B10 articulation)
Part roles:  26 rôles (0 unknown sur tous presets)
Tests:       9/9 blocks, 9/9 presets, 17/17 dynamic GREEN
BOM:         Complète (motor + crank modes)
Commit:      6514c98 (main, pushed)
```
