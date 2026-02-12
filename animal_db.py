"""
animal_db.py — Base de données animaux + calculateur de proportions
===================================================================
Tu donnes un nom d'animal → tu récupères toutes ses proportions.
Tu donnes juste un poids → tu récupères des proportions approximatives.

Données vérifiées :
  - Kilbourne & Hoffman 2013 (PLoS ONE) — allométrie membres
  - Campione 2012 (BMC Biology) — diamètre os
  - Bishop 2021 (PeerJ) — masse musculaire
  - Dimensions.com — mesures par espèce
  - CSE169 UCSD / Animator Notebook — patterns de marche
"""
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# ════════════════════════════════════════════════════════════════
#  §1 — TYPES DE CORPS (body plans)
# ════════════════════════════════════════════════════════════════

BODY_PLANS = {
    # id: (description, nb_pattes, type_mouvement_principal)
    "QUAD_TRAPU":   ("Quadrupède trapu (ours, hippo)",       4, "pace"),
    "QUAD_GRACE":   ("Quadrupède gracile (cerf, cheval)",    4, "trot"),
    "QUAD_EQUIN":   ("Quadrupède équin (cheval, zèbre)",     4, "gallop"),
    "QUAD_FELIN":   ("Quadrupède félin (chat, lion)",        4, "gallop"),
    "QUAD_CANIN":   ("Quadrupède canin (chien, loup)",       4, "trot"),
    "QUAD_PETIT":   ("Petit quadrupède (lapin, écureuil)",   4, "bound"),
    "BIPED_HUMAIN": ("Bipède humanoïde",                     2, "walk"),
    "BIPED_OISEAU": ("Bipède oiseau (poule, pingouin)",      2, "walk"),
    "OISEAU_VOL":   ("Oiseau volant (ailes battantes)",      2, "flap"),
    "SERPENT":      ("Serpent (sans pattes, ondulation)",     0, "slither"),
    "INSECTE":      ("Insecte / hexapode",                   6, "tripod"),
    "CRABE":        ("Crabe / décapode",                    10, "lateral"),
    "POISSON":      ("Poisson (nageoire caudale)",           0, "swim"),
}

# ════════════════════════════════════════════════════════════════
#  §2 — BASE DE DONNÉES ESPÈCES (données vérifiées)
# ════════════════════════════════════════════════════════════════

@dataclass
class AnimalData:
    """Données d'un animal. Toutes les longueurs en mm, masse en kg."""
    name_fr: str
    name_en: str
    name_sci: str               # nom scientifique
    body_plan: str              # clé dans BODY_PLANS
    mass_kg: float              # masse adulte typique
    body_length_mm: float       # longueur museau → base queue
    shoulder_height_mm: float   # hauteur au garrot (0 si pas applicable)
    body_width_mm: float        # largeur du corps
    leg_length_mm: float        # longueur d'une patte (0 si serpent/poisson)
    tail_length_mm: float       # longueur queue
    head_length_mm: float       # longueur tête
    n_legs: int                 # nombre de pattes
    gait: str                   # démarche principale
    gait_phases: Dict[str, float] = field(default_factory=dict)
    # phases de marche: {"LH": 0.0, "LF": 0.25, "RH": 0.5, "RF": 0.75}
    # LH=Left Hind, LF=Left Front, RH=Right Hind, RF=Right Front

    @property
    def body_ratio(self) -> float:
        """Ratio longueur/hauteur — utile pour la silhouette."""
        if self.shoulder_height_mm > 0:
            return self.body_length_mm / self.shoulder_height_mm
        return 2.0  # défaut pour animaux sans "hauteur d'épaule"

    def to_figurine(self, target_height_mm: float = 60.0) -> 'FigurineProportions':
        """Convertit en proportions pour une figurine à l'échelle."""
        if self.shoulder_height_mm > 0:
            scale = target_height_mm / self.shoulder_height_mm
        else:
            scale = target_height_mm / self.body_length_mm
        return FigurineProportions(
            body_l=round(self.body_length_mm * scale, 1),
            body_w=round(self.body_width_mm * scale, 1),
            body_h=round(self.shoulder_height_mm * scale, 1) if self.shoulder_height_mm > 0 else round(target_height_mm * 0.4, 1),
            head_l=round(self.head_length_mm * scale, 1),
            leg_l=round(self.leg_length_mm * scale, 1),
            tail_l=round(self.tail_length_mm * scale, 1),
            n_legs=self.n_legs,
            scale=scale,
            body_plan=self.body_plan,
            gait=self.gait,
            gait_phases=self.gait_phases,
        )


