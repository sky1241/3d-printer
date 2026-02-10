# 🎭 Automata Generator — 100% 3D Printed Mechanical Toys

Générateur paramétrique d'automates mécaniques à cames. Tape une description en français, récupère des STL prêts à imprimer.

## ✨ Deux modes

| Mode | Description | Quincaillerie |
|------|-------------|---------------|
| `crank` 🔧 | 100% imprimé — manivelle à tourner | **Rien** (zéro €) |
| `motor` ⚡ | Motorisé N20 + arbre acier | ~15€ de composants |

## 🚀 Quick Start

```bash
# Générer un oiseau 100% imprimé (mode crank par défaut)
python automata_unified_v4.py --text "oiseau qui hoche la tête" --out oiseau/

# Générer un dragon motorisé
python automata_unified_v4.py --text "dragon qui bat des ailes" --mode motor --out dragon/

# Interface web (Flask)
python automata_unified_v4.py --web

# Tests
python automata_unified_v4.py --test
```

## 📦 Ce que ça génère

```
output/
├── parts/           # STL individuels
│   ├── base_plate.stl
│   ├── cam_neck.stl
│   ├── camshaft.stl        # Arbre PLA Ø6mm (crank) ou acier Ø4mm (motor)
│   ├── crank_handle.stl    # Manivelle (crank mode uniquement)
│   ├── collar_0.stl        # Colliers imprimés (crank mode uniquement)
│   ├── fig_body.stl        # Figurine paramétrique
│   └── ...
├── assembly.stl     # Vue assemblée
├── ASSEMBLY.md      # Guide d'assemblage pas-à-pas
├── BOM.md           # Liste de matériel
├── PRINT_SETTINGS.md # Réglages par pièce
└── scene.json       # Paramètres de la scène
```

## 🐦 Exemples supportés

```
"oiseau qui hoche la tête"          → bird / nod
"dragon qui bat des ailes"          → quadruped / flap + wings
"chat qui fait coucou"              → seated / wave
"bonhomme qui marche"               → biped / walk
"cheval à bascule"                  → quadruped / rock
"poisson qui nage"                  → fish / swim
"forgeron avec un marteau"          → biped / strike
"batteur qui tape tambour"          → biped / drum
"coeur qui bat"                     → seated / nod
"robot qui salue"                   → biped / wave
```

## 🏗️ Architecture (15,257 lignes)

| Brique | Rôle | Status |
|--------|------|--------|
| **A** | FigurineBuilder — 5 body types CSG | ✅ |
| **B** | SceneBuilder — Config → Scene | ✅ |
| **C** | Mouvements V2-V10 (slide, rotate, geneva...) | 🔜 |
| **D** | Châssis adaptatif | 🔜 |
| **E** | Parser texte FR/EN → FigurineConfig | ✅ |
| **F** | Flask UI offline | ✅ |
| **G** | Solveur inverse (trajectoire → came) | 🔜 |
| **Constraint Engine** | 59 trous de validation mécanique | ✅ |

## 🖨️ Imprimantes testées

- **Bambu Lab X1C** (premium) — réglages optimisés inclus
- **Ender-3** (budget) — supporté via tier system
- Tout FDM avec buse 0.4mm et PLA

## 📁 Fichiers

| Fichier | Description |
|---------|-------------|
| `automata_unified_v4.py` | Code principal (15,257 lignes) |
| `oiseau_100_pourcent_imprime.zip` | Package test prêt à imprimer |
| `prompt_brique_C.md` | Prompt pour ChatGPT (Brique C) |

## 🧪 Tests

94 checks internes couvrant :
- Mécanique (collision, couple, flexion, undercut...)
- Fabrication (FDM, tolérances, supports...)
- Sécurité (EN 71 jouets)
- Physique (fatigue, thermique, résonance...)

## License

MIT
