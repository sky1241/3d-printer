# 🐛 BUG TRACKER v2 — Automata Generator v4
# Enrichi par Deep Research FDM + vérifié par audit automatisé
# Dernière mise à jour : 12 février 2026
# Commit actuel : 41162e6

---

## LÉGENDE
- ✅ CORRIGÉ — Vérifié par tests, pushé
- 🟡 RECLASSÉ — Pas un vrai bug / fonctionnel
- ⬜ FUTUR — Phase 4+

---

## ÉTAT VÉRIFIÉ — TOUS LES BUGS RÉSOLUS

| Bug | Description | Fix | Commit | Status |
|-----|-------------|-----|--------|--------|
| BUG-003 | Gap 1.5mm came→levier | pivot_z recalculé avec arm_thick/2 + 0.2mm FDM | `42b9af7` | ✅ 13/13 gaps=0.2mm |
| BUG-002 | Figurine pas attachée | Pushrod Ø3mm + socket Ø3.3mm vertical | `76a5c43` `ca24ea8` `41162e6` | ✅ 13/13 pushrods |
| BUG-001 | Follower guide = box | U-channel fonctionnel (euler=0, slot OK) | N/A | 🟡 Pas un bug |
| BUG-004 | make_snap_hook_3d() dead code | Marquée UNUSED, remplacée par pushrods | `ca24ea8` | ✅ Documenté |

---

## DÉTAILS DES CORRECTIONS

### ✅ BUG-003 : Gap came-levier (1.5mm → 0.2mm)
**Avant :** `pivot_z = cam_top_z + input_arm + 3` → gap 1.5mm
**Après :** `pivot_z = cam_top_z + input_arm + arm_thick/2 + 0.2` → gap 0.2mm FDM

La came pousse physiquement le bras d'entrée du levier. La gravité
maintient le contact dans les vallées du profil.

**Spécs Deep Research appliquées :**
- 0.2mm clearance FDM (recommandé 0.2-0.5mm)
- Contact par gravité (poids figurine > force centripète à 60 RPM)
- Levier en tant que hinged follower (pas de guidage linéaire nécessaire)

### ✅ BUG-002 : Liaison levier→figurine (pushrod + socket)
**Avant :** Aucune connexion physique entre levier et figurine
**Après :**
- Pushrod Ø3mm entre le tip du levier et la fig part la plus proche
- Name-based matching (lever_neck → fig_neck, lever_shoulder → fig_arm)
- Fallback par distance euclidienne
- Socket vertical Ø3.3mm (0.3mm clearance) soustrait dans la figurine
- Boolean via manifold3d

**Spécs Deep Research appliquées :**
- Dowel Ø3mm + hole Ø3.3mm (recommandé +0.2-0.3mm clearance)
- Socket vertical pour meilleure qualité FDM
- Profondeur max 50% hauteur fig (robustesse structurelle)

### 🟡 BUG-001 : Follower guide (reclassé)
Le follower guide est un U-channel fonctionnel :
- 16 vertices, euler=0 (slot traversant)
- slot_clearance=0.4mm par côté
- Guidage par gravité suffisant pour automates verticaux

### ✅ BUG-004 : Dead code snap functions
`make_snap_hook_3d()` et `make_snap_pocket_3d()` marquées UNUSED.
Remplacées par le système pushrod + socket (plus fiable en PLA).

---

## HISTORIQUE COMPLET DES CORRECTIONS

| Session | ID | Bug | Commit |
|---------|-----|-----|--------|
| 18 | BUG-003 | Gap came-levier 1.5→0.2mm | `42b9af7` |
| 18 | BUG-002 | Pushrod + socket figurine | `76a5c43` `ca24ea8` `41162e6` |
| 15 | A3 | Lever pivot hub bore fix | `ec6ed78` |
| 15 | AUDIT-3 | 3 bugs + B9 tests | `d814c03` |
| 13 | BORE-1 | Walls U-slot (Ø4.5 > mur 3mm) | `8998ac1` |
| 13 | LEVER-1 | 13 cames sans levier | `d0c78b5` |
| 12 | BUG-1 | CAM↔CAM collision | `56f1785` |
| 12 | BUG-2 | BRACKET↔MOTOR | `63fecf3` |
| 12 | BUG-3 | FIG↔CHASSIS | `b3e7967` |

---

## AMÉLIORATIONS FUTURES (Deep Research)

### ⬜ FUTUR-001 : Bell-crank (mouvement horizontal)
L-lever pivoté au coude, 3-4mm épaisseur, même clearance que pivots.

### ⬜ FUTUR-002 : Engrenages (rotation 360°)
Module ≥1.0mm, ≥12 dents, pression 20°, backlash 0.2-0.5mm.

### ⬜ FUTUR-003 : Collision automatique
`trimesh.collision.CollisionManager` + `in_collision_internal()`.

### ⬜ FUTUR-004 : Simulation cinématique
Balayage 0→360° par 5°, export GIF animé.

### ⬜ FUTUR-005 : Scaling global
Pièces esthétiques seulement, recalculer tolérances. Range 50-200%.

---

## RÉSUMÉ MÉTRIQUES

| Métrique | Valeur |
|----------|--------|
| Presets fonctionnels | 9/9 |
| Pièces par preset | 22-48 |
| Toutes watertight | oui |
| Cam-lever gap | 0.2mm |
| Pushrods | 13/13 levers connectés |
| Sockets figurine | OK (28mm³ enlevé en moyenne) |
| Tests régression | 9/9 pass |
