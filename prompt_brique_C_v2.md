# PROMPT DE CONTINUATION — BRIQUE C : Mouvements V2-V10

## SITUATION

Tu avais commencé la Brique C (mouvements V2-V10) sur `automata_unified_v4.py` mais tu as planté 2 fois avant de livrer quoi que ce soit de testable. On reprend de zéro sur le **fichier propre** joint à cette conversation.

## FICHIER JOINT

`automata_unified_v4.py` — **15,257 lignes**, tout fonctionne :
- 94 checks constraint engine ✅
- 10 presets motor mode ✅ (nodding_bird, flapping_bird, walking_figure, etc.)
- 8 configs crank mode ✅
- 12 cas parser texte ✅
- FigurineBuilder paramétrique (5 body types) ✅
- SceneBuilder.from_figurine() ✅
- Flask UI offline ✅
- Mode crank (100% imprimé, manivelle) + mode motor (N20) ✅

**NE TOUCHE PAS** au mode crank, aux joints, au constraint engine, à l'export, au FigurineBuilder, à la stabilité. Ce sont des briques terminées et testées.

## CE QUE TU DOIS FAIRE

Ajouter les mouvements V2-V10 **comme des macros** qui se décomposent en LIFT/PAUSE/WAVE existants. Le CamProfile ne change PAS.

## ARCHITECTURE ACTUELLE (ce que tu dois comprendre)

### MotionPrimitive (ligne ~3731)
```python
@dataclass
class MotionPrimitive:
    kind: str          # "LIFT", "PAUSE", "WAVE", "ROTATE", "NOD", "SNAP"
    amplitude: float = 30.0
    beta: float = 90.0
    law: MotionLaw = MotionLaw.CYCLOIDAL
    direction: int = 1

    def to_cam_segment(self):
        # Convertit en dict {type, beta_deg, height, law}
        # PAUSE → dwell, LIFT → rise/return, WAVE → rise_return
```

### MotionTrack (ligne ~3755)
```python
@dataclass
class MotionTrack:
    name: str
    joint_type: str = "revolute"
    axis: str = "x"
    primitives: List[MotionPrimitive] = field(default_factory=list)
    phase_offset_deg: float = 0.0
    frequency_multiplier: int = 1

    def to_cam_segments(self):
        self.normalize_to_360()
        segments = [p.to_cam_segment() for p in self.primitives]
        # ...
```

### SceneBuilder.TEMPLATE_CREATORS (ligne ~5129)
```python
TEMPLATE_CREATORS = {
    'nod': create_nodding_bird,
    'flap': create_flapping_bird,
    'walk': create_walking_figure,
    'wave': create_waving_cat,
    'peck': create_pecking_chicken,
    'rock': create_rocking_horse,
    'swim': create_swimming_fish,
    'drum': create_drummer,
    'strike': create_blacksmith,
}
```

### SceneBuilder.from_figurine(cfg) (ligne ~5186)
```python
mv = (cfg.movement or 'wave').lower().strip()
if mv not in cls.TEMPLATE_CREATORS:
    mv = 'wave'  # fallback
scene = cls.TEMPLATE_CREATORS[mv](style)
```

### parse_text_to_figurine_config(text) (ligne ~5253)
Matching FR/EN → FigurineConfig avec movement, body_type, etc.

## MOUVEMENTS À AJOUTER

### V2 — SLIDE (glissière horizontale)
- **Primitive** : `MotionPrimitive("SLIDE", amplitude, beta, law, direction)` → se comporte comme LIFT côté came
- **MotionTrack** : ajouter champ `follower_direction: str = "vertical"` (default). Si "horizontal", le guide est tourné 90°
- **Template** : `create_slide_scene(style)` → 1 track SLIDE, amplitude=15mm
- **Parsing** : "tiroir", "drawer", "glissière", "slide" → movement='slide'
- **SceneBuilder** : ajouter 'slide' dans TEMPLATE_CREATORS

### V4 — ROTATE (levier oscillant)
- **Primitive** : `MotionPrimitive("ROTATE", amplitude_deg, beta, law, direction)` → converti en lift_mm = `radians(amplitude_deg) * lever_length_mm` dans to_cam_segment()
- **MotionTrack** : ajouter champ `lever_length_mm: float = 0.0`. Si > 0, les ROTATE sont convertis
- **Template** : `create_rotate_scene(style)` → 1 track ROTATE ±30°, lever=20mm
- **Parsing** : "levier", "bascule", "balancier", "rocker", "lever" → movement='rotate'

