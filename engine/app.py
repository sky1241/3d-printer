#!/usr/bin/env python3
"""
AUTOMATA WEB — Interface web du générateur d'automates mécaniques
UX: Design Tree (infernal-wheel/ux_resources)
Backend: automata_unified_v4.py (Briques A→G)
"""

import os, sys, json, time, tempfile, shutil, io, base64, zipfile
import numpy as np
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify, send_file

# Import automata engine
sys.path.insert(0, os.path.dirname(__file__))
from automata_unified_v4 import (
    CamSegment, CamProfile,
    AutomataGenerator, AutomataScene, Link, Joint,
    MotionPrimitive, MotionTrack, MotionLaw, MotionStyle,
    SCENE_PRESETS,
    InverseSolver,
)

app = Flask(__name__)

# ═══════════════════════════════════════
# HTML TEMPLATE — Single Page App
# ═══════════════════════════════════════

HTML = r'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🔩 Automata Generator</title>
<style>
/* ── DESIGN TOKENS (from Design Tree) ── */
:root {
  --sp-0: 0px; --sp-1: 4px; --sp-2: 8px; --sp-3: 12px;
  --sp-4: 16px; --sp-5: 24px; --sp-6: 32px; --sp-7: 48px;
  --radius-sm: 8px; --radius-md: 12px; --radius-lg: 16px;
  --surface-0: #0d1117; --surface-1: #161b22; --surface-2: #21262d;
  --surface-3: #30363d; --surface-hover: #2d333b;
  --text-primary: #e6edf3; --text-secondary: #8b949e; --text-muted: #6e7681;
  --accent: #58a6ff; --accent-hover: #79c0ff; --accent-glow: rgba(88,166,255,0.15);
  --success: #3fb950; --warning: #d29922; --error: #f85149;
  --transition-micro: 150ms ease; --transition-std: 250ms ease;
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.3); --shadow-md: 0 4px 12px rgba(0,0,0,0.4);
  --shadow-lg: 0 8px 24px rgba(0,0,0,0.5);
  --font: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* ── RESET ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { font-size: 16px; -webkit-font-smoothing: antialiased; }
body {
  font-family: var(--font); background: var(--surface-0); color: var(--text-primary);
  min-height: 100vh; line-height: 1.5;
}

/* ── LAYOUT ── */
.app { max-width: 960px; margin: 0 auto; padding: var(--sp-5); }
.header {
  text-align: center; padding: var(--sp-7) 0 var(--sp-6);
  border-bottom: 1px solid var(--surface-3); margin-bottom: var(--sp-6);
}
.header h1 { font-size: 2rem; font-weight: 700; letter-spacing: -0.02em; }
.header h1 span { color: var(--accent); }
.header p { color: var(--text-secondary); margin-top: var(--sp-2); font-size: 0.95rem; }

/* ── PROGRESS BAR (Wizard — DESIGN TREE Phase 9) ── */
.progress-bar {
  display: flex; gap: var(--sp-2); margin-bottom: var(--sp-6);
  padding: 0 var(--sp-4);
}
.progress-step {
  flex: 1; height: 4px; border-radius: 2px;
  background: var(--surface-3); transition: background var(--transition-std);
}
.progress-step.active { background: var(--accent); }
.progress-step.done { background: var(--success); }

.step-labels {
  display: flex; justify-content: space-between;
  margin-bottom: var(--sp-5); padding: 0 var(--sp-1);
}
.step-label {
  font-size: 0.75rem; color: var(--text-muted);
  transition: color var(--transition-micro);
}
.step-label.active { color: var(--accent); font-weight: 600; }
.step-label.done { color: var(--success); }

/* ── SECTIONS ── */
.section { display: none; animation: fadeIn 300ms ease; }
.section.active { display: block; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

.section-title {
  font-size: 1.25rem; font-weight: 600; margin-bottom: var(--sp-1);
}
.section-desc {
  color: var(--text-secondary); font-size: 0.9rem; margin-bottom: var(--sp-5);
}

/* ── CARD GRID (Touch targets 48px+ — DESIGN TREE Phase 3) ── */
.card-grid {
  display: grid; gap: var(--sp-3);
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
}
.card-grid.wide { grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); }

.card {
  background: var(--surface-1); border: 1px solid var(--surface-3);
  border-radius: var(--radius-md); padding: var(--sp-4) var(--sp-5);
  cursor: pointer; transition: all var(--transition-micro);
  min-height: 48px; display: flex; flex-direction: column; justify-content: center;
  position: relative; overflow: hidden;
}
.card:hover { border-color: var(--accent); background: var(--surface-hover);
  box-shadow: var(--shadow-sm); transform: translateY(-1px); }
.card.selected { border-color: var(--accent); background: var(--accent-glow);
  box-shadow: 0 0 0 2px var(--accent); }
