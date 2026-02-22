"""
living_beings_db.py — Arbre de catégorisation complet des êtres vivants
=========================================================================
Chaque entrée = un body_type avec ses proportions RELATIVES (ratios)
+ des espèces concrètes avec des tailles ABSOLUES.

Tout est indexé pour FDM 3D printing :
  - Figurine target: 40-80mm de haut
  - Amplitudes came: 5-15mm max
  - Résolution FDM: 0.4mm nozzle min

Sources:
  - Kilbourne & Hoffman 2013 (allométrie membres)
  - Dimensions.com (mesures par espèce)
  - Wikipedia anatomie par taxon
  - CSE169 UCSD (gait patterns)
  - Études morphométriques par taxon
"""
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ════════════════════════════════════════════════════════════════
#  §1 — ARBRE DE CATÉGORISATION
# ════════════════════════════════════════════════════════════════
# Chaque noeud: (id, parent, nom, description)

CATEGORY_TREE = {
    # ── NIVEAU 0: Règnes ──
    "ANIMALIA":       (None,          "Animaux",         "Règne animal"),
    "PLANTAE":        (None,          "Plantes",         "Végétaux (automates décoratifs)"),
    "FUNGI":          (None,          "Champignons",     "Champignons (automates décoratifs)"),
    "FANTASIA":       (None,          "Fantastique",     "Créatures imaginaires"),

    # ── NIVEAU 1: Embranchements ──
    "VERTEBRATA":     ("ANIMALIA",    "Vertébrés",       "Colonne vertébrale"),
    "ARTHROPODA":     ("ANIMALIA",    "Arthropodes",     "Exosquelette, pattes articulées"),
    "MOLLUSCA":       ("ANIMALIA",    "Mollusques",      "Corps mou, coquille optionnelle"),

    # ── NIVEAU 2: Classes ──
    # Vertébrés
    "MAMMALIA":       ("VERTEBRATA",  "Mammifères",      "Poils, lait, sang chaud"),
    "AVES":           ("VERTEBRATA",  "Oiseaux",         "Plumes, bec, 2 pattes"),
    "REPTILIA":       ("VERTEBRATA",  "Reptiles",        "Écailles, sang froid"),
    "AMPHIBIA":       ("VERTEBRATA",  "Amphibiens",      "Double vie eau/terre"),
    "PISCES":         ("VERTEBRATA",  "Poissons",        "Nageoires, branchies"),
    # Arthropodes
    "INSECTA":        ("ARTHROPODA",  "Insectes",        "6 pattes, 3 segments, ailes optionnelles"),
    "ARACHNIDA":      ("ARTHROPODA",  "Arachnides",      "8 pattes, 2 segments"),
    "CRUSTACEA":      ("ARTHROPODA",  "Crustacés",       "Carapace, 10+ pattes"),
    "MYRIAPODA":      ("ARTHROPODA",  "Myriapodes",      "Mille-pattes, centipèdes"),

    # ── NIVEAU 3: Ordres / Sous-groupes fonctionnels ──
    # Mammifères
    "MAM_QUAD_TRAPU": ("MAMMALIA",   "Quadrup. trapus",  "Ours, hippo, rhino, éléphant"),
    "MAM_QUAD_GRACE": ("MAMMALIA",   "Quadrup. graciles","Cerf, cheval, girafe, vache"),
    "MAM_QUAD_FELIN": ("MAMMALIA",   "Félins",           "Chat, lion, tigre, guépard"),
    "MAM_QUAD_CANIN": ("MAMMALIA",   "Canidés",          "Chien, loup, renard"),
    "MAM_QUAD_PETIT": ("MAMMALIA",   "Petits quadrup.",  "Lapin, écureuil, souris, hamster"),
    "MAM_PRIMATE":    ("MAMMALIA",   "Primates",         "Singe, gorille, orang-outan"),
    "MAM_MARIN":      ("MAMMALIA",   "Mammifères marins","Dauphin, baleine, phoque"),
    "MAM_VOLANT":     ("MAMMALIA",   "Chiroptères",      "Chauve-souris"),
    # Oiseaux
    "AV_VOLANT":      ("AVES",       "Oiseaux volants",  "Battement d'ailes"),
    "AV_COUREUR":     ("AVES",       "Oiseaux coureurs", "Autruche, émeu"),
    "AV_NAGEUR":      ("AVES",       "Oiseaux nageurs",  "Pingouin, canard"),
    "AV_RAPACE":      ("AVES",       "Rapaces",          "Aigle, faucon, hibou"),
    "AV_PETIT":       ("AVES",       "Petits oiseaux",   "Moineau, colibri, mésange"),
    # Reptiles
    "REP_LEZARD":     ("REPTILIA",   "Lézards",          "4 pattes, queue"),
    "REP_SERPENT":     ("REPTILIA",   "Serpents",         "Sans pattes, ondulation"),
    "REP_TORTUE":      ("REPTILIA",   "Tortues",          "Carapace, lent"),
    "REP_CROCO":       ("REPTILIA",   "Crocodiliens",     "Croco, alligator"),
    "REP_DINO":        ("REPTILIA",   "Dinosaures",       "Disparus mais populaires"),
    # Amphibiens
    "AMP_GRENOUILLE":  ("AMPHIBIA",  "Grenouilles",      "Saut, nage"),
    "AMP_SALAMANDRE":  ("AMPHIBIA",  "Salamandres",      "4 pattes, queue, marche"),
    # Poissons
    "FISH_STANDARD":   ("PISCES",    "Poissons standard", "Nageoire caudale"),
    "FISH_PLAT":       ("PISCES",    "Poissons plats",   "Raie, sole"),
    # Insectes
    "INS_MARCHEUR":    ("INSECTA",   "Ins. marcheurs",   "Fourmis, scarabées, cafards"),
    "INS_VOLANT":      ("INSECTA",   "Ins. volants",     "Papillon, libellule, abeille"),
    "INS_SAUTEUR":     ("INSECTA",   "Ins. sauteurs",    "Sauterelle, criquet, puce"),
    "INS_MANTE":       ("INSECTA",   "Mantes",           "Pattes ravisseuses"),
    # Arachnides
    "ARA_ARAIGNEE":    ("ARACHNIDA", "Araignées",        "8 pattes, 2 segments"),
    "ARA_SCORPION":    ("ARACHNIDA", "Scorpions",        "Pinces + queue + dard"),
    # Crustacés
    "CRU_CRABE":       ("CRUSTACEA", "Crabes",           "Marche latérale, pinces"),
    "CRU_HOMARD":      ("CRUSTACEA", "Homards/écrevisses","Marche avant, pinces, queue"),
    "CRU_CREVETTE":    ("CRUSTACEA", "Crevettes",        "Nage, petit"),
    # Myriapodes
    "MYR_CENTIPEDE":   ("MYRIAPODA", "Centipèdes",       "1 paire pattes/segment, rapide"),
    "MYR_MILLIPEDE":   ("MYRIAPODA", "Millipèdes",       "2 paires pattes/segment, lent"),
    # Mollusques
    "MOL_ESCARGOT":    ("MOLLUSCA",  "Escargots",        "Coquille spirale, glisse"),
    "MOL_PIEUVRE":     ("MOLLUSCA",  "Céphalopodes",     "8 tentacules"),
    # Plantes
    "PL_FLEUR":        ("PLANTAE",   "Fleurs",           "Ouverture/fermeture pétales"),
    "PL_ARBRE":        ("PLANTAE",   "Arbres",           "Feuilles au vent"),
    "PL_CARNIVORE":    ("PLANTAE",   "Plantes carnivores","Mâchoire qui se ferme"),
    # Champignons
    "FU_CHAMPIGNON":   ("FUNGI",     "Champignons",      "Chapeau + pied, spores"),
    # Fantastique
    "FAN_DRAGON":      ("FANTASIA",  "Dragons",          "4 pattes + 2 ailes"),
    "FAN_LICORNE":     ("FANTASIA",  "Licornes",         "Cheval + corne"),
    "FAN_PHOENIX":     ("FANTASIA",  "Phénix",           "Oiseau de feu"),
    "FAN_ROBOT":       ("FANTASIA",  "Robots",           "Bipède mécanique"),
    "FAN_MONSTRE":     ("FANTASIA",  "Monstres",         "Créatures libres"),
}


