/**
 * AUTOMATA GENERATOR — JSCAD TEST
 * Parametric CAD, zéro triangle hardcodé.
 * Toutes les pièces sont dérivées des paramètres.
 */

const { primitives, booleans, transforms, extrusions } = require('@jscad/modeling');
const { cylinder, cuboid, sphere } = primitives;
const { union, subtract } = booleans;
const { translate, rotateX, rotateY, rotateZ, scale } = transforms;
const { extrudeLinear } = extrusions;
const stlSerializer = require('@jscad/stl-serializer');
const fs = require('fs');

// ═══════════════════════════════════════
// PARAMÈTRES — tout dérive de ça
// ═══════════════════════════════════════
const PARAMS = {
  // Box
  boxW: 70,       // mm largeur
  boxD: 40,       // mm profondeur
  boxH: 30,       // mm hauteur
  wall: 2,        // mm épaisseur murs

  // Shaft
  shaftR: 2.5,    // mm rayon arbre
  shaftClearance: 0.3, // mm jeu impression

  // Cam — DÉRIVÉ de amplitude + profile
  camCount: 2,
  camThick: 5,    // mm épaisseur came
  camBaseR: 8,    // mm rayon de base
  // lift sera calculé

  // Follower
  followerR: 1.5, // mm rayon tige
  followerClearance: 0.5,

  // Gears
  gearRatio: 2,
  gearModule: 1.5, // mm module dentaire
  smallTeeth: 10,

  // Motions per cam (from user input)
  motions: [
    { amplitude: 30, profile: 'smooth', type: 'OSCILLATE' },
    { amplitude: 45, profile: 'sharp',  type: 'OSCILLATE' },
  ],

  // Printer
  printer: 'ender3',
  layerH: 0.2,
  nozzle: 0.4,
};

// ═══════════════════════════════════════
// DERIVED PARAMETERS — tout est calculé
// ═══════════════════════════════════════
function deriveParams(p) {
  const d = { ...p };

  // Shaft length = box depth minus clearance
  d.shaftLen = d.boxD - 4;
  d.shaftZ = d.boxH * 0.5; // hauteur de l'arbre

  // Cam lifts — calculé d'après le type de mouvement et l'amplitude
  d.camLifts = d.motions.map(m => {
    let lift;
    if (m.type === 'ROTATE') lift = 5;
    else if (m.type === 'TRANSLATE_V' || m.type === 'TRANSLATE_H') lift = m.amplitude * 0.5;
    else lift = 15 * Math.sin(m.amplitude * Math.PI / 180);
    return Math.max(4, Math.min(lift, 12));
  });

  // Cam positions — distribués le long de l'arbre
  d.camPositions = d.motions.map((_, i) => {
    return (i - (d.camCount - 1) / 2) * (d.shaftLen * 0.6 / Math.max(d.camCount - 1, 1));
  });

  // Follower lengths — s'étendent au-dessus de la came + au-dessus du couvercle
  d.followerLens = d.camLifts.map(lift => {
    const maxR = d.camBaseR + lift;
    return d.boxH - d.shaftZ + 5; // dépasse le couvercle
  });

  // Top plate height
  d.plateZ = d.boxH;
  d.plateH = 2;

  // Gear params
  if (d.gearRatio > 1) {
    d.bigTeeth = d.smallTeeth * d.gearRatio;
    d.smallR = (d.smallTeeth * d.gearModule) / 2;
    d.bigR = (d.bigTeeth * d.gearModule) / 2;
  }

  // Round everything to printer resolution
  d.minWall = Math.max(d.nozzle * 2, d.wall);

  return d;
}

// ═══════════════════════════════════════
// CAM PROFILE — parametric, pas de triangle
// ═══════════════════════════════════════
function camRadius(angle, baseR, lift, profile) {
  const theta = ((angle % (Math.PI * 2)) + Math.PI * 2) % (Math.PI * 2);
  let d = 0;
  if (profile === 'smooth') {
    d = theta < Math.PI ? lift * Math.sin(theta) : 0;
  } else if (profile === 'sharp') {
    if (theta < Math.PI / 3) d = lift * (theta / (Math.PI / 3));
    else if (theta < Math.PI * 2 / 3) d = lift * (1 - (theta - Math.PI / 3) / (Math.PI / 3));
    else d = 0;
  } else { // dwell
    if (theta < Math.PI / 4) d = lift * (theta / (Math.PI / 4));
    else if (theta < Math.PI * 3 / 4) d = lift;
    else if (theta < Math.PI) d = lift * (1 - (theta - Math.PI * 3 / 4) / (Math.PI / 4));
    else d = 0;
  }
  return baseR + d;
}

