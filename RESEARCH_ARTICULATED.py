# 📐 RESEARCH DATA — Figurines Articulées FDM PLA
# Source: ChatGPT extraction, 13 février 2026
# Usage: Constantes et formules pour le module ArticulatedFigurine

# ══════════════════════════════════════════════════════════════
# 1. CLEARANCES FDM (PLA, nozzle 0.4mm, layer 0.2mm)
# ══════════════════════════════════════════════════════════════

# Format: (nominal_mm, serré_mm, sûr_mm)
PIN_CLEARANCES = {
    # Axe Ø → clearance radiale (par côté)
    # Trou = Ø_axe + 2×clearance
    3.0: {'radial': (0.15, 0.05, 0.25), 'axial': (0.10, 0.05, 0.20)},  # trou 3.3mm
    4.0: {'radial': (0.15, 0.05, 0.25), 'axial': (0.10, 0.05, 0.20)},  # trou 4.3mm
    5.0: {'radial': (0.15, 0.05, 0.25), 'axial': (0.10, 0.05, 0.20)},  # trou 5.3mm
    6.0: {'radial': (0.15, 0.05, 0.25), 'axial': (0.10, 0.05, 0.20)},  # trou 6.3mm
}

PRESS_FIT_INTERFERENCE = {
    # Axe Ø → interférence radiale (négatif = serré)
    'nominal': -0.05,  # mm
    'tight':   -0.10,
    'safe':     0.00,
    'max_depth': 2.0,  # mm max d'enfoncement
}

BALL_JOINT_CLEARANCES = {
    # Bille Ø → (clearance_radiale, offset_axial)
    6.0:  {'radial': (0.05, 0.02, 0.10), 'offset': 0.6},   # socket 6.1mm
    8.0:  {'radial': (0.05, 0.02, 0.10), 'offset': 0.8},   # socket 8.1mm
    10.0: {'radial': (0.05, 0.02, 0.10), 'offset': 1.0},   # socket 10.1mm
}

SNAP_FIT = {
    'clearance_fente': (0.3, 0.2, 0.5),  # mm (nom/serré/sûr)
    'epaisseur_languette': 1.2,            # mm (~3× nozzle 0.4)
    'angle_insertion': (30, 45),           # degrés
}

LIVING_HINGE = {
    'epaisseur_min': 0.4,    # mm (2 couches à 0.2mm)
    'epaisseur_max': 0.6,    # mm
    'largeur_min': 5.0,      # mm
    'cycles_pla': 20,        # cycles avant rupture (~)
    'amplitude_max': 90,     # degrés (PLA, au-delà ça casse)
}

DOVETAIL = {
    'clearance': (0.2, 0.1, 0.3),  # mm (nom/serré/sûr)
    'angle': 45,                     # degrés
}

PRINT_IN_PLACE = {
    'clearance_xy': (0.3, 0.2, 0.5),  # mm
    'clearance_z': 0.15,                # mm (1 layer minimum)
}


# ══════════════════════════════════════════════════════════════
# 2. PROPRIÉTÉS MATÉRIAUX
# ══════════════════════════════════════════════════════════════

MATERIALS = {
    'PLA': {
        'young_modulus_GPa': 2.3,
        'yield_MPa': 36,
        'elongation_pct': 4,
        'friction_self': 0.35,       # PLA/PLA statique
        'friction_petg': 0.30,       # PLA/PETG
        'living_hinge_min_mm': 0.4,
        'softening_C': 57,           # °C
        'creep': 'élevé à T>30°C',
    },
    'PETG': {
        'young_modulus_GPa': 1.9,
        'yield_MPa': 46,
        'elongation_pct': 6.5,
        'living_hinge_min_mm': 0.4,
        'softening_C': 82,
    },
    'TPU_95A': {
        'young_modulus_GPa': 0.06,
        'yield_MPa': 24,
        'elongation_pct': 500,
        'softening_C': 45,
    },
}


# ══════════════════════════════════════════════════════════════
# 3. MOUVEMENT → ARTICULATION (table de correspondance)
# ══════════════════════════════════════════════════════════════

