# 🔬 DEEP RESEARCH PROMPT — Dual-Shaft & Printed Gear Synchronization for 3D-Printed Cam Automata

> **Instructions pour ChatGPT :** Active le mode "Search" / "Deep Research". Je veux des réponses basées sur des **sources vérifiables** : papers académiques (ResearchGate, Google Scholar, IEEE, ASME), thèses de master/doctorat, manuels d'ingénierie (Shigley, Norton, Rothbart), documentation de fabricants (Igus, Misumi, McMaster), forums d'ingénieurs (Eng-Tips, GrabCAD), et projets open-source documentés (Thingiverse avec tests réels, Printables, GitHub). **Cite chaque source avec auteur, année, DOI ou URL.** Si tu ne trouves pas de source fiable sur un point précis, dis-le explicitement au lieu d'inventer.

---

## CONTEXTE DU PROJET

Je développe un **générateur procédural d'automates mécaniques imprimés en 3D** (FDM, PLA/PETG, buse 0.4mm, couche 0.2mm). Le système prend un animal en entrée (ex: "scorpion") et génère automatiquement toutes les pièces STL : châssis, arbre à cames, cames profilées, leviers, followers, pushrod, figurine.

### Ce qui marche
- 17 templates de génération, 118 espèces animales
- 17/17 builders génèrent sans crash, 100% pièces watertight
- Profils de came mathématiquement corrects (POLY_4567, CYCLOIDAL)
- Constraint engine avec 95 checks
- Bore D-flat dans les cames (euler=0 confirmé)
- Chaîne cinématique came→levier→pushrod→figurine fonctionnelle

### Ce qui est cassé — les 3 problèmes qui motivent cette recherche

| Problème | Espèces touchées | Données mesurées |
|----------|-----------------|------------------|
| **Arbre trop flexible** | 11/17 | Flèche 0.3mm (butterfly) → 7.3mm (scorpion). Seuil = 0.3mm |
| **Arbre trop long** pour le lit d'impression | 11/17 | 253mm (butterfly) → 491mm (dragon). Lit = 220×220mm |
| **Moteur insuffisant** | 3/17 | Couple requis 97-127 mN·m. Moteur N20 = 90 mN·m max |

**Root cause commune** : au-delà de 5-6 cames, un seul arbre Ø4mm acier de 220mm ne suffit plus. Le scorpion a 13 cames, le dragon 9, le crabe 10.

### Contraintes de fabrication
- **Imprimante** : Ender-3 / Bambu A1 Mini → lit 220×220mm max
- **Matériaux** : PLA (pièces imprimées), acier/laiton Ø4mm (arbre)
- **Buse** : 0.4mm, couche 0.2mm
- **Tolérances** : ±0.2mm XY, ±0.1mm Z
- **Pas d'usinage CNC** — tout doit être imprimable + visserie standard
- **Moteur** : N20 micro-gearmotor (90 mN·m, 30-60 RPM)
- **Budget** : <20€ de quincaillerie par automate

---

## DOMAINE 1 — DUAL-SHAFT : Diviser les cames sur 2 arbres synchronisés

### Questions précises

**1.1 Architecture mécanique**
- Dans les automates mécaniques traditionnels (bois, métal) et les jouets mécaniques, quelles architectures sont utilisées quand il y a plus de 6-8 cames ? Cherche des exemples documentés dans :
  - Les barrel organs / orgues mécaniques
  - Les automates de Jaquet-Droz, Vaucanson, Maillardet
  - Les jouets Automata de cabaret mécanique (Keith Newstead, Carlos Zapata, Paul Spooner)
  - Les karakuri ningyo japonais
  - Les machines industrielles multi-arbres (textile, packaging)