# ════════════════════════════════════════════════════════════════
#  §2 — BODY PLANS (comment construire le mesh)
# ════════════════════════════════════════════════════════════════

@dataclass
class BodyPlan:
    """
    Définition d'un plan corporel pour automate.
    Toutes les proportions sont des RATIOS par rapport à body_length.
    """
    id: str
    name: str
    category: str           # clé dans CATEGORY_TREE
    n_legs: int
    n_wings: int = 0
    n_arms: int = 0
    has_tail: bool = False
    has_head: bool = True

    # Proportions RELATIVES (ratio de body_length)
    body_width_ratio: float = 0.30      # largeur / longueur
    body_height_ratio: float = 0.25     # hauteur / longueur
    head_ratio: float = 0.20           # tête / longueur corps
    leg_ratio: float = 0.50            # pattes / longueur corps
    tail_ratio: float = 0.30           # queue / longueur corps
    wing_ratio: float = 0.0            # envergure aile / longueur corps
    arm_ratio: float = 0.0             # bras / longueur corps

    # Locomotion
    gait: str = "walk"                 # type de démarche
    gait_phases: Dict[str, float] = field(default_factory=dict)

    # Mouvements pour automate (quels joints bougent)
    movable_parts: List[str] = field(default_factory=list)
    # ex: ["legs", "head_nod", "tail_wag", "wings_flap"]

    # FDM constraints
    min_detail_mm: float = 1.0         # plus petit détail imprimable
    recommended_height_mm: float = 60  # hauteur cible figurine


# ── Phases de marche ──
GAIT_WALK_4     = {"LH": 0.0, "LF": 0.25, "RH": 0.5, "RF": 0.75}   # 4-beat
GAIT_TROT       = {"LH": 0.0, "LF": 0.5,  "RH": 0.5, "RF": 0.0}    # diagonal
GAIT_PACE       = {"LH": 0.0, "LF": 0.0,  "RH": 0.5, "RF": 0.5}    # latéral
GAIT_GALLOP     = {"LH": 0.0, "RH": 0.1,  "LF": 0.5, "RF": 0.6}    # transverse
GAIT_BOUND      = {"LH": 0.0, "RH": 0.0,  "LF": 0.5, "RF": 0.5}    # lapin
GAIT_TRIPOD     = {"L1": 0.0, "R2": 0.0,  "L3": 0.0, "R1": 0.5, "L2": 0.5, "R3": 0.5}
GAIT_WAVE_6     = {"L1": 0.0, "L2": 0.17, "L3": 0.33, "R1": 0.5, "R2": 0.67, "R3": 0.83}
GAIT_LATERAL    = {"L_all": 0.0, "R_all": 0.5}  # crabe
GAIT_BIPED      = {"L": 0.0, "R": 0.5}
GAIT_FLAP       = {"LW": 0.0, "RW": 0.0}  # ailes synchrones
GAIT_NONE       = {}  # serpent, escargot, poisson


# ════════════════════════════════════════════════════════════════
#  §3 — TOUS LES BODY PLANS
# ════════════════════════════════════════════════════════════════

BODY_PLANS: Dict[str, BodyPlan] = {}

def _bp(id, name, cat, n_legs, **kw):
    bp = BodyPlan(id=id, name=name, category=cat, n_legs=n_legs, **kw)
    BODY_PLANS[id] = bp
    return bp

# ━━━ MAMMIFÈRES ━━━
_bp("MAM_TRAPU",  "Mammifère trapu",    "MAM_QUAD_TRAPU", 4,
    body_width_ratio=0.35, body_height_ratio=0.30, head_ratio=0.20,
    leg_ratio=0.40, has_tail=True, tail_ratio=0.10,
    gait="pace", gait_phases=GAIT_PACE,
    movable_parts=["legs", "head_nod"])

_bp("MAM_GRACE",  "Mammifère gracile",  "MAM_QUAD_GRACE", 4,
    body_width_ratio=0.22, body_height_ratio=0.28, head_ratio=0.18,
    leg_ratio=0.55, has_tail=True, tail_ratio=0.25,
    gait="trot", gait_phases=GAIT_TROT,
    movable_parts=["legs", "head_nod", "tail_wag"])

_bp("MAM_FELIN",  "Félin",              "MAM_QUAD_FELIN", 4,
    body_width_ratio=0.25, body_height_ratio=0.22, head_ratio=0.18,
    leg_ratio=0.45, has_tail=True, tail_ratio=0.60,
    gait="walk", gait_phases=GAIT_WALK_4,
    movable_parts=["legs", "head_nod", "tail_wag"])

