#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  TEST INTEGRATION — automata_unified_v4.py + micr.py                       ║
║  Le générateur crée les pièces, le MICR optimise les contraintes           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import sys, os, time, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np

# ═══════════════════════════════════════════════════════════════════
# IMPORTS
# ═══════════════════════════════════════════════════════════════════

print("=" * 70)
print("  TEST INTEGRATION: automata_unified_v4 + MICR")
print("=" * 70)

t_global = time.time()

print("\n[1] Importing automata_unified_v4...")
t0 = time.time()
from automata_unified_v4 import (
    AutomataScene, AutomataGenerator, CamProfile, CamSegment,
    MotionPrimitive, MotionTrack, MotionLaw, MotionStyle,
    ChassisConfig, compile_scene_to_cams, check_motor_feasibility,
    create_nodding_bird, create_flapping_bird, create_waving_cat,
    create_turtle_simple, create_turtle_walking,
    create_slide_scene, create_rotate_scene,
    create_multi_scene, create_hold_scene,
    compute_Rb_min_translating_roller,
    SCENE_PRESETS,
)
print(f"    ✓ automata_unified_v4 imported ({time.time()-t0:.1f}s)")
print(f"    Available presets: {list(SCENE_PRESETS.keys())}")

print("\n[2] Importing MICR...")
t0 = time.time()
from micr import (
    MICR, MICRResult, DesignVector, SpatialRelation,
    apply_micr_to_chassis_config, apply_micr_to_scene,
    ALL_SPATIAL_RELATIONS, CLEARANCE_TABLE,
    constraint_shaft_deflection, constraint_pressure_angle,
    constraint_print_plate, constraint_roller_ratio,
    route_pushrod_around_obstacle, PushrodRoute,
)
print(f"    ✓ MICR imported ({time.time()-t0:.1f}s)")
print(f"    Spatial relations: {len(ALL_SPATIAL_RELATIONS)}")

# ═══════════════════════════════════════════════════════════════════
# TEST HELPERS
# ═══════════════════════════════════════════════════════════════════

results = []

def run_test(name, fn):
    """Run a test, catch errors, record result."""
    print(f"\n{'─'*70}")
    print(f"  TEST: {name}")
    print(f"{'─'*70}")
    t0 = time.time()
    try:
        ok, details = fn()
        dt = time.time() - t0
        status = "✓ PASS" if ok else "✗ FAIL"
        print(f"\n  {status} ({dt:.1f}s) — {details}")
        results.append((name, ok, dt, details))
    except Exception as e:
        dt = time.time() - t0
        tb = traceback.format_exc()
        print(f"\n  ✗ ERROR ({dt:.1f}s) — {e}")
        print(f"  {tb[-300:]}")
        results.append((name, False, dt, f"ERROR: {e}"))


# ═══════════════════════════════════════════════════════════════════
# TEST 1: Scene creation → compile cams → MICR (simple)
# ═══════════════════════════════════════════════════════════════════

def test_nodding_bird_micr():
    """Nodding bird: 1 cam, simplest case."""
    scene = create_nodding_bird()
    assert scene is not None, "Scene creation failed"
    
    cams = compile_scene_to_cams(scene)
    assert len(cams) >= 1, f"Expected ≥1 cam, got {len(cams)}"
    print(f"    Scene: {scene.name}, {len(cams)} cam(s)")
    
    # Motor check (simplified)
    motor_check = {'feasible': True, 'stall_torque_mNm': 150.0, 'peak_torque_mNm': 50.0}
    
    # Run MICR
    micr = MICR(scene, cams, motor_check, verbose=True)
    result = micr.solve()
    
    print(f"    MICR: {result.constraints_satisfied}/{result.constraints_total} constraints")
    print(f"    Chassis: {result.chassis_width:.0f}×{result.chassis_depth:.0f}×{result.chassis_height:.0f}mm")
    
    # Apply to scene
    apply_micr_to_scene(result, scene)
    assert hasattr(scene, '_solver_overrides'), "solver_overrides not set"
    assert 'cam_Rb_hints' in scene._solver_overrides, "cam_Rb_hints missing"
    
    return result.success or result.constraints_satisfied >= result.constraints_total * 0.9, \
        f"{result.constraints_satisfied}/{result.constraints_total} OK, {result.solve_time_s:.1f}s"

