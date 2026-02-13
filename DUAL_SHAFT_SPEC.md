# DUAL-SHAFT ARCHITECTURE — Complete Technical Specification

**Project:** 3D-Printed Automata Generator  
**Task:** DUAL-001 — Dual Parallel Shaft with 1:1 Sync Gear  
**Status:** Detection ✅ | Geometry ✅ | Constraints ✅ | Remaining: optimization  
**Date:** 2026-02-13  

---

## 1. Problem Statement

When an automata has >6 cams on a single shaft:
- Shaft deflection exceeds 0.3mm threshold (toy quality)
- Cam spacing compresses, causing axial overlap
- Total shaft length exceeds Ender-3 bed depth (220mm)
- Motor torque margin drops below safe 30%

**Solution:** Split cams across 2 parallel shafts synchronized by 1:1 spur gears.

---

## 2. Current Implementation Status

### 2.1 What EXISTS (commit d558391)

| Component | Status | Location |
|-----------|--------|----------|
| Auto-detection (>6 cams) | ✅ Working | `generate()` line ~8740 |
| ChassisConfig fields | ✅ Working | `dual_shaft`, `sync_gear_module`, etc. |
| Dual bore bracket | ✅ Working | `create_camshaft_bracket()` |
| Two parallel shafts (A/B) | ✅ Working | `_make_shaft_and_drive()` |
| Cam splitting (even/odd) | ✅ Working | `generate()` line ~8860 |
| Sync gear mesh generation | ✅ Working | `generate_involute_gear_mesh()` |
| Shaft-aware constraints | ✅ Working | `check_trou1_cam_collision()` + `trou11` |
| Follower X-offset for shaft B | ✅ Working | Cam meshes translated to ±x_off |

### 2.2 What's MISSING / Needs Improvement

| Gap | Priority | Description |
|-----|----------|-------------|
| Gear mesh validation | P2 | No check that gear teeth actually interlock (center distance) |
| Idler gear option | P3 | For same-direction rotation (currently gears reverse shaft B) |
| Mid-bearing for dual | P3 | Mid-bearing wall only works for single-shaft |
| BOM dual-shaft items | P2 | Second shaft, sync gears not in BOM output |
| Assembly guide dual | P2 | ASSEMBLY.md doesn't describe dual-shaft steps |
| Lever X-position | P1 | Levers still generated at X=0, not offset to their shaft |

---

## 3. Mechanical Design

### 3.1 Layout Geometry

```
TOP VIEW (looking down Z-axis)
                    
    Shaft A              Shaft B
    (drive)              (driven)
       ○──── d_c ────○
    -x_off    0    +x_off

    d_c = center distance = module × teeth
    x_off = d_c / 2
```

**Default parameters:**

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `sync_gear_module` | 1.5 mm | Good balance: printable teeth, reasonable gear size |
| `sync_gear_teeth` | 20 | Minimum for smooth mesh at module 1.5 |
| `sync_gear_pressure_angle` | 20° | ISO standard, good for PLA |
| `sync_gear_thickness` | 8 mm | Sufficient face width for PLA torque transfer |
| Center distance | 30 mm | = 1.5 × 20 |
| x_offset | ±15 mm | Half center distance |
| Backlash | 0.20 mm | FDM tolerance for PLA (0.4mm nozzle) |

### 3.2 Gear Specifications

**Involute spur gear pair (1:1 ratio):**

```
Pitch diameter:    d = m × z = 1.5 × 20 = 30.0 mm
Addendum:          ha = m = 1.5 mm
Dedendum:          hf = 1.25 × m = 1.875 mm
Outside diameter:  da = d + 2×ha = 33.0 mm
Root diameter:     df = d - 2×hf = 26.25 mm
Tooth thickness:   s = π×m/2 = 2.356 mm (at pitch circle)
Backlash:          0.20 mm circumferential (for FDM)
Base circle:       db = d × cos(20°) = 28.19 mm
```

**FDM printing guidelines for gears:**
- Print flat (gear axis = Z), layer height ≤ 0.15mm
- Minimum 5 wall lines for tooth strength
- Infill ≥ 50% (teeth are structural)
- PLA adequate for low-speed hand-crank automata (<10 RPM)
- Add 0.1mm oversize to bore for clearance fit on shaft

### 3.3 Rotation Direction

Two meshing spur gears rotate in **opposite directions**. This means:

