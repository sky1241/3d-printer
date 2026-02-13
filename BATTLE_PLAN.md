# 🎯 PLAN DE BATAILLE — Module Figurine Articulée
# Brique par brique, batterie de tests à chaque étape
# Date: 13 février 2026

# ══════════════════════════════════════════════════════════════
# PRINCIPE: Chaque étape est ISOLÉE et TESTABLE indépendamment
# On ne passe à l'étape N+1 que si N est 100% vert
# ══════════════════════════════════════════════════════════════

## ÉTAPE 1 — Pin Joint Generator (le plus simple)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**Input**: diamètre, longueur, clearance
**Output**: (axe_mesh, trou_mesh) — 2 trimesh objects

Quoi coder:
  - create_pin_joint(d=3.0, length=8.0, clearance=0.3) → (cylinder, cylinder)
  - L'axe = cylindre plein Ø d
  - Le trou = cylindre Ø (d + 2×clearance) à soustraire de la pièce hôte
  - Ajouter chanfrein 0.3mm sur entrée du trou (imprimabilité)
  - Ajouter collerette anti-sortie (optionnel, pour plus tard)

Tests étape 1:
  ✅ axe watertight
  ✅ trou watertight  
  ✅ axe.bounds OK (diamètre correct ±0.01mm)
  ✅ trou diamètre = axe + 2×clearance
  ✅ axe rentre dans le trou (pas de collision quand centré)
  ✅ axe Ø3, 4, 5, 6 → tous valides
  ✅ Régression: 9/9 presets, 17/17 dynamic toujours verts

Risque: ZÉRO — c'est une fonction isolée, elle touche à rien d'existant


## ÉTAPE 2 — Body Splitter (couper la figurine aux joints)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**Input**: figurine body mesh + joint_position + joint_axis
**Output**: (fixed_part, mobile_part) — 2 meshes coupés au bon endroit

Quoi coder:
  - split_at_joint(body_mesh, cut_point, cut_normal) → (fixed, mobile)
  - Utilise trimesh.intersections.slice_mesh_plane()
  - Ajoute 0.5mm de gap entre les 2 parties (pour clearance rotation)
  - Chaque partie doit être watertight après découpe (cap les faces ouvertes)
  
Tester sur:
  - Sphère (tête) → couper en 2 → 2 demi-sphères watertight
  - Ellipsoïde (corps tortue) → couper au cou → corps + bout de cou
  - Vérifier que volume(fixed) + volume(mobile) ≈ volume(original) - gap

Tests étape 2:
  ✅ fixed_part watertight
  ✅ mobile_part watertight
  ✅ Volumes cohérents (somme ≈ original ±5%)
  ✅ Gap visible entre les 2 parties (0.5mm min)
  ✅ Fonctionne sur sphère, ellipsoïde, cylindre
  ✅ Régression: tout vert

Risque: FAIBLE — fonction isolée, pas d'impact sur l'existant


## ÉTAPE 3 — Intégration Pin Joint dans Body Split
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**Input**: fixed_part + mobile_part + joint_params
**Output**: fixed_part avec trou, mobile_part avec trou, axe séparé

Quoi coder:
  - add_joint_to_parts(fixed, mobile, joint_pos, axis_dir, d=3.0, clearance=0.3)
  - Soustraire le trou de CHAQUE partie (fixed et mobile)
  - Créer l'axe comme pièce séparée
  - L'axe traverse les 2 parties
  - Vérifier que l'axe est aligné avec l'axe de rotation du joint

Tester sur:
  - Tortue: couper tête au cou, ajouter pin joint
  - Vérifier: tête peut pivoter autour de l'axe sans collision

Tests étape 3:
  ✅ Trou dans fixed: watertight après boolean subtract
  ✅ Trou dans mobile: watertight après boolean subtract  
  ✅ Axe passe à travers les 2 trous
  ✅ Mobile peut pivoter ±30° sans collision avec fixed
  ✅ Pas de collision axe/parois à amplitude max
  ✅ Régression: tout vert

Risque: MOYEN — les boolean CSG sur mesh peuvent être instables
Mitigation: fallback si boolean fail, log warning


## ÉTAPE 4 — Pushrod Attachment Point
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**Input**: joint_position + lever_arm_length + pushrod_direction
**Output**: (attachment_point, socket_mesh) sur la partie mobile

Quoi coder:
  - calculate_pushrod_attach(joint_pos, arm_R=16.0, direction='down')
  - Le point d'attache est à distance R du pivot, dans la direction du pushrod
  - Créer un socket (trou Ø pushrod + clearance) dans la partie mobile
  - Le pushrod s'insère dans ce socket avec jeu 0.3mm

Formule:
  - attach_point = joint_pos + R × direction_perpendiculaire_à_axe
  - θ_max = asin(pushrod_travel / R) — on vérifie que c'est dans les limites

Tests étape 4:
  ✅ Point d'attache à distance R du pivot (±0.1mm)
  ✅ θ_max calculé correctement (asin(8/16) = 30°)
  ✅ Socket watertight dans la partie mobile
  ✅ Pushrod rentre dans le socket
  ✅ Régression: tout vert

Risque: FAIBLE — calculs géométriques purs


## ÉTAPE 5 — Pushrod Router (levier → joint)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**Input**: lever_tip_position + attachment_point + obstacles
**Output**: pushrod_mesh (cylindre droit ou coudé)

Quoi coder:
  - route_pushrod(start, end, diameter=3.0, obstacles=[])
  - Cas simple: ligne droite (cylindre de start à end)
  - Cas complexe: si intersection avec obstacle → coude à 1 point
  - Vérifier pas de collision pushrod ↔ chassis/walls