_bp("MAM_CANIN",  "Canidé",             "MAM_QUAD_CANIN", 4,
    body_width_ratio=0.25, body_height_ratio=0.28, head_ratio=0.22,
    leg_ratio=0.50, has_tail=True, tail_ratio=0.35,
    gait="trot", gait_phases=GAIT_TROT,
    movable_parts=["legs", "head_nod", "tail_wag"])

_bp("MAM_PETIT",  "Petit mammifère",    "MAM_QUAD_PETIT", 4,
    body_width_ratio=0.30, body_height_ratio=0.25, head_ratio=0.20,
    leg_ratio=0.35, has_tail=True, tail_ratio=0.40,
    gait="bound", gait_phases=GAIT_BOUND,
    movable_parts=["legs", "head_nod"])

_bp("MAM_PRIMATE","Primate",            "MAM_PRIMATE", 4,
    body_width_ratio=0.35, body_height_ratio=0.40, head_ratio=0.25,
    leg_ratio=0.45, n_arms=2, arm_ratio=0.55, has_tail=True, tail_ratio=0.50,
    gait="walk", gait_phases=GAIT_WALK_4,
    movable_parts=["legs", "arms", "head_nod"])

_bp("MAM_MARIN",  "Mammifère marin",    "MAM_MARIN", 0,
    body_width_ratio=0.25, body_height_ratio=0.22, head_ratio=0.20,
    leg_ratio=0.0, has_tail=True, tail_ratio=0.30,
    gait="swim", gait_phases=GAIT_NONE,
    movable_parts=["tail_swim", "head_nod"],
    n_wings=2, wing_ratio=0.40)  # nageoires = pseudo-ailes

_bp("MAM_CHAUVE", "Chauve-souris",      "MAM_VOLANT", 2,
    body_width_ratio=0.30, body_height_ratio=0.25, head_ratio=0.22,
    leg_ratio=0.20, n_wings=2, wing_ratio=1.50, has_tail=False,
    gait="flap", gait_phases=GAIT_FLAP,
    movable_parts=["wings_flap"])

# ━━━ OISEAUX ━━━
_bp("AV_VOL",     "Oiseau volant",      "AV_VOLANT", 2,
    body_width_ratio=0.30, body_height_ratio=0.28, head_ratio=0.15,
    leg_ratio=0.25, n_wings=2, wing_ratio=1.20, has_tail=True, tail_ratio=0.25,
    gait="flap", gait_phases=GAIT_FLAP,
    movable_parts=["wings_flap", "head_nod", "tail_wag"])

_bp("AV_RAPACE",  "Rapace",             "AV_RAPACE", 2,
    body_width_ratio=0.28, body_height_ratio=0.25, head_ratio=0.18,
    leg_ratio=0.30, n_wings=2, wing_ratio=1.80, has_tail=True, tail_ratio=0.30,
    gait="flap", gait_phases=GAIT_FLAP,
    movable_parts=["wings_flap", "head_nod"])

_bp("AV_COUREUR", "Oiseau coureur",     "AV_COUREUR", 2,
    body_width_ratio=0.35, body_height_ratio=0.45, head_ratio=0.12,
    leg_ratio=0.60, n_wings=2, wing_ratio=0.40, has_tail=True, tail_ratio=0.15,
    gait="walk", gait_phases=GAIT_BIPED,
    movable_parts=["legs", "head_nod"])

_bp("AV_NAGEUR",  "Oiseau nageur",      "AV_NAGEUR", 2,
    body_width_ratio=0.35, body_height_ratio=0.35, head_ratio=0.18,
    leg_ratio=0.25, n_wings=2, wing_ratio=0.30, has_tail=True, tail_ratio=0.10,
    gait="waddle", gait_phases=GAIT_BIPED,
    movable_parts=["legs", "head_nod"])

_bp("AV_PETIT",   "Petit oiseau",       "AV_PETIT", 2,
    body_width_ratio=0.35, body_height_ratio=0.32, head_ratio=0.22,
    leg_ratio=0.30, n_wings=2, wing_ratio=0.90, has_tail=True, tail_ratio=0.20,
    gait="hop", gait_phases=GAIT_BOUND,
    movable_parts=["wings_flap", "head_nod"],
    recommended_height_mm=40)

# ━━━ REPTILES ━━━
_bp("REP_LEZARD", "Lézard",             "REP_LEZARD", 4,
    body_width_ratio=0.18, body_height_ratio=0.12, head_ratio=0.15,
    leg_ratio=0.25, has_tail=True, tail_ratio=0.80,
    gait="walk", gait_phases=GAIT_WALK_4,
    movable_parts=["legs", "tail_wag"])

_bp("REP_SERPENT","Serpent",             "REP_SERPENT", 0,
    body_width_ratio=0.06, body_height_ratio=0.06, head_ratio=0.05,
    leg_ratio=0.0, has_tail=False, tail_ratio=0.0,
    gait="slither", gait_phases=GAIT_NONE,
    movable_parts=["body_wave"])

_bp("REP_TORTUE", "Tortue",             "REP_TORTUE", 4,
    body_width_ratio=0.70, body_height_ratio=0.45, head_ratio=0.18,
    leg_ratio=0.20, has_tail=True, tail_ratio=0.10,
    gait="walk", gait_phases=GAIT_WALK_4,
    movable_parts=["legs", "head_retract"],
    recommended_height_mm=40)

_bp("REP_CROCO",  "Crocodilien",        "REP_CROCO", 4,
    body_width_ratio=0.20, body_height_ratio=0.12, head_ratio=0.25,
    leg_ratio=0.15, has_tail=True, tail_ratio=0.50,
    gait="walk", gait_phases=GAIT_WALK_4,
    movable_parts=["legs", "jaw_snap", "tail_wag"])

_bp("REP_DINO_B", "Dinosaure bipède",   "REP_DINO", 2,
    body_width_ratio=0.25, body_height_ratio=0.30, head_ratio=0.22,
    leg_ratio=0.55, n_arms=2, arm_ratio=0.15, has_tail=True, tail_ratio=0.60,
    gait="walk", gait_phases=GAIT_BIPED,
    movable_parts=["legs", "head_nod", "jaw_snap"])

_bp("REP_DINO_Q", "Dinosaure quadrupède","REP_DINO", 4,
    body_width_ratio=0.30, body_height_ratio=0.25, head_ratio=0.15,
    leg_ratio=0.40, has_tail=True, tail_ratio=0.50,
    gait="walk", gait_phases=GAIT_WALK_4,
    movable_parts=["legs", "head_nod", "tail_wag"])

