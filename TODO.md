# 📋 TODO LIST — Automata Generator v4
# Dernière mise à jour : 13 février 2026
# Commit: 43c1f51

---

## 🔴 CRITIQUE — Bloquants pour figurines fonctionnelles

### ART-001 — Module Figurine Articulée (THE BIG ONE)
**Status**: 🟢 ÉTAPES 1-7 TERMINÉES — reste étape 9 (contraintes)

**Sous-tâches:**

| # | Tâche | Priorité | Status | Commit |
|---|-------|----------|--------|--------|
| ART-001a | **Collecter data** — ChatGPT research | P0 | ✅ DONE | `f631f8e` |
| ART-001b | **Pin joint generator** — axe + trou + clearance | P0 | ✅ DONE | `b139e0f` |
| ART-001c | **Body splitter** — couper figurine en fixed/mobile | P0 | ✅ DONE | `f7976a9` |
| ART-001c+ | **Joint + Split combo** — trous + axe dans les 2 moitiés | P0 | ✅ DONE | `e06e8b3` |
| ART-001d | **Pushrod attach** — point d'attache sur mobile | P0 | ✅ DONE | `9513f65` |
| ART-001d+ | **Pushrod router** — cylindre levier → joint | P0 | ✅ DONE | `0cb6165` |
| ART-001e | **Motion calculator** — θ = asin(Δ/R) | P0 | ✅ DONE | intégré dans `b139e0f` |
| ART-001f | **Return mechanism** — gravité/friction/ressort | P1 | ❌ TODO | Data dans RESEARCH_ARTICULATED.py |
| ART-001g | **Ball joint generator** — rotule imprimable | P1 | ❌ TODO | Pour épaules multi-axe |
| ART-001h | **Living hinge generator** — charnière mince | P1 | ❌ TODO | Mâchoire, nageoire |
| ART-001i | **Crank-slider miniature** — patte qui marche | P1 | ❌ TODO | Pour walking quadrupeds |
| ART-001j | **Print-in-place** — imprimé déjà assemblé | P2 | ❌ TODO | Avancé, nécessite calibration |
| ART-001k | **Pipeline intégré** — pin joints dans generate() | P0 | ✅ DONE | `7e440bd` + `43c1f51` |
| ART-001l | **Tests & validation** — contraintes articulations (B10) | P0 | ❌ TODO | Étape 9 du battle plan |

**Résultats concrets:**
- `JointFactory` class: 6 méthodes statiques
- turtle_simple: 1/1 pin joint (cou) ✅
- turtle_walking: 6/6 pin joints (cou + 4 hanches + queue) ✅
- 17/17 espèces dynamiques: pin joints auto-ajoutés ✅
- Fuzzy name matching: leg_fl → fig_leg_0 automatique

---

### ART-002 — Pushrod ↔ Figurine Collision Fix
**Status**: ❌ Ouvert
**Problème**: Pushrod traverse fig_body (COLLISION)
**Solution**: Router via create_pushrod() avec obstacles=[fig_body]

---

## 🟡 SYS — Issues système

| # | Issue | Status |
|---|-------|--------|
| SYS-001a | `--validate` crash line ~14160 | ❌ |
| SYS-001b | Unknown roles print_settings.json | ❌ |
| SYS-001c | BOM incomplet crank | ❌ |
| SYS-001d | Missing DE/L-BFGS-B optimizers | ❌ |
| SYS-002a | Crank handle ergonomie | 🟡 |
| SYS-003a | 31 collisions pushrod turtle_walking | ❌ |

---

## ✅ COMPLÉTÉ (session 13 fév)

| Commit | Description |
|--------|-------------|
| `43c1f51` | Fuzzy joint→fig matching, turtle_walking 6/6 joints |
| `7e440bd` | Articulated figurines — pin joints dans pipeline |
| `0cb6165` | Pushrod Router |
| `9513f65` | Pushrod Attach |
| `e06e8b3` | Joint + Split combo |
| `f7976a9` | Body Splitter |
| `b139e0f` | JointFactory — pin joint generator |
| `f631f8e` | Research data + battle plan |
| `59def7b` | Figurines cosmétiques tortue |
| `c244ded` | Crank mode + collar fix |
| `77965ce` | Turtle presets |

## 📊 ÉTAT: ~19,200 lignes, 11 presets, 17 espèces, 94 checks, 9/9+17/17 tests GREEN

## 🎯 NEXT: Étape 9 (contraintes B10) → ART-002 (collision pushrod) → P1 features
