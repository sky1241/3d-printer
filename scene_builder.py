"""
scene_builder.py v2 — Genere une AutomataScene a partir d un nom d etre vivant
=============================================================================
Utilise living_beings_db (118 especes, 42 body plans).
"""
import math
from typing import Optional
from living_beings_db import (
    find_species, get_body_plan, Species, BodyPlan, BODY_PLANS, SPECIES_DB
)
try:
    from animal_db import find_animal, get_or_estimate, AnimalData
    _HAS_OLD_DB = True
except ImportError:
    _HAS_OLD_DB = False

import automata_unified_v4 as au

MAX_LEG_AMP = 12.0
MAX_ARM_AMP = 10.0
MAX_HEAD_AMP = 8.0
MAX_TAIL_AMP = 6.0
MAX_WING_AMP = 15.0
MAX_JAW_AMP = 8.0
MAX_BODY_WAVE_AMP = 6.0
MAX_TENTACLE_AMP = 8.0
MIN_DIM = 4.0

def _clamp(val, lo, hi):
    return max(lo, min(val, hi))

def _phase_deg(phase_01):
    return phase_01 * 360.0

class FigDims:
    def __init__(self, sp, bp, target_h=60.0):
        real_total_h = sp.body_length_mm * (bp.body_height_ratio + bp.leg_ratio)
        if real_total_h <= 0:
            real_total_h = sp.body_length_mm if sp.body_length_mm > 0 else 100
        self.scale = target_h / real_total_h
        bl = max(sp.body_length_mm * self.scale, MIN_DIM * 3)
        self.body_l = bl
        self.body_w = max(bl * bp.body_width_ratio, MIN_DIM)
        self.body_h = max(bl * bp.body_height_ratio, MIN_DIM)
        self.head_l = max(bl * bp.head_ratio, MIN_DIM)
        self.leg_l = max(bl * bp.leg_ratio, MIN_DIM) if bp.n_legs > 0 else 0
        self.tail_l = bl * bp.tail_ratio if bp.has_tail else 0
        self.wing_l = max(bl * bp.wing_ratio, MIN_DIM) if bp.n_wings > 0 else 0
        self.arm_l = max(bl * bp.arm_ratio, MIN_DIM) if bp.n_arms > 0 else 0
        self.n_legs = bp.n_legs
        self.n_wings = bp.n_wings
        self.n_arms = bp.n_arms
        self.has_tail = bp.has_tail
        self.gait_phases = bp.gait_phases
        self.movable_parts = bp.movable_parts
        self.total_height = target_h

def _gait_name(fig):
    ph = fig.gait_phases
    if not ph: return "idle"
    if "L1" in ph: return "tripod"
    if "L_all" in ph: return "lateral"
    if "LW" in ph: return "flap"
    lh = ph.get("LH", 0); lf = ph.get("LF", 0.25); rh = ph.get("RH", 0.5)
    if abs(lh - lf) < 0.01 and abs(rh - ph.get("RF", 0.5)) < 0.01: return "pace"
    if abs(lh - ph.get("RF", 0)) < 0.01: return "trot"
    return "walk"

def make_automaton(query, target_height_mm=60.0, style=au.MotionStyle.FLUID, rpm=2.0, fallback_mass_kg=10.0, drive_mode='crank'):
    sp = find_species(query)
    bp = get_body_plan(query) if sp else None
    if sp and bp:
        fig = FigDims(sp, bp, target_height_mm)
        scene = _route(sp, bp, fig, style, rpm)
        # Attach figurine config from body plan → FigurineBuilder will generate 3D meshes
        scene._figurine_cfg = bodyplan_to_figurine_cfg(sp, bp, target_height_mm, drive_mode)
        scene._drive_mode = drive_mode
        return scene
    if _HAS_OLD_DB:
        animal = get_or_estimate(query, fallback_mass_kg)
        old_fig = animal.to_figurine(target_height_mm)
        plan = animal.body_plan
        if plan in ("QUAD_TRAPU","QUAD_GRACE","QUAD_EQUIN","QUAD_FELIN","QUAD_CANIN","QUAD_PETIT"):
            return _wrap_old_quad(animal, old_fig, style, rpm)
        elif plan == "BIPED_HUMAIN":
            return _wrap_old_biped(animal, old_fig, style, rpm)
        elif plan == "BIPED_OISEAU":
            return _wrap_old_biped_bird(animal, old_fig, style, rpm)
        elif plan == "OISEAU_VOL":
            return _wrap_old_flapper(animal, old_fig, style, rpm)
        elif plan == "SERPENT":
            return _wrap_old_snake(animal, old_fig, style, rpm)
        elif plan == "INSECTE":
            return _wrap_old_insect(animal, old_fig, style, rpm)
    dummy_sp = Species(query.title(), query.title(), "", "MAM_FELIN", fallback_mass_kg, 500)
    dummy_bp = BODY_PLANS["MAM_FELIN"]
    fig = FigDims(dummy_sp, dummy_bp, target_height_mm)
    return _build_quadruped(query.title(), query.title(), fig, style, rpm)

def _route(sp, bp, fig, style, rpm):
    bid = bp.id
    nfr, nen = sp.name_fr, sp.name_en
    if bid in ("MAM_TRAPU","MAM_GRACE","MAM_FELIN","MAM_CANIN","MAM_PETIT"):
        return _build_quadruped(nfr, nen, fig, style, rpm)
    if bid == "MAM_PRIMATE":
        return _build_quadruped(nfr, nen, fig, style, rpm)
    if bid == "MAM_MARIN":
        return _build_swimmer(nfr, nen, fig, style, rpm)
    if bid == "MAM_CHAUVE":
        return _build_flapper(nfr, nen, fig, style, rpm)
    if bid in ("AV_VOL","AV_RAPACE","AV_PETIT"):
        return _build_flapper(nfr, nen, fig, style, rpm)
    if bid in ("AV_COUREUR","AV_NAGEUR"):
        return _build_biped(nfr, nen, fig, style, rpm)
    if bid in ("REP_LEZARD","REP_CROCO","REP_TORTUE","REP_DINO_Q","AMP_GREN","AMP_SALA"):
        return _build_quadruped(nfr, nen, fig, style, rpm)
    if bid == "REP_SERPENT":
        return _build_snake(nfr, nen, fig, style, rpm)
    if bid == "REP_DINO_B":
        return _build_dino_biped(nfr, nen, fig, style, rpm)
    if bid in ("FISH_STD","FISH_PLAT"):
        return _build_swimmer(nfr, nen, fig, style, rpm)
    if bid in ("INS_MARCH","INS_SAUT","INS_MANTE"):
        return _build_insect_6leg(nfr, nen, fig, style, rpm)
    if bid == "INS_VOL":
        return _build_insect_flying(nfr, nen, fig, style, rpm)
    if bid == "ARA_ARAIGN":
        return _build_arachnid(nfr, nen, fig, style, rpm)
    if bid == "ARA_SCORP":
        return _build_scorpion(nfr, nen, fig, style, rpm)
    if bid == "CRU_CRABE":
        return _build_crab(nfr, nen, fig, style, rpm)
    if bid == "CRU_HOMARD":
        return _build_lobster(nfr, nen, fig, style, rpm)
    if bid in ("MYR_CENTI","MYR_MILLI"):
        return _build_myriapod(nfr, nen, fig, style, rpm)
    if bid == "MOL_ESCARG":
        return _build_snail(nfr, nen, fig, style, rpm)
    if bid == "MOL_PIEUVRE":
        return _build_octopus(nfr, nen, fig, style, rpm)
    if bid in ("PL_FLEUR","PL_CARNIV","FU_CHAMP"):
        return _build_plant(nfr, nen, fig, style, rpm)
    if bid == "FAN_DRAGON":
        return _build_dragon(nfr, nen, fig, style, rpm)
    if bid == "FAN_LICORN":
        return _build_quadruped(nfr, nen, fig, style, rpm)
    if bid == "FAN_PHOENIX":
        return _build_flapper(nfr, nen, fig, style, rpm)
    if bid == "FAN_ROBOT":
        return _build_biped(nfr, nen, fig, style, rpm)
    return _build_quadruped(nfr, nen, fig, style, rpm)

# ═══════ TEMPLATES ═══════

