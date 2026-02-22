# MICR — Moteur Inverse de Contraintes Réelles
# Spécification v0.1 — Février 2026
# Repo : 3d-printer / automata_unified_v4.py

---

## CONCEPT

Le pipeline actuel fonctionne en **mode direct** :
```
Espèce → Body plan → Cames → Châssis → Assemblage → Validation (94 checks) → Violations listées
```

Le MICR inverse le flux :
```
Contraintes (94 checks) → Optimisation → Géométrie qui passe TOUT
```

Au lieu de générer d'abord et vérifier après, le MICR prend les contraintes comme **entrée** et calcule les dimensions/positions qui les satisfont toutes.

**Output** : `solved: true` + géométrie valide. Baobab pur — gros tronc, petite canopée.

---

## PROBLÈME À RÉSOUDRE

### État actuel (post-commit cc50d9c, 13 fév 2026)

- **94 constraint checks** (trou1→trou72 + cas101→cas110 + e1→e8)
- **skip_pairs** : paires de collisions "acceptées" car non résolues (~42-63 paires)
- **7 auto-scaling rules** (R1→R8) qui patchent les cas les plus courants
- **17/17 espèces** passent — mais avec des skip_pairs, pas des vrais zéro-collision

### Ce que le MICR doit faire

1. Prendre les contraintes comme **bornes** (pas comme checks post-hoc)
2. Résoudre les skip_pairs restantes en ajustant la géométrie
3. Remplacer les auto-scaling rules R1→R8 par un solveur unique
4. Garantir zéro-collision sans skip_pairs

---

## ARCHITECTURE

### Position dans le pipeline

```
AutomataGenerator.generate()
    │
    ├── [1/8] VALIDATE scene
    ├── [2/8] COMPILE CAMS
    ├── [3/8] OPTIMIZE PHASES          ← déjà de l'optim (torque)
    ├── [4/8] MOTOR CHECK
    │
    ├── [5/8] GEOMETRY                 ← ICI : le MICR remplace la géométrie hardcodée
    │   ├── MICR.solve(constraints, species, body_plan)
    │   │   ├── Input : toutes les contraintes trou1→trou72
    │   │   ├── Variables : Rb, cam_spacing, shaft_diam, chassis dims, lever lengths
    │   │   └── Output : config optimale (ChassisConfig + CamProfiles)
    │   └── Le reste du pipeline utilise les valeurs MICR
    │
    ├── [6/8] FDM tolerances
    ├── [7/8] TIMING
    └── [8/8] ASSEMBLY VALIDATION      ← devrait trouver 0 violations
```

### Brique G (InverseSolver) vs MICR

| | InverseSolver (Brique G) | MICR |
|---|---|---|
| **Scope** | 1 came (trajectoire → profil) | Assemblage complet |
| **Variables** | beta, height, Rb, phase | Rb, spacing, shaft, chassis, levers, tout |
| **Contraintes** | pressure angle < 30°, no undercut | 94 checks (mécanique + FDM + collision) |
| **Algo** | differential_evolution + L-BFGS-B | À définir (même pattern probable) |
| **Ligne** | L19963-20621 | À créer |

Le MICR **utilise** l'InverseSolver pour les cames individuelles, mais optimise les variables d'assemblage autour.

---

## VARIABLES D'OPTIMISATION

### Variables continues (float)

| Variable | Bornes | Unité | Description |
|----------|--------|-------|-------------|
| `Rb[i]` | [8, 80] | mm | Rayon de base came i |
| `cam_spacing` | [4, 12] | mm | Espacement entre cames |
| `shaft_diameter` | [3, 8] | mm | Diamètre arbre à cames |
| `chassis_width` | [40, 200] | mm | Largeur châssis |
| `chassis_depth` | [30, 100] | mm | Profondeur châssis |
| `chassis_height` | [30, 150] | mm | Hauteur châssis |
| `lever_input[i]` | [5, 40] | mm | Longueur bras levier entrée i |
| `lever_output[i]` | [10, 60] | mm | Longueur bras levier sortie i |
| `follower_x[i]` | [zone] | mm | Position X guide suiveur i |

### Variables discrètes

| Variable | Choix | Description |
|----------|-------|-------------|
| `shaft_type` | Ø3, Ø4, Ø5, Ø6, Ø8 | Standard dispo |
| `motor_ratio` | 100:1, 150:1, 298:1 | Réducteurs N20 |
| `chassis_style` | box, frame, central, flat | Type châssis |
| `has_mid_bearing` | bool | Palier intermédiaire |

---

## CONTRAINTES (HARD + SOFT)

### Hard constraints (violation = solution rejetée)

Directement des checks existants :