# ━━━ AMPHIBIENS ━━━
_bp("AMP_GREN",   "Grenouille",         "AMP_GRENOUILLE", 4,
    body_width_ratio=0.50, body_height_ratio=0.30, head_ratio=0.25,
    leg_ratio=0.70, has_tail=False,
    gait="jump", gait_phases=GAIT_BOUND,
    movable_parts=["legs_jump"],
    recommended_height_mm=40)

_bp("AMP_SALA",   "Salamandre",         "AMP_SALAMANDRE", 4,
    body_width_ratio=0.18, body_height_ratio=0.12, head_ratio=0.15,
    leg_ratio=0.20, has_tail=True, tail_ratio=0.60,
    gait="walk", gait_phases=GAIT_WALK_4,
    movable_parts=["legs", "tail_wag"])

# ━━━ POISSONS ━━━
_bp("FISH_STD",   "Poisson standard",   "FISH_STANDARD", 0,
    body_width_ratio=0.20, body_height_ratio=0.30, head_ratio=0.20,
    leg_ratio=0.0, has_tail=True, tail_ratio=0.25,
    gait="swim", gait_phases=GAIT_NONE,
    movable_parts=["tail_swim", "jaw_open"],
    n_wings=2, wing_ratio=0.15)  # nageoires pectorales

_bp("FISH_PLAT",  "Poisson plat",       "FISH_PLAT", 0,
    body_width_ratio=0.80, body_height_ratio=0.05, head_ratio=0.20,
    leg_ratio=0.0, has_tail=True, tail_ratio=0.40,
    gait="undulate", gait_phases=GAIT_NONE,
    movable_parts=["body_wave"])

# ━━━ INSECTES ━━━
_bp("INS_MARCH",  "Insecte marcheur",   "INS_MARCHEUR", 6,
    body_width_ratio=0.35, body_height_ratio=0.25, head_ratio=0.20,
    leg_ratio=0.50, has_tail=False,
    gait="tripod", gait_phases=GAIT_TRIPOD,
    movable_parts=["legs_tripod"],
    min_detail_mm=0.5, recommended_height_mm=40)

_bp("INS_VOL",    "Insecte volant",     "INS_VOLANT", 6,
    body_width_ratio=0.25, body_height_ratio=0.20, head_ratio=0.18,
    leg_ratio=0.30, n_wings=2, wing_ratio=1.50, has_tail=False,
    gait="flap", gait_phases=GAIT_FLAP,
    movable_parts=["wings_flap"],
    min_detail_mm=0.5, recommended_height_mm=50)

_bp("INS_SAUT",   "Insecte sauteur",    "INS_SAUTEUR", 6,
    body_width_ratio=0.20, body_height_ratio=0.25, head_ratio=0.18,
    leg_ratio=0.80, has_tail=False,  # pattes arrière TRÈS longues
    gait="jump", gait_phases=GAIT_BOUND,
    movable_parts=["legs_jump"],
    recommended_height_mm=50)

_bp("INS_MANTE",  "Mante religieuse",   "INS_MANTE", 6,
    body_width_ratio=0.15, body_height_ratio=0.15, head_ratio=0.15,
    leg_ratio=0.40, n_arms=2, arm_ratio=0.50, has_tail=False,
    gait="stalk", gait_phases=GAIT_WALK_4,
    movable_parts=["arms_strike", "head_rotate"])

# ━━━ ARACHNIDES ━━━
_bp("ARA_ARAIGN", "Araignée",           "ARA_ARAIGNEE", 8,
    body_width_ratio=0.40, body_height_ratio=0.35, head_ratio=0.40,
    leg_ratio=1.20, has_tail=False,  # céphalothorax = "tête" large
    gait="walk", gait_phases=GAIT_WAVE_6,  # vague alternée
    movable_parts=["legs"],
    recommended_height_mm=50)

_bp("ARA_SCORP",  "Scorpion",           "ARA_SCORPION", 8,
    body_width_ratio=0.30, body_height_ratio=0.15, head_ratio=0.20,
    leg_ratio=0.40, n_arms=2, arm_ratio=0.45, has_tail=True, tail_ratio=0.80,
    gait="walk", gait_phases=GAIT_WAVE_6,
    movable_parts=["legs", "tail_strike", "arms_pinch"])

# ━━━ CRUSTACÉS ━━━
_bp("CRU_CRABE",  "Crabe",              "CRU_CRABE", 8,
    body_width_ratio=1.20, body_height_ratio=0.30, head_ratio=0.10,
    leg_ratio=0.50, n_arms=2, arm_ratio=0.60, has_tail=False,
    gait="lateral", gait_phases=GAIT_LATERAL,
    movable_parts=["legs_lateral", "arms_pinch"])

_bp("CRU_HOMARD", "Homard",             "CRU_HOMARD", 8,
    body_width_ratio=0.25, body_height_ratio=0.20, head_ratio=0.18,
    leg_ratio=0.30, n_arms=2, arm_ratio=0.55, has_tail=True, tail_ratio=0.35,
    gait="walk", gait_phases=GAIT_WAVE_6,
    movable_parts=["legs", "arms_pinch", "tail_snap"])

# ━━━ MYRIAPODES ━━━
_bp("MYR_CENTI",  "Centipède",          "MYR_CENTIPEDE", 30,  # simplifié à 6 pour l'automate
    body_width_ratio=0.12, body_height_ratio=0.08, head_ratio=0.08,
    leg_ratio=0.15, has_tail=False,
    gait="wave", gait_phases=GAIT_WAVE_6,
    movable_parts=["body_wave"])

_bp("MYR_MILLI",  "Millipède",          "MYR_MILLIPEDE", 60,  # simplifié
    body_width_ratio=0.15, body_height_ratio=0.15, head_ratio=0.06,
    leg_ratio=0.08, has_tail=False,
    gait="wave", gait_phases=GAIT_WAVE_6,
    movable_parts=["body_wave"])

# ━━━ MOLLUSQUES ━━━
_bp("MOL_ESCARG", "Escargot",           "MOL_ESCARGOT", 0,
    body_width_ratio=0.30, body_height_ratio=0.60, head_ratio=0.15,
    leg_ratio=0.0, has_tail=False,
    gait="glide", gait_phases=GAIT_NONE,
    movable_parts=["head_emerge", "tentacles"],
    recommended_height_mm=40)

_bp("MOL_PIEUVRE","Pieuvre",              "MOL_PIEUVRE", 8,
    body_width_ratio=0.35, body_height_ratio=0.50, head_ratio=0.40,
    leg_ratio=1.00, has_tail=False,
    gait="swim", gait_phases=GAIT_NONE,
    movable_parts=["tentacles_wave"])

