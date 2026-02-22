# 🔧 PROMPT DE REPRISE — Automata Generator Site V4

## CONTEXTE PROJET

Je développe un **générateur d'automates mécaniques paramétriques** pour impression 3D (Ender-3 / Bambu Lab X1C).

**Code Python backend** : `automata_unified_v4.py` — 16 243 lignes, 94/94 tests ✅, 22 presets
**Site frontend** : `automata.html` — HTML standalone (pas de serveur), ~380 lignes
**GitHub** : https://github.com/sky1241/3d-printer

---

## ÉTAT ACTUEL DU SITE (V3)

Le site V3 est fonctionnel avec :
- Design industriel dark (#06060a) + accent orange (#ff6b35)
- Fonts : DM Sans + JetBrains Mono
- Canvas 2D animé (cames rotatives, followers, figurines)
- Loading animation 7 étapes
- Page résultats avec stats + accordion technique
- Mobile responsive, 540px max-width

**MAIS il y a des problèmes majeurs à corriger :**

---

## 🔴 PROBLÈMES IDENTIFIÉS — À CORRIGER EN V4

### 1. SEULEMENT 8-10 PRESETS AFFICHÉS AU LIEU DE 17

Le code Python contient **17 presets uniques + 5 alias** dans `SCENE_PRESETS` :

**10 figurines animées :**
- nodding_bird (Oiseau qui hoche)
- flapping_bird (Aigle — ailes battantes)
- walking_figure (Marcheur)
- bobbing_duck (Canard)
- rocking_horse (Cheval à bascule)
- pecking_chicken (Poule)
- waving_cat (Chat maneki-neko)
- drummer (Batteur)
- blacksmith (Forgeron) ← MANQUANT sur le site !
- swimming_fish (Poisson) ← MANQUANT sur le site !

**7 mouvements mécaniques :**
- slider (Translation linéaire)
- rocker (Rotation oscillante)
- turntable (Plateau Geneva)
- sequence (Séquence multi-étapes)
- striker (Frappe V2)
- holder (Maintien en position)
- multi_axis (Multi-axes combinés)

→ **TOUS les 17 doivent être affichés**, organisés en 2 sections : "Figurines" et "Mouvements"

### 2. TOGGLE MOTEUR / MANIVELLE MANQUANT

L'utilisateur doit pouvoir choisir entre :
- **🖐️ Manivelle** (manuel, sans moteur)
- **⚡ Moteur** (motorisé)

Ce toggle doit être visible en haut, AVANT le choix du preset. Il influence la génération (arbre moteur vs poignée manivelle).

### 3. MODE CUSTOM INCOMPLET

Le mode Custom existe mais n'exploite pas assez les 7 types de mouvements mécaniques du backend.

---

## SPECS TECHNIQUES DU SITE

- **HTML standalone** — tout dans un seul fichier (CSS + JS inline)
- **Pas de framework** — vanilla JS, Canvas 2D API
- **Pas de dépendance serveur** — ouvrable en double-clic dans le navigateur
- **Google Fonts** (DM Sans, JetBrains Mono) — seule dépendance externe
- **Mobile-first** — touch optimized, max-width 540px

---

## CE QU'IL FAUT FAIRE

Refaire le site V4 avec :

1. ✅ Toggle **Manivelle / Moteur** en haut
2. ✅ **17 presets** organisés en 2 catégories (Figurines + Mouvements)
3. ✅ Garder le design industriel dark + orange
4. ✅ Garder le canvas 3D animé
5. ✅ Garder loading + page résultats
6. ✅ UX best practices (accessibility, feedback visuel, transitions smooth)
7. ✅ Tout dans un seul fichier HTML standalone

---

## FICHIERS À CONSULTER

- Le site actuel V3 : `automata.html` (dans les uploads ou outputs)
- Le code Python : `automata_unified_v4.py` — chercher `SCENE_PRESETS` (ligne ~4394) pour la liste complète
- Les transcripts précédents dans `/mnt/transcripts/` si besoin de contexte

---

*Merci de commencer par lire le site V3 existant, puis le refaire en V4 avec les corrections ci-dessus.*
