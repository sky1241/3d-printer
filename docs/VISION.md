# 🧠 VISION — Automata Generator : le vrai projet

*Rédigé le 11 février 2026 à 3h30 — après 4-5 jours de dev intensif*

---

## Ce qu'on a construit (le moteur)

- `automata_unified_v4.py` — 16 243 lignes, 94/94 tests ✅
- Constraint engine complet (B1→B9)
- Solveur inverse (differential evolution + L-BFGS-B)
- Export STL + BOM + timing
- 22 presets, parser FR/EN
- Optimisé Bambu Lab X1C / Ender-3

**Le moteur est prêt. C'est la partie la plus dure et elle est faite.**

---

## Ce qu'on a mis dessus (la carrosserie actuelle)

Un site avec un menu de presets : "oiseau", "chat", "canard"...
Des formes hard-codées. Un menu déroulant.

→ C'est une Twingo avec un moteur Ferrari.

---

## La vraie vision (le saint graal)

**L'utilisateur dessine → le système fait tout.**

1. L'utilisateur dessine des formes simples sur un canvas (ronds, triangles, rectangles)
2. Il indique quel mouvement il veut (cette pièce monte/descend, celle-là bascule)
3. Le moteur paramétrique calcule automatiquement : cames, suiveurs, châssis, liaisons
4. Export STL prêt à imprimer

**Pas de menu. Pas de presets hard-codés. Du dessin libre → de la mécanique.**

---

## Les vrais X et Y (à définir proprement)

**X = les formes primitives**
- Rond, carré, triangle, rectangle, losange
- Un "oiseau" c'est juste : ellipse (corps) + cercle (tête) + triangle (bec) + triangles (ailes)
- L'utilisateur assemble ces primitives

**Y = le mouvement de chaque pièce**
- Pour chaque forme, il faut définir :
  - Le **point de pivot** (où est l'axe : haut, bas, centre, bord)
  - La **direction du mouvement** (haut-bas, gauche-droite, rotation)
  - L'**amplitude** et le **timing** (came)
- Exemple : aile (triangle) + pivot en bas + direction haut-bas = battement

**Matrice : Forme × Point de pivot × Direction = comportement mécanique**

Les coefficients (5x + 3y) c'est les paramètres numériques :
amplitude, vitesse, phase, nombre de cames, etc.

---

## Les problèmes réels à résoudre

### 1. "Un gamin va dessiner de la merde"
Oui. Faut des contraintes intelligentes :
- Snap-to-grid pour aligner les formes
- Formes prédéfinies (pas du dessin libre total)
- Validation en temps réel ("cette pièce est trop petite pour être imprimée")
- Le constraint engine (94 checks) sert exactement à ça

### 2. "Le système va bug de partout"
Approche progressive :
- Phase 1 : formes simples + 1 mouvement → ça marche d'abord avec le cas simple
- Phase 2 : multi-pièces + multi-mouvements
- Phase 3 : dessin libre
- Les presets actuels deviennent des **exemples/templates**, pas le produit

### 3. "Le pont entre le dessin et le moteur"
C'est la pièce manquante. Il faut traduire :
- Dessin canvas → `AutomataScene` (le format du moteur)
- Chaque forme dessinée → un `Link` ou `MotionTrack`
- Chaque mouvement indiqué → des `CamSegment`
- Le solveur fait le reste

### 4. Ludo n'aime pas les imprimantes 3D
Et c'est pas grave. Le projet c'est l'**algorithme**, la **génération paramétrique**.
L'impression 3D c'est juste le médium de sortie.
Le vrai produit c'est : dessin → mécanique automatique.
Ça pourrait sortir en SVG, en animation, en PDF, en instructions LEGO, whatever.

---

## Prochaines étapes (quand t'es reposé)

1. **Poser la matrice** : lister toutes les formes primitives, tous les mouvements possibles, tous les points de pivot
2. **Prototyper le canvas de dessin** : juste drag & drop de formes simples, pas de dessin libre
3. **Le pont** : forme dessinée → AutomataScene → moteur
4. **Garder les presets** comme exemples/démonstration, pas comme produit final

---

## État actuel des fichiers

- `automata_unified_v4.py` — le moteur (16 243 lignes, 94 tests ✅)
- `automata.html` — le site V4.3 (menu presets, 17 figurines, toggle moteur/manivelle)
- `PROMPT_REPRISE_SITE_V4.md` — prompt de reprise pour le site

---

*"J'ai le moteur le plus puissant. Maintenant faut construire le volant."*