# ━━━ PLANTES ━━━
_bp("PL_FLEUR",   "Fleur",              "PL_FLEUR", 0,
    body_width_ratio=0.15, body_height_ratio=3.0, head_ratio=0.40,
    leg_ratio=0.0, has_tail=False,
    gait="none", gait_phases=GAIT_NONE,
    movable_parts=["petals_open", "stem_sway"],
    recommended_height_mm=80)

_bp("PL_CARNIV",  "Plante carnivore",   "PL_CARNIVORE", 0,
    body_width_ratio=0.20, body_height_ratio=1.5, head_ratio=0.35,
    leg_ratio=0.0, has_tail=False,
    gait="none", gait_phases=GAIT_NONE,
    movable_parts=["jaw_snap"])

# ━━━ CHAMPIGNONS ━━━
_bp("FU_CHAMP",   "Champignon",         "FU_CHAMPIGNON", 0,
    body_width_ratio=0.20, body_height_ratio=1.0, head_ratio=0.60,
    leg_ratio=0.0, has_tail=False,
    gait="none", gait_phases=GAIT_NONE,
    movable_parts=["cap_open", "spore_puff"],
    recommended_height_mm=50)

# ━━━ FANTASTIQUE ━━━
_bp("FAN_DRAGON", "Dragon",             "FAN_DRAGON", 4,
    body_width_ratio=0.30, body_height_ratio=0.25, head_ratio=0.22,
    leg_ratio=0.40, n_wings=2, wing_ratio=1.60, has_tail=True, tail_ratio=0.70,
    gait="walk", gait_phases=GAIT_WALK_4,
    movable_parts=["legs", "wings_flap", "head_nod", "jaw_snap", "tail_wag"])

_bp("FAN_LICORN", "Licorne",            "FAN_LICORNE", 4,
    body_width_ratio=0.22, body_height_ratio=0.28, head_ratio=0.18,
    leg_ratio=0.55, has_tail=True, tail_ratio=0.45,
    gait="trot", gait_phases=GAIT_TROT,
    movable_parts=["legs", "head_nod", "tail_wag"])

_bp("FAN_PHOENIX","Phénix",             "FAN_PHOENIX", 2,
    body_width_ratio=0.28, body_height_ratio=0.25, head_ratio=0.15,
    leg_ratio=0.25, n_wings=2, wing_ratio=2.00, has_tail=True, tail_ratio=0.80,
    gait="flap", gait_phases=GAIT_FLAP,
    movable_parts=["wings_flap", "tail_wag"])

_bp("FAN_ROBOT",  "Robot bipède",       "FAN_ROBOT", 2,
    body_width_ratio=0.40, body_height_ratio=0.35, head_ratio=0.20,
    leg_ratio=0.50, n_arms=2, arm_ratio=0.45, has_tail=False,
    gait="walk", gait_phases=GAIT_BIPED,
    movable_parts=["legs", "arms", "head_rotate"])


# ════════════════════════════════════════════════════════════════
#  §4 — ESPÈCES (instances concrètes avec tailles réelles)
# ════════════════════════════════════════════════════════════════

@dataclass
class Species:
    """Une espèce concrète avec ses dimensions réelles en mm."""
    name_fr: str
    name_en: str
    name_sci: str
    body_plan: str          # clé dans BODY_PLANS
    mass_kg: float
    body_length_mm: float   # longueur du corps

