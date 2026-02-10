# 🔩 ROADMAP — LA LISTE DE COURSES

> Status: 50% fait. Le moteur tourne. Maintenant on finit le truc.

---

## 🟢 CE QUI EST FAIT (ne plus toucher)

```
✅ Brique A — FigurineBuilder (5 body types)
✅ Brique B — SceneBuilder (22 presets, 22/22 OK)
✅ Brique C — Mouvements V2-V10 (6 types)
✅ Brique D — Châssis adaptatif (4 types)
✅ Brique E — Catalogue + Parser FR/EN
✅ Brique F — Flask UI + Export
✅ Brique G — Solveur inverse (differential evolution)
✅ 94/94 tests
✅ Site web standalone
✅ GitHub à jour
```

---

## 🔴 CE QU'IL RESTE — PAR BLOC

### BLOC 1 — IMPRIMANTES (priorité max)
> But: que le système adapte TOUT aux specs réelles de la machine

**Ce que je code:**
- Profil machine complet (volume, vitesse, résolution, matériaux)
- Auto-détection des limites (pièce trop grande → découpe auto)
- Réglages slicer par machine (température, rétraction, supports)
- Export direct profil Cura / PrusaSlicer / OrcaSlicer / BambuStudio

**CE QUE TOI TU ME DONNES:**
```
□ Question 1: Tu as quoi comme imprimante(s) ?
   → Marque + modèle exact (ex: "Ender-3 V3 SE", "Bambu Lab X1C")
   
□ Question 2: Quels matériaux tu utilises ?
   → PLA ? PETG ? TPU ? ABS ?
   
□ Question 3: Quel slicer tu utilises ?
   → Cura ? PrusaSlicer ? BambuStudio ? OrcaSlicer ?
   
□ Question 4: Tu imprimes avec quels réglages habituels ?
   → Layer height (0.2 ? 0.16 ? 0.12 ?)
   → Vitesse (50mm/s ? 100mm/s ?)
   → Supports (oui/non, type tree ?)
   → Si tu sais pas → dis "je sais pas" c'est OK
   
□ Question 5: Y'a des imprimantes populaires que tu veux cibler ?
   → Pour que les AUTRES puissent imprimer facilement
   → Ex: "tout le monde a une Ender-3" ou "cible Bambu"
```

---

### BLOC 2 — VALIDATION PHYSIQUE
> But: que ce qui sort de la machine MARCHE vraiment

**Ce que je code:**
- Check auto des jeux/tolérances par matériau
- Vérification des assemblages (est-ce que ça rentre ?)
- Simulation de rotation (la came tourne-t-elle sans frotter ?)
- Rapport "print & check" avec photo de référence

**CE QUE TOI TU ME DONNES:**
```
□ Question 6: T'as déjà imprimé un des 22 presets ?
   → Si oui: lequel ? Ça marchait ?
   → Si non: c'est OK — on va définir le premier test

□ Question 7: Les tolérances actuelles (0.3mm clearance) 
   ça te semble correct pour ton imprimante ?
   → Trop serré ? Trop lâche ? Aucune idée ?

□ Question 8: Quel diamètre de tige tu utiliserais pour l'arbre ?
   → 4mm (standard) ? 3mm ? Autre ?
   → Tige acier ? Tige carbone ? Filament rigide ?
```

---

### BLOC 3 — UX / SITE WEB
> But: que n'importe qui puisse utiliser le truc sans réfléchir