### V5 — GENEVA (rotation par steps)
- **C'est une macro** : N steps de (LIFT up + LIFT down + PAUSE dwell)
- **Primitive** : `MotionPrimitive("GENEVA", amplitude=20, beta=360)` avec meta stocké quelque part
- **Solution la plus simple** : une fonction `expand_geneva(n_positions=4, step_lift=20, law=CYCLOIDAL)` qui retourne une liste de MotionPrimitive (LIFT + LIFT + PAUSE × N)
- **Template** : `create_geneva_scene(style)` → 1 track avec les primitives expandues
- **Parsing** : "plateau tournant", "carrousel", "carousel", "tournant", "turntable", "geneva" → movement='geneva'

### V7 — SEQUENCE (mouvements phasés)
- **Pas une nouvelle primitive** mais une **fonction helper** : `create_sequential_tracks(movements, dwell_between_deg=30)` qui calcule les phase_offset_deg pour que les mouvements ne se chevauchent pas
- **Template** : `create_sequence_scene(style)` → 2-3 tracks séquentiels
- **Parsing** : "séquentiel", "sequence", "un puis l'autre" → movement='sequence'

### V8 — STRIKE (frappe asymétrique)
- **C'est une macro** : LIFT(amp, beta_rise=200) + LIFT(-amp, beta_return=80) + PAUSE(80)
- **Solution** : fonction `expand_strike(amplitude=20, rise_ratio=0.65, law=CYCLOIDAL)` → liste de MotionPrimitive
- **NOTE** : le preset `create_blacksmith` existe déjà et fait déjà du strike ! Mais c'est avec des LIFT manuels. Ajouter la macro pour simplifier la création
- **Template** : `create_strike_scene(style)` = peut réutiliser create_blacksmith ou une variante
- **Parsing** : déjà géré ("forge", "marteau", "strike", "frappe") → mais mapper aussi vers la macro

### V9 — HOLD (maintien longue durée)
- **C'est une macro** : LIFT(amp, 60°) + PAUSE(beta_hold=200°) + LIFT(-amp, 60°) + PAUSE(40°)
- **Solution** : fonction `expand_hold(amplitude=15, hold_deg=200, law=CYCLOIDAL)` → liste de MotionPrimitive
- **Template** : `create_hold_scene(style)` → 1 track avec hold
- **Parsing** : "verrou", "lock", "maintien", "hold", "reste", "stay" → movement='hold'

### V10 — MULTI-AXE (2 cames, 1 objet)
- **Pas une nouvelle primitive** mais **2 MotionTrack** liés au même objet
- **Template** : `create_multi_scene(style)` → 2 tracks (1 vertical + 1 horizontal) avec phases décalées
- **Parsing** : "multi", "trajectoire", "deux axes", "multi-axe" → movement='multi'

## PLAN D'IMPLÉMENTATION PRÉCIS

### Étape 1 : Modifier MotionPrimitive.to_cam_segment()
Ajouter les cas `"SLIDE"` (= identique à LIFT) et mettre à jour `"ROTATE"` pour convertir degrés → mm si lever_length est fourni.

### Étape 2 : Modifier MotionTrack
Ajouter les 2 champs avec defaults :
```python
follower_direction: str = "vertical"
lever_length_mm: float = 0.0
```

### Étape 3 : Fonctions d'expansion macro
```python
def expand_geneva_primitives(n_positions=4, step_lift=20, law=MotionLaw.CYCLOIDAL): ...
def expand_strike_primitives(amplitude=20, rise_ratio=0.65, law=MotionLaw.CYCLOIDAL): ...
def expand_hold_primitives(amplitude=15, hold_deg=200, law=MotionLaw.CYCLOIDAL): ...
def create_sequential_tracks(track_configs, dwell_between_deg=30, law=MotionLaw.CYCLOIDAL): ...
```

### Étape 4 : Templates de scènes
```python
def create_slide_scene(style): ...
def create_rotate_scene(style): ...
def create_geneva_scene(style): ...
def create_sequence_scene(style): ...
def create_strike_v2_scene(style): ...   # ou réutiliser blacksmith
def create_hold_scene(style): ...
def create_multi_scene(style): ...
```

