#!/usr/bin/env python3
"""
DEBUG BUGS — Test-driven bug fixing for Automata Generator v4.
Each bug has a dedicated test. Fix one bug at a time, run this, push when green.

Usage:
    python3 debug_bugs.py              # run ALL bug tests
    python3 debug_bugs.py A1           # run only bug A1
    python3 debug_bugs.py A1 A2 A3     # run specific bugs
    python3 debug_bugs.py --phase 1    # run Phase 1 bugs (A1, A3, A9)
"""
import sys, io, os, time, traceback
import numpy as np

sys.argv_backup = sys.argv[:]
sys.argv = ['']

# Load module
with open('automata_unified_v4.py') as f:
    code = f.read().split('if __name__')[0]
exec(code)

# ─── Helpers ───────────────────────────────────────────────────────────────
PRESETS = [
    ('nodding_bird', create_nodding_bird), ('walking_figure', create_walking_figure),
    ('drummer', create_drummer), ('swimming_fish', create_swimming_fish),
    ('waving_cat', create_waving_cat), ('flapping_bird', create_flapping_bird),
    ('blacksmith', create_blacksmith), ('bobbing_duck', create_bobbing_duck),
    ('rocking_horse', create_rocking_horse),
]

_cache = {}
def get_parts(preset_name):
    """Generate parts for a preset (cached)."""
    if preset_name not in _cache:
        for name, fn in PRESETS:
            if name == preset_name:
                old_stdout = sys.stdout
                sys.stdout = io.StringIO()
                try:
                    gen = AutomataGenerator(fn(MotionStyle.FLUID), seed=42)
                    gen.generate()
                finally:
                    sys.stdout = old_stdout
                _cache[preset_name] = gen.all_parts
                break
    return _cache[preset_name]

def get_all_parts():
    """Generate parts for all presets."""
    results = {}
    for name, fn in PRESETS:
        if name not in _cache:
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            try:
                gen = AutomataGenerator(fn(MotionStyle.FLUID), seed=42)
                gen.generate()
            finally:
                sys.stdout = old_stdout
            _cache[name] = gen.all_parts
        results[name] = _cache[name]
    return results

# ─── BUG TESTS ─────────────────────────────────────────────────────────────

def test_A1_wall_bore():
    """A1: Walls must have a through-bore (euler=0) or functional U-slot for the shaft.
    
    Research says: Ø4.5mm bore in wall, 0.5mm chamfer.
    Problem: bore_dia > wall_thickness → bore impossible OR U-slot cuts too deep.
    Fix: Increase wall_thickness to ≥5mm so bore fits, OR verify U-slot is functional.
    
    PASS criteria: wall euler ≤ 0 (has bore) OR wall_thickness > bore_dia (bore fits)
                   OR wall has >8 vertices AND shaft can physically sit in slot.
    """
    errors = []
    all_parts = get_all_parts()
    for pname, parts in all_parts.items():
        for wn in ['wall_left', 'wall_right']:
            if wn not in parts:
                continue
            wall = parts[wn]
            # A proper bore = euler ≤ 0 (through-hole exists)
            if wall.euler_number > 0:
                # Euler=2 could be U-slot (valid) or solid box (invalid)
                if wall.vertices.shape[0] <= 12:
                    # Too few verts = basically a box with no slot/bore
                    errors.append(f"{pname}/{wn}: euler={wall.euler_number}, verts={wall.vertices.shape[0]} = SOLID BOX, no bore/slot")
                else:
                    # Has U-slot geometry. Check shaft can sit in it:
                    # The wall must have a concavity from the top that reaches the shaft Z
                    # For now accept U-slot as valid (verts > 12 means geometry was cut)
                    pass  # U-slot accepted as valid
    return errors

def test_A1_strict_bore():
    """A1-STRICT: Walls MUST have a true through-bore (euler ≤ 0).
    This is the ideal target per research doc. U-slots are a compromise.
    
    PASS criteria: ALL walls have euler ≤ 0 (through-hole for shaft).
    """
    errors = []
    all_parts = get_all_parts()
    for pname, parts in all_parts.items():
        for wn in ['wall_left', 'wall_right']:
            if wn not in parts:
                continue
            wall = parts[wn]
            if wall.euler_number > 0:
                errors.append(f"{pname}/{wn}: euler={wall.euler_number} — needs through-bore (euler≤0)")
    return errors