.card .emoji { font-size: 1.5rem; margin-bottom: var(--sp-2); }
.card .card-title { font-weight: 600; font-size: 0.95rem; }
.card .card-desc { color: var(--text-secondary); font-size: 0.8rem; margin-top: var(--sp-1); }
.card .badge {
  position: absolute; top: var(--sp-2); right: var(--sp-2);
  background: var(--accent); color: var(--surface-0);
  font-size: 0.65rem; font-weight: 700; padding: 2px 6px;
  border-radius: 4px; text-transform: uppercase;
}

/* ── PRESET CARDS (compact) ── */
.preset-grid {
  display: grid; gap: var(--sp-2);
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
}
.preset-card {
  background: var(--surface-1); border: 1px solid var(--surface-3);
  border-radius: var(--radius-sm); padding: var(--sp-3) var(--sp-4);
  cursor: pointer; transition: all var(--transition-micro);
  text-align: center; min-height: 48px;
}
.preset-card:hover { border-color: var(--accent); background: var(--surface-hover); }
.preset-card.selected { border-color: var(--accent); background: var(--accent-glow); }
.preset-card .preset-emoji { font-size: 1.3rem; }
.preset-card .preset-name { font-size: 0.8rem; font-weight: 500; margin-top: var(--sp-1); }

/* ── SLIDERS & INPUTS ── */
.param-group { margin-bottom: var(--sp-4); }
.param-group label {
  display: block; font-size: 0.85rem; font-weight: 500;
  margin-bottom: var(--sp-1); color: var(--text-secondary);
}
.param-group .value-display {
  float: right; color: var(--accent); font-weight: 600; font-size: 0.85rem;
}
input[type="range"] {
  width: 100%; height: 6px; -webkit-appearance: none; appearance: none;
  background: var(--surface-3); border-radius: 3px; outline: none;
  cursor: pointer;
}
input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none; width: 20px; height: 20px;
  background: var(--accent); border-radius: 50%; cursor: pointer;
  box-shadow: var(--shadow-sm);
}
select, input[type="text"] {
  width: 100%; padding: var(--sp-2) var(--sp-3);
  background: var(--surface-2); border: 1px solid var(--surface-3);
  border-radius: var(--radius-sm); color: var(--text-primary);
  font-size: 0.9rem; outline: none; transition: border var(--transition-micro);
}
select:focus, input[type="text"]:focus { border-color: var(--accent); }

/* ── BUTTONS ── */
.btn-row { display: flex; gap: var(--sp-3); margin-top: var(--sp-6); }
.btn {
  padding: var(--sp-3) var(--sp-5); border: none; border-radius: var(--radius-sm);
  font-size: 0.9rem; font-weight: 600; cursor: pointer;
  transition: all var(--transition-micro); min-height: 44px;
  display: inline-flex; align-items: center; gap: var(--sp-2);
}
.btn-primary {
  background: var(--accent); color: var(--surface-0);
}
.btn-primary:hover { background: var(--accent-hover); transform: translateY(-1px); }
.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }
.btn-secondary {
  background: var(--surface-2); color: var(--text-primary);
  border: 1px solid var(--surface-3);
}
.btn-secondary:hover { background: var(--surface-3); }

/* ── CANVAS (Inverse Solver) ── */
.canvas-container {
  position: relative; background: var(--surface-1);
  border: 2px dashed var(--surface-3); border-radius: var(--radius-md);
  margin: var(--sp-4) 0; overflow: hidden;
}
.canvas-container canvas {
  display: block; width: 100%; cursor: crosshair;
}
.canvas-hint {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%);
  color: var(--text-muted); font-size: 0.9rem; pointer-events: none;
  transition: opacity var(--transition-micro);
}
.canvas-container.drawing .canvas-hint { opacity: 0; }

/* ── RESULTS ── */
.result-panel {
  background: var(--surface-1); border: 1px solid var(--surface-3);
  border-radius: var(--radius-md); padding: var(--sp-5);
  margin-top: var(--sp-5);
}
.result-panel h3 { font-size: 1.1rem; margin-bottom: var(--sp-3); }
.result-stat {
  display: flex; justify-content: space-between; padding: var(--sp-2) 0;
  border-bottom: 1px solid var(--surface-2); font-size: 0.9rem;
}
.result-stat:last-child { border: none; }
.result-stat .label { color: var(--text-secondary); }
.result-stat .val { font-weight: 600; }
.result-stat .val.good { color: var(--success); }
.result-stat .val.warn { color: var(--warning); }