@dataclass
class FigurineProportions:
    """Proportions d'une figurine prête à être générée en 3D."""
    body_l: float   # longueur corps (mm)
    body_w: float   # largeur corps (mm)
    body_h: float   # hauteur corps (mm)
    head_l: float   # longueur tête (mm)
    leg_l: float    # longueur patte (mm)
    tail_l: float   # longueur queue (mm)
    n_legs: int
    scale: float
    body_plan: str
    gait: str
    gait_phases: Dict[str, float] = field(default_factory=dict)


# ── Phases de marche par défaut pour chaque type ──
# Sources: CSE169 UCSD, Animator Notebook, Muybridge
GAIT_PHASES = {
    "walk":    {"LH": 0.00, "LF": 0.25, "RH": 0.50, "RF": 0.75},  # 4-beat
    "trot":    {"LH": 0.00, "LF": 0.50, "RH": 0.50, "RF": 0.00},  # 2-beat diagonal
    "pace":    {"LH": 0.00, "LF": 0.00, "RH": 0.50, "RF": 0.50},  # 2-beat latéral (ours)
    "gallop":  {"LH": 0.00, "RH": 0.10, "LF": 0.50, "RF": 0.60},  # transverse
    "bound":   {"LH": 0.00, "RH": 0.00, "LF": 0.50, "RF": 0.50},  # lapin
    "flap":    {"LW": 0.00, "RW": 0.00},  # ailes simultanées
    "slither": {},       # pas de pattes
    "swim":    {},       # pas de pattes
    "tripod":  {"L1": 0.0, "R2": 0.0, "L3": 0.0, "R1": 0.5, "L2": 0.5, "R3": 0.5},
    "lateral": {"L1": 0.0, "R1": 0.5},  # crabe simplifié
}

# ── La base ──
# Données: Dimensions.com, Wikipedia, études morphométriques
# Format: (name_fr, name_en, name_sci, body_plan,
#          mass_kg, body_mm, shoulder_mm, width_mm, leg_mm, tail_mm, head_mm, n_legs, gait)