# Format: mouvement → (partie, axe, type_joint, amplitude_deg, force_pushrod_N)
MOTION_TO_JOINT = {
    'nod':          {'part': 'head',     'axis': 'X', 'joint': 'pin',       'amplitude': (20, 30),  'force_N': (1, 2)},
    'pan':          {'part': 'head',     'axis': 'Z', 'joint': 'pin',       'amplitude': (30, 45),  'force_N': (0.5, 1)},
    'jaw_open':     {'part': 'jaw',      'axis': 'X', 'joint': 'living',    'amplitude': (30, 45),  'force_N': (1, 2)},
    'flap':         {'part': 'wing',     'axis': 'Y', 'joint': 'pin',       'amplitude': (25, 35),  'force_N': (2, 3)},
    'walk_lift':    {'part': 'leg',      'axis': 'X', 'joint': 'pin',       'amplitude': (15, 20),  'force_N': (2, 4)},
    'walk_slide':   {'part': 'leg',      'axis': 'Y', 'joint': 'dovetail',  'amplitude': (10, 20),  'force_N': (1, 2)},  # mm not degrees
    'tail_updown':  {'part': 'tail',     'axis': 'X', 'joint': 'pin',       'amplitude': (15, 20),  'force_N': (0.5, 1)},
    'tail_lr':      {'part': 'tail',     'axis': 'Z', 'joint': 'pin',       'amplitude': (20, 30),  'force_N': (0.5, 1)},
    'swim':         {'part': 'body',     'axis': 'alt','joint': 'flexure',   'amplitude': (15, 20),  'force_N': (1, 2)},
    'eye_roll':     {'part': 'eye',      'axis': 'X', 'joint': 'pin',       'amplitude': (10, 15),  'force_N': (0.2, 0.5)},
    'arm_lift':     {'part': 'arm',      'axis': 'X', 'joint': 'pin',       'amplitude': (30, 45),  'force_N': (2, 3)},
    'pinch':        {'part': 'claw',     'axis': 'Z', 'joint': 'pin',       'amplitude': (15, 20),  'force_N': (0.5, 1)},
}


# ══════════════════════════════════════════════════════════════
# 4. FORMULES CINÉMATIQUES
# ══════════════════════════════════════════════════════════════

# θ_sortie = asin(Δ_pushrod / R_bras)
#   Δ_pushrod = amplitude linéaire du pushrod (mm)
#   R_bras = longueur du bras de levier au joint (mm)
#   θ_sortie = amplitude angulaire (rad)

# Pour bell-crank (conversion 90°):
#   Δ_horizontal = (V_arm / H_arm) × Δ_vertical
#   V_arm = bras vertical, H_arm = bras horizontal

# Pour amplification:
#   Δ_sortie = (R2/R1) × Δ_entrée
#   R1 = petit bras (côté pushrod), R2 = grand bras (côté figurine)

# Diamètre axe minimum:
#   d ≥ sqrt(4 × M × g × L / (π × σ_yield))
#   M = masse partie mobile (kg), L = bras de levier (m)

# Flambage pushrod (Euler):
#   d ≥ sqrt(4 × F × l² / (π² × E × I))
#   avec I = π×d⁴/64 → d ≥ (64×F×l² / (π³×E))^(1/4)

# Force minimale pushrod:
#   F = M×g×sin(θ) + μ×M×g×cos(θ)
#   μ = coefficient friction PLA/PLA ≈ 0.35


# ══════════════════════════════════════════════════════════════
# 5. PUSHROD ROUTING CONFIGS
# ══════════════════════════════════════════════════════════════

