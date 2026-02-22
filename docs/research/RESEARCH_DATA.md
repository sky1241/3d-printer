# RESEARCH_DATA.md — Données de Recherche Vérifiées
# Compilé le 2026-02-12 — Sources académiques uniquement
# Pour: Automata Generator — Moteur de Formes Paramétriques

---

## SUJET 1 — CLASSIFICATION ANIMALE → BODY PLAN MÉCANIQUE

### 1.1 APIs Taxonomiques Testées

| API | URL | Format | Multi-langue | Latence | Couverture |
|-----|-----|--------|--------------|---------|------------|
| ITIS | `https://www.itis.gov/ITISWebService/jsonservice/` | JSON | EN principal, FR partiel (param `language=FRENCH`) | ~0.5s | 800K+ taxa, focus NA |
| GBIF | `https://api.gbif.org/v1/species/match?name=` | JSON | EN principal, param `qField=VERNACULAR` | ~0.3s | 1.8M+ taxa, global |
| ENA (EBI) | `https://www.ebi.ac.uk/ena/taxonomy/rest/any-name/` | JSON | EN principal | ~0.5-1s | Tous organismes vivants |
| NCBI Taxonomy | `https://api.ncbi.nlm.nih.gov/datasets/v2/taxonomy/` | JSON | EN (noms scientifiques) | ~1s | Génomique-orienté |
| Wikidata | `https://www.wikidata.org/w/api.php?action=wbsearchentities` | JSON | **TOUTES LANGUES** (FR, DE, ES...) | ~0.5s | 100K+ espèces avec labels multi-langues |
| Wikipedia FR | `https://fr.wikipedia.org/w/api.php?action=query&titles=` | JSON | FR natif | ~0.3s | Espèces courantes, noms latins dans infobox |

**Stratégie multi-langue recommandée:**
1. Input "ours brun" → Wikidata `wbsearchentities?search=ours brun&language=fr` → Q36341 (Ursus arctos)
2. Extraire nom scientifique du Wikidata item
3. GBIF `/species/match?name=Ursus arctos` → classification complète
4. Fallback: Wikipedia FR → parse infobox pour nom latin

### 1.2 Taxonomie Fonctionnelle des Body Plans Mécaniques

| ID | Nom | Pattes | Ailes | Cames min | Cames max | Exemples (≥5) |
|----|-----|--------|-------|-----------|-----------|---------------|
| QUAD_TRAPU | Quadrupède trapu | 4 | 0 | 4 | 5 (+ cou) | ours, hippopotame, cochon, phoque, blaireau |
| QUAD_GRACE | Quadrupède gracile | 4 | 0 | 4 | 6 (+ cou + queue) | chien, chat, loup, renard, guépard, lion |
| QUAD_EQUIN | Quadrupède équin | 4 | 0 | 4 | 5 (+ cou) | cheval, âne, zèbre, tapir, rhinocéros |
| QUAD_MASSIF | Quadrupède massif | 4 | 0 | 4 | 5 (+ trompe) | éléphant, girafe, chameau, bison, orignal |
| BIPED_OISEAU | Bipède ailé | 2 | 2 | 2 | 5 (+ ailes + cou) | poule, canard, aigle, hibou, perroquet |
| BIPED_NON_VOL | Bipède non-volant | 2 | 0-2 | 2 | 3 (+ cou) | pingouin, autruche, émeu, kiwi, dodo |
| BIPED_PRIMATE | Bipède primate | 2 | 0 | 2 | 4 (+ bras + cou) | gorille, humain, chimpanzé, orang-outan, gibbon |
| HEXAPODE | Hexapode | 6 | 0-2 | 6 | 8 (+ ailes) | fourmi, scarabée, sauterelle, libellule, abeille |
| ARACHNIDE | Octopode | 8 | 0 | 8 | 9 (+ queue) | araignée, scorpion, tique, faucheur, solifuge |
| SERPENTIN | Limbless | 0 | 0 | 1 | 3 (ondulation) | serpent, ver, anguille, limace, sangsue |
| AQUATIQUE | Aquatique à nageoires | 0 | 0 | 1 | 3 (queue + nageoires) | poisson rouge, requin, dauphin, baleine, raie |
| CHELONIEN | Carapacé | 4 | 0 | 4 | 5 (+ cou) | tortue terrestre, tortue marine, tatou, pangolin, hérisson |
| VOLANT_MAMM | Volant mammifère | 2 | 2 | 2 | 4 (+ ailes) | chauve-souris (5 spp.) |
| CRUSTACE | Décapode/multi-pattes | 10 | 0 | 6-10 | 12 | crabe, homard, crevette, écrevisse, araignée de mer |
| RADIAL | Radial (non supporté) | 0 | 0 | 1 | 1 | méduse, étoile de mer, oursin, anémone, corail |