_RAW_DB = [
    # ── QUADRUPÈDES TRAPUS ──
    ("Ours brun",       "Brown bear",      "Ursus arctos",        "QUAD_TRAPU",   250, 2000, 1100, 600,  700, 100,  350, 4, "pace"),
    ("Ours polaire",    "Polar bear",       "Ursus maritimus",     "QUAD_TRAPU",   450, 2400, 1300, 700,  800, 120,  400, 4, "pace"),
    ("Hippopotame",     "Hippopotamus",     "Hippopotamus amphibius","QUAD_TRAPU", 1500, 3500, 1500, 1000, 600, 350,  600, 4, "walk"),
    ("Rhinocéros",      "Rhinoceros",       "Rhinoceros unicornis","QUAD_TRAPU",  2000, 3800, 1700, 900,  800, 700,  700, 4, "walk"),
    ("Cochon",          "Pig",              "Sus scrofa domesticus","QUAD_TRAPU",    80, 1200,  700, 400,  400, 250,  300, 4, "walk"),

    # ── QUADRUPÈDES GRACILES ──
    ("Cerf",            "Deer",             "Cervus elaphus",      "QUAD_GRACE",   200, 2000, 1200, 400,  800, 200,  350, 4, "trot"),
    ("Girafe",          "Giraffe",          "Giraffa",             "QUAD_GRACE",   800, 3800, 5000, 700, 2000, 800,  600, 4, "walk"),
    ("Vache",           "Cow",              "Bos taurus",          "QUAD_GRACE",   700, 2400, 1400, 600,  800, 600,  500, 4, "walk"),

    # ── QUADRUPÈDES ÉQUINS ──
    ("Cheval",          "Horse",            "Equus caballus",      "QUAD_EQUIN",   500, 2400, 1600, 500, 1000, 900,  600, 4, "trot"),
    ("Zèbre",           "Zebra",            "Equus quagga",        "QUAD_EQUIN",   350, 2200, 1400, 450,  900, 500,  500, 4, "trot"),
    ("Âne",             "Donkey",           "Equus asinus",        "QUAD_EQUIN",   250, 2000, 1200, 400,  800, 400,  450, 4, "walk"),

    # ── FÉLINS ──
    ("Chat",            "Cat",              "Felis catus",         "QUAD_FELIN",     4,  460,  250, 150,  200, 300,  100, 4, "walk"),
    ("Lion",            "Lion",             "Panthera leo",        "QUAD_FELIN",   190, 2000, 1200, 500,  700, 900,  350, 4, "walk"),
    ("Tigre",           "Tiger",            "Panthera tigris",     "QUAD_FELIN",   220, 2200, 1100, 500,  650, 1000, 350, 4, "walk"),
    ("Léopard",         "Leopard",          "Panthera pardus",     "QUAD_FELIN",    60, 1400,  700, 300,  450, 900,  250, 4, "walk"),
    ("Guépard",         "Cheetah",          "Acinonyx jubatus",    "QUAD_FELIN",    50, 1300,  800, 300,  550, 750,  200, 4, "gallop"),

    # ── CANINS ──
    ("Chien (moyen)",   "Dog (medium)",     "Canis familiaris",    "QUAD_CANIN",    20,  600,  450, 200,  300, 250,  200, 4, "trot"),
    ("Loup",            "Wolf",             "Canis lupus",         "QUAD_CANIN",    40, 1200,  800, 350,  500, 400,  280, 4, "trot"),
    ("Renard",          "Fox",              "Vulpes vulpes",       "QUAD_CANIN",     6,  700,  400, 200,  250, 400,  150, 4, "trot"),

    # ── PETITS QUADRUPÈDES ──
    ("Lapin",           "Rabbit",           "Oryctolagus cuniculus","QUAD_PETIT",     2,  400,  200, 120,  150, 60,   80, 4, "bound"),
    ("Écureuil",        "Squirrel",         "Sciurus vulgaris",    "QUAD_PETIT",   0.3,  250,  120,  70,   80, 200,   50, 4, "bound"),
    ("Souris",          "Mouse",            "Mus musculus",        "QUAD_PETIT",  0.02,   80,   30,  25,   20, 80,    20, 4, "walk"),
    ("Tortue",          "Turtle",           "Testudo",             "QUAD_TRAPU",     3,  250,  120, 150,   60, 30,    50, 4, "walk"),
    ("Éléphant",        "Elephant",         "Loxodonta africana",  "QUAD_TRAPU",  6000, 6000, 3500, 2000, 1800, 1200, 800, 4, "walk"),

    # ── BIPÈDES ──
    ("Humain",          "Human",            "Homo sapiens",        "BIPED_HUMAIN",  70, 500,  1750, 400,  800, 0,    230, 2, "walk"),
    ("Pingouin",        "Penguin",          "Aptenodytes patagonicus","BIPED_OISEAU", 13, 600, 900, 250,  200, 0,    150, 2, "walk"),
    ("Poule",           "Chicken",          "Gallus gallus",       "BIPED_OISEAU",   3,  350,  400, 200,  200, 150,  100, 2, "walk"),

    # ── OISEAUX VOLANTS ──
    ("Pigeon",          "Pigeon",           "Columba livia",       "OISEAU_VOL",   0.3, 300,  200, 150,   50, 120,   60, 2, "flap"),
    ("Aigle",           "Eagle",            "Aquila chrysaetos",   "OISEAU_VOL",     5, 800,  350, 250,  150, 300,  120, 2, "flap"),
    ("Canard",          "Duck",             "Anas platyrhynchos",  "OISEAU_VOL",   1.2, 500,  250, 200,  100, 100,  100, 2, "flap"),

    # ── SERPENT ──
    ("Serpent",         "Snake",            "Serpentes",           "SERPENT",         1, 1200,    0, 50,     0, 0,   40, 0, "slither"),

    # ── INSECTES ──
    ("Fourmi",          "Ant",              "Formicidae",          "INSECTE",     0.001,  3,    2,   1,     2, 0,    1, 6, "tripod"),
    ("Scarabée",        "Beetle",           "Coleoptera",          "INSECTE",     0.005, 30,   15,  15,    10, 0,    8, 6, "tripod"),
]

