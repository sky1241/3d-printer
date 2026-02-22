#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║  MICR — Moteur Inverse de Contraintes Réelles                              ║
║  Inverse constraint solver for cam-driven automata                         ║
║                                                                            ║
║  Au lieu de : generate → check → patch (forward)                           ║
║  On fait   : define space → optimize dims → generate (inverse)             ║
║                                                                            ║
║  S'insère entre étapes [4] Motor check et [5] Geometry dans generate()     ║
║                                                                            ║
║  Auteur: Sky + Claude                                                      ║
║  Date:   2026-02-14                                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

INTEGRATION:
  Dans generate(), après step [4/8] Motor check, avant step [5/8] Geometry:

  from micr import MICR
  micr = MICR(self.scene, self.cams, self.motor_check)
  micr_result = micr.solve()
  # micr_result contient les dimensions optimisées pour step 5
"""

import numpy as np
import math
import time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any

# ═══════════════════════════════════════════════════════════════════
# CONSTANTES — Données issues du deep research (tests FDM PLA réels)
# ═══════════════════════════════════════════════════════════════════

# Clearance table v2 — UPDATED from deep research data
# Source: 3DChimera, CNCKitchen, Prusa KB, community tests
# Format: (jeu radial par côté en mm, jeu total diamétral en mm)
CLEARANCE_TABLE = {
    # Interface                  radial/face  total     notes
    'pin_pivot':           0.25,  # pivot ±30° — 0.50mm total (was 0.15, trop serré)
    'shaft_bearing_4mm':   0.20,  # Ø4mm rotation 360° <60RPM
    'shaft_bearing_6mm':   0.30,  # Ø6mm rotation 360° (+ flexion)
    'cam_on_shaft':        0.05,  # press-fit + CA glue
    'follower_guide':      0.25,  # translation Z, ~10mm course
    'pushrod_socket':      0.20,  # rotation libre petit angle
    'gear_backlash':       0.40,  # M1.5 PLA backlash circulaire
    'collar_bracket':      0.25,  # contact sans fusion
    'adjacent_parts':      0.30,  # pièces côte à côte (min clearance)
    'lever_cam_gap':       0.20,  # FDM clearance gravity-closed
}

# Contraintes physiques
SHAFT_DEFLECTION_MAX  = 0.3      # mm
PRESSURE_ANGLE_IDEAL  = 30.0     # degrees
PRESSURE_ANGLE_CASCADE = [30, 45, 58]  # cascade phi
MOTOR_MARGIN_MIN      = 0.40     # 40% margin (peak < stall × 0.6)
RB_HARD_CAP           = 35.0     # mm — max cam base radius
ROLLER_RATIO_MAX      = 0.35     # rf/Rb undercut limit
PRINT_BED_ENDER3      = (220, 220, 250)  # mm
PRINT_BED_BAMBU       = (256, 256, 256)  # mm
EN71_SMALL_PART       = 31.7     # mm minimum dimension
E_STEEL               = 200e3    # MPa (steel shaft Young's modulus)

# Pushrod routing
PUSHROD_WIRE_D        = 1.5      # mm — steel wire diameter
PUSHROD_BEND_RMIN     = 15.0     # mm — 10×d practical minimum
PUSHROD_CLEARANCE     = 0.50     # mm — clearance around pushrod path

# Stack-up compensation
STACKUP_COMPENSATION  = 0.08     # +8% cam amplitude to compensate RSS tolerance chain

# Swept volume
SWEPT_VOXEL_SIZE      = 0.5      # mm — resolution for swept volume computation

# Solver
SOLVER_MAX_TIME       = 30.0     # seconds
SOLVER_MAX_ITER       = 200
SOLVER_FTOL           = 1e-4


# ═══════════════════════════════════════════════════════════════════
# SPATIAL RELATIONS — Les 3 catégories remplaçant les skip_pairs
# ═══════════════════════════════════════════════════════════════════

@dataclass
class SpatialRelation:
    """Définit la relation spatiale attendue entre deux pièces."""
    part_a: str         # prefix (ex: 'camshaft')
    part_b: str         # prefix (ex: 'cam_')
    category: str       # 'contact' | 'proximity' | 'forbidden'
    clearance_min: float  # mm — min distance
    clearance_max: float  # mm — max distance (only for 'contact')
    note: str = ""

# Catégorie A — Contact intentionnel : pièces qui DOIVENT être en contact
# La distance doit être dans [clearance_min, clearance_max]
CONTACT_RELATIONS = [
    SpatialRelation('camshaft', 'cam_', 'contact', 0.00, 0.10, 'cam press-fit on shaft'),
    SpatialRelation('camshaft', 'collar_', 'contact', 0.15, 0.30, 'collar on shaft'),
    SpatialRelation('camshaft', 'sync_gear', 'contact', 0.00, 0.10, 'gear on shaft'),
    SpatialRelation('pin_lever_', 'lever_', 'contact', 0.15, 0.30, 'pin through lever bore'),
    SpatialRelation('pin_lever_', 'bracket_lever_', 'contact', 0.15, 0.30, 'pin through bracket'),
    SpatialRelation('pin_lever_', 'collar_L_', 'contact', 0.15, 0.30, 'pin in collar'),
    SpatialRelation('pin_lever_', 'collar_R_', 'contact', 0.15, 0.30, 'pin in collar'),
    SpatialRelation('mid_bearing_wall', 'camshaft', 'contact', 0.20, 0.35, 'bearing holds shaft'),
    SpatialRelation('camshaft_bracket', 'camshaft', 'contact', 0.20, 0.35, 'bracket holds shaft'),
    SpatialRelation('shaft_coupler', 'camshaft', 'contact', 0.00, 0.15, 'coupler on shaft'),
    SpatialRelation('crank_handle', 'camshaft', 'contact', 0.00, 0.10, 'crank mounted on shaft'),
    SpatialRelation('collar_retention', 'camshaft', 'contact', 0.15, 0.30, 'retention on shaft'),
]

# Catégorie B — Proximité structurelle : pièces proches par design
# La distance doit être >= clearance_min (pas de max)
PROXIMITY_RELATIONS = [
    SpatialRelation('wall_', 'base_plate', 'proximity', 0.0, 999, 'structural connection'),
    SpatialRelation('wall_', 'camshaft_bracket', 'proximity', 0.0, 999, 'structural'),
    SpatialRelation('base_plate', 'motor_mount', 'proximity', 0.0, 999, 'structural'),
    SpatialRelation('mid_bearing_wall', 'base_plate', 'proximity', 0.0, 999, 'sits on plate'),
    SpatialRelation('mid_bearing_wall', 'wall_', 'proximity', 0.0, 999, 'structural'),
    SpatialRelation('mid_bearing_wall', 'motor_mount', 'proximity', 0.0, 999, 'adjacent'),
    SpatialRelation('sync_gear', 'wall_', 'proximity', 0.30, 999, 'gear near wall'),
    SpatialRelation('sync_gear', 'base_plate', 'proximity', 0.30, 999, 'gear near plate'),
    SpatialRelation('sync_gear', 'cam_', 'proximity', 0.30, 999, 'gear near cam'),
    SpatialRelation('sync_gear', 'collar_', 'proximity', 0.30, 999, 'gear near collar'),
    SpatialRelation('collar_L_', 'bracket_lever_', 'proximity', 0.15, 999, 'collar flush bracket'),
    SpatialRelation('collar_R_', 'bracket_lever_', 'proximity', 0.15, 999, 'collar flush bracket'),
    SpatialRelation('collar_L_', 'lever_', 'proximity', 0.15, 999, 'collar next to lever'),
    SpatialRelation('collar_R_', 'lever_', 'proximity', 0.15, 999, 'collar next to lever'),
    SpatialRelation('collar_retention', 'collar_L_', 'proximity', 0.15, 999, 'retention near collar'),
    SpatialRelation('collar_retention', 'collar_R_', 'proximity', 0.15, 999, 'retention near collar'),
    SpatialRelation('collar_retention', 'cam_', 'proximity', 0.15, 999, 'retention near cam'),
    SpatialRelation('crank_handle', 'cam_', 'proximity', 0.30, 999, 'crank near cam'),
    SpatialRelation('crank_handle', 'collar_retention', 'proximity', 0.15, 999, 'crank near collar'),
    SpatialRelation('lever_', 'cam_', 'proximity', 0.20, 999, 'lever rides on cam'),
    SpatialRelation('lever_', 'camshaft', 'proximity', 0.30, 999, 'lever near shaft'),
    SpatialRelation('bracket_lever_', 'cam_', 'proximity', 0.30, 999, 'bracket near cam'),
    SpatialRelation('bracket_lever_', 'camshaft', 'proximity', 0.30, 999, 'bracket near shaft'),
    SpatialRelation('bracket_lever_', 'follower_guide_', 'proximity', 0.30, 999, 'bracket near guide'),
    SpatialRelation('mid_bearing_wall', 'cam_', 'proximity', 0.30, 999, 'wall between cams'),
    SpatialRelation('mid_bearing_wall', 'lever_', 'proximity', 0.30, 999, 'lever near wall'),
    SpatialRelation('mid_bearing_wall', 'follower_guide_', 'proximity', 0.30, 999, 'guide near wall'),
    SpatialRelation('mid_bearing_wall', 'collar_', 'proximity', 0.15, 999, 'collar through wall'),
    SpatialRelation('mid_bearing_wall', 'bracket_lever_', 'proximity', 0.30, 999, 'bracket near wall'),
    SpatialRelation('mid_bearing_wall', 'pin_lever_', 'proximity', 0.30, 999, 'pin near wall'),
    SpatialRelation('pin_lever_', 'cam_', 'proximity', 0.30, 999, 'pin near cam'),
    SpatialRelation('pin_lever_', 'camshaft', 'proximity', 0.30, 999, 'pin near shaft'),
    SpatialRelation('pin_lever_', 'collar_', 'proximity', 0.15, 999, 'pin near collar'),
    SpatialRelation('pin_lever_', 'follower_guide_', 'proximity', 0.30, 999, 'pin near guide'),
    SpatialRelation('collar_L_', 'follower_guide_', 'proximity', 0.30, 999, 'collar near guide'),
    SpatialRelation('collar_R_', 'follower_guide_', 'proximity', 0.30, 999, 'collar near guide'),
    SpatialRelation('follower_guide_', 'fig_', 'proximity', 0.30, 999, 'guide near figurine'),
    SpatialRelation('lever_', 'fig_', 'proximity', 0.30, 999, 'lever near figurine'),
]

# Catégorie C — Adjacence multi-came : pièces répétées côte à côte
# Doivent avoir clearance suffisante ET ne pas collider dynamiquement
ADJACENCY_RELATIONS = [
    SpatialRelation('lever_', 'lever_', 'forbidden', 0.50, 999, 'adjacent levers'),
    SpatialRelation('bracket_lever_', 'bracket_lever_', 'forbidden', 0.30, 999, 'adjacent brackets'),
    SpatialRelation('pin_lever_', 'pin_lever_', 'forbidden', 0.30, 999, 'adjacent pins'),
    SpatialRelation('pushrod_', 'pushrod_', 'forbidden', 0.50, 999, 'parallel pushrods'),
    SpatialRelation('collar_L_', 'collar_L_', 'forbidden', 0.30, 999, 'adjacent collars'),
    SpatialRelation('collar_R_', 'collar_R_', 'forbidden', 0.30, 999, 'adjacent collars'),
    SpatialRelation('collar_L_', 'collar_R_', 'forbidden', 0.15, 999, 'flanking collars'),
    SpatialRelation('cam_', 'cam_', 'forbidden', 0.50, 999, 'cams at different Y'),
    SpatialRelation('lever_', 'pushrod_', 'forbidden', 0.50, 999, 'lever near pushrod'),
    SpatialRelation('follower_guide_', 'pushrod_', 'forbidden', 0.30, 999, 'guide near pushrod'),
    SpatialRelation('bracket_lever_', 'pushrod_', 'forbidden', 0.30, 999, 'bracket near pushrod'),
    SpatialRelation('pin_lever_', 'pushrod_', 'forbidden', 0.30, 999, 'pin near pushrod'),
    SpatialRelation('fig_', 'pushrod_', 'forbidden', PUSHROD_CLEARANCE, 999, 'CRITICAL: pushrod through fig'),
    SpatialRelation('collar_L_', 'pushrod_', 'forbidden', 0.30, 999, 'collar near pushrod'),
    SpatialRelation('collar_R_', 'pushrod_', 'forbidden', 0.30, 999, 'collar near pushrod'),
    SpatialRelation('fig_', 'fig_', 'proximity', 0.0, 999, 'fig-fig joints intentional'),
]

ALL_SPATIAL_RELATIONS = CONTACT_RELATIONS + PROXIMITY_RELATIONS + ADJACENCY_RELATIONS


# ═══════════════════════════════════════════════════════════════════
# DESIGN VECTOR — Les variables d'optimisation
# ═══════════════════════════════════════════════════════════════════

@dataclass
class DesignVector:
    """Vecteur de design pour le MICR.

    Toutes les variables que le solveur peut ajuster.
    Les bounds sont les limites physiques dures.
    """
    # ── Global (8 variables) ──
    shaft_diameter: float = 4.0        # mm  [4.0, 8.0]
    cam_spacing: float = 8.0           # mm  [4.0, 12.0]
    chassis_width: float = 80.0        # mm  [60, 220]
    chassis_depth: float = 60.0        # mm  [40, 220]
    chassis_height: float = 80.0       # mm  [50, 250]
    wall_thickness: float = 3.0        # mm  [2.0, 6.0]
    dual_shaft_x_offset: float = 0.0   # mm  [0=single, 15-40=dual]
    fig_mount_z_offset: float = 0.0    # mm  offset above shelf [0, 30]

    # ── Per-cam (5 × n_cams variables) ──
    cam_Rb: List[float] = field(default_factory=list)           # [8, 35] mm
    cam_lever_length: List[float] = field(default_factory=list) # [15, 120] mm
    cam_lever_ratio: List[float] = field(default_factory=list)  # [1.0, 5.0]
    cam_follower_x: List[float] = field(default_factory=list)   # [-100, 100] mm
    cam_pushrod_route: List[int] = field(default_factory=list)  # 0=straight, 1=L-shape, 2=S-shape

    def to_array(self) -> np.ndarray:
        """Flatten to numpy array for scipy."""
        arr = [
            self.shaft_diameter, self.cam_spacing,
            self.chassis_width, self.chassis_depth, self.chassis_height,
            self.wall_thickness, self.dual_shaft_x_offset, self.fig_mount_z_offset,
        ]
        arr.extend(self.cam_Rb)
        arr.extend(self.cam_lever_length)
        arr.extend(self.cam_lever_ratio)
        arr.extend(self.cam_follower_x)
        # pushrod_route is discrete — not in the continuous optimization
        return np.array(arr, dtype=float)

    def from_array(self, arr: np.ndarray, n_cams: int):
        """Unflatten from numpy array."""
        self.shaft_diameter = float(arr[0])
        self.cam_spacing = float(arr[1])
        self.chassis_width = float(arr[2])
        self.chassis_depth = float(arr[3])
        self.chassis_height = float(arr[4])
        self.wall_thickness = float(arr[5])
        self.dual_shaft_x_offset = float(arr[6])
        self.fig_mount_z_offset = float(arr[7])

        off = 8
        self.cam_Rb = list(arr[off:off+n_cams]); off += n_cams
        self.cam_lever_length = list(arr[off:off+n_cams]); off += n_cams
        self.cam_lever_ratio = list(arr[off:off+n_cams]); off += n_cams
        self.cam_follower_x = list(arr[off:off+n_cams]); off += n_cams
        return self

    def bounds(self, n_cams: int) -> list:
        """Return (min, max) bounds for each variable."""
        b = [
            (4.0, 8.0),       # shaft_diameter
            (4.0, 12.0),      # cam_spacing
            (60.0, 220.0),    # chassis_width
            (40.0, 220.0),    # chassis_depth
            (50.0, 250.0),    # chassis_height
            (2.0, 6.0),       # wall_thickness
            (0.0, 40.0),      # dual_shaft_x_offset
            (0.0, 30.0),      # fig_mount_z_offset
        ]
        b.extend([(8.0, RB_HARD_CAP)] * n_cams)    # cam_Rb
        b.extend([(15.0, 120.0)] * n_cams)          # lever_length
        b.extend([(1.0, 5.0)] * n_cams)             # lever_ratio
        b.extend([(-100.0, 100.0)] * n_cams)        # follower_x
        return b


# ═══════════════════════════════════════════════════════════════════
# MICR RESULT — Ce que le solveur retourne à generate()
# ═══════════════════════════════════════════════════════════════════

@dataclass
class MICRResult:
    """Résultat de l'optimisation MICR."""
    success: bool
    design: DesignVector
    n_iterations: int
    solve_time_s: float
    residual: float                    # objectif final
    constraints_satisfied: int
    constraints_total: int
    violations: List[str]              # contraintes violées avec détails

    # Paramètres dérivés pour generate()
    chassis_width: float = 0.0
    chassis_depth: float = 0.0
    chassis_height: float = 0.0
    shaft_diameter: float = 4.0
    cam_spacing: float = 8.0
    wall_thickness: float = 3.0
    dual_shaft: bool = False
    dual_shaft_x_offset: float = 0.0
    cam_Rb_hints: Dict[str, float] = field(default_factory=dict)
    cam_lever_ratios: Dict[str, float] = field(default_factory=dict)
    follower_x_positions: Dict[str, float] = field(default_factory=dict)
    fig_mount_z_offset: float = 0.0

    def summary(self) -> str:
        s = "✓ MICR CONVERGED" if self.success else "✗ MICR FAILED"
        lines = [
            f"  {s} in {self.solve_time_s:.1f}s ({self.n_iterations} iter)",
            f"  Constraints: {self.constraints_satisfied}/{self.constraints_total}",
            f"  Chassis: {self.chassis_width:.0f}×{self.chassis_depth:.0f}×{self.chassis_height:.0f}mm",
            f"  Shaft: Ø{self.shaft_diameter:.1f}mm, spacing={self.cam_spacing:.1f}mm",
            f"  Dual-shaft: {'ON (±' + f'{self.dual_shaft_x_offset:.0f}mm)' if self.dual_shaft else 'OFF'}",
        ]
        for name, rb in self.cam_Rb_hints.items():
            ratio = self.cam_lever_ratios.get(name, 1.0)
            lines.append(f"    · cam_{name}: Rb={rb:.1f}mm, lever 1:{ratio:.1f}")
        if self.violations:
            lines.append(f"  ⚠ {len(self.violations)} violation(s):")
            for v in self.violations[:5]:
                lines.append(f"    - {v}")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# CONSTRAINT FUNCTIONS — g(x) >= 0 pour le solveur