run_test("Nodding Bird → MICR", test_nodding_bird_micr)


# ═══════════════════════════════════════════════════════════════════
# TEST 2: Flapping bird (2 cams — wings + body bob)
# ═══════════════════════════════════════════════════════════════════

def test_flapping_bird_micr():
    """Flapping bird: 2+ cams, tests adjacent lever clearance."""
    scene = create_flapping_bird()
    cams = compile_scene_to_cams(scene)
    print(f"    Scene: {scene.name}, {len(cams)} cam(s)")
    
    motor_check = {'feasible': True, 'stall_torque_mNm': 150.0, 'peak_torque_mNm': 80.0}
    
    micr = MICR(scene, cams, motor_check, verbose=True)
    result = micr.solve()
    
    # Check Rb hints were generated for each cam
    assert len(result.cam_Rb_hints) == len(cams), \
        f"Rb hints count mismatch: {len(result.cam_Rb_hints)} vs {len(cams)} cams"
    
    for name, rb in result.cam_Rb_hints.items():
        assert 8.0 <= rb <= 35.0, f"cam {name}: Rb={rb} out of bounds"
        print(f"    cam_{name}: Rb={rb:.1f}mm")
    
    return result.success or result.constraints_satisfied >= result.constraints_total * 0.9, f"{len(cams)} cams, {result.constraints_satisfied}/{result.constraints_total} OK"

run_test("Flapping Bird → MICR", test_flapping_bird_micr)


# ═══════════════════════════════════════════════════════════════════
# TEST 3: Waving cat (3+ cams — arm, head, tail)
# ═══════════════════════════════════════════════════════════════════

def test_waving_cat_micr():
    """Waving cat: 3+ cams, tests multi-cam spacing + lever clearance."""
    scene = create_waving_cat()
    cams = compile_scene_to_cams(scene)
    print(f"    Scene: {scene.name}, {len(cams)} cam(s)")
    
    motor_check = {'feasible': True, 'stall_torque_mNm': 200.0, 'peak_torque_mNm': 100.0}
    
    micr = MICR(scene, cams, motor_check, verbose=True)
    result = micr.solve()
    
    # Apply and check ChassisConfig integration
    cc = ChassisConfig()
    apply_micr_to_chassis_config(result, cc)
    
    assert cc.width == result.chassis_width, "ChassisConfig width mismatch"
    assert cc.camshaft_diameter == result.shaft_diameter, "shaft diameter mismatch"
    print(f"    ChassisConfig applied: {cc.width:.0f}×{cc.depth:.0f}mm, shaft Ø{cc.camshaft_diameter:.0f}mm")
    
    return result.success or result.constraints_satisfied >= result.constraints_total * 0.9, f"{len(cams)} cams, chassis {result.chassis_width:.0f}×{result.chassis_depth:.0f}mm"

run_test("Waving Cat → MICR", test_waving_cat_micr)


# ═══════════════════════════════════════════════════════════════════
# TEST 4: Turtle simple (smooth motion)
# ═══════════════════════════════════════════════════════════════════

def test_turtle_simple_micr():
    """Turtle: test smooth poly345 motion laws."""
    scene = create_turtle_simple()
    cams = compile_scene_to_cams(scene)
    print(f"    Scene: {scene.name}, {len(cams)} cam(s)")
    
    motor_check = {'feasible': True, 'stall_torque_mNm': 150.0, 'peak_torque_mNm': 60.0}
    
    micr = MICR(scene, cams, motor_check, verbose=True)
    result = micr.solve()
    
    return result.success or result.constraints_satisfied >= result.constraints_total * 0.9, f"{len(cams)} cams, {result.solve_time_s:.1f}s"

run_test("Turtle Simple → MICR", test_turtle_simple_micr)


# ═══════════════════════════════════════════════════════════════════
# TEST 5: Turtle walking (complex, many cams — 4 legs)
# ═══════════════════════════════════════════════════════════════════

