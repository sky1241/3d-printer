#!/usr/bin/env python3
"""
Automata Generator — Web UI
Port 8013 | Brique F2 (visual builder)
UX rules from DESIGN_TREE.md
"""
from flask import Flask, request, jsonify, Response
import sys, os, io, json, time, tempfile, zipfile

sys.path.insert(0, '/home/claude/merge_work')

app = Flask(__name__)

# Pre-import engine at startup
import patched as engine
print(f"  Engine loaded: {len(engine.SCENE_PRESETS)} presets")

@app.route('/')
def index():
    return HTML_PAGE

@app.route('/api/presets')
def api_presets():
    try:
        # engine already imported globally
        presets = list(engine.SCENE_PRESETS.keys())
        return jsonify({'presets': presets})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def api_generate():
    try:
        # engine already imported globally
        data = request.json
        mode = data.get('mode', 'preset')
        if mode == 'preset':
            scene = engine.SCENE_PRESETS[data.get('preset', 'nodding_bird')]()
        elif mode == 'text':
            cfg = engine.parse_text_to_figurine_config(data.get('text', '')); scene = engine.SceneBuilder.from_figurine(cfg)
        elif mode == 'custom':
            text = f"{data.get('body','bird')} {data.get('movement','wave')} height {data.get('height',15)}mm {data.get('chassis','box')} chassis"
            cfg = engine.parse_text_to_figurine_config(text); scene = engine.SceneBuilder.from_figurine(cfg)
        else:
            return jsonify({'error': f'Unknown mode: {mode}'}), 400
        gen = engine.AutomataGenerator(scene, seed=data.get('seed', 42))
        gen.generate()
        tmpdir = tempfile.mkdtemp()
        gen.export(tmpdir)
        all_files = os.listdir(tmpdir)
        stl_files = [f for f in all_files if f.endswith('.stl')]
        total_kb = sum(os.path.getsize(os.path.join(tmpdir, f)) for f in stl_files) // 1024
        import shutil; shutil.rmtree(tmpdir, ignore_errors=True)
        return jsonify({'success': True, 'parts': len(stl_files), 'size_kb': total_kb, 'files': stl_files})
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

