# 🔄 PROMPT DE REPRISE — Session Figurines Articulées
# Dernière session: 13 février 2026
# Dernier commit: f631f8e (main, pushed)

---

## QUI EST L'UTILISATEUR

Sky — project manager, pas dev. Travaille avec l'IA pour assembler les systèmes. Parle français, style direct et informel. Préfère "brique par brique" avec tests complets à chaque étape. Zéro tolérance pour les bugs.

---

## LE PROJET

**Automata Generator v4** — Un système Python (~18,800 lignes) qui génère des automates mécaniques à came imprimables en 3D (STL). Tu tapes un nom d'animal → le système génère le mécanisme complet (châssis, cames, leviers, arbres, pushrods) + une figurine décorative, exportable en STL pour impression FDM.

**Repo**: `~/3d-printer/` (GitHub: sky1241/3d-printer, branch main)
**Fichier principal**: `automata_unified_v4.py` (~18,800 lignes)

---

## ÉTAT ACTUEL DU CODE

### Ce qui marche ✅
- **11 presets** fonctionnels (nodding_bird, flapping_bird, walking_figure, turtle_simple, turtle_walking, etc.)
- **17 espèces dynamiques** générées via `living_beings_db.py` (chat → dragon)
- **94 contraintes** dans 9 blocs (mécanique, fabrication, sécurité EN 71, thermique, FDM)
- **Mode crank** = 100% imprimable, zéro hardware externe (pas de moteur)
- **Mode motor** = N20 avec auto-upgrade selon torque
- **Export STL** fonctionnel pour toutes les espèces
- **FigurineBuilder** (L6804-7015) génère des figurines en CSG (ellipsoïdes, cylindres, cônes)
- Auto-scaling: shaft Ø4→6mm, motor upgrade, mid-bearing, cam spacing, chassis expand

