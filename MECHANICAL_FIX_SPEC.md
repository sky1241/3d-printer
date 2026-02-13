# MECHANICAL FIX SPEC — Faire que les automates FONCTIONNENT
# Date: 13 février 2026
# Mot d'ordre: ÇA DOIT TOURNER. On imprime, on assemble, la manivelle bouge la figurine.
# Scope: Fix le GÉNÉRATEUR → les 12 presets + toutes les espèces marchent d'un coup

---

## CONSTAT — 12/12 presets cassés mécaniquement

Audit de TOUS les presets:
```
Preset              Cams Parts  Shelf  PR∩Body  NeckArm  Guide  Gap(mm)
─────────────────────────────────────────────────────────────────────────
nodding_bird          1    23    ❌      ❌YES    ❌       ❌     -12
flapping_bird         3    40    ❌      ❌YES    ❌       ❌     -12
walking_figure        4    48    ❌      no       ❌       ❌     -13
bobbing_duck          1    22    ❌      ❌YES    ❌       ❌       0
rocking_horse         2    34    ❌      no       ❌       ❌       0
pecking_chicken       2    32    ❌      ❌YES    ❌       ❌      -1
waving_cat            1    24    ❌      no       ❌       ❌       0
drummer               2    33    ❌      ❌YES    ❌       ❌      -1
blacksmith            1    23    ❌      ❌YES    ❌       ❌      -1
swimming_fish         1    24    ❌      no       ❌       ❌       0
turtle_simple         1    27    ❌      ❌YES    ❌       ❌       0
turtle_walking        6    73    ❌      ❌YES    ❌       ❌       0
─────────────────────────────────────────────────────────────────────────
                              0/12    8/12    0/12    0/12
```

**Aucun preset n'est imprimable et fonctionnel.**

---

## 4 FIXES DANS LE GÉNÉRATEUR — Par ordre

Tout est dans `automata_unified_v4.py`. Fix le code du générateur 1 fois = 
les 12 presets + les 17 espèces + toute future figurine marche.

### FIX 1: SHELF (plateforme figurine)
**Fichier**: `generate()` ou `generate_chassis_parts()` 
**Quoi**: Plateau horizontal entre les walls, au sommet du châssis.
**Pourquoi**: La figurine a besoin de reposer sur quelque chose de solide. 
Actuellement elle est posée dans le vide à Z=base_z avec zéro support.
**Dimensions**: largeur = chassis.width - 2×wall_thickness, profondeur = chassis.depth - 2×wall_thickness, épaisseur = 3mm
**Position**: Z = chassis.total_height (top des walls)
**Trou**: Percer un trou par pushrod (Ø = pushrod_diameter + 5mm clearance) pour que le pushrod passe à travers
**Fixation**: Encastré dans les walls (rainure) ou posé sur un rebord
**Impact**: Toutes les figurines reposent sur un support solide
**Code cible**: Après la génération du châssis (~ligne 9200), ajouter la shelf comme pièce chassis

### FIX 2: PUSHROD ROUTING (contourne le body)
**Fichier**: `generate()` lignes 9478-9505
**Quoi**: Le pushrod ne doit JAMAIS traverser une pièce fig_*.
**Pourquoi**: 8/12 presets ont le pushrod qui traverse le body ou un accessoire.
En vrai le pushrod serait DANS le plastique du body → ça bouge pas.
**Algo actuel** (cassé):
```python
start_pt = lever_tip  
end_pt = fig_centroid_xy at fig_bottom_z  # ligne droite → traverse le body
```
**Algo fix** (contourne):
```
1. Calculer start_pt = lever_tip (ok)
2. Calculer end_pt = point d'attache sur la figurine (sous le joint)
3. Vérifier: est-ce que la ligne droite start→end intersecte un fig_* ?
4. Si OUI: router sur le côté
   - Décaler le pushrod en X (±body_width/2 + 5mm) 
   - Faire un L-shape ou Z-shape: montée verticale → coude → horizontal vers target
5. Si NON: ligne droite OK
```
**Forme du pushrod**: Au lieu d'un simple cylindre, créer un pushrod en L:
- Segment 1: vertical, du lever_tip vers le haut (passe à côté du body)
- Coude: virage à 90° (ou angle)
- Segment 2: horizontal/diagonal, vers le point d'attache
**Vérification post-routing**: Aucun `pushrod_*` ne doit avoir un bbox overlap >50mm³ avec un `fig_*`
**Impact**: Les 8 presets avec PR∩Body sont fixés

