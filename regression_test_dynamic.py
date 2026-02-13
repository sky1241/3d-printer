#!/usr/bin/env python3
"""Regression test: 17 builders via make_automaton() — dynamic pipeline."""
import sys
from scene_builder import make_automaton
import automata_unified_v4 as au

DYNAMIC_BASELINES = {
    'chat': {'parts': 74, 'wt': 74},
    'human': {'parts': 41, 'wt': 41},
    'eagle': {'parts': 54, 'wt': 54},
    'snake': {'parts': 28, 'wt': 28},
    'dolphin': {'parts': 37, 'wt': 37},
    'ant': {'parts': 78, 'wt': 78},
    'butterfly': {'parts': 45, 'wt': 45},
    'spider': {'parts': 91, 'wt': 91},
    'scorpion': {'parts': 128, 'wt': 128},
    'crab': {'parts': 102, 'wt': 102},
    'lobster': {'parts': 113, 'wt': 113},
    'centipede': {'parts': 48, 'wt': 48},
    'octopus': {'parts': 80, 'wt': 80},
    'snail': {'parts': 45, 'wt': 45},
    'sunflower': {'parts': 20, 'wt': 20},
    't-rex': {'parts': 64, 'wt': 64},
    'dragon': {'parts': 99, 'wt': 99},
}

def run():
    fails = []
    for animal, expected in DYNAMIC_BASELINES.items():
        try:
            scene = make_automaton(animal)
            gen = au.AutomataGenerator(scene)
            gen.generate()
            
            n = len(gen.all_parts)
            wt = sum(1 for m in gen.all_parts.values() if m.is_watertight)
            
            # Check part count
            if n != expected['parts']:
                fails.append(f"{animal}: parts {expected['parts']}→{n}")
            # Check watertight
            if wt != expected['wt']:
                fails.append(f"{animal}: wt {expected['wt']}→{wt}")
            
            # Check constraints don't crash
            report = au.run_all_constraints(gen, verbose=False)
            
            # Check all walls have through-bores (A1_STRICT)
            for wn in ['wall_left', 'wall_right']:
                wall = gen.all_parts.get(wn)
                if wall and wall.euler_number > 0:
                    fails.append(f"{animal}/{wn}: euler={wall.euler_number} (needs ≤0)")
            
            status = "✅" if not any(animal in f for f in fails) else "❌"
            print(f"  {status} {animal:12s}: {n} parts, {wt} wt")
            
        except Exception as e:
            fails.append(f"{animal}: CRASH — {e}")
            print(f"  ❌ {animal:12s}: CRASH — {e}")
    
    print()
    if fails:
        print("=" * 70)
        print(f"  🔴 {len(fails)} REGRESSION(S) DETECTED")
        for f in fails:
            print(f"     ↳ {f}")
        print("=" * 70)
        return 1
    else:
        print("=" * 70)
        print(f"  ✅ ALL 17 BUILDERS PASS — dynamic pipeline OK")
        print("=" * 70)
        return 0

if __name__ == '__main__':
    sys.exit(run())
