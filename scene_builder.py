"""
scene_builder.py — Génère une AutomataScene à partir d'un nom d'animal
========================================================================
Tu dis "ours" → tu récupères une scène complète avec les cames,
les pattes, la tête, la queue, les phases de marche, tout.

Usage:
    from scene_builder import make_automaton
    scene = make_automaton("ours")
    # Puis: gen = AutomataGenerator(scene); result = gen.generate()
"""
import math
from typing import Optional
from animal_db import (
    find_animal, get_or_estimate, AnimalData, FigurineProportions,
    BODY_PLANS, GAIT_PHASES
)

# On importe les classes du moteur principal
import automata_unified_v4 as au

# ════════════════════════════════════════════════════════════════
#  §1 — TEMPLATES DE MOUVEMENT PAR BODY PLAN
# ════════════════════════════════════════════════════════════════

# Amplitudes max pour FDM (mm) — au-delà, les cames deviennent trop grosses
MAX_LEG_AMP = 12.0      # balayage de patte
MAX_ARM_AMP = 10.0      # balayage de bras/aile
MAX_HEAD_AMP = 8.0       # hochement de tête
MAX_TAIL_AMP = 6.0       # queue
MAX_WING_AMP = 15.0      # battement d'aile


def _clamp_amp(val: float, max_val: float) -> float:
    """Clamp une amplitude pour rester réaliste en FDM."""
    return min(abs(val), max_val)


def _phase_to_deg(phase_01: float) -> float:
    """Convertit une phase 0.0-1.0 en degrés 0-360."""
    return phase_01 * 360.0


# ════════════════════════════════════════════════════════════════
#  §2 — CONSTRUCTEUR PRINCIPAL
# ════════════════════════════════════════════════════════════════

def make_automaton(
    animal_query: str,
    target_height_mm: float = 60.0,
    style: au.MotionStyle = au.MotionStyle.FLUID,
    rpm: float = 2.0,
    fallback_mass_kg: float = 10.0,
) -> au.AutomataScene:
    """
    Crée une AutomataScene complète à partir d'un nom d'animal.

    Args:
        animal_query: nom FR, EN, ou scientifique ("ours", "cat", "Felis catus")
        target_height_mm: hauteur de la figurine en mm (défaut: 60mm)
        style: style de mouvement (FLUID, MECHANICAL, ORGANIC)
        rpm: vitesse de rotation en tours/min
        fallback_mass_kg: masse par défaut si animal inconnu

    Returns:
        AutomataScene prête pour AutomataGenerator.generate()

    >>> scene = make_automaton("chat")
    >>> scene.name
    'Chat'
    >>> len(scene.tracks) > 0
    True
    """
    # 1. Récupérer les données animales
    animal = get_or_estimate(animal_query, fallback_mass_kg)
    fig = animal.to_figurine(target_height_mm)

    # 2. Router vers le bon template
    plan = animal.body_plan
    if plan in ("QUAD_TRAPU", "QUAD_GRACE", "QUAD_EQUIN", "QUAD_FELIN", "QUAD_CANIN", "QUAD_PETIT"):
        return _build_quadruped(animal, fig, style, rpm)
    elif plan == "BIPED_HUMAIN":
        return _build_biped_human(animal, fig, style, rpm)
    elif plan == "BIPED_OISEAU":
        return _build_biped_bird(animal, fig, style, rpm)
    elif plan == "OISEAU_VOL":
        return _build_flying_bird(animal, fig, style, rpm)
    elif plan == "SERPENT":
        return _build_snake(animal, fig, style, rpm)
    elif plan == "INSECTE":
        return _build_insect(animal, fig, style, rpm)
    else:
        # Fallback: quadrupède générique
        return _build_quadruped(animal, fig, style, rpm)


# ════════════════════════════════════════════════════════════════
#  §3 — TEMPLATES
# ════════════════════════════════════════════════════════════════