- **Shaft A** (drive): clockwise
- **Shaft B** (driven): counter-clockwise

For cam mechanisms this is usually acceptable because:
1. Cam followers respond to radial profile, not rotation direction
2. Phase offsets can compensate for reversed timing on shaft B
3. If same-direction is required: add an **idler gear** between A and B

**Idler gear option (not yet implemented):**
- Same module/teeth as sync gears
- Does NOT change gear ratio (still 1:1)
- Adds ~30mm to chassis width
- Introduces one more mesh → slightly more backlash (+0.05mm cumulative)

### 3.4 Shaft Assignment Algorithm

Current: alternating (even indices → A, odd → B)

```python
shaft_A_indices = list(range(0, n_cams, 2))  # [0, 2, 4, 6, ...]
shaft_B_indices = list(range(1, n_cams, 2))  # [1, 3, 5, 7, ...]
```

**Potential improvement — balanced load assignment:**
Sort cams by Rb (largest first), assign greedily to shaft with fewer total load:

```python
# Future: load-balanced assignment
sorted_cams = sorted(enumerate(cams), key=lambda x: x[1].Rb, reverse=True)
load_A, load_B = 0, 0
for idx, cam in sorted_cams:
    if load_A <= load_B:
        shaft_A.append(idx); load_A += cam.Rb
    else:
        shaft_B.append(idx); load_B += cam.Rb
```

---

## 4. Constraint Engine Integration

### 4.1 Cam Collision (trou1) — FIXED

**Before:** All cams compared pairwise → false overlaps between different shafts.

**After:** Each cam tagged with `shaft_id` ('A', 'B', or 'single'). Only same-shaft pairs compared.

```python
# Skip comparison if cams are on different shafts
si = ci.get('shaft_id', 'single')
sj = cj.get('shaft_id', 'single')
if si != sj and si != 'single' and sj != 'single':
    continue
```

### 4.2 Shaft Deflection (trou11) — FIXED

**Before:** All cam loads summed on single shaft → massive deflection.

**After:** Per-shaft load calculation. Each shaft checked independently.

```python
# Dual-shaft: check each shaft with its own cams
for sid in ['A', 'B']:
    shaft_loads = [l for l in all_loads if l['shaft_id'] == sid]
    check_trou11_shaft_deflection(..., point_loads=shaft_loads)
```

### 4.3 Shaft Length (trou2)

**Before:** Total cam stack length assumed single shaft.

**After:** `extract_design_data` uses worst-case shaft (longer of A or B).

### 4.4 Gear Mesh Validation (TODO)

Needed checks:
- Center distance matches pitch diameter sum / 2
- Gear bore fits shaft diameter with clearance
- Gear thickness sufficient for torque: τ = F × r_pitch
- Contact ratio ≥ 1.2 for smooth operation

---

## 5. Species Affected

Species with >6 cams that trigger dual-shaft:

| Species | Cams | Split A/B | Status |
|---------|------|-----------|--------|
| spider | 9 | 5/4 | ✅ 94 parts, 94 wt |
| ant | 7 | 4/3 | ✅ 79 parts, 79 wt |
| scorpion | 10+ | 5+/5+ | ✅ 131 parts, 131 wt |
| crab | 8+ | 4+/4+ | ✅ 104 parts, 104 wt |
| lobster | 9+ | 5/4+ | ✅ 115 parts, 115 wt |
| octopus | 8+ | 4+/4+ | ✅ 82 parts, 82 wt |
| dragon | 9+ | 5/4+ | ✅ 102 parts, 102 wt |

---

## 6. Code Architecture

### 6.1 Data Flow

```
make_automaton('spider')
  → scene with 9 tracks/cams
  → AutomataGenerator.generate()
    → n_cams > 6 → chassis_config.enable_dual_shaft()
    → cam profiles generated (auto_design_cam)
    → cam meshes split: even→shaft_A (-15mm X), odd→shaft_B (+15mm X)
    → _make_shaft_and_drive():
        → 2 cylinders (camshaft_A, camshaft_B)
        → 2 involute gears (sync_gear_A, sync_gear_B) at shaft ends
        → drive (crank/motor) on shaft A only
    → create_camshaft_bracket(): 2 bore holes per bracket
    → self._dual_shaft_assignment stored for constraint engine
  → run_all_constraints():
    → extract_design_data() tags each cam with shaft_id
    → check_trou1: only same-shaft pairs
    → check_trou11: per-shaft deflection
```