### Étape 5 : Mettre à jour SceneBuilder
```python
TEMPLATE_CREATORS = {
    # existants (NE PAS TOUCHER)
    'nod': create_nodding_bird,
    'flap': create_flapping_bird,
    'walk': create_walking_figure,
    'wave': create_waving_cat,
    'peck': create_pecking_chicken,
    'rock': create_rocking_horse,
    'swim': create_swimming_fish,
    'drum': create_drummer,
    'strike': create_blacksmith,
    # NOUVEAUX
    'slide': create_slide_scene,
    'rotate': create_rotate_scene,
    'geneva': create_geneva_scene,
    'sequence': create_sequence_scene,
    'hold': create_hold_scene,
    'multi': create_multi_scene,
}
```
+ ajouter les TEMPLATE_HEIGHT_MM pour les nouveaux.

### Étape 6 : Mettre à jour parse_text_to_figurine_config()
Ajouter dans `movement_overrides` :
```python
'slide': ['tiroir', 'drawer', 'glissière', 'slide', 'horizontal'],
'rotate': ['levier', 'lever', 'balancier', 'rocker', 'pivote'],
'geneva': ['plateau tournant', 'carrousel', 'carousel', 'tournant', 'turntable', 'geneva'],
'hold': ['verrou', 'lock', 'maintien', 'hold', 'reste', 'stay'],
'sequence': ['séquentiel', 'sequence', 'un puis'],
'multi': ['multi', 'trajectoire', 'deux axes'],
```

### Étape 7 : Mettre à jour SceneBuilder._auto_style_for()
Ajouter les nouveaux mouvements dans les catégories MECHANICAL/FLUID.

### Étape 8 (optionnel) : Guide horizontal pour SLIDE
Dans `create_linear_follower_guide()` (~ligne 1575), si `direction == "horizontal"`, tourner le guide de 90°.
Dans `AutomataGenerator.generate()` (~ligne 5543-5553 zone guides), passer la direction du track.

## CONTRAINTES ABSOLUES

1. **Les 10 presets originaux doivent toujours fonctionner identiquement** (regression zéro)
2. **test_master() doit passer** (94 checks, ALL PASS)
3. **Le mode crank doit toujours fonctionner** (8 configs testées)
4. **Le CamProfile ne change PAS** — les macros se décomposent en LIFT/PAUSE/WAVE
5. **Le fichier reste monolithique** (tout dans un seul .py)
6. **Les nouveaux champs MotionTrack ont des valeurs par défaut** → pas de casse des appels existants

## TESTS À EXÉCUTER

Après ton patch, exécute ces tests dans l'ordre :

```python
# 1. Master test (94 checks internes)
test_master()  # → ALL PASS

# 2. Les 10 presets originaux (motor mode)
for name in SCENE_PRESETS:
    scene = SCENE_PRESETS[name](MotionStyle.FLUID)
    gen = AutomataGenerator(scene, seed=42)
    gen.generate()
    assert gen.stability.is_stable

# 3. Parser texte → nouveaux mouvements
assert parse_text_to_figurine_config("tiroir secret").movement == 'slide'
assert parse_text_to_figurine_config("plateau tournant").movement == 'geneva'
assert parse_text_to_figurine_config("boîte à verrou").movement == 'hold'

# 4. Pipeline complet pour chaque nouveau mouvement
for mv in ['slide', 'rotate', 'geneva', 'sequence', 'hold', 'multi']:
    cfg = FigurineConfig(name=f'test_{mv}', body_type='biped', movement=mv)
    scene = SceneBuilder.from_figurine(cfg)
    gen = AutomataGenerator(scene, seed=42)
    gen.generate()
    assert gen.stability.is_stable
    print(f"✅ {mv}: {len(gen.all_parts)} parts, stable")

# 5. Mode crank toujours OK
cfg = FigurineConfig(name='test_crank', body_type='bird', movement='nod', drive_mode='crank')
scene = SceneBuilder.from_figurine(cfg)
gen = AutomataGenerator(scene, seed=42)
gen.generate()
assert 'crank_handle' in gen.all_parts
assert 'motor_mount' not in gen.all_parts
```

## LIVRABLES

Retourne-moi le fichier `automata_unified_v4.py` **complet patché** avec :
1. Les 6 nouveaux mouvements fonctionnels
2. Tous les tests passants
3. Zéro régression sur l'existant

**NE PLANTE PAS CETTE FOIS.** Si le fichier est trop gros pour une seule réponse, donne-moi le diff/patch des zones modifiées avec les numéros de lignes exacts, et je l'appliquerai moi-même.
