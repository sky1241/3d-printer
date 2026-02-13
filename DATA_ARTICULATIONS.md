# 📊 DATA — Figurines Articulées FDM PLA
# Source: ChatGPT response to PROMPT_FIGURINE_ARTICULEE.md
# Date: 13 février 2026

---

## 1. TYPES D'ARTICULATIONS — RÉSUMÉ TECHNIQUE

### 1.1 Pin Joint (Axe traversant) — ⭐ PRIORITÉ #1
- Axe Ø3-6mm, trou = axe + 0.3mm (jeu radial 0.15mm/côté)
- Amplitude: 0-180° (typique 20-30° chaque côté pour automate)
- Charge: axe Ø4mm → ~450N cisaillement statique (limiter à ~100N pratique)
- Orientation impression: axe HORIZONTAL (parallèle XY)
- CSG: Axe=Cylinder(r=d/2, h=L), Trou=Cylinder(r=(d+0.3)/2, h=L)

### 1.2 Ball Joint (Rotule clipsable)
- Bille ØD, socket = D + 0.1mm, offset axial = 10% de D
- Amplitude: ±45° pitch/roll, ±30° yaw
- Charge: très faible, 2-5N max avant détachement
- Clearance: 0.05mm radial (nominal), 0.02 serré, 0.10 sûr

### 1.3 Living Hinge (Charnière intégrée) — ⚠️ PLA FRAGILE
- Épaisseur: 0.4-0.6mm (≥2 couches à 0.2mm)
- Amplitude: ±90° max (PLA casse vers 90-120°)
- Durée vie: ~20-100 cycles seulement en PLA
- Orientation: pont perpendiculaire au plateau (couches dans épaisseur)

### 1.4 Print-in-place Pivot
- Clearance XY: 0.3mm nominal (0.2 serré, 0.5 sûr)
- Clearance Z: ≥0.15mm (1 layer)
- Amplitude: 360° théorique
- Charge: faible, risque délamination

### 1.5 Cantilever Snap-fit (Languette)
- Épaisseur: ~1.2mm (3×nozzle)
- Longueur: 20-30mm
- Angle insertion: 30-45°
- Force: <10N

### 1.6 Dovetail Slide (Queue d'aronde)
- Angle: 45°
- Clearance: 0.2mm nominal (0.1 serré, 0.3 sûr)
- Course: 10-20mm typique

---

## 2. TABLE MOUVEMENT → ARTICULATION

| Mouvement | Partie | Axe | Joint | Amplitude | Force pushrod |
|-----------|--------|-----|-------|-----------|---------------|
| Hocher tête (nod) | Tête | X (pitch) | Pin joint | ±20-30° | 1-2N |
| Tourner tête (pan) | Tête | Z (yaw) | Rotule/pivot vertical | ±30-45° | 1N |
| Ouvrir mâchoire | Mâchoire | X (pitch) | Living hinge / pivot | ±30-45° | 1-2N |
| Battre ailes | Ailes | Y (roll) | Pivot transversal | ±35° | 2-3N |
| Marcher (lever) | Patte | X (pitch) | Pivot hanche | ~20° | 2-4N |
| Marcher (avancer) | Patte | Y (slide) | Dovetail | 10-20mm | 1-2N |
| Queue up/down | Queue | X (pitch) | Pivot | ±15-20° | 1N |
| Queue left/right | Queue | Z (yaw) | Rotule/pivot | ±30° | 1N |
| Nager (ondulation) | Corps | Alterné | Flexure | ±15-20° | 1-2N |
| Yeux | Yeux | X/Z | Petit pivot | ±15° | <1N |
| Lever bras | Bras | X (pitch) | Pivot | ±45° | 2-3N |
| Pinces | Pince | Z (yaw) | Pivot / living hinge | ±20° | 1N |

---

## 3. CLEARANCES FDM — TABLE COMPLÈTE

### 3.1 Pin Joints (Axe dans trou, rotation libre)
| Axe Ø (mm) | Trou nominal | Trou serré | Trou sûr | Jeu radial nom. |
|------------|-------------|------------|----------|-----------------|
| 3.0 | 3.3 | 3.2 | 3.5 | 0.15 |
| 4.0 | 4.3 | 4.2 | 4.5 | 0.15 |
| 5.0 | 5.3 | 5.2 | 5.5 | 0.15 |
| 6.0 | 6.3 | 6.2 | 6.5 | 0.15 |