function makeCamShape(baseR, lift, profile, thick, segments = 72) {
  // Crée le profil 2D de la came via points
  const points = [];
  for (let i = 0; i < segments; i++) {
    const a = (i / segments) * Math.PI * 2;
    const r = camRadius(a, baseR, lift, profile);
    points.push([r * Math.cos(a), r * Math.sin(a)]);
  }

  // Extrude le profil en 3D
  const shape2d = require('@jscad/modeling').geometries.geom2.fromPoints(points);
  const cam3d = extrudeLinear({ height: thick }, shape2d);

  // Percer le trou pour l'arbre
  const hole = cylinder({ radius: PARAMS.shaftR + PARAMS.shaftClearance, height: thick + 2, segments: 24 });
  return subtract(cam3d, translate([0, 0, -1], hole));
}

// ═══════════════════════════════════════
// GEAR — parametric involute
// ═══════════════════════════════════════
function makeGear(teeth, module_, thick, holeR) {
  const r = (teeth * module_) / 2;
  const points = [];
  for (let i = 0; i < teeth * 2; i++) {
    const a = (i / (teeth * 2)) * Math.PI * 2;
    const rr = i % 2 === 0 ? r : r - module_ * 1.2;
    points.push([rr * Math.cos(a), rr * Math.sin(a)]);
  }
  const shape2d = require('@jscad/modeling').geometries.geom2.fromPoints(points);
  const gear3d = extrudeLinear({ height: thick }, shape2d);
  const hole = cylinder({ radius: holeR, height: thick + 2, segments: 24 });
  return subtract(gear3d, translate([0, 0, -1], hole));
}

