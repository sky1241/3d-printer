# 📋 TODO LIST — Automata Generator v4
# Dernière mise à jour : 13 février 2026
# Commit: 59def7b

---

## 🔴 CRITIQUE — Bloquants pour figurines fonctionnelles

### ART-001 — Module Figurine Articulée (THE BIG ONE)
**Status**: 🟡 En cours — data collection phase
**Prompt ChatGPT**: `PROMPT_FIGURINE_ARTICULEE.md`
**Problème**: Les figurines actuelles sont des blobs CSG décoratifs. Aucune articulation réelle.
Le pushrod pousse tout le bloc vers le haut au lieu de faire pivoter la tête.

**Sous-tâches:**

| # | Tâche | Priorité | Status | Notes |
|---|-------|----------|--------|-------|
| ART-001a | **Collecter data** — envoyer prompt à ChatGPT | P0 | 🟡 TODO | Clearances, joint types, formules |
| ART-001b | **Pin joint generator** — axe + trou avec clearance | P0 | ❌ | Base de toutes les articulations |
| ART-001c | **Body splitter** — couper figurine en fixed/mobile | P0 | ❌ | Plans de coupe aux joints |
| ART-001d | **Pushrod router** — connecter levier → joint | P0 | ❌ | Conversion vertical → rotation |
| ART-001e | **Motion calculator** — θ = atan(amp/bras) | P0 | ❌ | Cinématique inverse |
| ART-001f | **Return mechanism** — gravité/friction/ressort | P1 | ❌ | Quand utiliser quoi ? |
| ART-001g | **Ball joint generator** — rotule imprimable | P1 | ❌ | Pour épaules multi-axe |
| ART-001h | **Living hinge generator** — charnière mince | P1 | ❌ | Mâchoire, nageoire |
| ART-001i | **Crank-slider miniature** — patte qui marche | P1 | ❌ | Pour walking quadrupeds |
| ART-001j | **Print-in-place** — imprimé déjà assemblé | P2 | ❌ | Avancé, nécessite calibration |
| ART-001k | **Body plan templates** (12 types) | P1 | ❌ | Tortue → Dragon, toutes les espèces |
| ART-001l | **Tests & validation** — articulations fonctionnelles | P0 | ❌ | Nouveau bloc de contraintes |

**Dépendances**: ART-001a → ART-001b → ART-001c+d → ART-001e+f → ART-001k

---

### ART-002 — Pushrod ↔ Figurine Collision Fix
**Status**: ❌ Ouvert
**Problème**: Le pushrod traverse le corps de la figurine (COLLISION fig_body∩pushrod)
**Cause**: Le pushrod est routé en ligne droite sans tenir compte de la figurine
**Solution**: Router le pushrod pour qu'il passe sous/à travers un trou dans le corps
**Bloqué par**: ART-001c (body splitter)

---

## 🟡 IMPORTANT — Améliorations système

### SYS-001 — Codex Audit Issues (du 13 fév)
| # | Issue | Status |
|---|-------|--------|
| SYS-001a | `--validate` crash line ~14160 | ❌ À investiguer |
| SYS-001b | Unknown roles in `print_settings.json` | ❌ |
| SYS-001c | BOM incomplet (manque quincaillerie crank) | ❌ |
| SYS-001d | Missing DE/L-BFGS-B optimizers | ❌ |

### SYS-002 — Crank Mode Refinements
| # | Issue | Status |
|---|-------|--------|
| SYS-002a | Crank handle trop petite (30mm) → ergonomie | 🟡 |
| SYS-002b | Pas de guide anti-retour sur la manivelle | ❌ |
| SYS-002c | BOM crank mode (liste 0 hardware mais faut quand même colle) | ❌ |

### SYS-003 — Validation Crank Mode
| # | Issue | Status |
|---|-------|--------|
| SYS-003a | Walking turtle: 31 collisions pushrod (non-bloquant mais sale) | ❌ |
| SYS-003b | DFA_TOO_MANY_PARTS: 67 pièces turtle_walking | ⚠️ By design |