def _build_quadruped(nfr, nen, fig, style, rpm):
    law = au.STYLE_TO_LAW[style]
    bl, bw, bh = fig.body_l, fig.body_w, max(fig.body_h, 15)
    ll = max(fig.leg_l, 10)
    hl = max(fig.head_l, 8)
    scene = au.AutomataScene(name=nfr, description=f"{nen} — {_gait_name(fig)}", style=style, cycle_rpm=rpm)
    lw = max(bw * 0.15, MIN_DIM)
    lt = max(lw * 0.8, 3)
    scene.links = [
        au.Link("body", bl, bw, bh*0.4, bh*0.3),
        au.Link("head", hl, hl*0.6, hl*0.5, hl*0.2),
        au.Link("leg_fl", ll, lw, lt, lt*0.5),
        au.Link("leg_fr", ll, lw, lt, lt*0.5),
        au.Link("leg_hl", ll, lw, lt, lt*0.5),
        au.Link("leg_hr", ll, lw, lt, lt*0.5),
    ]
    if fig.tail_l > 5:
        scene.links.append(au.Link("tail", fig.tail_l, 3, 3, 1))
    hbl = bl/2; hbw = bw/2; bt = bh*0.4
    scene.joints = [
        au.Joint("neck", "revolute", (1,0,0), (0, hbl-2, bt), "body", "head", (-15,20)),
        au.Joint("hip_fl", "revolute", (1,0,0), (-hbw*0.6, hbl*0.6, 0), "body", "leg_fl", (-25,25)),
        au.Joint("hip_fr", "revolute", (1,0,0), (hbw*0.6, hbl*0.6, 0), "body", "leg_fr", (-25,25)),
        au.Joint("hip_hl", "revolute", (1,0,0), (-hbw*0.6, -hbl*0.4, 0), "body", "leg_hl", (-25,25)),
        au.Joint("hip_hr", "revolute", (1,0,0), (hbw*0.6, -hbl*0.4, 0), "body", "leg_hr", (-25,25)),
    ]
    if fig.tail_l > 5:
        scene.joints.append(au.Joint("tail_base", "revolute", (0,1,0), (0, -hbl, bt*0.5), "body", "tail", (-10,10)))
    la = _clamp(ll*0.15, 2, MAX_LEG_AMP)
    ha = _clamp(hl*0.2, 2, MAX_HEAD_AMP)
    ta = _clamp(fig.tail_l*0.1, 1, MAX_TAIL_AMP)
    ph = fig.gait_phases
    scene.tracks = [
        au.MotionTrack("hip_fl", phase_offset_deg=_phase_deg(ph.get("LF",0.25)), primitives=[au.MotionPrimitive("WAVE", la, 360, law)]),
        au.MotionTrack("hip_fr", phase_offset_deg=_phase_deg(ph.get("RF",0.75)), primitives=[au.MotionPrimitive("WAVE", la, 360, law)]),
        au.MotionTrack("hip_hl", phase_offset_deg=_phase_deg(ph.get("LH",0.0)), primitives=[au.MotionPrimitive("WAVE", la, 360, law)]),
        au.MotionTrack("hip_hr", phase_offset_deg=_phase_deg(ph.get("RH",0.5)), primitives=[au.MotionPrimitive("WAVE", la, 360, law)]),
        au.MotionTrack("neck", frequency_multiplier=2, primitives=[
            au.MotionPrimitive("LIFT", ha, 100, law, 1), au.MotionPrimitive("LIFT", ha, 60, law, -1), au.MotionPrimitive("PAUSE", beta=20)]),
    ]
    if fig.tail_l > 5:
        scene.tracks.append(au.MotionTrack("tail_base", frequency_multiplier=2, phase_offset_deg=90, primitives=[au.MotionPrimitive("WAVE", ta, 180, law)]))
    scene._preset_name = f"auto_{nen.lower().replace(' ','_')}"
    return scene

def _build_biped(nfr, nen, fig, style, rpm):
    law = au.STYLE_TO_LAW[style]
    bl = max(fig.body_l, 15); bw = max(fig.body_w, 10); ll = max(fig.leg_l, 15)
    hl = max(fig.head_l, 8)
    scene = au.AutomataScene(name=nfr, description=f"{nen} — walk", style=style, cycle_rpm=rpm)
    scene.links = [au.Link("body", bl, bw, bl*0.4, bl*0.3), au.Link("head", hl, hl*0.7, hl*0.5, 3),
        au.Link("leg_left", ll, 8, 6, MIN_DIM), au.Link("leg_right", ll, 8, 6, MIN_DIM)]
    scene.joints = [
        au.Joint("neck", "revolute", (1,0,0), (0, bl*0.3, bl*0.6), "body", "head", (-10,15)),
        au.Joint("hip_left", "revolute", (1,0,0), (-bw*0.3, 0, 0), "body", "leg_left", (-25,25)),
        au.Joint("hip_right", "revolute", (1,0,0), (bw*0.3, 0, 0), "body", "leg_right", (-25,25))]
    if fig.n_arms > 0:
        al = max(fig.arm_l, 10)
        scene.links += [au.Link("arm_left", al, 6, 5, 3), au.Link("arm_right", al, 6, 5, 3)]
        scene.joints += [
            au.Joint("shoulder_left", "revolute", (1,0,0), (-bw*0.4, 0, bl*0.8), "body", "arm_left", (-20,20)),
            au.Joint("shoulder_right", "revolute", (1,0,0), (bw*0.4, 0, bl*0.8), "body", "arm_right", (-20,20))]
    la = _clamp(ll*0.12, 2, MAX_LEG_AMP); ha = _clamp(5, 2, MAX_HEAD_AMP)
    scene.tracks = [
        au.MotionTrack("hip_left", phase_offset_deg=0, primitives=[au.MotionPrimitive("WAVE", la, 360, law)]),
        au.MotionTrack("hip_right", phase_offset_deg=180, primitives=[au.MotionPrimitive("WAVE", la, 360, law)]),
        au.MotionTrack("neck", frequency_multiplier=2, primitives=[
            au.MotionPrimitive("LIFT", ha, 100, law, 1), au.MotionPrimitive("LIFT", ha, 60, law, -1), au.MotionPrimitive("PAUSE", beta=20)])]
    if fig.n_arms > 0:
        aa = _clamp(fig.arm_l*0.1, 2, MAX_ARM_AMP)
        scene.tracks += [
            au.MotionTrack("shoulder_left", phase_offset_deg=180, primitives=[au.MotionPrimitive("WAVE", aa, 360, law)]),
            au.MotionTrack("shoulder_right", phase_offset_deg=0, primitives=[au.MotionPrimitive("WAVE", aa, 360, law)])]
    scene._preset_name = f"auto_{nen.lower().replace(' ','_')}"; return scene

def _build_flapper(nfr, nen, fig, style, rpm):
    law = au.STYLE_TO_LAW[style]
    bl = max(fig.body_l, 15); bw = max(fig.body_w, 10); wl = max(fig.wing_l, 20); hl = max(fig.head_l, 8)
    scene = au.AutomataScene(name=nfr, description=f"{nen} — flap", style=style, cycle_rpm=min(rpm, 1.5))
    scene.links = [au.Link("body", bl, bw, bl*0.35, bl*0.3), au.Link("head", hl, hl*0.6, hl*0.5, 3),
        au.Link("wing_left", wl, wl*0.4, 3, MIN_DIM), au.Link("wing_right", wl, wl*0.4, 3, MIN_DIM)]
    if fig.has_tail and fig.tail_l > 5:
        scene.links.append(au.Link("tail", fig.tail_l, 5, 3, 2))
    scene.joints = [
        au.Joint("neck", "revolute", (1,0,0), (0, bl*0.35, bl*0.4), "body", "head", (-10,20)),
        au.Joint("shoulder_left", "revolute", (0,1,0), (-bw*0.4, 0, bl*0.3), "body", "wing_left", (-30,60)),
        au.Joint("shoulder_right", "revolute", (0,1,0), (bw*0.4, 0, bl*0.3), "body", "wing_right", (-30,60))]
    if fig.has_tail and fig.tail_l > 5:
        scene.joints.append(au.Joint("tail_base", "revolute", (0,1,0), (0, -bl*0.4, bl*0.2), "body", "tail", (-10,10)))
    wa = _clamp(wl*0.2, 3, MAX_WING_AMP); ha = _clamp(5, 2, MAX_HEAD_AMP)
    wp = [au.MotionPrimitive("LIFT", wa, 200, law, 1), au.MotionPrimitive("LIFT", wa, 120, law, -1), au.MotionPrimitive("PAUSE", beta=40)]
    scene.tracks = [
        au.MotionTrack("shoulder_left", primitives=list(wp)),
        au.MotionTrack("shoulder_right", primitives=[au.MotionPrimitive(p.kind, p.amplitude, p.beta, p.law, p.direction) for p in wp]),
        au.MotionTrack("neck", frequency_multiplier=2, phase_offset_deg=30, primitives=[
            au.MotionPrimitive("LIFT", ha, 100, law, 1), au.MotionPrimitive("LIFT", ha, 60, law, -1), au.MotionPrimitive("PAUSE", beta=20)])]
    if fig.has_tail and fig.tail_l > 5:
        scene.tracks.append(au.MotionTrack("tail_base", frequency_multiplier=2, phase_offset_deg=90, primitives=[au.MotionPrimitive("WAVE", _clamp(fig.tail_l*0.1,1,MAX_TAIL_AMP), 180, law)]))
    scene._preset_name = f"auto_{nen.lower().replace(' ','_')}"; return scene

