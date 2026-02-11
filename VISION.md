# 🎯 VISION — Ce qu'on a compris à 3h30 du matin

## Le vrai projet

L'utilisateur **dessine à la main** sur un canvas → le système génère **toute la mécanique** automatiquement (cames, suiveurs, châssis, STL).

Pas un menu de presets. Un outil de dessin.

## Ce qu'on a déjà

- Le moteur paramétrique : 16 243 lignes, 94 tests ✅
- Constraint engine, solveur inverse, export STL
- Tout le backend est prêt

## Ce qu'il manque

- L'interface de dessin (canvas)
- Le pont entre le dessin et le moteur

## Les vraies questions à résoudre (frais, pas à 3h du mat)

1. **X = formes primitives** : rond, carré, triangle, rectangle, losange
2. **Y = dynamique** : comment chaque forme bouge (axe de pivot, direction, amplitude)
3. **Comment l'utilisateur indique le mouvement ?** Flèche ? Drag ? Animation preview ?
4. **Comment le système détecte quelles pièces sont liées ?** (les ailes attachées au corps)
5. **Comment éviter le "dessin de gamin qui bug" ?** → contraintes, snapping, formes assistées ?

## Le doute de 3h du mat

"Un gamin va dessiner de la merde, ça va bug de partout"
→ C'est un vrai problème de design à résoudre. Mais c'est un problème d'UX, pas un problème de moteur. Le moteur est solide.

## Options pour demain

- **Option A** : Dessin libre + contraintes intelligentes (snap-to-grid, formes magnétiques)
- **Option B** : Bibliothèque de formes qu'on assemble (drag & drop de primitives)
- **Option C** : Hybride — presets modifiables visuellement (tu pars d'un oiseau, tu changes les formes)

Rien n'est voué à l'échec. Faut juste choisir le bon chemin.

---
*Écrit le 11 février 2026 à 3h30. À relire frais.*