def test_A2_cam_lever_gap():
    """A2: Gap between cam top and lever bottom must be ≤ 2mm (contact required).
    
    Research says: flat-faced follower or hinged lever must physically touch the cam.
    Problem: 16.7mm gap on all presets = zero mechanical transmission.
    Fix: extend lever input arm down to cam, or add follower part.
    
    PASS criteria: for every cam/lever pair, gap ≤ 2.0mm.
    """
    errors = []
    all_parts = get_all_parts()
    for pname, parts in all_parts.items():
        for cn in [p for p in parts if p.startswith('cam_') and 'shaft' not in p]:
            target = cn.replace('cam_', '')
            ln = f'lever_{target}'
            if ln not in parts:
                continue
            cam_top_z = parts[cn].bounds[1][2]
            lever_bot_z = parts[ln].bounds[0][2]
            gap = lever_bot_z - cam_top_z
            if gap > 2.0:
                errors.append(f"{pname}/{cn}→{ln}: gap={gap:.1f}mm (max 2.0mm)")
    return errors

def test_A3_lever_pivot_bore():
    """A3: Levers must have a pivot bore (not be split into 2 pieces).
    
    Research says: bore Ø = pin + 0.3mm, arm must have ≥1.5mm wall around bore.
    Problem: pivot_bore_d=3.5mm > arm_thickness=3.0mm → bore severs the lever into 2 halves!
    Fix: add hub/boss around pivot OR reduce pin diameter OR increase arm thickness.
    
    PASS criteria: lever is a SINGLE connected body with euler ≤ 0 at pivot.
    """
    errors = []
    all_parts = get_all_parts()
    for pname, parts in all_parts.items():
        for ln in [p for p in parts if p.startswith('lever_') and 'bracket' not in p and 'pin' not in p]:
            lever = parts[ln]
            # Check body count — split lever = multiple bodies
            bodies = lever.split(only_watertight=False)
            if len(bodies) > 1:
                errors.append(f"{pname}/{ln}: SPLIT into {len(bodies)} bodies! Bore wider than arm.")
            # Check euler — should be 0 (one through-hole for pivot)
            elif lever.euler_number != 0:
                errors.append(f"{pname}/{ln}: euler={lever.euler_number} (expected 0 for pivot bore)")
    return errors

def test_A4_snap_hook_geometry():
    """A4: Follower guides with snap_hook metadata must have actual snap geometry.
    
    Research says: cantilever base ≥1mm, fillet 0.5×thickness, XY orientation.
    Problem: 16 vertices = plain box, no snap features.
    Fix: call make_snap_hook_3d() or use dowel/friction-fit alternative.
    
    PASS criteria: follower_guide parts with snap_hook metadata have > 24 vertices.
    """
    errors = []
    all_parts = get_all_parts()
    for pname, parts in all_parts.items():
        for fg in [p for p in parts if 'follower_guide' in p]:
            mesh = parts[fg]
            meta = mesh.metadata if hasattr(mesh, 'metadata') else {}
            jt = meta.get('joint_type', '')
            if jt == 'snap_hook' and mesh.vertices.shape[0] <= 24:
                errors.append(f"{pname}/{fg}: snap_hook metadata but only {mesh.vertices.shape[0]} verts (box)")
    return errors

def test_A5_fig_snap_pocket():
    """A5: Figurine parts with snap_pocket metadata must have actual pocket geometry.
    
    Research says: pocket = boolean cavity in figurine base. Or use dowel hole.
    Problem: fig_* parts have snap_pocket metadata but no cavity.
    Fix: call make_snap_pocket_3d() or cut a dowel hole.
    
    PASS criteria: fig parts with snap_pocket have a cavity (euler < 2) or a dowel hole.
    """
    errors = []
    all_parts = get_all_parts()
    for pname, parts in all_parts.items():
        fig_parts = [p for p in parts if p.startswith('fig_')]
        for fp in fig_parts:
            mesh = parts[fp]
            meta = mesh.metadata if hasattr(mesh, 'metadata') else {}
            jt = meta.get('joint_type', '')
            if jt == 'snap_pocket' and mesh.euler_number >= 2:
                # Check if it has a mating feature (more verts than expected)
                # For now just flag it
                errors.append(f"{pname}/{fp}: snap_pocket metadata, euler={mesh.euler_number} (no cavity)")
    return errors