PUSHROD_CONFIGS = {
    'direct_pivot': {
        'description': 'Pushrod droit → pivot simple (vertical → rotation pitch)',
        'formula': 'θ = asin(Δh / R)',
        'amplification': 1.0,
        'pieces': 3,  # pushrod + levier + axe pivot
    },
    'bell_crank': {
        'description': 'Pushrod + bell-crank 90° (vertical → horizontal)',
        'formula': 'Δ_out = (V_arm/H_arm) × Δh',
        'amplification': 'variable (V/H ratio)',
        'pieces': 4,  # pushrod + bell-crank + 2 axes
    },
    'lever_amplified': {
        'description': 'Levier déporté (petit bras → grand bras)',
        'formula': 'Δ_out = (R2/R1) × Δh',
        'amplification': 'R2/R1 (ex: 3×)',
        'pieces': 3,  # pushrod + levier + axe
    },
    'y_split': {
        'description': '1 pushrod → 2 sorties synchronisées',
        'formula': 'chaque sortie = formule du type choisi',
        'amplification': 1.0,
        'pieces': 5,  # Y-splitter + 2 pushrods + 2 mécanismes
    },
    'parallelogram': {
        'description': '4 barres → translation pure (vertical → vertical décalé)',
        'formula': 'ΔY_out = ΔY_in (1:1)',
        'amplification': 1.0,
        'pieces': 6,  # 4 barres + 2 pivots + pushrod
    },
}


# ══════════════════════════════════════════════════════════════
# 6. BODY PLAN ARTICULATION TEMPLATES
# ══════════════════════════════════════════════════════════════