def _build_quadruped(animal: AnimalData, fig: FigurineProportions,
                     style: au.MotionStyle, rpm: float) -> au.AutomataScene:
    """
    Quadrupède: corps + 4 pattes + tête + queue optionnelle.
    Pattes en phase selon le gait de l'animal.
    """
    law = au.STYLE_TO_LAW[style]
    bl, bw, bh = fig.body_l, fig.body_w, max(fig.body_h, 15)
    ll = max(fig.leg_l, 10)
    hl = max(fig.head_l, 8)

    scene = au.AutomataScene(
        name=animal.name_fr,
        description=f"{animal.name_en} — {animal.gait}",
        style=style, cycle_rpm=rpm
    )

    # Links
    leg_w = max(bw * 0.15, 4)
    leg_t = max(leg_w * 0.8, 3)
    scene.links = [
        au.Link("body", bl, bw, bh * 0.4, bh * 0.3),
        au.Link("head", hl, hl * 0.6, hl * 0.5, hl * 0.2),
        au.Link("leg_fl", ll, leg_w, leg_t, leg_t * 0.5),  # front left
        au.Link("leg_fr", ll, leg_w, leg_t, leg_t * 0.5),  # front right
        au.Link("leg_hl", ll, leg_w, leg_t, leg_t * 0.5),  # hind left
        au.Link("leg_hr", ll, leg_w, leg_t, leg_t * 0.5),  # hind right
    ]
    if fig.tail_l > 5:
        scene.links.append(au.Link("tail", fig.tail_l, 3, 3, 1))

    # Joints — positions relatives au centre du corps
    half_bl = bl / 2
    half_bw = bw / 2
    body_top = bh * 0.4

    scene.joints = [
        au.Joint("neck", "revolute", (1, 0, 0),
                 (0, half_bl - 2, body_top), "body", "head", (-15, 20)),
        au.Joint("hip_fl", "revolute", (1, 0, 0),
                 (-half_bw * 0.6, half_bl * 0.6, 0), "body", "leg_fl", (-25, 25)),
        au.Joint("hip_fr", "revolute", (1, 0, 0),
                 (half_bw * 0.6, half_bl * 0.6, 0), "body", "leg_fr", (-25, 25)),
        au.Joint("hip_hl", "revolute", (1, 0, 0),
                 (-half_bw * 0.6, -half_bl * 0.4, 0), "body", "leg_hl", (-25, 25)),
        au.Joint("hip_hr", "revolute", (1, 0, 0),
                 (half_bw * 0.6, -half_bl * 0.4, 0), "body", "leg_hr", (-25, 25)),
    ]
    if fig.tail_l > 5:
        scene.joints.append(
            au.Joint("tail_base", "revolute", (0, 1, 0),
                     (0, -half_bl, body_top * 0.5), "body", "tail", (-10, 10)))

    # Tracks — amplitudes et phases depuis les données réelles
    leg_amp = _clamp_amp(ll * 0.15, MAX_LEG_AMP)  # 15% de la longueur de patte
    head_amp = _clamp_amp(hl * 0.2, MAX_HEAD_AMP)
    tail_amp = _clamp_amp(fig.tail_l * 0.1, MAX_TAIL_AMP)

    phases = fig.gait_phases
    lh_phase = _phase_to_deg(phases.get("LH", 0.0))
    lf_phase = _phase_to_deg(phases.get("LF", 0.25))
    rh_phase = _phase_to_deg(phases.get("RH", 0.5))
    rf_phase = _phase_to_deg(phases.get("RF", 0.75))

    scene.tracks = [
        # 4 pattes avec phases de marche
        au.MotionTrack("hip_fl", phase_offset_deg=lf_phase, primitives=[
            au.MotionPrimitive("WAVE", leg_amp, 360, law)]),
        au.MotionTrack("hip_fr", phase_offset_deg=rf_phase, primitives=[
            au.MotionPrimitive("WAVE", leg_amp, 360, law)]),
        au.MotionTrack("hip_hl", phase_offset_deg=lh_phase, primitives=[
            au.MotionPrimitive("WAVE", leg_amp, 360, law)]),
        au.MotionTrack("hip_hr", phase_offset_deg=rh_phase, primitives=[
            au.MotionPrimitive("WAVE", leg_amp, 360, law)]),
        # Tête qui hoche (fréquence double)
        au.MotionTrack("neck", frequency_multiplier=2, phase_offset_deg=0, primitives=[
            au.MotionPrimitive("LIFT", head_amp, 100, law, 1),
            au.MotionPrimitive("LIFT", head_amp, 60, law, -1),
            au.MotionPrimitive("PAUSE", beta=20)]),
    ]
    if fig.tail_l > 5:
        scene.tracks.append(
            au.MotionTrack("tail_base", frequency_multiplier=2, phase_offset_deg=90, primitives=[
                au.MotionPrimitive("WAVE", tail_amp, 180, law)]))

    scene._preset_name = f"auto_{animal.name_en.lower().replace(' ', '_')}"
    return scene