def _build_snake(nfr, nen, fig, style, rpm):
    law = au.STYLE_TO_LAW[style]; sl = max(fig.body_l/3, 15)
    scene = au.AutomataScene(name=nfr, description=f"{nen} — slither", style=style, cycle_rpm=rpm)
    scene.links = [au.Link("seg1", sl, 8, 6, MIN_DIM), au.Link("seg2", sl, 7, 5, 3), au.Link("seg3", sl, 6, MIN_DIM, 2)]
    scene.joints = [au.Joint("j1", "revolute", (0,0,1), (0, sl*0.9, 0), "seg1", "seg2", (-15,15)),
        au.Joint("j2", "revolute", (0,0,1), (0, sl*0.9, 0), "seg2", "seg3", (-15,15))]
    a = _clamp(6, 2, MAX_BODY_WAVE_AMP)
    scene.tracks = [au.MotionTrack("j1", phase_offset_deg=0, primitives=[au.MotionPrimitive("WAVE", a, 360, law)]),
        au.MotionTrack("j2", phase_offset_deg=120, primitives=[au.MotionPrimitive("WAVE", a, 360, law)])]
    scene._preset_name = f"auto_{nen.lower().replace(' ','_')}"; return scene

def _build_swimmer(nfr, nen, fig, style, rpm):
    law = au.STYLE_TO_LAW[style]; bl = max(fig.body_l, 20); bw = max(fig.body_w, 8)
    tl = max(fig.tail_l, bl*0.25) if fig.has_tail or fig.tail_l > 0 else bl*0.25
    scene = au.AutomataScene(name=nfr, description=f"{nen} — swim", style=style, cycle_rpm=rpm)
    scene.links = [au.Link("body", bl, bw, bw*0.8, bw*0.3), au.Link("tail", tl, tl*0.6, tl*0.3, MIN_DIM)]
    scene.joints = [au.Joint("tail_joint", "revolute", (0,0,1), (0, -bl*0.4, 0), "body", "tail", (-20,20))]
    if fig.wing_l > 0:
        fl = max(fig.wing_l, 8)
        scene.links += [au.Link("fin_left", fl, fl*0.4, 2, 2), au.Link("fin_right", fl, fl*0.4, 2, 2)]
        scene.joints += [au.Joint("fin_left_j", "revolute", (1,0,0), (-bw*0.4, bl*0.1, 0), "body", "fin_left", (-15,15)),
            au.Joint("fin_right_j", "revolute", (1,0,0), (bw*0.4, bl*0.1, 0), "body", "fin_right", (-15,15))]
    ta = _clamp(tl*0.15, 2, MAX_TAIL_AMP)
    scene.tracks = [au.MotionTrack("tail_joint", primitives=[au.MotionPrimitive("WAVE", ta, 360, law)])]
    if fig.wing_l > 0:
        fa = _clamp(3, 2, MAX_ARM_AMP)
        scene.tracks += [au.MotionTrack("fin_left_j", phase_offset_deg=0, primitives=[au.MotionPrimitive("WAVE", fa, 360, law)]),
            au.MotionTrack("fin_right_j", phase_offset_deg=180, primitives=[au.MotionPrimitive("WAVE", fa, 360, law)])]
    scene._preset_name = f"auto_{nen.lower().replace(' ','_')}"; return scene

def _build_insect_6leg(nfr, nen, fig, style, rpm):
    law = au.STYLE_TO_LAW[style]; bl = max(fig.body_l, 15); bw = max(fig.body_w, 8); ll = max(fig.leg_l, 8)
    hl = max(fig.head_l, 5); lw = max(3, MIN_DIM)
    scene = au.AutomataScene(name=nfr, description=f"{nen} — tripod", style=style, cycle_rpm=rpm)
    scene.links = [au.Link("body", bl, bw, bl*0.3, bl*0.2), au.Link("head", hl, hl*0.6, hl*0.4, 3)]
    for i in range(1,4):
        scene.links += [au.Link(f"leg_L{i}", ll, lw, lw, 2), au.Link(f"leg_R{i}", ll, lw, lw, 2)]
    yp = [bl*0.3, 0, -bl*0.3]
    scene.joints = [au.Joint("neck", "revolute", (1,0,0), (0, bl*0.4, bl*0.15), "body", "head", (-10,10))]
    for i, y in enumerate(yp):
        n = i+1
        scene.joints += [au.Joint(f"hip_L{n}", "revolute", (1,0,0), (-bw*0.4, y, 0), "body", f"leg_L{n}", (-20,20)),
            au.Joint(f"hip_R{n}", "revolute", (1,0,0), (bw*0.4, y, 0), "body", f"leg_R{n}", (-20,20))]
    la = _clamp(ll*0.15, 2, MAX_LEG_AMP)
    # Tripod: L1+R2+L3=0, R1+L2+R3=180
    scene.tracks = [
        au.MotionTrack("hip_L1", phase_offset_deg=0, primitives=[au.MotionPrimitive("WAVE", la, 360, law)]),
        au.MotionTrack("hip_R1", phase_offset_deg=180, primitives=[au.MotionPrimitive("WAVE", la, 360, law)]),
        au.MotionTrack("hip_L2", phase_offset_deg=180, primitives=[au.MotionPrimitive("WAVE", la, 360, law)]),
        au.MotionTrack("hip_R2", phase_offset_deg=0, primitives=[au.MotionPrimitive("WAVE", la, 360, law)]),
        au.MotionTrack("hip_L3", phase_offset_deg=0, primitives=[au.MotionPrimitive("WAVE", la, 360, law)]),
        au.MotionTrack("hip_R3", phase_offset_deg=180, primitives=[au.MotionPrimitive("WAVE", la, 360, law)]),
        au.MotionTrack("neck", frequency_multiplier=2, primitives=[
            au.MotionPrimitive("LIFT", 3, 100, law, 1), au.MotionPrimitive("LIFT", 3, 60, law, -1), au.MotionPrimitive("PAUSE", beta=20)])]
    scene._preset_name = f"auto_{nen.lower().replace(' ','_')}"; return scene

def _build_insect_flying(nfr, nen, fig, style, rpm):
    law = au.STYLE_TO_LAW[style]; bl = max(fig.body_l, 12); bw = max(fig.body_w, 6); wl = max(fig.wing_l, 15)
    hl = max(fig.head_l, 5)
    scene = au.AutomataScene(name=nfr, description=f"{nen} — flap", style=style, cycle_rpm=min(rpm, 1.5))
    scene.links = [au.Link("body", bl, bw, bl*0.3, bl*0.2), au.Link("head", hl, hl*0.5, hl*0.4, 3),
        au.Link("wing_left", wl, wl*0.4, 2, 2), au.Link("wing_right", wl, wl*0.4, 2, 2)]
    scene.joints = [au.Joint("neck", "revolute", (1,0,0), (0, bl*0.35, bl*0.15), "body", "head", (-8,8)),
        au.Joint("wing_left_j", "revolute", (0,1,0), (-bw*0.3, bl*0.1, bl*0.25), "body", "wing_left", (-30,60)),
        au.Joint("wing_right_j", "revolute", (0,1,0), (bw*0.3, bl*0.1, bl*0.25), "body", "wing_right", (-30,60))]
    wa = _clamp(wl*0.2, 3, MAX_WING_AMP)
    wp = [au.MotionPrimitive("LIFT", wa, 200, law, 1), au.MotionPrimitive("LIFT", wa, 120, law, -1), au.MotionPrimitive("PAUSE", beta=40)]
    scene.tracks = [
        au.MotionTrack("wing_left_j", primitives=list(wp)),
        au.MotionTrack("wing_right_j", primitives=[au.MotionPrimitive(p.kind, p.amplitude, p.beta, p.law, p.direction) for p in wp]),
        au.MotionTrack("neck", frequency_multiplier=2, primitives=[
            au.MotionPrimitive("LIFT", 3, 100, law, 1), au.MotionPrimitive("LIFT", 3, 60, law, -1), au.MotionPrimitive("PAUSE", beta=20)])]
    scene._preset_name = f"auto_{nen.lower().replace(' ','_')}"; return scene

