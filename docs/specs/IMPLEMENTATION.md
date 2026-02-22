# IMPLEMENTATION — Structure moteur basée sur 5P+3O+5J

## Date : 11 février 2026
## Contexte : Formalisation de la nuit du 11/02. Mapping théorie → code.

---

## CE QUI EST FAIT (dans automata_unified_v4.py)

### ✅ Les 5 Primitives — DÉJÀ CODÉES via trimesh

| Primitive | Code existant                        | Statut |
|-----------|--------------------------------------|--------|
| Box       | `trimesh.creation.box()`             | ✅     |
| Cylinder  | `trimesh.creation.cylinder()`        | ✅     |
| Sphere    | `trimesh.primitives.Sphere()`        | ✅     |
| Cone      | `trimesh.creation.cone()`            | ✅     |
| Disk      | Profil came calculé → extrusion mesh | ✅     |

### ✅ Les 3 Opérations — DÉJÀ CODÉES via trimesh

| Opération | Code existant                        | Statut |
|-----------|--------------------------------------|--------|
| Union     | `trimesh.boolean.union()`            | ✅     |
| Trou      | `trimesh.boolean.difference()`       | ✅     |
| Coupe     | `mesh.slice_plane()`                 | ✅     |

### ✅ Les 5 Joints — DÉJÀ CODÉS (implicitement dans les presets)

| Joint      | Comment c'est codé actuellement              | Statut |
|------------|----------------------------------------------|--------|
| Trou rond  | Perçage Ø dans les murs pour l'arbre         | ✅     |
| Méplat D   | D-shaft sur l'arbre, trou D dans la came     | ✅     |
| Contact    | Came-follower calculé par le solveur         | ✅     |
| Pivot      | Articulation follower-figurine               | ✅     |
| Fixation   | Snap-fit / vis M3 base-murs                  | ✅     |

---

## CE QUI MANQUE — La couche explicite

### Problème actuel
Tout est codé EN DUR dans chaque preset. Le preset "canard" sait qu'il faut
un Box(80,60,3) pour la base, mais cette info est dans le code du preset,
pas dans une structure déclarative.

### Solution : Couche déclarative CSG

Chaque preset devrait être un ARBRE CSG lisible, pas du code impératif.

```python
# AVANT (code impératif actuel) :
def generate_nodding_bird(params):
    base = trimesh.creation.box([80, 60, 3])
    wall_L = trimesh.creation.box([3, 60, 50])
    hole = trimesh.creation.cylinder(radius=2.25, height=10)
    wall_L = wall_L.difference(hole)
    # ... 200 lignes de plus

# APRÈS (arbre CSG déclaratif) :
nodding_bird = {
    "chassis": {
        "base": {"op": "difference", "a": {"prim": "box", "L": 80, "W": 60, "H": 3},
                 "b": [{"prim": "cylinder", "R": 1.7, "H": 10, "pos": [10,10,0]},
                       {"prim": "cylinder", "R": 1.7, "H": 10, "pos": [70,10,0]},
                       {"prim": "cylinder", "R": 1.7, "H": 10, "pos": [10,50,0]},
                       {"prim": "cylinder", "R": 1.7, "H": 10, "pos": [70,50,0]}]},
        "wall_L": {"op": "difference",
                   "a": {"prim": "box", "L": 3, "W": 60, "H": 50},
                   "b": {"prim": "cylinder", "R": 2.25, "H": 10, "pos": [0,30,25]}},
        "wall_R": "=wall_L"
    },
    "drive": {
        "shaft": {"prim": "cylinder", "R": 2, "H": 55},
        "cam_1": {"op": "difference",
                  "a": {"prim": "disk", "Ri": 2, "profile": "computed", "ep": 8},
                  "b": {"prim": "cylinder", "R": 2, "H": 8, "D_flat": true}}
    },
    "output": {
        "follower_1": {"op": "union",
                       "a": {"prim": "cylinder", "R": 1.5, "H": 30},
                       "b": {"prim": "sphere", "R": 3, "pos": [0,0,30]}},
        "figurine": "$figurines/bird"
    },
    "joints": {
        "wall_L_shaft": {"type": "trou_rond", "clearance": 0.2},
        "shaft_cam1": {"type": "meplat_D", "depth": 0.5},
        "cam1_follower1": {"type": "contact", "spring": true},
        "follower1_figurine": {"type": "pivot", "axis": "x"},
        "base_walls": {"type": "snap_fit", "force": 5}
    }
}
```

### Catalogue figurines (le JSON manquant)

