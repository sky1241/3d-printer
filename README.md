# 🔩 Automata Generator

**Générateur paramétrique d'automates mécaniques imprimables en 3D**

16 243 lignes · 94 tests · 22 presets · 0 bug · 4 jours de dev

👉 **[Lire l'histoire complète →](STORY.md)**

## Quick Start

```bash
# Option 1: Site web (0 dépendance)
# Télécharger index.html et l'ouvrir dans un navigateur

# Option 2: Backend complet (génère de vrais STL)
pip install flask numpy scipy trimesh
python app.py
# → http://localhost:8013
```

## Fichiers

| Fichier | Description |
|---------|------------|
| `automata_unified_v4.py` | Moteur complet — 16 243 lignes, briques A→G |
| `app.py` | Backend Flask — API génération + export |
| `index.html` | Site standalone — 0 dépendance |
| `STORY.md` | L'histoire du projet |
| `MANIFEST.md` | État technique du backup |
| `backup_status.json` | Validation: 22/22 presets, 94/94 tests |

## Construit par

Un électricien qui code depuis moins d'un an. [L'histoire →](STORY.md)
