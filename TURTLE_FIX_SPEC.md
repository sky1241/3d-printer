# 🐢 TURTLE FIX SPEC — Faire fonctionner la tortue pour de vrai
# Date: 13 février 2026
# Objectif: Un automate tortue imprimable, assemblable, qui tourne la manivelle et la tête bouge
# Philosophie: hardcode ce qu'il faut, un modèle qui MARCHE > 100 modèles théoriques

---

## ÉTAT ACTUEL — Ce qui marche vs ce qui marche pas

### ✅ CE QUI MARCHE (prouvé)
- **Profil de came**: rise 120° → dwell 60° → fall 120° → dwell 60°, poly4567 law
- **Came mesh**: Rb=8.31mm, lift=8mm, φ_max=30°, watertight, 3244 faces, D-flat bore Ø4mm
- **Châssis**: base_plate 80×60×3mm, 2 walls 7.6×50×70mm, bracket, shaft holes Ø4.7mm
- **Arbre**: Ø4mm acier, 34.6mm long, trous dans walls + bracket
- **Manivelle**: imprimée PLA, connectée à l'arbre
- **Levier**: 20mm long, pivot à Z=47mm sur bracket
- **Maths contraintes**: 73 checks passent, 0 erreurs
- **Principe mécanique**: manivelle → arbre → came → follower → levier → pushrod → tête (prouvé par animation)

### ❌ CE QUI MARCHE PAS (bloquant pour impression)
| # | Bug | Impact | Cause racine |
|---|-----|--------|-------------|
| T1 | **Pushrod traverse le corps** | Pièce impossible à assembler | Routing droit lever→neck sans contourner le body |
| T2 | **Figurine sans support physique** | La tortue tombe au montage | Pas de plateau/shelf, juste un socket pushrod |
| T3 | **Tête pas connectée au pushrod** | Le mouvement se transmet pas | Le pushrod va au bottom du neck, mais le pin joint est au milieu du neck — pas de transmission |
| T4 | **Carapace recouvre tout** | On voit pas le mécanisme | Carapace 60×44×34mm englobe body+neck+legs |
| T5 | **Proportions irréalistes** | Ressemble pas à une tortue | Body 20×38×18, head 10×10×10, géométrie primitive |
| T6 | **Pas de guide pour le pushrod** | Le pushrod tangue dans le vide | Aucun guidage entre lever et figurine |
| T7 | **Mouvement gauche-droite impossible** | Limité au haut-bas | Pas de mécanisme de conversion cam→rotation axiale |

---

## ANATOMIE MÉCANIQUE — Comment ça devrait marcher

### Vue de côté (Y-Z), coupe au milieu
```
          Z (mm)
          ↑
    100  ─┤          ○ HEAD (pivote ici sur pin X-axis)
          │         ╱│╲
     93  ─┤      NECK  │  ← pushrod pousse ICI (attaché au neck, pas au body)
          │        │   │
     84  ─┤    ╔═BODY══╗  ← repose sur une SHELF (pas flottant)
          │    ║  ○○○○  ║  ← legs intégrés, touchent la shelf
     75  ─┤    ╚════════╝
          │    ┌──shelf──┐ ← NOUVELLE PIÈCE: plateforme fixée aux walls
     73  ─┤    │         │
          │    │WALL   WALL│
          │    │    │    │
     57  ─┤    │  lever  │ ← lever pivote, tip monte/descend
          │    │ /pushrod│ ← pushrod CONTOURNE le body (passe dehors)
     48  ─┤    │╱  │     │
          │    │   │     │
     35  ─┤    │==CAM==shaft│ ← came tourne avec l'arbre
          │    │  ╱      │
     29  ─┤    │bracket  │
          │    │         │
      3  ─┤    └─────────┘
      0  ─┤    ═══BASE═══
          └──────────────→ Y (mm)
              -25    0    25
```

### Chaîne cinématique détaillée
```
MANIVELLE (Y=-39, Z=35)
    │ tourne l'arbre Ø4mm
    ▼
ARBRE (Z=35, traverse les 2 walls)
    │ entraîne la came en press-fit (D-flat)
    ▼
CAME (Z=35, Rb=8.3mm, lift=8mm)
    │ profil poly4567 pousse le follower vers le haut
    ▼
FOLLOWER (X=0, Z=43→51, course=8mm)
    │ tige verticale dans un guide linéaire
    ▼
LEVIER (pivot Z=48, bras 12mm+20mm)
    │ le follower pousse un bout, l'autre bout pousse le pushrod
    ▼
PUSHROD (passe DEVANT ou SUR LE CÔTÉ du body, pas à travers)
    │ tige rigide ~30mm
    ▼
NECK ATTACHMENT (Y≈24, Z≈90)
    │ le pushrod pousse le cou de la tortue
    ▼
HEAD (pivote autour du pin X-axis à Z≈93)
    │ la tête hoche de haut en bas
    ▼
MOUVEMENT VISIBLE: ±12° de rotation tête
```