### 3.2 Press-fit
- Interférence: -0.05mm (nominal), -0.1mm (serré), 0mm (sûr)
- Profondeur insertion: <2mm

### 3.3 Ball Joints
| Bille Ø | Socket Ø | Offset axial | Clearance rad. |
|---------|----------|-------------|----------------|
| 6.0 | 6.1 | 0.6 (10%) | 0.05 |
| 8.0 | 8.1 | 0.8 (10%) | 0.05 |
| 10.0 | 10.1 | 1.0 (10%) | 0.05 |

### 3.4 Autres
| Config | Clearance nom. | Serré | Sûr |
|--------|---------------|-------|-----|
| Snap-fit fente | 0.3 | 0.2 | 0.5 |
| Living hinge épaisseur | 0.5 | 0.4 | 0.6 |
| Dovetail | 0.2 | 0.1 | 0.3 |
| Print-in-place XY | 0.3 | 0.2 | 0.5 |
| Print-in-place Z | 0.15 | 0.10 | 0.20 |

---

## 4. PUSHROD ROUTING — FORMULES

### 4.1 Formule principale
```
θ = asin(Δh / R)
```
- θ = angle de rotation de la partie mobile (radians)
- Δh = course du pushrod (mm)
- R = bras de levier du joint au point d'attache pushrod (mm)

### 4.2 Configurations
| Config | Conversion | Rapport | Formule |
|--------|-----------|---------|---------|
| Pushrod droit → pivot | Vertical → rotation | 1:1 | θ = asin(Δh/R) |
| Bell-crank (90°) | Vertical → horizontal | V_arm/H_arm | Δx = (H_arm/V_arm)·Δh |
| Bielle oscillante | Vertical → oscillation | ~1:1 | θ ∝ Δh × ratio bras |
| Crank-slider | Vertical → rotation | 1:1 | θ = asin(Δh/R) |
| Parallélogramme | Vertical → vertical | 1:1 | ΔY = ΔY_pushrod |
| Levier déporté | Amplification | R2/R1 | Δout = (R2/R1)·Δh |
| Bowden flexible | Courbe quelconque | 1:1 | Δout = Δin |
| Y-split bifurqué | 1 → 2 synchrones | 1:1 chaque | Identique par branche |

### 4.3 Exemple tortue
- Pushrod: Δh = 8mm
- Bras levier cou: R = 16mm
- θ = asin(8/16) = 30°
- Axe pivot cou: Ø3mm, trou Ø3.3mm
- Hauteur cou: ~50mm au-dessus levier

---

## 5. BODY PLANS — CAMES NÉCESSAIRES

| # | Body plan | Exemple | Cames min | Cames max |
|---|-----------|---------|-----------|-----------|
| 1 | Quadrupède carapace | Tortue | 3 | 6 |
| 2 | Oiseau debout | Poule | 3 | 5 |
| 3 | Oiseau en vol | Aigle | 2 | 3 |
| 4 | Bipède | Humain | 3 | 7 |
| 5 | Quadrupède standard | Chat | 4 | 10 |
| 6 | Poisson/serpent | Poisson | 1 | 3 |
| 7 | Arthropode 6 pattes | Fourmi | 3 | 7 |
| 8 | Araignée 8 pattes | Araignée | 4 | 8 |
| 9 | Crustacé | Crabe | 4 | 12 |
| 10 | Céphalopode | Poulpe | 1 | 1 |
| 11 | Gastéropode | Escargot | 1 | 2 |
| 12 | Dragon/fantaisie | Dragon | 5 | 10 |

---

## 6. DIMENSIONNEMENT PARAMÉTRIQUE — FORMULES

### Pour figurine hauteur H (mm), partie mobile masse M (kg):