def _build_biped_human(animal: AnimalData, fig: FigurineProportions,
                       style: au.MotionStyle, rpm: float) -> au.AutomataScene:
    """Bipède humanoïde: torse + 2 jambes + 2 bras alternés."""
    law = au.STYLE_TO_LAW[style]
    bl = max(fig.body_l, 15)
    bw = max(fig.body_w, 10)

    scene = au.AutomataScene(
        name=animal.name_fr, description=f"{animal.name_en} — walk",
        style=style, cycle_rpm=rpm)

    leg_l = max(fig.leg_l, 15)
    arm_l = leg_l * 0.8

    scene.links = [
        au.Link("torso", bl, bw, bl * 0.4, bl * 0.3),
        au.Link("leg_left", leg_l, 10, 8, 8),
        au.Link("leg_right", leg_l, 10, 8, 8),
        au.Link("arm_left", arm_l, 8, 5, 4),
        au.Link("arm_right", arm_l, 8, 5, 4),
    ]

    scene.joints = [
        au.Joint("hip_left", "revolute", (1, 0, 0), (-bw * 0.3, 0, 0),
                 "torso", "leg_left", (-25, 25)),
        au.Joint("hip_right", "revolute", (1, 0, 0), (bw * 0.3, 0, 0),
                 "torso", "leg_right", (-25, 25)),
        au.Joint("shoulder_left", "revolute", (1, 0, 0), (-bw * 0.4, 0, bl * 0.8),
                 "torso", "arm_left", (-20, 20)),
        au.Joint("shoulder_right", "revolute", (1, 0, 0), (bw * 0.4, 0, bl * 0.8),
                 "torso", "arm_right", (-20, 20)),
    ]

    leg_amp = _clamp_amp(10, MAX_LEG_AMP)
    arm_amp = _clamp_amp(8, MAX_ARM_AMP)

    scene.tracks = [
        au.MotionTrack("hip_left", phase_offset_deg=0, primitives=[
            au.MotionPrimitive("WAVE", leg_amp, 360, law)]),
        au.MotionTrack("hip_right", phase_offset_deg=180, primitives=[
            au.MotionPrimitive("WAVE", leg_amp, 360, law)]),
        au.MotionTrack("shoulder_left", phase_offset_deg=180, primitives=[
            au.MotionPrimitive("WAVE", arm_amp, 360, law)]),
        au.MotionTrack("shoulder_right", phase_offset_deg=0, primitives=[
            au.MotionPrimitive("WAVE", arm_amp, 360, law)]),
    ]
    scene._preset_name = f"auto_{animal.name_en.lower().replace(' ', '_')}"
    return scene