**Ce que je code:**
- Wizard amélioré (preview temps réel pendant la config)
- Preview 3D WebGL (rotation libre de l'automate)  
- Export 1-clic vers slicer
- Mode "je connais rien" (3 questions → automate prêt)
- Mode "expert" (tout paramétrable)
- Galerie des 22 presets avec GIF animé de chaque mouvement

**CE QUE TOI TU ME DONNES:**
```
□ Question 9: Le site actuel (index.html) — 
   qu'est-ce qui manque en premier ?
   → Preview 3D ? Téléchargement STL direct ? Autre ?

□ Question 10: Tu veux cibler qui ?
   → Débutants impression 3D ?
   → Makers expérimentés ?
   → Éducation / écoles ?
   → Tous ?

□ Question 11: Langue(s) du site ?
   → Français seul ? FR + EN ? Multilingue ?
```

---

### BLOC 4 — SOLVEUR INVERSE (amélioration)
> But: que le dessin → came soit encore plus précis

**Ce que je code:**
- Multi-template (rdrd + rr + rdr combinés)
- Harmoniques multiples (pour les trajectoires complexes type 8)
- Preview temps réel du résultat pendant l'optimisation
- Comparaison visuelle trajectoire dessinée vs simulée

**CE QUE TOI TU ME DONNES:**
```
□ Question 12: Le solveur inverse c'est important pour toi ?
   → C'est la feature killer ?
   → Ou les presets suffisent pour l'instant ?
```

---

### BLOC 5 — DOCUMENTATION / COMMUNAUTÉ
> But: que les gens comprennent et contribuent

**Ce que je code:**
- Guide "Premier automate en 30 minutes"
- Vidéo script (tu filmes, je prépare le script)
- Documentation API pour les devs
- Tuto "créer son propre preset"

**CE QUE TOI TU ME DONNES:**
```
□ Question 13: Tu veux faire une vidéo ?
   → Filmer l'impression + assemblage d'un preset ?
   → Screen recording du site ?

□ Question 14: Tu veux ouvrir aux contributions ?
   → Open source pur (MIT) ?
   → Tu gardes le contrôle ?
```

---

### BLOC 6 — APP MOBILE (futur)
> But: configurer depuis le téléphone, lancer l'impression

**Ce que je code:**
- App Flutter/Dart (ton terrain)
- Sync avec le backend
- Notifications quand l'impression est prête
- Scan QR → instructions d'assemblage

**CE QUE TOI TU ME DONNES:**
```
□ Question 15: L'app mobile c'est pour quand ?
   → Maintenant en parallèle ?
   → Après que le web soit fini ?
   → Pas prioritaire ?
```

---

## 📋 RÉSUMÉ — TES 15 QUESTIONS

Réponds quand tu veux, dans l'ordre que tu veux. Même "je sais pas" c'est une réponse. Chaque réponse débloque du travail de mon côté.

| # | Question | Bloc |
|---|----------|------|
| 1 | Ton/tes imprimante(s) ? | Imprimantes |
| 2 | Matériaux ? | Imprimantes |
| 3 | Slicer ? | Imprimantes |
| 4 | Réglages habituels ? | Imprimantes |
| 5 | Imprimantes à cibler ? | Imprimantes |
| 6 | Déjà imprimé un preset ? | Validation |
| 7 | Tolérances OK ? | Validation |
| 8 | Diamètre tige arbre ? | Validation |
| 9 | Quoi d'abord sur le site ? | UX |
| 10 | Public cible ? | UX |
| 11 | Langues ? | UX |
| 12 | Solveur inverse = priorité ? | Solveur |
| 13 | Vidéo ? | Docs |
| 14 | Open source ? | Docs |
| 15 | App mobile quand ? | Mobile |

---

## 🎯 ORDRE D'ATTAQUE RECOMMANDÉ

```
Semaine 1: BLOC 1 (imprimantes) + BLOC 2 (validation)
           → Un preset imprimé et assemblé qui MARCHE
           
Semaine 2: BLOC 3 (UX) 
           → Site utilisable par n'importe qui
           
Semaine 3: BLOC 4 (solveur) + BLOC 5 (docs)
           → Feature killer + premier tuto
           
Semaine 4+: BLOC 6 (mobile) + itérations
           → App Flutter + retours utilisateurs
```

---

*Réponds aux questions → je code. C'est aussi simple que ça.*
