#!/usr/bin/env python3
"""
REGRESSION TEST — Run after EVERY change before pushing.
Compares current state to baseline. Blocks push if anything regressed.

Usage:
    python3 regression_test.py          # full regression
    python3 regression_test.py --quick  # just errors + parts count
"""
import sys, io, json, time, os

sys.argv_backup = sys.argv[:]
sys.argv = ['']

# Load the main module
with open('automata_unified_v4.py') as f:
    code = f.read().split('if __name__')[0]
exec(code)

BASELINE = {
    'nodding_bird':   {'errors': 0, 'asm': 1,  'parts': 23, 'levers': 1, 'brackets': 1},
    'walking_figure': {'errors': 0, 'asm': 17, 'parts': 48, 'levers': 4, 'brackets': 4},
    'drummer':        {'errors': 2, 'asm': 11, 'parts': 33, 'levers': 2, 'brackets': 2},
    'swimming_fish':  {'errors': 0, 'asm': 1,  'parts': 24, 'levers': 1, 'brackets': 1},
    'waving_cat':     {'errors': 0, 'asm': 2,  'parts': 24, 'levers': 1, 'brackets': 1},
    'flapping_bird':  {'errors': 0, 'asm': 12, 'parts': 40, 'levers': 3, 'brackets': 3},
    'blacksmith':     {'errors': 0, 'asm': 3,  'parts': 23, 'levers': 1, 'brackets': 1},
    'bobbing_duck':   {'errors': 0, 'asm': 2,  'parts': 22, 'levers': 1, 'brackets': 1},
    'rocking_horse':  {'errors': 0, 'asm': 4,  'parts': 34, 'levers': 2, 'brackets': 2},
}

PRESETS = [
    ('nodding_bird', create_nodding_bird), ('walking_figure', create_walking_figure),
    ('drummer', create_drummer), ('swimming_fish', create_swimming_fish),
    ('waving_cat', create_waving_cat), ('flapping_bird', create_flapping_bird),
    ('blacksmith', create_blacksmith), ('bobbing_duck', create_bobbing_duck),
    ('rocking_horse', create_rocking_horse),
]

def run_regression(quick=False):
    print("=" * 70)
    print("  REGRESSION TEST — comparing to baseline")
    print("=" * 70)
    
    regressions = []
    improvements = []
    
    for name, creator in PRESETS:
        sys.stdout = io.StringIO()
        try:
            gen = AutomataGenerator(creator(MotionStyle.FLUID), seed=42)
            result = gen.generate()
            sys.stdout = sys.__stdout__
        except Exception as e:
            sys.stdout = sys.__stdout__
            print(f"  💀 {name:20s} CRASH: {e}")
            regressions.append(f"{name}: CRASH — {e}")
            continue
        
        cv = result.get('constraint_violations', [])
        av = result.get('assembly_violations', [])
        crit = [v for v in cv if v.severity == Severity.ERROR]
        warn = [v for v in cv if v.severity == Severity.WARNING]
        parts = len(gen.all_parts)
        levers = len([p for p in gen.all_parts if p.startswith('lever_')])
        brackets = len([p for p in gen.all_parts if p.startswith('bracket_lever_')])
        watertight = sum(1 for p in gen.all_parts.values() if hasattr(p, 'is_watertight') and p.is_watertight)
        
        bl = BASELINE[name]
        
        # Check regressions
        issues = []
        if len(crit) > bl['errors']:
            issues.append(f"errors {bl['errors']}→{len(crit)}")
        if len(av) > bl['asm']:
            issues.append(f"asm {bl['asm']}→{len(av)}")
        if parts < bl['parts']:
            issues.append(f"parts {bl['parts']}→{parts} (LOST)")
        if levers < bl['levers']:
            issues.append(f"levers {bl['levers']}→{levers} (LOST)")
        if brackets < bl['brackets']:
            issues.append(f"brackets {bl['brackets']}→{brackets} (LOST)")
        if watertight < parts:
            issues.append(f"watertight {watertight}/{parts}")
        
        # Check improvements
        impr = []
        if len(crit) < bl['errors']:
            impr.append(f"errors {bl['errors']}→{len(crit)}")
        if parts > bl['parts']:
            impr.append(f"parts {bl['parts']}→{parts}")
        
        if issues:
            flag = '🔴 REGRESS'
            regressions.append(f"{name}: {', '.join(issues)}")
        elif impr:
            flag = '🟢 IMPROVED'
            improvements.append(f"{name}: {', '.join(impr)}")
        else:
            flag = '✅ OK      '
        
        err_detail = ""
        if len(crit) > 0:
            err_detail = f" [{', '.join(v.code for v in crit[:3])}]"
        
        print(f"  {flag} {name:20s} {len(crit)}E {len(warn)}W asm={len(av)} parts={parts} lev={levers} brk={brackets} wt={watertight}/{parts}{err_detail}")
    
    # Test master — just run via subprocess
    print()
    import subprocess
    r = subprocess.run(['python3', 'automata_unified_v4.py', '--test'],
                       capture_output=True, text=True, timeout=120)
    if 'ALL PASS' in r.stdout:
        print("  ✅ test_master: ALL PASS")
    else:
        print(f"  🔴 test_master: FAIL")
        last_lines = r.stdout.strip().split('\n')[-5:]
        for l in last_lines:
            print(f"     {l}")
        regressions.append("test_master failed")
    
    # Summary
    print()
    print("=" * 70)
    if regressions:
        print(f"  🔴 REGRESSION DETECTED — DO NOT PUSH")
        for r in regressions:
            print(f"     ↳ {r}")
        print("=" * 70)
        return False
    else:
        if improvements:
            for i in improvements:
                print(f"  🟢 {i}")
        print(f"  ✅ NO REGRESSIONS — SAFE TO PUSH")
        print("=" * 70)
        return True

if __name__ == '__main__':
    quick = '--quick' in sys.argv_backup
    ok = run_regression(quick)
    sys.exit(0 if ok else 1)