def _build_arachnid(nfr, nen, fig, style, rpm):
    law = au.STYLE_TO_LAW[style]; bl = max(fig.body_l, 12); bw = max(fig.body_w, 8); ll = max(fig.leg_l, 10)
    cl = bl*0.45; al = bl*0.55; lw = max(3, MIN_DIM)
    scene = au.AutomataScene(name=nfr, description=f"{nen} — 8-leg walk", style=style, cycle_rpm=rpm)
    scene.links = [au.Link("cephalothorax", cl, bw, bw*0.4, bw*0.3), au.Link("abdomen", al, al*0.6, al*0.5, MIN_DIM)]
    for i in range(1,5):
        scene.links += [au.Link(f"leg_L{i}", ll, lw, lw, 2), au.Link(f"leg_R{i}", ll, lw, lw, 2)]
    scene.joints = [au.Joint("pedicel", "revolute", (1,0,0), (0, -cl*0.4, 0), "cephalothorax", "abdomen", (-5,5))]
    yp = [cl*0.3, cl*0.1, -cl*0.1, -cl*0.3]
    for i, y in enumerate(yp):
        n = i+1
        scene.joints += [au.Joint(f"hip_L{n}", "revolute", (1,0,0), (-bw*0.4, y, 0), "cephalothorax", f"leg_L{n}", (-20,20)),
            au.Joint(f"hip_R{n}", "revolute", (1,0,0), (bw*0.4, y, 0), "cephalothorax", f"leg_R{n}", (-20,20))]
    la = _clamp(ll*0.12, 2, MAX_LEG_AMP)
    scene.tracks = [au.MotionTrack("pedicel", frequency_multiplier=2, primitives=[au.MotionPrimitive("WAVE", 2, 180, law)])]
    for i in range(1,5):
        pL = 0 if i%2==1 else 180; pR = 180 if i%2==1 else 0
        scene.tracks += [au.MotionTrack(f"hip_L{i}", phase_offset_deg=pL, primitives=[au.MotionPrimitive("WAVE", la, 360, law)]),
            au.MotionTrack(f"hip_R{i}", phase_offset_deg=pR, primitives=[au.MotionPrimitive("WAVE", la, 360, law)])]
    scene._preset_name = f"auto_{nen.lower().replace(' ','_')}"; return scene

def _build_scorpion(nfr, nen, fig, style, rpm):
    law = au.STYLE_TO_LAW[style]; bl = max(fig.body_l, 15); bw = max(fig.body_w, 8); ll = max(fig.leg_l, 8)
    tl = max(fig.tail_l, 15); lw = max(3, MIN_DIM)
    scene = au.AutomataScene(name=nfr, description=f"{nen} — scorpion walk", style=style, cycle_rpm=rpm)
    scene.links = [au.Link("body", bl, bw, bl*0.15, bl*0.1),
        au.Link("tail_s1", tl*0.35, 5, 5, 3), au.Link("tail_s2", tl*0.35, MIN_DIM, MIN_DIM, 2), au.Link("stinger", tl*0.3, 3, 3, 2),
        au.Link("claw_left", max(fig.arm_l,8), 6, 3, MIN_DIM), au.Link("claw_right", max(fig.arm_l,8), 6, 3, MIN_DIM)]
    for i in range(1,5):
        scene.links += [au.Link(f"leg_L{i}", ll, lw, lw, 2), au.Link(f"leg_R{i}", ll, lw, lw, 2)]
    scene.joints = [
        au.Joint("tail_j1", "revolute", (1,0,0), (0, -bl*0.4, bl*0.1), "body", "tail_s1", (-10,30)),
        au.Joint("tail_j2", "revolute", (1,0,0), (0, tl*0.3, 0), "tail_s1", "tail_s2", (-10,30)),
        au.Joint("sting_j", "revolute", (1,0,0), (0, tl*0.3, 0), "tail_s2", "stinger", (-20,10)),
        au.Joint("claw_L", "revolute", (0,0,1), (-bw*0.3, bl*0.4, 0), "body", "claw_left", (-15,15)),
        au.Joint("claw_R", "revolute", (0,0,1), (bw*0.3, bl*0.4, 0), "body", "claw_right", (-15,15))]
    yp = [bl*0.2, bl*0.05, -bl*0.1, -bl*0.25]
    for i, y in enumerate(yp):
        n = i+1
        scene.joints += [au.Joint(f"hip_L{n}", "revolute", (1,0,0), (-bw*0.4, y, 0), "body", f"leg_L{n}", (-20,20)),
            au.Joint(f"hip_R{n}", "revolute", (1,0,0), (bw*0.4, y, 0), "body", f"leg_R{n}", (-20,20))]
    la = _clamp(ll*0.12, 2, MAX_LEG_AMP); ta = _clamp(tl*0.08, 2, MAX_TAIL_AMP); ca = _clamp(5, 2, MAX_ARM_AMP)
    scene.tracks = [
        au.MotionTrack("tail_j1", phase_offset_deg=0, primitives=[au.MotionPrimitive("WAVE", ta, 360, law)]),
        au.MotionTrack("tail_j2", phase_offset_deg=60, primitives=[au.MotionPrimitive("WAVE", ta, 360, law)]),
        au.MotionTrack("sting_j", phase_offset_deg=120, primitives=[au.MotionPrimitive("WAVE", ta*0.5, 360, law)]),
        au.MotionTrack("claw_L", phase_offset_deg=0, frequency_multiplier=2, primitives=[au.MotionPrimitive("WAVE", ca, 180, law)]),
        au.MotionTrack("claw_R", phase_offset_deg=180, frequency_multiplier=2, primitives=[au.MotionPrimitive("WAVE", ca, 180, law)])]
    for i in range(1,5):
        pL = 0 if i%2==1 else 180; pR = 180 if i%2==1 else 0
        scene.tracks += [au.MotionTrack(f"hip_L{i}", phase_offset_deg=pL, primitives=[au.MotionPrimitive("WAVE", la, 360, law)]),
            au.MotionTrack(f"hip_R{i}", phase_offset_deg=pR, primitives=[au.MotionPrimitive("WAVE", la, 360, law)])]
    scene._preset_name = f"auto_{nen.lower().replace(' ','_')}"; return scene

def _build_crab(nfr, nen, fig, style, rpm):
    law = au.STYLE_TO_LAW[style]; bl = max(fig.body_l, 12); bw = max(fig.body_w, bl*1.2); ll = max(fig.leg_l, 8)
    lw = max(3, MIN_DIM)
    scene = au.AutomataScene(name=nfr, description=f"{nen} — lateral walk", style=style, cycle_rpm=rpm)
    scene.links = [au.Link("carapace", bl, bw, bl*0.3, bl*0.2),
        au.Link("claw_left", max(fig.arm_l,8), 5, 3, MIN_DIM), au.Link("claw_right", max(fig.arm_l,8), 5, 3, MIN_DIM)]
    for i in range(1,5):
        scene.links += [au.Link(f"leg_L{i}", ll, lw, lw, 2), au.Link(f"leg_R{i}", ll, lw, lw, 2)]
    scene.joints = [
        au.Joint("claw_L", "revolute", (0,0,1), (-bw*0.3, bl*0.35, bl*0.1), "carapace", "claw_left", (-15,15)),
        au.Joint("claw_R", "revolute", (0,0,1), (bw*0.3, bl*0.35, bl*0.1), "carapace", "claw_right", (-15,15))]
    xp = [bw*0.35, bw*0.25, bw*0.15, bw*0.05]
    for i, xo in enumerate(xp):
        n = i+1; y = bl*0.1 - i*bl*0.15
        scene.joints += [au.Joint(f"hip_L{n}", "revolute", (0,1,0), (-xo, y, 0), "carapace", f"leg_L{n}", (-20,20)),
            au.Joint(f"hip_R{n}", "revolute", (0,1,0), (xo, y, 0), "carapace", f"leg_R{n}", (-20,20))]
    la = _clamp(ll*0.12, 2, MAX_LEG_AMP); ca = _clamp(5, 2, MAX_ARM_AMP)
    scene.tracks = [
        au.MotionTrack("claw_L", frequency_multiplier=2, primitives=[au.MotionPrimitive("WAVE", ca, 180, law)]),
        au.MotionTrack("claw_R", frequency_multiplier=2, phase_offset_deg=180, primitives=[au.MotionPrimitive("WAVE", ca, 180, law)])]
    for i in range(1,5):
        ph = _phase_deg((i-1)*0.25)
        scene.tracks += [au.MotionTrack(f"hip_L{i}", phase_offset_deg=ph, primitives=[au.MotionPrimitive("WAVE", la, 360, law)]),
            au.MotionTrack(f"hip_R{i}", phase_offset_deg=ph, primitives=[au.MotionPrimitive("WAVE", la, 360, law)])]
    scene._preset_name = f"auto_{nen.lower().replace(' ','_')}"; return scene