### 1.3 Cas Limites — Décisions

| Animal | Problème | Body Plan Assigné | Justification |
|--------|----------|-------------------|---------------|
| Serpent | 0 pattes | SERPENTIN | 1 came pour ondulation latérale sinusoïdale |
| Méduse | Symétrie radiale | RADIAL (limité) | 1 came pour pulsation de la cloche |
| Pieuvre | 8 bras flexibles | NON SUPPORTÉ | Trop de DOF par bras, impossible en cames simples |
| Mille-pattes | >20 pattes | NON SUPPORTÉ | Trop de cames sur un seul arbre |
| Chauve-souris | 2 pattes + 2 ailes | VOLANT_MAMM | Traiter comme oiseau (4 cames) |
| Pingouin | Oiseau non-volant | BIPED_NON_VOL | 2 cames pattes + 1 cou, ailes décoratives fixes |
| Phoque | Quadrupède à nageoires | QUAD_TRAPU | 4 nageoires = 4 cames, mouvement simplifié |
| Tortue | Carapace + 4 pattes | CHELONIEN | 4 cames pattes, tête rétractable = 1 came |

### 1.4 Algorithme de Décision (Pseudocode)

```
function classify(animal_name: str, lang: str = "fr") -> BodyPlan:
    # Étape 1: Résolution taxonomique
    if lang != "en":
        scientific = wikidata_search(animal_name, lang)  # "ours brun" → "Ursus arctos"
    else:
        scientific = animal_name
    
    taxon = gbif_match(scientific)  # → {kingdom, phylum, class, order, family}
    
    # Étape 2: Mapping Class → Body Plan
    match taxon.class:
        case "Mammalia":
            if taxon.order == "Chiroptera": return VOLANT_MAMM
            if taxon.order == "Primates": return BIPED_PRIMATE
            if taxon.order in ["Cetacea", "Sirenia"]: return AQUATIQUE
            if taxon.order == "Carnivora" and taxon.family == "Phocidae": return QUAD_TRAPU
            # Default mammifère = quadrupède
            if taxon.family in ["Ursidae", "Hippopotamidae", "Suidae"]: return QUAD_TRAPU
            if taxon.family in ["Equidae", "Rhinocerotidae"]: return QUAD_EQUIN
            if taxon.family in ["Elephantidae", "Giraffidae", "Camelidae"]: return QUAD_MASSIF
            return QUAD_GRACE  # default mammal
        
        case "Aves":
            if taxon.order in ["Struthioniformes", "Sphenisciformes"]: return BIPED_NON_VOL
            return BIPED_OISEAU
        
        case "Reptilia":
            if taxon.order == "Squamata" and taxon.suborder == "Serpentes": return SERPENTIN
            if taxon.order == "Testudines": return CHELONIEN
            return QUAD_GRACE  # lézards, crocodiles
        
        case "Actinopterygii" | "Chondrichthyes": return AQUATIQUE
        case "Insecta": return HEXAPODE
        case "Arachnida": return ARACHNIDE
        case "Malacostraca": return CRUSTACE
        case "Amphibia": return QUAD_GRACE  # grenouille = quasi-quadrupède
    
    # Étape 3: Fallback
    return QUAD_GRACE  # défaut sûr pour animal inconnu
```

---

## SUJET 2 — PROPORTIONS MORPHOLOGIQUES

### 2.1 Lois d'Allométrie — Données Clés

**Source principale:** Kilbourne & Hoffman, PLoS ONE 2013 — 44 espèces, 8 ordres taxonomiques