@app.route('/api/download', methods=['POST'])
def api_download():
    try:
        # engine already imported globally
        data = request.json
        mode = data.get('mode', 'preset')
        if mode == 'preset':
            scene = engine.SCENE_PRESETS[data.get('preset', 'nodding_bird')]()
        elif mode == 'text':
            cfg = engine.parse_text_to_figurine_config(data.get('text', '')); scene = engine.SceneBuilder.from_figurine(cfg)
        elif mode == 'custom':
            text = f"{data.get('body','bird')} {data.get('movement','wave')} height {data.get('height',15)}mm {data.get('chassis','box')} chassis"
            cfg = engine.parse_text_to_figurine_config(text); scene = engine.SceneBuilder.from_figurine(cfg)
        else:
            return jsonify({'error': f'Unknown mode'}), 400
        gen = engine.AutomataGenerator(scene, seed=data.get('seed', 42))
        gen.generate()
        tmpdir = tempfile.mkdtemp()
        gen.export(tmpdir)
        stl_files = [f for f in os.listdir(tmpdir) if f.endswith('.stl')]
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            for f in stl_files: zf.write(os.path.join(tmpdir, f), f)
        import shutil; shutil.rmtree(tmpdir, ignore_errors=True)
        zip_buf.seek(0)
        name = data.get('preset', 'custom')
        return Response(zip_buf.getvalue(), mimetype='application/zip',
                       headers={'Content-Disposition': f'attachment; filename=automata_{name}.zip'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inverse', methods=['POST'])
def api_inverse():
    try:
        # engine already imported globally
        data = request.json
        points = data.get('points', [])
        if len(points) < 4:
            return jsonify({'error': 'Min 4 points'}), 400
        solver = engine.InverseSolver(verbose=False)
        sol = solver.from_canvas(points, data.get('canvas_width', 400), data.get('canvas_height', 400),
                                 real_width_mm=50, real_height_mm=50, max_cams=2, timeout_s=20)
        return jsonify({
            'success': True, 'n_cams': sol.n_cams,
            'error_rms': round(sol.error_rms_mm, 3), 'error_max': round(sol.error_max_mm, 3),
            'cams': [{'axis': sol.axis_mapping[i], 'phase': round(c.phase_offset_deg, 1),
                      'segments': [{'type': s.seg_type, 'beta': round(s.beta_deg, 1),
                                    'height': round(s.height, 1), 'law': s.law} for s in c.segments]}
                     for i, c in enumerate(sol.cams)],
            'simulated': sol.simulated.tolist(),
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


HTML_PAGE = r"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Automata Generator</title>
<style>
:root {
    --sp-1:4px; --sp-2:8px; --sp-3:12px; --sp-4:16px; --sp-5:24px; --sp-6:32px; --sp-7:48px;
    --bg:#0a0a0f; --sf:#141420; --sf2:#1e1e2e; --sf3:#2a2a3e;
    --pr:#6c5ce7; --pr-h:#7c6df7; --ac:#00cec9; --ac2:#fd79a8;
    --tx:#e8e8f0; --tx-m:#9090a8; --ok:#00b894; --err:#e17055; --bd:#2d2d44;
    --r-sm:8px; --r-md:12px; --r-lg:16px;
    --sh:0 4px 16px rgba(0,0,0,.4);
    --font:'Segoe UI',system-ui,-apple-system,sans-serif;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:var(--font);background:var(--bg);color:var(--tx);line-height:1.5;font-size:16px;min-height:100vh}
.app{max-width:1100px;margin:0 auto;padding:var(--sp-5) var(--sp-4)}
header{text-align:center;padding:var(--sp-7) 0 var(--sp-6)}
header h1{font-size:2.2rem;font-weight:700;background:linear-gradient(135deg,var(--pr),var(--ac));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:var(--sp-2)}
header p{color:var(--tx-m);font-size:1.05rem}

.tabs{display:flex;gap:var(--sp-1);background:var(--sf);border-radius:var(--r-lg);padding:var(--sp-1);margin-bottom:var(--sp-6)}
.tab{flex:1;padding:var(--sp-3) var(--sp-4);border:none;background:0;color:var(--tx-m);font-size:.95rem;font-weight:500;border-radius:var(--r-md);cursor:pointer;transition:all .15s;min-height:44px;font-family:var(--font)}
.tab:hover{color:var(--tx);background:var(--sf2)}
.tab.active{background:var(--pr);color:#fff;box-shadow:var(--sh)}

.panel{display:none}.panel.active{display:block;animation:fadeIn .3s ease-out}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}

.section{background:var(--sf);border-radius:var(--r-lg);padding:var(--sp-5);margin-bottom:var(--sp-5);border:1px solid var(--bd)}
.section-title{font-size:.8rem;text-transform:uppercase;letter-spacing:.1em;color:var(--tx-m);margin-bottom:var(--sp-4);font-weight:600}

.option-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:var(--sp-3)}
.option-btn{display:flex;flex-direction:column;align-items:center;gap:var(--sp-2);padding:var(--sp-4) var(--sp-3);background:var(--sf2);border:2px solid transparent;border-radius:var(--r-md);color:var(--tx);cursor:pointer;transition:all .15s;min-height:48px;font-family:var(--font);font-size:.9rem}
.option-btn:hover{background:var(--sf3);border-color:var(--pr);transform:translateY(-2px)}
.option-btn.selected{background:rgba(108,92,231,.15);border-color:var(--pr);box-shadow:0 0 0 1px var(--pr)}
.option-btn .icon{font-size:1.8rem;line-height:1}
.option-btn .label{font-weight:500;font-size:.85rem}

.preset-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(155px,1fr));gap:var(--sp-3)}
.preset-card{padding:var(--sp-4);background:var(--sf2);border:2px solid transparent;border-radius:var(--r-md);cursor:pointer;transition:all .15s;text-align:center;min-height:48px;font-family:var(--font)}
.preset-card:hover{border-color:var(--ac);transform:translateY(-2px);box-shadow:var(--sh)}
.preset-card.selected{background:rgba(0,206,201,.12);border-color:var(--ac)}
.preset-card .emoji{font-size:2rem;margin-bottom:var(--sp-2)}
.preset-card .name{font-weight:600;font-size:.9rem}
.preset-card .desc{font-size:.75rem;color:var(--tx-m);margin-top:var(--sp-1)}

.text-input{width:100%;padding:var(--sp-4);background:var(--sf2);border:2px solid var(--bd);border-radius:var(--r-md);color:var(--tx);font-size:1rem;font-family:var(--font);resize:vertical;min-height:80px;transition:border-color .15s}
.text-input:focus{outline:none;border-color:var(--pr);box-shadow:0 0 0 3px rgba(108,92,231,.2)}
.text-input::placeholder{color:var(--tx-m)}

.canvas-wrap{position:relative;background:var(--sf2);border-radius:var(--r-md);border:2px solid var(--bd);overflow:hidden}
#drawCanvas{display:block;width:100%;height:400px;cursor:crosshair}
.canvas-toolbar{display:flex;gap:var(--sp-2);padding:var(--sp-3);background:var(--sf3)}

.btn{display:inline-flex;align-items:center;justify-content:center;gap:var(--sp-2);padding:var(--sp-3) var(--sp-5);border:none;border-radius:var(--r-md);font-size:.95rem;font-weight:600;cursor:pointer;transition:all .15s;min-height:48px;font-family:var(--font)}
.btn-primary{background:var(--pr);color:#fff}.btn-primary:hover{background:var(--pr-h);transform:translateY(-1px)}
.btn-accent{background:var(--ac);color:#000}.btn-accent:hover{filter:brightness(1.1)}
.btn-ghost{background:0;color:var(--tx-m);border:1px solid var(--bd)}.btn-ghost:hover{color:var(--tx);border-color:var(--tx-m)}
.btn-block{width:100%}
.btn:disabled{opacity:.5;cursor:not-allowed;transform:none!important}

.action-bar{display:flex;gap:var(--sp-3);margin-top:var(--sp-5)}

.result{background:var(--sf);border:1px solid var(--ok);border-radius:var(--r-lg);padding:var(--sp-5);margin-top:var(--sp-5);animation:fadeIn .3s}
.result h3{color:var(--ok);margin-bottom:var(--sp-3)}.result .stat{color:var(--tx-m);margin-bottom:var(--sp-2)}
.result-error{border-color:var(--err)}.result-error h3{color:var(--err)}

.loading{display:none;padding:var(--sp-6);text-align:center}.loading.visible{display:block}
.spinner{width:40px;height:40px;border:3px solid var(--sf3);border-top-color:var(--pr);border-radius:50%;animation:spin .8s linear infinite;margin:0 auto var(--sp-4)}
@keyframes spin{to{transform:rotate(360deg)}}

.slider-group{margin-bottom:var(--sp-4)}
.slider-group label{display:flex;justify-content:space-between;margin-bottom:var(--sp-2);font-size:.85rem;color:var(--tx-m)}
.slider-group label span:last-child{color:var(--ac);font-weight:600}
input[type=range]{width:100%;height:6px;-webkit-appearance:none;background:var(--sf3);border-radius:3px;outline:none}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:20px;height:20px;border-radius:50%;background:var(--pr);cursor:pointer}

.toast{position:fixed;bottom:var(--sp-5);left:50%;transform:translateX(-50%) translateY(100px);background:var(--ok);color:#000;padding:var(--sp-3) var(--sp-5);border-radius:var(--r-md);font-weight:600;box-shadow:0 8px 32px rgba(0,0,0,.5);transition:transform .3s ease-out;z-index:1000}
.toast.show{transform:translateX(-50%) translateY(0)}
.cam-result{margin-top:var(--sp-3);padding:var(--sp-3);background:var(--sf3);border-radius:var(--r-sm);font-family:monospace;font-size:.85rem;line-height:1.6}

@media(max-width:768px){
    .option-grid,.preset-grid{grid-template-columns:repeat(2,1fr)}
    header h1{font-size:1.6rem}.action-bar{flex-direction:column}
}
</style>
</head>
<body>
<div class="app">
    <header>
        <h1>&#9881; Automata Generator</h1>
        <p>Automate mecanique 100% imprimable en 3D</p>
    </header>

    <div class="tabs">
        <button class="tab active" onclick="switchTab('visual',this)">&#127912; Builder</button>
        <button class="tab" onclick="switchTab('presets',this)">&#128230; Presets</button>
        <button class="tab" onclick="switchTab('draw',this)">&#9999; Dessiner</button>
    </div>

    <!-- VISUAL BUILDER -->
    <div id="panel-visual" class="panel active">
        <div class="section">
            <div class="section-title">1. Type de mouvement</div>
            <div class="option-grid" id="movement-grid">
                <button class="option-btn selected" data-val="wave" onclick="sel('movement',this)"><span class="icon">&#8597;</span><span class="label">Vertical</span></button>
                <button class="option-btn" data-val="slide" onclick="sel('movement',this)"><span class="icon">&#8596;</span><span class="label">Horizontal</span></button>
                <button class="option-btn" data-val="rotate" onclick="sel('movement',this)"><span class="icon">&#128260;</span><span class="label">Rotation</span></button>
                <button class="option-btn" data-val="geneva" onclick="sel('movement',this)"><span class="icon">&#9201;</span><span class="label">Geneva</span></button>
                <button class="option-btn" data-val="sequence" onclick="sel('movement',this)"><span class="icon">&#127925;</span><span class="label">Sequence</span></button>
                <button class="option-btn" data-val="multi" onclick="sel('movement',this)"><span class="icon">&#127917;</span><span class="label">Multi-axes</span></button>
            </div>
        </div>
        <div class="section">
            <div class="section-title">2. Personnage</div>
            <div class="option-grid" id="body-grid">
                <button class="option-btn selected" data-val="bird" onclick="sel('body',this)"><span class="icon">&#128038;</span><span class="label">Oiseau</span></button>
                <button class="option-btn" data-val="human" onclick="sel('body',this)"><span class="icon">&#129489;</span><span class="label">Humanoide</span></button>
                <button class="option-btn" data-val="fish" onclick="sel('body',this)"><span class="icon">&#128031;</span><span class="label">Poisson</span></button>
                <button class="option-btn" data-val="cat" onclick="sel('body',this)"><span class="icon">&#128049;</span><span class="label">Chat</span></button>
                <button class="option-btn" data-val="horse" onclick="sel('body',this)"><span class="icon">&#128052;</span><span class="label">Cheval</span></button>
                <button class="option-btn" data-val="duck" onclick="sel('body',this)"><span class="icon">&#129414;</span><span class="label">Canard</span></button>
            </div>
        </div>
        <div class="section">
            <div class="section-title">3. Chassis</div>
            <div class="option-grid" id="chassis-grid">
                <button class="option-btn selected" data-val="box" onclick="sel('chassis',this)"><span class="icon">&#128230;</span><span class="label">Boite</span></button>
                <button class="option-btn" data-val="frame" onclick="sel('chassis',this)"><span class="icon">&#127959;</span><span class="label">Cadre</span></button>
                <button class="option-btn" data-val="central" onclick="sel('chassis',this)"><span class="icon">&#128508;</span><span class="label">Pilier</span></button>
                <button class="option-btn" data-val="flat" onclick="sel('chassis',this)"><span class="icon">&#128208;</span><span class="label">Plat</span></button>
            </div>
        </div>
        <div class="section">
            <div class="section-title">4. Amplitude</div>
            <div class="slider-group">
                <label>Hauteur <span id="hv">15 mm</span></label>
                <input type="range" id="hs" min="3" max="25" value="15" oninput="document.getElementById('hv').textContent=this.value+' mm'">
            </div>
        </div>
        <div class="action-bar">
            <button class="btn btn-primary btn-block" onclick="genCustom()">&#9881; Generer l'automate</button>
        </div>
    </div>

    <!-- PRESETS -->
    <div id="panel-presets" class="panel">
        <div class="section">
            <div class="section-title">Choisis un preset</div>
            <div class="preset-grid" id="preset-grid"></div>
        </div>
        <div class="action-bar">
            <button class="btn btn-accent btn-block" onclick="genPreset()">&#128230; Generer le preset</button>
        </div>
    </div>

    <!-- DRAW -->
    <div id="panel-draw" class="panel">
        <div class="section">
            <div class="section-title">Dessine la trajectoire</div>
            <div class="canvas-wrap">
                <canvas id="drawCanvas" width="800" height="400"></canvas>
                <div class="canvas-toolbar">
                    <button class="btn btn-ghost" onclick="clearC()">&#128465; Effacer</button>
                    <button class="btn btn-ghost" onclick="undoC()">&#8617; Undo</button>
                    <button class="btn btn-primary" onclick="solveInv()" id="btn-solve">&#129504; Resoudre</button>
                </div>
            </div>
            <div id="inv-result"></div>
        </div>
    </div>

    <div class="loading" id="ld"><div class="spinner"></div><p id="ld-t">Generation...</p></div>
    <div id="res"></div>
</div>
<div class="toast" id="toast"></div>

<script>
const S={movement:'wave',body:'bird',chassis:'box',preset:'nodding_bird'};
function switchTab(n,b){document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));b.classList.add('active');document.getElementById('panel-'+n).classList.add('active');if(n==='presets')loadP();if(n==='draw')initC()}
function sel(g,b){b.closest('.option-grid').querySelectorAll('.option-btn').forEach(x=>x.classList.remove('selected'));b.classList.add('selected');S[g]=b.dataset.val}

const PM={nodding_bird:{e:'&#128038;',n:'Oiseau hocheur',d:'Tete qui hoche'},flapping_bird:{e:'&#129413;',n:'Oiseau battant',d:'Ailes qui battent'},walking_figure:{e:'&#128694;',n:'Marcheur',d:'Jambes articulees'},bobbing_duck:{e:'&#129414;',n:'Canard',d:'Bob haut-bas'},rocking_horse:{e:'&#128052;',n:'Cheval bascule',d:'Balance'},pecking_chicken:{e:'&#128020;',n:'Poule',d:'Picore'},waving_cat:{e:'&#128049;',n:'Chat',d:'Patte qui salue'},drummer:{e:'&#129345;',n:'Batteur',d:'Tambour'},blacksmith:{e:'&#9874;',n:'Forgeron',d:'Marteau'},swimming_fish:{e:'&#128031;',n:'Poisson',d:'Queue ondule'},cat:{e:'&#128570;',n:'Chat coucou',d:'Apparait'},chicken:{e:'&#128037;',n:'Poussin',d:'Picore'},duck:{e:'&#129414;',n:'Canard simple',d:'Basique'},fish:{e:'&#128032;',n:'Poisson tropical',d:'Nage'},horse:{e:'&#127943;',n:'Cheval',d:'Galop'},rocker:{e:'&#129681;',n:'Bascule',d:'Pendule'},slider:{e:'&#10145;',n:'Glisseur',d:'Translation'},striker:{e:'&#128296;',n:'Frappeur',d:'Impact'},turntable:{e:'&#128191;',n:'Platine',d:'Rotation'},holder:{e:'&#9995;',n:'Mainteneur',d:'Pause'},multi_axis:{e:'&#127917;',n:'Multi-axes',d:'Complexe'},sequence:{e:'&#127926;',n:'Sequence',d:'Multi'}};
function loadP(){const g=document.getElementById('preset-grid');if(g.children.length>0)return;fetch('/api/presets').then(r=>r.json()).then(d=>{d.presets.forEach(n=>{const m=PM[n]||{e:'&#9881;',n:n,d:''};const c=document.createElement('button');c.className='preset-card'+(n===S.preset?' selected':'');c.innerHTML='<div class="emoji">'+m.e+'</div><div class="name">'+m.n+'</div><div class="desc">'+m.d+'</div>';c.onclick=()=>{g.querySelectorAll('.preset-card').forEach(x=>x.classList.remove('selected'));c.classList.add('selected');S.preset=n};g.appendChild(c)})})}

function showL(m){document.getElementById('ld').classList.add('visible');document.getElementById('ld-t').textContent=m||'Generation...';document.getElementById('res').innerHTML=''}
function hideL(){document.getElementById('ld').classList.remove('visible')}
function toast(m){const t=document.getElementById('toast');t.textContent=m;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),4000)}