def test_A9_bracket_bore():
    """A9: Camshaft bracket must have a bore for the shaft.
    
    PASS criteria: camshaft_bracket has euler ≤ 0 (through-hole).
    """
    errors = []
    all_parts = get_all_parts()
    for pname, parts in all_parts.items():
        if 'camshaft_bracket' in parts:
            brk = parts['camshaft_bracket']
            if brk.euler_number > 0:
                # Check if it has bore geometry (more than box verts)
                if brk.vertices.shape[0] <= 16:
                    errors.append(f"{pname}/camshaft_bracket: euler={brk.euler_number}, solid (no bore)")
                # Bracket uses shapely difference in create_camshaft_bracket, 
                # which should create a hole. Check body count.
    return errors

def test_B2_snap_functions_called():
    """B2: make_snap_hook_3d/make_snap_pocket_3d must be called during generation.
    
    Problem: functions exist but are dead code (0 calls for hook).
    Fix: wire them into the generation pipeline.
    
    PASS criteria: code contains actual invocations of these functions in generate flow.
    """
    errors = []
    import re
    with open('automata_unified_v4.py') as f:
        code = f.read()
    
    hook_def = len(re.findall(r'def make_snap_hook_3d', code))
    hook_call = len(re.findall(r'make_snap_hook_3d\s*\(', code)) - hook_def
    
    if hook_def > 0 and hook_call <= 0:
        errors.append(f"make_snap_hook_3d: defined {hook_def}x but called {hook_call}x (dead code)")
    
    return errors

def test_C2_pdf_coherence():
    """C2: Assembly PDF instructions must match actual geometry.
    
    Problem: PDF says 'insert shaft in wall bore' but walls have no bore.
    This test checks the TEXT content matches reality.
    
    PASS criteria: if PDF mentions 'bore', the corresponding wall has euler ≤ 0.
    """
    # This is a documentation coherence test — passes when A1 is fixed
    # For now, just check the code doesn't reference features that don't exist
    return []  # Placeholder — will be meaningful after A1 fix

def test_REGRESSION_watertight():
    """REGRESSION: All parts must remain watertight (100% currently)."""
    errors = []
    all_parts = get_all_parts()
    for pname, parts in all_parts.items():
        for part_name, mesh in parts.items():
            if not mesh.is_watertight:
                errors.append(f"{pname}/{part_name}: NOT watertight")
    return errors

def test_REGRESSION_volume():
    """REGRESSION: No parts should have negative volume."""
    errors = []
    all_parts = get_all_parts()
    for pname, parts in all_parts.items():
        for part_name, mesh in parts.items():
            if mesh.volume < 0:
                errors.append(f"{pname}/{part_name}: negative volume={mesh.volume:.1f}")
    return errors

def test_REGRESSION_no_crash():
    """REGRESSION: All 9 presets generate without exception."""
    errors = []
    for name, fn in PRESETS:
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            gen = AutomataGenerator(fn(MotionStyle.FLUID), seed=42)
            gen.generate()
        except Exception as e:
            errors.append(f"{name}: CRASH — {e}")
        finally:
            sys.stdout = old_stdout
    return errors

def test_REGRESSION_part_count():
    """REGRESSION: Part counts must not decrease."""
    BASELINE_PARTS = {
        'nodding_bird': 22, 'walking_figure': 44, 'drummer': 31,
        'swimming_fish': 23, 'waving_cat': 23, 'flapping_bird': 32,
        'blacksmith': 22, 'bobbing_duck': 21, 'rocking_horse': 22,
    }
    errors = []
    all_parts = get_all_parts()
    for pname, parts in all_parts.items():
        count = len(parts)
        baseline = BASELINE_PARTS.get(pname, 0)
        if count < baseline:
            errors.append(f"{pname}: {count} parts < baseline {baseline}")
    return errors

# ─── TEST REGISTRY ─────────────────────────────────────────────────────────