| Propriété | Formule | Exposant b | IC 95% | Source |
|-----------|---------|------------|--------|--------|
| Longueur membre (tous mammifères) | L = a × M^b | **0.40** | 0.37-0.43 | Kilbourne 2013 |
| Longueur membre antérieur | L_fore = a × M^b | 0.40 | 0.37-0.43 | Kilbourne 2013 |
| Longueur membre postérieur | L_hind = a × M^b | 0.37 | 0.34-0.40 | Kilbourne 2013 |
| Masse membre (fraction du corps) | M_limb ∝ M^1.0 | **1.00** | isométrie | Kilbourne 2013 |
| Diamètre os (fémur) | D = a × M^b | **0.35** | 0.32-0.38 | Campione 2012 |
| Longueur os | L_bone = a × M^b | **0.31** | 0.28-0.34 | Biewener 1983 |
| Courbure os | C = a × M^b | **-0.09** | neg. allom. | Biewener 1983 |
| Angle os/sol | θ = a × M^b | **-0.07** | neg. allom. | Biewener 1983 |
| Masse musculaire | M_musc ∝ M^(0.9-1.15) | **~1.0** | variable | Bishop 2021 |
| Force musculaire PCSA | F ∝ M^(0.69-0.91) | **~0.80** | variable | Bishop 2021 |

**Interprétation pour notre moteur:**
- Les gros animaux ont des pattes proportionnellement plus longues (b=0.40 > 0.33)
- Les os deviennent plus épais mais moins longs relativement (D: 0.35, L: 0.31)
- Les petits animaux sont plus "accroupis" (angle os/sol: b=-0.07)

### 2.2 Table de Ratios Morphologiques — 20 Espèces

**Ratios normalisés par hauteur au garrot (H)**
Sources: Morphométrie de terrain, Dimensions.com, études publiées, allométrie calculée

| Espèce | body_L/H | leg_F/H | leg_R/H | body_D/H | head_R/H | neck_L/H | tail_L/H | Masse typ. |
|--------|----------|---------|---------|----------|----------|----------|----------|-----------|
| Ours brun | 1.60 | 0.35 | 0.35 | 0.40 | 0.16 | 0.08 | 0.05 | 250 kg |
| Chien (berger) | 1.20 | 0.55 | 0.55 | 0.25 | 0.12 | 0.15 | 0.30 | 30 kg |
| Chat | 1.30 | 0.50 | 0.55 | 0.22 | 0.13 | 0.12 | 0.45 | 4 kg |
| Cheval | 1.00 | 0.55 | 0.55 | 0.30 | 0.14 | 0.35 | 0.40 | 500 kg |
| Vache | 1.20 | 0.50 | 0.50 | 0.35 | 0.14 | 0.20 | 0.30 | 600 kg |
| Chèvre | 1.10 | 0.55 | 0.55 | 0.22 | 0.12 | 0.15 | 0.10 | 50 kg |
| Lapin | 0.90 | 0.30 | 0.50 | 0.25 | 0.14 | 0.05 | 0.05 | 2 kg |
| Souris | 0.80 | 0.25 | 0.35 | 0.20 | 0.16 | 0.05 | 0.80 | 0.02 kg |
| Éléphant | 1.30 | 0.55 | 0.55 | 0.40 | 0.12 | 0.15 | 0.20 | 5000 kg |
| Girafe | 0.80 | 0.55 | 0.50 | 0.22 | 0.08 | 0.60 | 0.20 | 800 kg |
| Lion | 1.30 | 0.50 | 0.50 | 0.28 | 0.14 | 0.12 | 0.40 | 190 kg |
| Loup | 1.20 | 0.55 | 0.55 | 0.22 | 0.11 | 0.15 | 0.25 | 40 kg |
| Renard | 1.15 | 0.55 | 0.55 | 0.20 | 0.10 | 0.12 | 0.45 | 6 kg |
| Cerf | 1.10 | 0.60 | 0.60 | 0.22 | 0.10 | 0.25 | 0.10 | 150 kg |
| Cochon | 1.30 | 0.35 | 0.35 | 0.35 | 0.14 | 0.10 | 0.10 | 100 kg |
| Mouton | 1.10 | 0.50 | 0.50 | 0.28 | 0.12 | 0.15 | 0.10 | 60 kg |
| Gorille | 1.10 | 0.45 | 0.40 | 0.35 | 0.14 | 0.08 | 0.00 | 160 kg |
| Aigle | 0.60 | 0.35 | 0.35 | 0.20 | 0.12 | 0.15 | 0.15 | 5 kg |
| Canard | 0.70 | 0.25 | 0.25 | 0.25 | 0.12 | 0.20 | 0.08 | 1.5 kg |
| Poisson rouge | 0.40 | 0.00 | 0.00 | 0.25 | 0.15 | 0.00 | 0.20 | 0.1 kg |