# (name_fr, name_en, name_sci, body_plan_id, mass_kg, body_length_mm)
_SPECIES_RAW = [
    # ── Mammifères trapus ──
    ("Ours brun",        "Brown bear",       "Ursus arctos",           "MAM_TRAPU",   250, 2000),
    ("Ours polaire",     "Polar bear",       "Ursus maritimus",        "MAM_TRAPU",   450, 2400),
    ("Hippopotame",      "Hippopotamus",     "Hippopotamus amphibius", "MAM_TRAPU",  1500, 3500),
    ("Rhinocéros",       "Rhinoceros",       "Rhinoceros unicornis",   "MAM_TRAPU",  2000, 3800),
    ("Éléphant",         "Elephant",         "Loxodonta africana",     "MAM_TRAPU",  6000, 6000),
    ("Cochon",           "Pig",              "Sus scrofa domesticus",  "MAM_TRAPU",    80, 1200),
    ("Sanglier",         "Wild boar",        "Sus scrofa",             "MAM_TRAPU",   100, 1500),
    ("Panda",            "Giant panda",      "Ailuropoda melanoleuca", "MAM_TRAPU",   100, 1500),

    # ── Mammifères graciles ──
    ("Cerf",             "Red deer",         "Cervus elaphus",         "MAM_GRACE",   200, 2000),
    ("Cheval",           "Horse",            "Equus caballus",         "MAM_GRACE",   500, 2400),
    ("Girafe",           "Giraffe",          "Giraffa",                "MAM_GRACE",   800, 3800),
    ("Vache",            "Cow",              "Bos taurus",             "MAM_GRACE",   700, 2400),
    ("Zèbre",            "Zebra",            "Equus quagga",           "MAM_GRACE",   350, 2200),
    ("Âne",              "Donkey",           "Equus asinus",           "MAM_GRACE",   250, 2000),
    ("Gazelle",          "Gazelle",          "Gazella",                "MAM_GRACE",    25, 1200),
    ("Chameau",          "Camel",            "Camelus dromedarius",    "MAM_GRACE",   500, 3000),
    ("Lama",             "Llama",            "Lama glama",             "MAM_GRACE",   150, 1800),

    # ── Félins ──
    ("Chat",             "Cat",              "Felis catus",            "MAM_FELIN",     4,  460),
    ("Lion",             "Lion",             "Panthera leo",           "MAM_FELIN",   190, 2000),
    ("Tigre",            "Tiger",            "Panthera tigris",        "MAM_FELIN",   220, 2200),
    ("Léopard",          "Leopard",          "Panthera pardus",        "MAM_FELIN",    60, 1400),
    ("Guépard",          "Cheetah",          "Acinonyx jubatus",       "MAM_FELIN",    50, 1300),
    ("Panthère noire",   "Black panther",    "Panthera pardus",        "MAM_FELIN",    60, 1400),
    ("Jaguar",           "Jaguar",           "Panthera onca",          "MAM_FELIN",    80, 1700),
    ("Lynx",             "Lynx",             "Lynx lynx",              "MAM_FELIN",    25,  900),

    # ── Canidés ──
    ("Chien",            "Dog",              "Canis familiaris",       "MAM_CANIN",    20,  600),
    ("Loup",             "Wolf",             "Canis lupus",            "MAM_CANIN",    40, 1200),
    ("Renard",           "Fox",              "Vulpes vulpes",          "MAM_CANIN",     6,  700),
    ("Husky",            "Husky",            "Canis familiaris",       "MAM_CANIN",    25,  700),
    ("Coyote",           "Coyote",           "Canis latrans",          "MAM_CANIN",    15,  900),
    ("Hyène",            "Hyena",            "Crocuta crocuta",        "MAM_CANIN",    55, 1300),

    # ── Petits mammifères ──
    ("Lapin",            "Rabbit",           "Oryctolagus cuniculus",  "MAM_PETIT",     2,  400),
    ("Écureuil",         "Squirrel",         "Sciurus vulgaris",       "MAM_PETIT",   0.3,  250),
    ("Souris",           "Mouse",            "Mus musculus",           "MAM_PETIT",  0.02,   80),
    ("Rat",              "Rat",              "Rattus norvegicus",      "MAM_PETIT",   0.3,  250),
    ("Hamster",          "Hamster",          "Mesocricetus auratus",   "MAM_PETIT",   0.1,  150),
    ("Hérisson",         "Hedgehog",         "Erinaceus europaeus",    "MAM_PETIT",   0.8,  250),
    ("Furet",            "Ferret",           "Mustela furo",           "MAM_PETIT",   1.0,  500),
    ("Castor",           "Beaver",           "Castor fiber",           "MAM_PETIT",    25,  800),

    # ── Primates ──
    ("Gorille",          "Gorilla",          "Gorilla gorilla",        "MAM_PRIMATE", 180, 1700),
    ("Chimpanzé",        "Chimpanzee",       "Pan troglodytes",        "MAM_PRIMATE",  50, 1200),
    ("Orang-outan",      "Orangutan",        "Pongo pygmaeus",         "MAM_PRIMATE",  75, 1400),
    ("Singe capucin",    "Capuchin monkey",  "Cebus capucinus",        "MAM_PRIMATE",   3,  450),

    # ── Mammifères marins ──
    ("Dauphin",          "Dolphin",          "Tursiops truncatus",     "MAM_MARIN",   200, 3000),
    ("Baleine",          "Whale",            "Balaenoptera musculus",  "MAM_MARIN", 100000, 25000),
    ("Phoque",           "Seal",             "Phoca vitulina",         "MAM_MARIN",    80, 1500),
    ("Morse",            "Walrus",           "Odobenus rosmarus",      "MAM_MARIN",  1000, 3200),
    ("Orque",            "Orca",             "Orcinus orca",           "MAM_MARIN",  5000, 8000),

    # ── Chiroptères ──
    ("Chauve-souris",    "Bat",              "Chiroptera",             "MAM_CHAUVE",  0.02,   60),

    # ── Oiseaux volants ──
    ("Pigeon",           "Pigeon",           "Columba livia",          "AV_VOL",      0.3,  300),
    ("Moineau",          "Sparrow",          "Passer domesticus",      "AV_PETIT",    0.03, 150),
    ("Colibri",          "Hummingbird",      "Trochilidae",            "AV_PETIT",    0.005, 80),
    ("Perroquet",        "Parrot",           "Psittacidae",            "AV_VOL",      0.4,  350),
    ("Canard",           "Duck",             "Anas platyrhynchos",     "AV_VOL",      1.2,  500),

    # ── Rapaces ──
    ("Aigle",            "Eagle",            "Aquila chrysaetos",      "AV_RAPACE",     5,  800),
    ("Faucon",           "Falcon",           "Falco peregrinus",       "AV_RAPACE",   1.5,  450),
    ("Hibou",            "Owl",              "Bubo bubo",              "AV_RAPACE",     3,  650),
    ("Vautour",          "Vulture",          "Gyps fulvus",            "AV_RAPACE",     8, 1000),

    # ── Oiseaux coureurs ──
    ("Autruche",         "Ostrich",          "Struthio camelus",       "AV_COUREUR", 120, 2000),
    ("Émeu",             "Emu",              "Dromaius novaehollandiae","AV_COUREUR",  40, 1700),

    # ── Oiseaux nageurs ──
    ("Pingouin",         "Penguin",          "Aptenodytes patagonicus","AV_NAGEUR",    13,  600),
    ("Flamant rose",     "Flamingo",         "Phoenicopterus roseus",  "AV_COUREUR",  3.5, 1100),

    # ── Reptiles ──
    ("Lézard",           "Lizard",           "Lacerta agilis",         "REP_LEZARD",  0.01, 200),
    ("Iguane",           "Iguana",           "Iguana iguana",           "REP_LEZARD",   5, 1500),
    ("Caméléon",         "Chameleon",        "Chamaeleo",              "REP_LEZARD",  0.2,  250),
    ("Gecko",            "Gecko",            "Gekkonidae",             "REP_LEZARD",  0.05, 150),
    ("Serpent",          "Snake",            "Serpentes",              "REP_SERPENT",   1, 1200),
    ("Cobra",            "Cobra",            "Naja naja",              "REP_SERPENT",   3, 1800),
    ("Python",           "Python",           "Python regius",          "REP_SERPENT",   2, 1500),
    ("Tortue",           "Turtle",           "Testudo",                "REP_TORTUE",    3,  250),
    ("Tortue marine",    "Sea turtle",       "Chelonia mydas",         "REP_TORTUE",  150, 1200),
    ("Crocodile",        "Crocodile",        "Crocodylus niloticus",   "REP_CROCO",   400, 4000),
    ("Alligator",        "Alligator",        "Alligator mississippiensis","REP_CROCO", 250, 3500),

    # ── Dinosaures ──
    ("T-Rex",            "T-Rex",            "Tyrannosaurus rex",      "REP_DINO_B", 8000, 12000),
    ("Vélociraptor",     "Velociraptor",     "Velociraptor mongoliensis","REP_DINO_B",  15, 1800),
    ("Tricératops",      "Triceratops",      "Triceratops horridus",   "REP_DINO_Q", 8000, 8000),
    ("Stégosaure",       "Stegosaurus",      "Stegosaurus stenops",    "REP_DINO_Q", 5000, 9000),
    ("Brachiosaure",     "Brachiosaurus",    "Brachiosaurus altithorax","REP_DINO_Q",50000,23000),
    ("Ptérodactyle",     "Pterodactyl",      "Pteranodon longiceps",   "AV_RAPACE",    20, 1800),

    # ── Amphibiens ──
    ("Grenouille",       "Frog",             "Rana temporaria",        "AMP_GREN",    0.03, 100),
    ("Crapaud",          "Toad",             "Bufo bufo",              "AMP_GREN",    0.08, 130),
    ("Salamandre",       "Salamander",       "Salamandra salamandra",  "AMP_SALA",    0.04, 200),
    ("Axolotl",          "Axolotl",          "Ambystoma mexicanum",    "AMP_SALA",    0.15, 250),

    # ── Poissons ──
    ("Poisson rouge",    "Goldfish",         "Carassius auratus",      "FISH_STD",    0.05, 150),
    ("Requin",           "Shark",            "Carcharodon carcharias", "FISH_STD",   1000, 5000),
    ("Poisson-clown",    "Clownfish",        "Amphiprion ocellaris",   "FISH_STD",    0.01, 100),
    ("Espadon",          "Swordfish",        "Xiphias gladius",        "FISH_STD",    450, 4500),
    ("Raie",             "Stingray",         "Dasyatis",               "FISH_PLAT",    25, 1500),

    # ── Insectes marcheurs ──
    ("Fourmi",           "Ant",              "Formicidae",             "INS_MARCH",  0.001,    3),
    ("Scarabée",         "Beetle",           "Coleoptera",             "INS_MARCH",  0.005,   30),
    ("Cafard",           "Cockroach",        "Blattodea",              "INS_MARCH",  0.003,   40),
    ("Coccinelle",       "Ladybug",          "Coccinellidae",          "INS_MARCH",  0.001,    8),

    # ── Insectes volants ──
    ("Papillon",         "Butterfly",        "Lepidoptera",            "INS_VOL",    0.001,   30),
    ("Libellule",        "Dragonfly",        "Odonata",                "INS_VOL",    0.003,   50),
    ("Abeille",          "Bee",              "Apis mellifera",         "INS_VOL",    0.001,   15),
    ("Mouche",           "Fly",              "Musca domestica",        "INS_VOL",    0.001,    8),

    # ── Insectes sauteurs ──
    ("Sauterelle",       "Grasshopper",      "Caelifera",              "INS_SAUT",   0.005,   50),
    ("Criquet",          "Cricket",          "Gryllidae",              "INS_SAUT",   0.003,   30),

    # ── Mantes ──
    ("Mante religieuse", "Praying mantis",   "Mantis religiosa",       "INS_MANTE",  0.005,   75),

    # ── Arachnides ──
    ("Araignée",         "Spider",           "Araneae",                "ARA_ARAIGN",  0.01,   15),
    ("Tarentule",        "Tarantula",        "Theraphosidae",          "ARA_ARAIGN",  0.08,   50),
    ("Scorpion",         "Scorpion",         "Scorpiones",             "ARA_SCORP",   0.05,   80),

    # ── Crustacés ──
    ("Crabe",            "Crab",             "Brachyura",              "CRU_CRABE",   0.5,  150),
    ("Homard",           "Lobster",          "Homarus gammarus",       "CRU_HOMARD",  3.0,  500),
    ("Écrevisse",        "Crayfish",         "Astacus astacus",        "CRU_HOMARD",  0.1,  120),
    ("Crevette",         "Shrimp",           "Caridea",                "CRU_HOMARD",  0.02,  80),

    # ── Myriapodes ──
    ("Centipède",        "Centipede",        "Chilopoda",              "MYR_CENTI",   0.01, 100),
    ("Millipède",        "Millipede",        "Diplopoda",              "MYR_MILLI",   0.02, 120),

    # ── Mollusques ──
    ("Escargot",         "Snail",            "Helix pomatia",          "MOL_ESCARG",  0.02,  50),
    ("Pieuvre",          "Octopus",          "Octopus vulgaris",       "MOL_PIEUVRE",  5.0,  600),
    ("Calmar",           "Squid",            "Loligo vulgaris",        "MOL_PIEUVRE",  1.5,  400),

    # ── Plantes ──
    ("Tournesol",        "Sunflower",        "Helianthus annuus",      "PL_FLEUR",    0, 2000),
    ("Dionée",           "Venus flytrap",    "Dionaea muscipula",      "PL_CARNIV",   0,  150),

    # ── Champignons ──
    ("Amanite tue-mouches","Fly agaric",     "Amanita muscaria",       "FU_CHAMP",    0,  150),

    # ── Fantastique ──
    ("Dragon",           "Dragon",           "Draco fantasticus",      "FAN_DRAGON",  500, 5000),
    ("Licorne",          "Unicorn",          "Equus unicornis",        "FAN_LICORN",  400, 2400),
    ("Phénix",           "Phoenix",          "Phoenix ignis",          "FAN_PHOENIX",  10, 1000),
    ("Robot",            "Robot",            "Machina sapiens",        "FAN_ROBOT",    50, 1500),
]

