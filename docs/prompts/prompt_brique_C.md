# BRIQUE C — Mouvements V2-V10

## CONTEXTE

Tu travailles sur `automata_unified_v4.py` (15,119 lignes, joint à cette conversation).

C'est un générateur paramétrique d'automates mécaniques imprimables en 3D. Le moteur de cames est complet et fonctionne. Actuellement il ne supporte que 2 types de mouvement :

- **V1 Vertical** : suiveur classique, monte/descend 0-25mm
- **V3 Oscillation** : came symétrique, va-et-vient

Tout passe par `MotionPrimitive` → `MotionTrack` → `compile_scene_to_cams()` → `CamProfile`. Les primitives existantes sont : `LIFT`, `PAUSE`, `WAVE`.

## CE QUE JE VEUX

Ajouter les mouvements manquants pour étendre les possibilités du générateur. Chaque nouveau mouvement doit :

1. S'intégrer dans le système existant de `MotionPrimitive` + `MotionTrack`
2. Passer par `compile_scene_to_cams()` et générer un `CamProfile` valide
3. Être utilisable dans `SceneBuilder.MOVEMENT_TEMPLATES`
4. Passer le `test_master()` sans rien casser
5. Les 10 presets originaux doivent toujours fonctionner

## MOUVEMENTS À IMPLÉMENTER

### V2 — Linéaire horizontal (glissière)
- Le suiveur pousse latéralement au lieu de verticalement
- Amplitude : 0-20mm
- Cas d'usage : tiroir, translation latérale
- Implémentation : nouvelle primitive `SLIDE` ou adaptation du suiveur avec un flag `direction='horizontal'`
- Le profil de came reste identique (c'est le même calcul), seul le montage change
- Dans le `MotionTrack`, ajouter un champ `follower_direction` (default='vertical', option='horizontal')

### V4 — Rotation oscillante (levier)
- Le suiveur pousse un levier qui pivote autour d'un point fixe
- Amplitude : ±30° de rotation
- Cas d'usage : bascule de plateau, balancier
- Implémentation : primitive `ROTATE` avec conversion amplitude_mm → angle via longueur de levier
- Formule : `angle_rad = lift_mm / lever_length_mm`
- Ajouter `lever_length_mm` dans `MotionTrack` (default=0, si >0 → mode levier)
- Le CamProfile ne change PAS — c'est toujours un lift en mm, la conversion angle se fait à la sortie

### V5 — Rotation continue (Geneva drive)
- Rotation 360° en N steps (ex: 4 positions = 90° par step)
- Cas d'usage : plateau tournant, carrousel
- Implémentation : primitive `GENEVA` avec paramètres `n_positions` et `dwell_ratio`
- Le CamProfile génère des segments LIFT alternés avec des DWELL longs
- Note : il y a du code archivé pour Geneva dans le fichier, cherche "geneva" ou "worm" — c'est peut-être réutilisable

### V7 — Séquentiel
- Plusieurs cames coordonnées avec des phases précises pour que les mouvements se suivent
- Cas d'usage : boîte qui s'ouvre en séquence, personnage qui fait un geste puis un autre
- Implémentation : primitive `SEQUENCE` qui est un macro qui génère automatiquement les phases
- Ou plus simplement : ajouter une fonction `create_sequential_tracks(movements, dwell_between)` qui calcule les phases automatiquement pour que les mouvements ne se chevauchent pas

### V8 — Impact/frappe (came asymétrique)
- Montée lente, descente rapide (ou l'inverse)
- Cas d'usage : marteau de forgeron, pivert
- Implémentation : c'est déjà faisable avec des LIFT asymétriques (beta_rise >> beta_return), mais ajouter une primitive `STRIKE` qui est un raccourci pour :
  - `LIFT(amplitude, beta_rise=240)` + `LIFT(-amplitude, beta_return=80)` + `PAUSE(40)`
- Le ratio rise/return est paramétrable

### V9 — Maintien/verrou (dwell long)
- La came maintient le suiveur en position haute pendant longtemps (>180°)
- Cas d'usage : porte qui reste ouverte, bras qui reste levé
- Implémentation : primitive `HOLD` = `LIFT(amp, 60)` + `PAUSE(beta_hold)` + `LIFT(-amp, 60)` + `PAUSE(rest)`
- `beta_hold` paramétrable (default=200°)

### V10 — Multi-axe
- Combine 2 mouvements sur le même objet (vertical + horizontal, ou vertical + rotation)
- Cas d'usage : trajectoire complexe, mouvement en L
- Implémentation : `MultiAxisTrack` qui contient 2 `MotionTrack` liés au même objet
- Chaque axe a sa propre came mais le résultat est combiné sur la figurine
- C'est principalement du routing dans `SceneBuilder` — 2 cames, 2 suiveurs, 1 objet

## COMMENT IMPLÉMENTER

1. **Primitives** : Ajouter dans la section MotionPrimitive les nouvelles primitives (SLIDE, ROTATE, GENEVA, STRIKE, HOLD, SEQUENCE). La plupart sont des macros qui se décomposent en LIFT + PAUSE existants.

2. **MotionTrack** : Ajouter les champs optionnels nécessaires (`follower_direction`, `lever_length_mm`, etc.)

3. **compile_scene_to_cams()** : Adapter pour gérer les nouvelles primitives. La plupart se transforment en segments RISE/RETURN/DWELL classiques donc le CamProfile ne change pas.

4. **SceneBuilder.MOVEMENT_TEMPLATES** : Ajouter les templates qui utilisent les nouveaux mouvements.

5. **parse_text_to_figurine_config()** : Ajouter les keywords pour les nouveaux mouvements (tiroir, tournant, carrousel, etc.)

## CONTRAINTES

- NE PAS casser les 10 presets existants
- NE PAS modifier la logique de CamProfile (le calcul de came reste identique)
- NE PAS modifier le constraint engine (les 94 checks doivent passer)
- Les nouvelles primitives doivent se DÉCOMPOSER en LIFT/PAUSE/WAVE existants dans compile_scene_to_cams() — c'est des macros, pas de la nouvelle math
- Garder le fichier monolithique (tout dans automata_unified_v4.py)

## TESTS À FAIRE

Après implémentation, vérifie :

```python
# 1. Master test
python automata_unified_v4.py --test
# Doit afficher: MASTER TEST: ALL PASS

# 2. Les 10 presets originaux
# Tester chaque preset dans SCENE_PRESETS : nodding_bird, flapping_bird, 
# walking_figure, bobbing_duck, rocking_horse, pecking_chicken, waving_cat,
# drummer, blacksmith, swimming_fish
# Tous doivent générer avec stable=✓

# 3. Nouveaux mouvements via texte libre
parse_text_to_figurine_config("tiroir secret") → movement devrait utiliser SLIDE
parse_text_to_figurine_config("plateau tournant") → movement devrait utiliser GENEVA
parse_text_to_figurine_config("marteau qui frappe") → movement devrait utiliser STRIKE

# 4. Pipeline complet pour chaque nouveau mouvement
# Pour chaque nouveau V2-V10, créer une FigurineConfig, passer par
# SceneBuilder.from_figurine(), AutomataGenerator.generate()
# Vérifier : génération OK, stable, imprimable
```

## FICHIER

Le fichier `automata_unified_v4.py` est joint. Fais un patch propre, retourne-moi le fichier complet patché.