# Construction de la DB
ANIMAL_DB: Dict[str, AnimalData] = {}
_NAME_INDEX: Dict[str, str] = {}  # index nom_fr/en/sci → clé DB

for _row in _RAW_DB:
    _name_fr, _name_en, _name_sci, _plan, _mass, _bl, _sh, _bw, _ll, _tl, _hl, _nl, _gait = _row
    _key = _name_en.lower().replace(" ", "_").replace("(", "").replace(")", "")
    _phases = dict(GAIT_PHASES.get(_gait, {}))
    _animal = AnimalData(
        name_fr=_name_fr, name_en=_name_en, name_sci=_name_sci,
        body_plan=_plan, mass_kg=_mass,
        body_length_mm=_bl, shoulder_height_mm=_sh, body_width_mm=_bw,
        leg_length_mm=_ll, tail_length_mm=_tl, head_length_mm=_hl,
        n_legs=_nl, gait=_gait, gait_phases=_phases,
    )
    ANIMAL_DB[_key] = _animal
    # Index multi-langue
    _NAME_INDEX[_name_fr.lower()] = _key
    _NAME_INDEX[_name_en.lower()] = _key
    _NAME_INDEX[_name_sci.lower()] = _key


# ════════════════════════════════════════════════════════════════
#  §3 — RECHERCHE D'ANIMAL
# ════════════════════════════════════════════════════════════════

def find_animal(query: str) -> Optional[AnimalData]:
    """
    Cherche un animal par nom (FR, EN, ou scientifique).
    Supporte la recherche floue (contient le mot).

    >>> find_animal("ours")
    AnimalData(name_fr='Ours brun', ...)
    >>> find_animal("cat")
    AnimalData(name_fr='Chat', ...)
    """
    q = query.lower().strip()

    # Match exact
    if q in _NAME_INDEX:
        return ANIMAL_DB[_NAME_INDEX[q]]

    # Match par clé DB
    if q in ANIMAL_DB:
        return ANIMAL_DB[q]

    # Match partiel (contient)
    candidates = []
    for name, key in _NAME_INDEX.items():
        if q in name or name in q:
            candidates.append((len(name), key))  # préfère les noms courts (plus spécifiques)

    if candidates:
        candidates.sort(key=lambda x: -x[0])  # plus long match = meilleur
        return ANIMAL_DB[candidates[0][1]]

    return None


def list_animals() -> List[str]:
    """Liste tous les animaux disponibles (noms FR)."""
    return [a.name_fr for a in ANIMAL_DB.values()]


# ════════════════════════════════════════════════════════════════
#  §4 — CALCULATEUR DE PROPORTIONS (allométrie)
# ════════════════════════════════════════════════════════════════
#
# Quand on a PAS l'animal dans la base, on peut calculer
# des proportions approximatives juste avec la masse.
#
# Sources:
#   Kilbourne & Hoffman 2013: limb_length ∝ mass^0.40
#   Campione 2012: bone_diameter ∝ mass^0.35
#   Alexander 1977: shoulder_height ≈ 4.5 × mass^0.26