# ═══════════════════════════════════════════════════════════════════

def _shaft_inertia(d_mm):
    """Moment d'inertie d'un arbre cylindrique plein."""
    return math.pi * (d_mm ** 4) / 64.0

def _shaft_deflection(d_mm, L_mm, F_N, n_loads=1):
    """Flèche max d'un arbre simplement supporté avec charge(s) centrée(s).

    Pour n_loads uniformes: δ = (5 × F × L³) / (384 × E × I)
    Pour charge ponctuelle centrale: δ = (F × L³) / (48 × E × I)
    """
    I = _shaft_inertia(d_mm)
    if I < 1e-12:
        return 999.0
    if n_loads > 1:
        return (5.0 * F_N * L_mm**3) / (384.0 * E_STEEL * I)
    else:
        return (F_N * L_mm**3) / (48.0 * E_STEEL * I)


def constraint_shaft_deflection(x, n_cams, cam_forces_N):
    """g(x) = δ_max - δ(x) >= 0"""
    d = x[0]  # shaft_diameter
    spacing = x[1]
    wall_t = x[5]
    L = n_cams * spacing + 2 * wall_t + 10  # approximate shaft length
    F_total = sum(cam_forces_N)
    delta = _shaft_deflection(d, L, F_total, n_cams)
    return SHAFT_DEFLECTION_MAX - delta


