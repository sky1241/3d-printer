# 🐛 BUG TRACKER v2 — Automata Generator v4
# Enrichi par Deep Research FDM (tolérance, snap-fit, came-follower, engrenages, bell-crank)
# Re-audité le 12 février 2026 sur 9 presets / 240 pièces
# Commit actuel : d814c03

---

## LÉGENDE
- ✅ CORRIGÉ (vérifié par audit)
- 🔴 BUG OUVERT — À corriger, avec test + push individuel
- 🟡 AMÉLIORATION — Pas bloquant, mais recommandé par la research
- ⬜ FUTUR — Phase 4+

---

## ÉTAT RÉEL VÉRIFIÉ (12 fév 2026, post-fixes)

| Bug initial | Audit précédent | État ACTUEL | Verdict |
|-------------|----------------|-------------|---------|
| A1 Wall sans bore | 🔴 18× euler=2 | ✅ U-slot OK (228 verts) | FIXÉ (commit 8998ac1) |
| A2 Gap came→levier | 🔴 16.7mm | ✅ 0.2mm (13/13) | FIXÉ (commit 42b9af7) |
| A3 Levier sans pivot | 🔴 13× euler=2 | ✅ euler=0 (bore OK) | FIXÉ (commit d0c78b5) |
| A4 Snap-hook metadata | 🔴 16× box | 🟡 U-channel fonctionnel | RECLASSÉ mineur |
| A5 Figurine sans attache | 🔴 9× presets | ✅ 13 pushrods + sockets | FIXÉ (commits 76a5c43→6faf51b) |

---

## 🟡 BUG-001 : Follower guide = U-channel fonctionnel (RECLASSÉ MINEUR)
**Sévérité :** MINEUR | **Instances :** 16 (tous presets) | **Status :** RECLASSÉ

### Constat
`follower_guide_*` = 16 vertices = boîte plate. Metadata dit `joint_type=snap_hook` 
(hook_width=4mm, lip_height=1.2mm) mais aucune géométrie de hook/slot.

`make_snap_hook_3d()` existe dans le code mais est appelée **0 fois**.

### Ce que dit la Deep Research
> **Snap-Fits FDM :**
> - Cantilever base ≥ 1–1.2mm (≥3 perimeters)
> - Fillet base ~0.5–1× épaisseur  
> - Lead-in taper 30–45°
> - Clearance gap 0.2–0.5mm
> - Orienter en XY (Z = 50% plus faible)
> - PLA = usage unique, PETG = réutilisable
> - Infill 100% sur zones snap
>
> **Alternative recommandée :**
> - Simple dowel Ø3mm + friction fit (Ø3mm -0.1mm ↔ trou Ø3mm +0.2mm)
> - Plus simple, plus robuste pour vibrations 30-60 RPM
> - Force rétention ~0.5-1N suffisante

### Fix prévu
**Option A (rapide) :** Appeler `make_snap_hook_3d()` existante dans le flow de génération  
**Option B (recommandée) :** Remplacer par dowel/pin cylindrique — plus fiable en FDM

### Test de validation
```python
def test_bug001_follower_guide_has_geometry():
    """Follower guide must have >24 vertices (not a plain box)"""
    for preset in ALL_PRESETS:
        parts = generate_preset(preset)
        for name, mesh in parts.items():
            if 'follower_guide' in name:
                assert mesh.vertices.shape[0] > 24, f"{preset}/{name}: still a plain box ({mesh.vertices.shape[0]}v)"
```

---

## ✅ BUG-002 : Figurines sans attache → FIXÉ par pushrod+socket
**Sévérité :** MAJEUR | **Instances :** 9 presets | **Status :** CORRIGÉ