### FIX 3: TRANSMISSION MOUVEMENT (pushrod → joint)
**Fichier**: `generate()` lignes 9478+ et `FigurineBuilder.build()` ligne 7921+
**Quoi**: Le pushrod doit exercer une force QUI FAIT TOURNER le joint.
**Pourquoi**: Actuellement le pushrod se connecte au bottom du fig_neck/fig_arm.
Mais le joint (pin) est au MILIEU de cette pièce. Pour créer un couple de rotation,
il faut pousser SOUS le pivot (ou tirer au-dessus).
**Principe mécanique**:
```
          PIVOT (pin joint)
            │
   PUSHROD──┤──── partie mobile (tête/aile/bras)
   pousse   │
   ICI      │ bras de levier = distance pushrod↔pivot
```
**Fix**: Pour chaque joint animé:
1. Identifier le pin position (center du pin joint)
2. Créer un "bras de transmission" solidaire de la partie mobile
   - Descend de 8-12mm SOUS le pin (en Z)
   - C'est un petit cylindre ou une languette PLA
3. Le pushrod se connecte à ce bras (socket dans le bras)
4. Quand le pushrod monte → le bras monte → le joint tourne
**Calcul du bras de levier**:
- distance = 8mm minimum (force raisonnable)
- angle de rotation = arctan(pushrod_travel / bras_distance)
- Pour 8mm de travel et 8mm de bras: angle = ±45° (largement suffisant)
**Impact**: Le mouvement se transmet réellement dans les 12 presets

### FIX 4: GUIDE PUSHROD (le pushrod coulisse droit)
**Fichier**: `generate()` après la shelf
**Quoi**: Tube guide fixé à la shelf pour chaque pushrod.
**Pourquoi**: Un pushrod de 30mm sans guide tangue latéralement.
En vrai il se coincerait ou sortirait de sa trajectoire.
**Dimensions**: 
- Tube: Ø_ext=6mm, Ø_int=pushrod_diameter+0.5mm, hauteur=10-15mm
- Fixé à la shelf (intégré ou collé)
- Le pushrod coulisse verticalement dedans
**Position**: Centré sur le trou dans la shelf (même axe que le pushrod)
**Impact**: Mouvement guidé et fiable

---

## ORDRE D'IMPLÉMENTATION

```
FIX 1 (shelf)     → les figurines reposent sur un support
  ↓
FIX 2 (routing)   → les pushrods ne traversent plus rien  
  ↓
FIX 3 (transmit)  → le mouvement arrive vraiment au joint
  ↓
FIX 4 (guide)     → le pushrod coulisse droit sans tanguer
```

Chaque fix est indépendant et testable séparément.

---

## CODE À MODIFIER — Localisations exactes

### generate() dans AutomataGenerator (~ligne 8800-9700)
C'est LA fonction centrale. Ordre des steps:
```
[1/8] Validation
[2/8] Cames
[3/8] Phases  
[4/8] Moteur
[5/8] Géométrie  ← ICI: chassis, levers, figurine, joints, pushrods
[6/8] FDM
[7/8] Timing
[8/8] Validation
```