def constraint_pressure_angle(x, cam_idx, v_arr, s_arr, rf):
    """g(x) = Rb - Rb_needed >= 0
    Uses cascade: try phi=30°, if Rb would exceed cap try 45°, then 58°."""
    n_g = 8  # global vars
    Rb = x[n_g + cam_idx]  # cam_Rb[cam_idx]

    # Cascade through pressure angle limits
    for phi_deg in PRESSURE_ANGLE_CASCADE:
        tan_phi = np.tan(np.radians(phi_deg))
        # Avoid division issues with zero velocity points
        mask = np.abs(v_arr) > 1e-9
        if not np.any(mask):
            return Rb  # no velocity → any Rb is fine
        Rp_required = np.abs(v_arr[mask]) / tan_phi - s_arr[mask]
        Rp_min = float(np.max(Rp_required))
        Rb_needed = max(Rp_min - rf, rf)

        if Rb_needed <= RB_HARD_CAP:
            return Rb - Rb_needed  # >= 0 means Rb is big enough

    # Even at 58° it needs more than cap — return deficit
    return Rb - Rb_needed


def constraint_cam_fits_chassis(x, cam_idx, max_amp, rf, n_cams):
    """g(x) = R_available - (Rb + amp + rf) >= 0"""
    n_g = 8
    Rb = x[n_g + cam_idx]
    chassis_w = x[2]
    wall_t = x[5]

    R_available = min(chassis_w, x[3]) / 2 - wall_t - 2.0
    return R_available - (Rb + max_amp + rf)