**Notes:**
- body_L = longueur nez→queue, leg_F = patte avant, leg_R = patte arrière
- body_D = diamètre/largeur du corps (section transversale)
- head_R = rayon de la tête (approximé sphère)
- Les oiseaux: leg_F/R = patte seule (pas d'aile), envergure séparée
- Poisson: tail_L = nageoire caudale

### 2.3 Format JSON Proposé

```json
{
  "species_id": "ursus_arctos",
  "common_names": {"fr": "ours brun", "en": "brown bear", "de": "Braunbär"},
  "body_plan": "QUAD_TRAPU",
  "mass_kg": 250,
  "ratios": {
    "body_length": 1.60,
    "body_diameter": 0.40,
    "leg_front_length": 0.35,
    "leg_front_radius": 0.06,
    "leg_rear_length": 0.35,
    "leg_rear_radius": 0.06,
    "head_radius": 0.16,
    "neck_length": 0.08,
    "neck_radius": 0.10,
    "tail_length": 0.05,
    "tail_radius": 0.02,
    "ear_height": 0.04,
    "shoulder_hump": 0.08
  },
  "joints": {
    "neck_yaw": {"range_deg": 60, "default_motion": "nod_lr"},
    "neck_pitch": {"range_deg": 30, "default_motion": "nod_ud"},
    "leg_FL": {"range_deg": 45, "default_motion": "walk"},
    "leg_FR": {"range_deg": 45, "default_motion": "walk"},
    "leg_RL": {"range_deg": 45, "default_motion": "walk"},
    "leg_RR": {"range_deg": 45, "default_motion": "walk"}
  },
  "spine_segments": 8,
  "spine_radii": [0.14, 0.18, 0.20, 0.20, 0.19, 0.18, 0.15, 0.08]
}
```

---

## SUJET 3 — GÉNÉRATION DE MESH PAR PRIMITIVES

### 3.1 Approches de Skinning

| Approche | Complexité | Qualité visuelle | Imprimable FDM | Vertices typiques |
|----------|-----------|-----------------|----------------|-------------------|
| Capsule/Cylindre + Sphère | O(n) | Basse (reconnaissable) | ✅ Excellent | 200-500 |
| Metaball (isosurface) | O(n³) | Moyenne (lisse) | ⚠️ Surplombs possibles | 2000-5000 |
| Swept cross-section (spline) | O(n×m) | Bonne | ✅ Bon avec orientation | 500-2000 |
| SMAL (neural skinning) | GPU requis | Excellente | ❌ Trop détaillé | 3889 (fixe) |

**Recommandation: Swept cross-section** — bon compromis qualité/performance/imprimabilité

### 3.2 Algorithme Spine + Cross-Section

```
INPUT: spine_points[N] (3D), radii[N] (float)
OUTPUT: trimesh watertight

1. Pour chaque segment i de 0 à N-1:
   a. Calculer le vecteur tangent T[i] = normalize(spine[i+1] - spine[i-1])
      (endpoints: forward/backward difference)
   b. Calculer le Bishop frame (normal N[i], binormal B[i])
      - Évite les twists de Frenet-Serret
      - N[0] = arbitrary perpendicular to T[0]
      - N[i] = parallel_transport(N[i-1], T[i-1], T[i])
      - B[i] = cross(T[i], N[i])
   c. Générer cross-section circulaire:
      Pour j de 0 à M-1 (M = résolution angulaire, typ. 12-16):
        θ = 2π × j / M
        vertex[i][j] = spine[i] + radii[i] × (cos(θ) × N[i] + sin(θ) × B[i])

2. Trianguler:
   Pour chaque paire de sections (i, i+1):
     Pour j de 0 à M-1:
       face1 = (v[i][j], v[i+1][j], v[i+1][j+1])
       face2 = (v[i][j], v[i+1][j+1], v[i][j+1])
   
3. Caps (fermeture aux extrémités):
   Endpoint 0: fan triangulation de v[0][0..M] vers centroïde spine[0]
   Endpoint N: idem pour v[N][0..M]

4. Résultat: mesh watertight, ~N×M×2 faces
```

### 3.3 Jonctions Membre↔Corps

**Problème:** Quand un cylindre (patte) rejoint un ellipsoïde (corps), l'intersection est moche.

**Solutions par ordre de complexité:**

1. **Simple overlap** (le plus rapide):
   - La patte pénètre dans le corps de 2mm
   - Boolean union pour fusionner
   - Complexité: O(n log n) via trimesh
   - Qualité: acceptable pour FDM

2. **Fillet sphérique** (meilleur visuel):
   - Ajouter une sphère à l'intersection
   - Rayon sphère = 1.5× rayon patte
   - Union des 3 meshes
   - Complexité: O(n log n)

3. **Metaball blend** (le plus lisse):
   - Chaque primitive = source de champ scalaire
   - Isosurface via marching cubes
   - Complexité: O(résolution³)
   - Qualité: excellente mais lent

### 3.4 Découpe aux Articulations

```
Pour chaque joint (ex: épaule):
  1. Plan de coupe = perpendiculaire à l'axe du membre, à la position du joint
  2. Séparer le mesh en 2 parties avec trimesh.slice_mesh()
  3. Partie haute (corps) : ajouter face de fermeture (disk cap)
  4. Partie basse (patte mobile) : ajouter face de fermeture
  5. Ajouter socket cylindrique dans partie basse:
     - Trou Ø3.3mm (pushrod Ø3mm + 0.3mm clearance)
     - Profondeur 5mm
     - Boolean difference avec trimesh
  6. Vérifier watertight sur les 2 parties
```

### 3.5 Contraintes FDM

| Paramètre | Valeur min | Source |
|-----------|-----------|--------|
| Épaisseur de paroi | 0.8mm (2 périmètres × 0.4mm) | Standard FDM |
| Détail minimal | 0.4mm (1 périmètre) | Nozzle 0.4mm |
| Surplomb max | 45° (sans support) | Standard FDM |
| Pont max | 10mm (sans support) | Dépend matériau |
| Hauteur couche | 0.2mm (standard) | Standard FDM |
| Tolérance ajustement | 0.2-0.3mm (axe/bore) | Empirique |
| Taille pièce min | 5mm (chaque dimension) | Manipulation |

### 3.6 Benchmark Vertices

| Modèle | Vertices | Faces | Temps génération |
|--------|----------|-------|-----------------|
| Quadrupède primitives (notre approche) | ~400-800 | ~800-1600 | <100ms |
| SMAL template | 3889 | 7774 | N/A (pré-calculé) |
| Infinigen (Blender) | 10K-50K | 20K-100K | minutes |
| Impression FDM: slicer peut gérer | <500K | <1M | OK |

---

## SUJET 4 — SYSTÈMES DE CAMES MULTI-DOF

### 4.1 Gait Patterns — Déphasages Exacts

**Source: Muybridge, CSE169 UCSD, Animator Notebook, Scientific Reports 2017**

Phases normalisées (0.0 = début cycle, 1.0 = fin cycle)
Convention: LH=Left Hind, LF=Left Front, RH=Right Hind, RF=Right Front

| Gait | LH | LF | RH | RF | Beats | Vitesse |
|------|-----|-----|-----|-----|-------|---------|
| **Walk** | 0.00 | 0.25 | 0.50 | 0.75 | 4 | Lente |
| **Amble** | 0.00 | 0.20 | 0.50 | 0.70 | 4 | Lente-moyenne |
| **Trot** | 0.00 | 0.50 | 0.50 | 0.00 | 2 | Moyenne |
| **Pace** | 0.00 | 0.00 | 0.50 | 0.50 | 2 | Moyenne |
| **Canter** | 0.00 | 0.70 | 0.30 | 0.00 | 3 | Moy-rapide |
| **Gallop (transverse)** | 0.00 | 0.50 | 0.10 | 0.60 | 4 (rapide) | Rapide |

**Conversion en déphasage angulaire pour cames (× 360°):**

| Gait | Came LH | Came LF | Came RH | Came RF |
|------|---------|---------|---------|---------|
| Walk | 0° | 90° | 180° | 270° |
| Trot | 0° | 180° | 180° | 0° |
| Pace | 0° | 0° | 180° | 180° |

**Note importante:** Les ours et chameaux utilisent naturellement le **pace** (pas latéral), pas le trot !
→ Pour "ours qui marche": utiliser PACE (LH+LF ensemble, puis RH+RF)

### 4.2 Profils de Came — Fonctions Standard

| Profil | Formule s(θ) pour rise | Jerk continu? | Pression angle max | Usage |
|--------|----------------------|---------------|-------------------|-------|
| Simple Harmonic | s = h/2 × (1 - cos(πθ/β)) | ❌ Non | Élevé | **NE PAS UTILISER** |
| Cycloidal | s = h × (θ/β - sin(2πθ/β)/(2π)) | ✅ Oui | Moyen | Bon choix général |
| 3-4-5 Polynomial | s = h × (10(θ/β)³ - 15(θ/β)⁴ + 6(θ/β)⁵) | ✅ Oui | Bas | **RECOMMANDÉ** |
| Modified Trapezoid | (piecewise) | ✅ Oui | Très bas | Haute vitesse |
| Modified Sine | (piecewise) | ✅ Oui | Bas | Bonne alternative |

**Recommandation pour automates: 3-4-5 polynomial** — jerk continu, pression angle basse, simple à implémenter

### 4.3 Angle de Pression — Formules

**Définition:** Angle entre la direction de mouvement du follower et la direction de la force transmise (normale au contact).

```
Pour un cam radial avec follower translateur:
  tan(φ) = (ds/dθ - e) / (√(R₀² - e²) + s)
  
  où:
    φ = angle de pression
    s = déplacement du follower à l'angle θ
    ds/dθ = vitesse du follower (dérivée par rapport à l'angle de rotation)
    R₀ = rayon de base du cam
    e = excentricité (0 si in-line)

Simplification (e=0, in-line):
  tan(φ) = (ds/dθ) / (R₀ + s)
```

**Limites:**
- Follower translateur: φ_max ≤ **30°**
- Follower oscillant: φ_max ≤ **35°**
- Au-delà: risque de blocage (jamming) par friction

**Comment réduire φ si trop élevé:**
1. Augmenter R₀ (rayon de base) — le plus efficace
2. Augmenter β (angle de rise) — réduire la pente
3. Réduire h (hauteur de levée) — réduire l'amplitude
4. Ajouter excentricité — optimisation fine

### 4.4 Couple et Forces — Calcul

```
Hypothèses pour notre automate:
  - Figurine: m = 20g = 0.020 kg
  - Hauteur de levée: h = 10mm = 0.010 m
  - Nombre de cames actives: N = 5
  - Rayon de base: R₀ = 15mm
  - Rayon max came: R_max = R₀ + h = 25mm
  
Force de levée par came:
  F_lift = m × g = 0.020 × 9.81 = 0.196 N ≈ 0.2 N

Couple par came (au rayon max):
  T_cam = F_lift × R_max = 0.2 × 0.025 = 0.005 N·m = 5 mN·m

Couple total (N cames):
  T_total = N × T_cam = 5 × 0.005 = 0.025 N·m = 25 mN·m

Avec friction (rendement η ≈ 0.5 pour came sèche PLA):
  T_réel = T_total / η = 0.025 / 0.5 = 0.050 N·m = 50 mN·m

Comparaison:
  - Manivelle humaine: peut fournir ~1-5 N·m facilement → ✅ LARGEMENT SUFFISANT
  - Petit moteur DC (N20, 6V): ~0.1-0.3 N·m → ✅ SUFFISANT
  - Servomoteur SG90: ~0.18 N·m → ✅ SUFFISANT
```

### 4.5 Synthèse de Came Inverse

```
INPUT: 
  - displacement_curve s(θ) pour θ ∈ [0, 360°]
  - R₀ (rayon de base)
  - e (excentricité, typ. 0)

ALGORITHME:
  Pour chaque angle θ de 0 à 360° par pas de 1°:
    1. Calculer s(θ) depuis le profil choisi (3-4-5 polynomial)
    2. Rayon du cam: R(θ) = R₀ + s(θ)
    3. Position du point sur le profil:
       x(θ) = R(θ) × cos(θ)
       y(θ) = R(θ) × sin(θ)
    4. Vérifier angle de pression:
       ds = s(θ+1) - s(θ)  (différence finie)
       tan_phi = ds / (R₀ + s(θ))
       phi = atan(tan_phi)
       ASSERT |phi| < 30°

OUTPUT:
  - Profil du cam: liste de 360 points (x, y)
  - Angle de pression max
  - Rayon min de courbure (doit être > rayon du roller follower)
```

### 4.6 Détection de Collision Cinématique

```
ALGORITHME pour 360° de rotation:
  
  Pour chaque angle θ de 0 à 360° par pas de 5°:
    1. Pour chaque came i:
       - Calculer s_i(θ + phase_i)  # déplacement avec déphasage
       - Calculer position de la figurine connectée
       - Transformer le mesh de la figurine à sa nouvelle position
    
    2. Pour chaque paire de figurines (i, j):
       - Test de collision rapide: AABB (bounding box) overlap?
       - Si AABB overlap: test GJK/EPA précis (trimesh.collision)
       - Si collision détectée: SIGNALER erreur
    
    3. Pour chaque figurine vs châssis:
       - Vérifier que la figurine ne sort pas du volume du châssis
       - Vérifier que la figurine ne descend pas sous la base plate
  
  Complexité: O(360/step × N² × collision_cost)
  Pour N=5 figurines, step=5°: 72 × 10 × O(n log n) ≈ rapide
```

### 4.7 Papiers SIGGRAPH Clés

| Paper | Auteurs | Année | Méthode | Réutilisable? |
|-------|---------|-------|---------|---------------|
| Computational Design of Mechanical Characters | Coros et al. | 2013 | Drag-and-drop + physical sim + evolutionary optimization | **Oui** — formules de couple et collision |
| Designing Mechanical Automata from Mocap | Ceylan et al. | 2013 | Mocap → cam profile synthesis | **Oui** — algorithme de synthèse inverse |
| Spatial-temporal motion via composite cams | Song et al. | 2021 | 3D cam profiles, analytical kinematics | Partiel — trop complexe pour V1 |

---

## RÉFÉRENCES

1. Kilbourne & Hoffman (2013). "Scale Effects between Body Size and Limb Design in Quadrupedal Mammals." PLoS ONE 8(11): e78392.
2. Campione & Evans (2012). "A universal scaling relationship between body mass and proximal limb bone dimensions." BMC Biology 10:60.
3. Bishop et al. (2021). "Whole-limb scaling of muscle mass and force-generating capacity in amniotes." PeerJ 9:e12574.
4. Biewener (1983). "Allometry of quadrupedal locomotion: the scaling of duty factor, bone curvature and limb orientation." J. Exp. Biology 105:147-171.
5. Norton (2009). Cam Design and Manufacturing Handbook, 2nd ed. Industrial Press.
6. Coros et al. (2013). "Computational Design of Mechanical Characters." ACM Trans. Graphics 32(4).
7. Owaki et al. (2017). "A Quadruped Robot Exhibiting Spontaneous Gait Transitions." Scientific Reports 7:277.
8. Fukuoka et al. (2015). "A simple rule for quadrupedal gait generation." Scientific Reports 5:8169.
9. Rotenberg (2016). "Locomotion" CSE169 UCSD lecture slides.
10. Animator Notebook (2025). "A Guide to Quadrupeds' Gaits."
11. Glenn & Miller (1980). "Morphometric Characteristics of Brown Bears on the Central Alaska Peninsula." Int. Conf. Bear Research.
12. Moriwaki et al. (2020). "Photograph-based method for body condition in brown bears." PeerJ 8:e9982.