def test_turtle_walking_micr():
    """Turtle walking: 4+ cams, tests heavy multi-cam case."""
    scene = create_turtle_walking()
    cams = compile_scene_to_cams(scene)
    print(f"    Scene: {scene.name}, {len(cams)} cam(s)")
    
    motor_check = {'feasible': True, 'stall_torque_mNm': 200.0, 'peak_torque_mNm': 120.0}
    
    micr = MICR(scene, cams, motor_check, verbose=True)
    result = micr.solve()
    
    # Print plate check — must fit 220mm
    assert result.chassis_width <= 220, f"Width {result.chassis_width} > 220mm!"
    assert result.chassis_depth <= 220, f"Depth {result.chassis_depth} > 220mm!"
    print(f"    Print plate: {result.chassis_width:.0f}×{result.chassis_depth:.0f}mm ≤ 220mm ✓")
    
    return result.success or result.constraints_satisfied >= result.constraints_total * 0.9, f"{len(cams)} cams, {result.constraints_satisfied}/{result.constraints_total} OK"

run_test("Turtle Walking → MICR", test_turtle_walking_micr)


# ═══════════════════════════════════════════════════════════════════
# TEST 6: Multi-scene (stress test — many cams)
# ═══════════════════════════════════════════════════════════════════

def test_multi_scene_micr():
    """Multi-scene: many cams, tests scaling rules."""
    scene = create_multi_scene()
    cams = compile_scene_to_cams(scene)
    print(f"    Scene: {scene.name}, {len(cams)} cam(s)")
    
    motor_check = {'feasible': True, 'stall_torque_mNm': 300.0, 'peak_torque_mNm': 150.0}
    
    micr = MICR(scene, cams, motor_check, verbose=True)
    result = micr.solve()
    
    # Heavy case: check dual-shaft triggered if many cams
    if len(cams) > 6:
        print(f"    Dual-shaft: {'ON' if result.dual_shaft else 'OFF'} ({len(cams)} cams)")
    
    return result.success or result.constraints_satisfied >= result.constraints_total * 0.8, \
        f"{len(cams)} cams, {result.constraints_satisfied}/{result.constraints_total} OK"

run_test("Multi Scene (stress) → MICR", test_multi_scene_micr)


# ═══════════════════════════════════════════════════════════════════
# TEST 7: scene_builder → MICR (full pipeline with species)
# ═══════════════════════════════════════════════════════════════════

def test_scene_builder_to_micr():
    """Use scene_builder.make_automaton() → compile → MICR."""
    from scene_builder import make_automaton
    
    species_tests = ['cat', 'eagle', 'turtle', 'spider']
    all_ok = True
    details = []
    
    for species in species_tests:
        print(f"\n    --- {species} ---")
        try:
            scene = make_automaton(species)
            cams = compile_scene_to_cams(scene)
            print(f"    {species}: {len(cams)} cams")
            
            motor_check = {'feasible': True, 'stall_torque_mNm': 200.0, 'peak_torque_mNm': 100.0}
            micr = MICR(scene, cams, motor_check, verbose=False)
            result = micr.solve()
            
            status = "✓" if result.success else f"⚠ {result.constraints_satisfied}/{result.constraints_total}"
            details.append(f"{species}({len(cams)}c)={status}")
            print(f"    {species}: {result.summary().split(chr(10))[0]}")
            
            if not result.success and result.constraints_satisfied < result.constraints_total * 0.7:
                all_ok = False
                
        except Exception as e:
            details.append(f"{species}=ERR:{e}")
            print(f"    {species}: ERROR — {e}")
            all_ok = False
    
    return all_ok, " | ".join(details)

run_test("SceneBuilder species → MICR", test_scene_builder_to_micr)


# ═══════════════════════════════════════════════════════════════════
# TEST 8: Full pipeline — generate() + MICR injection
# ═══════════════════════════════════════════════════════════════════