| Paramètre | Formule | Exemple (H=45mm) |
|-----------|---------|-------------------|
| Diamètre axe (d) | d ≥ √(4·M·g·L / (π·σ_all)) | M=5g, L=50mm → d≥4.4mm → 5mm |
| Paroi autour trou | ≥ 2×d (minimum 1-2mm) | d=4mm → paroi ≥8mm |
| Longueur pushrod | dist_came→joint + quelques mm | ~60mm (50+10 jeux) |
| Diamètre pushrod (flambage) | d ≥ √(4·F·L²/(π²·E·I)) | E=2.3GPa, L=100mm, F=10N → d≈6mm |
| Living hinge épaisseur | 0.4-0.6mm (≥2 layers) | 0.5mm |
| Ball joint diamètre | ≈ 0.1×H | H=45mm → D≈4-6mm |
| Couple résistant | T = μ·M·g·R (μ PLA≈0.3) | M=5g, R=16mm → T≈0.24mNm |
| Force min pushrod | F ≈ M·g·sinθ + μ·M·g | ~0.04N (+ marge → 0.5-1N) |
| Amplitude angulaire | θ = asin(Δpush / R) | Δ=8mm, R=16mm → 30° |
| Retour mécanisme | Gravité si vertical, friction sinon | Gravité pour tête/queue |

---

## 7. ANTI-PATTERNS FDM — TOP 10

| # | Erreur | Cause | Solution | Cote critique |
|---|--------|-------|----------|---------------|
| 1 | Axes verticaux fragiles | Couches perpendiculaires à charge | Imprimer horizontal | Toujours |
| 2 | Print-in-place fusionné | Surextrusion comble le gap | Calibrer flow, gap ≥0.3mm | 0.2-0.3mm |
| 3 | Axes cassent | Sous-dimensionné | d_min ≥ 2-3mm, congé pied | d≥3mm |
| 4 | Living hinge casse vite | PLA trop cassant | ≥0.4mm, fillets base, <100 cycles | 0.4-0.6mm |
| 5 | Ball joint impossible | Socket trop serré | Clearance 0.1mm, offset 10%Ø | 0.05-0.10mm |
| 6 | Pushrod flambe | Trop fin/long | d≈5-6mm pour 10N/100mm | d≥5mm |
| 7 | Mécanisme bloqué | Friction excessive | Jeu 0.1-0.2mm, silicone sec | 0.15mm |
| 8 | Mouvement mou | Jeu excessif | Réduire clearances, calibrer | balance |
| 9 | Porte-à-faux | Trou s'effondre | Support ou imprimer horizontal | bridges<5mm |
| 10 | Bridges sur trous | Coins déformés | Imprimer axes séparément | bridges<5mm |

---

## 8. PROPRIÉTÉS MATÉRIAUX

| Propriété | PLA | PETG | TPU 95A |
|-----------|-----|------|---------|
| Module Young (GPa) | 2.3 | 1.9 | 0.06 |
| σ rupture (MPa) | 36 | 46 | 24 |
| Allongement (%) | 4 | 6-7 | >500 |
| μ PLA/PLA | 0.3-0.4 | - | - |
| μ PLA/PETG | ~0.3 | - | - |
| Living hinge min (mm) | 0.4-0.6 | 0.4-0.6 | N/A |
| T ramollissement (°C) | 55-60 | 75-85 | 40-50 |
| Fluage | Élevé >30°C | Modéré | Faible |

---

## 9. EXEMPLES CONCRETS COTÉS

### Ex.1 — Tortue hochant la tête (1 came)
- Pivot cou: axe Ø3.0mm, trou Ø3.3mm (clearance 0.3mm)
- Bras levier: R = 16.0mm
- Course pushrod: Δh = 8.0mm
- Amplitude: θ = asin(8/16) = 30°
- Pushrod: Ø5mm, longueur ~60mm
- Hauteur cou: ~50mm au-dessus levier
- Retour: gravité (tête penche vers l'avant)

### Ex.2 — Oiseau battant des ailes (2 cames)
- Pivot aile: axe Ø4.0mm, trou Ø4.3mm
- Bras levier aile: R = 20.0mm
- Course pushrod: Δh = 12.0mm
- Amplitude: θ = asin(12/20) ≈ 37°
- Synchro: 1 came + Y-split OU 2 cames opposées

### Ex.3 — Chat marchant (4 cames)
- Pivot hanche: axe Ø4.0mm, trou Ø4.3mm
- Bras hanche: R = 15.0mm
- Course pushrod: Δh = 4.0mm
- Amplitude: θ = asin(4/15) ≈ 15°
- Gait: FL+RR en phase, FR+RL déphasées 180°
- Genou: print-in-place ou 2e axe Ø3mm