---

## DIMENSIONS RÉELLES — Chaque pièce

### Châssis (5 pièces)
| Pièce | Dimensions (mm) | Position center | Matériau | Notes |
|-------|----------------|----------------|----------|-------|
| base_plate | 80 × 60 × 3 | (0, 0, 1.5) | PLA | 4× trous M3 aux coins |
| wall_left | 7.6 × 50 × 70 | (-38.5, 0, 37.9) | PLA | Trou Ø4.7mm pour arbre à Z=35 |
| wall_right | 7.6 × 50 × 70 | (38.5, 0, 37.9) | PLA | Idem |
| camshaft_bracket | 74 × 15 × 3 | (0, 7.5, 29) | PLA | Support arbre, trou Ø4.7mm |
| **fig_shelf** (NOUVEAU) | **74 × 50 × 3** | **(0, 0, 73)** | **PLA** | **Plateau pour poser la figurine** |

### Arbre + Manivelle (3 pièces)
| Pièce | Dimensions | Position | Notes |
|-------|-----------|----------|-------|
| camshaft | Ø4 × 34.6mm | (0, 0, 35) | Tige acier, traverse walls + bracket |
| crank_handle | 10 × 39 × 15 | (0, -38.6, 35) | PLA, bouton de manivelle |
| collar_retention | Ø9 × 3 | (0, 15.3, 35) | Empêche l'arbre de glisser |

### Mécanisme came (6 pièces)
| Pièce | Dimensions | Position | Notes |
|-------|-----------|----------|-------|
| cam_neck | 26.3 × 24.6 × 5 | (2.3, -3.9, 35) | Profil came, bore D-flat Ø4mm press-fit |
| follower_guide_0 | 14 × 18 × 5 | (0, 29, 55.5) | Guide linéaire pour la tige |
| lever_neck | 7.5 × 3.5 × 20.1 | (2.8, -5.7, 47.5) | Bras de levier, pivote |
| bracket_lever_neck | 10.5 × 13.5 × 3 | (2.8, -6, 48.5) | Support du levier |
| pin_lever_neck | Ø4.2 × 12.5 | (2.8, -4, 47) | Axe de pivot du levier |
| collar_L/R_neck | Ø8 × 1.5 | — | Maintien latéral du levier |

### Pushrod (1 pièce — À REFAIRE)
| Pièce | Dimensions actuelles | Problème | Fix |
|-------|---------------------|----------|-----|
| pushrod_neck | 9.5 × 29.9 × 33.1 | **Traverse le body** | Router à l'extérieur du body, passer devant (Y+) ou sur le côté (X±) |

### Figurine tortue (12 pièces)
| Pièce | Dimensions | Position center | Notes |
|-------|-----------|----------------|-------|
| fig_body | 20.2 × 38.2 × 18 | (0, 10, 84) | Ellipsoïde, corps principal |
| fig_head | Ø9.9 sphère | (0, 31, 94.5) | Icosphère, tête |
| fig_neck | 5 × 7.4 × 9 | (0, 23.7, 93.5) | Cylindre, connecte body↔head |
| fig_pin_neck | 10 × 3 × 3 | (0, 23.7, 93.5) | Pin joint pour pivotement tête |
| fig_eye_L/R | Ø1.4 | (±2, 35.2, 95.2) | Yeux décoratifs |
| fig_tail | 7.3 × 9.9 × 7.1 | (0, -13.5, 87.6) | Cône, queue |
| fig_leg_0..3 | 7.3 × 3.6 × 13.5 | ±(6.5, 10, 78) | 4 pattes cylindriques |
| fig_acc_carapace | 60 × 44 × 34.2 | (0.4, 10, 92.3) | Ellipsoïde, carapace |

---

## PLAN DE FIX — 7 bugs, par priorité

### T1 — PUSHROD TRAVERSE LE CORPS (CRITIQUE)
**Problème**: `pushrod_neck` va en ligne droite de lever_tip (Z=57.8) à fig_neck bottom (Z=89.1), passant à travers fig_body (Z=75→93) et fig_acc_carapace.