Tests étape 5:
  ✅ Pushrod watertight
  ✅ Pushrod de bonne longueur (distance start→end ±1mm)
  ✅ Pushrod Ø correct
  ✅ Pas de collision avec chassis (si obstacle fourni)
  ✅ Cas droit + cas coudé testés
  ✅ Régression: tout vert

Risque: MOYEN — collision detection peut être lente sur gros meshes


## ÉTAPE 6 — Assemblage Complet Tortue Simple (1 joint)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**Input**: turtle_simple preset
**Output**: mécanisme + figurine avec tête articulée

Quoi coder:
  - Brancher étapes 1-5 dans le generate() pipeline
  - UNIQUEMENT pour turtle_simple (1 seul joint = cou)
  - Workflow:
    1. FigurineBuilder crée le body (carapace + tête)
    2. Body splitter coupe au cou
    3. Pin joint ajoute axe + trous
    4. Pushrod router connecte lever_neck → tête
    5. Carapace = fixed au châssis
    6. Tête = mobile, pivote sur axe du cou

Tests étape 6:
  ✅ Toutes les pièces watertight
  ✅ Tête peut pivoter ±30° sans collision
  ✅ Pushrod connecté au bon endroit
  ✅ Carapace fixe (pas de mouvement)
  ✅ 0 collisions entre pièces fixes
  ✅ Rendu visuel correct (4 vues)
  ✅ Export STL OK
  ✅ Régression: 9/9 presets, 17/17 dynamic, 13/13 debug

Risque: ÉLEVÉ — première intégration, beaucoup de pièces en jeu
Mitigation: if-guard sur _figurine_cfg, fallback vers ancien mode si échec


## ÉTAPE 7 — Turtle Walking (6 joints)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**Input**: turtle_walking preset  
**Output**: mécanisme + figurine avec tête + 4 pattes + queue articulées

Quoi coder:
  - Étendre étape 6 à multiple joints
  - Chaque patte = split + pin joint + pushrod
  - Queue = split + pin joint + pushrod
  - Gait timing: diagonales en phase (déjà codé dans les cames)

Tests étape 7:
  ✅ 6 articulations fonctionnelles
  ✅ Chaque patte pivote ±20°
  ✅ Queue pivote ±15°
  ✅ Tête pivote ±30°  
  ✅ Pas de collision entre pattes adjacentes
  ✅ 0 collision fixed-to-fixed
  ✅ Régression: tout vert

Risque: ÉLEVÉ — 6× plus de geometry + collisions
Mitigation: implémenter 1 patte d'abord, valider, puis les 3 autres


## ÉTAPE 8 — Généralisation Body Plans
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**Input**: BODY_PLAN_JOINTS table (RESEARCH_ARTICULATED.py)
**Output**: n'importe quel body plan → figurine articulée

Quoi coder:
  - ArticulatedFigurineBuilder qui lit BODY_PLAN_JOINTS[body_type]
  - Pour chaque joint dans le template → split + pin + pushrod
  - Mapper automatiquement les cames du mécanisme aux joints
  - Gérer les cas spéciaux (flexure, living hinge)

Tests étape 8:
  ✅ Les 12 body plans génèrent sans crash
  ✅ Toutes les pièces watertight
  ✅ 17/17 espèces dynamiques passent
  ✅ Nouveaux constraint checks pour articulations

Risque: TRÈS ÉLEVÉ — c'est le boss final
Mitigation: faire 1 body plan à la fois, en commençant par les plus simples


## ÉTAPE 9 — Constraint Engine Update
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**Input**: assemblage articulé
**Output**: nouveau bloc B10 de contraintes

Nouveaux checks:
  - JOINT_PIN_TOO_THIN: d_axe < 3mm
  - JOINT_CLEARANCE_TIGHT: clearance < 0.1mm
  - JOINT_CLEARANCE_LOOSE: clearance > 0.5mm
  - JOINT_AMPLITUDE_EXCEEDED: θ > θ_max pour le type
  - PUSHROD_BUCKLING: d < seuil Euler pour F et L donnés
  - PUSHROD_COLLISION: pushrod intersecte une pièce fixe
  - MOBILE_COLLISION_AT_MAX: pièce mobile touche fixed à amplitude max
  - LIVING_HINGE_TOO_THIN: < 0.4mm
  - LIVING_HINGE_CYCLES: PLA > 20 cycles warning

Tests étape 9:
  ✅ Chaque check déclenche correctement sur cas pathologique
  ✅ Chaque check passe sur cas nominal
  ✅ Intégré dans full_constraint_audit
  ✅ Régression: tout vert


# ══════════════════════════════════════════════════════════════
# RÉSUMÉ: 9 étapes, ~2-3 sessions de travail
# ══════════════════════════════════════════════════════════════
#
# Étape 1: Pin Joint         → ISOLÉ, risque zéro      ⏱ 15min
# Étape 2: Body Splitter     → ISOLÉ, risque faible     ⏱ 30min
# Étape 3: Joint + Split     → COMBINÉ, risque moyen    ⏱ 30min
# Étape 4: Pushrod Attach    → ISOLÉ, risque faible     ⏱ 15min
# Étape 5: Pushrod Router    → ISOLÉ, risque moyen      ⏱ 30min
# Étape 6: Turtle Simple     → INTÉGRATION, risque élevé⏱ 1h
# Étape 7: Turtle Walking    → EXTENSION, risque élevé  ⏱ 1h
# Étape 8: Tous Body Plans   → BOSS FINAL, risque max   ⏱ 2h
# Étape 9: Constraints       → VALIDATION, risque moyen ⏱ 1h
#
# Total estimé: ~7h de travail réparti sur 2-3 sessions
# ══════════════════════════════════════════════════════════════
