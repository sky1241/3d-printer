# 🔩 ROADMAP — ÉTAT RÉEL DU PROJET

> Dernière mise à jour: 13 février 2026 — post-fix CAM_ROLLER + P0 crash
> Audit complet sur 17 builders × 118 espèces
> Commit: f946ed2

---

## 📊 ÉTAT DES LIEUX

### Ce qui MARCHE ✅
- 17 templates de génération couvrant 118 espèces
- `make_automaton("chat")` → scène complète pour N'IMPORTE QUEL animal
- 17/17 builders génèrent sans crash, toutes pièces watertight
- Chaîne cinématique came→levier→pushrod→figurine fonctionnelle
- `run_all_constraints()` accepte Scene, Generator et Dict (P0 fixé)
- Murs avec vrais through-bores (euler=0, A1_STRICT OK)
- Ratio roller/cam ≤ 0.27 (CAM_ROLLER_LARGE éliminé)
- Axe Z aligné : cames, murs, followers tous sur l'arbre
- Rb cappé à 50mm (plus de cames géantes)
- Site web Flask + Export STL
- 94/94 tests master, 49/49 scene_builder, 20/20 living_beings

### Ce qui RESTE À FIXER 🔴

| # | Bug | Espèces | Gravité | Difficulté | Root cause |
|---|-----|---------|---------|------------|------------|
| BUG-010 | wall∩follower COLLISION | 13/17 | P1 | Moyenne | Placement spatial X |
| BUG-011 | SHAFT_DEFLECTION | 11/17 | P1 | Haute | Arbre Ø4mm trop long |
| BUG-012 | CAMSHAFT_OVERSIZED | 11/17 | P1 | Haute | 1 seul arbre, toutes cames |
| BUG-013 | MOTOR_OVERLOADED | 3/17 | P2 | Moyenne | Couple > 90mN·m |
| BUG-014 | TOO_MANY_CAMS | 1/17 | P2 | Haute | Scorpion 13 cames |

**Espèces 100% clean : sunflower, snake (2/17)**

---

## 🎯 PLAN D'ACTION — Priorisé

### P1-A : COLLISION wall∩follower (BUG-010) — PROCHAIN FIX
- Décaler followers_guides pour éviter overlap avec murs
- Impact : 13 espèces d'un coup
- Effort : ~30 min
- Fichier : `generate()` dans automata_unified_v4.py

### P1-B : SHAFT + OVERSIZED (BUG-011 + BUG-012)
- Option rapide : palier intermédiaire + arbre Ø6mm
- Option complète : dual-shaft avec engrenage sync → **DEEP RESEARCH**
- Impact : 11 espèces
- Effort : 2-4h (option rapide) ou research + implémentation (option complète)

### P2-A : MOTOR_OVERLOADED (BUG-013)
- Auto-réduction des amplitudes quand torque > seuil
- Ou ajout ratio de réduction engrenage
- Impact : 3 espèces

### P2-B : CONTRAINTES MORTES
- 47/95 contraintes jamais appelées
- Progressivement activer et brancher

### P3 : FINITION
- [ ] STL Export par espèce
- [ ] Instructions assemblage PDF
- [ ] Profils slicer (Cura/PrusaSlicer)
- [ ] BOM complet (visserie, moteur, alim)

---

## 🔬 DEEP RESEARCH NÉCESSAIRE?

| Sujet | Research? | Raison |
|-------|-----------|--------|
| Dual-shaft >6 cames | **OUI** | Engrenages PLA imprimés, sync, tolérance |
| Tout le reste | NON | Bugs de placement, clamps, math |

---

## 📈 MÉTRIQUES

```
Master tests:        94/94  ✅
Scene builder:       49/49  ✅
Living beings:       20/20  ✅
Regression presets:  9/9    ✅
Regression dynamic:  17/17  ✅
Debug bugs:          13/13  ✅
Builders testés:     17/17  (100%)
Espèces supportées:  118
Z-axis alignment:    17/17  ✅ (toutes espèces)
Through-bores:       17/17  ✅ (euler=0)
CAM_ROLLER warnings: 0      ✅
Espèces 100% clean:  7/17   (sunflower, snake, butterfly, eagle, human, centipede, chat)
```

## 📝 HISTORIQUE COMMITS (sessions 13 fév)

| Commit | Description | Impact |
|--------|-------------|--------|
| `7418f59` | FIX: CAM_ROLLER_LARGE — ratio rf/Rb ≤ 0.27 | 17/17 espèces |
| `521e5b7` | P0-FIX: run_all_constraints() accepte AutomataScene | 17/17 espèces |
| `f6153d3` | fix P0+CAM: tests 17 builders + Rb cap 50mm | 17/17 espèces |
| `0872f00` | fix CAM-1: cap Rb_max=50mm + binary search amplitude | Cames oversized |
| `1601960` | fix A1_STRICT: vrais trous dans les murs | Through-bores |
| `a930f82` | fix P0: run_all_constraints() accepte Generator | Pipeline crash |
| `b20bdab` | docs: ROADMAP audit complet | Documentation |
| `e75cac6` | fix: restore levers + scale + pushrod + baselines | Leviers restaurés |