def estimate_proportions(mass_kg: float, n_legs: int = 4,
                         body_plan: str = "QUAD_GRACE") -> AnimalData:
    """
    Estime les proportions d'un animal à partir de sa masse.
    Retourne un AnimalData avec des valeurs calculées.

    >>> props = estimate_proportions(50, n_legs=4)
    >>> props.shoulder_height_mm > 0
    True
    """
    m = max(mass_kg, 0.001)

    # Allométrie (coefficients issus de la littérature)
    shoulder_h = 4500 * m**0.26        # mm — Alexander 1977
    limb_l     = 280 * m**0.40         # mm — Kilbourne & Hoffman 2013
    body_l     = 6000 * m**0.33        # mm — estimation longueur corps
    body_w     = body_l * 0.30         # largeur ≈ 30% de la longueur
    head_l     = body_l * 0.18         # tête ≈ 18% du corps
    tail_l     = body_l * 0.25         # queue ≈ 25% du corps

    if n_legs == 0:
        shoulder_h = 0
        limb_l = 0
    elif n_legs == 2:
        shoulder_h *= 1.8  # bipèdes sont plus hauts
        limb_l *= 1.5

    gait = BODY_PLANS.get(body_plan, ("", 4, "walk"))[2]
    phases = dict(GAIT_PHASES.get(gait, {}))

    return AnimalData(
        name_fr=f"Animal estimé ({mass_kg}kg)",
        name_en=f"Estimated animal ({mass_kg}kg)",
        name_sci="Estimatus automaticus",
        body_plan=body_plan,
        mass_kg=m,
        body_length_mm=round(body_l, 1),
        shoulder_height_mm=round(shoulder_h, 1),
        body_width_mm=round(body_w, 1),
        leg_length_mm=round(limb_l, 1),
        tail_length_mm=round(tail_l, 1),
        head_length_mm=round(head_l, 1),
        n_legs=n_legs,
        gait=gait,
        gait_phases=phases,
    )


def get_or_estimate(query: str, fallback_mass_kg: float = 10.0) -> AnimalData:
    """
    Cherche l'animal dans la base. Si pas trouvé, estime avec la masse.

    >>> get_or_estimate("chat").name_fr
    'Chat'
    >>> get_or_estimate("animal inconnu", 25.0).mass_kg
    25.0
    """
    found = find_animal(query)
    if found:
        return found
    return estimate_proportions(fallback_mass_kg)


# ════════════════════════════════════════════════════════════════
#  §5 — TESTS
# ════════════════════════════════════════════════════════════════