---

## 🟢 NICE TO HAVE — Futures améliorations

### FUT-001 — Qualité visuelle figurines
| # | Tâche | Notes |
|---|-------|-------|
| FUT-001a | Subdivision surfaces (plus lisse que CSG) | Catmull-Clark |
| FUT-001b | Carapace tortue réaliste (hexagones) | Pattern procedural |
| FUT-001c | Yeux/pupilles avec relief | Pas juste des sphères noires |
| FUT-001d | Texture/pattern sur pattes | Écailles, plumes |

### FUT-002 — Optimisations mécaniques
| # | Tâche | Notes |
|---|-------|-------|
| FUT-002a | Turntable cam auto-split (>256mm) | Geneva trop grosse |
| FUT-002b | Multi-shaft support | 2 arbres parallèles |
| FUT-002c | Réducteur épicycloïdal imprimé | Plus compact que N20 |

### FUT-003 — UX / Documentation
| # | Tâche | Notes |
|---|-------|-------|
| FUT-003a | Guide d'assemblage auto-généré (PDF) | Avec images des pièces |
| FUT-003b | Paramètres d'impression par pièce | Slicer profiles |
| FUT-003c | STL orientation auto pour slicer | Flat face down |

---

## ✅ COMPLÉTÉ (session 13 fév)

| Tâche | Description | Commit |
|-------|-------------|--------|
| ✅ Turtle presets | turtle_simple (1 came) + turtle_walking (6 cames) | `77965ce` |
| ✅ Crank mode | 100% imprimable, zéro hardware | `c244ded` |
| ✅ Crank handle fix | Bras en -Y, pas en +X (évite collision wall) | `c244ded` |
| ✅ Collar fix | 1 collar_retention au lieu de N entre les cames | `c244ded` |
| ✅ Torque skip crank | Pas de check torque en mode manivelle | `c244ded` |
| ✅ Figurine cosmétique | FigurineConfig quadruped + carapace accessory | `59def7b` |
| ✅ Rendu 3D | pyrender multi-view avec couleurs par pièce | session |
| ✅ Bug audit 64 violations | Hertz, Rb, lever sweep, torque, BOM/PTC | session précédente |
| ✅ Auto-scaling R1-R8 | Shaft, motor, spacing, chassis auto | session précédente |
| ✅ 17/17 espèces clean | Zéro bugs sur toutes les espèces dynamiques | session précédente |
| ✅ CODEMAP_v4 | 18,615 lignes, architecture complète | session précédente |

---

## 📊 ÉTAT DU SYSTÈME

```
Code:        ~18,800 lignes (automata_unified_v4.py)
Presets:     11 (9 originaux + 2 tortues)
Espèces:     17 dynamiques (chat → dragon)
Contraintes: 94 checks, 9 blocs
Tests:       9/9 B-blocks, 9/9 presets, 17/17 dynamic, 13/13 debug
Commits:     59def7b (main, pushed)
```

---

## 🎯 PROCHAINES ÉTAPES (ordre recommandé)

```
1. 📨 Envoyer PROMPT_FIGURINE_ARTICULEE.md à ChatGPT
2. 📥 Importer les données dans le code (constantes, formules, tables)
3. 🔧 Coder ART-001b: Pin joint generator (le plus simple)
4. ✂️ Coder ART-001c: Body splitter (couper figurine aux joints)
5. 🔗 Coder ART-001d: Pushrod router (levier → joint)
6. 🧮 Coder ART-001e: Motion calculator (cinématique)
7. 🐢 Tester sur turtle_simple (1 joint = cou)
8. 🐢 Tester sur turtle_walking (7 joints = cou + 4 hanches + queue)
9. 🐱 Généraliser aux 12 body plans
10. 🧪 Nouveau bloc de contraintes pour articulations
```