def _build_lobster(nfr, nen, fig, style, rpm):
    law = au.STYLE_TO_LAW[style]; bl = max(fig.body_l, 15); bw = max(fig.body_w, 8); ll = max(fig.leg_l, 6)
    tl = max(fig.tail_l, bl*0.3); lw = max(3, MIN_DIM)
    scene = au.AutomataScene(name=nfr, description=f"{nen} — lobster walk", style=style, cycle_rpm=rpm)
    scene.links = [au.Link("body", bl, bw, bl*0.2, bl*0.15), au.Link("tail_fan", tl, tl*0.5, tl*0.2, MIN_DIM),
        au.Link("claw_left", max(fig.arm_l,8), 6, 3, MIN_DIM), au.Link("claw_right", max(fig.arm_l,8), 6, 3, MIN_DIM)]
    for i in range(1,5):
        scene.links += [au.Link(f"leg_L{i}", ll, lw, lw, 2), au.Link(f"leg_R{i}", ll, lw, lw, 2)]
    scene.joints = [
        au.Joint("tail_j", "revolute", (1,0,0), (0, -bl*0.4, 0), "body", "tail_fan", (-15,15)),
        au.Joint("claw_L", "revolute", (0,0,1), (-bw*0.3, bl*0.4, bl*0.05), "body", "claw_left", (-15,15)),
        au.Joint("claw_R", "revolute", (0,0,1), (bw*0.3, bl*0.4, bl*0.05), "body", "claw_right", (-15,15))]
    for i in range(1,5):
        y = bl*0.2 - i*bl*0.15
        scene.joints += [au.Joint(f"hip_L{i}", "revolute", (1,0,0), (-bw*0.4, y, 0), "body", f"leg_L{i}", (-18,18)),
            au.Joint(f"hip_R{i}", "revolute", (1,0,0), (bw*0.4, y, 0), "body", f"leg_R{i}", (-18,18))]
    la = _clamp(ll*0.12, 2, MAX_LEG_AMP); ta = _clamp(tl*0.1, 2, MAX_TAIL_AMP); ca = _clamp(5, 2, MAX_ARM_AMP)
    scene.tracks = [
        au.MotionTrack("tail_j", primitives=[au.MotionPrimitive("WAVE", ta, 360, law)]),
        au.MotionTrack("claw_L", frequency_multiplier=2, primitives=[au.MotionPrimitive("WAVE", ca, 180, law)]),
        au.MotionTrack("claw_R", frequency_multiplier=2, phase_offset_deg=180, primitives=[au.MotionPrimitive("WAVE", ca, 180, law)])]
    for i in range(1,5):
        pL = 0 if i%2==1 else 180; pR = 180 if i%2==1 else 0
        scene.tracks += [au.MotionTrack(f"hip_L{i}", phase_offset_deg=pL, primitives=[au.MotionPrimitive("WAVE", la, 360, law)]),
            au.MotionTrack(f"hip_R{i}", phase_offset_deg=pR, primitives=[au.MotionPrimitive("WAVE", la, 360, law)])]
    scene._preset_name = f"auto_{nen.lower().replace(' ','_')}"; return scene

def _build_myriapod(nfr, nen, fig, style, rpm):
    law = au.STYLE_TO_LAW[style]; bl = max(fig.body_l, 20); sl = bl/4
    scene = au.AutomataScene(name=nfr, description=f"{nen} — wave", style=style, cycle_rpm=rpm)
    scene.links = [au.Link("head", sl*0.8, 6, 5, 3)]
    for i in range(1,5):
        scene.links.append(au.Link(f"seg{i}", sl, 7 if i<3 else 6, 5 if i<3 else MIN_DIM, MIN_DIM if i<3 else 3))
    scene.joints = [au.Joint("j0", "revolute", (0,0,1), (0, sl*0.45, 0), "head", "seg1", (-10,10))]
    for i in range(1,4):
        scene.joints.append(au.Joint(f"j{i}", "revolute", (0,0,1), (0, -sl*0.45, 0), f"seg{i}", f"seg{i+1}", (-12,12)))
    a = _clamp(5, 2, MAX_BODY_WAVE_AMP)
    scene.tracks = [au.MotionTrack(f"j{i}", phase_offset_deg=i*90, primitives=[au.MotionPrimitive("WAVE", a, 360, law)]) for i in range(4)]
    scene._preset_name = f"auto_{nen.lower().replace(' ','_')}"; return scene

def _build_octopus(nfr, nen, fig, style, rpm):
    law = au.STYLE_TO_LAW[style]; bl = max(fig.body_l, 15); bw = max(fig.body_w, 10); tl = max(fig.leg_l, 12)
    scene = au.AutomataScene(name=nfr, description=f"{nen} — tentacles", style=style, cycle_rpm=max(rpm, 0.8))
    scene.links = [au.Link("mantle", bl, bw, bl*0.5, bl*0.3)]
    for i in range(1,5):
        scene.links += [au.Link(f"tent_L{i}", tl, 3, 3, 2), au.Link(f"tent_R{i}", tl, 3, 3, 2)]
    for i in range(1,5):
        ang = (i-1)*0.2 - 0.3
        scene.joints += [au.Joint(f"tent_L{i}_j", "revolute", (1,0,0), (-bw*0.3, bl*ang, 0), "mantle", f"tent_L{i}", (-20,20)),
            au.Joint(f"tent_R{i}_j", "revolute", (1,0,0), (bw*0.3, bl*ang, 0), "mantle", f"tent_R{i}", (-20,20))]
    ta = _clamp(tl*0.15, 2, MAX_TENTACLE_AMP)
    for i in range(1,5):
        ph = (i-1)*45
        scene.tracks += [au.MotionTrack(f"tent_L{i}_j", phase_offset_deg=ph, primitives=[au.MotionPrimitive("WAVE", ta, 360, law)]),
            au.MotionTrack(f"tent_R{i}_j", phase_offset_deg=ph+180, primitives=[au.MotionPrimitive("WAVE", ta, 360, law)])]
    scene._preset_name = f"auto_{nen.lower().replace(' ','_')}"; return scene

def _build_snail(nfr, nen, fig, style, rpm):
    law = au.STYLE_TO_LAW[style]; bl = max(fig.body_l, 15)
    scene = au.AutomataScene(name=nfr, description=f"{nen} — glide", style=style, cycle_rpm=max(rpm, 0.5))
    scene.links = [au.Link("shell", bl*0.5, bl*0.5, bl*0.6, bl*0.3), au.Link("body", bl, bl*0.25, bl*0.1, bl*0.05),
        au.Link("head", bl*0.15, bl*0.12, bl*0.08, 3), au.Link("tentacle_L", bl*0.15, 2, 2, 1), au.Link("tentacle_R", bl*0.15, 2, 2, 1)]
    scene.joints = [au.Joint("shell_j", "revolute", (1,0,0), (0, -bl*0.15, bl*0.1), "body", "shell", (-5,5)),
        au.Joint("neck", "revolute", (1,0,0), (0, bl*0.4, bl*0.05), "body", "head", (-10,15)),
        au.Joint("tent_L", "revolute", (1,0,0), (-bl*0.04, bl*0.06, bl*0.04), "head", "tentacle_L", (-20,20)),
        au.Joint("tent_R", "revolute", (1,0,0), (bl*0.04, bl*0.06, bl*0.04), "head", "tentacle_R", (-20,20))]
    scene.tracks = [
        au.MotionTrack("neck", primitives=[au.MotionPrimitive("LIFT", 4, 200, law, 1), au.MotionPrimitive("LIFT", 4, 150, law, -1), au.MotionPrimitive("PAUSE", beta=10)]),
        au.MotionTrack("tent_L", phase_offset_deg=0, frequency_multiplier=2, primitives=[au.MotionPrimitive("WAVE", 3, 180, law)]),
        au.MotionTrack("tent_R", phase_offset_deg=90, frequency_multiplier=2, primitives=[au.MotionPrimitive("WAVE", 3, 180, law)]),
        au.MotionTrack("shell_j", primitives=[au.MotionPrimitive("WAVE", 2, 360, law)])]
    scene._preset_name = f"auto_{nen.lower().replace(' ','_')}"; return scene