```python
figurines = {
    "bird": {
        "body": {"prim": "sphere", "R": 12, "scale_z": 0.7},
        "head": {"prim": "sphere", "R": 7, "pos": [0, 0, 15]},
        "beak": {"prim": "cone", "R1": 2, "R2": 0, "H": 8, "pos": [7, 0, 15]},
        "tail": {"prim": "cone", "R1": 4, "R2": 1, "H": 10, "pos": [-12, 0, 5]}
    },
    "duck": {
        "body": {"prim": "sphere", "R": 15, "scale_z": 0.6},
        "head": {"prim": "sphere", "R": 8, "pos": [0, 0, 18]},
        "beak": {"prim": "box", "L": 10, "W": 6, "H": 3, "pos": [8, 0, 16]}
    },
    "person": {
        "head": {"prim": "sphere", "R": 10},
        "body": {"prim": "box", "L": 12, "W": 8, "H": 25, "pos": [0, 0, -20]},
        "arm_L": {"prim": "cylinder", "R": 3, "H": 18, "pos": [-10, 0, -10]},
        "arm_R": {"prim": "cylinder", "R": 3, "H": 18, "pos": [10, 0, -10]},
        "leg_L": {"prim": "cylinder", "R": 3.5, "H": 20, "pos": [-5, 0, -40]},
        "leg_R": {"prim": "cylinder", "R": 3.5, "H": 20, "pos": [5, 0, -40]}
    },
    "horse": {
        "body": {"prim": "box", "L": 30, "W": 12, "H": 15},
        "head": {"prim": "sphere", "R": 8, "pos": [18, 0, 10]},
        "neck": {"prim": "cylinder", "R": 4, "H": 12, "pos": [14, 0, 8], "rot": [30,0,0]},
        "legs": [
            {"prim": "cylinder", "R": 2.5, "H": 20, "pos": [-10, -5, -15]},
            {"prim": "cylinder", "R": 2.5, "H": 20, "pos": [-10, 5, -15]},
            {"prim": "cylinder", "R": 2.5, "H": 20, "pos": [10, -5, -15]},
            {"prim": "cylinder", "R": 2.5, "H": 20, "pos": [10, 5, -15]}
        ],
        "tail": {"prim": "cone", "R1": 3, "R2": 1, "H": 15, "pos": [-18, 0, 8]}
    }
}
```

---

## ROADMAP D'IMPLÉMENTATION

### Phase 1 — Couche CSG déclarative (estimé : 1 nuit)
- [ ] Créer `csg_engine.py` : interpréteur d'arbres CSG
- [ ] Fonction `build_piece(csg_tree) → trimesh.Mesh`
- [ ] Fonction `build_assembly(preset_tree) → list[Mesh]`
- [ ] Tests : les 22 presets reconstruits en CSG déclaratif = mêmes STL

### Phase 2 — Catalogue figurines (estimé : 2h)
- [ ] Créer `figurines.json` avec 10-20 figurines de base
- [ ] Fonction `load_figurine(name) → csg_tree`
- [ ] Intégrer dans le moteur : preset + figurine = automate complet

### Phase 3 — Site V4 avec vraies pièces (estimé : 1 nuit)
- [ ] Rendu 3D de chaque pièce individuelle (pas un wireframe décoratif)
- [ ] Vue éclatée : chaque pièce séparée, nommée, dimensionnée
- [ ] Vue assemblée : toutes les pièces emboîtées
- [ ] Animation : les cames tournent, les followers bougent

### Phase 4 — Le mode papy (estimé : 1 nuit)
- [ ] Interface simplifiée : choisis figurine → choisis mouvement → imprime
- [ ] Guide d'assemblage visuel étape par étape
- [ ] Estimation temps d'impression + PLA nécessaire

---

## RÉSUMÉ

| Composant | Lignes estimées | Priorité |
|-----------|----------------|----------|
| csg_engine.py | ~500 | P1 |
| figurines.json | ~200 | P1 |
| Site V4 (vraies pièces) | ~800 (HTML) | P2 |
| Mode papy | ~400 (HTML) | P3 |

Total nouveau code estimé : ~1900 lignes
Code existant : 16 243 lignes
Ratio existant/nouveau : **90% fait, 10% restant**

---

## NOTE HISTORIQUE

Cette nuit du 11 février 2026, la formalisation 5P+3O+5J a émergé
d'une session de réflexion entre Ludo et Claude. La recherche exhaustive
(web search multi-angles) n'a trouvé AUCUN précédent de cette formulation
spécifique appliquée aux automates mécaniques à cames pour impression 3D.

Le plus proche : Disney Research, Coros et al., SIGGRAPH 2013.
Leur code n'a jamais été publié. Leur approche utilise des engrenages,
pas des arbres CSG déclaratifs bornés par contraintes FDM.

Ce moteur est, à notre connaissance, le seul système fonctionnel au monde
qui fait : input mot → output assemblage mécanique multi-pièces STL.
