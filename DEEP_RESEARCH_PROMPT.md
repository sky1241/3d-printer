# DEEP RESEARCH — Fix assemblage spatial automata_unified_v4.py

## CONTEXTE

Générateur d'automates mécaniques 3D imprimables. Python + trimesh + shapely.  
Fichier unique 16 375 lignes. 94 tests passent, 9 presets génèrent sans crash.  
**L'assembly.stl est mécaniquement impossible** — chaque pièce est correcte individuellement, mais l'assemblage ne fonctionne pas car les pièces ne sont pas aux bonnes positions.

**Convention 3D visée** : X = largeur, Y = profondeur, Z = hauteur (UP).

---

## ÉTAT MESURÉ (bounds en mm)

```
nodding_bird — positions actuelles:
  base_plate     : X=[-40, 40]  Y=[-30, 30]  Z=[ 0,  3]   ← OK
  wall_left      : X=[-40,-37]  Y=[-25, 45]  Z=[ 3, 53]   ← Y/Z swapped
  wall_right     : X=[ 37, 40]  Y=[-25, 45]  Z=[ 3, 53]   ← Y/Z swapped
  camshaft       : X=[ -2,  2]  Y=[-12, 12]  Z=[33, 37]   ← OK (already fixed)
  cam_neck       : X=[-36, 60]  Y=[-60, 36]  Z=[ 0,  5]   ← WRONG Z=0
  follower_0     : X=[ -7,  7]  Y=[ 20, 55]  Z=[50, 55]   ← WRONG Z=50
```

**Arbre OK** (SPATIAL-1 déjà corrigé) : Z=[33,37], le long de Y. ✅

---

## 3 BUGS SPATIAUX RESTANTS

### BUG A : Murs — Y=hauteur, Z=profondeur (Y/Z swapped)

**Code actuel** (`create_bearing_wall`, L1582) :
```python
h, d, t = config.total_height, config.depth, config.wall_thickness
wall = shapely_box(0, 0, t, h)              # 2D: X=épaisseur(3mm), Y=hauteur(70mm)
# ... bore et cutout en 2D ...
mesh = extrude_polygon(ensure_polygon(wall), d-10)  # extrude en Z → Z=profondeur(50mm)
mesh.apply_translation([-w/2, -d/2+5, plate_t])
```

**Résultat** :
- X = épaisseur (3mm) ✅
- **Y = hauteur (70mm)** ← devrait être profondeur
- **Z = profondeur (50mm)** ← devrait être hauteur