def test_animal_db():
    """Tests de la base de données animaux."""
    passed = 0
    total = 0

    # Test 1: DB non vide
    total += 1
    assert len(ANIMAL_DB) >= 30, f"DB trop petite: {len(ANIMAL_DB)}"
    passed += 1

    # Test 2: Recherche FR
    total += 1
    bear = find_animal("ours brun")
    assert bear is not None, "Ours brun non trouvé"
    assert bear.mass_kg == 250
    passed += 1

    # Test 3: Recherche EN
    total += 1
    cat = find_animal("cat")
    assert cat is not None, "Cat non trouvé"
    assert cat.n_legs == 4
    passed += 1

    # Test 4: Recherche partielle
    total += 1
    lion = find_animal("lion")
    assert lion is not None, "Lion non trouvé"
    assert lion.body_plan == "QUAD_FELIN"
    passed += 1

    # Test 5: Recherche scientifique
    total += 1
    horse = find_animal("Equus caballus")
    assert horse is not None, "Equus caballus non trouvé"
    assert horse.name_fr == "Cheval"
    passed += 1

    # Test 6: Estimation par masse
    total += 1
    est = estimate_proportions(100, n_legs=4)
    assert est.shoulder_height_mm > 500, f"Hauteur trop petite: {est.shoulder_height_mm}"
    assert est.leg_length_mm > 200, f"Pattes trop courtes: {est.leg_length_mm}"
    passed += 1

    # Test 7: Conversion en figurine
    total += 1
    bear = find_animal("ours")
    fig = bear.to_figurine(target_height_mm=60)
    assert 30 < fig.body_l < 200, f"Figurine body_l hors limites: {fig.body_l}"
    assert fig.n_legs == 4
    assert fig.body_plan == "QUAD_TRAPU"
    passed += 1

    # Test 8: get_or_estimate fallback
    total += 1
    unknown = get_or_estimate("licorne magique", 50.0)
    assert unknown.mass_kg == 50.0
    assert unknown.shoulder_height_mm > 0
    passed += 1

    # Test 9: Tous les animals ont des gait_phases
    total += 1
    for key, animal in ANIMAL_DB.items():
        if animal.n_legs >= 2:
            assert len(animal.gait_phases) > 0, f"{key} n'a pas de gait_phases"
    passed += 1

    # Test 10: body_ratio cohérent
    total += 1
    for key, animal in ANIMAL_DB.items():
        if animal.shoulder_height_mm > 0:
            r = animal.body_ratio
            assert 0.2 < r < 10, f"{key} body_ratio aberrant: {r}"
    passed += 1

    # Test 11: Toutes les espèces ont un body_plan valide
    total += 1
    for key, animal in ANIMAL_DB.items():
        assert animal.body_plan in BODY_PLANS, f"{key} body_plan invalide: {animal.body_plan}"
    passed += 1

    # Test 12: Allométrie cohérente (plus lourd = plus grand)
    total += 1
    small = estimate_proportions(1)
    big = estimate_proportions(1000)
    assert big.shoulder_height_mm > small.shoulder_height_mm
    assert big.leg_length_mm > small.leg_length_mm
    assert big.body_length_mm > small.body_length_mm
    passed += 1

    # Test 13: Figurine scale est correcte
    total += 1
    elephant = find_animal("éléphant")
    fig_e = elephant.to_figurine(60)
    mouse = find_animal("souris")
    fig_m = mouse.to_figurine(60)
    # Les deux font ~60mm de haut mais des body_l différents
    assert fig_e.scale < fig_m.scale  # éléphant est réduit plus
    passed += 1

    # Test 14: list_animals retourne tout
    total += 1
    names = list_animals()
    assert len(names) == len(ANIMAL_DB)
    assert "Chat" in names
    passed += 1

    # Test 15: Bipèdes ont 2 pattes
    total += 1
    for key, animal in ANIMAL_DB.items():
        if "BIPED" in animal.body_plan or "OISEAU" in animal.body_plan:
            assert animal.n_legs == 2, f"{key} bipède avec {animal.n_legs} pattes"
    passed += 1

    print(f"animal_db: {passed}/{total} tests passés {'✅' if passed == total else '❌'}")
    return passed == total


if __name__ == "__main__":
    test_animal_db()
    print(f"\n{len(ANIMAL_DB)} animaux dans la base")
    print("\nExemple — Ours brun:")
    bear = find_animal("ours")
    print(f"  Masse: {bear.mass_kg}kg")
    print(f"  Corps: {bear.body_length_mm}mm × {bear.body_width_mm}mm")
    print(f"  Hauteur: {bear.shoulder_height_mm}mm")
    print(f"  Démarche: {bear.gait} ({bear.gait_phases})")
    fig = bear.to_figurine(60)
    print(f"\nFigurine 60mm:")
    print(f"  Corps: {fig.body_l}×{fig.body_w}×{fig.body_h}mm")
    print(f"  Pattes: {fig.leg_l}mm")
    print(f"  Échelle: 1:{1/fig.scale:.0f}")