def _build_biped_bird(animal: AnimalData, fig: FigurineProportions,
                      style: au.MotionStyle, rpm: float) -> au.AutomataScene:
    """Oiseau bipède (pingouin, poule): corps + 2 pattes + tête bob."""
    law = au.STYLE_TO_LAW[style]
    bl = max(fig.body_l, 15)
    bw = max(fig.body_w, 10)

    scene = au.AutomataScene(
        name=animal.name_fr, description=f"{animal.name_en} — waddle",
        style=style, cycle_rpm=rpm)

    scene.links = [
        au.Link("body", bl, bw, bl * 0.4, bl * 0.3),
        au.Link("head", fig.head_l, fig.head_l * 0.7, fig.head_l * 0.5, 3),
        au.Link("leg_left", fig.leg_l, 6, 5, 3),
        au.Link("leg_right", fig.leg_l, 6, 5, 3),
    ]

    scene.joints = [
        au.Joint("neck", "revolute", (1, 0, 0), (0, bl * 0.3, bl * 0.6),
                 "body", "head", (-10, 15)),
        au.Joint("hip_left", "revolute", (1, 0, 0), (-bw * 0.3, 0, 0),
                 "body", "leg_left", (-20, 20)),
        au.Joint("hip_right", "revolute", (1, 0, 0), (bw * 0.3, 0, 0),
                 "body", "leg_right", (-20, 20)),
    ]

    leg_amp = _clamp_amp(8, MAX_LEG_AMP)
    head_amp = _clamp_amp(5, MAX_HEAD_AMP)

    scene.tracks = [
        au.MotionTrack("hip_left", phase_offset_deg=0, primitives=[
            au.MotionPrimitive("WAVE", leg_amp, 360, law)]),
        au.MotionTrack("hip_right", phase_offset_deg=180, primitives=[
            au.MotionPrimitive("WAVE", leg_amp, 360, law)]),
        au.MotionTrack("neck", frequency_multiplier=2, primitives=[
            au.MotionPrimitive("LIFT", head_amp, 100, law, 1),
            au.MotionPrimitive("LIFT", head_amp, 60, law, -1),
            au.MotionPrimitive("PAUSE", beta=20)]),
    ]
    scene._preset_name = f"auto_{animal.name_en.lower().replace(' ', '_')}"
    return scene


def _build_flying_bird(animal: AnimalData, fig: FigurineProportions,
                       style: au.MotionStyle, rpm: float) -> au.AutomataScene:
    """Oiseau volant: corps + 2 ailes battantes + tête."""
    law = au.STYLE_TO_LAW[style]
    bl = max(fig.body_l, 15)
    bw = max(fig.body_w, 10)
    wing_l = max(bl * 0.7, 20)

    scene = au.AutomataScene(
        name=animal.name_fr, description=f"{animal.name_en} — flap",
        style=style, cycle_rpm=min(rpm, 1.5))

    scene.links = [
        au.Link("body", bl, bw, bl * 0.35, bl * 0.3),
        au.Link("head", fig.head_l, fig.head_l * 0.6, fig.head_l * 0.5, 3),
        au.Link("wing_left", wing_l, wing_l * 0.4, 3, 4),
        au.Link("wing_right", wing_l, wing_l * 0.4, 3, 4),
    ]

    scene.joints = [
        au.Joint("neck", "revolute", (1, 0, 0), (0, bl * 0.35, bl * 0.4),
                 "body", "head", (-10, 20)),
        au.Joint("shoulder_left", "revolute", (0, 1, 0), (-bw * 0.4, 0, bl * 0.3),
                 "body", "wing_left", (-30, 60)),
        au.Joint("shoulder_right", "revolute", (0, 1, 0), (bw * 0.4, 0, bl * 0.3),
                 "body", "wing_right", (-30, 60)),
    ]

    wing_amp = _clamp_amp(15, MAX_WING_AMP)
    head_amp = _clamp_amp(5, MAX_HEAD_AMP)

    wing_prims = [
        au.MotionPrimitive("LIFT", wing_amp, 200, law, 1),
        au.MotionPrimitive("LIFT", wing_amp, 120, law, -1),
        au.MotionPrimitive("PAUSE", beta=40),
    ]

    scene.tracks = [
        au.MotionTrack("shoulder_left", primitives=list(wing_prims)),
        au.MotionTrack("shoulder_right", primitives=[
            au.MotionPrimitive(p.kind, p.amplitude, p.beta, p.law, p.direction)
            for p in wing_prims]),
        au.MotionTrack("neck", frequency_multiplier=2, phase_offset_deg=30, primitives=[
            au.MotionPrimitive("LIFT", head_amp, 100, law, 1),
            au.MotionPrimitive("LIFT", head_amp, 60, law, -1),
            au.MotionPrimitive("PAUSE", beta=20)]),
    ]
    scene._preset_name = f"auto_{animal.name_en.lower().replace(' ', '_')}"
    return scene