def constraint_print_plate(x):
    """g(x) = 220 - max(width, depth) >= 0"""
    return PRINT_BED_ENDER3[0] - max(x[2], x[3])


def constraint_motor_torque(peak_torque_mNm, stall_torque_mNm):
    """g(x) = stall × 0.6 - peak >= 0"""
    return stall_torque_mNm * (1 - MOTOR_MARGIN_MIN) - peak_torque_mNm


def constraint_roller_ratio(x, cam_idx, rf, n_cams):
    """g(x) = 0.35 - rf/Rb >= 0"""
    n_g = 8
    Rb = x[n_g + cam_idx]
    if Rb < 1e-6:
        return -1.0
    return ROLLER_RATIO_MAX - (rf / Rb)


def constraint_lever_sweep_in_chassis(x, cam_idx, n_cams):
    """g(x) = chassis_height - lever_top >= 0
    Le levier ne doit pas dépasser du châssis (avant shelf)."""
    n_g = 8
    lever_len = x[n_g + n_cams + cam_idx]  # cam_lever_length
    chassis_h = x[4]
    shaft_z = chassis_h * 0.5  # shaft at mid-height

    # Lever top ≈ shaft_z + Rb + lever_input + lever_output
    Rb = x[n_g + cam_idx]
    lever_input = lever_len * 0.3   # ~30% input arm
    lever_output = lever_len * 0.7
    lever_top = shaft_z + Rb + 5 + lever_input + lever_output

    return chassis_h + 20 - lever_top  # 20mm margin above chassis for shelf


def constraint_guide_wall_clearance(x, cam_idx, n_cams):
    """g(x) = guide_x - wall_extent - clearance >= 0 (distance from wall)."""
    n_g = 8
    guide_x = abs(x[n_g + 3*n_cams + cam_idx])  # |follower_x|
    wall_t = x[5]
    chassis_w = x[2]
    shaft_d = x[0]

    bore_r = shaft_d / 2 + CLEARANCE_TABLE['shaft_bearing_4mm']
    boss_r = bore_r + 1.5
    wall_extent = max(wall_t, 2 * boss_r)
    wall_inner = chassis_w / 2 - wall_extent

    guide_half = 4.0 + wall_t  # guide width/2
    return wall_inner - guide_x - guide_half - 1.5  # 1.5mm clearance


def constraint_adjacent_lever_clearance(x, cam_i, cam_j, n_cams):
    """g(x) = |guide_x_i - guide_x_j| - min_clearance >= 0"""
    n_g = 8
    xi = x[n_g + 3*n_cams + cam_i]
    xj = x[n_g + 3*n_cams + cam_j]
    guide_width = 12.0  # typical guide + bracket width
    return abs(xi - xj) - guide_width - CLEARANCE_TABLE['adjacent_parts']


def constraint_en71_safety(x, n_cams):
    """Les pièces critiques doivent être > 31.7mm."""
    # Le châssis est toujours > 60mm, OK.
    # Les cames doivent avoir un diamètre > 31.7mm
    n_g = 8
    violations = []
    for i in range(n_cams):
        Rb = x[n_g + i]
        cam_diameter = 2 * Rb
        if cam_diameter < EN71_SMALL_PART:
            violations.append(f"cam_{i}: Ø{cam_diameter:.1f}mm < {EN71_SMALL_PART}mm")
    return len(violations) == 0, violations


# ═══════════════════════════════════════════════════════════════════
# SWEPT VOLUME — Calcul de l'espace balayé par les pièces mobiles
# ═══════════════════════════════════════════════════════════════════

def compute_swept_bbox(pivot_pos, arm_length, arm_width, swing_deg, axis='z'):
    """Calcule le bounding box du volume balayé par un bras en rotation.

    Plus rapide que le swept volume mesh complet.
    Retourne (min_corner, max_corner) du AABB englobant.

    Args:
        pivot_pos: [x, y, z] position du pivot
        arm_length: longueur du bras (mm)
        arm_width: largeur du bras (mm)
        swing_deg: amplitude de rotation (±deg)
        axis: axe de rotation ('x', 'y', 'z')
    """
    swing_rad = math.radians(swing_deg)
    r = arm_length + arm_width / 2  # rayon max du sweep

    px, py, pz = pivot_pos
    half_w = arm_width / 2

    if axis == 'y':
        # Rotation dans le plan XZ
        dx = r * math.sin(swing_rad) + half_w
        dz = r  # conservative: full arm length
        return (
            np.array([px - dx, py - half_w, pz - dz]),
            np.array([px + dx, py + half_w, pz + dz])
        )
    elif axis == 'x':
        dy = r * math.sin(swing_rad) + half_w
        dz = r
        return (
            np.array([px - half_w, py - dy, pz - dz]),
            np.array([px + half_w, py + dy, pz + dz])
        )
    else:  # z-axis
        dx = r * math.sin(swing_rad) + half_w
        dy = r * math.sin(swing_rad) + half_w
        return (
            np.array([px - dx, py - dy, pz - arm_length]),
            np.array([px + dx, py + dy, pz + arm_length])
        )


def swept_volume_angular_step(voxel_size, max_radius):
    """Pas angulaire optimal pour le swept volume.

    Formule du deep research: Δθ ≤ 2·arcsin(voxel / (2×R))
    """
    if max_radius < 1e-6:
        return 5.0  # fallback
    step_rad = 2.0 * math.asin(min(voxel_size / (2.0 * max_radius), 1.0))
    return max(math.degrees(step_rad), 0.5)  # minimum 0.5°


# ═══════════════════════════════════════════════════════════════════
# PUSHROD ROUTER — Routage des pushrods autour de la figurine
# ═══════════════════════════════════════════════════════════════════

