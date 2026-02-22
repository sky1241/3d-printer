# BRIQUE G — SOLVEUR INVERSE DE CAMES POUR AUTOMATES MÉCANIQUES
## Prompt de Recherche Approfondie

---

## CONTEXTE DU PROJET

Je développe un **générateur paramétrique d'automates mécaniques** imprimables en 3D (PLA, Ender-3 / Bambu Lab X1C). Le projet fait ~15 600 lignes Python et génère des automates complets : figurines, cames, châssis, arbre à cames, guides de suiveur — le tout exportable en STL.

**Architecture actuelle :**
- **Briques A-D** : FigurineBuilder paramétrique, SceneBuilder auto, 16 types de mouvements (V1-V10), 4 types de châssis (box/frame/central/flat)
- **Moteur de contraintes** : 59 checks mécaniques (flexion, couple, collision, fatigue PLA, sécurité EN 71, tolerances FDM...)
- **Lois de mouvement** implémentées : cycloid, modified_trapezoid, simple_harmonic, polynomial_345, polynomial_4567, modified_sine, constant_velocity, dwell
- **Profils de came** : synthèse forward (loi → CamProfile → points polaires → mesh 3D) fonctionnelle
- **35/35 tests passent**, zéro régression

**Ce qui MANQUE = Brique G : le solveur inverse.**

---

## LE PROBLÈME EXACT

### Forward (ce que j'ai déjà) :
```
Loi de mouvement + paramètres → CamProfile → points polaires (r, θ) → mesh 3D → STL
```

### Inverse (ce que je dois construire) :
```
Trajectoire XY dessinée par l'utilisateur → Optimiser les paramètres de came(s) qui reproduisent cette trajectoire au plus proche
```

L'utilisateur dessine une courbe dans le navigateur (Flask UI), et le système doit trouver :
1. **Combien de cames** sont nécessaires (1, 2, ou 3)
2. **Quel type de came** pour chaque (disque, coeur, conjugée...)
3. **Les paramètres optimaux** : rayon de base (Rb), amplitude, angles de levée/retour/dwell, loi de mouvement
4. **Les phases relatives** entre cames (si multi-cames)
5. **La transmission** : directe (suiveur) ou par levier/bielle