**Cause**: Ligne 9482 — `end_pt = [fig_centroid_xy[0], fig_centroid_xy[1], fig_bottom[2]]` calcule le endpoint au centroid XY du neck. Comme le neck est au-dessus du body, le pushrod traverse le body.

**Fix proposé**: Router le pushrod en 2 segments (L-shape):
1. Segment vertical: lever_tip → juste au-dessus du body (Z=75, X décalé)  
2. Segment horizontal: contourne vers le neck (Y=24, Z=90)
Ou plus simple: décaler le pushrod sur le CÔTÉ (X=+15mm) pour qu'il passe à côté du body au lieu d'à travers.

**Code à modifier**: Lignes 9478-9505 dans `generate()` — la section pushrod creation.

**Hardcode pour tortue**: Le pushrod part de lever_tip, monte verticalement à X=+12mm (côté droit du body dont la demi-largeur est ~10mm), puis se connecte au neck par un coude.

---

### T2 — FIGURINE SANS SUPPORT (CRITIQUE)
**Problème**: La figurine (base Z=75mm) repose à 2mm au-dessus du top des walls (Z=73mm). Il n'y a aucune shelf/platform entre les deux. Le seul point de contact est le socket du pushrod dans le neck.

**Cause**: Le FigurineBuilder pose les pièces à `base_z = chassis_config.total_height + plate_thickness = 73mm` mais ne crée pas de support physique.