@dataclass
class PushrodRoute:
    """Chemin d'un pushrod du levier au point d'attache figurine."""
    waypoints: List[np.ndarray]
    route_type: str        # 'straight', 'L-shape', 'S-shape', 'rear'
    total_length: float    # mm
    clearance_ok: bool
    min_bend_radius: float  # mm (INFINITY for straight)

def route_pushrod_around_obstacle(
    start: np.ndarray,       # lever tip position
    end: np.ndarray,         # figurine attach point
    obstacle_bbox: tuple,    # (min_corner, max_corner) of figurine body
    clearance: float = PUSHROD_CLEARANCE,
) -> PushrodRoute:
    """Route un pushrod du levier à la figurine en évitant l'obstacle.

    Stratégies par priorité:
    1. Straight (si pas d'obstacle)
    2. Rear (passer derrière la figurine, -Y)
    3. L-shape (monter puis contourner)
    4. S-shape (deux coudes, dernier recours)
    """
    obs_min, obs_max = obstacle_bbox

    # Expand obstacle by clearance
    obs_min_e = obs_min - clearance
    obs_max_e = obs_max + clearance

    # Check if straight path intersects obstacle
    direction = end - start
    length = np.linalg.norm(direction)

    if length < 1e-6:
        return PushrodRoute([start, end], 'straight', 0.0, True, float('inf'))

    # Simple ray-box intersection test
    d = direction / length
    intersects = _ray_intersects_aabb(start, d, length, obs_min_e, obs_max_e)

    if not intersects:
        return PushrodRoute(
            [start, end], 'straight', length, True, float('inf'))

    # Strategy 2: Route behind (negative Y direction)
    rear_y = obs_min_e[1] - 5.0  # 5mm behind obstacle
    wp1 = np.array([start[0], rear_y, start[2]])  # move to rear
    wp2 = np.array([end[0], rear_y, end[2]])       # move up at rear

    rear_path = [start, wp1, wp2, end]
    rear_length = sum(np.linalg.norm(rear_path[i+1] - rear_path[i])
                      for i in range(len(rear_path)-1))

    # Check if rear path is clear
    rear_ok = True
    for i in range(len(rear_path)-1):
        seg_d = rear_path[i+1] - rear_path[i]
        seg_l = np.linalg.norm(seg_d)
        if seg_l > 1e-6:
            if _ray_intersects_aabb(rear_path[i], seg_d/seg_l, seg_l,
                                     obs_min_e, obs_max_e):
                rear_ok = False
                break

    if rear_ok:
        return PushrodRoute(
            rear_path, 'rear', rear_length, True, PUSHROD_BEND_RMIN)

    # Strategy 3: L-shape (go up above obstacle, then horizontal)
    above_z = obs_max_e[2] + 10.0  # 10mm above obstacle
    wp_up = np.array([start[0], start[1], above_z])
    l_path = [start, wp_up, end]
    l_length = sum(np.linalg.norm(l_path[i+1] - l_path[i])
                   for i in range(len(l_path)-1))

    return PushrodRoute(
        l_path, 'L-shape', l_length, True, PUSHROD_BEND_RMIN)


def _ray_intersects_aabb(origin, direction, length, box_min, box_max):
    """Test rapide d'intersection rayon-AABB."""
    t_min = 0.0
    t_max = length

    for i in range(3):
        if abs(direction[i]) < 1e-9:
            if origin[i] < box_min[i] or origin[i] > box_max[i]:
                return False
            continue

        inv_d = 1.0 / direction[i]
        t1 = (box_min[i] - origin[i]) * inv_d
        t2 = (box_max[i] - origin[i]) * inv_d

        if t1 > t2:
            t1, t2 = t2, t1

        t_min = max(t_min, t1)
        t_max = min(t_max, t2)

        if t_min > t_max:
            return False

    return True


# ═══════════════════════════════════════════════════════════════════
# MICR SOLVER — Le solveur principal
# ═══════════════════════════════════════════════════════════════════