BODY_PLAN_JOINTS = {
    'turtle': {
        'fixed': ['shell'],
        'mobile': ['head', 'leg_fl', 'leg_fr', 'leg_rl', 'leg_rr', 'tail'],
        'joints': {
            'neck':     {'type': 'pin', 'axis': 'X', 'diameter': 3.0, 'motion': 'nod',       'amplitude': 30},
            'hip_fl':   {'type': 'pin', 'axis': 'X', 'diameter': 3.0, 'motion': 'walk_lift', 'amplitude': 20},
            'hip_fr':   {'type': 'pin', 'axis': 'X', 'diameter': 3.0, 'motion': 'walk_lift', 'amplitude': 20},
            'hip_rl':   {'type': 'pin', 'axis': 'X', 'diameter': 3.0, 'motion': 'walk_lift', 'amplitude': 20},
            'hip_rr':   {'type': 'pin', 'axis': 'X', 'diameter': 3.0, 'motion': 'walk_lift', 'amplitude': 20},
            'tail':     {'type': 'pin', 'axis': 'X', 'diameter': 3.0, 'motion': 'tail_updown','amplitude': 15},
        },
        'cams_min': 3, 'cams_max': 6,
        'pushrod_arm_mm': 16.0,
    },
    'bird_standing': {
        'fixed': ['body'],
        'mobile': ['head', 'wing_l', 'wing_r', 'tail', 'leg_l', 'leg_r'],
        'joints': {
            'neck':     {'type': 'pin', 'axis': 'X', 'diameter': 3.0, 'motion': 'nod',  'amplitude': 30},
            'wing_l':   {'type': 'pin', 'axis': 'Y', 'diameter': 4.0, 'motion': 'flap', 'amplitude': 35},
            'wing_r':   {'type': 'pin', 'axis': 'Y', 'diameter': 4.0, 'motion': 'flap', 'amplitude': 35},
            'tail':     {'type': 'pin', 'axis': 'X', 'diameter': 3.0, 'motion': 'tail_updown', 'amplitude': 15},
        },
        'cams_min': 3, 'cams_max': 5,
    },
    'bird_flying': {
        'fixed': ['body'],
        'mobile': ['head', 'wing_l', 'wing_r'],
        'joints': {
            'neck':     {'type': 'pin', 'axis': 'Z', 'diameter': 3.0, 'motion': 'pan',  'amplitude': 30},
            'wing_l':   {'type': 'pin', 'axis': 'Y', 'diameter': 4.0, 'motion': 'flap', 'amplitude': 35},
            'wing_r':   {'type': 'pin', 'axis': 'Y', 'diameter': 4.0, 'motion': 'flap', 'amplitude': 35},
        },
        'cams_min': 2, 'cams_max': 3,
    },
    'biped': {
        'fixed': ['torso'],
        'mobile': ['head', 'arm_l', 'arm_r', 'leg_l', 'leg_r'],
        'joints': {
            'neck':      {'type': 'pin', 'axis': 'X', 'diameter': 3.0, 'motion': 'nod',      'amplitude': 25},
            'shoulder_l':{'type': 'pin', 'axis': 'X', 'diameter': 4.0, 'motion': 'arm_lift', 'amplitude': 45},
            'shoulder_r':{'type': 'pin', 'axis': 'X', 'diameter': 4.0, 'motion': 'arm_lift', 'amplitude': 45},
            'hip_l':     {'type': 'pin', 'axis': 'X', 'diameter': 4.0, 'motion': 'walk_lift','amplitude': 20},
            'hip_r':     {'type': 'pin', 'axis': 'X', 'diameter': 4.0, 'motion': 'walk_lift','amplitude': 20},
        },
        'cams_min': 3, 'cams_max': 7,
    },
    'quadruped': {
        'fixed': ['body'],
        'mobile': ['head', 'leg_fl', 'leg_fr', 'leg_rl', 'leg_rr', 'tail'],
        'joints': {
            'neck':     {'type': 'pin', 'axis': 'X', 'diameter': 3.0, 'motion': 'nod',       'amplitude': 25},
            'hip_fl':   {'type': 'pin', 'axis': 'X', 'diameter': 4.0, 'motion': 'walk_lift', 'amplitude': 20},
            'hip_fr':   {'type': 'pin', 'axis': 'X', 'diameter': 4.0, 'motion': 'walk_lift', 'amplitude': 20},
            'hip_rl':   {'type': 'pin', 'axis': 'X', 'diameter': 4.0, 'motion': 'walk_lift', 'amplitude': 20},
            'hip_rr':   {'type': 'pin', 'axis': 'X', 'diameter': 4.0, 'motion': 'walk_lift', 'amplitude': 20},
            'tail':     {'type': 'pin', 'axis': 'X', 'diameter': 3.0, 'motion': 'tail_updown','amplitude': 20},
        },
        'cams_min': 4, 'cams_max': 10,
    },
    'fish': {
        'fixed': ['body_front'],
        'mobile': ['tail', 'jaw', 'fin_l', 'fin_r'],
        'joints': {
            'tail':  {'type': 'flexure', 'axis': 'Z', 'diameter': None, 'motion': 'swim', 'amplitude': 20},
            'jaw':   {'type': 'living',  'axis': 'X', 'diameter': None, 'motion': 'jaw_open', 'amplitude': 30},
            'fin_l': {'type': 'pin',     'axis': 'Y', 'diameter': 3.0,  'motion': 'flap', 'amplitude': 20},
            'fin_r': {'type': 'pin',     'axis': 'Y', 'diameter': 3.0,  'motion': 'flap', 'amplitude': 20},
        },
        'cams_min': 1, 'cams_max': 3,
    },
    'arthropod_6': {
        'fixed': ['body'],
        'mobile': ['head', 'leg_l1', 'leg_r1', 'leg_l2', 'leg_r2', 'leg_l3', 'leg_r3', 'mandible_l', 'mandible_r', 'antenna_l', 'antenna_r'],
        'joints': {
            'neck':       {'type': 'pin', 'axis': 'X', 'diameter': 3.0, 'motion': 'nod', 'amplitude': 15},
            'hip_l1':     {'type': 'pin', 'axis': 'X', 'diameter': 3.0, 'motion': 'walk_lift', 'amplitude': 20},
            'hip_r1':     {'type': 'pin', 'axis': 'X', 'diameter': 3.0, 'motion': 'walk_lift', 'amplitude': 20},
            'hip_l2':     {'type': 'pin', 'axis': 'X', 'diameter': 3.0, 'motion': 'walk_lift', 'amplitude': 20},
            'hip_r2':     {'type': 'pin', 'axis': 'X', 'diameter': 3.0, 'motion': 'walk_lift', 'amplitude': 20},
            'hip_l3':     {'type': 'pin', 'axis': 'X', 'diameter': 3.0, 'motion': 'walk_lift', 'amplitude': 20},
            'hip_r3':     {'type': 'pin', 'axis': 'X', 'diameter': 3.0, 'motion': 'walk_lift', 'amplitude': 20},
            'mandible_l': {'type': 'pin', 'axis': 'Z', 'diameter': 2.0, 'motion': 'pinch', 'amplitude': 20},
            'mandible_r': {'type': 'pin', 'axis': 'Z', 'diameter': 2.0, 'motion': 'pinch', 'amplitude': 20},
        },
        'cams_min': 3, 'cams_max': 7,
    },
    'spider': {
        'fixed': ['body'],
        'mobile': ['leg_l1','leg_r1','leg_l2','leg_r2','leg_l3','leg_r3','leg_l4','leg_r4'],
        'joints': {k: {'type': 'pin', 'axis': 'X', 'diameter': 3.0, 'motion': 'walk_lift', 'amplitude': 20}
                   for k in ['hip_l1','hip_r1','hip_l2','hip_r2','hip_l3','hip_r3','hip_l4','hip_r4']},
        'cams_min': 4, 'cams_max': 8,
    },
    'crustacean': {
        'fixed': ['carapace'],
        'mobile': ['claw_l', 'claw_r', 'leg_l1', 'leg_r1', 'leg_l2', 'leg_r2', 'leg_l3', 'leg_r3', 'leg_l4', 'leg_r4', 'antenna_l', 'antenna_r'],
        'joints': {
            'claw_l':  {'type': 'pin', 'axis': 'Z', 'diameter': 4.0, 'motion': 'pinch', 'amplitude': 25},
            'claw_r':  {'type': 'pin', 'axis': 'Z', 'diameter': 4.0, 'motion': 'pinch', 'amplitude': 25},
            **{k: {'type': 'pin', 'axis': 'X', 'diameter': 3.0, 'motion': 'walk_lift', 'amplitude': 20}
               for k in ['hip_l1','hip_r1','hip_l2','hip_r2','hip_l3','hip_r3','hip_l4','hip_r4']},
        },
        'cams_min': 4, 'cams_max': 12,
    },
    'cephalopod': {
        'fixed': ['mantle'],
        'mobile': ['tentacle_1','tentacle_2','tentacle_3','tentacle_4','tentacle_5','tentacle_6','tentacle_7','tentacle_8'],
        'joints': {k: {'type': 'flexure', 'axis': 'alt', 'diameter': None, 'motion': 'swim', 'amplitude': 20}
                   for k in [f'tent_{i}' for i in range(8)]},
        'cams_min': 1, 'cams_max': 4,
    },
    'gastropod': {
        'fixed': ['shell'],
        'mobile': ['head', 'horn_l', 'horn_r', 'foot'],
        'joints': {
            'neck':   {'type': 'dovetail', 'axis': 'Y', 'diameter': None, 'motion': 'walk_slide', 'amplitude': 10},
            'horn_l': {'type': 'pin',      'axis': 'X', 'diameter': 2.0,  'motion': 'nod', 'amplitude': 15},
            'horn_r': {'type': 'pin',      'axis': 'X', 'diameter': 2.0,  'motion': 'nod', 'amplitude': 15},
        },
        'cams_min': 1, 'cams_max': 2,
    },
    'dragon': {
        'fixed': ['body'],
        'mobile': ['head', 'jaw', 'wing_l', 'wing_r', 'leg_fl', 'leg_fr', 'leg_rl', 'leg_rr', 'tail'],
        'joints': {
            'neck':     {'type': 'pin', 'axis': 'X', 'diameter': 4.0, 'motion': 'nod',       'amplitude': 25},
            'jaw':      {'type': 'living', 'axis': 'X', 'diameter': None, 'motion': 'jaw_open', 'amplitude': 35},
            'wing_l':   {'type': 'pin', 'axis': 'Y', 'diameter': 5.0, 'motion': 'flap',      'amplitude': 35},
            'wing_r':   {'type': 'pin', 'axis': 'Y', 'diameter': 5.0, 'motion': 'flap',      'amplitude': 35},
            'hip_fl':   {'type': 'pin', 'axis': 'X', 'diameter': 4.0, 'motion': 'walk_lift', 'amplitude': 20},
            'hip_fr':   {'type': 'pin', 'axis': 'X', 'diameter': 4.0, 'motion': 'walk_lift', 'amplitude': 20},
            'hip_rl':   {'type': 'pin', 'axis': 'X', 'diameter': 4.0, 'motion': 'walk_lift', 'amplitude': 20},
            'hip_rr':   {'type': 'pin', 'axis': 'X', 'diameter': 4.0, 'motion': 'walk_lift', 'amplitude': 20},
            'tail':     {'type': 'pin', 'axis': 'X', 'diameter': 3.0, 'motion': 'tail_updown','amplitude': 20},
        },
        'cams_min': 5, 'cams_max': 10,
    },
}