def _build_snake(animal: AnimalData, fig: FigurineProportions,
                 style: au.MotionStyle, rpm: float) -> au.AutomataScene:
    """Serpent: 3 segments ondulants en phase."""
    law = au.STYLE_TO_LAW[style]
    seg_l = max(fig.body_l / 3, 15)

    scene = au.AutomataScene(
        name=animal.name_fr, description=f"{animal.name_en} — slither",
        style=style, cycle_rpm=rpm)

    scene.links = [
        au.Link("seg1", seg_l, 8, 6, 4),
        au.Link("seg2", seg_l, 7, 5, 3),
        au.Link("seg3", seg_l, 6, 4, 2),
    ]
    scene.joints = [
        au.Joint("j1", "revolute", (0, 0, 1), (0, seg_l * 0.9, 0),
                 "seg1", "seg2", (-15, 15)),
        au.Joint("j2", "revolute", (0, 0, 1), (0, seg_l * 0.9, 0),
                 "seg2", "seg3", (-15, 15)),
    ]

    amp = _clamp_amp(6, MAX_TAIL_AMP)
    scene.tracks = [
        au.MotionTrack("j1", phase_offset_deg=0, primitives=[
            au.MotionPrimitive("WAVE", amp, 360, law)]),
        au.MotionTrack("j2", phase_offset_deg=120, primitives=[
            au.MotionPrimitive("WAVE", amp, 360, law)]),
    ]
    scene._preset_name = f"auto_{animal.name_en.lower().replace(' ', '_')}"
    return scene


def _build_insect(animal: AnimalData, fig: FigurineProportions,
                  style: au.MotionStyle, rpm: float) -> au.AutomataScene:
    """Insecte simplifié: corps + 2 groupes de 3 pattes (tripod gait)."""
    law = au.STYLE_TO_LAW[style]
    bl = max(fig.body_l, 15)
    bw = max(fig.body_w, 8)

    scene = au.AutomataScene(
        name=animal.name_fr, description=f"{animal.name_en} — tripod",
        style=style, cycle_rpm=rpm)

    # Simplifié: 2 "groupes" de pattes (tripod = L1+R2+L3 vs R1+L2+R3)
    scene.links = [
        au.Link("body", bl, bw, bl * 0.3, bl * 0.2),
        au.Link("legs_group_a", bl * 0.5, bw * 0.8, 3, 2),  # L1+R2+L3
        au.Link("legs_group_b", bl * 0.5, bw * 0.8, 3, 2),  # R1+L2+R3
    ]
    scene.joints = [
        au.Joint("tripod_a", "revolute", (1, 0, 0), (-bw * 0.3, 0, 0),
                 "body", "legs_group_a", (-15, 15)),
        au.Joint("tripod_b", "revolute", (1, 0, 0), (bw * 0.3, 0, 0),
                 "body", "legs_group_b", (-15, 15)),
    ]

    amp = _clamp_amp(5, MAX_LEG_AMP)
    scene.tracks = [
        au.MotionTrack("tripod_a", phase_offset_deg=0, primitives=[
            au.MotionPrimitive("WAVE", amp, 360, law)]),
        au.MotionTrack("tripod_b", phase_offset_deg=180, primitives=[
            au.MotionPrimitive("WAVE", amp, 360, law)]),
    ]
    scene._preset_name = f"auto_{animal.name_en.lower().replace(' ', '_')}"
    return scene


# ════════════════════════════════════════════════════════════════
#  §4 — TESTS
# ════════════════════════════════════════════════════════════════