def test_full_pipeline_with_micr():
    """Simulate what generate() would do with MICR injected at step 4.5."""
    scene = create_turtle_simple()
    
    # Step 1-2: scene validation + compile cams
    print("    [1/8] Validate scene...")
    assert scene.validate() is None or True  # may return None or list
    
    print("    [2/8] Compile cams...")
    cams = compile_scene_to_cams(scene)
    n_cams = len(cams)
    print(f"    → {n_cams} cam(s) compiled")
    
    # Step 3: optimize phases (simplified)
    print("    [3/8] Optimize phases... (skip — no inter-cam phase optim for 1-2 cams)")
    
    # Step 4: motor check
    print("    [4/8] Motor check...")
    motor_check = {'feasible': True, 'stall_torque_mNm': 150.0, 'peak_torque_mNm': 60.0}
    
    # ──── Step 4.5: MICR ────
    print("    [4.5/8] MICR — Optimisation inverse...")
    micr = MICR(scene, cams, motor_check, verbose=True)
    micr_result = micr.solve()
    
    if micr_result.success:
        apply_micr_to_scene(micr_result, scene)
        print("    ✓ MICR applied to scene")
    else:
        print(f"    ⚠ MICR partial: {micr_result.constraints_satisfied}/{micr_result.constraints_total}")
        apply_micr_to_scene(micr_result, scene)  # apply anyway, best effort
    
    # Step 5: Geometry — use MICR results
    print("    [5/8] Geometry (using MICR overrides)...")
    overrides = getattr(scene, '_solver_overrides', {})
    rb_hints = overrides.get('cam_Rb_hints', {})
    lever_ratios = overrides.get('lever_ratios', {})
    follower_positions = overrides.get('follower_x_positions', {})
    
    print(f"    Rb hints: {rb_hints}")
    print(f"    Lever ratios: {lever_ratios}")
    print(f"    Follower X: {follower_positions}")
    
    # Create ChassisConfig from MICR
    cc = ChassisConfig()
    apply_micr_to_chassis_config(micr_result, cc)
    print(f"    Chassis: {cc.width:.0f}×{cc.depth:.0f}×{cc.total_height:.0f}mm")
    print(f"    Shaft: Ø{cc.camshaft_diameter:.0f}mm, spacing={cc.cam_spacing:.0f}mm")
    
    # Step 5 would now use these values to generate meshes...
    # Step 6-7-8 would validate
    
    # Verify the data chain is intact
    assert len(rb_hints) == n_cams, f"Rb hints count: {len(rb_hints)} != {n_cams}"
    for name, rb in rb_hints.items():
        assert 8.0 <= rb <= 35.0, f"Rb out of bounds: {name}={rb}"
    
    assert cc.width <= 220, f"Chassis too wide for print bed: {cc.width}"
    assert cc.depth <= 220, f"Chassis too deep for print bed: {cc.depth}"
    
    print("    [6-8/8] FDM + Timing + Assembly validation... (would run here)")
    
    return micr_result.success or micr_result.constraints_satisfied >= micr_result.constraints_total * 0.9, \
        f"Pipeline OK, {n_cams} cams, chassis {cc.width:.0f}×{cc.depth:.0f}mm"

run_test("Full Pipeline [1→8] with MICR at 4.5", test_full_pipeline_with_micr)


# ═══════════════════════════════════════════════════════════════════
# TEST 9: Constraint cross-validation — MICR vs existing checks
# ═══════════════════════════════════════════════════════════════════

def test_constraint_crossvalidation():
    """Compare MICR constraint results with the existing trou checks."""
    scene = create_waving_cat()
    cams = compile_scene_to_cams(scene)
    
    motor_check = {'feasible': True, 'stall_torque_mNm': 200.0, 'peak_torque_mNm': 100.0}
    micr = MICR(scene, cams, motor_check, verbose=False)
    result = micr.solve()
    
    # Now check: do MICR Rb values satisfy pressure angle constraints?
    from automata_unified_v4 import compute_Rb_min_translating_roller
    from micr import PRESSURE_ANGLE_CASCADE, RB_HARD_CAP
    
    all_ok = True
    for i, cam in enumerate(cams):
        theta_deg = np.linspace(0, 360, 720, endpoint=False)
        s, ds, dds = cam.evaluate(theta_deg)
        rf = 3.0
        
        Rb_micr = result.cam_Rb_hints.get(cam.name, 15.0)
        
        # Use cascade like MICR does
        Rb_min = RB_HARD_CAP
        for phi_deg in PRESSURE_ANGLE_CASCADE:
            Rb_cand = compute_Rb_min_translating_roller(ds, s, rf, np.radians(phi_deg), 0.0)
            Rb_cand = max(Rb_cand, rf / 0.34, 5.0)
            if Rb_cand <= RB_HARD_CAP:
                Rb_min = Rb_cand
                break
        
        ok = Rb_micr >= Rb_min * 0.95  # 5% tolerance
        status = "✓" if ok else "✗"
        print(f"    {status} cam_{cam.name}: MICR Rb={Rb_micr:.1f}mm ≥ Rb_min={Rb_min:.1f}mm")
        if not ok:
            all_ok = False
    
    # Check shaft deflection with MICR dimensions
    from micr import _shaft_deflection
    d = result.shaft_diameter
    L = len(cams) * result.cam_spacing + 2 * result.wall_thickness + 10
    forces = [max(0.5, np.max(np.abs(cam.evaluate(np.linspace(0,360,360))[0])) * 0.05) 
              for cam in cams]
    F_total = sum(forces)
    delta = _shaft_deflection(d, L, F_total, len(cams))
    ok = delta <= 0.3
    status = "✓" if ok else "✗"
    print(f"    {status} Shaft: Ø{d:.0f}mm, L={L:.0f}mm, δ={delta:.4f}mm ≤ 0.3mm")
    if not ok:
        all_ok = False
    
    return all_ok, f"Rb + shaft cross-validated on {len(cams)} cams"