# ══════════════════════════════════════════════════════════════
# 7. EXEMPLES COTÉS (dimensions en mm)
# ══════════════════════════════════════════════════════════════

EXAMPLE_TURTLE_NOD = {
    'description': 'Tortue hochant la tête, 1 came',
    'pivot_diameter': 3.0,
    'hole_diameter': 3.3,
    'clearance': 0.3,
    'lever_arm_R': 16.0,
    'pushrod_travel': 8.0,
    'pushrod_diameter': 5.0,
    'pushrod_length': 60.0,
    'neck_height': 50.0,
    'angle_output_deg': 30.0,  # asin(8/16)
}

EXAMPLE_BIRD_FLAP = {
    'description': 'Oiseau battant des ailes, 2 cames',
    'pivot_diameter': 4.0,
    'hole_diameter': 4.3,
    'clearance': 0.3,
    'lever_arm_R': 20.0,
    'pushrod_travel': 12.0,
    'pushrod_diameter': 5.0,
    'angle_output_deg': 35.0,  # asin(12/20) ≈ 37°
}

EXAMPLE_CAT_WALK = {
    'description': 'Chat marchant, 4 cames',
    'pivot_diameter': 4.0,
    'hole_diameter': 4.3,
    'clearance': 0.3,  # trou = 4.3mm (0.15mm radial par côté)
    'lever_arm_R': 15.0,
    'pushrod_travel': 4.0,
    'pushrod_diameter': 5.0,
    'angle_output_deg': 15.0,  # asin(4/15) ≈ 15.5°
    'gait': 'diagonal',  # FL+RR en phase, FR+RL 180°
}