### Contraintes physiques à respecter pendant l'optimisation :
- Angle de pression < 30° partout
- Rayon de courbure > 0 (pas d'undercut)
- Couple moteur < capacité N20 (ou effort manivelle < 2N pour crank mode)
- Tout doit tenir dans l'enveloppe Ender-3 (220×220×250mm)
- Came imprimable FDM (épaisseur min 3mm, pas de porte-à-faux > 45°)

---

## RÉFÉRENCE ACADÉMIQUE CLÉ

### Disney Research — Coros et al. 2013
**"Computational Design of Mechanical Characters"**
ACM SIGGRAPH 2013, ACM Transactions on Graphics, Vol. 32, No. 4

**Auteurs :** Stelian Coros, Bernhard Thomaszewski, Gioacchino Noris, Shinjiro Sueda, Moira Forberg, Robert W. Sumner, Wojciech Matusik, Bernd Bickel

**PDF :** https://s3-us-west-1.amazonaws.com/disneyresearch/wp-content/uploads/20140804211255/CDMC1.pdf
**Aussi :** https://www.ri.cmu.edu/pub_files/2013/0/CDMC_final.pdf

**Ce qui est pertinent :**
- Leur système prend des "motion curves" dessinées par l'utilisateur
- Pour chaque motion curve, il **optimise un mécanisme** (came, bielle, 4-bar) qui la reproduit
- Ils pré-calculent un **échantillonnage sparse de l'espace des paramètres** pour chaque type de mécanisme
- Puis utilisent cet échantillonnage pour trouver rapidement le mécanisme optimal
- Les mécanismes sont connectés par gear trains
- Le tout est fabriqué par impression 3D

### Thomaszewski et al. 2014 (suite)
**"Computational Design of Linkage-Based Characters"**
ACM SIGGRAPH 2014

**Ce qui est pertinent :**
- Extension aux mécanismes à bielles (4-bar linkages)
- Optimisation combinant esthétique + fonction mécanique
- Détection de singularités dans les mécanismes

### Autres papiers à explorer :
- **Ceylan et al. 2013** — "Designing and fabricating mechanical automata from mocap sequences" — prend une séquence de motion capture et génère un automate
- **Zhu et al.** — "Synthesis of mechanical toys from motion" — simulated annealing pour l'espace de configuration
- **Megaro et al. 2017** — "A computational design tool for compliant mechanisms"
- Cabrera et al. 2002 — "Optimal synthesis of mechanisms with genetic algorithms"

---

## CE QUE JE CHERCHE PRÉCISÉMENT

### 1. L'algorithme d'optimisation inverse

**Questions :**
- Quelle formulation mathématique exacte ? (fonction objectif, variables de décision, contraintes)
- Quel solveur ? scipy.optimize.minimize (L-BFGS-B, SLSQP) ? differential_evolution ? Basin-hopping ?
- Comment gérer le problème multi-modal ? (plusieurs configurations de cames donnent des trajectoires similaires)
- Comment décomposer une trajectoire 2D en composantes X(θ) et Y(θ) qui correspondent chacune à une came ?

**Ma formulation actuelle (à valider/améliorer) :**
```python
# Variables de décision pour N cames :
# x = [Rb_1, h_1, beta_rise_1, beta_return_1, phase_1, law_idx_1, 
#       Rb_2, h_2, beta_rise_2, beta_return_2, phase_2, law_idx_2, ...]

# Fonction objectif :
def objective(x, target_trajectory):
    """Minimiser l'erreur entre trajectoire cible et trajectoire simulée."""
    cams = decode_params(x)
    simulated = forward_simulate(cams)  # → points (x,y) sur un cycle
    # Discrete Fréchet distance ou simple MSE ?
    return frechet_distance(target_trajectory, simulated)

# Contraintes :
# - pressure_angle(θ) < 30° pour tout θ
# - radius_of_curvature(θ) > 0 pour tout θ (pas d'undercut)
# - max_torque < motor_capacity
# - Rb + h < max_radius (encombrement)
# - épaisseur came > 3mm
```

### 2. La décomposition de trajectoire

Si l'utilisateur dessine un cercle, il faut 2 cames (X = sin, Y = cos). Si c'est un mouvement linéaire vertical, 1 came suffit.

**Questions :**
- Comment décomposer automatiquement une trajectoire 2D arbitraire en N composantes 1D ?
- PCA ? FFT ? Autre méthode ?
- Comment déterminer N_cams optimal ? (1, 2, ou 3)
- L'approche Disney de "sparse sampling" de l'espace des paramètres est-elle meilleure que l'optimisation directe ?

### 3. La correspondance trajectoire → loi de mouvement

J'ai 8 lois de mouvement. Chacune a une forme caractéristique. Comment matcher automatiquement une portion de trajectoire à la meilleure loi ?

**Ma piste :**
- Pré-calculer les signatures (dérivées, harmoniques FFT) de chaque loi
- Pour chaque segment de la trajectoire cible, calculer sa signature
- Nearest-neighbor dans l'espace des signatures → meilleure loi

### 4. Gestion des mécanismes non-came

Parfois un mécanisme à bielles (4-bar linkage) reproduit mieux une trajectoire qu'une came. Comment décider ?

**Critères possibles :**
- Si la trajectoire a des boucles fermées → 4-bar linkage
- Si c'est un aller-retour simple → came classique
- Si c'est une rotation partielle → levier + came

### 5. Implémentation pratique en Python

**Ce dont j'ai besoin en sortie (code Python utilisable) :**

```python
class InverseSolver:
    """Brique G — Solveur inverse de cames."""
    
    def __init__(self, chassis_config, constraint_engine):
        self.config = chassis_config
        self.constraints = constraint_engine
    
    def solve(self, target_trajectory_xy, max_cams=3, timeout_s=30):
        """
        Entrée : liste de points [(x0,y0), (x1,y1), ...] = 1 cycle de trajectoire
        Sortie : list[CamProfile] + phases + transmission_type
        """
        # 1. Décomposer la trajectoire en composantes
        components = self.decompose_trajectory(target_trajectory_xy)
        
        # 2. Pour chaque composante, trouver la meilleure came
        cam_solutions = []
        for comp in components:
            sol = self.optimize_single_cam(comp)
            cam_solutions.append(sol)
        
        # 3. Vérifier les contraintes physiques
        self.validate_solution(cam_solutions)
        
        # 4. Retourner
        return InverseSolution(cams=cam_solutions, ...)
    
    def decompose_trajectory(self, points):
        """Décomposer XY en N composantes 1D."""
        ...
    
    def optimize_single_cam(self, target_1d):
        """Optimiser paramètres d'une came pour reproduire target_1d."""
        ...
```

---

## LIVRABLES ATTENDUS

Je veux que tu me donnes :

### A. L'algorithme complet détaillé
Pas juste un résumé — le **pseudocode complet** avec :
- La formulation mathématique exacte (objectif + contraintes)
- Le choix du solveur et pourquoi
- La stratégie d'initialisation (comment éviter les minima locaux)
- La méthode de décomposition de trajectoire
- Le critère de sélection du nombre de cames

### B. L'état de l'art consolidé
- Ce que Disney a fait exactement (leur approche)
- Ce que les papiers post-2013 ont amélioré
- Les approches modernes (neural-network-based inverse kinematics vs classical optimization)
- Les limitations connues et les pièges

### C. Les formules mathématiques
- Fréchet distance vs MSE vs autre métrique pour comparer trajectoires
- Formule de l'angle de pression en fonction des paramètres de came
- Formule du rayon de courbure minimal
- Jacobien analytique pour scipy (si possible, sinon justifier finite-diff)

### D. Le code Python exploitable
- Fonctions d'optimisation avec scipy
- Fonctions de décomposition de trajectoire
- Pré-calcul de lookup tables pour accélérer
- Le tout compatible avec ma structure existante (CamProfile, MotionPrimitive, etc.)

### E. Plan de tests
- Cas simples : mouvement vertical pur (→ 1 came)
- Cas moyen : mouvement en arc (→ 1 came + levier)
- Cas complexe : trajectoire en 8 (→ 2 cames déphasées)
- Cas dégénéré : trajectoire impossible → message d'erreur gracieux

---

## CONTRAINTES TECHNIQUES

- **Python 3.10+** (pas de typing fancy, ça tourne sur Ender-3 OctoPrint)
- **scipy** est disponible (optimize, interpolate, fft)
- **numpy** est disponible
- **trimesh** est disponible (pour le mesh 3D des cames)
- **PAS de torch/tensorflow** — trop lourd pour l'environnement cible
- Le solveur doit converger en **< 30 secondes** sur un Raspberry Pi 4 (cas simple) et < 120s (cas complexe)
- Le résultat doit être directement injectible dans mon pipeline existant :

```python
# Ce que le solveur retourne doit être convertible en :
cam_profile = CamProfile(segments=[
    CamSegment(beta_deg=120, displacement=15.0, law="cycloid"),
    CamSegment(beta_deg=60, displacement=0.0, law="dwell"),
    CamSegment(beta_deg=120, displacement=-15.0, law="cycloid"),
    CamSegment(beta_deg=60, displacement=0.0, law="dwell"),
])
```

---

## MON PIPELINE EXISTANT (pour contexte)

```python
# Structure d'une came dans mon système :
@dataclass
class CamSegment:
    beta_deg: float      # arc angulaire du segment (somme = 360°)
    displacement: float  # déplacement du suiveur (mm)
    law: str            # 'cycloid', 'modified_trapezoid', 'simple_harmonic', etc.

@dataclass  
class CamProfile:
    segments: List[CamSegment]
    base_radius: float = 30.0
    roller_radius: float = 5.0
    
    def evaluate(self, theta_deg) -> float:
        """Retourne le déplacement s(θ) à l'angle θ."""
        ...
    
    def get_polar_points(self, n=360) -> np.ndarray:
        """Retourne N points (r, θ) du profil de came."""
        ...
    
    def pressure_angle(self, theta_deg) -> float:
        """Angle de pression à θ."""
        ...
    
    def min_radius_of_curvature(self) -> float:
        """Rayon de courbure minimum sur tout le profil."""
        ...

# Lois de mouvement disponibles :
MOTION_LAWS = {
    'cycloid': lambda u: u - np.sin(2*np.pi*u)/(2*np.pi),
    'modified_trapezoid': ...,
    'simple_harmonic': lambda u: (1 - np.cos(np.pi*u))/2,
    'polynomial_345': lambda u: 10*u**3 - 15*u**4 + 6*u**5,
    'polynomial_4567': lambda u: 35*u**4 - 84*u**5 + 70*u**6 - 20*u**7,
    'modified_sine': ...,
    'constant_velocity': lambda u: u,
    'dwell': lambda u: 0.0,
}
```

---

## RÉSUMÉ EN UNE PHRASE

**Je veux l'algorithme complet, mathématiquement rigoureux et implémentable en Python/scipy, pour résoudre le problème inverse : "étant donné une trajectoire XY dessinée par l'utilisateur, trouver les paramètres de came(s) qui la reproduisent au mieux sous contraintes mécaniques FDM"** — en s'inspirant de Coros et al. 2013 (Disney Research) et de l'état de l'art post-2013.