Dans le step [5/8], après la figurine et les joints:
```
Ligne ~9200: generate_chassis_parts()     → AJOUTER shelf ici (FIX 1)
Ligne ~9430: figurine creation             
Ligne ~9440: joint creation
Ligne ~9478: pushrod creation              → MODIFIER routing (FIX 2)
                                           → AJOUTER bras de transmission (FIX 3)
Ligne ~9530: pushrod hole punching         → SUPPRIMER (plus besoin si routing correct)
Post-pushrod:                              → AJOUTER guide tubes (FIX 4)
```

### FigurineBuilder.build() (ligne 7921)
Pour FIX 3: après création du neck/arm, ajouter un bras de transmission:
```python
# Après création de parts['neck']:
if joint connecté au neck:
    transmission_arm = cylinder(r=2, h=10)  # bras sous le pin
    position = pin_center - [0, 0, 5]  # 5mm sous le pin
    parts['neck_arm'] = transmission_arm
```

### generate_chassis_parts() (ligne ~1700)
Pour FIX 1: à la fin de la fonction, ajouter la shelf:
```python
shelf = trimesh.creation.box([width - 2*wall_t, depth - 2*wall_t, 3])
shelf.translate([0, 0, total_height])
parts['fig_shelf'] = shelf
```

---

## VALIDATION — Quand c'est VRAIMENT bon

### Test mécanique (le plus important)
Pour chaque preset, vérifier:
1. **Zero overlap** pushrod vs fig_*: `max(bbox_overlap) < 10mm³`
2. **Shelf exists**: `'fig_shelf' in parts`
3. **Pushrod guide exists**: au moins 1 `pushrod_guide_*` par pushrod
4. **Transmission arm exists**: 1 `*_arm` par joint animé
5. **Chaîne mécanique continue**: chaque pièce de la chaîne touche la suivante
6. **Course vérifiée**: pushrod_travel > 0 quand cam au max lift

### Nouveau test dans le code (à ajouter)
```python
def check_mechanical_chain(gen):
    """Vérifie que la chaîne cinématique est continue et fonctionnelle."""
    errors = []
    for pname, pmesh in gen.all_parts.items():
        if not pname.startswith('pushrod_'): continue
        # Check: pushrod ne traverse aucune fig_*
        for fname, fmesh in gen.all_parts.items():
            if not fname.startswith('fig_'): continue
            if 'arm' in fname or 'pin' in fname: continue  # attendu
            overlap = bbox_overlap_volume(pmesh, fmesh)
            if overlap > 10:
                errors.append(f"FATAL: {pname} traverse {fname} ({overlap:.0f}mm³)")
    # Check: shelf exists
    if not any('shelf' in k for k in gen.all_parts):
        errors.append("FATAL: pas de shelf pour supporter la figurine")
    return errors
```

---

## APRÈS LES 4 FIXES

Une fois que les 12 presets passent les tests mécaniques:
1. **Exporter les STL de turtle_simple** → viewer 3D pour vérifier visuellement
2. **Tester l'animation** → le mouvement est visible et cohérent
3. **Imprimer turtle_simple sur Ender-3** → première preuve physique
4. **Généraliser** → les 17 espèces passent aussi

Les proportions visuelles (T4, T5 du turtle spec) sont secondaires.
Un cube qui tourne la tête > une belle tortue qui bouge pas.

---

## RÉSUMÉ POUR CLAUDE (prochain chat)

```
TU DOIS LIRE CE FICHIER: MECHANICAL_FIX_SPEC.md
REPO: sky1241/3d-printer, branche main
FICHIER: automata_unified_v4.py (20447 lignes)

4 FIXES À FAIRE DANS generate():
1. Shelf (plateforme, ~ligne 9200)
2. Pushrod routing (contourne body, ~ligne 9478) 
3. Transmission arm (bras sous le joint, ~ligne 9478 + FigurineBuilder)
4. Guide tube (sur la shelf, post-pushrod)

TESTER AVEC:
- 12 presets (validate_preset)
- Collision check pushrod vs fig_*
- Chaîne mécanique continue

MOT D'ORDRE: ÇA DOIT TOURNER. Pas de maths, du réel.
```