/* ── LOADING (Design Tree: skeleton < 3s, progress > 3s) ── */
.loading-overlay {
  display: none; position: fixed; inset: 0; z-index: 100;
  background: rgba(13,17,23,0.85); backdrop-filter: blur(4px);
  flex-direction: column; align-items: center; justify-content: center;
}
.loading-overlay.active { display: flex; }
.spinner { width: 48px; height: 48px; border: 3px solid var(--surface-3);
  border-top-color: var(--accent); border-radius: 50%;
  animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { margin-top: var(--sp-4); color: var(--text-secondary); font-size: 0.9rem; }

/* ── TOAST (Design Tree: success = auto 4s, bottom) ── */
.toast {
  position: fixed; bottom: var(--sp-5); left: 50%; transform: translateX(-50%) translateY(100px);
  background: var(--surface-2); border: 1px solid var(--surface-3);
  padding: var(--sp-3) var(--sp-5); border-radius: var(--radius-sm);
  box-shadow: var(--shadow-lg); transition: transform 300ms ease; z-index: 200;
  font-size: 0.9rem;
}
.toast.show { transform: translateX(-50%) translateY(0); }
.toast.success { border-color: var(--success); }

/* ── TEXT INPUT MODE ── */
.text-input-area {
  width: 100%; min-height: 100px; padding: var(--sp-4);
  background: var(--surface-2); border: 1px solid var(--surface-3);
  border-radius: var(--radius-md); color: var(--text-primary);
  font-family: var(--font); font-size: 0.95rem; resize: vertical;
  outline: none; transition: border var(--transition-micro);
}
.text-input-area:focus { border-color: var(--accent); }
.text-input-area::placeholder { color: var(--text-muted); }

/* ── RESPONSIVE ── */
@media (max-width: 640px) {
  .app { padding: var(--sp-4); }
  .card-grid { grid-template-columns: 1fr; }
  .preset-grid { grid-template-columns: repeat(2, 1fr); }
  .btn-row { flex-direction: column; }
}
</style>
</head>
<body>

<div class="app">
  <!-- HEADER -->
  <div class="header">
    <h1>🔩 <span>Automata</span> Generator</h1>
    <p>Générateur d'automates mécaniques imprimables en 3D</p>
  </div>

  <!-- PROGRESS -->
  <div class="progress-bar" id="progressBar">
    <div class="progress-step active" data-step="0"></div>
    <div class="progress-step" data-step="1"></div>
    <div class="progress-step" data-step="2"></div>
    <div class="progress-step" data-step="3"></div>
  </div>
  <div class="step-labels">
    <span class="step-label active">Mode</span>
    <span class="step-label">Config</span>
    <span class="step-label">Paramètres</span>
    <span class="step-label">Générer</span>
  </div>

  <!-- STEP 0: MODE -->
  <div class="section active" id="step0">
    <div class="section-title">Comment créer ton automate ?</div>
    <div class="section-desc">Choisis un mode de création</div>
    <div class="card-grid">
      <div class="card" onclick="selectMode('preset')">
        <div class="emoji">🎭</div>
        <div class="card-title">Presets</div>
        <div class="card-desc">22 automates prêts à imprimer</div>
        <div class="badge">rapide</div>
      </div>
      <div class="card" onclick="selectMode('wizard')">
        <div class="emoji">🛠️</div>
        <div class="card-title">Wizard</div>
        <div class="card-desc">Configure axe par axe</div>
      </div>
      <div class="card" onclick="selectMode('text')">
        <div class="emoji">💬</div>
        <div class="card-title">Texte libre</div>
        <div class="card-desc">Décris en français, on génère</div>
      </div>
      <div class="card" onclick="selectMode('draw')">
        <div class="emoji">✏️</div>
        <div class="card-title">Dessiner</div>
        <div class="card-desc">Trace la trajectoire → solveur inverse</div>
        <div class="badge">IA</div>
      </div>
    </div>
  </div>

  <!-- STEP 1: CONFIG (depends on mode) -->
  <div class="section" id="step1">
    <!-- PRESET MODE -->
    <div id="presetMode" style="display:none">
      <div class="section-title">Choisis un automate</div>
      <div class="section-desc">Chaque preset est optimisé pour l'impression FDM</div>
      <div class="preset-grid" id="presetGrid"></div>
    </div>

    <!-- WIZARD MODE -->
    <div id="wizardMode" style="display:none">
      <div class="section-title">Combien d'axes de mouvement ?</div>
      <div class="section-desc">Chaque axe = 1 came sur l'arbre</div>
      <div class="card-grid">
        <div class="card" onclick="selectAxes(1)">
          <div class="emoji">↕️</div>
          <div class="card-title">1 axe</div>
          <div class="card-desc">Vertical ou horizontal — hochement, battement</div>
        </div>
        <div class="card" onclick="selectAxes(2)">
          <div class="emoji">↔️↕️</div>
          <div class="card-title">2 axes</div>
          <div class="card-desc">X + Y combinés — marche, nage, 8</div>
        </div>
        <div class="card" onclick="selectAxes(3)">
          <div class="emoji">🔄</div>
          <div class="card-title">3+ axes</div>
          <div class="card-desc">Multi-pièces — forgeron, batteur</div>
        </div>
      </div>
    </div>

    <!-- TEXT MODE -->
    <div id="textMode" style="display:none">
      <div class="section-title">Décris ton automate</div>
      <div class="section-desc">En français ou anglais — le parser comprend les mouvements</div>
      <textarea class="text-input-area" id="textInput"
        placeholder="Ex: un oiseau qui bat des ailes, hauteur 10mm, avec un châssis boîte"></textarea>
    </div>

    <!-- DRAW MODE -->
    <div id="drawMode" style="display:none">
      <div class="section-title">Dessine la trajectoire</div>
      <div class="section-desc">Le solveur inverse trouvera les cames optimales</div>
      <div class="canvas-container" id="canvasContainer">
        <canvas id="drawCanvas" width="600" height="400"></canvas>
        <div class="canvas-hint">Clique et dessine ici</div>
      </div>
      <div class="btn-row">
        <button class="btn btn-secondary" onclick="clearCanvas()">🗑️ Effacer</button>
      </div>
    </div>

    <div class="btn-row">
      <button class="btn btn-secondary" onclick="goStep(0)">← Retour</button>
      <button class="btn btn-primary" id="step1Next" onclick="step1Next()" disabled>
        Suivant →
      </button>
    </div>
  </div>

  <!-- STEP 2: PARAMS -->
  <div class="section" id="step2">
    <div class="section-title" id="step2Title">Paramètres</div>
    <div class="section-desc" id="step2Desc">Ajuste les dimensions et le comportement</div>

    <div id="wizardParams" style="display:none">
      <!-- Axes config (dynamique) -->
      <div id="axesConfig"></div>
    </div>

    <!-- Common params -->
    <div style="margin-top: var(--sp-5);">
      <div class="section-title" style="font-size:1rem; margin-bottom: var(--sp-3);">Châssis</div>

      <div class="card-grid" id="chassisGrid" style="margin-bottom: var(--sp-4);">
        <div class="card selected" data-chassis="box" onclick="selectChassis('box')">
          <div class="card-title">📦 Boîte</div>
          <div class="card-desc">Standard, fermé</div>
        </div>
        <div class="card" data-chassis="frame" onclick="selectChassis('frame')">
          <div class="card-title">🏗️ Cadre</div>
          <div class="card-desc">Ouvert, léger</div>
        </div>
        <div class="card" data-chassis="central" onclick="selectChassis('central')">
          <div class="card-title">🗼 Central</div>
          <div class="card-desc">Pilier unique</div>
        </div>
        <div class="card" data-chassis="flat" onclick="selectChassis('flat')">
          <div class="card-title">📋 Plat</div>
          <div class="card-desc">Base plate</div>
        </div>
      </div>

      <div class="param-group">
        <label>Largeur châssis <span class="value-display" id="widthVal">80mm</span></label>
        <input type="range" id="paramWidth" min="40" max="150" value="80"
          oninput="updateVal('widthVal', this.value+'mm')">
      </div>
      <div class="param-group">
        <label>Profondeur <span class="value-display" id="depthVal">60mm</span></label>
        <input type="range" id="paramDepth" min="30" max="120" value="60"
          oninput="updateVal('depthVal', this.value+'mm')">
      </div>
      <div class="param-group">
        <label>Hauteur totale <span class="value-display" id="heightVal">80mm</span></label>
        <input type="range" id="paramHeight" min="40" max="200" value="80"
          oninput="updateVal('heightVal', this.value+'mm')">
      </div>

      <div class="param-group">
        <label>Entraînement</label>
        <select id="paramDrive">
          <option value="motor">Moteur N20</option>
          <option value="crank">Manivelle</option>
        </select>
      </div>
    </div>

    <div class="btn-row">
      <button class="btn btn-secondary" onclick="goStep(1)">← Retour</button>
      <button class="btn btn-primary" onclick="goStep(3)">Générer 🚀</button>
    </div>
  </div>

  <!-- STEP 3: GENERATE -->
  <div class="section" id="step3">
    <div class="section-title">Génération</div>
    <div class="section-desc" id="genStatus">Prêt à générer</div>

    <div class="result-panel" id="resultPanel" style="display:none">
      <h3>✅ Automate généré</h3>
      <div id="resultStats"></div>
      <div class="btn-row" style="margin-top: var(--sp-4);">
        <button class="btn btn-primary" onclick="downloadResult()">📥 Télécharger ZIP</button>
        <button class="btn btn-secondary" onclick="goStep(0)">🔄 Nouveau</button>
      </div>
    </div>

    <div class="btn-row">
      <button class="btn btn-secondary" onclick="goStep(2)">← Retour</button>
      <button class="btn btn-primary" id="btnGenerate" onclick="generate()">
        ⚡ Lancer la génération
      </button>
    </div>
  </div>
</div>

<!-- LOADING OVERLAY -->
<div class="loading-overlay" id="loadingOverlay">
  <div class="spinner"></div>
  <div class="loading-text" id="loadingText">Génération en cours...</div>
</div>

<!-- TOAST -->
<div class="toast" id="toast"></div>

<script>
// ═══════════════════════════════════════
// STATE
// ═══════════════════════════════════════
const state = {
  mode: null,        // 'preset' | 'wizard' | 'text' | 'draw'
  preset: null,      // preset name
  axes: 0,           // 1, 2, 3
  chassis: 'box',
  drawPoints: [],
  step: 0,
  axisConfigs: [],   // [{type, amplitude, law}, ...]
};

const PRESETS = {{ presets_json|safe }};

const MOVEMENT_TYPES = [
  { id: 'nod',      emoji: '🔄', name: 'Hochement',    desc: 'Haut-bas vertical' },
  { id: 'wave',     emoji: '🌊', name: 'Vague',        desc: 'Oscillation douce' },
  { id: 'slide',    emoji: '↔️', name: 'Glissière',    desc: 'Translation horizontale' },
  { id: 'rotate',   emoji: '🔃', name: 'Rotation',     desc: 'Rotation partielle' },
  { id: 'flap',     emoji: '🦅', name: 'Battement',    desc: 'Ailes ou bras' },
  { id: 'strike',   emoji: '🔨', name: 'Frappe',       desc: 'Impact rapide + retour' },
  { id: 'geneva',   emoji: '⚙️', name: 'Genève',       desc: 'Pas à pas indexé' },
  { id: 'hold',     emoji: '⏸️', name: 'Maintien',     desc: 'Pause + mouvement' },
];

const LAWS = ['cycloidal', 'harmonic', 'poly_345', 'poly_4567'];

// ═══════════════════════════════════════
// NAVIGATION
// ═══════════════════════════════════════
function goStep(n) {
  state.step = n;
  document.querySelectorAll('.section').forEach((s,i) => {
    s.classList.toggle('active', i === n);
  });
  document.querySelectorAll('.progress-step').forEach((s,i) => {
    s.classList.toggle('active', i === n);
    s.classList.toggle('done', i < n);
  });
  document.querySelectorAll('.step-label').forEach((s,i) => {
    s.classList.toggle('active', i === n);
    s.classList.toggle('done', i < n);
  });
}

// ═══════════════════════════════════════
// STEP 0: MODE SELECT
// ═══════════════════════════════════════
function selectMode(mode) {
  state.mode = mode;
  // Highlight card
  document.querySelectorAll('#step0 .card').forEach(c => c.classList.remove('selected'));
  event.currentTarget.classList.add('selected');

  // Setup step 1 for this mode
  document.getElementById('presetMode').style.display = mode === 'preset' ? 'block' : 'none';
  document.getElementById('wizardMode').style.display = mode === 'wizard' ? 'block' : 'none';
  document.getElementById('textMode').style.display = mode === 'text' ? 'block' : 'none';
  document.getElementById('drawMode').style.display = mode === 'draw' ? 'block' : 'none';

  if (mode === 'preset') buildPresetGrid();
  if (mode === 'draw') initCanvas();
  if (mode === 'text') {
    document.getElementById('step1Next').disabled = false;
  }

  setTimeout(() => goStep(1), 200);
}

// ═══════════════════════════════════════
// PRESETS
// ═══════════════════════════════════════
function buildPresetGrid() {
  const grid = document.getElementById('presetGrid');
  const emojis = {
    nodding_bird:'🐦', flapping_bird:'🦅', walking_figure:'🚶', bobbing_duck:'🦆',
    rocking_horse:'🐴', pecking_chicken:'🐔', waving_cat:'🐱', drummer:'🥁',
    blacksmith:'⚒️', swimming_fish:'🐟', cat:'🐱', chicken:'🐔', duck:'🦆',
    fish:'🐟', horse:'🐴', rocker:'🪑', slider:'📏', striker:'🔨',
    turntable:'💿', multi_axis:'🔄', sequence:'📋', holder:'📌',
  };
  grid.innerHTML = PRESETS.map(p => `
    <div class="preset-card" onclick="selectPreset('${p}')" data-preset="${p}">
      <div class="preset-emoji">${emojis[p] || '🔩'}</div>
      <div class="preset-name">${p.replace(/_/g, ' ')}</div>
    </div>
  `).join('');
}

function selectPreset(name) {
  state.preset = name;
  document.querySelectorAll('.preset-card').forEach(c =>
    c.classList.toggle('selected', c.dataset.preset === name));
  document.getElementById('step1Next').disabled = false;
}

// ═══════════════════════════════════════
// WIZARD — AXES
// ═══════════════════════════════════════
function selectAxes(n) {
  state.axes = n;
  document.querySelectorAll('#wizardMode .card').forEach(c => c.classList.remove('selected'));
  event.currentTarget.classList.add('selected');
  document.getElementById('step1Next').disabled = false;
  buildAxisConfigs(n);
}

function buildAxisConfigs(n) {
  state.axisConfigs = [];
  const container = document.getElementById('axesConfig');
  const labels = ['Axe 1 (principal)', 'Axe 2 (secondaire)', 'Axe 3 (tertiaire)'];
  let html = '';
  for (let i = 0; i < n; i++) {
    state.axisConfigs.push({ type: 'nod', amplitude: 10, law: 'cycloidal' });
    html += `
    <div style="margin-bottom: var(--sp-5); padding: var(--sp-4);
      background: var(--surface-1); border-radius: var(--radius-md);
      border: 1px solid var(--surface-3);">
      <div style="font-weight:600; margin-bottom: var(--sp-3);">${labels[i]}</div>
      <div class="card-grid" style="margin-bottom: var(--sp-3);">
        ${MOVEMENT_TYPES.map(m => `
          <div class="card ${m.id==='nod'?'selected':''}" style="padding: var(--sp-2) var(--sp-3);"
            onclick="selectAxisType(${i}, '${m.id}', this)">
            <div style="font-size:1.1rem; text-align:center;">${m.emoji}</div>
            <div class="card-title" style="font-size:0.8rem; text-align:center;">${m.name}</div>
          </div>
        `).join('')}
      </div>
      <div class="param-group">
        <label>Amplitude <span class="value-display" id="amp${i}Val">10mm</span></label>
        <input type="range" min="2" max="25" value="10"
          oninput="state.axisConfigs[${i}].amplitude=+this.value; updateVal('amp${i}Val', this.value+'mm')">
      </div>
      <div class="param-group">
        <label>Loi de mouvement</label>
        <select onchange="state.axisConfigs[${i}].law=this.value">
          ${LAWS.map(l => `<option value="${l}">${l}</option>`).join('')}
        </select>
      </div>
    </div>`;
  }
  container.innerHTML = html;
  document.getElementById('wizardParams').style.display = 'block';
}

function selectAxisType(axisIdx, typeId, el) {
  state.axisConfigs[axisIdx].type = typeId;
  el.parentElement.querySelectorAll('.card').forEach(c => c.classList.remove('selected'));
  el.classList.add('selected');
}

// ═══════════════════════════════════════
// DRAW CANVAS
// ═══════════════════════════════════════
let isDrawing = false;
function initCanvas() {
  const canvas = document.getElementById('drawCanvas');
  const ctx = canvas.getContext('2d');
  const rect = canvas.parentElement.getBoundingClientRect();
  canvas.width = rect.width;
  canvas.height = 400;
  clearCanvas();

  canvas.onmousedown = canvas.ontouchstart = (e) => {
    isDrawing = true;
    state.drawPoints = [];
    document.getElementById('canvasContainer').classList.add('drawing');
    const p = getCanvasPoint(e, canvas);
    state.drawPoints.push(p);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawGrid(ctx, canvas);
    ctx.beginPath();
    ctx.moveTo(p[0], p[1]);
    ctx.strokeStyle = '#58a6ff';
    ctx.lineWidth = 3;
    ctx.lineCap = 'round';
  };

  canvas.onmousemove = canvas.ontouchmove = (e) => {
    if (!isDrawing) return;
    e.preventDefault();
    const p = getCanvasPoint(e, canvas);
    state.drawPoints.push(p);
    ctx.lineTo(p[0], p[1]);
    ctx.stroke();
  };

  canvas.onmouseup = canvas.ontouchend = () => {
    isDrawing = false;
    if (state.drawPoints.length > 5) {
      document.getElementById('step1Next').disabled = false;
    }
  };
}

function getCanvasPoint(e, canvas) {
  const rect = canvas.getBoundingClientRect();
  const ev = e.touches ? e.touches[0] : e;
  return [ev.clientX - rect.left, ev.clientY - rect.top];
}

function drawGrid(ctx, canvas) {
  ctx.strokeStyle = '#21262d';
  ctx.lineWidth = 1;
  for (let x = 0; x < canvas.width; x += 40) {
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
  }
  for (let y = 0; y < canvas.height; y += 40) {
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
  }
  // Center crosshair
  ctx.strokeStyle = '#30363d'; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(canvas.width/2, 0); ctx.lineTo(canvas.width/2, canvas.height); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(0, canvas.height/2); ctx.lineTo(canvas.width, canvas.height/2); ctx.stroke();
}

function clearCanvas() {
  state.drawPoints = [];
  const canvas = document.getElementById('drawCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawGrid(ctx, canvas);
  document.getElementById('canvasContainer').classList.remove('drawing');
  document.getElementById('step1Next').disabled = true;
}

// ═══════════════════════════════════════
// CHASSIS SELECT
// ═══════════════════════════════════════
function selectChassis(type) {
  state.chassis = type;
  document.querySelectorAll('#chassisGrid .card').forEach(c =>
    c.classList.toggle('selected', c.dataset.chassis === type));
}

// ═══════════════════════════════════════
// STEP TRANSITIONS
// ═══════════════════════════════════════
function step1Next() {
  if (state.mode === 'preset' || state.mode === 'text') {
    goStep(2);
  } else if (state.mode === 'wizard') {
    document.getElementById('step2Title').textContent = `${state.axes} axe(s) — Paramètres`;
    goStep(2);
  } else if (state.mode === 'draw') {
    goStep(2);
  }
}

function updateVal(id, val) {
  document.getElementById(id).textContent = val;
}

// ═══════════════════════════════════════
// GENERATE
// ═══════════════════════════════════════
async function generate() {
  showLoading('Génération en cours...');

  const payload = {
    mode: state.mode,
    preset: state.preset,
    axes: state.axes,
    axis_configs: state.axisConfigs,
    text: state.mode === 'text' ? document.getElementById('textInput').value : '',
    draw_points: state.drawPoints,
    chassis: state.chassis,
    width: +document.getElementById('paramWidth').value,
    depth: +document.getElementById('paramDepth').value,
    height: +document.getElementById('paramHeight').value,
    drive: document.getElementById('paramDrive').value,
  };

  try {
    const resp = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await resp.json();
    hideLoading();

    if (data.success) {
      showResult(data);
      toast('✅ Automate généré avec succès !', 'success');
    } else {
      toast('❌ ' + (data.error || 'Erreur inconnue'));
    }
  } catch (err) {
    hideLoading();
    toast('❌ Erreur réseau: ' + err.message);
  }
}

function showResult(data) {
  document.getElementById('resultPanel').style.display = 'block';
  document.getElementById('btnGenerate').style.display = 'none';
  const stats = document.getElementById('resultStats');
  stats.innerHTML = `
    <div class="result-stat"><span class="label">Pièces STL</span><span class="val good">${data.n_stl}</span></div>
    <div class="result-stat"><span class="label">Taille ZIP</span><span class="val">${data.zip_size_kb} KB</span></div>
    <div class="result-stat"><span class="label">Cames</span><span class="val">${data.n_cams || '?'}</span></div>
    <div class="result-stat"><span class="label">Châssis</span><span class="val">${data.chassis_type}</span></div>
    <div class="result-stat"><span class="label">Mode</span><span class="val">${data.mode}</span></div>
    ${data.solver_rms ? `<div class="result-stat"><span class="label">Solveur RMS</span><span class="val ${data.solver_rms < 1 ? 'good' : 'warn'}">${data.solver_rms.toFixed(2)} mm</span></div>` : ''}
  `;
  window._lastZipId = data.zip_id;
}

function downloadResult() {
  if (window._lastZipId) {
    window.location.href = '/api/download/' + window._lastZipId;
  }
}

// ═══════════════════════════════════════
// UI HELPERS
// ═══════════════════════════════════════
function showLoading(text) {
  document.getElementById('loadingText').textContent = text;
  document.getElementById('loadingOverlay').classList.add('active');
}
function hideLoading() {
  document.getElementById('loadingOverlay').classList.remove('active');
}
function toast(msg, type) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'toast show' + (type === 'success' ? ' success' : '');
  setTimeout(() => t.classList.remove('show'), 4000);
}
</script>
</body>
</html>
'''

# ═══════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════

# Temp storage for generated zips
_zip_store = {}

@app.route('/')
def index():
    presets = list(SCENE_PRESETS.keys())
    return render_template_string(HTML, presets_json=json.dumps(presets))


@app.route('/api/generate', methods=['POST'])
def api_generate():
    try:
        data = request.json
        mode = data.get('mode', 'preset')
        t0 = time.time()

        scene = None
        solver_rms = None

        if mode == 'preset':
            preset_name = data.get('preset', 'nodding_bird')
            if preset_name in SCENE_PRESETS:
                scene = SCENE_PRESETS[preset_name]()
            else:
                return jsonify(success=False, error=f"Preset '{preset_name}' inconnu")

        elif mode == 'text':
            text = data.get('text', '').strip().lower()
            if not text:
                return jsonify(success=False, error="Texte vide")
            # Simple keyword matching to find best preset
            best, best_score = 'nodding_bird', 0
            keywords = {
                'nodding_bird': ['oiseau', 'hoche', 'nod', 'bird', 'tête'],
                'flapping_bird': ['bat', 'aile', 'flap', 'wing', 'vol'],
                'walking_figure': ['march', 'walk', 'jambe', 'leg', 'figure'],
                'bobbing_duck': ['canard', 'duck', 'bob'],
                'rocking_horse': ['cheval', 'horse', 'bascule', 'rock'],
                'pecking_chicken': ['poule', 'chicken', 'picore', 'peck'],
                'waving_cat': ['chat', 'cat', 'wave', 'patte'],
                'drummer': ['tambour', 'drum', 'baguette'],
                'blacksmith': ['forgeron', 'forge', 'marteau', 'blacksmith', 'anvil'],
                'swimming_fish': ['poisson', 'fish', 'nage', 'swim'],
                'slider': ['glisse', 'slide', 'horizontal'],
                'turntable': ['tourne', 'rotate', 'plateau', 'turn'],
            }
            for preset, kws in keywords.items():
                score = sum(1 for kw in kws if kw in text)
                if score > best_score:
                    best, best_score = preset, score
            scene = SCENE_PRESETS[best]()

        elif mode == 'wizard':
            # Build scene from axis configs
            axis_configs = data.get('axis_configs', [])
            tracks = []
            for i, ac in enumerate(axis_configs):
                amplitude = ac.get('amplitude', 10)
                law_str = ac.get('law', 'cycloidal')
                law_map = {
                    'cycloidal': MotionLaw.CYCLOIDAL,
                    'harmonic': MotionLaw.SIMPLE_HARMONIC,
                    'poly_345': MotionLaw.POLY_345,
                    'poly_4567': MotionLaw.POLY_4567,
                }
                law = law_map.get(law_str, MotionLaw.CYCLOIDAL)

                tracks.append(MotionTrack(
                    name=f"axis_{i}",
                    joint_type='revolute',
                    axis='x' if i % 2 == 0 else 'y',
                    primitives=[
                        MotionPrimitive(kind='rise', amplitude=amplitude, beta=120, law=law),
                        MotionPrimitive(kind='dwell', amplitude=0, beta=60, law=law),
                        MotionPrimitive(kind='return', amplitude=amplitude, beta=120, law=law),
                        MotionPrimitive(kind='dwell', amplitude=0, beta=60, law=law),
                    ],
                ))

            link = Link(name='body', length=60, width=30, thickness=15, mass_grams=15)
            joint = Joint(name='joint_0', joint_type='revolute', axis=(1,0,0),
                         position=(0,30,40), parent_link='body', child_link='head')

            scene = AutomataScene(
                name='Custom Wizard',
                description=f'{len(tracks)} axe(s) configuré(s)',
                links=[link],
                joints=[joint],
                tracks=tracks,
            )

        elif mode == 'draw':
            # Inverse solver
            points = data.get('draw_points', [])
            if len(points) < 10:
                return jsonify(success=False, error="Pas assez de points (min 10)")

            solver = InverseSolver(verbose=False)
            canvas_w = 600
            canvas_h = 400
            solution = solver.from_canvas(
                points, canvas_w, canvas_h,
                real_width_mm=50, real_height_mm=35,
                max_cams=2, timeout_s=20,
            )
            solver_rms = solution.error_rms_mm

            # Build scene from solver result
            tracks = []
            for i, cam in enumerate(solution.cams):
                law_map = {
                    'cycloidal': MotionLaw.CYCLOIDAL,
                    'harmonic': MotionLaw.SIMPLE_HARMONIC,
                    'poly_345': MotionLaw.POLY_345,
                    'poly_4567': MotionLaw.POLY_4567,
                }
                prims = []
                for s in cam.segments:
                    prims.append(MotionPrimitive(
                        kind=s.seg_type,
                        amplitude=s.height,
                        beta=s.beta_deg,
                        law=law_map.get(s.law, MotionLaw.CYCLOIDAL),
                    ))
                tracks.append(MotionTrack(
                    name=f"inv_axis_{i}",
                    joint_type='revolute',
                    axis='x' if i == 0 else 'y',
                    primitives=prims,
                ))

            link = Link(name='body', length=60, width=30, thickness=15, mass_grams=15)
            joint = Joint(name='joint_0', joint_type='revolute', axis=(1,0,0),
                         position=(0,30,40), parent_link='body', child_link='head')

            scene = AutomataScene(
                name='Inverse Solver',
                description=f'{solution.n_cams} came(s), RMS={solver_rms:.2f}mm',
                links=[link],
                joints=[joint],
                tracks=tracks,
            )

        if scene is None:
            return jsonify(success=False, error="Impossible de créer la scène")

        # Generate
        gen = AutomataGenerator(scene, seed=42)
        gen.generate()

        # Export to ZIP in memory
        tmpdir = tempfile.mkdtemp()
        try:
            gen.export(tmpdir)
            stl_files = list(Path(tmpdir).glob('**/*.stl'))

            buf = io.BytesIO()
            with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
                for f in Path(tmpdir).rglob('*'):
                    if f.is_file():
                        zf.write(f, f.relative_to(tmpdir))
            buf.seek(0)
            zip_bytes = buf.read()

            zip_id = f"gen_{int(time.time())}"
            _zip_store[zip_id] = zip_bytes

            return jsonify(
                success=True,
                n_stl=len(stl_files),
                zip_size_kb=round(len(zip_bytes) / 1024),
                n_cams=len(scene.tracks),
                chassis_type=data.get('chassis', 'box'),
                mode=mode,
                solver_rms=solver_rms,
                zip_id=zip_id,
                time_s=round(time.time() - t0, 2),
            )
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify(success=False, error=str(e))


@app.route('/api/download/<zip_id>')
def api_download(zip_id):
    if zip_id not in _zip_store:
        return "Not found", 404
    buf = io.BytesIO(_zip_store[zip_id])
    return send_file(buf, mimetype='application/zip',
                     as_attachment=True, download_name=f'automata_{zip_id}.zip')


# ═══════════════════════════════════════
# MAIN
# ═══════════════════════════════════════
if __name__ == '__main__':
    port = 8013
    print(f"\n🔩 Automata Web — http://localhost:{port}")
    print(f"   Briques A→G loaded")
    print(f"   {len(SCENE_PRESETS)} presets")
    app.run(host='0.0.0.0', port=port, debug=False)
