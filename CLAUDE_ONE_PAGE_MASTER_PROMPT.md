# CLAUDE ONE-PAGE MASTER PROMPT (AUTOMATA V4)

Copy/paste the full prompt below into Claude.

---

You have access to this repo and can run code/tests. Work directly on the codebase.

## Objective
Fix the spatial assembly issues in `automata_unified_v4.py` so generated `assembly.stl` is mechanically coherent and printable.

Coordinate convention to enforce everywhere:
- X = width
- Y = depth
- Z = height (UP)

## Non-negotiable workflow
1. Before each fix: identify root cause with code references.
2. Apply exactly one logical fix.
3. Run validation commands.
4. Commit immediately.
5. Push immediately.
6. Continue to next fix.

Rule: **1 correction = 1 commit = 1 push**.

If blocked or uncertain:
- reason step by step,
- test hypotheses in code,
- if still blocked, do targeted web research (official docs / primary sources),
- implement the best defensible solution,
- document why.

## Priority bugs to fix
1. `_make_shaft_and_drive()`
- Current bug: translate then rotate moves shaft centroid incorrectly.
- Expected: rotate first, then translate, with shaft along Y and centered at Z=shaft height.

2. `create_bearing_wall()` and same pattern functions
- Current bug: wall height/depth axes swapped due to `extrude_polygon` semantics.
- Affected likely functions:
  - `create_bearing_wall()`
  - `create_bearing_wall_with_joints()`
  - `create_camshaft_bracket()`
  - `create_linear_follower_guide()`
  - chassis generators that call them
- Expected: wall vertical in Z, depth in Y, bores aligned with shaft axis.

3. Cam placement in `generate()` Step 5
- Current bug: cams placed at Z near floor.
- Expected: cam bores aligned to shaft centerline; cam thickness centered around shaft Z.

4. Follower hardcoded Z and related alignment metadata
- Remove hardcoded Z assumptions.
- Ensure followers, metadata bores, joints are derived from same shaft/chassis reference frame.

5. Oversized cam (`auto_design_cam`)
- Keep requested motion but prevent impossible packaging.
- Add constraints/strategy fallback (pressure angle tradeoff, lever ratio, follower radius, internal/groove option, or warning + auto-scale policy).

## Research questions you must answer (with links)
1. Does `trimesh.creation.extrude_polygon` always extrude along Z? Any direction/transform option?
2. How reliable is `trimesh` boolean `difference()` for box-cylinder bores? Which engines and failure modes?
3. Best practice for vertical wall + horizontal bore in trimesh: extrude+rotate vs box+CSG?
4. Correct transform math after `Rx(-pi/2)` to place bores exactly at world targets.
5. Practical methods to reduce cam size while preserving motion amplitude.

## Implementation guidance
- Prefer robust geometry pipelines over fragile booleans where possible.
- Keep functions pure and parameter-driven (no hidden hardcoded Z values).
- Centralize frame references (shaft center, cam plane, wall origins) to avoid drift.
- Add/adjust unit checks or geometry sanity assertions where useful.

## Validation checklist (run after each fix as applicable)
- Existing test mode, if present.
- Generation of at least one known profile (`nodding_bird`) without crash.
- Numeric alignment checks:
  - shaft axis orientation and centroid,
  - bearing bore center vs shaft axis,
  - cam bore centers on shaft line,
  - followers reach expected cam contact zones.
- STL exports generated successfully.

## Required deliverables in ONE FILE
Create/update one single report file in repo:
- `reports/deep_research_automata_v4.md`

That file must contain:
1. Executive summary.
2. Internet findings with source links.
3. Fix-by-fix changelog (commit hash per fix).
4. Validation results (commands + key outputs).
5. Remaining risks and next actions.

Keep everything on that single page/file (no scattered notes).

## Git discipline
- Commit message format:
  - `fix(spatial): <short description>`
  - `test(validation): <short description>` (if adding tests)
  - `docs(report): update deep research report`
- Push after every commit.
- If push fails, resolve (fetch/rebase), then push again.

## Start now
1. Locate spatial transform bugs.
2. Apply first minimal safe fix.
3. Validate.
4. Commit + push.
5. Update `reports/deep_research_automata_v4.md`.
6. Repeat until all priority bugs are addressed.

---

## Quick run commands (adapt to repo)
```bash
python automata_unified_v4.py --test
python automata_unified_v4.py --validate nodding_bird
```

## Core acceptance criteria
- Assembly respects X/Y/Z convention.
- Shaft, walls, bores, cams, followers are spatially coherent.
- No mechanically impossible placement remains in `assembly.stl`.
- All work is traceable by commits + pushes + one consolidated report file.