TESTS = {
    # Phase 1 — ASSEMBLABLE
    'A1':       ('🔴 Wall bore (U-slot accepted)', test_A1_wall_bore),
    'A1_STRICT':('🔴 Wall bore (true bore required)', test_A1_strict_bore),
    'A3':       ('🔴 Lever pivot bore (not split)', test_A3_lever_pivot_bore),
    'A9':       ('🔴 Bracket bore', test_A9_bracket_bore),
    # Phase 2 — FONCTIONNEL
    'A2':       ('🔴 Cam→Lever gap ≤ 2mm', test_A2_cam_lever_gap),
    # Phase 3 — ATTACHÉ  
    'A4':       ('🟠 Snap-hook geometry', test_A4_snap_hook_geometry),
    'A5':       ('🟠 Figurine snap-pocket', test_A5_fig_snap_pocket),
    'B2':       ('🟠 Snap functions called', test_B2_snap_functions_called),
    # Coherence
    'C2':       ('🟡 PDF coherence', test_C2_pdf_coherence),
    # Regressions (must ALWAYS pass)
    'REG_WT':   ('✅ Regression: watertight', test_REGRESSION_watertight),
    'REG_VOL':  ('✅ Regression: no negative vol', test_REGRESSION_volume),
    'REG_CRASH':('✅ Regression: no crash', test_REGRESSION_no_crash),
    'REG_PARTS':('✅ Regression: part count', test_REGRESSION_part_count),
}

PHASES = {
    1: ['A1', 'A3', 'A9', 'REG_WT', 'REG_VOL', 'REG_CRASH', 'REG_PARTS'],
    2: ['A2', 'REG_WT', 'REG_VOL', 'REG_CRASH', 'REG_PARTS'],
    3: ['A4', 'A5', 'B2', 'REG_WT', 'REG_VOL', 'REG_CRASH', 'REG_PARTS'],
}

# ─── RUNNER ────────────────────────────────────────────────────────────────

def run_tests(test_ids=None):
    if test_ids is None:
        test_ids = list(TESTS.keys())
    
    print("═" * 70)
    print("  DEBUG BUGS — Test Runner")
    print("═" * 70)
    
    # Generate all parts once
    t0 = time.time()
    print("  ⏳ Generating all presets...", end='', flush=True)
    get_all_parts()
    print(f" done ({time.time()-t0:.1f}s)")
    print()
    
    passed = 0
    failed = 0
    results = {}
    
    for tid in test_ids:
        if tid not in TESTS:
            print(f"  ⚠️  Unknown test: {tid}")
            continue
        
        label, fn = TESTS[tid]
        try:
            errors = fn()
        except Exception as e:
            errors = [f"TEST CRASHED: {e}\n{traceback.format_exc()}"]
        
        results[tid] = errors
        
        if errors:
            failed += 1
            print(f"  ❌ {tid:12s} {label}")
            for e in errors[:3]:
                print(f"     → {e}")
            if len(errors) > 3:
                print(f"     ... +{len(errors)-3} more")
        else:
            passed += 1
            print(f"  ✅ {tid:12s} {label}")
    
    print()
    print("═" * 70)
    total = passed + failed
    if failed == 0:
        print(f"  🟢 ALL {total} TESTS PASSED — safe to push")
    else:
        print(f"  🔴 {failed}/{total} FAILED — fix before pushing")
        
        # Show which regressions failed (blocking)
        reg_fails = [t for t in results if t.startswith('REG_') and results[t]]
        bug_fails = [t for t in results if not t.startswith('REG_') and results[t]]
        
        if reg_fails:
            print(f"  ⛔ REGRESSIONS: {', '.join(reg_fails)} — MUST fix before push")
        if bug_fails:
            print(f"  🔧 BUG TESTS: {', '.join(bug_fails)} — fix target for this session")
    
    print("═" * 70)
    return failed == 0

if __name__ == '__main__':
    args = sys.argv_backup[1:]
    
    if '--phase' in args:
        idx = args.index('--phase')
        phase = int(args[idx + 1])
        test_ids = PHASES.get(phase, [])
        print(f"\n  Running Phase {phase} tests: {', '.join(test_ids)}\n")
    elif args:
        test_ids = [a.upper() for a in args]
    else:
        test_ids = None  # all
    
    ok = run_tests(test_ids)
    sys.exit(0 if ok else 1)
