# 🔬 DEEP RESEARCH RESULTS — Dual-Shaft & Engrenages PLA
# Source: ChatGPT Deep Research sur DEEP_RESEARCH_PROMPT_v3.md
# Date: 13 février 2026
# Lié aux bugs: BUG-011 (shaft), BUG-012 (oversized), BUG-013 (motor)
# Espèces concernées: spider, octopus, dragon, crab, lobster, scorpion (6/17)

---

## SYNTHÈSE DÉCISIONNELLE — Ce qu'on injecte dans le code

### DÉCISION 1: DUAL-SHAFT (BUG-011 + BUG-012)
**Architecture retenue:** 2 arbres parallèles synchronisés par engrenages
- Module engrenage: **1.5mm** (testé FDM, dents assez larges pour PLA)
- Nombre de dents: **20** (>13 min pour 20°)
- Angle de pression: **20°** standard (pas de modif FDM nécessaire)
- Backlash: **0.2mm** (compromis 0.1-0.3)
- Entraxe: **30mm** (d1+d2)/2 = m×(z1+z2)/2 = 1.5×40/2 = 30mm
- Erreur de phase acceptable: **±5°** (0.003s à 30RPM = imperceptible)
- Ratio split: **50/50** (cames réparties équitablement)

### DÉCISION 2: ARBRE Ø6mm (déjà implémenté, confirmé)
- I(Ø6) = 63.62 mm⁴ vs I(Ø4) = 12.57 mm⁴ → **5.06× moins de flèche**
- Coût: ~3-5€/m (tige acier plein)
- ⚠ Ø6 sur 434mm fléchit encore ~1-2mm → dual-shaft obligatoire pour scorpion

### DÉCISION 3: PALIER INTERMÉDIAIRE
- Palier au milieu → L_effectif = L/2 → **flèche ÷16**
- Option retenue: **trou Ø6.5mm dans mur PLA** (simple, pas de hardware)
- Alternative premium: roulement MR84 (4×8×3mm) → μ≈0.01
- Friction PLA/acier: μ≈0.2-0.3 (acceptable à 30-60RPM)

### DÉCISION 4: MOTEUR (BUG-013)
- N20 168:1 → couple nominal ~10.4 mN·m, stall ~196 mN·m
- Couple utile continu: ~30-50% du stall = **60-100 mN·m**
- Nos besoins: 97-127 mN·m → **N20 seul insuffisant pour scorpion/lobster**
- Solution: dual-shaft = 2 moteurs, chacun ~50-65 mN·m → dans les clous
- Alternative: étage réduction 2:1 imprimé avant l'arbre

---

## DONNÉES BRUTES PAR DOMAINE

### D1 — DUAL-SHAFT
| Paramètre | Valeur | Source |
|-----------|--------|--------|
| Module engrenage PLA | ≥1.0, recommandé 1.5 | Tests FDM, forums |
| Dents minimum (20°) | 13 | Géométrie involute |
| Dents minimum (25°) | 9 | Géométrie involute |
| Backlash PLA | 0.1-0.3mm | Projets Thingiverse |
| Entraxe (m=1.5, z=20) | 30mm | (d1+d2)/2 |
| Erreur phase à 30RPM | 5° = 0.003s | Calcul |
| Profil | Involute standard | Pas de modif FDM |
| Angle pression | 20° standard | Shigley |

### D2 — DEFLEXION ARBRE  
| Paramètre | Valeur | Source |
|-----------|--------|--------|
| E acier doux (étiré) | 200 GPa | Handbook |
| E laiton CuZn37 | 105-110 GPa | Handbook |
| I Ø4mm | 12.57 mm⁴ | π×4⁴/64 |
| I Ø6mm | 63.62 mm⁴ | π×6⁴/64 |
| δ Ø4mm L=220mm F=5N | 0.42mm | F×L³/(48EI) |
| δ Ø4mm L=253mm F=5N | 0.64mm | idem |
| L_max sans palier (<0.3mm) | ~180mm | Estimé |
| Palier milieu → facteur | ÷16 | L/2 → (L/2)³ = L³/8 × 2 appuis |
| μ PLA/acier sec | 0.2-0.3 | Mesuré |
| μ bronze Oilite | 0.10-0.15 | Fabricant |
| μ roulement MR84 | ~0.01 | Fabricant |
| Tige Ø6mm prix | 3-5€/m | CommentFer |