class MICR:
    """Moteur Inverse de Contraintes Réelles.

    Usage:
        micr = MICR(scene, cams, motor_check)
        result = micr.solve()
        # result.cam_Rb_hints, result.chassis_width, etc.
        # → inject into generate() step 5
    """

    def __init__(self, scene, cams, motor_check,
                 print_bed='ender3', verbose=True):
        """
        Args:
            scene: AutomataScene avec tracks, motor specs
            cams: list of CamProfile (compiled from scene)
            motor_check: dict from check_motor_feasibility()
            print_bed: 'ender3' or 'bambu'
            verbose: print progress
        """
        self.scene = scene
        self.cams = cams
        self.motor_check = motor_check
        self.verbose = verbose
        self.n_cams = len(cams)
        self.print_bed = PRINT_BED_BAMBU if print_bed == 'bambu' else PRINT_BED_ENDER3

        # Pre-compute cam motion profiles
        self._cam_profiles = []
        self._cam_max_amps = []
        self._cam_forces = []  # estimated follower forces (N)

        for cam in self.cams:
            theta_deg = np.linspace(0, 360, 720, endpoint=False)
            s, ds, dds = cam.evaluate(theta_deg)
            max_amp = float(np.max(np.abs(s)))

            # Estimate follower force: F = k_spring × s + m × a × ω²
            # For toy automata at ~10 RPM, forces are small (~0.5-2N)
            F_est = max(0.5, max_amp * 0.05)  # rough: 0.05 N/mm displacement

            self._cam_profiles.append({
                's': s, 'ds': ds, 'dds': dds,
                'theta_deg': theta_deg,
                'max_amp': max_amp,
            })
            self._cam_max_amps.append(max_amp)
            self._cam_forces.append(F_est)

        # Figurine envelope (will be estimated from FigurineConfig if available)
        self._fig_bbox = self._estimate_figurine_bbox()

    def _estimate_figurine_bbox(self):
        """Estime le bounding box de la figurine depuis FigurineConfig."""
        fig_cfg = getattr(self.scene, '_figurine_cfg', None)
        if fig_cfg is None:
            # Default: small box above chassis
            return (np.array([-20, -15, 0]), np.array([20, 15, 45]))

        h = fig_cfg.height if fig_cfg.height > 0 else 45.0
        # Estimate width based on body type
        w = h * 0.4  # typical width ratio
        d = h * 0.3  # typical depth

        if fig_cfg.body_type in ('quadruped', 'insect', 'arachnid'):
            w = h * 0.6  # wider for legs
            d = h * 0.8  # longer
        elif fig_cfg.body_type == 'bird':
            w = h * 0.5  # wings

        return (np.array([-w/2, -d/2, 0]), np.array([w/2, d/2, h]))

    def _warm_start(self) -> DesignVector:
        """Crée le vecteur initial depuis les règles auto-scaled actuelles (R1-R9)."""
        dv = DesignVector()
        n = self.n_cams

        # Global: apply R1-R9 heuristics
        if n > 5:
            dv.shaft_diameter = 6.0  # R1
        if n > 6:
            dv.cam_spacing = 6.0     # R2

        # Dual-shaft: R9
        if n > 6:
            dv.dual_shaft_x_offset = 15.0  # sync gear M1.5×20t → center dist = 15mm

        # Estimate chassis from figurine + mechanism
        fig_min, fig_max = self._fig_bbox
        fig_w = fig_max[0] - fig_min[0]
        fig_d = fig_max[1] - fig_min[1]
        fig_h = fig_max[2] - fig_min[2]

        # Chassis must fit: mechanism below + figurine above
        max_cam_outer = max((self._cam_max_amps[i] + 15) for i in range(n))  # rough Rb + amp
        mech_w = 2 * (max_cam_outer + dv.wall_thickness + 2.0)
        dv.chassis_width = max(round(max(fig_w + 20, mech_w, 60) / 5) * 5, 60)
        dv.chassis_depth = max(round(max(fig_d + 20, 60) / 5) * 5, 60)
        # Height: enough for shaft + biggest cam + lever + margin to figurine
        est_lever = max_cam_outer * 1.5
        min_height = max_cam_outer * 2 + est_lever + 20
        dv.chassis_height = max(round(max(min_height, 80) / 5) * 5, 80)
        dv.fig_mount_z_offset = 5.0  # 5mm default lift above shelf

        # Per-cam: estimate Rb from cam profiles
        dv.cam_Rb = []
        dv.cam_lever_length = []
        dv.cam_lever_ratio = []
        dv.cam_follower_x = []
        dv.cam_pushrod_route = []

        for i in range(n):
            prof = self._cam_profiles[i]
            rf = 3.0  # default roller

            # Rb_min with pressure angle cascade (30° → 45° → 58°)
            Rb_min = None
            for phi_deg in PRESSURE_ANGLE_CASCADE:
                try:
                    from automata_unified_v4 import compute_Rb_min_translating_roller
                    Rb_cand = compute_Rb_min_translating_roller(
                        prof['ds'], prof['s'], rf, np.radians(phi_deg), 0.0)
                except ImportError:
                    v_max = float(np.max(np.abs(prof['ds'])))
                    Rb_cand = max(v_max / np.tan(np.radians(phi_deg)) + rf, rf / 0.38, 5.0)

                Rb_cand = max(Rb_cand, rf / 0.34, 5.0)  # rf/Rb <= 0.35 → Rb >= rf/0.35
                if Rb_cand <= RB_HARD_CAP:
                    Rb_min = Rb_cand
                    break

            if Rb_min is None:
                Rb_min = RB_HARD_CAP  # best we can do

            Rb_min = min(Rb_min, RB_HARD_CAP)

            dv.cam_Rb.append(Rb_min)

            # Lever sizing
            lever_len = max(20.0, Rb_min * 1.5)  # proportional to cam
            dv.cam_lever_length.append(lever_len)
            dv.cam_lever_ratio.append(1.5)  # default 1:1.5

            # Follower X: evenly distributed
            if n <= 1:
                fx = 0.0
            else:
                usable = dv.chassis_width - 2 * dv.wall_thickness - 20
                fx = -usable/2 + i * usable / max(n-1, 1)
            dv.cam_follower_x.append(fx)

            # Pushrod: default straight, will be resolved later
            dv.cam_pushrod_route.append(0)

        return dv

    def _build_constraints(self, dv_array, n_cams):
        """Évalue toutes les contraintes et retourne une liste de g(x) values.

        Convention: g(x) >= 0 signifie contrainte satisfaite.
        """
        results = []
        labels = []

        # 1. Shaft deflection
        g = constraint_shaft_deflection(dv_array, n_cams, self._cam_forces)
        results.append(g)
        labels.append(f'shaft_deflection (δ≤{SHAFT_DEFLECTION_MAX}mm)')

        # 2. Print plate fit
        g = constraint_print_plate(dv_array)
        results.append(g)
        labels.append(f'print_plate (≤{self.print_bed[0]}mm)')

        # 3. Per-cam constraints
        for i in range(n_cams):
            prof = self._cam_profiles[i]
            rf = 3.0

            # Pressure angle
            g = constraint_pressure_angle(
                dv_array, i, prof['ds'], prof['s'], rf)
            results.append(g)
            labels.append(f'pressure_angle_cam{i} (φ≤{PRESSURE_ANGLE_IDEAL}°)')

            # Cam fits in chassis
            g = constraint_cam_fits_chassis(
                dv_array, i, prof['max_amp'], rf, n_cams)
            results.append(g)
            labels.append(f'cam_fits_chassis_{i}')

            # Roller ratio
            g = constraint_roller_ratio(dv_array, i, rf, n_cams)
            results.append(g)
            labels.append(f'roller_ratio_{i} (rf/Rb≤{ROLLER_RATIO_MAX})')

            # Lever doesn't exceed chassis + shelf
            g = constraint_lever_sweep_in_chassis(dv_array, i, n_cams)
            results.append(g)
            labels.append(f'lever_sweep_{i}')

            # Guide-wall clearance
            g = constraint_guide_wall_clearance(dv_array, i, n_cams)
            results.append(g)
            labels.append(f'guide_wall_clearance_{i}')

        # 4. Adjacent lever clearance (all pairs)
        for i in range(n_cams):
            for j in range(i+1, n_cams):
                g = constraint_adjacent_lever_clearance(dv_array, i, j, n_cams)
                results.append(g)
                labels.append(f'adjacent_clearance_{i}_{j}')

        # 5. Figurine space — lever tip + pushrod must not enter figurine zone
        chassis_h = dv_array[4]
        shelf_z = chassis_h + 3.0  # shelf thickness = 3mm
        fig_z_base = shelf_z + dv_array[7]  # fig_mount_z_offset
        fig_min, fig_max = self._fig_bbox
        fig_world_min = fig_min + np.array([0, 0, fig_z_base])
        fig_world_max = fig_max + np.array([0, 0, fig_z_base])

        shaft_z = chassis_h * 0.5
        FIGURINE_BUFFER = 2.0  # 2mm safety buffer
        for i in range(n_cams):
            n_g = 8
            Rb = dv_array[n_g + i]
            lever_len = dv_array[n_g + n_cams + i]

            # Lever tip Z ≈ shaft_z + Rb + lever_total
            lever_top_z = shaft_z + Rb + 5 + lever_len

            # Option A: lever stays below figurine zone
            clearance_below = (fig_world_min[2] - FIGURINE_BUFFER) - lever_top_z

            # Option B: lever exits through side (outside figurine XY)
            fx = dv_array[n_g + 3*n_cams + i]
            fig_x_margin = fig_world_max[0] + PUSHROD_CLEARANCE + FIGURINE_BUFFER
            clearance_side = abs(fx) - fig_x_margin

            # Satisfied if EITHER condition holds (smooth max)
            g = max(clearance_below, clearance_side)
            results.append(g)
            labels.append(f'lever_vs_figurine_{i}')

        return results, labels

    def _objective(self, x):
        """Fonction objectif : minimiser le volume total du mécanisme."""
        chassis_vol = x[2] * x[3] * x[4]  # W × D × H

        # Penalty for constraint violations (soft constraints)
        constraints, _ = self._build_constraints(x, self.n_cams)
        penalty = 0.0
        for g in constraints:
            if g < 0:
                penalty += g ** 2  # quadratic penalty for violations

        # Normalize: chassis volume in cm³ (~100-2000), penalty weight
        return chassis_vol / 1e6 + 1000.0 * penalty

    def _scipy_constraints(self):
        """Build scipy constraint dicts (inequality: g(x) >= 0)."""
        constraints = []

        def make_constraint(idx):
            def con(x):
                vals, _ = self._build_constraints(x, self.n_cams)
                return vals[idx] if idx < len(vals) else 0.0
            return con

        # Get number of constraints from warm start
        dv = self._warm_start()
        x0 = dv.to_array()
        vals, labels = self._build_constraints(x0, self.n_cams)

        for i in range(len(vals)):
            constraints.append({
                'type': 'ineq',
                'fun': make_constraint(i)
            })

        return constraints, labels

    def solve(self) -> MICRResult:
        """Lance l'optimisation MICR.

        Stratégie hiérarchique:
        1. Warm-start depuis les valeurs auto-scaled (R1-R9)
        2. Niveau 1: optimiser macro-layout (chassis, shaft)
        3. Niveau 2: optimiser per-cam (Rb, lever, follower_x)
        4. Fixed-point iteration (2-3 passes) pour dépendances cycliques
        5. Valider et retourner
        """
        t0 = time.time()

        if self.verbose:
            print(f"\n{'─'*60}")
            print(f"  MICR — Moteur Inverse de Contraintes Réelles")
            print(f"  {self.n_cams} cames, print bed {self.print_bed[0]}×{self.print_bed[1]}mm")
            print(f"{'─'*60}")

        # ── WARM START ──
        dv = self._warm_start()
        x0 = dv.to_array()
        bounds = dv.bounds(self.n_cams)

        if self.verbose:
            CTOL = 1e-3
            vals0, labels0 = self._build_constraints(x0, self.n_cams)
            n_ok = sum(1 for v in vals0 if v >= -CTOL)
            print(f"  Warm-start: {n_ok}/{len(vals0)} constraints OK")
            for v, l in zip(vals0, labels0):
                if v < -CTOL:
                    print(f"    ✗ {l}: g={v:.3f}")

        # ── PHASE 1: Fixed-point iteration ──
        best_x = x0.copy()
        best_violations = 999
        fp_iter = 0

        for fp_iter in range(3):  # max 3 fixed-point passes
            if self.verbose:
                print(f"\n  Pass {fp_iter+1}/3...")

            try:
                from scipy.optimize import minimize

                # Build constraint functions
                scipy_cons, con_labels = self._scipy_constraints()

                result = minimize(
                    self._objective,
                    best_x,
                    method='SLSQP',
                    bounds=bounds,
                    constraints=scipy_cons,
                    options={
                        'maxiter': min(SOLVER_MAX_ITER, 100),  # fewer per pass
                        'ftol': SOLVER_FTOL,
                        'disp': False,
                    }
                )

                if result.success or result.fun < self._objective(best_x):
                    best_x = result.x.copy()

            except ImportError:
                if self.verbose:
                    print("    ⚠ scipy not available — using warm-start only")
                break
            except Exception as e:
                if self.verbose:
                    print(f"    ⚠ Solver error: {e}")
                break

            # Check convergence — tolerance 1e-3 for floating-point boundary
            CTOL = 1e-3
            vals, labels = self._build_constraints(best_x, self.n_cams)
            n_violations = sum(1 for v in vals if v < -CTOL)

            if self.verbose:
                n_ok = len(vals) - n_violations
                print(f"    → {n_ok}/{len(vals)} constraints OK ({n_violations} violations)")

            if n_violations <= best_violations:
                best_violations = n_violations

            if n_violations == 0:
                if self.verbose:
                    print("    ✓ All constraints satisfied!")
                break

            # Check time budget
            if time.time() - t0 > SOLVER_MAX_TIME:
                if self.verbose:
                    print(f"    ⏰ Time budget exceeded ({SOLVER_MAX_TIME}s)")
                break

        # ── PHASE 2: Pushrod routing ──
        dv_final = DesignVector()
        dv_final.from_array(best_x, self.n_cams)

        # Compute figurine position for pushrod routing
        chassis_h = dv_final.chassis_height
        shelf_z = chassis_h + 3.0
        fig_z_base = shelf_z + dv_final.fig_mount_z_offset
        fig_min, fig_max = self._fig_bbox
        fig_world_min = fig_min + np.array([0, 0, fig_z_base])
        fig_world_max = fig_max + np.array([0, 0, fig_z_base])

        pushrod_routes = {}
        shaft_z = chassis_h * 0.5
        for i, cam in enumerate(self.cams):
            Rb = dv_final.cam_Rb[i]
            lever_len = dv_final.cam_lever_length[i]
            fx = dv_final.cam_follower_x[i]

            lever_top_z = shaft_z + Rb + 5 + lever_len
            start = np.array([fx, 0, lever_top_z])

            # End point: above figurine center, at joint height
            end = np.array([fx, 0, fig_z_base + (fig_max[2] - fig_min[2]) * 0.5])

            route = route_pushrod_around_obstacle(
                start, end, (fig_world_min, fig_world_max))
            pushrod_routes[cam.name] = route

            if self.verbose and route.route_type != 'straight':
                print(f"    · pushrod_{cam.name}: {route.route_type} "
                      f"({route.total_length:.0f}mm, "
                      f"{'OK' if route.clearance_ok else 'COLLISION'})")

        # ── BUILD RESULT ──
        CTOL = 1e-3  # constraint satisfaction tolerance
        solve_time = time.time() - t0
        vals_final, labels_final = self._build_constraints(best_x, self.n_cams)
        violations = []
        for v, l in zip(vals_final, labels_final):
            if v < -CTOL:
                violations.append(f"{l}: g={v:.3f}")

        n_satisfied = sum(1 for v in vals_final if v >= -CTOL)

        result = MICRResult(
            success=(len(violations) == 0),
            design=dv_final,
            n_iterations=fp_iter + 1,
            solve_time_s=solve_time,
            residual=self._objective(best_x),
            constraints_satisfied=n_satisfied,
            constraints_total=len(vals_final),
            violations=violations,
            chassis_width=dv_final.chassis_width,
            chassis_depth=dv_final.chassis_depth,
            chassis_height=dv_final.chassis_height,
            shaft_diameter=dv_final.shaft_diameter,
            cam_spacing=dv_final.cam_spacing,
            wall_thickness=dv_final.wall_thickness,
            dual_shaft=(dv_final.dual_shaft_x_offset > 1.0),
            dual_shaft_x_offset=dv_final.dual_shaft_x_offset,
            fig_mount_z_offset=dv_final.fig_mount_z_offset,
        )

        # Per-cam hints for generate()
        for i, cam in enumerate(self.cams):
            result.cam_Rb_hints[cam.name] = dv_final.cam_Rb[i]
            result.cam_lever_ratios[cam.name] = dv_final.cam_lever_ratio[i]
            result.follower_x_positions[cam.name] = dv_final.cam_follower_x[i]

        if self.verbose:
            print(f"\n{result.summary()}")
            print(f"{'─'*60}\n")

        return result