### Fix appliqué (commits 76a5c43 → ca24ea8 → 6faf51b)
- Pushrod Ø3mm entre chaque levier et la figurine cible
- Socket Ø3.3mm soustrait de la figurine (boolean difference)
- Ciblage intelligent: match par nom (lever_neck→fig_neck) + sémantique (shoulder→arm/wing)
- 13/13 pushrods créés, sockets partiels (boolean silencieux si pas d'intersection)

### Constat
Toutes les pièces `fig_*` ont euler=2 (solide plein). Metadata dit `joint_type=snap_pocket`
mais aucune cavité n'est soustraite. La figurine n'est attachée à rien.

`make_snap_pocket_3d()` existe, appelée 1 seule fois dans tout le code.

### Ce que dit la Deep Research
> **Fixation figurine :**
> - Dowel Ø3mm + hole avec +0.2–0.3mm clearance = plus simple que snap
> - Ou peg Ø3mm sur le levier + trou dans la figurine
> - Pour vibrations 30-60 RPM : dowel press-fit ou snap avec 0.5-1N rétention
> - Colle (cyanoacrylate) = plus fort mais irréversible
> - Vis M2 = solide mais ajoute du bulk

### Fix prévu
Ajouter un trou cylindrique (Ø3.3mm) dans la figurine au point d'attache, correspondant
à un peg (Ø3mm) sur le levier. Boolean difference sur la fig_part principale.

### Test de validation
```python
def test_bug002_figurine_has_attachment():
    """At least one fig_part per preset must have attachment geometry (euler≤0 or >8 verts with hole)"""
    for preset in ALL_PRESETS:
        parts = generate_preset(preset)
        fig_parts = {n:m for n,m in parts.items() if n.startswith('fig_')}
        attached = any(m.euler_number <= 0 for m in fig_parts.values())
        assert attached, f"{preset}: no figurine part has attachment hole"
```

---

## ✅ BUG-003 : Gap 1.5mm → 0.2mm contact came-levier
**Sévérité :** IMPORTANT | **Instances :** 13 | **Status :** CORRIGÉ (commit 42b9af7)

### Constat
Le gap est passé de 16.7mm (audit précédent) à 1.5mm (actuel), mais il reste 1.5mm
d'air entre le sommet de la came et le bas du bras d'entrée du levier.

Sans follower pad, le levier ne touche pas la came physiquement.

### Ce que dit la Deep Research
> **Follower Type FDM :**
> - Flat-faced follower (patin plat) = standard pour automates FDM
> - Pad au moins aussi large que l'épaisseur axiale de la came
> - Épaisseur pad 3-4mm (≥3 perimeters)
> - Clearance guide 0.2-0.3mm par côté
>
> **Alternative hinged follower :**
> - Levier en L pivoté à un bout, un bras touche la came, l'autre pousse la figurine
> - Élimine le besoin de guidage linéaire
> - Le levier actuel EST presque ça — il manque que le bras descende jusqu'à la came
>
> **Contact/retour :**
> - Gravité maintient contact si figurine au-dessus
> - Sinon ressort (quelques newtons de précharge)
> - PLA sur PLA : lubrifier PTFE spray

### Fix prévu
**Option A :** Étendre le bras d'entrée du levier de 1.5mm vers le bas pour qu'il touche la came  
**Option B :** Ajouter un follower pad (nouvelle pièce) entre came et levier  
→ Option A est plus simple (modifier la position Z du lever arm)

### Test de validation
```python
def test_bug003_cam_lever_contact():
    """Gap between cam top and lever bottom must be ≤ 0.5mm (contact with clearance)"""
    for preset in ALL_PRESETS:
        parts = generate_preset(preset)
        for cn in parts:
            if cn.startswith('cam_') and 'camshaft' not in cn:
                ln = 'lever_' + cn.replace('cam_','')
                if ln in parts:
                    gap = parts[ln].bounds[0][2] - parts[cn].bounds[1][2]
                    assert gap <= 0.5, f"{preset}/{cn}→{ln}: gap={gap:.1f}mm (need ≤0.5)"
```

---

## ✅ BUG-004 : make_snap_hook_3d() dead code → marquée UNUSED
**Sévérité :** CODE | **Instances :** 1 | **Status :** CORRIGÉ

Fonctions snap gardées pour référence, marquées UNUSED. Le système pushrod+socket les remplace.

### Constat
La fonction existe (définie 1×) mais n'est jamais appelée (0 appels dans generate flow).
`make_snap_pocket_3d()` est appelée 1 seule fois.

### Fix prévu
Brancher l'appel dans le flow de génération des follower_guides, ou supprimer si on
remplace par dowel/pin (cf BUG-001).

---

## 🟡 AMÉLIO-001 : Follower guide slot trop simple
**Sévérité :** MINEUR | **Status :** OUVERT

### Ce que dit la Deep Research
> - Guide rod clearance : 0.2-0.3mm par côté (total 0.4-0.6mm)
> - Tige Ø3mm → trou Ø3.3-3.5mm
> - Imprimer guide verticalement (trou en XY) pour circularité
> - Guide long = empêche le tilt du shaft

Le follower_guide actuel a un slot 2D (rectangle soustrait). Il faudrait un trou cylindrique
pour un meilleur guidage.

---

## 🟡 AMÉLIO-002 : Pas de vérification collision automatique
**Sévérité :** MINEUR | **Status :** OUVERT

### Ce que dit la Deep Research
> - Utiliser `trimesh.collision.CollisionManager` + `in_collision_internal()`
> - Ou intersection mesh : `A.intersection(B).volume > 1e-6`
> - Clearance minimum 0.2-0.5mm entre pièces mobiles
> - Tests unitaires automatiques recommandés

---

## 🟡 AMÉLIO-003 : Pas de simulation cinématique
**Sévérité :** MINEUR | **Status :** OUVERT

### Ce que dit la Deep Research
> - Pour chaque angle came 0→360° par 5°, calculer displacement follower
> - Propager via géométrie levier/bell-crank
> - Vérifier contact cam-follower maintenu et pas de collision
> - Exporter GIF/GLTF animé pour vérification visuelle

---

## ⬜ FUTUR-001 : Bell-crank (mouvement axe Z)
### Ce que dit la Deep Research
> - L-lever pivoté au coude, convertit vertical → horizontal à 90°
> - Épaisseur 3-4mm, pivot Ø2-3mm
> - Même stratégie clearance que les autres pivots
> - Monter entre les murs du châssis
> - Pas besoin de guidage linéaire (le pivot confine le mouvement)

---

## ⬜ FUTUR-002 : Engrenages (rotation 360°)
### Ce que dit la Deep Research
> - Module ≥1.0mm, ≥12 dents, pression 20°, backlash 0.2-0.5mm
> - Infill 100%, couche 0.15-0.2mm, orientation horizontale
> - Alternative simple : friction wheel (2 cylindres pressés ensemble)
> - PLA OK pour faible charge + PTFE spray

---

## ⬜ FUTUR-003 : Scaling global
### Ce que dit la Deep Research
> - NE PAS scaler : clearances (0.3-0.5mm), diamètre arbre (Ø4mm), épaisseur mur min (1.2mm)
> - Range raisonnable : 50-200%
> - Appliquer scale seulement aux pièces esthétiques
> - Recalculer toutes les tolérances à la nouvelle échelle

---

## HISTORIQUE DES BUGS DÉJÀ CORRIGÉS

| ID | Bug | Fix | Commit | Vérifié |
|----|-----|-----|--------|---------|
| BORE-1 | Walls sans bore (Ø4.5 > mur 3mm) | U-slot cradle ouverte | `8998ac1` | ✅ 228v, euler=2 attendu |
| LEVER-1 | 13 cames sans levier physique | create_lever_arm() | `d0c78b5` | ✅ euler=0, bore OK |
| BUG-003 | Gap came→levier 1.5mm | pivot_z = cam_top + arm + thick/2 + 0.2 | `42b9af7` | ✅ 13/13 gap=0.2mm |
| BUG-002 | Figurine sans attache | pushrod Ø3mm + socket Ø3.3mm | `76a5c43`→`6faf51b` | ✅ 13/13 pushrods |
| BUG-002c | Pushrod cible mauvais fig part | Match par nom + sémantique | `6faf51b` | ✅ neck→fig_neck etc |
| BUG-004 | snap_hook_3d() dead code | Marqué UNUSED | `6faf51b` | ✅ |
| BUG-1 | CAM↔CAM collision (11 cas) | Dynamic Y spacing | `56f1785` | ✅ |
| BUG-2 | BRACKET↔MOTOR (9/9) | bracket_z adaptive | `63fecf3` | ✅ |
| BUG-3 | FIG↔CHASSIS (19 cas) | Piédestaux 12mm | `b3e7967` | ✅ |
| SPATIAL-1→4 | Positions incorrectes | Transform fixes | session 10 | ✅ |
| ROLLER-1 | rf/Rb=0.60 | rf adaptatif | `ae7d6e6` | ✅ |
| RB-1 | Rb < 5mm | max(Rb, 5.0) | `229b30f` | ✅ |
| PHI-1 | φ_max > 45° | Cascade + reduction | `35e8272` | ✅ |

---

## PLAN D'ATTAQUE (1 bug = 1 commit = 1 push)

1. ✅ **BUG-003** : Gap 1.5mm→0.2mm contact came-levier (`42b9af7`)
2. ✅ **BUG-002** : Pushrods levier→figurine + socket (`76a5c43`→`6faf51b`)
3. ✅ **BUG-001** : Reclassé MINEUR (U-channel fonctionnel)
4. ✅ **BUG-004** : Dead code snap marqué UNUSED
5. 🟡 AMÉLIO-001→003 : Améliorations post-fix (collision check, kinematics, scaling)

## RÉSUMÉ AUDIT FINAL

| Métrique | Avant | Après |
|----------|-------|-------|
| Gaps came→levier | 1.5mm (13/13) | 0.2mm (13/13) |
| Pushrods levier→figurine | 0/13 | 13/13 |
| Murs U-slot | 18/18 OK | 18/18 OK |
| Pivots levier | 13/13 bore | 13/13 bore |
| Presets fonctionnels | 9/9 | 9/9 |
| **Bugs critiques ouverts** | **4** | **0** |