### 6.2 Key Functions

| Function | File:Line | Role |
|----------|-----------|------|
| `ChassisConfig.enable_dual_shaft()` | ~1605 | Sets flags, computes x_offset |
| `generate_involute_gear_mesh()` | ~2020 | Creates sync gear STL mesh |
| `_make_shaft_and_drive()` | ~2138 | Builds dual shafts + gears |
| `create_camshaft_bracket()` | ~1810 | Bracket with 2 bore holes |
| `check_trou1_cam_collision()` | ~10677 | Shaft-aware collision check |
| `extract_design_data()` | ~17931 | Tags cams with shaft_id |

---

## 7. Involute Gear Generation

The `generate_involute_gear_mesh()` function creates watertight STL meshes for 3D printing:

### 7.1 Algorithm

1. Compute gear circles (base, pitch, addendum, dedendum)
2. Generate involute curve points from base to addendum
3. Mirror for symmetric tooth profile
4. Add root fillet arcs between teeth
5. Extrude 2D profile to 3D (top face, bottom face, tooth side walls)
6. Subtract central bore cylinder
7. Apply backlash by reducing tooth thickness

### 7.2 Parameters

```python
generate_involute_gear_mesh(
    module=1.5,              # ISO module (mm)
    teeth=20,                # tooth count
    pressure_angle_deg=20.0, # standard
    thickness=8.0,           # face width (mm)
    bore_diameter=4.3,       # shaft + 0.3mm clearance
    backlash_mm=0.20,        # FDM backlash
    n_involute_pts=20,       # curve resolution
)
```

### 7.3 Bug Fix (commit d558391)

`involute_points(r_addendum, r_addendum, 1)` caused division by zero when `n_pts=1`:

```python
# BEFORE (crashed):
r = r_start + (r_end - r_start) * i / (n_pts - 1)  # 0/0!

# AFTER (fixed):
r = r_start if n_pts <= 1 else r_start + (r_end - r_start) * i / (n_pts - 1)
```

---

## 8. Future Enhancements

### 8.1 Lever X-Offset (P1)
Currently levers are generated at X=0. For dual-shaft, each lever must be offset to its cam's shaft X position. This requires passing `cam_x_positions[idx]` through to lever generation.

### 8.2 Pushrod Routing (P1)
Pushrods from shaft B cams need to route around shaft A. May require angled pushrods or guide channels with X-offset.

### 8.3 BOM Update (P2)
Add to `generate_chassis_bom()`:
- 2× steel shaft Ø4mm (or Ø6mm)
- 2× sync gear (PLA, printed)
- Extra bearings/brackets for second shaft

### 8.4 Assembly Guide (P2)
Add dual-shaft assembly steps to ASSEMBLY.md:
1. Insert sync gears on both shafts
2. Verify gear mesh (manual rotation test)
3. Install shaft A with drive, shaft B through brackets
4. Check synchronization

### 8.5 Worm Gear Alternative (P3)
For high cam-count (>12), consider worm gear reduction:
- 10:1 or higher reduction
- One handle turn = partial cam rotation
- Allows complex sequences over multiple turns
- Rob Ives documented this approach for paper automata

---

## 9. Test Results

### Before Fix (commit pre-d558391)
```
7 CRASHES: spider, ant, scorpion, crab, lobster, octopus, dragon
Root cause: ZeroDivisionError in involute_points()
```

### After Fix (commit d558391)
```
17/17 ALL PASS
- 0 crashes
- All dual-shaft species: 100% watertight
- Constraint errors reduced from ~10 to 1 (DOCS_MISSING only)
- False CAM_SOLID_INTERSECTION eliminated
- Shaft deflection checked per-shaft
```

---

## 10. References

- **SIGGRAPH Asia 2021** — "3D Cam Mechanisms" (Cheng et al.) — Composite cam-follower optimization
- **ISO 1328** — Cylindrical gear tolerances
- **DIN 3960** — Involute gear geometry
- **Cabaret Mechanical Theatre** — Dug's Tips on cam followers
- **EngineerDog** — Practical guide to FDM 3D printing gears
- **HowToMechatronics** — 3D printed gear strength testing (module 1.5, PLA)
- **Rob Ives** — Worm gear + cam prototyping for paper automata