**Fix proposé**: Ajouter une **shelf** (plateau) fixée aux walls à Z=73mm:
- Plateau PLA 74 × 50 × 3mm (s'insère entre les 2 walls)
- Trou central pour passage du pushrod (Ø12mm)
- 2 clips ou rainures pour maintien dans les walls

**Alternativement**: Prolonger les walls vers le haut avec un rebord intérieur (shelf intégrée).

**Code à modifier**: `generate_chassis_parts()` ou post-generation dans `generate()`.

---

### T3 — TÊTE PAS CONNECTÉE AU PUSHROD (IMPORTANT)
**Problème**: Le pushrod arrive au bottom du fig_neck (Z=89.1mm). Le pin joint est au centre du neck (Z=93.5mm). Pour que la tête tourne, le pushrod doit exercer une force SOUS le pivot, pas AU pivot.

**Cause**: Le pushrod endpoint est calculé comme le centroid XY du fig_neck au Z le plus bas. Le pin est au milieu du neck.

**Détail du joint**: Le pin_neck est un axe X (gauche-droite, 10mm long). La tête+neck pivotent autour de cet axe. Pour créer un couple, le pushrod doit pousser le neck en DESSOUS du pin.

**Fix proposé**: Le pushrod se connecte à un **levier de cou** — un bras solidaire du neck qui descend sous le pin. Quand le pushrod pousse ce bras vers le haut, le neck pivote autour du pin et la tête monte.

**Hardcode pour tortue**: 
- Ajouter un bras de 8mm sous le pin (Z=93.5 → Z=85.5)
- Le pushrod se connecte à ce bras (Z≈86mm)
- Socket de Ø3mm dans le bras

---

### T4 — CARAPACE ENGLOBE TOUT (VISUEL)
**Problème**: La carapace fait 60×44×34mm et englobe le body, le neck, et déborde sur les legs. C'est un gros blob.

**Fix proposé**: 
- Réduire la carapace: 40×30×20mm (proportionnel au body)
- La positionner uniquement sur le DOS du body (Z offset +8mm, pas centré sur le body)
- Elle ne doit PAS couvrir le neck ni la tête
- Option: la carapace est une coquille évidée (shell) plutôt qu'un ellipsoïde plein → économie de filament et look plus réaliste

**Hardcode pour tortue**: `AccessoryDef("carapace", "ellipsoid", (20.0, 15.0, 12.0), "body", (0, 0, 8.0))`

---

### T5 — PROPORTIONS IRRÉALISTES (VISUEL)
**Problème**: Body 20×38×18mm, head Ø10mm, neck 5×7×9mm. C'est des formes primitives empilées.

**Proportions réelles d'une tortue**:
- Corps large et plat (ratio largeur/longueur ≈ 0.8, hauteur/longueur ≈ 0.3)
- Tête petite (≈ 20% du body length)
- Cou extensible (long et fin, ~30% du body length)
- Pattes courtes et trapues
- Queue très courte

**Fix proposé pour turtle_simple**:
```python
# Body: plus large et plus plat
body = _make_ellipsoid(rx=18, ry=16, rz=8)  # au lieu de (10, 19, 9)

# Head: plus petite
head = icosphere(radius=5)  # au lieu de 5

# Neck: plus long et fin
neck = cylinder(radius=2, height=12)  # plus long pour le mouvement

# Carapace: dôme aplati sur le dos
carapace = ellipsoid(rx=20, ry=18, rz=10)  # sur le dos uniquement

# Legs: courtes et larges
leg = cylinder(radius=2.5, height=8)  # au lieu de 13.5mm
```

---

### T6 — PAS DE GUIDE PUSHROD (FONCTIONNEL)
**Problème**: Le pushrod est une tige libre entre le levier (Z=57.8) et le neck (Z=89.1). Sur 33mm de course, rien ne le guide. En vrai, il va tanguer et potentiellement se coincer.

**Fix proposé**: Ajouter un **tube guide** fixé à la shelf:
- Tube PLA Ø_ext=6mm, Ø_int=3.5mm (pushrod Ø3mm + 0.5mm jeu)
- Hauteur 15mm, fixé à la shelf par clip
- Le pushrod coulisse dedans

**Code**: Ajouter dans `generate()` après la shelf creation.

---

### T7 — MOUVEMENT GAUCHE-DROITE (FEATURE)
**Problème**: Le système actuel ne fait que du haut-bas (follower linéaire vertical). Pour gauche-droite, il faudrait un mécanisme de conversion.

**Options mécaniques**:
1. **Came à rainure (groove cam)**: rainure taillée dans un disque, un follower suit la rainure et convertit la rotation en oscillation
2. **Scotch yoke**: bielle transforme rotation en translation horizontale
3. **Came latérale**: came montée perpendiculairement à l'arbre, pousse le neck latéralement

**Note**: Ceci est une V2. Pour la V1, on se concentre sur le haut-bas qui marche.

---

## ORDRE D'IMPLÉMENTATION

### Phase 1 — Hardcode (la tortue marche)
1. **T2**: Ajouter shelf entre walls (plateforme figurine)
2. **T1**: Router pushrod sur le côté (X=+12mm, bypass body)
3. **T3**: Bras de cou sous le pin (transmission mouvement)
4. **T6**: Tube guide pushrod sur la shelf

### Phase 2 — Polish visuel
5. **T4**: Réduire carapace, positionner sur le dos uniquement
6. **T5**: Ajuster proportions (body plat, pattes courtes)

### Phase 3 — Feature
7. **T7**: Mouvement gauche-droite (scotch yoke ou groove cam)

---

## VALIDATION — Comment savoir que ça marche

### Test 1: Collision zero
```
Aucune pièce mobile ne traverse une pièce fixe.
Pushrod ne touche pas fig_body ni fig_acc_carapace.
```

### Test 2: Continuité mécanique
```
Chaque pièce de la chaîne touche la suivante:
manivelle ↔ arbre ↔ came → follower → levier → pushrod → neck_arm → neck → head
                     (contact cam)  (contact)  (contact)  (socket)   (pin joint)
```

### Test 3: Course vérifiée
```
Le pushrod monte de X mm quand la came est au max lift.
Le neck_arm reçoit cette course et la convertit en rotation autour du pin.
La tête tourne de Y degrés (target: ±10-15°).
```

### Test 4: Jeux suffisants
```
Arbre dans walls: Ø4mm dans trou Ø4.7mm → jeu 0.35mm/côté ✅
Pin dans neck: Ø3mm dans trou Ø3.3mm → jeu 0.15mm/côté ✅  
Pushrod dans guide: Ø3mm dans tube Ø3.5mm → jeu 0.25mm/côté ✅
Came ne touche pas follower guide: gap 15.5mm ✅
```

### Test 5: Impression physique
```
Imprimer sur Ender-3, PLA 0.2mm, 20% infill.
Assembler sans forcer.
Tourner la manivelle → la tête bouge.
Filmer et partager.
```

---

## FICHIERS À MODIFIER
- `automata_unified_v4.py`:
  - `create_turtle_simple()` → proportions + carapace size (ligne ~6147)
  - `FigurineBuilder.build()` → neck arm creation (ligne ~7921)
  - `generate()` → pushrod routing (ligne ~9478), shelf creation
  - `generate_chassis_parts()` → shelf piece
- Ce fichier (`TURTLE_FIX_SPEC.md`) → tracker de progression

---

## PROGRESSION
- [ ] T1 — Pushrod routing (bypass body)
- [ ] T2 — Shelf / platform figurine
- [ ] T3 — Neck arm (transmission pushrod→rotation)
- [ ] T4 — Carapace resize
- [ ] T5 — Proportions
- [ ] T6 — Tube guide pushrod
- [ ] T7 — Mouvement gauche-droite (V2)
