# 🔬 PROMPT DATA EXTRACTION — Figurines Articulées pour Automates 3D Imprimés

> **Objectif** : Extraire toutes les données techniques nécessaires pour coder un module de **figurine articulée** qui se pose sur un mécanisme à came. La figurine doit avoir des parties fixes (corps/carapace) et des parties mobiles (tête, pattes, queue, ailes, mâchoire) connectées au mécanisme par des pushrods.

---

## COPIER-COLLER CE PROMPT DANS CHATGPT :

---

Tu es un expert en conception mécanique de jouets articulés imprimés en 3D (FDM, PLA). Je développe un **générateur automatique d'automates à came** qui produit des fichiers STL imprimables. Le système génère déjà le mécanisme interne (châssis, cames, leviers, arbres, manivelle). 

**Mon problème** : je dois maintenant générer automatiquement des **figurines articulées** qui se posent sur le mécanisme. La figurine doit avoir :
- Des parties **fixes** (corps vissé/clipsé au châssis)
- Des parties **mobiles** (tête qui hoche, pattes qui marchent, queue qui bouge, ailes qui battent, mâchoire qui s'ouvre)
- Des **articulations imprimables** entre parties fixes et mobiles
- Des **connexions pushrod** entre le levier du mécanisme et la partie mobile de la figurine

J'ai besoin de données EXHAUSTIVES et CHIFFRÉES. Pas de blabla, que du concret avec des cotes en mm.

---

### BLOC 1 — TYPES D'ARTICULATIONS IMPRIMABLES FDM (PLA)

Pour CHAQUE type d'articulation ci-dessous, donne-moi :
- **Géométrie exacte** (dimensions, rayons, angles) avec schéma ASCII
- **Clearances** entre pièces (en mm) pour FDM 0.4mm nozzle, layer 0.2mm
- **Amplitude angulaire** réaliste (degrés min/max)
- **Force maximale** supportée avant rupture (Newtons)
- **Avantages / inconvénients** pour un automate à came
- **Orientation d'impression** recommandée
- **Code pseudo-CSG** pour générer la géométrie en trimesh (Python)

Types d'articulations :
1. **Pin joint (axe traversant)** — un cylindre traverse un trou. Ex: cou de poulet, hanche.
2. **Snap-fit ball joint (rotule clipsable)** — bille dans une coupelle. Ex: épaule, hanche multi-axe.
3. **Living hinge (charnière intégrée)** — pont mince entre 2 parties. Ex: mâchoire, aileron.
4. **Print-in-place pivot** — imprimé assemblé (clearance dans le Gcode). Ex: tête qui tourne.
5. **Mortaise-tenon cylindrique** — cylindre mâle/femelle avec axe de rotation. Ex: articulation coude.
6. **Cantilever snap-fit** — languette flexible avec crochet. Ex: clipser figurine sur châssis.
7. **Dovetail slide** — queue d'aronde pour mouvement linéaire. Ex: patte qui avance/recule.
8. **Hinge with pin** — charnière classique avec axe (2 pièces + axe imprimé). Ex: aile de papillon.
9. **Compliant mechanism / flexure** — lame flexible qui plie. Ex: nageoire de poisson.
10. **Crank-slider pivot** — bielle-manivelle miniature. Ex: patte de marcheur.

---

### BLOC 2 — TABLE DE CORRESPONDANCE MOUVEMENT ↔ ARTICULATION

Pour CHAQUE mouvement d'automate, quel type d'articulation est optimal ?

| Mouvement | Partie du corps | Axe rotation | Type articulation recommandé | Amplitude typique | Force pushrod typique |
|-----------|----------------|--------------|------------------------------|--------------------|-----------------------|
| Hocher la tête (nod) | Tête | X (pitch) | ? | ? | ? |
| Tourner la tête (pan) | Tête | Z (yaw) | ? | ? | ? |
| Ouvrir la mâchoire | Mâchoire inf. | X (pitch) | ? | ? | ? |
| Battre des ailes | Ailes | Y (roll) | ? | ? | ? |
| Marcher (lever patte) | Patte | X (pitch) | ? | ? | ? |
| Marcher (avancer patte) | Patte | Y (slide) | ? | ? | ? |
| Balancer la queue (up/down) | Queue | X (pitch) | ? | ? | ? |
| Balancer la queue (left/right) | Queue | Z (yaw) | ? | ? | ? |
| Nager (ondulation) | Corps/nageoire | alternating | ? | ? | ? |
| Rouler les yeux | Yeux | X ou Z | ? | ? | ? |
| Lever les bras | Bras | X (pitch) | ? | ? | ? |
| Serrer/ouvrir la pince | Pince | Z (yaw) | ? | ? | ? |

---

### BLOC 3 — CLEARANCES ET TOLÉRANCES FDM DÉTAILLÉES

Donne-moi un tableau COMPLET des clearances pour FDM PLA avec nozzle 0.4mm :

| Configuration | Clearance radiale (mm) | Clearance axiale (mm) | Notes |
|---------------|------------------------|----------------------|-------|
| Axe Ø3mm dans trou (rotation libre) | ? | ? | ? |
| Axe Ø4mm dans trou (rotation libre) | ? | ? | ? |
| Axe Ø5mm dans trou (rotation libre) | ? | ? | ? |
| Axe Ø6mm dans trou (rotation libre) | ? | ? | ? |
| Axe dans trou (press-fit) | ? | ? | ? |
| Ball joint Ø6mm | ? | ? | Ouverture coupelle ? |
| Ball joint Ø8mm | ? | ? | ? |
| Ball joint Ø10mm | ? | ? | ? |
| Snap-fit languette | ? | ? | Épaisseur ? Angle ? |
| Living hinge (PLA) | N/A | N/A | Épaisseur min ? Largeur ? |
| Dovetail slide | ? | ? | Angle queue d'aronde ? |
| Print-in-place | ? | ? | Clearance Z min ? |

Pour chaque cas, précise :
- Valeur NOMINALE
- Valeur SERRÉE (pour Bambu Lab X1C / Ender-3 Pro)
- Valeur SÛRE (pour imprimante mal calibrée)

---

### BLOC 4 — PUSHROD ROUTING (connexion levier ↔ figurine)

Comment physiquement connecter un levier de came (mouvement vertical, 5-12mm d'amplitude) à une partie mobile de figurine ?

Pour chaque configuration, donne-moi :
- **Schéma mécanique** (ASCII)
- **Conversion de mouvement** (vertical → rotation, vertical → horizontal, etc.)
- **Rapport d'amplification** ou de réduction
- **Dimensions typiques** en mm
- **Nombre de pièces imprimées** nécessaires
- **Formule** pour calculer l'amplitude angulaire de sortie en fonction de l'amplitude linéaire d'entrée

Configurations :
1. **Pushrod droit** → pivot simple (vertical → rotation pitch)
2. **Pushrod + bell-crank** → conversion 90° (vertical → horizontal)  
3. **Pushrod + bielle** → mouvement alternatif (vertical → oscillation)
4. **Pushrod + crank-slider** → rotation continue (vertical → rotation)
5. **Pushrod + parallélogramme** → translation pure (vertical → vertical décalé)
6. **Pushrod + levier déporté** → amplification (5mm → 15mm)
7. **Fil flexible / bowden** → routing courbe (vertical → direction quelconque)
8. **Pushrod bifurqué (Y-split)** → 1 came → 2 mouvements synchronisés

Pour un automate tortue qui hoche la tête :
- Le levier monte de 8mm
- La tête doit tourner de ~30° autour du cou
- Le cou est à ~50mm au-dessus du levier
- Dessine le mécanisme complet avec toutes les cotes

---

### BLOC 5 — BODY PLANS ARTICULÉS PAR ESPÈCE

Pour CHAQUE body plan ci-dessous, décris l'architecture d'articulation complète :

**Pour chaque body plan :**
- Schéma ASCII vu de côté montrant les articulations
- Liste des pièces (fixes vs mobiles)
- Type d'articulation pour chaque joint
- Pushrod routing depuis le mécanisme
- Nombre de cames nécessaires (min → max)

| # | Body plan | Exemple | Mouvements typiques |
|---|-----------|---------|---------------------|
| 1 | Quadrupède à carapace | Tortue | Tête hoche, 4 pattes marchent, queue |
| 2 | Oiseau debout | Poule, canard | Tête picore, ailes battent, queue |
| 3 | Oiseau en vol | Aigle, papillon | Ailes battent, tête tourne |
| 4 | Bipède | Humain, robot | Bras lèvent, jambes marchent, tête |
| 5 | Quadrupède standard | Chat, chien, cheval | 4 pattes, tête, queue |
| 6 | Poisson/serpent | Poisson, anguille | Ondulation corps, mâchoire, nageoires |
| 7 | Arthropode 6 pattes | Fourmi, scarabée | 6 pattes tripod, mandibules, antennes |
| 8 | Arthropode 8 pattes | Araignée | 8 pattes alternées, chélicères |
| 9 | Crustacé | Crabe, homard | Pinces, 8 pattes, antennes |
| 10 | Céphalopode | Pieuvre, calamar | 8 tentacules ondulants |
| 11 | Gastéropode | Escargot | Tête sort/rentre, cornes, pied glisse |
| 12 | Dragon/fantaisie | Dragon | Ailes, queue, mâchoire, 4 pattes |

---

### BLOC 6 — DIMENSIONNEMENT PARAMÉTRIQUE

Donne-moi les **formules** et **ratios** pour dimensionner automatiquement les articulations en fonction de la taille de la figurine :

1. **Diamètre d'axe** en fonction de : masse de la partie mobile, amplitude, fréquence
2. **Épaisseur de paroi** autour des trous d'axe
3. **Longueur de pushrod** en fonction de la distance levier→joint
4. **Diamètre de pushrod** en fonction de la force et de la longueur (flambage)
5. **Épaisseur de living hinge** en fonction de l'amplitude et du nombre de cycles
6. **Taille de ball joint** en fonction de la masse et du mouvement
7. **Couple résistant** d'une articulation PLA (friction + poids)
8. **Force minimale du pushrod** pour vaincre la friction + gravité
9. **Retour élastique** : quand faut-il un ressort vs gravité vs friction ?
10. **Formule d'amplitude angulaire** : θ = atan(amplitude_pushrod / bras_levier)

Tout en unités SI avec exemples numériques pour une figurine de 45mm de haut en PLA.

---

### BLOC 7 — ANTI-PATTERNS ET PIÈGES FDM

Liste-moi les **erreurs classiques** à éviter quand on imprime des articulations en PLA :

1. Orientation d'impression qui tue les joints
2. Surextrusion qui fusionne les pièces print-in-place
3. Sous-dimensionnement des axes (cassure)
4. Living hinges qui cassent après 10 cycles
5. Ball joints impossibles à assembler
6. Pushrods qui flambent
7. Friction excessive → le mécanisme bloque
8. Jeu excessif → mouvement mou/imprécis
9. Porte-à-faux non supportés
10. Ponts (bridges) qui s'effondrent sur les trous

Pour chaque erreur : cause, solution, cotes critiques.

---

### BLOC 8 — MATÉRIAUX ET FATIGUE

Table de propriétés mécaniques pour les articulations :

| Propriété | PLA | PETG | TPU 95A | Notes |
|-----------|-----|------|---------|-------|
| Module Young (GPa) | ? | ? | ? | |
| Contrainte rupture (MPa) | ? | ? | ? | |
| Allongement rupture (%) | ? | ? | ? | |
| Fatigue 10k cycles (% de rupture) | ? | ? | ? | |
| Fatigue 100k cycles (% de rupture) | ? | ? | ? | |
| Coefficient friction PLA/PLA | ? | ? | ? | |
| Coefficient friction PLA/PETG | ? | ? | ? | |
| Épaisseur living hinge min (mm) | ? | ? | ? | |
| Température ramollissement (°C) | ? | ? | ? | |
| Fluage sous charge constante | ? | ? | ? | |

---

### BLOC 9 — EXEMPLES CONCRETS AVEC COTES

Donne-moi **3 exemples complets** avec toutes les cotes en mm :

**Exemple 1 — Tortue qui hoche la tête (1 came)**
- Carapace fixe sur châssis
- Tête sur pivot au cou
- 1 pushrod vertical → pivot cou → rotation 25°
- Toutes les cotes : diamètre axe, clearance, longueur pushrod, point d'attache, bras de levier

**Exemple 2 — Oiseau qui bat des ailes (2 cames)**
- Corps fixe
- 2 ailes sur pivots latéraux
- 2 pushrods → 2 pivots → battement ±35°
- Mécanisme de synchronisation (1 came → 2 ailes via Y-split OU 2 cames séparées)

**Exemple 3 — Chat qui marche (4 cames)**
- Corps fixe
- 4 pattes sur pivots (2 DOF chacune: lever + avancer)
- Pattern de marche: diagonales en phase
- Gait timing: FL+RR en phase, FR+RL déphasées 180°
- Toutes les cotes des articulations de hanches

---

### BLOC 10 — PSEUDO-CODE PYTHON

Donne-moi le **pseudo-code Python** pour :

```python
class ArticulatedFigurine:
    """Génère une figurine avec des articulations fonctionnelles."""
    
    def split_body(self, body_mesh, joint_definitions):
        """Coupe un mesh en parties fixes et mobiles autour des joints."""
        # Comment découper ? Boolean ? Plans de coupe ?
        
    def create_pin_joint(self, diameter, length, clearance):
        """Crée un axe + trou pour articulation pivot."""
        # Géométrie exacte ?
        
    def create_ball_joint(self, diameter, cup_opening_angle):
        """Crée une rotule (bille + coupelle)."""
        # Géométrie exacte ?
        
    def route_pushrod(self, start_point, end_point, obstacles):
        """Route un pushrod du levier au joint, en évitant les obstacles."""
        # Algorithme ? Pathfinding ?
        
    def calculate_motion(self, pushrod_amplitude, joint_type, arm_length):
        """Calcule l'amplitude de mouvement de la partie articulée."""
        # Formules cinématiques ?
        
    def add_return_mechanism(self, joint, method='gravity'):
        """Ajoute un mécanisme de retour (gravité, ressort, friction)."""
        # Quand utiliser quoi ?
```

Remplis CHAQUE méthode avec le code réel, les formules, et les edge cases.

---

### FORMAT DE RÉPONSE ATTENDU

- **Tableaux** avec des valeurs numériques (pas de "ça dépend")
- **Formules** en notation mathématique avec variables définies
- **Cotes en mm** avec précision 0.1mm
- **Schémas ASCII** quand c'est utile
- **Références** (papers, datasheets, guides de design)
- Si une valeur est incertaine, donne une **plage** [min, max] avec la valeur recommandée

Pas de disclaimers, pas de "je suis un modèle de langage". Que de la data.