def _build_plant(nfr, nen, fig, style, rpm):
    law = au.STYLE_TO_LAW[style]; bl = max(fig.body_l, 20); hl = max(fig.head_l, 10)
    scene = au.AutomataScene(name=nfr, description=f"{nen} — sway", style=style, cycle_rpm=max(rpm, 0.5))
    scene.links = [au.Link("stem", bl, max(bl*0.1, MIN_DIM), max(bl*0.1, MIN_DIM), MIN_DIM), au.Link("flower", hl, hl*0.8, hl*0.4, 3)]
    scene.joints = [au.Joint("stem_top", "revolute", (1,0,0), (0, bl*0.45, 0), "stem", "flower", (-15,15))]
    scene.tracks = [au.MotionTrack("stem_top", primitives=[au.MotionPrimitive("WAVE", 5, 360, law)])]
    scene._preset_name = f"auto_{nen.lower().replace(' ','_')}"; return scene

def _build_dino_biped(nfr, nen, fig, style, rpm):
    law = au.STYLE_TO_LAW[style]; bl = max(fig.body_l, 20); bw = max(fig.body_w, 10); ll = max(fig.leg_l, 15)
    hl = max(fig.head_l, 10); tl = max(fig.tail_l, 15); al = max(fig.arm_l, 5) if fig.n_arms > 0 else 5
    scene = au.AutomataScene(name=nfr, description=f"{nen} — stomp", style=style, cycle_rpm=max(rpm, 0.8))
    scene.links = [au.Link("body", bl, bw, bl*0.3, bl*0.25), au.Link("head", hl, hl*0.7, hl*0.5, hl*0.2),
        au.Link("jaw", hl*0.5, hl*0.5, hl*0.15, 2),
        au.Link("leg_left", ll, 10, 8, MIN_DIM), au.Link("leg_right", ll, 10, 8, MIN_DIM),
        au.Link("arm_left", al, MIN_DIM, 3, 2), au.Link("arm_right", al, MIN_DIM, 3, 2),
        au.Link("tail", tl, 8, 6, 3)]
    scene.joints = [
        au.Joint("neck", "revolute", (1,0,0), (0, bl*0.35, bl*0.25), "body", "head", (-10,15)),
        au.Joint("jaw_j", "revolute", (1,0,0), (0, hl*0.2, -hl*0.1), "head", "jaw", (-20,5)),
        au.Joint("hip_left", "revolute", (1,0,0), (-bw*0.3, -bl*0.1, 0), "body", "leg_left", (-25,25)),
        au.Joint("hip_right", "revolute", (1,0,0), (bw*0.3, -bl*0.1, 0), "body", "leg_right", (-25,25)),
        au.Joint("shoulder_L", "revolute", (1,0,0), (-bw*0.25, bl*0.2, bl*0.15), "body", "arm_left", (-10,10)),
        au.Joint("shoulder_R", "revolute", (1,0,0), (bw*0.25, bl*0.2, bl*0.15), "body", "arm_right", (-10,10)),
        au.Joint("tail_j", "revolute", (0,0,1), (0, -bl*0.4, bl*0.1), "body", "tail", (-10,10))]
    la = _clamp(ll*0.1, 2, MAX_LEG_AMP); ha = _clamp(5, 2, MAX_HEAD_AMP); ta = _clamp(tl*0.05, 2, MAX_TAIL_AMP)
    scene.tracks = [
        au.MotionTrack("hip_left", phase_offset_deg=0, primitives=[au.MotionPrimitive("WAVE", la, 360, law)]),
        au.MotionTrack("hip_right", phase_offset_deg=180, primitives=[au.MotionPrimitive("WAVE", la, 360, law)]),
        au.MotionTrack("neck", frequency_multiplier=2, primitives=[
            au.MotionPrimitive("LIFT", ha, 100, law, 1), au.MotionPrimitive("LIFT", ha, 60, law, -1), au.MotionPrimitive("PAUSE", beta=20)]),
        au.MotionTrack("jaw_j", frequency_multiplier=3, primitives=[
            au.MotionPrimitive("LIFT", 4, 40, law, -1), au.MotionPrimitive("LIFT", 4, 30, law, 1), au.MotionPrimitive("PAUSE", beta=50)]),
        au.MotionTrack("tail_j", phase_offset_deg=90, primitives=[au.MotionPrimitive("WAVE", ta, 360, law)])]
    scene._preset_name = f"auto_{nen.lower().replace(' ','_')}"; return scene

def _build_dragon(nfr, nen, fig, style, rpm):
    law = au.STYLE_TO_LAW[style]; bl = max(fig.body_l, 20); bw = max(fig.body_w, 10); ll = max(fig.leg_l, 10)
    wl = max(fig.wing_l, 20); tl = max(fig.tail_l, 15); hl = max(fig.head_l, 10)
    lw = max(bw*0.15, MIN_DIM)
    scene = au.AutomataScene(name=nfr, description=f"{nen} — dragon walk", style=style, cycle_rpm=rpm)
    scene.links = [au.Link("body", bl, bw, bl*0.3, bl*0.2), au.Link("head", hl, hl*0.6, hl*0.5, hl*0.2),
        au.Link("jaw", hl*0.4, hl*0.4, hl*0.1, 2),
        au.Link("wing_left", wl, wl*0.35, 3, MIN_DIM), au.Link("wing_right", wl, wl*0.35, 3, MIN_DIM),
        au.Link("tail", tl, 6, 5, 3),
        au.Link("leg_fl", ll, lw, lw, 3), au.Link("leg_fr", ll, lw, lw, 3),
        au.Link("leg_hl", ll, lw, lw, 3), au.Link("leg_hr", ll, lw, lw, 3)]
    hbl = bl/2; hbw = bw/2
    scene.joints = [
        au.Joint("neck", "revolute", (1,0,0), (0, hbl-2, bl*0.2), "body", "head", (-15,20)),
        au.Joint("jaw_j", "revolute", (1,0,0), (0, hl*0.2, -hl*0.1), "head", "jaw", (-20,5)),
        au.Joint("wing_L", "revolute", (0,1,0), (-hbw*0.6, hbl*0.2, bl*0.25), "body", "wing_left", (-30,60)),
        au.Joint("wing_R", "revolute", (0,1,0), (hbw*0.6, hbl*0.2, bl*0.25), "body", "wing_right", (-30,60)),
        au.Joint("tail_j", "revolute", (0,0,1), (0, -hbl, bl*0.1), "body", "tail", (-10,10)),
        au.Joint("hip_fl", "revolute", (1,0,0), (-hbw*0.6, hbl*0.5, 0), "body", "leg_fl", (-25,25)),
        au.Joint("hip_fr", "revolute", (1,0,0), (hbw*0.6, hbl*0.5, 0), "body", "leg_fr", (-25,25)),
        au.Joint("hip_hl", "revolute", (1,0,0), (-hbw*0.6, -hbl*0.3, 0), "body", "leg_hl", (-25,25)),
        au.Joint("hip_hr", "revolute", (1,0,0), (hbw*0.6, -hbl*0.3, 0), "body", "leg_hr", (-25,25))]
    la = _clamp(ll*0.12, 2, MAX_LEG_AMP); wa = _clamp(wl*0.15, 3, MAX_WING_AMP)
    ta = _clamp(tl*0.08, 2, MAX_TAIL_AMP); ha = _clamp(5, 2, MAX_HEAD_AMP)
    wp = [au.MotionPrimitive("LIFT", wa, 200, law, 1), au.MotionPrimitive("LIFT", wa, 120, law, -1), au.MotionPrimitive("PAUSE", beta=40)]
    scene.tracks = [
        au.MotionTrack("hip_fl", phase_offset_deg=0, primitives=[au.MotionPrimitive("WAVE", la, 360, law)]),
        au.MotionTrack("hip_fr", phase_offset_deg=180, primitives=[au.MotionPrimitive("WAVE", la, 360, law)]),
        au.MotionTrack("hip_hl", phase_offset_deg=180, primitives=[au.MotionPrimitive("WAVE", la, 360, law)]),
        au.MotionTrack("hip_hr", phase_offset_deg=0, primitives=[au.MotionPrimitive("WAVE", la, 360, law)]),
        au.MotionTrack("wing_L", primitives=list(wp)),
        au.MotionTrack("wing_R", primitives=[au.MotionPrimitive(p.kind, p.amplitude, p.beta, p.law, p.direction) for p in wp]),
        au.MotionTrack("neck", frequency_multiplier=2, primitives=[
            au.MotionPrimitive("LIFT", ha, 100, law, 1), au.MotionPrimitive("LIFT", ha, 60, law, -1), au.MotionPrimitive("PAUSE", beta=20)]),
        au.MotionTrack("jaw_j", frequency_multiplier=3, primitives=[
            au.MotionPrimitive("LIFT", 4, 40, law, -1), au.MotionPrimitive("LIFT", 4, 30, law, 1), au.MotionPrimitive("PAUSE", beta=50)]),
        au.MotionTrack("tail_j", phase_offset_deg=90, primitives=[au.MotionPrimitive("WAVE", ta, 360, law)])]
    scene._preset_name = f"auto_{nen.lower().replace(' ','_')}"; return scene