### D3 — COUPLE MOTEUR
| Paramètre | Valeur | Source |
|-----------|--------|--------|
| N20 168:1 stall (3V) | 196 mN·m | Zhaowei |
| N20 168:1 nominal | 10.4 mN·m | Zhaowei |
| N20 continu safe | 30-50% stall = 60-100 mN·m | Pratique |
| 28BYJ-48 holding | 34.3 mN·m | Welten Motors |
| Nos besoins max | 127 mN·m (scorpion) | Mesuré |
| Dual-shaft split | ~65 mN·m/moteur | Estimé |

### D4 — PROJETS EXISTANTS
- **AUCUN projet open-source trouvé avec >6 cames sur dual-shaft**
- Projets courants: 1-5 cames sur arbre unique
- gzumwalt (Thingiverse): automates simples, 1-3 cames
- Rob Ives: carton/PLA, <6 cames
- Wintergatan: trains d'engrenages mais pas cames multiples
- → **On est pionniers sur ce problème**

### D5 — VALIDATION FORMULES
| Formule | Verdict | Correction |
|---------|---------|------------|
| δ=F×L³/(48EI) charge centrée | ✅ Correct | Pour N charges: superposition Σδᵢ |
| Hertz σ_H=0.418×√(...) | ❌ **Faux** | Coeff correct: 1/√π ≈ 0.564 |
| E* = E₁×E₂/(E₁+E₂) | ✅ Approx OK | E*≈3.44 GPa (acier+PLA) |
| T = F×(Rb+h)×tan(φ) | ⚠ Approximatif | Surestime à grand φ, OK pour jouet |

---

## PLAN D'IMPLÉMENTATION — DUAL-SHAFT

### Phase 1: Logique de split (code Python)
```
SI n_cams > MAX_CAMS_PER_SHAFT (6):
  n_shaft_1 = n_cams // 2
  n_shaft_2 = n_cams - n_shaft_1
  
  # Générer 2 ChassisConfig parallèles
  # Entraxe = 30mm (m=1.5, z=20)
  # Chaque arbre: longueur = n_shaft_i × cam_spacing + margins
  # Sync gear pair: 2× engrenage z=20, m=1.5
```

### Phase 2: Pièces à générer
1. **Sync gear × 2** — engrenage involute z=20, m=1.5, épaisseur 8mm, bore D-flat
2. **Mur central** — bearing wall entre les 2 arbres (2 trous)
3. **Base plate élargie** — accueillir 2 arbres à 30mm d'entraxe
4. **Motor mount × 2** ou **1 moteur + réduction**

### Phase 3: Seuils
| Paramètre | Seuil | Action |
|-----------|-------|--------|
| n_cams > 6 | → dual-shaft | Split en 2 arbres |
| shaft_length > 180mm | → mid-bearing | Palier intermédiaire |
| torque > 80 mN·m | → dual motor ou réduction | Split couple |
| shaft_length > 220mm | → ERREUR si pas dual | Bloquant |

---

## CORRECTIONS À APPLIQUER AU CODE

### FIX-HERTZ: Formule de Hertz incorrecte
- **Avant:** σ_H = 0.418 × √(F × E* / (L × R*))
- **Après:** σ_H = √(E* × F / (π × L × R*))  [coeff ≈ 0.564]
- Fichier: automata_unified_v4.py, chercher "0.418" ou "hertz"
- Commit associé: à faire

### FIX-TORQUE: Formule couple approximative
- T = F × (Rb+h) × tan(φ) → OK pour jouet, garder mais documenter
- Ajouter warning dans le code: "approximation, surestime à grand φ"

### FIX-DEFLECTION: Superposition pour N charges
- Vérifier qu'on fait bien Σδᵢ et pas juste δ_max
- Formule par charge: δᵢ = Fᵢ×a²ᵢ×b²ᵢ/(3×E×I×L) (charge à distance aᵢ du support)

---

## LIENS COMMITS ↔ BUGS ↔ RESEARCH

| Bug | Commit fixé | Research utilisée | Status |
|-----|------------|-------------------|--------|
| BUG-010 | `f946ed2` | — (spatial fix) | ✅ DONE |
| BUG-011 SHAFT | `0865043` (Ø6mm) | D2 confirmé | ✅ Partiel (3/11 restent) |
| BUG-012 OVERSIZED | — | D1 dual-shaft | 🔴 À IMPL |
| BUG-013 MOTOR | — | D3 dual-motor | 🔴 À IMPL |
| FIX-HERTZ | — | D5 correction formule | 🔴 À IMPL |
| AUTO Ø6mm | `0865043` | D2 I=63.62mm⁴ | ✅ DONE |
| AUTO spacing | `0865043` | D1 (réduction long.) | ✅ DONE |
