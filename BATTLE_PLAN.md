# ⚔️ PLAN DE BATAILLE — Figurines Articulées
# Approche: brique par brique, tests à chaque étape
# Date: 13 février 2026

---

## PHILOSOPHIE
- **1 brique = 1 feature isolée + tests complets**
- On merge PAS si les tests passent pas
- Chaque brique est utilisable indépendamment
- On teste sur turtle_simple d'abord (1 seul joint = le plus simple)
- Puis on généralise

---

## 🧱 BRIQUE 1 — Pin Joint Generator (le pivot de base)
**Objectif**: Générer un axe + trou imprimables avec clearance correcte

### Ce qu'on code:
```python
def create_pin_joint(diameter, length, clearance=0.3):
    """Retourne (axe_mesh, hole_mesh) pour un pivot imprimable."""
    # axe = cylindre plein Ø diameter
    # trou = cylindre creux Ø diameter+clearance
    # + chanfrein 0.5mm à l'entrée du trou (facilite insertion)
    # + flat optionnel sur l'axe (anti-rotation si press-fit)
```

### Constantes (de DATA_ARTICULATIONS.md):
- Clearance nominale: 0.30mm (radiale totale, soit 0.15/côté)
- Clearance serrée: 0.20mm (X1C calibrée)
- Clearance sûre: 0.50mm (imprimante mal calibrée)
- Chanfrein entrée: 0.5mm @ 45°
- Diamètres supportés: 3, 4, 5, 6mm

### Tests BRIQUE 1:
- [ ] T1.1: Pin joint Ø3mm → axe watertight, trou watertight
- [ ] T1.2: Pin joint Ø6mm → idem
- [ ] T1.3: Axe rentre dans trou (bounding box axe < bounding box trou)
- [ ] T1.4: Clearance mesurée = valeur demandée (±0.01mm)
- [ ] T1.5: Chanfrein présent (faces count > cylindre simple)
- [ ] T1.6: Orientation check — axe horizontal (max extent en X ou Y, pas Z)
- [ ] T1.7: Aucune régression sur les 9 presets existants
- [ ] T1.8: Aucune régression sur les 17 espèces dynamiques

---

## 🧱 BRIQUE 2 — Joint Definition System
**Objectif**: Définir OÙ couper la figurine pour créer les articulations

### Ce qu'on code:
```python
@dataclass
class JointDef:
    name: str              # "neck", "hip_fl", "tail"
    joint_type: str        # "pin", "ball", "hinge"
    axis: Tuple[float,float,float]  # axe de rotation (1,0,0)=pitch
    position: Tuple[float,float,float]  # point de pivot dans l'espace figurine
    amplitude_deg: float   # ±30°
    parent_part: str       # "body" (fixe)
    child_part: str        # "head" (mobile)
    pushrod_attach: str    # "child" — le pushrod pousse la partie mobile
    arm_length: float      # bras de levier en mm (pour formule θ=asin(Δ/R))
    return_method: str     # "gravity", "friction", "spring"
```

### Mapping body_type → joints:
```python
JOINT_TEMPLATES = {
    'quadruped_shell': [  # Tortue
        JointDef("neck", "pin", (1,0,0), ..., 30, "body", "head", ...),
        JointDef("hip_fl", "pin", (1,0,0), ..., 20, "body", "leg_0", ...),
        JointDef("hip_fr", "pin", (1,0,0), ..., 20, "body", "leg_1", ...),
        JointDef("hip_rl", "pin", (1,0,0), ..., 20, "body", "leg_2", ...),
        JointDef("hip_rr", "pin", (1,0,0), ..., 20, "body", "leg_3", ...),
        JointDef("tail", "pin", (1,0,0), ..., 15, "body", "tail", ...),
    ],
}
```