# ═══════ WRAPPERS RETRO-COMPAT (ancien animal_db) ═══════

def _wrap_old_quad(animal, fig, style, rpm):
    sp = Species(animal.name_fr, animal.name_en, "", "MAM_FELIN", animal.mass_kg, animal.body_length_mm)
    bp = BodyPlan(id="MAM_FELIN", name="Legacy", category="MAM_QUAD_FELIN", n_legs=4,
                  has_tail=True, gait=animal.gait, gait_phases=fig.gait_phases, movable_parts=["legs","head_nod","tail_wag"])
    fd = FigDims(sp, bp, getattr(fig, "total_height", fig.body_h + fig.leg_l))
    fd.body_l=fig.body_l; fd.body_w=fig.body_w; fd.body_h=max(fig.body_h,15)
    fd.head_l=fig.head_l; fd.leg_l=fig.leg_l; fd.tail_l=fig.tail_l; fd.gait_phases=fig.gait_phases
    return _build_quadruped(animal.name_fr, animal.name_en, fd, style, rpm)

def _wrap_old_biped(animal, fig, style, rpm):
    sp = Species(animal.name_fr, animal.name_en, "", "MAM_PRIMATE", animal.mass_kg, animal.body_length_mm)
    bp = BodyPlan(id="BIPED", name="Legacy", category="MAM_PRIMATE", n_legs=2, n_arms=2, arm_ratio=0.45, movable_parts=["legs","arms"])
    fd = FigDims(sp, bp, getattr(fig, "total_height", fig.body_h + fig.leg_l))
    fd.body_l=max(fig.body_l,15); fd.body_w=max(fig.body_w,10); fd.head_l=fig.head_l
    fd.leg_l=max(fig.leg_l,15); fd.arm_l=fd.leg_l*0.8; fd.n_arms=2; fd.gait_phases={}
    return _build_biped(animal.name_fr, animal.name_en, fd, style, rpm)

def _wrap_old_biped_bird(animal, fig, style, rpm):
    sp = Species(animal.name_fr, animal.name_en, "", "AV_NAGEUR", animal.mass_kg, animal.body_length_mm)
    bp = BodyPlan(id="AV_NAGEUR", name="Legacy", category="AV_NAGEUR", n_legs=2, movable_parts=["legs","head_nod"])
    fd = FigDims(sp, bp, getattr(fig, "total_height", fig.body_h + fig.leg_l))
    fd.body_l=max(fig.body_l,15); fd.body_w=max(fig.body_w,10); fd.head_l=fig.head_l
    fd.leg_l=fig.leg_l; fd.n_arms=0; fd.gait_phases={}
    return _build_biped(animal.name_fr, animal.name_en, fd, style, rpm)

def _wrap_old_flapper(animal, fig, style, rpm):
    sp = Species(animal.name_fr, animal.name_en, "", "AV_VOL", animal.mass_kg, animal.body_length_mm)
    bp = BodyPlan(id="AV_VOL", name="Legacy", category="AV_VOLANT", n_legs=2, n_wings=2, wing_ratio=1.2, movable_parts=["wings_flap"])
    fd = FigDims(sp, bp, getattr(fig, "total_height", fig.body_h + fig.leg_l))
    fd.body_l=max(fig.body_l,15); fd.body_w=max(fig.body_w,10); fd.head_l=fig.head_l
    fd.wing_l=max(fd.body_l*0.7,20); fd.tail_l=fig.tail_l; fd.has_tail=fig.tail_l>5; fd.gait_phases={}
    return _build_flapper(animal.name_fr, animal.name_en, fd, style, rpm)

def _wrap_old_snake(animal, fig, style, rpm):
    sp = Species(animal.name_fr, animal.name_en, "", "REP_SERPENT", animal.mass_kg, animal.body_length_mm)
    bp = BodyPlan(id="REP_SERPENT", name="Legacy", category="REP_SERPENT", n_legs=0, movable_parts=["body_wave"])
    fd = FigDims(sp, bp, getattr(fig, "total_height", fig.body_h + fig.leg_l))
    fd.body_l=max(fig.body_l,45); fd.gait_phases={}
    return _build_snake(animal.name_fr, animal.name_en, fd, style, rpm)

def _wrap_old_insect(animal, fig, style, rpm):
    sp = Species(animal.name_fr, animal.name_en, "", "INS_MARCH", animal.mass_kg, animal.body_length_mm)
    bp = BodyPlan(id="INS_MARCH", name="Legacy", category="INS_MARCHEUR", n_legs=6, movable_parts=["legs_tripod"])
    fd = FigDims(sp, bp, getattr(fig, "total_height", fig.body_h + fig.leg_l))
    fd.body_l=max(fig.body_l,15); fd.body_w=max(fig.body_w,8); fd.leg_l=max(fig.leg_l,8)
    fd.head_l=max(fig.head_l,5); fd.gait_phases={}
    return _build_insect_6leg(animal.name_fr, animal.name_en, fd, style, rpm)

# ═══════ TESTS ═══════

