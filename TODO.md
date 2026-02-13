# 📋 TODO LIST — Automata Generator v4
# Dernière mise à jour : 13 février 2026 (soir)
# Commit: 2ff8b4c

---

## ✅ ART-001 — Module Figurine Articulée — COMPLET
**Battle plan 9/9 + ART-002 résolu**

| # | Tâche | Status | Commit |
|---|-------|--------|--------|
| ART-001a | Research data ChatGPT | ✅ | `f631f8e` |
| ART-001b | Pin joint generator | ✅ | `b139e0f` |
| ART-001c | Body splitter | ✅ | `f7976a9` |
| ART-001c+ | Joint + Split combo | ✅ | `e06e8b3` |
| ART-001d | Pushrod attach | ✅ | `9513f65` |
| ART-001d+ | Pushrod router | ✅ | `0cb6165` |
| ART-001e | Motion calculator | ✅ | `b139e0f` |
| ART-001k | Pipeline intégré | ✅ | `7e440bd`+`43c1f51` |
| ART-001l | Contraintes B10 | ✅ | `8001745` |
| ART-002 | Collision pushrod fix | ✅ | `ad321fa` |
| — | Assembly role annotations | ✅ | `2ff8b4c` |

---

## 🟡 P1 — Prochaines features

| # | Tâche | Impact | Difficulté |
|---|-------|--------|------------|
| ART-001f | Return mechanism (gravité/ressort) | Moyen | Faible |
| ART-001g | Ball joint generator (rotule) | Épaules multi-axe | Moyen |
| ART-001h | Living hinge generator | Mâchoire, nageoire | Moyen |
| ART-001i | Crank-slider miniature (patte) | Walking réaliste | Élevé |
| ART-001j | Print-in-place | Avancé | Très élevé |

---

## 🟡 SYS — Issues système (du codex audit)

| # | Issue | Priorité | Status |
|---|-------|----------|--------|
| SYS-001a | `--validate` crash line ~14160 | P1 | ❌ |
| SYS-001b | Unknown roles print_settings.json | P2 | ❌ |
| SYS-001c | BOM incomplet crank | P2 | ❌ |
| SYS-001d | Missing DE/L-BFGS-B optimizers | P2 | ❌ |
| SYS-002a | Crank handle ergonomie (30mm) | P2 | 🟡 |
| SYS-003a | 26 collisions structurelles turtle_walking | P2 | ❌ |

---

## 🟢 FUT — Nice to have

- FUT-001: Qualité visuelle (subdivision, textures, carapace hex)
- FUT-002: Multi-shaft, réducteur épicycloïdal, turntable split
- FUT-003: Guide assemblage PDF, slicer profiles, STL orientation auto

---

## 📊 ÉTAT DU SYSTÈME

```
Code:        ~19,400 lignes
Presets:     11 (9 originaux + 2 tortues)
Espèces:     17 dynamiques (chat → dragon)
Contraintes: 98 checks (94 + 4 B10 articulation)
Tests:       9/9 B-blocks, 9/9 presets, 17/17 dynamic GREEN
Articulations: JointFactory (6 méthodes), pin joints auto, collision fix
Commit:      2ff8b4c (main, pushed)
```

## 🎯 PROCHAINES ÉTAPES RECOMMANDÉES

```
1. SYS-001a: Fix --validate crash (P1, le seul vrai bug connu)
2. ART-001f: Return mechanisms (gravité vs ressort)
3. ART-001g: Ball joints pour épaules
4. SYS-001b-d: Nettoyage codex audit
```
