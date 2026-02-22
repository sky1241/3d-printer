# 🗺️ AUTOMATA CODE MAP — V7.13 (2041 lignes)
# Fichier: automata.html (single-file HTML)
# Repo: github.com/sky1241/3d-printer

## ARCHITECTURE RAPIDE

```
L1-168      HTML + CSS
L168-345    HTML body (UI panels, buttons, canvas)
L346-377    GLOBALS (figurine, motions, drive, gearRatio, selectedPiece)
L347-388    loadThreeJS() — charge Three.js depuis CDN
L389-836    TEMPLATES (33 animaux/objets) + formKeys (47 aliases)
L837-1021   AI PARSING — matchTemplate() + matchMotions()
L1022-1233  UI HANDLERS — steps, shapes, motions, sliders
L1234-1600  STL EXPORT — math utils, realCamRadiusSTL(), doGenerate()
L1601-1709  CAMERA + ANIMATION LOOP
L1710-1834  FIGURINE 3D — getShapeSize(), make3DShape(), buildFigurine3D()
L1835-2000  MECHANISM 3D — buildMechanism3D()
L2000-2041  HELPERS — rebuildAll3D(), highlightSelected3D(), toggleExplode()
```

## 🌳 ARBRE DE DÉCISION — "OÙ CHERCHER QUOI"

```
PROBLÈME ?
│
├── BOUTON/UI ne marche pas
│   ├── Bouton forme (circle,rect,tri...) → L1127 setShape()
│   ├── Bouton mouvement (TV,TH,OSC,ROT) → L1144 setMotion()
│   ├── Bouton phase (0°,90°,180°,270°) → L1158 setPhase()
│   ├── Bouton profil (smooth,sharp,dwell) → L1170 setProfile()
│   ├── Bouton pivot (haut,centre,bas..) → L1184 setPivot()
│   ├── Sliders (amp,speed,size,gear) → L1198 updateParam()
│   ├── Bouton drive (crank/motor) → L389 setDrive()
│   ├── Step navigation → L1028 goToStep()
│   └── Pièce select/toggle → L1059 selectPiece() / L1118 toggleMovable()
│
├── TEMPLATE pas reconnu ("un chat" → rien)
│   ├── formKeys manque un alias → L750-836 (formKeys dict)
│   ├── Template manque → L402-749 (TEMPLATES object)
│   └── Parsing AI foireux → L837 matchTemplate() / L880 matchMotions()
│
├── FIGURINE 3D foireuse (preview)
│   ├── Forme pas bonne → L1720 make3DShape()
│   ├── Position/taille → L1752 buildFigurine3D()
│   ├── Pièce pas visible → L1710 getShapeSize()
│   └── Rebuild manqué → L2000 rebuildAll3D()
│
├── MÉCANISME 3D foireux (preview)
│   ├── Box/Shaft/Bearings → L1835-1870 (début buildMechanism3D)
│   ├── Cames (forme, taille) → L1870-1900 (camGeo, ExtrudeGeometry)
│   ├── Follower/T-bar → L1900-1920
│   ├── Couvercle (lid) → L1933-1940
│   ├── Manivelle → L1942-1950
│   ├── Engrenages → L1951-1995 (if gearRatio>1)
│   └── Labels came → L1920-1932
│
├── ANIMATION désync
│   ├── Figurine bouge pas/mal → L1612-1653 (FIGURINE ANIMATION)
│   ├── Mécanisme tourne pas → L1654-1700 (MECHANISM ANIMATION)
│   ├── Cames désync → L1659 (isCam rotation)
│   ├── Follower désync → L1662 (isFollower/isTbar)
│   └── realCamRadiusSTL() → L1253 (profil partagé)
│
├── STL EXPORT foireux
│   ├── Paramètres (base,lift,clamp) → L1290-1292
│   ├── Box → L1269-1273
│   ├── Shaft → L1274-1279
│   ├── Cams → L1281-1304
│   ├── Followers → L1307-1329
│   ├── T-bars → L1331-1349
│   ├── Top plate + slots → L1351-1368
│   ├── Bearings → L1370-1385
│   ├── Crank → L1387-1408
│   ├── Gears → L1410-1439
│   ├── Figurine pieces → L1441-1500
│   └── buildSTL() (binary writer) → L1238-1251
│
└── CSS/STYLE
    ├── Layout général → L1-136
    ├── .phase-row (boutons phase) → L100-110
    ├── .pivot-row (boutons pivot) → L100-110
    ├── @keyframes spin → L136
    └── @keyframes shake → L137
```

## PARAMÈTRES CRITIQUES (doivent être identiques partout)

| Param | Valeur | Fichiers |
|-------|--------|----------|
| base_radius_mm | 8 | realCamRadiusSTL L1254, doGenerate L1292, buildMechanism3D ~L1870, animate ~L1665 |
| ROTATE lift | 5 | doGenerate L1290, buildMechanism3D, animate |
| TRANSLATE factor | amp×0.5 | doGenerate L1290, buildMechanism3D, animate |
| Lift clamp | [4, 12] | doGenerate L1291, buildMechanism3D, animate |
| maxR | 8 + lift | doGenerate L1312/1335, buildMechanism3D ~L1905 |

## FLUX DE DONNÉES

```
User tape "un chat" 
  → matchTemplate() → figurine = {pieces:[...]}
  → matchMotions() → motions = {motions:[...], cam_count:N}
  → buildFigurine3D() → Three.js meshes
  → buildMechanism3D() → Three.js meshes (box,shaft,cams,etc)
  → animate() loop → bouge tout en sync

User clique "Générer STL"
  → doGenerate() → construit triangles
  → buildSTL() → binary STL blob
  → download
```

## VERSIONS

| Ver | Commit | Description |
|-----|--------|-------------|
| V7.2 | e992a2e | Per-cam speed |
| V7.3 | 166d487 | Sync figurine ↔ cam |
| V7.4 | 574b501 | Phase/Pivot séparés |
| V7.5 | 1abb69f | Follower sync realCamRadiusSTL |
| V7.6 | 28a6953 | selectPiece sync all controls |
| V7.7 | 5ceb87e | Dynamic lift figurine |
| V7.8 | 338a9bb | Template ours |
| V7.9 | a9315f8 | Remove implicit event (Firefox) |
| V7.10 | cbec0fa | setShape shake feedback |
| V7.11 | 57db189 | STL params = 3D preview |
| V7.12 | 00e184b | Gears dans STL |
| V7.13 | 490f29a | Couvercle preview 3D |
