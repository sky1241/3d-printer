# DEBUG — scene_builder v2 (living_beings_db integration)

## PROBLÈME INITIAL
- scene_builder.py v1 importait animal_db (33 espèces, 6 templates)
- living_beings_db (118 espèces, 42 body plans) était ignoré
- 15/42 body plans tombaient en fallback quadrupède générique
- Araignée 8 pattes → généré comme quadrupède ❌
- Crabe → pas de marche latérale ❌
- Insectes → pas de tripod 6 pattes ❌
- Oiseaux volants → pas de cames d'ailes ❌

## RÉÉCRITURE
- scene_builder.py v2: 753 lignes, utilise living_beings_db en priorité
- 17 templates spécialisés:
  - _build_quadruped (4 pattes, phases gait)
  - _build_biped (2 jambes ± bras)
  - _build_flapper (ailes battantes: oiseaux, chauve-souris, phénix)
  - _build_snake (3 segments ondulants)
  - _build_swimmer (poisson/dauphin: queue + nageoires)
  - _build_insect_6leg (tripod gait: L1+R2+L3 vs R1+L2+R3)
  - _build_insect_flying (ailes insecte)
  - _build_arachnid (8 pattes alternées tetrapod)
  - _build_scorpion (8 pattes + queue articulée + pinces)
  - _build_crab (carapace large + marche latérale + pinces)
  - _build_lobster (corps allongé + pattes + pinces + queue)
  - _build_myriapod (4 segments ondulants)
  - _build_octopus (manteau + 8 tentacules)
  - _build_snail (coquille + corps + tentacules)
  - _build_plant (tige + fleur oscillante)
  - _build_dino_biped (T-Rex: grosses pattes + petits bras + mâchoire)
  - _build_dragon (4 pattes + 2 ailes + mâchoire + queue)
- Rétrocompat: 6 wrappers _wrap_old_* pour animal_db

## BUGS TROUVÉS ET FIXÉS
1. beta incohérent avec frequency_multiplier:
   - freq=2 → beta doit être 180 (pas 360)
   - freq=3 → beta total doit être 120 (pas 360)
   - Corrigé pour: pedicel, claw_L/R, tent_L/R, jaw_j
2. FigurineProportions (ancien) n'a pas total_height:
   - Fix: getattr(fig, "total_height", fig.body_h + fig.leg_l)

## FAUX POSITIFS E2E (non-bugs)
- INS_VOL (abeille): 6 pattes physiques mais seules les ailes animées (design correct pour automate)
- MOL_PIEUVRE: 8 tentacules nommés tent_*, pas hip_* (naming correct)

## RÉSULTATS FINAUX
- scene_builder tests: 49/49 ✅
- living_beings_db tests: 20/20 ✅
- Rétrocompat animal_db: 33/33 ✅
- E2E engine: 42/42 body plans génèrent des meshes 3D ✅