**Conséquence critique** : Le trou de roulement (bore) est percé en 2D via `shapely.Point.buffer()`. Comme le polygone 2D a Y=hauteur, le bore est un cylindre le long de **Z** (direction d'extrusion). Mais l'arbre court le long de **Y**. → **Le bore est perpendiculaire à l'arbre.**

**Fonctions impactées** (même pattern `shapely_box` → `extrude_polygon`) :
| Fonction | Ligne | Description |
|----------|-------|-------------|
| `create_bearing_wall()` | 1582 | Murs latéraux gauche/droite |
| `create_bearing_wall_with_joints()` | 2590 | Variante avec snap-fits |
| `create_camshaft_bracket()` | ~1600 | Bracket central traverse |
| `create_linear_follower_guide()` | ~1582 | Guide de suiveur |

**Fix proposé** : Après extrusion, appliquer `rotation(-π/2, [1,0,0])` pour swapper Y↔Z, puis recalculer la translation.

**Questions pour la recherche** :

1. **Après rotation -π/2 autour de X**, les axes changent : Y_old → Z_new et Z_old → -Y_new. Donc la translation [-w/2, -d/2+5, plate_t] doit devenir quoi exactement ?  
   
   Calcul partiel :
   - Avant rotation : mesh X∈[0,t], Y∈[0,h], Z∈[0, d-10]
   - Après rotation -π/2 X : X∈[0,t], Y∈[0, d-10]→[-(d-10), 0], Z∈[0,h]→[0, h]
   - Non — rotation -π/2 autour de X : (x,y,z) → (x, z, -y)
   - Donc : X∈[0,t], Y∈[0, d-10], Z∈[-h, 0]
   - Hmm, ça met Z négatif. Peut-être +π/2 ? (x,y,z) → (x, -z, y)
   - +π/2 : X∈[0,t], Y∈[-(d-10), 0], Z∈[0, h]
   - **+π/2 donne Z=hauteur ✅ et Y=profondeur (négatif → corriger par translation)**
   
   **Confirmer ce calcul et donner la translation corrigée pour left et right.**

2. **Le bore** : actuellement percé en 2D dans le polygone shapely. Après rotation, le bore (qui était un cylindre le long de Z) deviendrait un cylindre le long de Y. Le shaft court le long de Y. **Est-ce que ça suffit, ou faut-il refaire le bore autrement ?**

3. **Le cutout (lightening hole)** : `shapely_box(t*0.3, h*0.3, t*0.7, h*0.7)` découpe un rectangle centré. Après rotation, ça devrait donner un rectangle vertical centré dans le mur. **Est-ce correct visuellement ?**

4. `create_bearing_wall_with_joints()` à la ligne 2590 ajoute des snap-fit features après le même pattern. **Comment adapter les positions des snap-fits après rotation ?**

---

### BUG B : Cames au sol (Z=0 au lieu de Z=35)

**Code actuel** (`generate()`, L6071) :
```python
mesh.apply_translation([0, i*8.0, 0])   # espacement Y uniquement, Z=0
```

**Résultat** : Cames à Z∈[0,5]. Arbre à Z∈[33,37]. Gap de 28mm.

**Fix proposé** :
```python
cz = chassis_config.total_height * 0.5  # = 35.0 pour config par défaut
cam_thickness = 5.0
mesh.apply_translation([0, i * 8.0, cz - cam_thickness / 2])
```

Le bore de la came est à (0,0) en local XY → après translation, il s'aligne sur l'arbre à (0, y_i, cz).

**Questions** :

1. `cz` est calculé différemment selon le type de châssis. Voici les 4 appels :
   ```python
   # chassis_box:    _make_shaft_and_drive(config, cam_count, cz=config.total_height*0.5)
   # chassis_frame:  _make_shaft_and_drive(config, cam_count, cz=cz + rail_h/2)
   # chassis_central:_make_shaft_and_drive(config, cam_count, cz=cz)
   # chassis_flat:   _make_shaft_and_drive(config, cam_count, cz=t + bracket_h * 0.6)
   ```
   **Comment récupérer le `cz` utilisé par le châssis dans `generate()` ?** Actuellement `generate()` crée un `ChassisConfig` mais ne récupère pas le `cz` choisi par `generate_chassis_*()`. Faut-il le stocker dans `ChassisConfig` ou le retourner depuis `generate_chassis()` ?

2. La came est extrudée depuis Z=0. Après translation par `cz - cam_thickness/2`, le centre de la came est à Z=cz. **Mais le bore de la came est-il bien centré en Z ?** Le bore est percé en 2D (shapely) puis extrudé → il traverse toute l'épaisseur. Après translation, le centre du bore est à Z=cz. L'arbre est à Z∈[cz-2, cz+2]. **L'alignement bore-arbre dépend de l'épaisseur relative (came 5mm, arbre Ø4mm). Vérifier.**

---

### BUG C : Suiveurs à Z=50, loin des cames

**Code actuel** (`generate()`, ~L6094) :
```python
guides.append(FollowerGuide(
    position=[x_offset, 20, 50],   # Z=50 hardcodé
    stroke_mm=amp + 5, ...))
```

Résultat : Followers à Z∈[50,55]. Cames à Z∈[0,5]. Gap = 45mm.

**Fix** : Remplacer Z=50 par `cz + cam_max_radius + 5` (juste au-dessus du point le plus haut de la came).

**Questions** :

1. Le follower guide est un rectangle 2D extrudé, placé verticalement. Son bord inférieur doit être au contact du sommet de la came. **Quel est le point haut de la came ?** C'est `cz + Rb + amplitude`. Valeurs mesurées : nodding_bird Rb=35.8mm, amplitude=25mm → point haut cam = 35 + 35.8 + 25 ≈ 95mm. Ça dépasse le châssis (70mm). → Le problème BUG D (came trop grande) aggrave ce positionnement.

2. Le follower guide a un slot pour le follower rod. **Le slot doit être aligné radialement avec la came**. Actuellement le slot est vertical. Après correction de Z, **le follower rod doit coulisser verticalement et toucher le bord de la came**. Est-ce que `position=[x, 20, cz+cam_top]` suffit ?

3. `create_linear_follower_guide()` utilise aussi `extrude_polygon` (même pattern que les murs). **A-t-il le même bug d'orientation Y/Z que les murs (BUG A) ?** Si oui, le fix de BUG A le corrige automatiquement ?

---

## BUG D : Came surdimensionnée (95mm > châssis 80mm)

**Mesuré** :
```
nodding_bird cam_neck: 95×95mm (bbox), chassis: 80×60mm
walking_figure cam_hip_right: 64×68mm (bbox), dépasse depth 60mm
```

**Code** (`auto_design_cam`, L1090) :
```python
Rb = compute_Rb_min_translating_roller(v, s, rf, phi_max_rad, eps)
Rb = max(Rb, rf + 2)  # minimum Rb
for attempt in range(10):
    # ... check undercut and pressure angle ...
    Rb *= 1.15  # grow 15% if not OK
```

Amplitude=25mm → Rb≈42mm → diamètre came ≈ 2*(42+25) = 134mm. C'est pire que le bbox mesuré car la came n'est pas circulaire.

**Questions** :

1. **Formule exacte `Rb = f(amplitude, phi_max)` pour un roller follower translating ?**
   La formule classique est : `Rb_min = (h * sin(phi_max)) / (phi_max - sin(phi_max) * cos(phi_max))` pour une loi cycloïdale. **Confirmer pour chaque loi de mouvement (cycloidal, poly_345, poly_4567, modified_trap, harmonic).**

2. **Techniques pour réduire Rb tout en gardant l'amplitude** :
   - Augmenter `phi_max` (angle de pression max). Pour PLA, quel phi_max est acceptable ? Métal = 30°, plastique = ?
   - Utiliser un **levier démultiplicateur** entre la came et la figurine. Si levier ratio = 2:1, la came n'a besoin que de 12.5mm de course au lieu de 25mm. **Formule du bras de levier et impact sur Rb ?**
   - **Came conjuguée** (groove cam / desmodromique) → élimine le problème du follower flottant et permet un Rb plus petit ?
   - **Came à fond plat** au lieu de roller : réduit Rb mais augmente friction.

3. **Contrainte max : Rb ≤ (chassis_width - 2*wall_thickness) / 2 ?** Ou faut-il aussi considérer la profondeur du châssis et l'excentricité ?

4. Si Rb ne peut pas être réduit assez, **faut-il agrandir le châssis automatiquement** ou réduire l'amplitude et avertir l'utilisateur ?

---

## INTERACTIONS ENTRE BUGS

Les 4 bugs ne sont pas indépendants :

```
BUG A (murs Y/Z) ──affects──→ position bore ──affects──→ alignement shaft
        │
        └──affects──→ position snap-fits, cutout orientation
        
BUG B (cams Z=0) ──────────→ cam-shaft gap ──affects──→ BUG C (follower Z)
                                                          │
BUG D (cam trop grande) ───→ cam sort du chassis ────────→ follower position impossible
```

**Ordre de fix recommandé** :
1. **BUG D** d'abord — réduire Rb pour que la came rentre dans le châssis
2. **BUG A** — fixer l'orientation des murs (rotation post-extrusion)
3. **BUG B** — positionner les cames à Z=cz (après fix des murs, les bores seront dans le bon axe)
4. **BUG C** — positionner les followers juste au-dessus des cames (dépend de Rb final de D)

---

## FONCTIONS À MODIFIER

| Fonction | Ligne | Bug | Modification |
|----------|-------|-----|-------------|
| `create_bearing_wall()` | 1582 | A | +rotation π/2 X post-extrusion, recalc translation |
| `create_bearing_wall_with_joints()` | 2590 | A | idem + adapter snap-fit positions |
| `create_camshaft_bracket()` | ~1600 | A | +rotation, recalc |
| `create_linear_follower_guide()` | 1582 | A+C | +rotation + Z dynamique |
| `generate()` Step 5 | 6071 | B | +Z offset = cz - cam_t/2 |
| `generate()` ~6094 | 6094 | C | Z = cz + cam_top au lieu de 50 |
| `auto_design_cam()` | 1090 | D | clamp Rb ≤ chassis_max / 2 |
| `generate_chassis_*()` | 1668-1798 | B | retourner cz dans le dict |

---

## LIVRABLES ATTENDUS

1. **Calcul complet des translations post-rotation** pour `create_bearing_wall` (left ET right) et `create_camshaft_bracket`
2. **Stratégie bore** : après rotation +π/2 X, le bore 2D extrudé court le long de quel axe ? Est-ce aligné avec l'arbre (Y) ?
3. **Formule Rb(amplitude, phi_max)** par loi de mouvement + phi_max max réaliste pour PLA
4. **Recommandation** : levier démultiplicateur (oui/non, formules) ou phi_max augmenté ou châssis auto-resize ?
5. **Code de validation** : test que shaft, bore, came et follower sont coaxiaux après fix — vérifier que le centre du bore du mur est à (wall_x, *, cz) et que l'axe du bore pointe en Y