### Tests BRIQUE 2:
- [ ] T2.1: JointDef pour tortue → 6 joints (cou + 4 hanches + queue)
- [ ] T2.2: Chaque joint a un parent et child valides (existent dans fig_parts)
- [ ] T2.3: Position du joint est ENTRE parent et child (pas à l'extérieur)
- [ ] T2.4: Amplitude est dans range [5°, 90°]
- [ ] T2.5: arm_length > 0 et < hauteur figurine
- [ ] T2.6: Pas de régression presets/espèces

---

## 🧱 BRIQUE 3 — Body Splitter (découpe figurine)
**Objectif**: Couper le mesh figurine en parties fixes et mobiles

### Ce qu'on code:
```python
def split_figurine(fig_parts, joint_defs):
    """
    Prend les pièces figurine actuelles (ellipsoïdes) et les réorganise:
    - Corps (body) = FIXE, monté sur châssis
    - Tête (head) = MOBILE, connectée par pin joint au cou
    - Chaque partie mobile a un "bras" pour attacher le pushrod
    
    Retourne: dict de pièces avec metadata (fixed/mobile, joint_name)
    """
```

### Approche simple (V1):
On ne COUPE PAS les meshes existants. On les RÉORGANISE:
- fig_body + fig_acc_carapace → FIXE (snap-fit sur châssis)
- fig_head + fig_neck → MOBILE (pivote autour du cou)
- fig_leg_N → MOBILE (pivote autour de la hanche)
- fig_tail → MOBILE (pivote autour de la base queue)

Chaque partie mobile reçoit:
- Un TROU d'axe au point de pivot
- Un BRAS (extension) pour attacher le pushrod

Chaque partie fixe reçoit:
- Un TROU d'axe correspondant
- Des SUPPORTS pour les axes

### Tests BRIQUE 3:
- [ ] T3.1: split_figurine sur tortue → body=FIXE, head=MOBILE
- [ ] T3.2: Chaque partie mobile a un trou d'axe (boolean subtract visible)
- [ ] T3.3: Chaque partie fixe a un trou d'axe correspondant
- [ ] T3.4: Les trous sont ALIGNÉS (même axe, même position)
- [ ] T3.5: Aucun mesh ne devient non-watertight après découpe
- [ ] T3.6: Le pin joint FIT (axe.bounds < trou.bounds)
- [ ] T3.7: Pas de régression

---

## 🧱 BRIQUE 4 — Pushrod Router (connexion levier → joint)
**Objectif**: Créer un pushrod qui va du levier mécanique au bras de la partie mobile

### Ce qu'on code:
```python
def route_pushrod_to_joint(lever_tip, joint_def, fig_parts):
    """
    Crée un pushrod (tige Ø3-5mm) du sommet du levier 
    au bras de la partie mobile.
    
    Le pushrod a:
    - Un embout sphérique en bas (socket dans le levier)
    - Un embout sphérique en haut (socket dans le bras mobile)
    - Un corps cylindrique entre les deux
    
    Retourne: pushrod_mesh, socket_holes (à soustraire des pièces)
    """
```

### Cinématique:
```
θ_sortie = asin(Δh_pushrod / R_bras)
```
- Δh_pushrod = amplitude du levier (donnée par la came)
- R_bras = distance joint_pivot → point_attache_pushrod sur la partie mobile

### Tests BRIQUE 4:
- [ ] T4.1: Pushrod connecte lever_neck au bras de la tête
- [ ] T4.2: Pushrod est watertight
- [ ] T4.3: Pushrod ne traverse PAS le corps fixe (fig_body)
- [ ] T4.4: Socket holes sont bien positionnés
- [ ] T4.5: Amplitude calculée ≈ amplitude attendue (30° ± 5°)
- [ ] T4.6: Pushrod ne flambe pas (Ø ≥ 3mm pour longueur ≤ 60mm)
- [ ] T4.7: Pas de régression

---

## 🧱 BRIQUE 5 — Assemblage Complet (turtle_simple)
**Objectif**: Assembler le tout sur turtle_simple — premier automate fonctionnel

### Ce qu'on code:
Intégration dans `AutomataGenerator.generate()`:
1. Générer mécanisme (existant) ✅
2. Générer figurine cosmétique (existant) ✅  
3. **NOUVEAU**: Appliquer joints (split + pin joints)
4. **NOUVEAU**: Router pushrods (levier → joint)
5. Valider assemblage

### Résultat attendu:
```
turtle_simple avec:
- Carapace FIXE sur le châssis
- Tête MOBILE sur pivot au cou (Ø3mm)  
- Pushrod du lever_neck au bras de la tête
- Quand le levier monte de 8mm → tête tourne de 30°
- 4 pattes FIXES (pas articulées en V1 simple)
- Queue FIXE
```

### Tests BRIQUE 5:
- [ ] T5.1: turtle_simple génère sans crash
- [ ] T5.2: Tête est une pièce SÉPARÉE du corps
- [ ] T5.3: Pin joint visible entre tête et corps
- [ ] T5.4: Pushrod connecte levier à tête
- [ ] T5.5: 0 collisions pushrod↔body (le pushrod passe AUTOUR)
- [ ] T5.6: STL export — toutes pièces watertight
- [ ] T5.7: Rendu visuel montre l'articulation
- [ ] T5.8: Tous les presets/espèces passent encore

---

## 🧱 BRIQUE 6 — Assemblage Walking (turtle_walking)
**Objectif**: 6 joints articulés (cou + 4 hanches + queue)

### Ce qu'on code:
- Appliquer les 6 JointDefs de la tortue marcheuse
- 6 pushrods routés depuis les 6 leviers
- Pattes articulées aux hanches
- Queue articulée

### Tests BRIQUE 6:
- [ ] T6.1: 6 joints créés (6 axes + 6 trous)
- [ ] T6.2: 6 pushrods routés
- [ ] T6.3: Amplitudes correctes (tête 30°, pattes 20°, queue 15°)
- [ ] T6.4: Gait pattern correct (diagonales en phase)
- [ ] T6.5: ≤5 collisions (objectif 0)
- [ ] T6.6: Export STL complet
- [ ] T6.7: Pas de régression

---

## 🧱 BRIQUE 7 — Généralisation (12 body plans)
**Objectif**: Appliquer le système à tous les types d'animaux

### Ce qu'on code:
- JOINT_TEMPLATES pour les 12 body plans
- Auto-dimensionnement des articulations (formules Bloc 6)
- Tests sur les 17 espèces dynamiques

### C'est la DERNIÈRE brique — on y arrive seulement si B1-B6 sont solides.

---

## 📅 ORDRE D'EXÉCUTION

```
BRIQUE 1 → test → commit → push
   ↓
BRIQUE 2 → test → commit → push  
   ↓
BRIQUE 3 → test → commit → push
   ↓
BRIQUE 4 → test → commit → push
   ↓
BRIQUE 5 → test → commit → push  ← premier automate FONCTIONNEL
   ↓
BRIQUE 6 → test → commit → push
   ↓
BRIQUE 7 → test → commit → push  ← tous les animaux
```

Chaque brique: code → tests unitaires → tests régression → commit → push.
Aucun skip. Aucun raccourci.

---

## 🧪 BATTERIE DE TESTS (à chaque brique)

```bash
# Tests unitaires de la brique
python3 -c "... tests spécifiques ..."

# Régression blocs
python3 -c "import automata_unified_v4 as au; au.run_all_tests()"

# Régression presets  
python3 regression_test.py

# Régression dynamiques
python3 regression_test_dynamic.py

# Régression debug
python3 debug_bugs.py

# TOUT doit être vert avant commit
```