def test_scene_builder():
    """Tests du constructeur de scènes."""
    passed = 0
    total = 0

    # Test 1: Quadrupède (chat)
    total += 1
    scene = make_automaton("chat")
    assert scene.name == "Chat", f"Nom: {scene.name}"
    errors = scene.validate()
    assert not errors, f"Validation chat: {errors}"
    passed += 1

    # Test 2: Ours (quadrupède trapu)
    total += 1
    scene = make_automaton("ours brun")
    assert len(scene.tracks) >= 5, f"Tracks ours: {len(scene.tracks)}"
    assert any("hip" in t.name for t in scene.tracks)
    errors = scene.validate()
    assert not errors, f"Validation ours: {errors}"
    passed += 1

    # Test 3: Cheval (quadrupède équin)
    total += 1
    scene = make_automaton("cheval")
    assert "QUAD_EQUIN" in scene.description or "trot" in scene.description
    errors = scene.validate()
    assert not errors, f"Validation cheval: {errors}"
    passed += 1

    # Test 4: Humain (bipède)
    total += 1
    scene = make_automaton("humain")
    assert len([t for t in scene.tracks if "hip" in t.name]) == 2
    assert len([t for t in scene.tracks if "shoulder" in t.name]) == 2
    errors = scene.validate()
    assert not errors, f"Validation humain: {errors}"
    passed += 1

    # Test 5: Pigeon (oiseau volant)
    total += 1
    scene = make_automaton("pigeon")
    assert any("shoulder" in t.name or "wing" in t.name for t in scene.tracks)
    errors = scene.validate()
    assert not errors, f"Validation pigeon: {errors}"
    passed += 1

    # Test 6: Serpent
    total += 1
    scene = make_automaton("serpent")
    assert len(scene.links) == 3  # 3 segments
    errors = scene.validate()
    assert not errors, f"Validation serpent: {errors}"
    passed += 1

    # Test 7: Fourmi (insecte)
    total += 1
    scene = make_automaton("fourmi")
    assert "tripod" in scene.description
    errors = scene.validate()
    assert not errors, f"Validation fourmi: {errors}"
    passed += 1

    # Test 8: Pingouin (bipède oiseau)
    total += 1
    scene = make_automaton("pingouin")
    assert len([t for t in scene.tracks if "hip" in t.name]) == 2
    errors = scene.validate()
    assert not errors, f"Validation pingouin: {errors}"
    passed += 1

    # Test 9: Animal inconnu → fallback
    total += 1
    scene = make_automaton("licorne", fallback_mass_kg=30)
    assert scene is not None
    assert len(scene.tracks) > 0
    errors = scene.validate()
    assert not errors, f"Validation licorne: {errors}"
    passed += 1

    # Test 10: Toutes les espèces de la DB passent la validation
    total += 1
    from animal_db import ANIMAL_DB
    all_ok = True
    for key, animal in ANIMAL_DB.items():
        try:
            s = make_automaton(animal.name_en)
            errs = s.validate()
            if errs:
                print(f"  ❌ {key}: {errs}")
                all_ok = False
        except Exception as ex:
            print(f"  ❌ {key}: CRASH — {ex}")
            all_ok = False
    assert all_ok, "Certains animaux échouent"
    passed += 1

    # Test 11: Phases de marche correctes pour l'ours (pace = latéral)
    total += 1
    scene = make_automaton("ours brun")
    fl_track = [t for t in scene.tracks if t.name == "hip_fl"][0]
    fr_track = [t for t in scene.tracks if t.name == "hip_fr"][0]
    hl_track = [t for t in scene.tracks if t.name == "hip_hl"][0]
    hr_track = [t for t in scene.tracks if t.name == "hip_hr"][0]
    # Pace = pattes du même côté bougent ensemble
    # LH et LF en phase, RH et RF en phase
    assert fl_track.phase_offset_deg == hl_track.phase_offset_deg, \
        f"Pace: FL={fl_track.phase_offset_deg} != HL={hl_track.phase_offset_deg}"
    passed += 1

    # Test 12: Amplitude des pattes raisonnable (< 15mm)
    total += 1
    for key, animal in ANIMAL_DB.items():
        s = make_automaton(animal.name_en)
        for t in s.tracks:
            for p in t.primitives:
                if p.kind != "PAUSE":
                    assert p.amplitude <= 15, f"{key}/{t.name}: amp={p.amplitude}mm trop grande"
    passed += 1

    print(f"scene_builder: {passed}/{total} tests passés {'✅' if passed == total else '❌'}")
    return passed == total


if __name__ == "__main__":
    test_scene_builder()

    print("\n─── Exemple: make_automaton('ours') ───")
    scene = make_automaton("ours")
    print(f"Nom: {scene.name}")
    print(f"Tracks: {len(scene.tracks)}")
    for t in scene.tracks:
        phases = f" phase={t.phase_offset_deg}°" if t.phase_offset_deg else ""
        amps = "/".join(f"{p.amplitude}mm" for p in t.primitives if p.kind != "PAUSE")
        print(f"  {t.name}: {amps}{phases}")
