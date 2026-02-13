# CODE_TREE — automata_unified_v4.py
# Generated: 2026-02-13 (post cam skip-pairs fix)
# Total: 20217 lines, 793 entries

L  108 | # ══════════════════════════════════════════════════════════════════════
L  110 | # ══════════════════════════════════════════════════════════════════════
L  138 | def ensure_polygon(geom):
L  146 | # ───────────────────────────────────────────────────────────
L  148 | # ───────────────────────────────────────────────────────────
L  153 | def _extrude_polygon_fallback(poly: ShapelyPolygon, height: float) -> trimesh.Trimesh:
L  183 |     def vid(x, y, z):
L  211 |     def add_walls(ring_coords, reverse=False):
L  245 | def extrude_polygon_safe(poly, height: float, **kwargs) -> trimesh.Trimesh:
L  272 | # ╔══════════════════════════════════════════════════════════════════╗
L  273 | # ║  BRIQUE 5 — TIMING ENGINE                                       ║
L  274 | # ║  Lois de mouvement, profils de cames, optimisation de phases     ║
L  277 | # ───────────────────────────────────────────────────────────
L  279 | # ───────────────────────────────────────────────────────────
L  281 | def cycloidal_motion(u: np.ndarray):
L  291 | def poly_345_motion(u: np.ndarray):
L  300 | def poly_4567_motion(u: np.ndarray):
L  309 | def simple_harmonic_motion(u: np.ndarray):
L  318 | def modified_trapezoidal_motion(u: np.ndarray):
L  379 | def _trap_half(ui, A, b, v_b, s_b, v_3b, s_3b):
L  416 | # ───────────────────────────────────────────────────────────
L  418 | # ───────────────────────────────────────────────────────────
L  421 | class CamSegment:
L  429 |     def beta_rad(self) -> float:
L  434 | class CamProfile:
L  440 |     def evaluate(self, theta_deg: np.ndarray):
L  523 | # ───────────────────────────────────────────────────────────
L  525 | # ───────────────────────────────────────────────────────────
L  527 | def estimate_cam_torque(
L  551 | # ───────────────────────────────────────────────────────────
L  553 | # ───────────────────────────────────────────────────────────
L  555 | def optimize_phases(
L  582 |     def peak_torque_with_phases(phases_deg):
L  622 | def generate_timing_diagram(cams: List[CamProfile], n_points: int = 1000) -> Dict:
L  644 | # ── SVG Timing Diagram Generator ──────────────────────────────────
L  650 | def generate_timing_svg(cams: List['CamProfile'],
L  694 |     def x_px(deg):
L  697 |     def y_px(s):
L  700 |     def y_torque_px(t):
L  855 | def generate_timing_html(cams: List['CamProfile'],
L  875 | def check_motor_feasibility(
L  893 | # ╔══════════════════════════════════════════════════════════════════╗
L  894 | # ║  BRIQUE 1 — SYNTHÈSE INVERSE DE CAMES                           ║
L  895 | # ║  Pitch curve → profil came → mesh STL                           ║
L  898 | def pitch_curve_translating_roller(theta, s, Rb, rf, eps=0.0):
L  906 | def cam_profile_translating_roller(theta, s, v, Rb, rf, eps=0.0):
L  921 | def pressure_angle_translating_roller(s, v, Rb, rf, eps=0.0):
L  928 | def curvature_radius_pitch_curve_roller(s, v, a, Rb, rf):
L  938 | def check_undercut_roller(rho_pitch, rf, safety_factor=2.0):
L  961 | def compute_Rb_min_translating_roller(v, s, rf, phi_max_rad=np.radians(30), eps=0.0):
L  969 | def cam_profile_flat_faced(theta, s, v, Rb):
L  976 | def curvature_radius_flat_faced(s, a, Rb):
L  981 | def check_undercut_flat_faced(s, a, Rb, rho_min_design=1.0):
L  997 | def compute_Rb_min_flat_faced(s, a, rho_min_design=1.0):
L 1002 | def cam_profile_oscillating_roller(theta, psi, pivot_world, arm_length, rf):
L 1016 | def pressure_angle_oscillating(theta, psi, pivot_world, arm_length):
L 1035 | def curvature_radius_parametric(theta, x, y):
L 1046 | # ── ⚠️ ARCHIVE: Barrel cam (cylindrical cam) ──────────────────────
L 1049 | def barrel_cam_groove(theta, s, Rc, groove_width=4.0, groove_depth=3.0):
L 1054 | def barrel_cam_unwrap(theta, s, Rc):
L 1059 | def cam_profile_to_mesh(x_cam, y_cam, thickness=5.0, bore_diameter=4.0,
L 1091 | class CamDesignResult:
L 1102 | def auto_design_cam(
L 1263 | # ╔══════════════════════════════════════════════════════════════════╗
L 1264 | # ║  ⚠️ ARCHIVE — BRIQUE 2 — SYNTHÈSE DE MÉCANISMES À BARRES       ║
L 1265 | # ║  Burmester 3/5 poses, Grashof, crank-slider                     ║
L 1266 | # ║  Kept as lib for potential four-bar synthesis. Not in pipeline.  ║
L 1270 | class LinkagePose:
L 1275 | class FourBarSolution:
L 1282 | def rot2d(theta):
L 1286 | def circumcenter(p1, p2, p3, eps=1e-9):
L 1294 | def world_point(pose, body_pt):
L 1298 | def synthesize_four_bar_3poses(poses, A_body, B_body):
L 1317 | def synthesize_four_bar_5poses(poses, n_starts=200, seed=42):
L 1322 |     def dyad_equations(x, poses):
L 1358 | def check_grashof(L1, L2, L3, L4):
L 1364 | def compute_min_transmission_angle(L1, L2, L3, L4, n_samples=360):
L 1377 | def filter_solutions(solutions, require_grashof=True, mu_min_threshold=40.0, max_ratio=10.0):
L 1385 | def crank_slider_position(theta, r, L, e=0.0):
L 1390 | def crank_slider_velocity(theta, r, L, e=0.0):
L 1396 | def crank_slider_acceleration(theta, r, L, e=0.0):
L 1403 | def quick_return_dimensions(time_ratio, stroke):
L 1416 | # ── REMOVED: theo_jansen, klann, chebyshev, get_walking_mechanism ──
L 1421 | def simulate_four_bar(sol, n_steps=360):
L 1439 | # ╔══════════════════════════════════════════════════════════════════╗
L 1440 | # ║  BRIQUE 3 — TRANSMISSION & MÉCANISMES INTERMITTENTS              ║
L 1441 | # ║  Worm gear, Geneva, ratchet, calcul de couple                    ║
L 1445 | class WormGearParams:
L 1449 |     def d1(self): return self.q * self.module
L 1451 |     def d2(self): return self.z_wheel * self.module
L 1453 |     def ratio(self): return self.z_wheel / self.starts
L 1455 |     def lead(self): return self.starts * np.pi * self.module
L 1457 |     def lead_angle_rad(self): return np.arctan2(self.lead, np.pi * self.d1)
L 1459 |     def lead_angle_deg(self): return np.degrees(self.lead_angle_rad)
L 1461 |     def center_distance(self): return (self.d1 + self.d2) / 2
L 1463 |     def is_potentially_self_locking(self): return bool(self.lead_angle_deg < 5.0)  # FIX-11: native bool
L 1466 | def worm_efficiency(lead_angle_rad, friction_coeff=0.3, pressure_angle_rad=np.radians(20)):
L 1473 | # ── REMOVED: generate_worm_mesh ──
L 1479 | class GearStage:
L 1483 | def compute_train_torque(stages, motor_torque_mNm=150.0):
L 1494 | def n20_output_rpm(stages, motor_rpm=300.0):
L 1502 | # ── ⚠️ ARCHIVE: Geneva mechanism (intermittent motion) ────────────
L 1506 | class GenevaParams:
L 1509 |     def center_distance(self): return self.driver_radius / np.sin(np.pi / self.n_slots)
L 1511 |     def driven_radius(self): return self.driver_radius / np.tan(np.pi / self.n_slots)
L 1513 |     def step_angle_deg(self): return 360.0 / self.n_slots
L 1515 |     def dwell_ratio(self): return 1.0 - 1.0 / self.n_slots
L 1517 |     def slot_length(self): return self.driven_radius + self.driver_radius - self.center_distance
L 1519 |     def motion_ratio(self): return 1.0 / self.n_slots
L 1522 | def generate_geneva_driven_mesh(params, thickness=5.0, slot_width=None):
L 1537 | def generate_geneva_driver_mesh(params, thickness=5.0):
L 1547 | # ── REMOVED: RatchetParams, generate_ratchet_mesh ──
L 1551 | def preset_automata_drive_train():
L 1556 | # ── REMOVED: preset_worm_drive_train ──
L 1560 | # ╔══════════════════════════════════════════════════════════════════╗
L 1561 | # ║  BRIQUE 4 — CHÂSSIS & ARCHITECTURE D'ASSEMBLAGE                  ║
L 1565 | class ChassisConfig:
L 1593 |     def __post_init__(self):
L 1606 |     def enable_dual_shaft(self):
L 1613 |     def compute_camshaft_length(self):
L 1627 |     def shaft_center_z(self) -> float:
L 1641 | def create_base_plate(config):
L 1653 | def create_lever_arm(pivot_pos, input_length, output_length,
L 1688 | def create_lever_bracket(pivot_pos, arm_width, pin_diameter, wall_thickness=3.0):
L 1725 | def create_pivot_pin(pivot_pos, arm_width, pin_diameter, wall_thickness=3.0):
L 1744 | def create_collar(pivot_pos, pin_diameter, offset_y, wall_thickness=3.0):
L 1770 | def create_bearing_wall(config, side="left", bearing_positions=None):
L 1806 | def create_camshaft_bracket(config, z_position=40.0):
L 1829 | def create_motor_mount(config):
L 1851 | class FollowerGuide:
L 1857 | def create_linear_follower_guide(guide, config):
L 1871 | def create_shaft_coupler(shaft_diameter=6.0, length=15.0, bore_clearance=0.25):
L 1891 | def create_mid_bearing_wall(config, shaft_positions, y_position=0.0):
L 1927 | def create_crank_handle(config, z_position=0.0):
L 1951 | def create_printed_collar(config, z_position=0.0, y_position=0.0):
L 1967 | def generate_chassis(config, cam_count=1, follower_guides=None):
L 1980 | def generate_involute_gear_mesh(module: float = 1.5, teeth: int = 20,
L 2021 |     def involute(a):
L 2030 |     def involute_points(r_start, r_end, n_pts):
L 2135 | def _make_shaft_and_drive(config, cam_count, cz, parts):
L 2192 | def _add_follower_guides(parts, follower_guides, config):
L 2199 | def generate_chassis_box(config, cam_count=1, follower_guides=None):
L 2226 | def generate_chassis_frame(config, cam_count=1, follower_guides=None):
L 2267 | def generate_chassis_central(config, cam_count=1, follower_guides=None):
L 2306 | def generate_chassis_flat(config, cam_count=1, follower_guides=None):
L 2340 | def generate_chassis_bom(config):
L 2364 | # ╔══════════════════════════════════════════════════════════════════╗
L 2365 | # ║  BRIQUE 4b — JOINTS PHYSIQUES & FEATURES D'ASSEMBLAGE           ║
L 2366 | # ║  Opérations CSG pour rendre les STL assemblables physiquement    ║
L 2370 | # ╔══════════════════════════════════════════════════════════════════╗
L 2371 | # ║  TOLÉRANCES FDM RÉELLES — Base de données par tier/matériau     ║
L 2372 | # ║  Valeurs typiques — à affiner par calibration physique          ║
L 2376 | class FDMToleranceProfile:
L 2405 |     def bore_free_dia(self) -> float:
L 2410 |     def bore_press_dia(self) -> float:
L 2414 |     def shrinkage_for(self, material: str) -> float:
L 2425 |     def compensated_hole(self, nominal_dia: float) -> float:
L 2485 | def get_tolerance_profile(tier: str = "medium") -> FDMToleranceProfile:
L 2490 | def apply_tolerances_to_profile(fdm_profile: 'FDMProfile',
L 2504 | def generate_tolerance_report(tier: str = "medium",
L 2552 | class JointConfig:
L 2584 |     def for_tier(cls, tier: str = "medium") -> 'JointConfig':
L 2595 | # ── Shaft Bore Hole (free rotation) ──────────────────────────
L 2597 | def make_bore_hole_2d(center_x: float, center_y: float,
L 2624 | def make_chamfered_bore_3d(mesh: trimesh.Trimesh,
L 2693 | # ── D-Shaft (keyed bore for cam-to-shaft) ──────────────────
L 2695 | def make_d_shaft_bore_2d(center_x: float, center_y: float,
L 2724 | # ── E-Clip Groove (axial retention on shaft) ──────────────────
L 2726 | def make_eclip_groove_3d(shaft_mesh: trimesh.Trimesh,
L 2771 | # ── M3 Screw Hole (clearance or insert pocket) ──────────────
L 2773 | def make_m3_hole_2d(center_x: float, center_y: float,
L 2794 | def make_m3_insert_pocket_2d(center_x: float, center_y: float,
L 2811 | # ── Snap-Fit Hook (figurine → follower platform) ──────────────
L 2813 | def make_snap_hook_3d(platform_width: float,
L 2851 | def make_snap_pocket_3d(cfg: 'JointConfig' = None) -> trimesh.Trimesh:
L 2873 | # ── M3 Head/Nut Pockets (3D) ──────────────────
L 2875 | def make_m3_head_pocket_3d(center: np.ndarray,
L 2894 | def make_m3_nut_pocket_3d(center: np.ndarray,
L 2914 | # ── Assembly Feature Integrator ──────────────────────────────
L 2916 | def apply_joint_features(parts: Dict[str, trimesh.Trimesh],
L 3099 | # ── Enhanced cam bore: D-shaft instead of round hole ─────────
L 3101 | def cam_profile_to_mesh_keyed(x_cam, y_cam, thickness=5.0,
L 3129 | # ── Enhanced bearing wall with chamfered bore ─────────────────
L 3131 | def create_bearing_wall_with_joints(config: 'ChassisConfig',
L 3184 | # ╔══════════════════════════════════════════════════════════════════╗
L 3185 | # ║  BRIQUE 6 — DÉTECTION DE COLLISIONS                             ║
L 3186 | # ║  🟡 FIX-5: Pénétration réelle via contains()                    ║
L 3190 | class MechanismPart:
L 3199 | class CollisionResult:
L 3204 | class CollisionReport:
L 3209 |     def summary(self):
L 3218 | def rotation_matrix_axis_angle(axis, angle_rad):
L 3224 | def transform_matrix(R, t):
L 3230 | def compute_part_transform(part):
L 3245 | def forward_kinematics_all(parts, joint_values):
L 3258 | def compute_aabb(mesh, transform):
L 3265 | def aabb_overlap(min_a, max_a, min_b, max_b, margin=0.0):
L 3269 | def z_slabs_overlap(part_a, part_b, clearance=0.5):
L 3275 | def broadphase_pairs(parts, transforms, margin=2.0):
L 3290 | def mesh_distance(mesh_a, transform_a, mesh_b, transform_b):
L 3346 | def verify_collisions(parts, cam_profiles=None, theta_steps=360, clearance_mm=0.5, verbose=True):
L 3375 | def compute_swept_volume(part, cam_profile=None, theta_steps=72, voxel_size=1.0):
L 3397 | # ╔══════════════════════════════════════════════════════════════════╗
L 3398 | # ║  BRIQUE 6b — STABILITÉ, POIDS & CENTRE DE GRAVITÉ              ║
L 3399 | # ║  Calcul CoG 3D, critère de non-basculement, lest automatique    ║
L 3425 | class StabilityResult:
L 3439 |     def is_stable(self) -> bool:
L 3442 |     def summary(self) -> str:
L 3455 | def _point_in_polygon_margin(px, py, polygon_pts):
L 3465 | def compute_stability(parts: Dict[str, trimesh.Trimesh],
L 3600 | # ╔══════════════════════════════════════════════════════════════════╗
L 3601 | # ║  BRIQUE 7 — CONTRAINTES FDM & FABRICABILITÉ                     ║
L 3602 | # ║  🟡 FIX-6: Wall thickness par ray-casting                       ║
L 3606 | class FDMProfile:
L 3625 | def fdm_profile_for_tier(tier: str = "medium", material: str = "PLA") -> FDMProfile:
L 3633 | def tolerance_stack_up(nominal_clearance, n_interfaces, profile=None,
L 3645 | class ValidationResult:
L 3653 | def validate_mesh_fdm(mesh, part_name, profile=None, part_type="structural",
L 3742 | def run_real_constraint_checks(gen, chassis_config):
L 4814 | def validate_assembly_post_generate(parts, chassis_config, verbose=False):
L 4979 | def optimize_print_orientation(mesh, n_samples=50, overhang_angle=45.0,
L 5001 | def generate_print_settings(parts, part_types=None, profile=None):
L 5009 | # ╔══════════════════════════════════════════════════════════════════╗
L 5010 | # ║  PRINT OPTIMIZER — Auto Print Settings per Part per Tier         ║
L 5011 | # ║  3 tiers: Budget (~200€) / Medium (~500€) / Premium (~1100€)    ║
L 5012 | # ║  Analyse chaque pièce → réglages optimaux automatiques           ║
L 5055 | def classify_part_role(name: str) -> str:
L 5069 | class PartPrintSettings:
L 5271 | class PrintOptimizer:
L 5372 |     def __init__(self, tier="medium", filament="PLA"):
L 5385 |     def _scale_speed(self, base_speed: int) -> int:
L 5390 |     def _clamp_layer(self, layer: float) -> float:
L 5394 |     def analyze_one(self, name: str, mesh=None) -> PartPrintSettings:
L 5488 |     def analyze_parts(self, parts: dict) -> List['PartPrintSettings']:
L 5496 |     def generate_print_guide(self, parts: dict, part_types: dict = None) -> str:
L 5596 |     def export_slicer_json(self, settings: List['PartPrintSettings'], output_dir: str):
L 5666 |     def print_summary(self, settings: List['PartPrintSettings']):
L 5709 | # ── Backward compatibility alias ──
L 5713 | # ╔══════════════════════════════════════════════════════════════════╗
L 5714 | # ║  BRIQUE 8 — MOTION VOCABULARY & SCENE DESCRIPTION                ║
L 5715 | # ║  Pont sémantique: intention → primitives → cam segments          ║
L 5718 | class MotionLaw(Enum):
L 5722 | class MotionStyle(Enum):
L 5732 | class MotionPrimitive:
L 5736 |     def to_cam_segment(self):
L 5765 | class MotionTrack:
L 5773 |     def total_beta(self):
L 5776 |     def normalize_to_360(self):
L 5783 |     def to_cam_segments(self):
L 5812 | class Joint:
L 5824 | class Link:
L 5830 | class AutomataScene:
L 5838 |     def compile_cam_program(self):
L 5844 |     def validate(self):
L 5870 |     def to_json(self):
L 5892 |     def from_json(cls, json_str):
L 5921 | # ───────────────────────────────────────────────────────────
L 5923 | # ───────────────────────────────────────────────────────────
L 5925 | def create_nodding_bird(style=MotionStyle.MECHANICAL):
L 5938 | def create_flapping_bird(style=MotionStyle.FLUID):
L 5962 | def create_walking_figure(style=MotionStyle.MECHANICAL):
L 5983 | def create_bobbing_duck(style=MotionStyle.FLUID):
L 5997 | def create_rocking_horse(style=MotionStyle.FLUID):
L 6014 | def create_pecking_chicken(style=MotionStyle.MECHANICAL):
L 6034 | def create_waving_cat(style=MotionStyle.FLUID):
L 6050 | def create_drummer(style=MotionStyle.MECHANICAL):
L 6073 | def create_blacksmith(style=MotionStyle.MECHANICAL):
L 6089 | def create_swimming_fish(style=MotionStyle.FLUID):
L 6103 | def create_turtle_simple(style=MotionStyle.FLUID):
L 6131 | def create_turtle_walking(style=MotionStyle.FLUID):
L 6190 | # ╔══════════════════════════════════════════════════════════════════╗
L 6191 | # ║  BRIQUE C — Mouvements V2-V10 (macros + templates)              ║
L 6194 | # ── Macro expansion functions ──
L 6198 | def expand_geneva_primitives(n_positions: int = 4, step_lift: float = 20.0,
L 6215 | def expand_strike_primitives(amplitude: float = 20.0, rise_ratio: float = 0.6,
L 6230 | def expand_hold_primitives(amplitude: float = 15.0, hold_deg: float = 200.0,
L 6248 | def create_sequential_tracks(track_configs: List[dict],
L 6271 | # ── Scene templates for new movements ──
L 6273 | def create_slide_scene(style=MotionStyle.MECHANICAL):
L 6290 | def create_rotate_scene(style=MotionStyle.FLUID):
L 6308 | def create_geneva_scene(style=MotionStyle.MECHANICAL):
L 6321 | def create_sequence_scene(style=MotionStyle.MECHANICAL):
L 6344 | def create_strike_v2_scene(style=MotionStyle.MECHANICAL):
L 6357 | def create_hold_scene(style=MotionStyle.FLUID):
L 6370 | def create_multi_scene(style=MotionStyle.FLUID):
L 6389 | # ── Scene preset registry ──
L 6418 | # ╔══════════════════════════════════════════════════════════════════╗
L 6419 | # ║  PIPELINE PRINCIPAL — GENERATOR                                  ║
L 6420 | # ║  🔴 FIX-1: phase_offset scope corrigé dans compile_scene_to_cams║
L 6423 | def compile_scene_to_cams(scene: AutomataScene) -> list:
L 6465 | def create_cam_disk_placeholder(cam, base_radius=15.0, thickness=5.0,
L 6490 | # ╔══════════════════════════════════════════════════════════════════╗
L 6491 | # ║  BRIQUE 9 — FIGURINES PARAMÉTRIQUES                              ║
L 6492 | # ║  Personnages simples montés sur le mécanisme                      ║
L 6495 | def _make_ellipsoid(rx, ry, rz, sections=24):
L 6503 | def _make_wing(span, chord, thickness=1.5):
L 6513 | def _make_leg(length, diameter=4.0):
L 6522 | def _make_arm(length, diameter=3.0):
L 6526 | def _make_eyes(head_mesh, head_center, head_radius, eye_radius=0.8,
L 6572 | def _make_cone_beak(radius, height, direction=None):
L 6588 | def _make_ear(height=2.5, base_radius=1.2):
L 6593 | # ═══════════════════════════════════════════════════════════════
L 6595 | # ═══════════════════════════════════════════════════════════════
L 6597 | def generate_figurine_nodding_bird(chassis_config):
L 6657 | # ═══════════════════════════════════════════════════════════════
L 6659 | # ═══════════════════════════════════════════════════════════════
L 6661 | def generate_figurine_flapping_bird(chassis_config):
L 6721 | # ═══════════════════════════════════════════════════════════════
L 6723 | # ═══════════════════════════════════════════════════════════════
L 6725 | def generate_figurine_walking_figure(chassis_config):
L 6785 | # ═══════════════════════════════════════════════════════════════
L 6787 | # ═══════════════════════════════════════════════════════════════
L 6789 | def generate_figurine_duck(chassis_config):
L 6836 | # ═══════════════════════════════════════════════════════════════
L 6838 | # ═══════════════════════════════════════════════════════════════
L 6840 | def generate_figurine_rocking_horse(chassis_config):
L 6903 | # ═══════════════════════════════════════════════════════════════
L 6905 | # ═══════════════════════════════════════════════════════════════
L 6907 | def generate_figurine_waving_cat(chassis_config):
L 6967 | # ═══════════════════════════════════════════════════════════════
L 6969 | # ═══════════════════════════════════════════════════════════════
L 6971 | def generate_figurine_drummer(chassis_config):
L 7032 | # ═══════════════════════════════════════════════════════════════
L 7034 | # ═══════════════════════════════════════════════════════════════
L 7036 | def generate_figurine_blacksmith(chassis_config):
L 7093 | # ═══════════════════════════════════════════════════════════════
L 7095 | # ═══════════════════════════════════════════════════════════════
L 7097 | def generate_figurine_fish(chassis_config):
L 7150 | # ═══════════════════════════════════════════════════════════════
L 7152 | # ═══════════════════════════════════════════════════════════════
L 7154 | def generate_figurine_chicken(chassis_config):
L 7205 | # ═══════════════════════════════════════════════════════════════
L 7207 | # ═══════════════════════════════════════════════════════════════
L 7231 | # ╔══════════════════════════════════════════════════════════════════╗
L 7232 | # ║  BRIQUE A — FIGURINE BUILDER PARAMÉTRIQUE (V1)                   ║
L 7233 | # ║  Objectif: remplacer les figurines hardcodées par une config      ║
L 7234 | # ║  Assemblage CSG simple (ellipsoïdes, cylindres, ailes, accessoires)
L 7238 | class AccessoryDef:
L 7256 | class FigurineConfig:
L 7276 | # ═══════════════════════════════════════════════════════════════════
L 7278 | # ═══════════════════════════════════════════════════════════════════
L 7280 | class JointFactory:
L 7309 |     def create_pin_joint(
L 7390 |     def pin_hole_diameter(pin_diameter: float, clearance: float = None) -> float:
L 7401 |     def pin_fits_in_hole(pin_diameter: float, hole_diameter: float) -> bool:
L 7406 |     def create_pushrod(
L 7485 |     def calculate_pushrod_attach(
L 7526 |     def create_pushrod_socket(
L 7567 |     def add_joint_to_split(
L 7647 |     def split_at_joint(
L 7700 |     def calculate_amplitude(pushrod_travel: float, lever_arm: float) -> float:
L 7733 |     def create_ball_joint(
L 7788 |     def ball_socket_diameter(ball_d: float, clearance: float = 0.10) -> float:
L 7794 |     def create_living_hinge(
L 7837 | class FigurineBuilder:
L 7845 |     def __init__(self, seed: int = 0):
L 7849 |     def _rot(rx, ry, rz):
L 7856 |     def _make_accessory(self, acc: AccessoryDef) -> trimesh.Trimesh:
L 7877 |     def build(self, cfg: FigurineConfig, chassis_config: 'ChassisConfig') -> Dict[str, trimesh.Trimesh]:
L 8054 | # ╔══════════════════════════════════════════════════════════════════╗
L 8055 | # ║  BRIQUE B — SCENE BUILDER (V1)                                   ║
L 8056 | # ║  Objectif: générer automatiquement une scène depuis FigurineConfig ║
L 8059 | class SceneBuilder:
L 8107 |     def _scale_scene(scene: AutomataScene, scale: float):
L 8127 |     def _auto_style_for(cfg: FigurineConfig) -> MotionStyle:
L 8136 |     def from_figurine(cls, cfg: FigurineConfig) -> AutomataScene:
L 8180 | # ╔══════════════════════════════════════════════════════════════════╗
L 8181 | # ║  BRIQUE E — CATALOGUE (V0.5)                                     ║
L 8182 | # ║  Mapping type→template (partiel). Les châssis avancés arrivent V2  ║
L 8211 | def parse_text_to_figurine_config(user_text: str) -> FigurineConfig:
L 8411 | # ╔══════════════════════════════════════════════════════════════════╗
L 8412 | # ║  BRIQUE F — FLASK OFFLINE (V0.5)                                 ║
L 8413 | # ║  UI minimal: texte libre → config → scene → génération → ZIP       ║
L 8424 | def create_flask_app() -> 'Flask':
L 8468 |     def index():
L 8472 |     def generate_zip():
L 8502 | def run_flask_offline(host: str = '127.0.0.1', port: int = 0):
L 8516 | def generate_assembly_guide_pdf(gen, output_path: str = "assembly_guide.pdf"):
L 8687 | class AutomataGenerator:
L 8690 |     def __init__(self, scene: AutomataScene, seed: int = 42):
L 8702 |     def generate(self) -> dict:
L 9686 |     def generate_assembly_guide(self) -> str:
L 9893 |     def export(self, output_dir):
L10041 |     def generate_pdf_guide(self, output_path: str = None) -> str:
L10053 | # ╔══════════════════════════════════════════════════════════════════╗
L10054 | # ║  CLI                                                              ║
L10057 | def main():
L10112 | # ════════════════════════════════════════════════════════════════════════
L10114 | # ════════════════════════════════════════════════════════════════════════
L10116 | class Severity(Enum):
L10122 | # ════════════════════════════════════════════════════════════════════════
L10124 | # ════════════════════════════════════════════════════════════════════════
L10126 | class Violation:
L10135 |     def __init__(self, code="", *args, **kwargs):
L10168 |     def is_error(self):
L10171 |     def is_warning(self):
L10174 |     def __str__(self):
L10179 |     def __repr__(self):
L10183 | # ════════════════════════════════════════════════════════════════════════
L10185 | # ════════════════════════════════════════════════════════════════════════
L10188 | class ConstraintReport:
L10195 |     def errors(self) -> List[Violation]:
L10199 |     def warnings(self) -> List[Violation]:
L10203 |     def infos(self) -> List[Violation]:
L10207 |     def has_errors(self) -> bool:
L10211 |     def is_ok(self) -> bool:
L10214 |     def add(self, violation: Violation):
L10217 |     def summary(self) -> str:
L10231 | # ════════════════════════════════════════════════════════════════════════
L10233 | # ════════════════════════════════════════════════════════════════════════
L10390 | # ════════════════════════════════════════════════════════════════════════
L10392 | # ════════════════════════════════════════════════════════════════════════
L10394 | class MotorSpec:
L10406 |     def torque_stall_mNm(self) -> float:
L10410 |     def torque_safe_Nm(self) -> float:
L10415 |     def torque_safe_mNm(self) -> float:
L10419 |     def current_safe_A(self) -> float:
L10422 |     def torque_at_rpm(self, rpm: float) -> float:
L10430 |     def current_at_rpm(self, rpm: float) -> float:
L10440 | # ════════════════════════════════════════════════════════════════════
L10442 | # ════════════════════════════════════════════════════════════════════
L10445 | class PrinterProfile:
L10457 |     def bambu_x1c():
L10470 |     def ender3():
L10474 | # ════════════════════════════════════════════════════════════════════
L10477 | # ════════════════════════════════════════════════════════════════════════
L10479 | # ════════════════════════════════════════════════════════════════════════
L10481 | def shaft_moment_of_inertia(diameter_mm: float) -> float:
L10485 | def shaft_deflection_point_load(F_N: float, L_mm: float, a_mm: float,
L10500 | def hertz_contact_pressure_cylinder(F_N: float, L_mm: float,
L10526 | def follower_jump_critical_rpm(spring_rate_N_per_mm: float,
L10542 | def estimate_print_time_hours(volume_cm3: float) -> float:
L10548 | def estimate_mass_grams(volume_cm3: float) -> float:
L10553 | def cumulative_backlash_mm(n_gear_stages: int, n_pivots: int,
L10569 | # ════════════════════════════════════════════════════════════════════
L10571 | # ════════════════════════════════════════════════════════════════════
L10574 | # ════════════════════════════════════════════════════════════════════════
L10576 | # ════════════════════════════════════════════════════════════════════════
L10581 | # ════════════════════════════════════════════════════════════════════════
L10583 | # ════════════════════════════════════════════════════════════════════════
L10588 | # ════════════════════════════════════════════════════════════════════════
L10590 | # ════════════════════════════════════════════════════════════════════════
L10636 | # ═══════════════════════════════════════
L10638 | # ═══════════════════════════════════════
L10642 | # ════════════════════════════════════════════════════════════════════════
L10644 | # ════════════════════════════════════════════════════════════════════════
L10660 | # ═══════════════════════════════════════
L10662 | # ═══════════════════════════════════════
L10666 | # ════════════════════════════════════════════════════════════════════════
L10668 | # ════════════════════════════════════════════════════════════════════════
L10730 | # ═══════════════════════════════════════════════════════════════
L10732 | # ═══════════════════════════════════════════════════════════════
L10736 | # ════════════════════════════════════════════════════════════════════════
L10738 | # ════════════════════════════════════════════════════════════════════════
L10740 | def _pv_product(contact_pressure_mpa: float, sliding_speed_m_s: float) -> float:
L10745 | def _cam_surface_speed_m_s(Rb_mm: float, amplitude_mm: float,
L10754 | def _natural_frequency_hz(mass_kg: float, stiffness_N_per_m: float) -> float:
L10761 | def _stress_from_cam_force(force_N: float, cross_section_mm2: float) -> float:
L10771 | # ════════════════════════════════════════════════════════════════════════
L10773 | # ════════════════════════════════════════════════════════════════════════
L10775 | def check_trou1_cam_collision(cams: List[Dict]) -> List[Violation]:
L10825 | # ════════════════════════════════════════════════════════════════════
L10827 | # ════════════════════════════════════════════════════════════════════
L10829 | def check_trou2_shaft_length(cams: List[Dict],
L10875 | # ════════════════════════════════════════════════════════════════════
L10877 | # ════════════════════════════════════════════════════════════════════
L10879 | def check_trou3_pressure_angle(cams: List[Dict]) -> List[Violation]:
L10943 | # ════════════════════════════════════════════════════════════════════
L10945 | # ════════════════════════════════════════════════════════════════════
L10947 | def check_trou4_lever_sweep(levers: List[Dict],
L11006 | # ════════════════════════════════════════════════════════════════════
L11008 | # ════════════════════════════════════════════════════════════════════
L11010 | def check_trou5_torque_with_lever(total_tau_peak_Nm: float,
L11047 | # ════════════════════════════════════════════════════════════════════
L11049 | # ════════════════════════════════════════════════════════════════════
L11051 | def check_trou6_gravity(orientation: str,
L11069 | # ════════════════════════════════════════════════════════════════════
L11071 | # ════════════════════════════════════════════════════════════════════
L11073 | def check_trou7_spring(orientation: str,
L11119 | # ════════════════════════════════════════════════════════════════════
L11121 | # ════════════════════════════════════════════════════════════════════
L11123 | def check_trou8_cumulative_lift(tracks: List[Dict]) -> List[Violation]:
L11167 | # ════════════════════════════════════════════════════════════════════
L11169 | # ════════════════════════════════════════════════════════════════════
L11171 | def check_trou9_chassis(chassis_dims_mm: Dict,
L11215 | # ════════════════════════════════════════════════════════════════════
L11217 | # ════════════════════════════════════════════════════════════════════
L11219 | def check_trou10_figure_clearance(figure_bottom_z_mm: float,
L11255 | # ════════════════════════════════════════════════════════════════════
L11257 | # ════════════════════════════════════════════════════════════════════
L11259 | def check_trou11_shaft_deflection(shaft_diameter_mm: float,
L11304 | # ════════════════════════════════════════════════════════════════════
L11306 | # ════════════════════════════════════════════════════════════════════
L11308 | def check_trou12_transmission(motor: MotorSpec,
L11356 | # ════════════════════════════════════════════════════════════════════
L11358 | # ════════════════════════════════════════════════════════════════════
L11362 | # ════════════════════════════════════════════════════════════════════════
L11364 | # ════════════════════════════════════════════════════════════════════════
L11366 | def check_trou13_shaft_retention(
L11460 | # ═══════════════════════════════════════
L11462 | # ═══════════════════════════════════════
L11464 | def check_trou14_component_retention(
L11506 | # ═══════════════════════════════════════
L11508 | # ═══════════════════════════════════════
L11510 | def check_trou15_assembly_order(
L11548 | # ═══════════════════════════════════════
L11550 | # ═══════════════════════════════════════
L11552 | def check_trou16_cam_phasing(
L11616 | # ═══════════════════════════════════════
L11618 | # ═══════════════════════════════════════
L11620 | def check_trou17_startup_torque(
L11699 | # ═══════════════════════════════════════
L11701 | # ═══════════════════════════════════════
L11703 | def check_trou18_stall_protection(
L11755 | # ═══════════════════════════════════════
L11757 | # ═══════════════════════════════════════
L11759 | def check_trou19_manual_crank(
L11808 | # ═══════════════════════════════════════
L11810 | # ═══════════════════════════════════════
L11812 | def check_trou20_power_supply(
L11874 | # ═══════════════════════════════════════
L11876 | # ═══════════════════════════════════════
L11878 | def check_trou21_print_orientation(
L11937 | # ═══════════════════════════════════════
L11939 | # ═══════════════════════════════════════
L11941 | def check_trou22_print_supports(
L11992 | # ═══════════════════════════════════════
L11994 | # ═══════════════════════════════════════
L11996 | def check_trou23_print_estimate(
L12044 | # ═══════════════════════════════════════
L12046 | # ═══════════════════════════════════════
L12048 | def check_trou24_calibration(
L12078 | # ═══════════════════════════════════════
L12080 | # ═══════════════════════════════════════
L12082 | def check_trou25_modularity(
L12146 | # ═══════════════════════════════════════
L12148 | # ═══════════════════════════════════════
L12150 | def check_trou26_safety(
L12211 | # ═══════════════════════════════════════
L12213 | # ═══════════════════════════════════════
L12215 | def check_trou27_bom_quality(
L12289 | # ═══════════════════════════════════════
L12291 | # ═══════════════════════════════════════
L12295 | # ════════════════════════════════════════════════════════════════════════
L12297 | # ════════════════════════════════════════════════════════════════════════
L12299 | # ── Constantes B4 ──
L12377 | def check_exotic_cas101_rotation_pure(tracks: List[Dict]) -> List[Violation]:
L12419 | # ── CAS 102 — Grand déplacement linéaire ────────────────────────────
L12421 | def check_exotic_cas102_large_stroke(tracks: List[Dict]) -> List[Violation]:
L12466 | # ── CAS 103 — Mouvement très rapide / beta très petit ───────────────
L12468 | def check_exotic_cas103_fast_motion(segments: List[Dict]) -> List[Violation]:
L12515 | # ── CAS 104 — 8+ mouvements synchronisés ────────────────────────────
L12517 | def check_exotic_cas104_many_cams(n_cams: int,
L12567 | # ── CAS 105 — Mouvement non-planaire (2D simultané) ─────────────────
L12569 | def check_exotic_cas105_compound_motion(tracks: List[Dict]) -> List[Violation]:
L12627 | # ── CAS 106 — Intermittence (Geneva, ratchet) ───────────────────────
L12629 | def check_exotic_cas106_intermittent(tracks: List[Dict]) -> List[Violation]:
L12684 | # ── CAS 107 — Mouvement asymétrique ─────────────────────────────────
L12686 | def check_exotic_cas107_asymmetric(segments: List[Dict]) -> List[Violation]:
L12735 | # ── CAS 108 — Charge variable externe ───────────────────────────────
L12737 | def check_exotic_cas108_external_load(tracks: List[Dict],
L12796 | # ── CAS 109 — Automate inversé ───────────────────────────────────────
L12798 | def check_exotic_cas109_inverted(orientation: str,
L12850 | # ── CAS 110 — Échelle extrême ────────────────────────────────────────
L12852 | def check_exotic_cas110_scale(total_size_mm: float,
L12906 | # ════════════════════════════════════════════════════════════════════
L12908 | # ════════════════════════════════════════════════════════════════════
L12910 | # ── E1 — Friction et usure PLA ───────────────────────────────────────
L12912 | def check_physics_e1_friction_wear(cams: List[Dict],
L12984 | # ── E2 — Fatigue PLA ─────────────────────────────────────────────────
L12986 | def check_physics_e2_fatigue(cams: List[Dict],
L13041 | # ── E3 — Vibrations et bruit ─────────────────────────────────────────
L13043 | def check_physics_e3_vibrations(rpm: float,
L13092 | # ── E4 — Tolérances directionnelles ──────────────────────────────────
L13094 | def check_physics_e4_tolerances(parts: List[Dict],
L13154 | # ── E5 — Assemblage pratique ─────────────────────────────────────────
L13156 | def check_physics_e5_assembly(fasteners: List[Dict],
L13251 | # ── E6 — Contact Hertz (wrapper B1) ──────────────────────────────────
L13253 | def check_physics_e6_hertz(cams: List[Dict]) -> List[Violation]:
L13310 | # ── E7 — Backlash cumulé (wrapper B1) ────────────────────────────────
L13312 | def check_physics_e7_backlash(n_gear_stages: int,
L13353 | # ── E8 — Follower jump (wrapper B1) ──────────────────────────────────
L13355 | def check_physics_e8_follower_jump(spring_rate_N_per_mm: float,
L13407 | # ════════════════════════════════════════════════════════════════════
L13409 | # ════════════════════════════════════════════════════════════════════
L13411 | def run_block4_all(scene: Dict) -> List[Violation]:
L13469 | # ════════════════════════════════════════════════════════════════════
L13471 | # ════════════════════════════════════════════════════════════════════
L13475 | # ════════════════════════════════════════════════════════════════════════
L13477 | # ════════════════════════════════════════════════════════════════════════
L13479 | def check_trou28_motion_law_suitability(
L13544 | # ═══════════════════════════════════════
L13546 | # ═══════════════════════════════════════
L13548 | def compute_Rb_min_analytical(
L13589 | def check_trou29_Rb_min(
L13633 | # ═══════════════════════════════════════
L13635 | # ═══════════════════════════════════════
L13637 | def check_trou30_return_spring(
L13717 | # ═══════════════════════════════════════
L13719 | # ═══════════════════════════════════════
L13721 | def check_trou31_cam_pv_product(
L13795 | # ═══════════════════════════════════════
L13797 | # ═══════════════════════════════════════
L13799 | def check_trou32_bell_crank(
L13842 | # ═══════════════════════════════════════
L13844 | # ═══════════════════════════════════════
L13846 | def check_trou33_roller_sizing(cams: List[Dict]) -> List[Violation]:
L13886 | # ═══════════════════════════════════════
L13888 | # ═══════════════════════════════════════
L13890 | def check_trou34_cam_thickness(cams: List[Dict]) -> List[Violation]:
L13932 | # ═══════════════════════════════════════
L13934 | # ═══════════════════════════════════════
L13936 | def check_trou35_dwell_angles(
L13982 | # ════════════════════════════════════════════════════════════════
L13984 | # ════════════════════════════════════════════════════════════════
L13986 | def run_block5_all(scene: Dict) -> List[Violation]:
L14009 | # ════════════════════════════════════════════════════════════════
L14011 | # ════════════════════════════════════════════════════════════════
L14015 | # ════════════════════════════════════════════════════════════════════════
L14017 | # ════════════════════════════════════════════════════════════════════════
L14019 | def check_trou36_lever_pivot(levers: List[Dict]) -> List[Violation]:
L14076 | # ═══════════════════════════════════════
L14078 | # ═══════════════════════════════════════
L14080 | def check_trou37_lever_bending(levers: List[Dict]) -> List[Violation]:
L14128 | # ═══════════════════════════════════════
L14130 | # ═══════════════════════════════════════
L14132 | def check_trou38_grashof(linkages: List[Dict]) -> List[Violation]:
L14189 | # ═══════════════════════════════════════
L14191 | # ═══════════════════════════════════════
L14193 | def check_trou39_transmission_angle(linkages: List[Dict]) -> List[Violation]:
L14240 | # ═══════════════════════════════════════
L14242 | # ═══════════════════════════════════════
L14244 | def check_trou40_crank_slider(sliders: List[Dict]) -> List[Violation]:
L14301 | # ═══════════════════════════════════════
L14303 | # ═══════════════════════════════════════
L14305 | def check_trou41_worm_gear(worm_gears: List[Dict]) -> List[Violation]:
L14381 | # ═══════════════════════════════════════
L14383 | # ═══════════════════════════════════════
L14385 | def check_trou42_gear_efficiency(
L14449 | # ═══════════════════════════════════════
L14451 | # ═══════════════════════════════════════
L14453 | def check_trou43_geneva_timing(genevas: List[Dict]) -> List[Violation]:
L14515 | # ════════════════════════════════════════════════════════════════
L14517 | # ════════════════════════════════════════════════════════════════
L14519 | def run_block6_all(scene: Dict) -> List[Violation]:
L14536 | # ════════════════════════════════════════════════════════════════
L14538 | # ════════════════════════════════════════════════════════════════
L14542 | # ════════════════════════════════════════════════════════════════════════
L14544 | # ════════════════════════════════════════════════════════════════════════
L14546 | def check_trou44_thermal(
L14608 | # ═══════════════════════════════════════
L14610 | # ═══════════════════════════════════════
L14612 | def check_trou45_creep(
L14682 | # ═══════════════════════════════════════
L14684 | # ═══════════════════════════════════════
L14686 | def check_trou46_resonance(
L14740 | # ═══════════════════════════════════════
L14742 | # ═══════════════════════════════════════
L14744 | def check_trou47_fatigue(
L14803 | # ═══════════════════════════════════════
L14805 | # ═══════════════════════════════════════
L14807 | def check_trou48_tolerance_stackup(
L14867 | # ═══════════════════════════════════════
L14869 | # ═══════════════════════════════════════
L14871 | def check_trou49_shrinkage(
L14921 | # ═══════════════════════════════════════
L14923 | # ═══════════════════════════════════════
L14925 | def check_trou50_bearing(
L14997 | # ═══════════════════════════════════════
L14999 | # ═══════════════════════════════════════
L15001 | def check_trou51_degradation(
L15070 | # ════════════════════════════════════════════════════════════════
L15072 | # ════════════════════════════════════════════════════════════════
L15074 | def run_block7_all(scene: Dict) -> List[Violation]:
L15097 | # ════════════════════════════════════════════════════════════════
L15099 | # ════════════════════════════════════════════════════════════════
L15103 | # ════════════════════════════════════════════════════════════════════════
L15105 | # ════════════════════════════════════════════════════════════════════════
L15107 | def check_trou52_en71_safety(
L15182 | # ═══════════════════════════════════════
L15184 | # ═══════════════════════════════════════
L15186 | def check_trou53_electrical(
L15243 | # ═══════════════════════════════════════
L15245 | # ═══════════════════════════════════════
L15247 | def check_trou54_noise(
L15312 | # ═══════════════════════════════════════
L15314 | # ═══════════════════════════════════════
L15316 | def check_trou55_assembly(
L15395 | # ═══════════════════════════════════════
L15397 | # ═══════════════════════════════════════
L15399 | def check_trou56_bom(
L15463 | # ═══════════════════════════════════════
L15465 | # ═══════════════════════════════════════
L15467 | def check_trou57_print_plate(
L15533 | # ═══════════════════════════════════════
L15535 | # ═══════════════════════════════════════
L15537 | def check_trou58_integration(
L15606 | # ═══════════════════════════════════════
L15608 | # ═══════════════════════════════════════
L15610 | def check_trou59_documentation(
L15675 | # ════════════════════════════════════════════════════════════════
L15677 | # ════════════════════════════════════════════════════════════════
L15679 | def run_block8_all(scene: Dict, block_results: Dict[str, List] = None) -> List[Violation]:
L15713 | # ════════════════════════════════════════════════════════════════
L15715 | # ════════════════════════════════════════════════════════════════
L15719 | # ════════════════════════════════════════════════════════════════════════
L15721 | # ════════════════════════════════════════════════════════════════════════
L15723 | def check_trou_60_offset_pressure_angle(
L15807 | # ═══════════════════════════════════════════════════════════════
L15809 | # ═══════════════════════════════════════════════════════════════
L15811 | def check_trou_61_gear_module(
L15864 | # ═══════════════════════════════════════════════════════════════
L15866 | # ═══════════════════════════════════════════════════════════════
L15868 | def check_trou_62_min_teeth(
L15916 | # ═══════════════════════════════════════════════════════════════
L15918 | # ═══════════════════════════════════════════════════════════════
L15920 | def check_trou_63_gear_fatigue(
L15986 | # ═══════════════════════════════════════════════════════════════
L15988 | # ═══════════════════════════════════════════════════════════════
L15990 | def check_trou_64_wear_rate(
L16047 | # ═══════════════════════════════════════════════════════════════
L16049 | # ═══════════════════════════════════════════════════════════════
L16051 | def check_trou_65_lubrication(
L16120 | # ═══════════════════════════════════════════════════════════════
L16122 | # ═══════════════════════════════════════════════════════════════
L16124 | def check_trou_66_hole_compensation(
L16180 | # ═══════════════════════════════════════════════════════════════
L16182 | # ═══════════════════════════════════════════════════════════════
L16184 | def check_trou_67_horizontal_hole(
L16237 | # ═══════════════════════════════════════════════════════════════
L16239 | # ═══════════════════════════════════════════════════════════════
L16241 | def check_trou_68_press_fit(
L16307 | # ═══════════════════════════════════════════════════════════════
L16309 | # ═══════════════════════════════════════════════════════════════
L16311 | def check_trou_69_motor_protection(
L16382 | # ═══════════════════════════════════════════════════════════════
L16384 | # ═══════════════════════════════════════════════════════════════
L16386 | def check_trou_70_battery_autonomy(
L16450 | # ═══════════════════════════════════════════════════════════════
L16452 | # ═══════════════════════════════════════════════════════════════
L16454 | def check_trou_71_shaft_deflection(
L16532 | # ═══════════════════════════════════════════════════════════════
L16534 | # ═══════════════════════════════════════════════════════════════
L16536 | def check_min_wall_thickness(parts: Dict[str, 'trimesh.Trimesh'],
L16579 | def check_trou_72_infill(
L16633 | # ═══════════════════════════════════════════════════════════════
L16635 | # ═══════════════════════════════════════════════════════════════
L16639 | # ════════════════════════════════════════════════════════════════════════
L16641 | # ════════════════════════════════════════════════════════════════════════
L16644 | def test_block2():
L16788 | def test_block3():
L16974 | def test_block4():
L17281 | def test_block5():
L17396 | def test_block6():
L17495 | def test_block7():
L17596 | def test_block8():
L17694 | def test_block9():
L17698 |     def test(name, violations, expected_severity):
L17879 | def test_block1():
L17969 | # ════════════════════════════════════════════════════════════════════════
L17971 | # ════════════════════════════════════════════════════════════════════════
L17973 | def run_all_tests():
L18038 | def extract_design_data(scene: 'AutomataScene', gen_result: Dict) -> Dict:
L18362 | def run_all_constraints(design_data, verbose: bool = True) -> 'ConstraintReport':
L18560 | def _safe_check(report: 'ConstraintReport', block: str, check_fn, verbose: bool = False):
L18579 | def validate_preset(preset_name: str = 'nodding_bird', verbose: bool = True) -> 'ConstraintReport':
L18624 | # ╔══════════════════════════════════════════════════════════════════╗
L18625 | # ║  §C.2  SOLVER LOOP — Correction automatique itérative           ║
L18626 | # ║  Détecte → corrige → régénère → re-vérifie (max N itérations)  ║
L18664 | def _apply_fix(design_data: Dict, violation: 'Violation') -> Tuple[Dict, str]:
L18675 |     def _find_cam_by_name(cams, msg):
L18799 | def auto_fix(
L18957 | def _propagate_to_scene(scene: 'AutomataScene', data: Dict):
L19001 | def auto_fix_preset(
L19169 | def diagnose(report: 'ConstraintReport' = None, violations: List = None) -> str:
L19266 | def diagnose_error(error: Exception) -> str:
L19337 | def test_master(verbose: bool = True) -> bool:
L19518 | # ╔══════════════════════════════════════════════════════════════════╗
L19519 | # ║  CLI + MAIN                                                      ║
L19524 | # ═══════════════════════════════════════════════════════════════════
L19528 | # ═══════════════════════════════════════════════════════════════════
L19531 | class InverseSolution:
L19542 |     def summary(self) -> str:
L19559 | class InverseSolver:
L19595 |     def __init__(self, roller_radius=5.0, pressure_angle_limit=30.0,
L19606 |     def solve(self, target_xy, max_cams=3, timeout_s=30.0):
L19677 |     def _preprocess(self, target_xy):
L19712 |     def _decompose(self, target, max_cams):
L19751 |     def _optimize_single_cam(self, target_1d, axis_label, cam_idx, timeout_s):
L19950 |     def _simulate_solution(self, cam_solutions, axis_labels, n_points):
L19971 |     def from_canvas(self, canvas_points, canvas_width_px, canvas_height_px,
L19985 | # ── Tests Brique G ──
L19987 | def test_inverse_solver():