# ══════════════════════════════════════════════════════════════
# 8. ANTI-PATTERNS (pour le constraint engine)
# ══════════════════════════════════════════════════════════════

ANTI_PATTERNS = [
    {'id': 'AP01', 'name': 'Axe vertical fragile',     'fix': 'Imprimer axe horizontal (layers ⊥ cisaillement)'},
    {'id': 'AP02', 'name': 'Surextrusion print-in-place','fix': 'Clearance min 0.3mm XY, calibrer flow'},
    {'id': 'AP03', 'name': 'Axe sous-dimensionné',      'fix': 'd_min ≥ 3mm, congé pied 0.5mm'},
    {'id': 'AP04', 'name': 'Living hinge cassante',      'fix': '≥0.4mm épaisseur, fillets base, PLA ≤20 cycles'},
    {'id': 'AP05', 'name': 'Ball joint impossible',      'fix': 'Clearance 0.1mm, offset 10% du Ø'},
    {'id': 'AP06', 'name': 'Pushrod flambage',           'fix': 'd ≥ 5mm pour L=100mm, F=10N (Euler)'},
    {'id': 'AP07', 'name': 'Friction excessive',         'fix': 'Jeu min 0.1-0.2mm, silicone sec si besoin'},
    {'id': 'AP08', 'name': 'Jeu excessif',              'fix': 'Réduire clearance, calibration imprimante'},
    {'id': 'AP09', 'name': 'Porte-à-faux non supporté', 'fix': 'Support ou réorienter pièce'},
    {'id': 'AP10', 'name': 'Bridge sur trou déformé',   'fix': 'Imprimer trou horizontal, ou post-percer'},
]
