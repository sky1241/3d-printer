# 🔩 ROADMAP — ÉTAT RÉEL DU PROJET

> Dernière mise à jour: 13 février 2026
> Commit: 0865043

---

## 📊 ÉTAT DES LIEUX

### Ce qui MARCHE ✅
- 17 templates, 118 espèces, 17/17 builders sans crash
- **11/17 espèces 100% clean** (0 erreurs, 0 collisions)
- Auto Ø6mm shaft pour >5 cames (élimine deflection)
- Auto cam_spacing 6mm pour >6 cames
- Follower guides correctement espacés (0 collision wall∩guide)
- Châssis auto-expand pour espèces complexes
- Through-bores, roller ratio, Rb cap — tous fixés
- 94/94 tests master, 49/49 scene_builder, 20/20 living_beings

### Ce qui RESTE 🔴 (6/17 espèces — need dual-shaft)

| Espèce | Cams | Problèmes | Fix nécessaire |
|--------|------|-----------|----------------|
| octopus | 8 | shaft 234mm>220 | Dual-shaft |
| spider | 9 | shaft 255mm>220 | Dual-shaft |
| dragon | 9 | shaft 289mm + deflection 0.43mm | Dual-shaft |
| crab | 10 | shaft 241mm + motor -8% | Dual-shaft |
| lobster | 11 | shaft 262mm + deflection + motor -19% | Dual-shaft |
| scorpion | 13 | shaft 316mm + deflection + motor -41% | Dual-shaft |

---

## 🎯 PLAN D'ACTION

### BLOQUÉ — Deep Research nécessaire
- [ ] DUAL-SHAFT architecture (engrenages PLA sync)
- [ ] Prompt envoyé à ChatGPT: DEEP_RESEARCH_PROMPT_v3.md

### P3 — FINITION (peut avancer en parallèle)
- [ ] STL Export par espèce
- [ ] Instructions assemblage PDF
- [ ] Profils slicer
- [ ] BOM complet

---

## 📈 MÉTRIQUES

```
Master tests:        94/94  ✅
Scene builder:       49/49  ✅
Living beings:       20/20  ✅
Regression presets:  9/9    ✅
Regression dynamic:  17/17  ✅
Debug bugs:          13/13  ✅
Espèces 100% clean:  11/17  ✅ (65%)
Collisions:          0/17   ✅ (was 13/17)
```

## 📝 COMMITS SESSION 13 FÉV

| Commit | Description |
|--------|-------------|
| `0865043` | Auto-scale Ø6mm + boss extent fix — 11/17 clean |
| `a7de852` | docs: tracking update |
| `f946ed2` | BUG-010: wall∩follower collision fix |
| `7418f59` | CAM_ROLLER ratio fix |
| `521e5b7` | P0 AutomataScene crash fix |
| `4d0aa53` | Deep research prompt v3 |
| `c20b395` | Docs tracking update |
