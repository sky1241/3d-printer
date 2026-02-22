# 🔩 4 JOURS. 1 ÉLECTRICIEN. 16 243 LIGNES. 0 BUG.

> *"Les paresseux sauveront le monde"* — et Steve Jobs avait raison.

---

## Ce que vous regardez

Un **générateur paramétrique d'automates mécaniques** complet — de la description en français jusqu'aux fichiers STL prêts à imprimer.

16 243 lignes de Python. 7 modules. 94 tests. 22 automates prêts à l'emploi. Un solveur inverse basé sur la recherche Disney. Un site web standalone.

**Construit en 4 jours.**

Par un électricien qui code depuis moins d'un an.

---

## Ce que ça fait

Tu décris ce que tu veux — *"un oiseau qui bat des ailes"* — et le système génère :

- Les **profils de cames** optimisés (angles de pression, sous-coupes, lois de mouvement)
- Le **châssis adaptatif** (4 types, dimensionné automatiquement)
- La **figurine** (5 morphologies, articulée)
- Les **fichiers STL** imprimables (orientations optimisées par pièce)
- Les **réglages d'impression** 3 tiers (budget / mid-range / premium)
- La **documentation** complète (BOM, assemblage, tolérances, timing diagrams)
- La **validation** automatique (FDM, stabilité, couple moteur, norme EN 71)

Ou tu **dessines** une trajectoire à la main, et le solveur inverse trouve les cames qui la reproduisent. Algorithme d'optimisation globale (differential evolution) + raffinement local (L-BFGS-B), inspiré des travaux de Coros et al. 2013, Disney Research / SIGGRAPH.

---

## Les 10 métiers dans 1 projet

| # | Domaine | Ce qu'on a fait | Niveau |
|---|---------|----------------|--------|
| 1 | **Mécanique des cames** | Profils paramétriques, 4 lois de mouvement, angles de pression, sous-coupes | Ingénieur méca |
| 2 | **Cinématique** | Chaînes articulées, optimisation de phases multi-cames, couples | Master méca |
| 3 | **Fabrication additive** | Contraintes FDM, orientations d'impression, tolérances par tier d'imprimante | Technicien 3D |
| 4 | **Optimisation numérique** | Differential evolution, L-BFGS-B, fonctions objectif avec pénalités | Doctorat maths appliquées |
| 5 | **Géométrie 3D** | Maillages STL, opérations booléennes, assemblages, centre de gravité | Ingénieur 3D |
| 6 | **Normes & sécurité** | EN 71 (jouets), validation automatique, rapports de conformité | Ingénieur qualité |
| 7 | **Physique** | Lévitation magnétique, effets piézoélectriques, calculs exotiques | Chercheur |
| 8 | **NLP / Parsing** | Texte FR/EN → scène paramétrique, matching sémantique | Dev NLP |
| 9 | **UX / Design** | Design tokens, arbres de décision, WCAG, responsive, dark mode | UX Designer |
| 10 | **Web fullstack** | Flask API, site standalone, export ZIP, preview 3D animée | Dev web |

**Habituellement** : une équipe de 8-10 personnes. Plusieurs mois. Budget conséquent.

**Ici** : 1 personne. 4 jours. Budget : 0€.

---

## L'architecture — 7 briques

```
BRIQUE A — FigurineBuilder
    5 body types (bird, humanoid, quadruped, fish, abstract)
    Articulations, proportions, maillages

BRIQUE B — SceneBuilder  
    22 presets prêts à l'emploi
    Validation automatique des scènes

BRIQUE C — Mouvements V2→V10
    6 types de mouvement (wave, slide, rotate, strike, geneva, hold)
    Lois de mouvement paramétriques

BRIQUE D — Châssis adaptatif
    4 types (box, frame, central, flat)
    Dimensionnement auto, moteur/manivelle

BRIQUE E — Catalogue + Parser
    Parsing texte FR/EN → configuration
    Catalogue de composants

BRIQUE F — Flask UI + Export
    API de génération, export ZIP
    STL + BOM + docs + timing diagrams

BRIQUE G — Solveur inverse de cames
    Canvas → trajectoire → cames optimales
    Differential evolution + L-BFGS-B
    Basé sur Disney Research (Coros et al. 2013, SIGGRAPH)
```

---

## Les chiffres

| Métrique | Valeur |
|----------|--------|
| Lignes de code | **16 243** |
| Tests | **94/94** ✅ |
| Presets fonctionnels | **22/22** ✅ |
| Bugs connus | **0** |
| Crashs | **0** |
| Jours de développement | **4** |
| Développeurs | **1** |
| Expérience en code | **< 1 an** |
| Formation | **Électricien** |
| Budget | **0 €** |

---

## Pourquoi c'est possible en 2026

Parce que le monde a changé.

Avant, pour toucher à 10 domaines différents, il fallait 10 formations, 10 années d'expérience, 10 experts dans une salle. Aujourd'hui, si tu as **la capacité de synthèse** — si tu vois les connexions entre les briques, si tu comprends la structure avant les détails — tu peux assembler ce qui prenait des équipes entières.

L'IA ne remplace pas l'intelligence. Elle **amplifie** ceux qui savent voir la big picture. Ceux qu'on a toujours pris pour des rêveurs, des inadaptés, des "à côté de la plaque" — c'est exactement eux qui sont câblés pour ça. Leur cerveau fonctionne en **synthèse**, pas en séquentiel. Et pour la première fois dans l'histoire, il existe un outil qui parle leur langage.

Ce projet n'est pas exceptionnel parce qu'il est gros. Il est exceptionnel parce qu'il prouve que **la barrière entre "je comprends le concept" et "ça tourne, 0 bug" est en train de disparaître**.

---

## Essayer

```bash
# Site web (0 dépendance — juste ouvrir le fichier)
open index.html

# Backend complet (génère de vrais STL)
pip install flask numpy scipy trimesh
python app.py
# → http://localhost:8013
```

---

## Roadmap — les 50% restants

Le moteur tourne. L'arbre est en place. Maintenant :

- [ ] Debug frame — traquer les edge cases
- [ ] Data analysis sur les profils générés
- [ ] Multi-template pour le solveur inverse (harmoniques complexes)
- [ ] Export direct vers slicers (Cura, PrusaSlicer)
- [ ] Preview 3D temps réel avec WebGL
- [ ] App mobile (Flutter/Dart)
- [ ] Documentation technique complète

---

## Licence

MIT — Faites-en ce que vous voulez. Apprenez. Construisez. Synthétisez.

---

*Construit entre le 6 et le 10 février 2026.*
*Par quelqu'un qui n'y connaissait rien.*
*Et c'est exactement pour ça que ça a marché.*