- **trou1** : cam-to-cam collision → `cam_spacing > 2 * max(Rb[i]) + clearance`
- **trou2** : shaft length vs chassis → `camshaft_length < chassis_depth`
- **trou3** : pressure angle < 30° → dépend de Rb[i]
- **trou4** : lever sweep vs chassis width → `lever_output[i] < chassis_width / 2`
- **trou5** : torque sufficiency → couple moteur > couple résistant
- **trou8** : cumulative lift vs height → `sum(lifts) < chassis_height`
- **trou9** : chassis dims vs parts envelope
- **trou10** : figurine clearance above chassis
- **trou11** : shaft deflection < 0.5mm
- **trou57** : all parts fit print plate (220×220mm)

### Soft constraints (pénalité dans fitness)

- Compacité : minimiser volume total
- Centre de gravité : maximiser stabilité
- Uniformité : cam sizes similaires (esthétique)
- Matière : minimiser filament PLA

---

## ALGORITHME PROPOSÉ

### Pattern : même ADN que HSBC + InverseSolver

```python
class MICR:
    """Moteur Inverse de Contraintes Réelles.
    
    Baobab : 660 lignes de solveur, output = solved: true.
    """
    
    def __init__(self, scene: AutomataScene, constraints: List[Check]):
        self.scene = scene
        self.constraints = constraints
        self.n_cams = len(scene.cam_tracks)
        
    def solve(self, method='hybrid') -> MICRSolution:
        """
        Phase 1 : differential_evolution (global search)
            - Population 100, generations 200
            - Évalue toutes les hard constraints comme pénalités
            - Soft constraints dans la fitness
            
        Phase 2 : L-BFGS-B (local refinement)
            - Prend le meilleur de Phase 1
            - Affine les variables continues
            
        Phase 3 : validation complète
            - run_all_constraints() sur la géométrie générée
            - Si violations → feedback loop (max 3 itérations)
        """
        pass
        
    def _encode(self) -> np.ndarray:
        """Encode toutes les variables en vecteur plat."""
        pass
        
    def _decode(self, x: np.ndarray) -> Dict:
        """Décode vecteur → ChassisConfig + CamProfiles."""
        pass
        
    def _fitness(self, x: np.ndarray) -> float:
        """
        fitness = hard_penalty + soft_penalty + compactness_bonus
        
        hard_penalty : 1e6 par violation hard (rend la solution inviable)
        soft_penalty : somme pondérée des soft constraints
        compactness  : -1 * volume_total (minimiser)
        """
        pass
        
    def _evaluate_constraints(self, config: Dict) -> ConstraintReport:
        """Évalue les 94 checks sur la config proposée."""
        pass
```

### Fitness détaillée

```
fitness(x) = -1e6 * n_hard_violations           # hard: invalide la solution
             - sum(w_i * soft_violation_i)        # soft: pénalise
             - 0.01 * total_volume_mm3            # compacité
             + 100 * stability_score              # bonus stabilité
             + 50 * (1 - max_deflection / 0.5)    # bonus rigidité
```

---

## INTÉGRATION AVEC L'EXISTANT

### Ce qui change

1. `AutomataGenerator.generate()` appelle `MICR.solve()` **avant** [5/8] GEOMETRY
2. Les auto-scaling rules R1→R8 deviennent des **contraintes** dans le MICR
3. Les skip_pairs disparaissent (le MICR trouve des géométries sans collision)
4. [8/8] ASSEMBLY VALIDATION devient une **vérification** (devrait trouver 0 violations)

### Ce qui ne change pas

- Les 94 checks restent identiques (le MICR les utilise, il ne les remplace pas)
- L'InverseSolver (Brique G) reste pour les cames individuelles
- Le pipeline [1/8] → [8/8] garde sa structure
- Les espèces / body plans / living_beings_db restent

---

## TODO

- [ ] Définir l'encodage exact (vecteur de variables)
- [ ] Implémenter `MICR.__init__()` et `solve()`
- [ ] Wrapper les 94 checks existants en `_evaluate_constraints()`
- [ ] Tests sur les 17 espèces existantes
- [ ] Comparer skip_pairs avant/après MICR
- [ ] Benchmark temps de résolution (target < 30s par espèce)

---

## CONNEXION MYCELIUM

Le MICR partage le même ADN algorithmique que :

- **HSBC** `IchimokuTrader.mutate()/crossover()/fitness` : optimisation génétique sous contraintes
- **HSBC** `InverseSolver` (Brique G) : differential_evolution + L-BFGS-B sur des profils de came
- **HSBC** `optuna_optimize_profile()` : Bayesian optimization avec validation walk-forward
- **tree** `validate_growth()` : validation contre des règles biologiques

Même pattern partout : **bounded search space + hard constraints + hybrid global/local optimization + validation against physical laws**.