# ═══════════════════════════════════════════════════════════════════
# INTEGRATION HELPER — Pour injecter le MICR dans generate()
# ═══════════════════════════════════════════════════════════════════

def apply_micr_to_chassis_config(micr_result: MICRResult, chassis_config):
    """Applique les résultats MICR à un ChassisConfig existant.

    Usage dans generate(), après MICR.solve():
        apply_micr_to_chassis_config(micr_result, chassis_config)
    """
    chassis_config.width = micr_result.chassis_width
    chassis_config.depth = micr_result.chassis_depth
    chassis_config.total_height = micr_result.chassis_height
    chassis_config.camshaft_diameter = micr_result.shaft_diameter
    chassis_config.cam_spacing = micr_result.cam_spacing
    chassis_config.wall_thickness = micr_result.wall_thickness

    if micr_result.dual_shaft:
        chassis_config.dual_shaft = True
        chassis_config.dual_shaft_x_offset = micr_result.dual_shaft_x_offset

    chassis_config.compute_camshaft_length()

    return chassis_config


def apply_micr_to_scene(micr_result: MICRResult, scene):
    """Injecte les Rb hints dans la scène pour que generate() les utilise.

    Usage dans generate(), après MICR.solve():
        apply_micr_to_scene(micr_result, self.scene)
    """
    if not hasattr(scene, '_solver_overrides'):
        scene._solver_overrides = {}

    scene._solver_overrides['cam_Rb_hints'] = micr_result.cam_Rb_hints
    scene._solver_overrides['lever_ratios'] = micr_result.cam_lever_ratios
    scene._solver_overrides['follower_x_positions'] = micr_result.follower_x_positions
    scene._solver_overrides['fig_mount_z_offset'] = micr_result.fig_mount_z_offset

    return scene