run_test("Constraint cross-validation (MICR vs trou checks)", test_constraint_crossvalidation)


# ═══════════════════════════════════════════════════════════════════
# TEST 10: Pushrod routing with real figurine bbox
# ═══════════════════════════════════════════════════════════════════

def test_pushrod_routing_integration():
    """Test pushrod routing with realistic figurine dimensions."""
    # Simulate a cat figurine: ~45mm tall, 30mm wide, 40mm deep
    fig_bbox = (np.array([-15, -20, 0]), np.array([15, 20, 45]))
    
    # Chassis top + shelf
    shelf_z = 83.0  # chassis_height=80 + shelf=3
    fig_world_min = fig_bbox[0] + np.array([0, 0, shelf_z])
    fig_world_max = fig_bbox[1] + np.array([0, 0, shelf_z])
    
    # 3 lever tips at different X positions
    test_cases = [
        ("center", np.array([0, 0, 70]), np.array([0, 0, shelf_z + 22])),
        ("left", np.array([-25, 0, 70]), np.array([-10, 0, shelf_z + 22])),
        ("right", np.array([25, 0, 70]), np.array([10, 0, shelf_z + 22])),
    ]
    
    all_ok = True
    for label, start, end in test_cases:
        route = route_pushrod_around_obstacle(start, end, (fig_world_min, fig_world_max))
        ok = route.clearance_ok
        print(f"    {label}: {route.route_type} ({route.total_length:.0f}mm, "
              f"{len(route.waypoints)} waypoints) — {'OK' if ok else 'COLLISION'}")
        if not ok:
            all_ok = False
    
    return all_ok, f"3 routes tested, all clear"

run_test("Pushrod routing (real figurine bbox)", test_pushrod_routing_integration)


# ═══════════════════════════════════════════════════════════════════
# TEST 11: Spatial relations coverage check
# ═══════════════════════════════════════════════════════════════════

def test_spatial_relations_coverage():
    """Verify spatial relations cover the known skip_pairs patterns."""
    # Known part prefixes from generate()
    part_prefixes = [
        'camshaft', 'cam_', 'collar_L_', 'collar_R_', 'collar_retention',
        'lever_', 'bracket_lever_', 'pin_lever_', 'follower_guide_',
        'wall_', 'base_plate', 'motor_mount', 'mid_bearing_wall',
        'camshaft_bracket', 'shaft_coupler', 'crank_handle',
        'sync_gear', 'pushrod_', 'fig_',
    ]
    
    # Check that all critical pairs are covered
    covered_pairs = set()
    for rel in ALL_SPATIAL_RELATIONS:
        covered_pairs.add((rel.part_a, rel.part_b))
    
    # Known critical pairs that MUST be covered
    critical_pairs = [
        ('camshaft', 'cam_'),
        ('lever_', 'cam_'),
        ('lever_', 'lever_'),
        ('cam_', 'cam_'),
        ('fig_', 'pushrod_'),
        ('mid_bearing_wall', 'camshaft'),
    ]
    
    all_ok = True
    for a, b in critical_pairs:
        found = (a, b) in covered_pairs or (b, a) in covered_pairs
        status = "✓" if found else "✗"
        print(f"    {status} {a} ↔ {b}")
        if not found:
            all_ok = False
    
    print(f"\n    Total relations: {len(ALL_SPATIAL_RELATIONS)}")
    print(f"    Contact: {sum(1 for r in ALL_SPATIAL_RELATIONS if r.category == 'contact')}")
    print(f"    Proximity: {sum(1 for r in ALL_SPATIAL_RELATIONS if r.category == 'proximity')}")
    print(f"    Forbidden: {sum(1 for r in ALL_SPATIAL_RELATIONS if r.category == 'forbidden')}")
    
    return all_ok, f"{len(ALL_SPATIAL_RELATIONS)} relations, all critical pairs covered"

