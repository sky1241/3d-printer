# 🔧 Guide d'Assemblage — Automata Generator v4

## Vue d'ensemble

Ce guide explique comment assembler un automate mécanique généré par le système.
Chaque automate est composé de pièces imprimées en 3D (PLA) et de quincaillerie standard.

---

## Quincaillerie nécessaire

| Pièce | Spécification | Quantité | Rôle |
|-------|--------------|----------|------|
| Tige acier | Ø4mm ou Ø6mm (selon espèce) | 1-2 | Arbre à cames |
| Vis M3×10 | ISO 4762 (tête hex creuse) | 4-8 | Fixation base |
| Inserts M3 | Ø4mm×4mm (thermique) | 4-8 | Filetage dans PLA |
| E-clips | Ø4mm ou Ø6mm | 2-6 | Blocage axial |
| Fil acier | Ø1.5mm (corde à piano) | Par pushrod | Tiges de liaison |

> **Astuce :** Pour les espèces ≤5 cames, Ø4mm suffit. Au-delà, le système auto-upgrade à Ø6mm.

---

## Étapes d'assemblage

### 1. Préparer les pièces imprimées

- Retirer les supports (surtout dans les trous de guidage)
- Vérifier que les perçages D-flat des cames sont propres (lime fine)
- Tester l'ajustement de chaque came sur la tige acier : elle doit coulisser librement mais sans jeu excessif

### 2. Monter la base et les murs

1. Placer la **base_plate** à plat
2. Insérer les **inserts M3** dans les trous de la base (fer à souder à 220°C)
3. Fixer les **wall_left** et **wall_right** avec les vis M3
4. Si présent, fixer le **camshaft_bracket** (mur intermédiaire)
5. Si dual-shaft : fixer aussi le **mid_bearing_wall**

### 3. Assembler l'arbre à cames

1. **Aplatir la tige** : limer un méplat (D-flat) de 0.5mm sur toute la longueur de la zone cames
2. **Enfiler les cames** dans l'ordre indiqué (voir BOM), en respectant les angles de phase
   - Le D-flat empêche la rotation : aligner le méplat de chaque came
   - Utiliser les repères de phase gravés sur chaque came (trait = 0°)
3. **Bloquer axialement** avec les e-clips dans les gorges prévues
4. **Insérer l'arbre** dans les paliers des murs (gauche → bracket → droit)

> **Dual-shaft** : Répéter pour les 2 arbres. Monter les **sync_gears** en dernier, en vérifiant l'engrènement.

### 4. Installer les leviers et followers

1. Glisser chaque **levier** sur son **pin_lever** (axe pivot)
2. Fixer avec les **colliers L/R** de chaque côté
3. Vérifier que le galet (bout du levier) repose sur la came correspondante
4. Le levier doit pivoter librement avec un peu de jeu

### 5. Monter la figurine

1. Assembler les pièces de la figurine (body, head, legs, etc.)
2. Les **pin_joints** connectent les parties mobiles (tête, pattes, ailes)
3. Positionner la figurine sur le châssis
4. Connecter les **pushrods** (tiges de liaison) :
   - Bout supérieur → trou dans la figurine
   - Bout inférieur → socket sur le levier
   - Plier légèrement le fil si nécessaire pour éviter les frottements

### 6. Entraînement

**Mode manivelle (crank)** :
- Tourner la manivelle à ~2 RPM pour un mouvement fluide
- La tige acier de l'arbre dépasse côté manivelle

**Mode moteur** :
- Moteur N20 (150:1 ou 298:1 selon complexité)
- Fixer le motor_mount, connecter via accouplement

---

## Conseils de dépannage

| Symptôme | Cause probable | Solution |
|----------|---------------|----------|
| Arbre tourne dur | Paliers serrés | Poncer légèrement l'intérieur des perçages |
| Came patine sur l'arbre | D-flat insuffisant | Limer plus profond (0.5-0.8mm) |
| Levier ne retombe pas | Frottement pin/bracket | Ajouter une goutte d'huile, vérifier alignement |
| Figurine ne bouge pas | Pushrod déconnecté | Vérifier le clip/socket aux deux extrémités |
| Mouvement saccadé | Phase mal calée | Re-vérifier l'angle de phase de chaque came |
| Moteur cale | Trop de friction | Huiler les paliers, vérifier que rien ne frotte |

---

## Paramètres d'impression recommandés

| Paramètre | Valeur | Note |
|-----------|--------|------|
| Matériau | PLA | Rigidité suffisante pour les engrenages |
| Hauteur couche | 0.2mm | Compromis qualité/temps |
| Remplissage | 20-30% | Grille ou gyroïde |
| Périmètres | 3 | Solidité des parois |
| Supports | Oui (selon pièce) | Surtout pour les perçages horizontaux |
| Température | 210°C buse / 60°C plateau | PLA standard |
| Vitesse | 50mm/s | Réduire à 30mm/s pour les engrenages |

> **Ender-3** : bed 220×220mm, hauteur max 250mm
> **Bambu Lab X1C** : bed 256×256mm, AMS compatible

---

## Nomenclature des pièces (conventions)

| Préfixe | Type | Exemple |
|---------|------|---------|
| `cam_` | Came (disque profilé) | `cam_hip_fl` |
| `lever_` | Bras de levier | `lever_neck` |
| `bracket_lever_` | Support de levier | `bracket_lever_hip_fl` |
| `pin_lever_` | Axe pivot du levier | `pin_lever_neck` |
| `collar_L_` / `collar_R_` | Collier axial | `collar_L_hip_fl` |
| `follower_guide_` | Guide du suiveur | `follower_guide_0` |
| `pushrod_` | Tige de liaison | `pushrod_neck` |
| `fig_` | Pièce de figurine | `fig_body`, `fig_head` |
| `wall_` | Mur latéral du châssis | `wall_left` |
| `base_plate` | Plaque de base | — |
| `camshaft` | Arbre à cames (imprimé) | — |
| `sync_gear_` | Engrenage de synchronisation | `sync_gear_A` |
| `crank_handle` | Manivelle | — |
| `motor_mount` | Support moteur | — |

---

*Généré par Automata Generator v4 — 13 février 2026*