- Quelles configurations existent : arbres parallèles, perpendiculaires (renvoi d'angle), arbres coaxiaux ?
- Quel est le ratio de répartition optimal des cames (50/50, ou grouper par type de mouvement) ?

**1.2 Synchronisation par engrenages imprimés FDM**
- Quel module d'engrenage est imprimable de manière fiable en PLA sur une buse 0.4mm ? Cherche des **tests réels documentés** :
  - Module 1.0mm ? 1.5mm ? 2.0mm ? Quel est le minimum testé et validé ?
  - Nombre minimum de dents pour un fonctionnement lisse ? (12? 16? 20?)
  - Angle de pression : 20° standard vs 14.5° ?
  - Backlash recommandé pour PLA imprimé ? (0.2mm ? 0.3mm ? 0.5mm ?)
  - Profil involute standard vs profil modifié pour FDM ?
- Cherche spécifiquement :
  - Des papers sur "3D printed gears" + "PLA" + "tolerance" ou "backlash"
  - Des projets Thingiverse/Printables avec des engrenages PLA testés et commentés
  - La thèse de Hofstätter (TU Wien) sur les engrenages imprimés
  - Les travaux de l'équipe de Diegel sur l'impression d'engrenages
  - Le gear generator de Dr. Rainer Hessmer (drh-consultancy.demon.co.uk)

**1.3 Tolérance de synchronisation requise**
- Pour un automate jouet tournant à 30-60 RPM, quelle précision angulaire est nécessaire entre 2 arbres synchronisés ?
- Si l'erreur de phase est de ±5° entre les 2 arbres, est-ce visible/acceptable sur un jouet décoratif ?
- Comment le backlash des engrenages imprimés affecte-t-il la synchronisation des cames en aval ?

**1.4 Conception du palier inter-arbres**
- Comment supporter le 2ème arbre ? Options :
  - Mur intermédiaire (bearing wall) avec trou de passage ?
  - Bracket séparé ?
  - Palier en bronze/nylon imprimé vs douille laiton ?
- Quel espacement minimum entre 2 arbres parallèles Ø4mm avec engrenages module 1.5, 20 dents ? (calcul d'entraxe)
- Comment gérer l'alignement axial des 2 arbres pour que les engrenages restent en prise ?

---

## DOMAINE 2 — SHAFT DEFLECTION : Réduire la flèche de l'arbre

### Questions précises

**2.1 Données matériaux pour calcul de flèche**
- Module d'Young de l'acier doux (mild steel) Ø4mm étiré à froid ? (valeur exacte, pas approximation)
- Module d'Young du laiton Ø4mm (CuZn37) ?
- Moment d'inertie I = π×d⁴/64 pour Ø4mm et Ø6mm ?
- Formule de flèche exacte pour arbre sur 2 appuis avec N charges ponctuelles réparties (les cames) ?

**2.2 Palier intermédiaire (mid-bearing)**
- Quelle est la portée maximale sans palier intermédiaire pour un arbre Ø4mm sous charge radiale de 1-5N par came ?
- Un palier intermédiaire imprimé (trou Ø4.5mm dans un mur PLA) ajoute-t-il assez de rigidité ? Quelles sont les données de friction PLA-on-steel ?
- Recherche sur les self-lubricating bearings imprimés : PLA infusé graphite ? Nylon ? PETG ?
- Comparaison : palier imprimé vs douille bronze Ø4mm (Igus ref?) vs roulement à billes 4×8×3mm (réf 684ZZ)

**2.3 Arbre Ø6mm vs Ø4mm**
- Un passage à Ø6mm réduit la flèche d'un facteur (6/4)⁴ = 5.06×. Est-ce suffisant pour les pires cas (scorpion 434mm) ?
- Disponibilité et coût d'une tige acier Ø6mm lisse (Amazon, AliExpress, eBay, quincaillerie) ?
- Impact sur les cames : le bore passe de 4.0 à 6.0mm, le D-flat aussi. Y a-t-il des études sur la résistance d'un bore D-flat dans un disque PLA Ø20-30mm avec trou Ø6mm ?

**2.4 Solutions alternatives**
- Arbre tubulaire imprimé avec tige acier intérieure (renfort composite) ?
- Arbre segmenté avec accouplement (coupler) entre segments ?
- Réduction du cam_spacing : quel espacement minimum entre 2 cames Ø20-30mm pour éviter les interférences tout en réduisant la longueur totale ?

---

## DOMAINE 3 — TORQUE MANAGEMENT : Gérer le couple moteur

### Questions précises

**3.1 Données réelles sur les moteurs N20**
- Courbe couple/vitesse réelle d'un N20 micro-gearmotor avec réducteur 1:100 et 1:150 ?
- Couple de décrochage (stall torque) vs couple nominal ? Quelle marge de sécurité ?
- Cherche des datasheets véritables (pas des listings AliExpress) — idéalement Pololu, DFRobot, ou Zhaowei ZWPD
- Alternative : moteur 28BYJ-48 (stepper) — couple réel mesuré ?

**3.2 Réduction de couple par optimisation des phases**
- Y a-t-il des publications sur l'optimisation de la séquence de phases d'un arbre à cames multi-lobes pour minimiser le pic de couple ?
- En moteur à combustion (engine camshaft timing), comment les phases sont-elles optimisées pour lisser le couple ? (applicable à notre cas ?)
- Algorithme : si j'ai N cames avec chacune un profil de couple C_i(θ), quel algorithme trouve les déphasages φ_i qui minimisent max(Σ C_i(θ + φ_i)) ?

**3.3 Réduction mécanique additionnelle**
- Un étage de réduction par engrenages imprimés (ratio 2:1 ou 3:1) avant l'arbre à cames est-il viable en PLA ?
- Vis sans fin imprimée en PLA : faisable ? Module minimum ? Auto-blocage = avantage pour maintenir la position ?
- Système poulie/courroie imprimée : GT2 en PLA, viable à faible charge ?

---

## DOMAINE 4 — CAS CONCRETS ET PRÉCÉDENTS

### Ce que je cherche
- Y a-t-il des projets open-source d'automates 3D imprimés avec >6 cames ? Si oui, comment gèrent-ils le problème ?
- Le projet "Automata" de Thingiverse user "gzumwalt" — combien de cames max, quel arbre, quelle longueur ?
- Les "marble machines" de Martin Molin ou Wintergatan — comment gèrent-ils les arbres à cames longs ?
- Les projets de Rob Ives (robives.com) — versions imprimées vs carton ?
- Le projet "Cranky Contraptions" — architecture multi-arbre ?

### Données numériques recherchées
Pour chaque exemple trouvé, je veux si possible :
- Nombre de cames
- Diamètre et matériau de l'arbre
- Longueur totale de l'arbre
- Type de paliers
- Motorisation (ou manivelle)
- Matériau des pièces (PLA, bois, métal)
- Source (URL, DOI)

---

## DOMAINE 5 — VALIDATION DES FORMULES

Vérifie ces formules que j'utilise actuellement :

**Flèche arbre (beam deflection) :**
```
δ = (F × L³) / (48 × E × I)    pour charge centrée
I = π × d⁴ / 64
```
- Est-ce la bonne formule pour N charges ponctuelles réparties sur 2 appuis simples ?
- Faut-il utiliser la superposition (Σ des flèches individuelles) ou une formule intégrée ?

**Pression de Hertz came-follower :**
```
σ_H = 0.418 × √(F × E* / (L × R*))
E* = E₁×E₂ / (E₁+E₂)  (contact acier-PLA)
R* = R_cam × R_follower / (R_cam + R_follower)
```
- Cette formule est-elle correcte pour un contact cylindre-plan (flat follower) ?
- Valeur de E* pour contact acier (E=200GPa) sur PLA (E=3.5GPa) ?

**Couple d'une came :**
```
T = F_follower × (Rb + h) × tan(φ)
φ = angle de pression
```
- Cette approximation est-elle suffisante pour un automate jouet ?

---

## FORMAT DE RÉPONSE SOUHAITÉ

Pour chaque domaine, structure ta réponse ainsi :

1. **Réponse courte** (3-5 lignes) — la recommandation directe
2. **Données chiffrées** — les valeurs exactes avec unités
3. **Sources** — auteur, année, titre, DOI/URL
4. **Ce que je n'ai PAS trouvé** — les questions sans réponse fiable

Ne me donne PAS de généralités du type "il faudrait tester". Je veux des **valeurs concrètes issues de tests réels ou de la littérature** que je peux directement injecter dans mon code Python.

---

## RÉSUMÉ — Ce qui bloque concrètement

```
Mon scorpion a 13 cames sur un arbre acier Ø4mm de 434mm.
L'arbre fléchit de 7.3mm (max admissible : 0.3mm).
L'arbre ne rentre pas sur le lit 220mm.
Le couple total dépasse le moteur de 40%.

Comment je split ça en 2 arbres synchronisés par des engrenages
imprimés en PLA, avec quelles dimensions, quels modules, quels
paliers, et quelle erreur de phase est acceptable ?
```
