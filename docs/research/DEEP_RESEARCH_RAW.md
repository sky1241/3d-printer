# 🔬 DEEP RESEARCH — Résultats bruts ChatGPT
# Date: 13 février 2026
# Source: DEEP_RESEARCH_PROMPT_v3.md → ChatGPT Deep Research
# Lié à: BUG-011 (shaft deflection), BUG-012 (oversized), BUG-013 (motor)
# Espèces: spider, octopus, dragon, crab, lobster, scorpion (6/17)

---

## DOMAINE 1 — ARBRES DOUBLES & ENGRENAGES

### Décisions design (injectables dans le code)
| Paramètre | Valeur | Justification |
|-----------|--------|---------------|
| Module engrenage PLA | **1.5mm** | ≥1.0 recommandé, 1.5 robuste FDM |
| Nombre de dents | **20** | Min 13 pour 20°, 20 = bon compromis |
| Angle pression | **20°** standard | 25° possible mais 20° suffit |
| Backlash | **0.1–0.3mm** | Compense tolérances PLA |
| Entraxe (z=20, m=1.5) | **30mm** | a = m×(z1+z2)/2 = 1.5×40/2 |
| Erreur phase à 30RPM | **5° = 0.003s** | Imperceptible visuellement |
| Palier inter-arbres | **Trou Ø6.5mm dans cloison PLA** | μ≈0.2-0.3, OK à 30-60RPM |

### Ce qui manque (pas trouvé)
- Aucun exemple concret d'automate 3D >6 cames (on est pionniers)
- Pas de test PLA module/jeu documenté
- Pas d'étude profil engrenage modifié FDM

### Commit linkage
- **BUG-012 OVERSIZED** → dual-shaft split quand n_cams > 6
- Commit à faire: `DUAL_SHAFT_SPLIT`

---

## DOMAINE 2 — DÉFLEXION ARBRE

### Données validées
| Paramètre | Valeur | Source |
|-----------|--------|--------|
| E acier doux | **200 GPa** | Manuel RDM |
| E laiton CuZn37 | **105-110 GPa** | Manuel |
| I(Ø4mm) | **12.57 mm⁴** | π×4⁴/64 |
| I(Ø6mm) | **63.62 mm⁴** | π×6⁴/64 → **5.06× moins de flèche** |
| δ Ø4mm L=220mm F=5N | **0.42mm** | F×L³/(48EI) — trop grand |
| δ Ø4mm L=253mm F=5N | **0.64mm** | idem |
| L_max sans palier (<0.3mm) | **~180mm** | Estimé |
| Palier milieu → facteur | **÷16** | L/2 → (L/2)³ chaque moitié |
| μ PLA/acier sec | **0.2-0.3** | Mesuré |
| μ bronze Oilite | **0.10-0.15** | Fabricant |
| μ roulement MR84 (4×8×3) | **~0.01** | Fabricant |
| Tige Ø6mm inox 0.5m | **1.51-4€** | CommentFer |

### Commit linkage
- **BUG-011 SHAFT** → Auto Ø6mm déjà fait (commit `0865043`)
- Palier intermédiaire → `MID_BEARING_WALL` (en cours)
- Seuil: shaft_span > 180mm → auto mid-bearing

---

## DOMAINE 3 — COUPLE MOTEUR

### Données N20
| Paramètre | Valeur | Source |
|-----------|--------|--------|
| N20 168:1 (3V) nominal | **10.4 mN·m** | Zhaowei |
| N20 168:1 (3V) stall | **196 mN·m** | Zhaowei |
| Usage continu safe | **30-50% stall = 60-100 mN·m** | Pratique |
| 28BYJ-48 holding | **34.3 mN·m** | Welten Motors — insuffisant |

### Nos besoins vs dispo
| Espèce | Couple requis | N20 safe (60-100) | Verdict |
|--------|---------------|---------------------|---------|
| crab | 97.5 mN·m | ⚠ limite | Faisable |
| lobster | 107.3 mN·m | ❌ dépasse | Dual-motor |
| scorpion | 126.8 mN·m | ❌ dépasse | Dual-motor |

### Commit linkage
- **BUG-013 MOTOR** → dual-motor ou réduction
- Pas de publication sur optimisation phases cames (combinatoire minimax)

---

## DOMAINE 4 — EXEMPLES CONCRETS

### Résultat: AUCUN
- **Aucune référence open-source** d'automate 3D >6 cames sur dual-shaft
- Projets courants: 1-5 cames, arbre unique
- gzumwalt (Thingiverse): automates simples
- Rob Ives: carton/PLA, <6 cames
- Wintergatan: trains engrenages mais pas multi-cames
- **→ On est pionniers sur ce problème**

---

## DOMAINE 5 — VALIDATION FORMULES

### Résultats
| Formule | Verdict | Action code |
|---------|---------|-------------|
| δ=F×L³/(48EI) charge centrée | **✅ Correct** | Déjà implémenté |
| Superposition N charges: Σδᵢ | **✅ Correct** | Déjà implémenté |
| Hertz σ_H coeff **0.418** | **❌ FAUX** | Coeff correct = 1/√π ≈ **0.564** |
| E* = E₁×E₂/(E₁+E₂) | **✅ Approx OK** | E*≈3.44 GPa (acier+PLA) |
| T = F×(Rb+h)×tan(φ) | **⚠ Approx** | Surestime à grand φ, OK jouet |

### FIX-HERTZ: Formule à corriger
- Code actuel: utilise dérivation propre (pas 0.418) → **déjà correct** ✅
- Vérifié commit `80140ea`: hertz_contact_pressure_cylinder() calcule via b et p_max

### Commit linkage
- Formule Hertz → **PAS DE FIX NÉCESSAIRE** (code déjà correct)
- Formule couple → OK pour jouet, documenter approximation

---

## RÉSUMÉ ACTIONS → CODE

| # | Action | Bug lié | Priorité | Status |
|---|--------|---------|----------|--------|
| 1 | Exclure camshaft du check OVERSIZED | BUG-012 | P1 | ✅ FAIT |
| 2 | Auto Ø6mm shaft >5 cames | BUG-011 | P1 | ✅ FAIT (`0865043`) |
| 3 | Auto cam_spacing 6mm >6 cames | BUG-012 | P1 | ✅ FAIT (`0865043`) |
| 4 | Mid-bearing wall auto >180mm | BUG-011 | P1 | 🔧 EN COURS |
| 5 | Deflection /2 avec mid-bearing | BUG-011 | P1 | 🔧 EN COURS |
| 6 | Dual-shaft split >6 cames | BUG-012 | P2 | ⬜ FUTUR |
| 7 | Engrenage sync PLA m=1.5 z=20 | BUG-012 | P2 | ⬜ FUTUR |
| 8 | Dual-motor ou réduction | BUG-013 | P2 | ⬜ FUTUR |
| 9 | Hertz formule | — | — | ✅ DÉJÀ CORRECT |