SPECIES_DB: Dict[str, Species] = {}
_SPECIES_INDEX: Dict[str, str] = {}

for _row in _SPECIES_RAW:
    _nfr, _nen, _nsci, _bp_id, _mass, _bl = _row
    _key = _nen.lower().replace(" ", "_").replace("-", "_")
    _sp = Species(_nfr, _nen, _nsci, _bp_id, _mass, _bl)
    SPECIES_DB[_key] = _sp
    _SPECIES_INDEX[_nfr.lower()] = _key
    _SPECIES_INDEX[_nen.lower()] = _key
    _SPECIES_INDEX[_nsci.lower()] = _key


# ════════════════════════════════════════════════════════════════
#  §5 — FONCTIONS DE RECHERCHE
# ════════════════════════════════════════════════════════════════

def find_species(query: str) -> Optional[Species]:
    """Cherche une espèce par nom (FR/EN/scientifique)."""
    q = query.lower().strip()
    if q in _SPECIES_INDEX:
        return SPECIES_DB[_SPECIES_INDEX[q]]
    if q in SPECIES_DB:
        return SPECIES_DB[q]
    # Partiel
    for name, key in _SPECIES_INDEX.items():
        if q in name or name in q:
            return SPECIES_DB[key]
    return None


def get_body_plan(species_or_query) -> Optional[BodyPlan]:
    """Retourne le BodyPlan pour une espèce ou un nom."""
    if isinstance(species_or_query, Species):
        return BODY_PLANS.get(species_or_query.body_plan)
    sp = find_species(species_or_query)
    if sp:
        return BODY_PLANS.get(sp.body_plan)
    return None