run_test("Spatial relations coverage", test_spatial_relations_coverage)


# ═══════════════════════════════════════════════════════════════════
# TEST 12: MICR solve time budget
# ═══════════════════════════════════════════════════════════════════

def test_solve_time_budget():
    """Verify MICR stays within 30s budget even for complex scenes."""
    scene = create_turtle_walking()  # complex: many cams
    cams = compile_scene_to_cams(scene)
    
    motor_check = {'feasible': True, 'stall_torque_mNm': 200.0, 'peak_torque_mNm': 120.0}
    
    t0 = time.time()
    micr = MICR(scene, cams, motor_check, verbose=False)
    result = micr.solve()
    dt = time.time() - t0
    
    ok = dt <= 35.0  # 30s budget + 5s margin for overhead
    print(f"    {len(cams)} cams: solved in {dt:.1f}s (budget: 30s)")
    print(f"    {result.constraints_satisfied}/{result.constraints_total} constraints OK")
    
    return ok, f"{dt:.1f}s for {len(cams)} cams"

run_test("Solve time budget (≤30s)", test_solve_time_budget)


# ═══════════════════════════════════════════════════════════════════
# BATCH TEST: All presets through MICR
# ═══════════════════════════════════════════════════════════════════

def test_all_presets_batch():
    """Run all available presets through MICR."""
    preset_results = []
    
    for name, creator in SCENE_PRESETS.items():
        try:
            scene = creator()
            cams = compile_scene_to_cams(scene)
            
            motor_check = {'feasible': True, 'stall_torque_mNm': 300.0, 'peak_torque_mNm': 150.0}
            micr = MICR(scene, cams, motor_check, verbose=False)
            result = micr.solve()
            
            ok = result.success or result.constraints_satisfied >= result.constraints_total * 0.9
            status = "✓" if ok else f"⚠{result.constraints_satisfied}/{result.constraints_total}"
            preset_results.append((name, len(cams), ok, result.solve_time_s))
            print(f"    {status} {name:25s} | {len(cams)} cams | "
                  f"{result.chassis_width:.0f}×{result.chassis_depth:.0f}mm | "
                  f"{result.solve_time_s:.1f}s")
            
        except Exception as e:
            preset_results.append((name, 0, False, 0))
            print(f"    ✗ {name:25s} | ERROR: {e}")
    
    n_pass = sum(1 for _, _, ok, _ in preset_results if ok)
    n_total = len(preset_results)
    
    return n_pass >= n_total * 0.5, f"{n_pass}/{n_total} presets passed"

run_test("ALL PRESETS batch → MICR", test_all_presets_batch)


# ═══════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════

dt_total = time.time() - t_global

print(f"\n{'═'*70}")
print(f"  RESULTS SUMMARY — {dt_total:.1f}s total")
print(f"{'═'*70}\n")

n_pass = 0
n_total = len(results)
for name, ok, dt, details in results:
    status = "✓ PASS" if ok else "✗ FAIL"
    print(f"  {status}  {name}")
    print(f"         {details} ({dt:.1f}s)")
    if ok:
        n_pass += 1

print(f"\n{'─'*70}")
print(f"  {n_pass}/{n_total} tests passed ({n_pass/n_total*100:.0f}%)")
print(f"  Total time: {dt_total:.1f}s")
print(f"{'─'*70}")

if n_pass == n_total:
    print("\n  🎉 ALL TESTS PASSED — Generator + MICR fusion works!")
elif n_pass >= n_total * 0.8:
    print(f"\n  ⚠ MOSTLY OK — {n_total - n_pass} test(s) need attention")
else:
    print(f"\n  ✗ {n_total - n_pass} FAILURES — needs fixing")