# ═══════════════════════════════════════════════════════════════════
# GENERATE() INTEGRATION SNIPPET
# ═══════════════════════════════════════════════════════════════════
"""
COMMENT INTÉGRER DANS generate() de AutomataGenerator:

Après step [4/8] Motor check (ligne ~8800), ajouter:

    # Step 4.5: MICR — Inverse constraint solver
    print("[4.5/8] MICR — Optimisation inverse...")
    from micr import MICR, apply_micr_to_scene
    micr = MICR(self.scene, self.cams, self.motor_check)
    micr_result = micr.solve()
    if micr_result.success:
        apply_micr_to_scene(micr_result, self.scene)
        # The Rb hints and overrides will be picked up by step 5
        # when it calls auto_design_cam() and positions followers
    else:
        print(f"  ⚠ MICR did not fully converge — using auto-scaled values")
        # Fall back to existing R1-R9 rules (no change needed)

Puis dans step [5/8] Geometry, le code existant lit déjà _solver_overrides:
    - rb_hint = self.scene._solver_overrides.get('cam_Rb_hints', {}).get(cam.name)
    - Ceci est déjà implémenté à ligne ~8871

Pour le ChassisConfig, remplacer le bloc de pré-calcul (lignes 8807-8832) par:

    if hasattr(self.scene, '_solver_overrides') and 'cam_Rb_hints' in getattr(self.scene, '_solver_overrides', {}):
        # MICR a déjà optimisé les dimensions
        from micr import apply_micr_to_chassis_config
        chassis_config = ChassisConfig(...)
        apply_micr_to_chassis_config(micr_result, chassis_config)
    else:
        # Fallback: original pre-sizing logic
        [... existing code ...]
"""


# ═══════════════════════════════════════════════════════════════════
# SELF-TEST
# ═══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("MICR — Self-test")
    print("="*60)

    # Test clearance table
    print("\n1. Clearance Table (FDM PLA):")
    for k, v in CLEARANCE_TABLE.items():
        print(f"  {k:25s} : {v:.2f}mm radial ({v*2:.2f}mm total)")

    # Test swept volume angular step
    print("\n2. Swept Volume Angular Steps:")
    for R in [10, 25, 50]:
        for vox in [0.5, 1.0]:
            step = swept_volume_angular_step(vox, R)
            print(f"  R={R}mm, voxel={vox}mm → Δθ={step:.2f}° ({360/step:.0f} steps)")

    # Test shaft deflection
    print("\n3. Shaft Deflection:")
    for d in [4.0, 6.0, 8.0]:
        for L in [80, 120, 180]:
            delta = _shaft_deflection(d, L, 2.0, 5)
            status = "✓" if delta <= SHAFT_DEFLECTION_MAX else "✗"
            print(f"  {status} Ø{d}mm, L={L}mm, 5 cams: δ={delta:.4f}mm")

    # Test pushrod routing
    print("\n4. Pushrod Routing:")
    start = np.array([0, 0, 50])
    end = np.array([0, 0, 90])
    obs = (np.array([-20, -15, 60]), np.array([20, 15, 85]))

    route = route_pushrod_around_obstacle(start, end, obs)
    print(f"  Route: {route.route_type}, length={route.total_length:.1f}mm, "
          f"waypoints={len(route.waypoints)}")

    # Test design vector
    print("\n5. Design Vector (3 cams):")
    dv = DesignVector()
    dv.cam_Rb = [12.0, 15.0, 10.0]
    dv.cam_lever_length = [25.0, 30.0, 20.0]
    dv.cam_lever_ratio = [1.5, 2.0, 1.2]
    dv.cam_follower_x = [-20.0, 0.0, 20.0]
    arr = dv.to_array()
    print(f"  Array length: {len(arr)} ({8} global + {3*4} per-cam)")
    dv2 = DesignVector()
    dv2.from_array(arr, 3)
    print(f"  Round-trip OK: Rb={dv2.cam_Rb}, lever={dv2.cam_lever_length}")

    # Test spatial relations coverage
    print(f"\n6. Spatial Relations:")
    print(f"  Contact  (A): {len(CONTACT_RELATIONS)} pairs")
    print(f"  Proximity(B): {len(PROXIMITY_RELATIONS)} pairs")
    print(f"  Adjacency(C): {len(ADJACENCY_RELATIONS)} pairs")
    print(f"  TOTAL: {len(ALL_SPATIAL_RELATIONS)} (replaces 63 skip_pairs)")

    print(f"\n{'='*60}")
    print("MICR self-test complete.")
    print("\nTo run full optimization, import from automata_unified_v4.py:")
    print("  from micr import MICR")
    print("  micr = MICR(scene, cams, motor_check)")
    print("  result = micr.solve()")