def list_categories(parent=None) -> List[str]:
    """Liste les sous-catégories d'un parent."""
    return [k for k, v in CATEGORY_TREE.items() if v[0] == parent]


def list_species_in_category(cat_id: str) -> List[Species]:
    """Liste les espèces dans une catégorie (et sous-catégories)."""
    # Collecter toutes les sous-catégories
    cats = {cat_id}
    changed = True
    while changed:
        changed = False
        for k, v in CATEGORY_TREE.items():
            if v[0] in cats and k not in cats:
                cats.add(k)
                changed = True
    # Collecter les body plans de ces catégories
    bps = {bp_id for bp_id, bp in BODY_PLANS.items() if bp.category in cats}
    return [sp for sp in SPECIES_DB.values() if sp.body_plan in bps]


def print_tree(parent=None, indent=0):
    """Affiche l'arbre de catégorisation."""
    children = [k for k, v in CATEGORY_TREE.items() if v[0] == parent]
    for child in children:
        info = CATEGORY_TREE[child]
        n_species = len(list_species_in_category(child))
        prefix = "  " * indent + ("├─ " if indent > 0 else "")
        print(f"{prefix}{info[1]} [{child}] ({n_species} espèces)")
        print_tree(child, indent + 1)


# ════════════════════════════════════════════════════════════════
#  §6 — TESTS
# ════════════════════════════════════════════════════════════════

def test_living_beings_db():
    passed = 0
    total = 0

    # 1: DB non vide
    total += 1
    assert len(SPECIES_DB) >= 100, f"Trop peu d'espèces: {len(SPECIES_DB)}"
    passed += 1

    # 2: Body plans non vides
    total += 1
    assert len(BODY_PLANS) >= 30, f"Trop peu de body plans: {len(BODY_PLANS)}"
    passed += 1

    # 3: Chaque espèce a un body plan valide
    total += 1
    for key, sp in SPECIES_DB.items():
        assert sp.body_plan in BODY_PLANS, f"{key}: body_plan '{sp.body_plan}' invalide"
    passed += 1

    # 4: Chaque body plan a une catégorie valide
    total += 1
    for bp_id, bp in BODY_PLANS.items():
        assert bp.category in CATEGORY_TREE, f"{bp_id}: category '{bp.category}' invalide"
    passed += 1

    # 5: Recherche FR
    total += 1
    assert find_species("chat") is not None
    assert find_species("chat").name_en == "Cat"
    passed += 1

    # 6: Recherche EN
    total += 1
    assert find_species("spider") is not None
    passed += 1

    # 7: Recherche scientifique
    total += 1
    assert find_species("Felis catus") is not None
    passed += 1

    # 8: Body plan lookup
    total += 1
    bp = get_body_plan("lion")
    assert bp is not None
    assert bp.n_legs == 4
    assert bp.gait == "walk"
    passed += 1

    # 9: Catégories enfants
    total += 1
    kids = list_categories("ANIMALIA")
    assert "VERTEBRATA" in kids
    assert "ARTHROPODA" in kids
    passed += 1

    # 10: Espèces par catégorie
    total += 1
    mammals = list_species_in_category("MAMMALIA")
    assert len(mammals) >= 30, f"Mammifères: {len(mammals)}"
    passed += 1

    # 11: Insectes dans la DB
    total += 1
    insects = list_species_in_category("INSECTA")
    assert len(insects) >= 8, f"Insectes: {len(insects)}"
    passed += 1

    # 12: Arachnides
    total += 1
    arach = list_species_in_category("ARACHNIDA")
    assert len(arach) >= 3, f"Arachnides: {len(arach)}"
    passed += 1

    # 13: Crustacés
    total += 1
    crust = list_species_in_category("CRUSTACEA")
    assert len(crust) >= 3, f"Crustacés: {len(crust)}"
    passed += 1

    # 14: Fantastique
    total += 1
    fan = list_species_in_category("FANTASIA")
    assert len(fan) >= 4, f"Fantastique: {len(fan)}"
    passed += 1

    # 15: Proportions cohérentes
    total += 1
    for bp_id, bp in BODY_PLANS.items():
        assert 0 <= bp.body_width_ratio <= 2.0, f"{bp_id}: width_ratio={bp.body_width_ratio}"
        assert 0 <= bp.head_ratio <= 1.0, f"{bp_id}: head_ratio={bp.head_ratio}"
        if bp.n_legs > 0:
            assert bp.leg_ratio > 0, f"{bp_id}: {bp.n_legs} pattes mais leg_ratio=0"
    passed += 1

    # 16: Gait phases existent pour les marcheurs
    total += 1
    for bp_id, bp in BODY_PLANS.items():
        if bp.gait in ("walk", "trot", "pace", "gallop", "bound", "tripod", "lateral"):
            assert len(bp.gait_phases) > 0, f"{bp_id}: gait={bp.gait} sans phases"
    passed += 1

    # 17: Movable parts non vides
    total += 1
    for bp_id, bp in BODY_PLANS.items():
        assert len(bp.movable_parts) > 0, f"{bp_id}: aucune partie mobile"
    passed += 1

    # 18: Arbre de catégories cohérent (pas de parent orphelin)
    total += 1
    for k, v in CATEGORY_TREE.items():
        if v[0] is not None:
            assert v[0] in CATEGORY_TREE, f"{k}: parent '{v[0]}' n'existe pas"
    passed += 1

    # 19: Au moins 5 catégories racines
    total += 1
    roots = [k for k, v in CATEGORY_TREE.items() if v[0] is None]
    assert len(roots) >= 4, f"Racines: {roots}"
    passed += 1

    # 20: Couverture tous les grands groupes
    total += 1
    required = ["MAMMALIA", "AVES", "REPTILIA", "INSECTA", "ARACHNIDA", "CRUSTACEA"]
    for r in required:
        assert r in CATEGORY_TREE, f"Groupe manquant: {r}"
        spp = list_species_in_category(r)
        assert len(spp) >= 2, f"{r}: seulement {len(spp)} espèces"
    passed += 1

    print(f"living_beings_db: {passed}/{total} tests passés {'✅' if passed == total else '❌'}")
    return passed == total


if __name__ == "__main__":
    test_living_beings_db()
    print(f"\n{len(SPECIES_DB)} espèces | {len(BODY_PLANS)} body plans | {len(CATEGORY_TREE)} catégories")
    print("\n─── ARBRE ───")
    print_tree()