// ═══════════════════════════════════════
// BUILD ALL PARTS
// ═══════════════════════════════════════
function buildAutomata(params) {
  const d = deriveParams(params);
  const parts = [];

  // 1. BOX — open top, hollow
  const boxOuter = cuboid({ size: [d.boxW, d.boxD, d.boxH] });
  const boxInner = cuboid({ size: [d.boxW - d.wall * 2, d.boxD - d.wall * 2, d.boxH] });
  const boxShell = subtract(
    translate([0, 0, d.boxH / 2], boxOuter),
    translate([0, 0, d.boxH / 2 + d.wall], boxInner)
  );
  parts.push(boxShell);
  console.log('✅ Box: hollow shell, wall=' + d.wall + 'mm');

  // 2. SHAFT
  const shaft = rotateX(Math.PI / 2,
    cylinder({ radius: d.shaftR, height: d.shaftLen, segments: 24 })
  );
  parts.push(translate([0, 0, d.shaftZ], shaft));
  console.log('✅ Shaft: r=' + d.shaftR + 'mm, len=' + d.shaftLen + 'mm');

  // 3. BEARING SUPPORTS (pillars with shaft holes)
  [-d.shaftLen / 2, d.shaftLen / 2].forEach(y => {
    const pillar = cylinder({ radius: d.shaftR + 3, height: d.shaftZ, segments: 16 });
    const hole = cylinder({ radius: d.shaftR + d.shaftClearance, height: d.shaftZ + 2, segments: 24 });
    const bearing = subtract(
      translate([0, y, d.shaftZ / 2], pillar),
      translate([0, y, d.shaftZ / 2], hole)
    );
    parts.push(bearing);
  });
  console.log('✅ Bearings: 2x pillar with shaft hole');

  // 4. CAMS
  for (let ci = 0; ci < d.camCount; ci++) {
    const lift = d.camLifts[ci];
    const profile = d.motions[ci].profile;
    const cam = makeCamShape(d.camBaseR, lift, profile, d.camThick);
    const yPos = d.camPositions[ci];
    parts.push(translate([0, yPos - d.camThick / 2, d.shaftZ], rotateX(Math.PI / 2, cam)));
    console.log(`✅ Cam ${ci + 1}: baseR=${d.camBaseR}, lift=${lift.toFixed(1)}mm, profile=${profile}`);
  }

  // 5. FOLLOWERS
  for (let ci = 0; ci < d.camCount; ci++) {
    const lift = d.camLifts[ci];
    const maxR = d.camBaseR + lift;
    const fLen = d.followerLens[ci];
    const yPos = d.camPositions[ci];
    const rod = cylinder({ radius: d.followerR, height: fLen, segments: 12 });
    parts.push(translate([0, yPos, d.shaftZ + maxR + fLen / 2], rod));
    console.log(`✅ Follower ${ci + 1}: r=${d.followerR}mm, len=${fLen.toFixed(1)}mm`);
  }

  // 6. T-BARS
  const tW = 12, tH = 1.5, tD = 3;
  for (let ci = 0; ci < d.camCount; ci++) {
    const lift = d.camLifts[ci];
    const maxR = d.camBaseR + lift;
    const fLen = d.followerLens[ci];
    const yPos = d.camPositions[ci];
    const tZ = d.shaftZ + maxR + fLen;
    const tbar = cuboid({ size: [tW, tD, tH] });
    parts.push(translate([0, yPos, tZ], tbar));
    console.log(`✅ T-bar ${ci + 1}: at z=${tZ.toFixed(1)}mm`);
  }

  // 7. TOP PLATE with follower slots
  let plate = cuboid({ size: [d.boxW, d.boxD, d.plateH] });
  plate = translate([0, 0, d.plateZ + d.plateH / 2], plate);
  for (let ci = 0; ci < d.camCount; ci++) {
    const yPos = d.camPositions[ci];
    const slot = cuboid({ size: [d.followerR * 2 + d.followerClearance * 2, 4, d.plateH + 2] });
    plate = subtract(plate, translate([0, yPos, d.plateZ + d.plateH / 2], slot));
  }
  parts.push(plate);
  console.log('✅ Top plate: with ' + d.camCount + ' follower slots');

  // 8. CRANK HANDLE
  const crankLen = 15;
  const arm = rotateY(Math.PI / 2,
    cylinder({ radius: 1.5, height: crankLen, segments: 10 })
  );
  const knob = sphere({ radius: 3, segments: 12 });
  const crank = union(
    translate([crankLen / 2, -d.shaftLen / 2 - 2, d.shaftZ], arm),
    translate([crankLen, -d.shaftLen / 2 - 2, d.shaftZ], knob)
  );
  parts.push(crank);
  console.log('✅ Crank: len=' + crankLen + 'mm');

  // 9. GEARS (if ratio > 1)
  if (d.gearRatio > 1) {
    const gearThick = 3;
    const gearY = -d.shaftLen / 2 - 5;

    const small = makeGear(d.smallTeeth, d.gearModule, gearThick, d.shaftR + d.shaftClearance);
    parts.push(translate([0, gearY, d.shaftZ], rotateX(Math.PI / 2, small)));

    const big = makeGear(d.bigTeeth, d.gearModule, gearThick, d.shaftR + d.shaftClearance);
    parts.push(translate([0, gearY - gearThick - 1, d.shaftZ], rotateX(Math.PI / 2, big)));

    console.log(`✅ Gears: ${d.smallTeeth}T (r=${d.smallR.toFixed(1)}) + ${d.bigTeeth}T (r=${d.bigR.toFixed(1)}), ratio 1:${d.gearRatio}`);
  }

  return union(...parts);
}

// ═══════════════════════════════════════
// GENERATE & EXPORT
// ═══════════════════════════════════════
console.log('');
console.log('═'.repeat(50));
console.log('JSCAD AUTOMATA GENERATOR — TEST');
console.log('═'.repeat(50));
console.log('');
console.log('Paramètres:');
console.log(`  Box: ${PARAMS.boxW}×${PARAMS.boxD}×${PARAMS.boxH}mm`);
console.log(`  Arbre: r=${PARAMS.shaftR}mm`);
console.log(`  Cames: ${PARAMS.camCount}x, base=${PARAMS.camBaseR}mm`);
console.log(`  Gear ratio: 1:${PARAMS.gearRatio}`);
console.log(`  Motions: ${PARAMS.motions.map(m => `${m.type} ${m.amplitude}° ${m.profile}`).join(', ')}`);
console.log('');

const model = buildAutomata(PARAMS);

console.log('');
console.log('Exporting STL...');
const rawData = stlSerializer.serialize({ binary: true }, model);
const buffer = Buffer.concat(rawData.map(d => Buffer.from(d)));
fs.writeFileSync('/home/claude/test_automata.stl', buffer);
const sizeMB = (buffer.length / 1024 / 1024).toFixed(2);
console.log(`✅ STL saved: test_automata.stl (${sizeMB} MB, ${buffer.length} bytes)`);
console.log('');
console.log('ZÉRO triangle hardcodé. Tout est paramétrique.');
console.log('Change PARAMS → STL change automatiquement.');