let lastCfg={};
function showRes(d){hideL();const a=document.getElementById('res');if(d.error){a.innerHTML='<div class="result result-error"><h3>&#10060; Erreur</h3><p class="stat">'+d.error+'</p></div>';return}a.innerHTML='<div class="result"><h3>&#9989; Automate genere !</h3><p class="stat">&#128230; '+d.parts+' pieces STL &mdash; '+d.size_kb+' KB</p><p class="stat">&#128196; '+d.files.join(', ')+'</p><div class="action-bar" style="margin-top:16px"><button class="btn btn-accent btn-block" onclick="dlRes()">&#11015; Telecharger ZIP</button></div></div>';toast('Automate pret !')}

function genCustom(){const c={mode:'custom',movement:S.movement,body:S.body,chassis:S.chassis,height:parseInt(document.getElementById('hs').value)};lastCfg=c;showL('Construction...');fetch('/api/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(c)}).then(r=>r.json()).then(showRes).catch(e=>showRes({error:e.message}))}
function genPreset(){const c={mode:'preset',preset:S.preset};lastCfg=c;showL('Generation '+S.preset+'...');fetch('/api/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(c)}).then(r=>r.json()).then(showRes).catch(e=>showRes({error:e.message}))}
function dlRes(){showL('ZIP...');fetch('/api/download',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(lastCfg)}).then(r=>r.blob()).then(b=>{hideL();const u=URL.createObjectURL(b);const a=document.createElement('a');a.href=u;a.download='automata.zip';a.click();URL.revokeObjectURL(u);toast('ZIP telecharge !')}).catch(e=>showRes({error:e.message}))}

// CANVAS
let cv,cx,drawing=false,strokes=[],cur=[];
function initC(){cv=document.getElementById('drawCanvas');cx=cv.getContext('2d');const r=cv.getBoundingClientRect();cv.width=r.width*devicePixelRatio;cv.height=r.height*devicePixelRatio;cx.scale(devicePixelRatio,devicePixelRatio);drawG();cv.onpointerdown=e=>{drawing=true;cur=[];const r=cv.getBoundingClientRect();cur.push([e.clientX-r.left,e.clientY-r.top])};cv.onpointermove=e=>{if(!drawing)return;const r=cv.getBoundingClientRect();cur.push([e.clientX-r.left,e.clientY-r.top]);redraw();cx.strokeStyle='#6c5ce7';cx.lineWidth=3;cx.lineJoin='round';cx.lineCap='round';cx.beginPath();cur.forEach((p,i)=>{if(i===0)cx.moveTo(p[0],p[1]);else cx.lineTo(p[0],p[1])});cx.stroke()};cv.onpointerup=()=>{if(cur.length>1)strokes.push([...cur]);drawing=false;cur=[];redraw()}}
function drawG(){if(!cx)return;const w=cv.width/devicePixelRatio,h=cv.height/devicePixelRatio;cx.fillStyle='#1e1e2e';cx.fillRect(0,0,w,h);cx.strokeStyle='#2a2a3e';cx.lineWidth=1;for(let x=0;x<w;x+=20){cx.beginPath();cx.moveTo(x,0);cx.lineTo(x,h);cx.stroke()}for(let y=0;y<h;y+=20){cx.beginPath();cx.moveTo(0,y);cx.lineTo(w,y);cx.stroke()}cx.strokeStyle='#3a3a5e';cx.setLineDash([5,5]);cx.beginPath();cx.moveTo(w/2,0);cx.lineTo(w/2,h);cx.stroke();cx.beginPath();cx.moveTo(0,h/2);cx.lineTo(w,h/2);cx.stroke();cx.setLineDash([])}
function redraw(){drawG();strokes.forEach(s=>{cx.strokeStyle='#00cec9';cx.lineWidth=3;cx.lineJoin='round';cx.lineCap='round';cx.beginPath();s.forEach((p,i)=>{if(i===0)cx.moveTo(p[0],p[1]);else cx.lineTo(p[0],p[1])});cx.stroke()})}
function clearC(){strokes=[];cur=[];redraw();document.getElementById('inv-result').innerHTML=''}
function undoC(){strokes.pop();redraw()}
function solveInv(){const pts=strokes.flat();if(pts.length<4){toast('Dessine au moins 4 points !');return}const b=document.getElementById('btn-solve');b.disabled=true;b.textContent='Calcul...';const r=cv.getBoundingClientRect();fetch('/api/inverse',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({points:pts,canvas_width:r.width,canvas_height:r.height})}).then(r=>r.json()).then(d=>{b.disabled=false;b.innerHTML='&#129504; Resoudre';const a=document.getElementById('inv-result');if(d.error){a.innerHTML='<div class="result result-error"><h3>&#10060;</h3><p>'+d.error+'</p></div>';return}let h=d.cams.map((c,i)=>'<div>Cam '+i+' ['+c.axis+'] phase='+c.phase+'&deg; : '+c.segments.map(s=>s.type+'('+s.beta+'&deg;, '+s.height+'mm, '+s.law+')').join(' &rarr; ')+'</div>').join('');a.innerHTML='<div class="result"><h3>&#129504; '+d.n_cams+' came(s)</h3><p class="stat">RMS: '+d.error_rms+'mm | Max: '+d.error_max+'mm</p><div class="cam-result">'+h+'</div></div>';if(d.simulated){const w=r.width,ht=r.height;cx.strokeStyle='#fd79a8';cx.lineWidth=2;cx.setLineDash([6,4]);cx.beginPath();d.simulated.forEach((p,i)=>{const sx=w/2+p[0]*(w/50),sy=ht/2-p[1]*(ht/50);if(i===0)cx.moveTo(sx,sy);else cx.lineTo(sx,sy)});cx.closePath();cx.stroke();cx.setLineDash([])}toast('Cames calculees !')}).catch(e=>{b.disabled=false;b.innerHTML='&#129504; Resoudre';toast('Erreur: '+e.message)})}
</script>
</body>
</html>
"""

if __name__ == '__main__':
    print("\n  AUTOMATA GENERATOR — http://localhost:8013\n")
    app.run(host='0.0.0.0', port=8013, debug=False, threaded=True)
