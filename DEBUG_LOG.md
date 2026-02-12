# 🔍 DEBUG LOG — Automata Generator v4
# Chaque push est suivi d'un test de régression complet.
# Pattern: implémenter → regression_test.py → push si OK → sinon rollback
# Dernière mise à jour: 12 février 2026

---

## CURRENT STATE (post-P12)

```
Commit: 1e43980
Date: 12 fév 2026

✅ nodding_bird    0E 17W  parts=19  lev=1  brk=1  wt=19/19
✅ walking_figure  0E 27W  parts=32  lev=4  brk=4  wt=32/32
✅ drummer         0E 25W  parts=25  lev=2  brk=2  wt=25/25
✅ swimming_fish   0E 16W  parts=20  lev=1  brk=1  wt=20/20
✅ waving_cat      0E 18W  parts=20  lev=1  brk=1  wt=20/20
✅ flapping_bird   0E 32W  parts=26  lev=2  brk=2  wt=26/26
✅ blacksmith      0E 18W  parts=19  lev=1  brk=1  wt=19/19
✅ bobbing_duck    0E 17W  parts=18  lev=1  brk=1  wt=18/18
✅ rocking_horse   0E 22W  parts=22  lev=0  brk=0  wt=22/22
test_master: ALL PASS
77/94 checks wired (82%)
```

## HISTORIQUE DES PUSHES (Sessions 10-14)

| # | Commit | Description | Régression? | Résultat |
|---|--------|-------------|-------------|----------|
| 1 | `2100e5b` | P1: wire 13 checks to real data | — | 9/9 ✅ |
| 2 | `ae7d6e6` | fix(ROLLER): rf/Rb ≤ 0.4 | — | 9/9 ✅ |
| 3 | `229b30f` | fix(Rb): min Rb=5mm | — | 9/9 ✅ |
| 4 | `35e8272` | fix(PHI): pressure angle cascade | — | 9/9 ✅ |
| 5 | `cb7d9af` | fix(P2): Phase 5 real validation | — | 9/9 ✅ |
| 6 | `a2c047e` | feat(P3): STL validation | — | 9/9 ✅ |
| 7 | `8998ac1` | fix(P4): U-slot bore | — | 9/9 ✅ |
| 8 | `d0c78b5` | feat(P5): lever arms | — | 9/9 ✅ |
| 9 | `83e1c68` | feat(P6): 15 more checks (26/94) | — | 9/9 ✅ |
| 10 | `3092d45` | feat(P6b): 11 more checks (37/94) | — | 9/9 ✅ |
| 11 | `4e74d0a` | feat(P7): lever brackets | — | 9/9 ✅ |
| 12 | `c532b2c` | feat(P8): follower reach | — | 9/9 ✅ |
| 13 | `1101463` | infra: regression_test.py + DEBUG_LOG | — | 9/9 ✅ |
| 14 | `83a962a` | feat(P9): 6 dead-code checks (43/94) | ✅ NO REGRESS | 9/9 ✅ |
| 15 | `652e86f` | feat(P10): 8 more checks (51/94) | ✅ NO REGRESS | 9/9 ✅ |
| 16 | `bc7a69e` | feat(P11): physics + trou18/23 (59/94) | ✅ NO REGRESS | 9/9 ✅ |
| 17 | `1e43980` | feat(P12): exotics + remaining (77/94) | ✅ NO REGRESS | 9/9 ✅ |

---

## TÂCHES RESTANTES

| ID | Description | Priorité | Status |
|----|-------------|----------|--------|
| — | 17 checks non branchés | N/A | gear/geneva/crank (pas dans nos presets) ou dict-return |
| — | Min wall thickness (ray-based) | Difficile | FUTURE |
| — | Lever pivot pin + collar meshes | Moyen | FUTURE |
| — | Assembly guide PDF | Moyen | FUTURE |

## WARNINGS CONNUS (pas des bugs, design choices)

- FOLLOWER_REACH_GAP: flapping_bird/neck, rocking_horse/rocker+neck (3 gaps, direct drive)
- TOLERANCE_STACKUP: walking_figure (4 cams = 6 interfaces)
- ASSEMBLY_HIGH_PART_COUNT: walking_figure (32 parts), flapping_bird (26 parts)
- DOCS_MISSING_OPTIONAL: timing diagram manquant partout
- Various material warnings (creep, degradation) — normal PLA limits

---

## PATTERN DE TRAVAIL

```
1. Implémenter le changement
2. python3 regression_test.py
3. Si "SAFE TO PUSH" → git add + commit + push
4. Si "REGRESSION DETECTED" → git checkout -- . (rollback)
5. Mettre à jour ce fichier après chaque push
```