### CE QUI NE MARCHE PAS ❌ (= le chantier en cours)
**Les figurines sont des DÉCORATIONS STATIQUES**. Le FigurineBuilder actuel crée des blobs cosmétiques:
- Le pushrod pousse TOUT le bloc figurine vers le haut
- La tête ne hoche PAS — tout le corps bouge ensemble
- Aucune articulation mécanique (pas de pivot, pas de trou d'axe)
- Corps pas fixé au châssis, pas de parties mobiles séparées

**C'est LE problème à résoudre** → Module "ArticulatedFigurineBuilder"

---

## SYSTÈME DE TESTS — CRITIQUE ⚠️

Avant CHAQUE commit, lancer les 2 suites de tests:

```bash
cd ~/3d-printer
python3 regression_test.py        # 9/9 blocs + 9/9 presets + 13/13 debug
python3 regression_test_dynamic.py # 17/17 espèces dynamiques
```

**Résultat attendu:**
- `✅ NO REGRESSIONS — SAFE TO PUSH`
- `✅ ALL 17 BUILDERS PASS — dynamic pipeline OK`

Si un test casse → on ne push PAS, on debug d'abord.

---

## FICHIERS CLÉS À CONNAÎTRE

| Fichier | Rôle |
|---------|------|
| `automata_unified_v4.py` | LE moteur principal (~18,800 lignes) |
| `regression_test.py` | Tests statiques (9 blocs + 9 presets + 13 debug) |
| `regression_test_dynamic.py` | Tests dynamiques (17 espèces, baselines de part count) |
| `living_beings_db.py` | Base de données 118 espèces, 42 body plans |
| `RESEARCH_ARTICULATED.py` | **DATA FRAÎCHE** — constantes, clearances, formules, 12 body plan templates |
| `BATTLE_PLAN.md` | **PLAN DE BATAILLE** — 9 étapes détaillées avec tests par étape |
| `TODO.md` | Liste complète des tâches (ART-001 → ART-001l) |
| `CODEMAP_v4.md` | Architecture du code, 18,615 lignes documentées |
| `BUG_TRACKER_v2.md` | Historique bugs — actuellement 17/17 clean |
| `AUDIT.md` | Audit complet du système |

---

## LE PLAN DE BATAILLE (9 étapes)

On attaque **brique par brique**. Chaque étape est isolée et testée.

| # | Étape | Status | Risque | Temps |
|---|-------|--------|--------|-------|
| 1 | **Pin Joint Generator** — create_pin_joint(d, length, clearance) → (axe_mesh, trou_mesh) | ❌ À FAIRE | Zéro | 15min |
| 2 | **Body Splitter** — split_at_joint(mesh, cut_point, normal) → (fixed, mobile) | ❌ | Faible | 30min |
| 3 | **Joint + Split combo** — ajouter trou d'axe dans les 2 parties coupées | ❌ | Moyen | 30min |
| 4 | **Pushrod Attach** — point d'attache + socket sur partie mobile | ❌ | Faible | 15min |
| 5 | **Pushrod Router** — tracer pushrod levier→joint sans collision | ❌ | Moyen | 30min |
| 6 | **Turtle Simple** (1 joint = cou) — première intégration complète | ❌ | Élevé | 1h |
| 7 | **Turtle Walking** (6 joints) — tête + 4 pattes + queue | ❌ | Élevé | 1h |
| 8 | **Généralisation** — 12 body plans pour toutes les espèces | ❌ | Max | 2h |
| 9 | **Constraints B10** — nouveau bloc de checks pour articulations | ❌ | Moyen | 1h |

**COMMENCER PAR ÉTAPE 1** — c'est isolé, risque zéro, ça touche à rien d'existant.

---

## DONNÉES TECHNIQUES (dans RESEARCH_ARTICULATED.py)

Les constantes sont PRÊTES à être utilisées:
- `PIN_CLEARANCES` — clearances par Ø d'axe (3/4/5/6mm), 3 niveaux
- `BALL_JOINT_CLEARANCES` — rotules Ø6/8/10mm
- `MATERIALS` — PLA/PETG/TPU (Young, yield, friction, fatigue)
- `MOTION_TO_JOINT` — 12 mouvements → type d'articulation optimal
- `BODY_PLAN_JOINTS` — 12 templates (turtle, bird, biped, quadruped, etc.)
- `PUSHROD_CONFIGS` — 5 types de routing (direct, bell-crank, amplified, Y-split, parallelogram)
- Formule clé: **θ = asin(Δ_pushrod / R_bras)**

---

## ARBRE DU REPO (structure)

```
~/3d-printer/
├── automata_unified_v4.py      # Moteur principal
├── regression_test.py           # Tests statiques
├── regression_test_dynamic.py   # Tests 17 espèces
├── living_beings_db.py          # DB 118 espèces
├── RESEARCH_ARTICULATED.py      # Data articulations (NOUVEAU)
├── BATTLE_PLAN.md               # Plan 9 étapes (NOUVEAU)
├── TODO.md                      # Roadmap (NOUVEAU)
├── CODEMAP_v4.md                # Architecture code
├── BUG_TRACKER_v2.md            # Historique bugs
├── AUDIT.md                     # Audit système
└── ... (autres docs/prompts)
```

---

## ISSUES CONNUES (non-bloquantes)

| Issue | Sévérité | Notes |
|-------|----------|-------|
| `--validate` crash line ~14160 | ⚠️ | Codex audit, pas investigué |
| Unknown roles in `print_settings.json` | ⚠️ | Codex audit |
| BOM incomplet mode crank | ℹ️ | Manque liste quincaillerie |
| Missing DE/L-BFGS-B optimizers | ℹ️ | Codex audit |
| turntable cam 373mm > build 256mm | ℹ️ | Auto-split planifié |
| 31 collisions pushrod turtle_walking | ℹ️ | Non-bloquant, sera fixé par ART-001 |

---

## COMMENT DÉMARRER LA SESSION

```bash
# 1. Vérifier l'état du repo
cd ~/3d-printer && git log --oneline -5

# 2. Lancer les tests (doit être 100% vert)
python3 regression_test.py
python3 regression_test_dynamic.py

# 3. Lire le battle plan
cat BATTLE_PLAN.md

# 4. Lire les données techniques
cat RESEARCH_ARTICULATED.py

# 5. Attaquer l'étape 1 (Pin Joint Generator)
# → Fonction isolée, pas d'impact sur l'existant
# → Voir BATTLE_PLAN.md pour les tests à passer
```

---

## RÈGLES DE TRAVAIL

1. **Brique par brique** — jamais 2 étapes en même temps
2. **Tests complets** après chaque modification (regression_test.py + regression_test_dynamic.py)
3. **Git commit + push** après chaque étape validée
4. **Si un test casse** → on debug immédiatement, on ne passe pas à la suite
5. **Fallback** — si une étape échoue, l'ancien mode (figurines décoratives) doit toujours marcher
6. Le user préfère le français, style décontracté

---

## COMMIT HISTORY RÉCENT (pour contexte)

```
f631f8e docs: research data + battle plan figurines articulées
fad9f56 docs: prompt ChatGPT figurine articulée + TODO list complète
59def7b feat: turtle figurines (carapace, tête, pattes, queue, yeux)
c244ded feat: turtle presets 100% printable (crank mode, no motor)
77965ce feat: add turtle_simple (1 cam) + turtle_walking (6 cams) presets
```