def test_scene_builder():
    from living_beings_db import SPECIES_DB, BODY_PLANS as LB_PLANS
    passed = 0; total = 0

    def _t(cond, msg):
        nonlocal passed, total; total += 1
        if cond: passed += 1
        else: print(f"  FAIL: {msg}")

    # 1: Chat quadrupede
    s = make_automaton("chat")
    _t(s.name == "Chat", f"nom={s.name}")
    _t(any("hip" in t.name for t in s.tracks), "pas de hip tracks")
    _t(not s.validate(), f"validate: {s.validate()}")

    # 2: Araignee 8 pattes
    s = make_automaton("araignée")
    lt = [t for t in s.tracks if "hip" in t.name]
    _t(len(lt) == 8, f"araignee: {len(lt)} leg tracks (attendu 8)")
    _t(not s.validate(), f"validate: {s.validate()}")

    # 3: Crabe lateral + pinces
    s = make_automaton("crabe")
    _t("lateral" in s.description, f"crabe desc: {s.description}")
    ct = [t for t in s.tracks if "claw" in t.name]
    _t(len(ct) == 2, f"crabe: {len(ct)} claw tracks")
    _t(not s.validate(), f"validate: {s.validate()}")

    # 4: Scorpion 8 pattes + queue + pinces
    s = make_automaton("scorpion")
    tt = [t for t in s.tracks if "tail" in t.name or "sting" in t.name]
    _t(len(tt) >= 2, f"scorpion: {len(tt)} tail tracks")
    lt = [t for t in s.tracks if "hip" in t.name]
    _t(len(lt) == 8, f"scorpion: {len(lt)} leg tracks")
    _t(not s.validate(), f"validate: {s.validate()}")

    # 5: Pieuvre 8 tentacules
    s = make_automaton("pieuvre")
    tt = [t for t in s.tracks if "tent" in t.name]
    _t(len(tt) == 8, f"pieuvre: {len(tt)} tentacle tracks")
    _t(not s.validate(), f"validate: {s.validate()}")

    # 6: Aigle ailes
    s = make_automaton("aigle")
    wt = [t for t in s.tracks if "shoulder" in t.name or "wing" in t.name]
    _t(len(wt) >= 2, f"aigle: {len(wt)} wing tracks")
    _t("flap" in s.description, f"aigle desc: {s.description}")
    _t(not s.validate(), f"validate: {s.validate()}")

    # 7: Fourmi 6 pattes tripod
    s = make_automaton("fourmi")
    _t("tripod" in s.description, f"fourmi desc: {s.description}")
    lt = [t for t in s.tracks if "hip" in t.name]
    _t(len(lt) == 6, f"fourmi: {len(lt)} leg tracks (attendu 6)")
    _t(not s.validate(), f"validate: {s.validate()}")

    # 8: Dragon 4 pattes + ailes + machoire
    s = make_automaton("dragon")
    _t(len([t for t in s.tracks if "hip" in t.name]) == 4, "dragon hips")
    _t(len([t for t in s.tracks if "wing" in t.name]) == 2, "dragon wings")
    _t(len([t for t in s.tracks if "jaw" in t.name]) == 1, "dragon jaw")
    _t(not s.validate(), f"validate: {s.validate()}")

    # 9: Serpent 3 segments
    s = make_automaton("serpent")
    _t(len(s.links) == 3, f"serpent: {len(s.links)} links")
    _t(not s.validate(), f"validate: {s.validate()}")

    # 10: Centipede ondulation
    s = make_automaton("centipède")
    _t("wave" in s.description, f"centipede desc: {s.description}")
    _t(len(s.tracks) == 4, f"centipede: {len(s.tracks)} tracks")
    _t(not s.validate(), f"validate: {s.validate()}")

    # 11: Escargot
    s = make_automaton("escargot")
    _t("glide" in s.description, f"escargot desc: {s.description}")
    _t(not s.validate(), f"validate: {s.validate()}")

    # 12: Chauve-souris ailes
    s = make_automaton("chauve-souris")
    _t("flap" in s.description, f"bat desc: {s.description}")
    wt = [t for t in s.tracks if "shoulder" in t.name]
    _t(len(wt) == 2, f"bat: {len(wt)} wing tracks")
    _t(not s.validate(), f"validate: {s.validate()}")

    # 13: T-Rex bipede + machoire
    s = make_automaton("T-Rex")
    _t("stomp" in s.description, f"trex desc: {s.description}")
    _t(len([t for t in s.tracks if "jaw" in t.name]) == 1, "trex jaw")
    _t(not s.validate(), f"validate: {s.validate()}")

    # 14: Homard pinces + queue
    s = make_automaton("homard")
    ct = [t for t in s.tracks if "claw" in t.name]
    _t(len(ct) == 2, f"homard: {len(ct)} claw tracks")
    _t(not s.validate(), f"validate: {s.validate()}")

    # 15: Dauphin nage
    s = make_automaton("dauphin")
    _t("swim" in s.description, f"dauphin desc: {s.description}")
    _t(not s.validate(), f"validate: {s.validate()}")

    # 16: Tournesol plante
    s = make_automaton("tournesol")
    _t("sway" in s.description, f"tournesol desc: {s.description}")
    _t(not s.validate(), f"validate: {s.validate()}")

    # 17: Abeille insecte volant
    s = make_automaton("abeille")
    _t("flap" in s.description, f"abeille desc: {s.description}")
    wt = [t for t in s.tracks if "wing" in t.name]
    _t(len(wt) == 2, f"abeille: {len(wt)} wing tracks")
    _t(not s.validate(), f"validate: {s.validate()}")

    # 18: Millipede
    s = make_automaton("millipède")
    _t("wave" in s.description, f"millipede desc: {s.description}")
    _t(not s.validate(), f"validate: {s.validate()}")

    # 19: TOUTES 118 especes passent validation scene
    all_ok = True; fails = []
    for key, sp in SPECIES_DB.items():
        try:
            sc = make_automaton(sp.name_fr)
            errs = sc.validate()
            if errs:
                fails.append(f"{key}: {errs}"); all_ok = False
        except Exception as ex:
            fails.append(f"{key}: CRASH {ex}"); all_ok = False
    if not all_ok:
        for f in fails[:10]: print(f"  FAIL: {f}")
    _t(all_ok, f"{len(fails)} especes echouent")

    # 20: Amplitudes raisonnables
    amp_ok = True
    for key, sp in SPECIES_DB.items():
        sc = make_automaton(sp.name_fr)
        for t in sc.tracks:
            for p in t.primitives:
                if p.kind != "PAUSE" and p.amplitude > 16:
                    print(f"  AMP: {key}/{t.name}: {p.amplitude}mm"); amp_ok = False
    _t(amp_ok, "amplitudes trop grandes")

    print(f"scene_builder v2: {passed}/{total} tests {'✅' if passed==total else '❌'}")
    return passed == total

if __name__ == "__main__":
    test_scene_builder()


# ═══════════════════════════════════════════════════════════════
#  BRIDGE: BodyPlan → FigurineConfig (pour FigurineBuilder)
# ═══════════════════════════════════════════════════════════════

def bodyplan_to_figurine_cfg(sp, bp, target_h=60.0, drive_mode='crank'):
    """Convertit un BodyPlan (living_beings_db) en FigurineConfig (automata_unified_v4).
    
    Utilise les proportions EXACTES du body plan pour dimensionner la figurine.
    """
    fig = FigDims(sp, bp, target_h)
    
    # Map body plan category to FigurineConfig body_type
    bid = bp.id
    if bid in ("FISH_STD", "FISH_PLAT", "MAM_MARIN"):
        bt = "fish"
    elif bid in ("AV_VOL", "AV_RAPACE", "AV_PETIT", "AV_COUREUR", "AV_NAGEUR"):
        bt = "bird"
    elif bid in ("MAM_PRIMATE", "FAN_ROBOT"):
        bt = "biped"
    else:
        bt = "quadruped"
    
    # Map movable_parts to movement type
    mp = bp.movable_parts
    if "wings_flap" in mp or "wings" in mp:
        mv = "flap"
    elif "legs" in mp and bp.n_legs >= 4:
        mv = "walk"
    elif "head_nod" in mp or "head_retract" in mp:
        mv = "nod"
    elif "body_wave" in mp or "undulate" in mp:
        mv = "swim"
    else:
        mv = "nod"
    
    # Build accessories from body plan specifics
    accessories = []
    
    # Turtle shell (carapace) — dome on top of body
    if bid == "REP_TORTUE":
        shell_w = fig.body_w * 0.95
        shell_l = fig.body_l * 0.85
        shell_h = fig.body_h * 0.9  # tall dome
        accessories.append(au.AccessoryDef(
            "carapace", "ellipsoid", 
            (shell_w/2, shell_l/2, shell_h/2),
            "body", (0, 0, fig.body_h * 0.25)
        ))
    
    # Crocodile snout
    if bid == "REP_CROCO":
        accessories.append(au.AccessoryDef(
            "snout", "cone", (fig.head_l * 0.3, fig.head_l * 0.8, 0),
            "head", (0, fig.head_l * 0.5, -fig.head_l * 0.1)
        ))
    
    # Dinosaur crest / horns
    if bid in ("REP_DINO_B", "REP_DINO_Q"):
        accessories.append(au.AccessoryDef(
            "crest", "cone", (fig.head_l * 0.15, fig.head_l * 0.4, 0),
            "head", (0, -fig.head_l * 0.1, fig.head_l * 0.4)
        ))
    
    cfg = au.FigurineConfig(
        name=sp.name_fr,
        body_type=bt,
        height=target_h,
        head_ratio=bp.head_ratio,
        n_legs=bp.n_legs,
        n_arms=bp.n_arms,
        has_wings=bp.n_wings > 0,
        has_tail=bp.has_tail,
        has_eyes=True,
        has_ears=bid in ("MAM_TRAPU","MAM_GRACE","MAM_FELIN","MAM_CANIN","MAM_PETIT","MAM_PRIMATE"),
        has_beak=bid in ("AV_VOL","AV_RAPACE","AV_PETIT","AV_COUREUR","AV_NAGEUR"),
        movement=mv,
        drive_mode=drive_mode,
        accessories=accessories,
    )
    
    # Override FigurineBuilder proportions with actual body plan ratios
    # These will be read by the enhanced FigurineBuilder
    cfg._bp_body_width_ratio = bp.body_width_ratio
    cfg._bp_body_height_ratio = bp.body_height_ratio
    cfg._bp_head_ratio = bp.head_ratio
    cfg._bp_leg_ratio = bp.leg_ratio
    cfg._bp_tail_ratio = bp.tail_ratio
    cfg._bp_wing_ratio = bp.wing_ratio
    cfg._bp_id = bp.id
    
    return cfg
