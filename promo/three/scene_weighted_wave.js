// scene_weighted_wave.js — SMART LOOKUP · PART II · "THE WEIGHTED WAVE"
// 16:9 master (also lays itself out 9:16 for the teaser). 95.0 s at 60 fps.
//
// Every wave on screen is computed from weighted_wave_math.mjs, the same module
// weighted_wave_check.mjs verifies: theta, psi, the gradient steps, the peaks.
// Bloom is driven by |psi|: line brightness is a function of local amplitude,
// and the bloom pass only catches what is bright, so glow appears exactly where
// the superposition is strong and nowhere it is near zero.
import { Line2 } from 'three/addons/lines/Line2.js';
import { LineGeometry } from 'three/addons/lines/LineGeometry.js';
import { LineSegments2 } from 'three/addons/lines/LineSegments2.js';
import { LineSegmentsGeometry } from 'three/addons/lines/LineSegmentsGeometry.js';
import { LineMaterial } from 'three/addons/lines/LineMaterial.js';
import * as M from './weighted_wave_math.mjs';

export const FPS = 60;
export const DURATION = 95.0;

// palette (Part I continuity + the three new colours)
const BG = 0x05070f, CURVE = 0x2ee6c8, TARGET = 0xff8a2b, VOCAB = 0x3b6fd4, WEIGHT = 0x9b5cf6,
      GOLD = 0xffd166, NEG = 0x6e4a9c, WHITE = 0xeaf2ff;
const CSS = { ink: '#EAF2FF', gold: '#FFD166', curve: '#2EE6C8', weight: '#9B5CF6', dim: '#8A94A6' };

// beats (seconds)
const B = { slam: [0.15, 5.6], theta: 6, bars: 12, waves: 20, sup: 28, interf: 35, wrap: 44, land: 52,
            problem: 59, train: 66, bloom: 73, burst: 75.0, reveal: 80, tease: 86, card: [90.5, 93.3], seam: [93.3, 95.0] };
const PULSE = 0.4;                                     // the 8 training pulses, 0.4 s apart

const clamp01 = (x) => Math.min(1, Math.max(0, x));
const ease = (x) => { x = clamp01(x); return x * x * (3 - 2 * x); };
const easeOut = (x) => 1 - (1 - clamp01(x)) ** 3;
const easeExp = (x) => { x = clamp01(x); return x < 0.5 ? 0.5 * (2 ** (20 * x - 10)) : 1 - 0.5 * (2 ** (-20 * x + 10)); };
const lerp = (a, b, k) => a + (b - a) * k;
const win = (t, a, b, fi = 0.4, fo = 0.4) => ease((t - a) / fi) * ease((b - t) / fo);

// ---------------------------------------------------------------- assets
const SVGS = ['eq_psi', 'eq_update', ...Array.from({ length: 32 }, (_, k) => `th_${k + 1}`)];
async function loadSvgs() {
  const out = {};
  for (const name of SVGS) {
    const img = new Image(); img.src = `/tex/${name}.svg`; await img.decode();
    const pt = name.startsWith('th_') ? 9 : 7;           // pixels per TeX point
    const cv = document.createElement('canvas'); cv.width = Math.ceil(img.width * pt / 1.333); cv.height = Math.ceil(img.height * pt / 1.333);
    cv.getContext('2d').drawImage(img, 0, 0, cv.width, cv.height);
    out[name] = cv;
  }
  return out;
}

function textCanvas(str, o = {}) {
  const size = o.size || 64, weight = o.weight || '700', spacing = o.spacing || 0, color = o.color || CSS.ink, SS = 2;
  const c = document.createElement('canvas').getContext('2d');
  c.font = `${weight} ${size * SS}px "DejaVu Sans", sans-serif`;
  const chars = [...str]; const widths = chars.map((ch) => c.measureText(ch).width / SS);
  const w = Math.ceil(widths.reduce((a, b) => a + b, 0) + spacing * (chars.length - 1)) + size, h = Math.ceil(size * 1.6);
  const cv = document.createElement('canvas'); cv.width = w * SS; cv.height = h * SS;
  const g = cv.getContext('2d'); g.scale(SS, SS); g.font = `${weight} ${size}px "DejaVu Sans", sans-serif`;
  g.fillStyle = color; g.textBaseline = 'middle'; let x = size / 2;
  if (o.glow) { g.shadowColor = o.glow; g.shadowBlur = size * 0.35; }
  chars.forEach((ch, i) => { g.fillText(ch, x, h / 2); x += widths[i] + spacing; });
  return cv;
}

export async function buildAsync(THREE, W, H) {
  const tex = await loadSvgs();
  return build(THREE, W, H, tex);
}

export function build(THREE, W, H, svg) {
  const A = THREE.AdditiveBlending;
  const PORTRAIT = H > W;
  const scene = new THREE.Scene(); scene.background = new THREE.Color(BG);
  scene.fog = new THREE.FogExp2(BG, 0.018);
  const camera = new THREE.PerspectiveCamera(PORTRAIT ? 52 : 35, W / H, 0.01, 400);
  const DIST = PORTRAIT ? 1.75 : 1.0;                    // the teaser backs off so the same shot fits the tall frame
  const HW = PORTRAIT ? 540 : 960, HH = PORTRAIT ? 960 : 540;
  const hud = new THREE.Scene(); const hudCam = new THREE.OrthographicCamera(-HW, HW, HH, -HH, -10, 10);
  scene.add(new THREE.AmbientLight(0x404a6a, 0.6));
  const key = new THREE.DirectionalLight(0xffffff, 1.4); key.position.set(3, 8, 6); key.castShadow = true;
  key.shadow.mapSize.set(1024, 1024); key.shadow.camera.near = 0.5; key.shadow.camera.far = 40;
  scene.add(key); scene.add(key.target);

  // ------------------------------------------------------------ the math
  const WORDS = M.buildWords();
  const water = WORDS[M.WATER];
  const X = (u) => u;                                    // curve parameter as a fraction of a lap
  const euler = (u) => { const t = 2 * Math.PI * u, r = Math.exp(Math.cos(t));
    return new THREE.Vector3(2 * r * Math.cos(t), 2 * r * Math.sin(t), 2 * 1.3 * Math.sin(2 * t)); };
  const CC = (() => { const v = new THREE.Vector3(); for (let j = 0; j < 400; j++) v.add(euler(j / 400)); return v.multiplyScalar(1 / 400); })();
  const outward = (u) => { const p = euler(u); const n = new THREE.Vector3(p.x - CC.x, p.y - CC.y, 0).normalize(); n.z = 0.28; return n.normalize(); };
  // display sign: theta and -theta put the peak in the same place; show the peak pointing outward
  const signed = (th, xt) => (M.psi(th, xt) < 0 ? th.map((a) => -a) : th);
  const thW0 = signed(water.hist[0], water.xt), thW8 = signed(water.hist[M.STEPS], water.xt);
  const maxAbs = (arr) => Math.max(...arr.map(Math.abs));

  // ------------------------------------------------------------ helpers
  const sprite = (() => { const cv = document.createElement('canvas'); cv.width = cv.height = 128; const g = cv.getContext('2d');
    const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(255,255,255,1)');
    gr.addColorStop(0.3, 'rgba(255,255,255,0.55)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, 128, 128);
    return new THREE.CanvasTexture(cv); })();
  // the bloom gradient from the brief: near-white core, gold at 60%, turquoise at the edge
  const haloTex = (() => { const cv = document.createElement('canvas'); cv.width = cv.height = 256; const g = cv.getContext('2d');
    const gr = g.createRadialGradient(128, 128, 0, 128, 128, 128);
    gr.addColorStop(0, 'rgba(234,242,255,1)'); gr.addColorStop(0.6, 'rgba(255,209,102,0.55)'); gr.addColorStop(1, 'rgba(46,230,200,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 256, 256); return new THREE.CanvasTexture(cv); })();
  function fatLine(n, width, opts = {}) {
    const g = new LineGeometry(); const z = new Float32Array(n * 3); g.setPositions(z); g.setColors(z);
    const m = new LineMaterial({ color: 0xffffff, linewidth: width, vertexColors: true, transparent: true, blending: A, depthWrite: false, opacity: 1, ...opts });
    m.resolution.set(W, H);
    const l = new Line2(g, m); l.frustumCulled = false; l.userData = { n, pos: new Float32Array(n * 3), col: new Float32Array(n * 3) }; scene.add(l); return l;
  }
  function setLine(l, fnPos, fnCol) {
    const { n, pos, col } = l.userData;
    for (let j = 0; j < n; j++) { const u = j / (n - 1); const p = fnPos(u, j); pos[3 * j] = p.x; pos[3 * j + 1] = p.y; pos[3 * j + 2] = p.z;
      const c = fnCol(u, j); col[3 * j] = c.r; col[3 * j + 1] = c.g; col[3 * j + 2] = c.b; }
    l.geometry.setPositions(pos); l.geometry.setColors(col);
  }
  const C = (hex) => new THREE.Color(hex);
  const cVocab = C(VOCAB), cGold = C(GOLD), cWhite = C(WHITE), cCurve = C(CURVE), cWeight = C(WEIGHT), cNeg = C(NEG), cTarget = C(TARGET), cTmp = new THREE.Color();
  const bright = (base, a) => {                                 // amplitude -> colour: dim where |psi| is small, white-hot at the peak
    cTmp.copy(base).multiplyScalar(0.18 + 0.82 * a * a);
    if (a > 0.82) cTmp.lerp(cWhite, (a - 0.82) / 0.18 * 0.9);
    return cTmp;
  };

  // ------------------------------------------------------------ Part I's world: curve + 2,144 points
  const curvePts = Array.from({ length: 600 }, (_, j) => euler(j / 600));
  const curveTube = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(curvePts, true), 900, 0.022, 8, true),
    new THREE.MeshBasicMaterial({ color: CURVE, transparent: true, opacity: 0.55, blending: A, depthWrite: false }));
  scene.add(curveTube);
  const pts = new THREE.Points(new THREE.BufferGeometry(), new THREE.PointsMaterial({ size: 0.075, map: sprite, color: VOCAB,
    transparent: true, depthWrite: false, blending: A }));
  pts.geometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(Array.from({ length: M.N_POINTS }, (_, j) => euler(j / M.N_POINTS).toArray()).flat()), 3));
  scene.add(pts);
  const waterPts = new THREE.Points(new THREE.BufferGeometry(), new THREE.PointsMaterial({ size: 0.16, map: sprite, color: TARGET,
    transparent: true, depthWrite: false, blending: A }));
  waterPts.geometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(Array.from({ length: 32 }, (_, j) => euler(j / M.N_POINTS).toArray()).flat()), 3));
  scene.add(waterPts);
  const PW = euler(water.xt);                                   // WATER on the curve

  // ------------------------------------------------------------ theta, in 3D
  const thetaGroup = new THREE.Group(); scene.add(thetaGroup);
  const thMat = new THREE.MeshStandardMaterial({ color: WEIGHT, emissive: WEIGHT, emissiveIntensity: 0.55, metalness: 0.3, roughness: 0.35, transparent: true });
  const ring = new THREE.Mesh(new THREE.TorusGeometry(0.5, 0.075, 24, 96), thMat); ring.scale.set(0.72, 1, 1); ring.castShadow = true;
  const bar = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.74, 24), thMat); bar.rotation.z = Math.PI / 2; bar.castShadow = true;
  thetaGroup.add(ring, bar);
  const floor = new THREE.Mesh(new THREE.CircleGeometry(1.6, 64), new THREE.ShadowMaterial({ opacity: 0.45, transparent: true }));
  floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; scene.add(floor);
  const thetaGlow = new THREE.Sprite(new THREE.SpriteMaterial({ map: sprite, color: WEIGHT, transparent: true, blending: A, depthWrite: false }));
  scene.add(thetaGlow);

  // ------------------------------------------------------------ the stage (decomposition, waves, interference)
  const ST = new THREE.Vector3(CC.x, CC.y, 0);
  const SW = 11;                                                  // stage width
  const stageX = (u) => ST.x - SW / 2 + SW * u;
  const mxW0 = maxAbs(thW0);
  const BAR_SCALE = 2.4 / mxW0, ROW_SCALE = 0.30 / mxW0, ROW_GAP = 0.215;
  const rowY = (k) => ST.y + 2.75 - k * 0.19;                  // k = 0..31
  const barX = (k) => ST.x - 5.0 + 10.0 * (k + 0.5) / 32;
  const bars = Array.from({ length: 32 }, (_, k) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(0.2, 1, 0.12),
      new THREE.MeshStandardMaterial({ color: WEIGHT, emissive: WEIGHT, emissiveIntensity: 0.6, transparent: true }));
    scene.add(m); return m; });
  const barLbl = Array.from({ length: 32 }, (_, k) => {
    const cv = svg[`th_${k + 1}`]; const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace;
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: t, transparent: true, depthWrite: false }));
    const h = 0.17; sp.scale.set(h * cv.width / cv.height, h, 1); scene.add(sp); return sp; });
  const N_W = 220;
  const comps = Array.from({ length: 32 }, () => fatLine(N_W, 1.6));
  const sumLine = fatLine(420, 4.2);
  const psiW0 = Array.from({ length: 420 }, (_, j) => M.psi(thW0, j / 419));
  const mxPsi0 = maxAbs(psiW0);
  const SUM_SCALE = 1.7 / mxPsi0;
  const ia = fatLine(420, 3.0), ib = fatLine(420, 3.0), isum = fatLine(420, 4.4);
  const interfGlow = new THREE.Sprite(new THREE.SpriteMaterial({ map: haloTex, transparent: true, blending: A, depthWrite: false }));
  scene.add(interfGlow);

  // ------------------------------------------------------------ wrapped wave + the 67 words
  const wrapLine = fatLine(900, 3.6);
  const peakDot = new THREE.Sprite(new THREE.SpriteMaterial({ map: sprite, color: TARGET, transparent: true, blending: A, depthWrite: false }));
  scene.add(peakDot);
  const spikeGeo = new LineSegmentsGeometry(); spikeGeo.setPositions(new Float32Array(67 * 6)); spikeGeo.setColors(new Float32Array(67 * 6));
  const spikeMat = new LineMaterial({ color: 0xffffff, linewidth: 3.2, vertexColors: true, transparent: true, blending: A, depthWrite: false });
  spikeMat.resolution.set(W, H);
  const spikes = new LineSegments2(spikeGeo, spikeMat); spikes.frustumCulled = false; scene.add(spikes);
  const wordDots = new THREE.Points(new THREE.BufferGeometry(), new THREE.PointsMaterial({ size: 0.15, map: sprite, vertexColors: true, transparent: true, depthWrite: false, blending: A }));
  wordDots.geometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(67 * 3), 3));
  wordDots.geometry.setAttribute('color', new THREE.BufferAttribute(new Float32Array(67 * 3), 3)); scene.add(wordDots);
  const ringTex = (() => { const cv = document.createElement('canvas'); cv.width = cv.height = 128; const g = cv.getContext('2d');
    g.strokeStyle = 'rgba(255,255,255,0.9)'; g.lineWidth = 7; g.beginPath(); g.arc(64, 64, 48, 0, 7); g.stroke(); return new THREE.CanvasTexture(cv); })();
  const targets = new THREE.Points(new THREE.BufferGeometry(), new THREE.PointsMaterial({ size: 0.34, map: ringTex, color: WEIGHT, transparent: true, depthWrite: false, blending: A }));
  const wrongIdx = WORDS.filter((w) => M.circDist(w.peaks[0].x, w.xt) > M.TOL).map((w) => w.i);
  targets.geometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(wrongIdx.flatMap((i) => euler(WORDS[i].xt).toArray())), 3));
  scene.add(targets);
  const mxAmpAll = Math.max(...WORDS.map((w) => w.peaks[M.STEPS].amp));

  // ------------------------------------------------------------ the bloom (petals, halo, dust)
  const N_PET = 96;
  const petGeo = new THREE.PlaneGeometry(0.035, 1); petGeo.translate(0, 0.5, 0);
  // each petal carries its own light gradient: dark at the base, bright a third of the way out,
  // gone at the tip. Without it 96 petals stacked at one point and summed to a white disc.
  const petTex = (() => { const cv = document.createElement('canvas'); cv.width = 8; cv.height = 128; const g = cv.getContext('2d');
    const gr = g.createLinearGradient(0, 128, 0, 0); gr.addColorStop(0, 'rgba(255,255,255,0)'); gr.addColorStop(0.18, 'rgba(255,255,255,0.15)');
    gr.addColorStop(0.38, 'rgba(255,255,255,1)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, 8, 128);
    return new THREE.CanvasTexture(cv); })();
  const petals = new THREE.InstancedMesh(petGeo, new THREE.MeshBasicMaterial({ color: 0xffffff, map: petTex, transparent: true, blending: A, depthWrite: false, side: THREE.DoubleSide }), N_PET);
  const petCol = new THREE.Color(); const rp = M.rng(96);
  const petRand = Array.from({ length: N_PET }, () => [rp(), rp()]);
  for (let i = 0; i < N_PET; i++) { const f = petRand[i][0];
    petCol.copy(cWhite).lerp(cGold, Math.min(1, f * 1.6)); if (f > 0.62) petCol.lerp(cCurve, (f - 0.62) / 0.38); petals.setColorAt(i, petCol.multiplyScalar(0.55)); }
  petals.frustumCulled = false; scene.add(petals);
  const halos = [0, 1, 2].map(() => { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: haloTex, transparent: true, blending: A, depthWrite: false })); scene.add(s); return s; });
  const N_DUST = 40; const rd = M.rng(40);
  const dustV = Array.from({ length: N_DUST }, () => { const v = new THREE.Vector3(rd() * 2 - 1, rd() * 2 - 1, rd() * 2 - 1).normalize(); return { v, birth: rd() * 1.3, speed: 0.35 + rd() * 0.5 }; });
  const dust = new THREE.Points(new THREE.BufferGeometry(), new THREE.PointsMaterial({ size: 0.05, map: sprite, vertexColors: true, transparent: true, depthWrite: false, blending: A }));
  dust.geometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(N_DUST * 3), 3));
  dust.geometry.setAttribute('color', new THREE.BufferAttribute(new Float32Array(N_DUST * 3), 3)); scene.add(dust);
  const local = Array.from({ length: 32 }, () => fatLine(160, 1.4));       // WATER's 32 components, wrapped locally
  const localSum = fatLine(160, 4.0);

  // ------------------------------------------------------------ HUD
  const items = [];
  function hudPlane(cv, x, y, o = {}) {
    const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace;
    const sc = o.scale || 0.5, w = cv.width * sc, h = cv.height * sc;
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: t, transparent: true, depthTest: false, toneMapped: false }));
    if (o.top !== undefined) y = o.top - h / 2;                          // anchor by the top edge (tall TeX: limits on the sum)
    if (Math.abs(y) + h / 2 > HH - 8 || w / 2 > HW - 8) throw new Error(`HUD item off frame: ${w.toFixed(0)}x${h.toFixed(0)} at y=${y.toFixed(0)}`);
    m.position.set(x, y, 0); m.visible = false; hud.add(m);
    const it = Object.assign({ m, x, y, w, t0: 0, t1: 1, fin: 0.4, fout: 0.5 }, o); items.push(it); return it;
  }
  const TOP = PORTRAIT ? 720 : 462;
  hudPlane(textCanvas('BUT WHY DO THEY MOVE?', { size: PORTRAIT ? 64 : 92, spacing: 6, glow: 'rgba(46,230,200,0.35)' }), 0, PORTRAIT ? 620 : 300, { t0: B.slam[0], t1: B.slam[1], fin: 0.3, fout: 0.5, slam: true });
  hudPlane(svg.eq_psi, 0, TOP, { t0: B.waves, t1: B.sup - 0.3, fin: 0.25, fout: 0.6, wipe: 2.0, scale: PORTRAIT ? 0.62 : 0.88, top: PORTRAIT ? 820 : 522 });
  hudPlane(textCanvas('SUPERPOSITION', { size: 60, spacing: 14, color: CSS.gold }), 0, TOP, { t0: B.interf, t1: B.wrap - 0.4, fin: 0.5, fout: 0.5 });
  hudPlane(textCanvas('PEAK → POSITION', { size: 76, spacing: 8, glow: 'rgba(255,138,43,0.4)' }), 0, TOP, { t0: B.wrap + 0.15, t1: B.land - 0.5, fin: 0.3, fout: 0.5, slam: true });
  hudPlane(svg.eq_update, 0, TOP, { t0: B.train, t1: B.bloom - 0.4, fin: 0.4, fout: 0.6, wipe: 1.0, scale: PORTRAIT ? 0.9 : 1.1 });
  hudPlane(textCanvas('PART III — THE TEACHERS', { size: PORTRAIT ? 50 : 70, spacing: 10 }), 0, 0, { t0: B.tease + 0.5, t1: B.card[0] - 0.2, fin: 0.9, fout: 0.6 });
  hudPlane(textCanvas('S M A R T   L O O K U P  ·  P A R T  I I', { size: PORTRAIT ? 38 : 56, weight: '700', color: CSS.curve }), 0, PORTRAIT ? 150 : 120, { t0: B.card[0], t1: B.card[1], fin: 0.6, fout: 0.5 });
  hudPlane(textCanvas('θ  ·  ψ(x)  ·  superposition', { size: PORTRAIT ? 34 : 44, weight: '400', color: CSS.ink }), 0, PORTRAIT ? 60 : 30, { t0: B.card[0] + 0.25, t1: B.card[1], fin: 0.6, fout: 0.5 });
  hudPlane(textCanvas('PART III — THE TEACHERS', { size: PORTRAIT ? 34 : 44, spacing: 6, color: CSS.gold }), 0, PORTRAIT ? -30 : -60, { t0: B.card[0] + 0.5, t1: B.card[1], fin: 0.6, fout: 0.5 });
  hudPlane(textCanvas('[ COMING ]', { size: PORTRAIT ? 28 : 34, weight: '400', spacing: 8, color: CSS.dim }), 0, PORTRAIT ? -110 : -140, { t0: B.card[0] + 0.75, t1: B.card[1], fin: 0.6, fout: 0.5 });

  // ------------------------------------------------------------ camera on rails
  const orbit = (c, d, ang, el) => ({ pos: new THREE.Vector3(c.x + d * DIST * Math.sin(ang) * Math.cos(el), c.y + d * DIST * Math.sin(el), c.z + d * DIST * Math.cos(ang) * Math.cos(el)), look: c.clone() });
  const recapCam = (tau) => orbit(CC, 12.5, 0.5 + 0.012 * tau, 0.33);
  const nW = outward(water.xt);
  const nearW = (d) => ({ pos: PW.clone().addScaledVector(nW, 0.35 * d).add(new THREE.Vector3(0, 0.25 * d, d)), look: PW.clone() });
  const shots = [
    [0, (t) => recapCam(t)],
    [B.theta, (t) => { const k = easeExp((t - B.theta) / 2.6); const a = recapCam(t), b = nearW(3.3 * DIST);
      return { pos: a.pos.clone().lerp(b.pos, k), look: a.look.clone().lerp(b.look, k) }; }],
    [B.bars - 0.8, (t) => orbit(ST, 10.8, 0.10 * Math.sin((t - B.bars) * 0.25), 0.06)],
    [B.waves, (t) => orbit(ST.clone().add(new THREE.Vector3(0, -0.15, 0)), 12.6, 0.05 * Math.sin((t - B.waves) * 0.2), 0.04)],
    [B.sup, (t) => orbit(ST, lerp(12.0, 10.4, ease((t - B.sup) / 6)), 0.35 * ease((t - B.sup) / 4) * 0.9, 0.12)],
    [B.interf, (t) => { const u = (t - B.interf) / 9; return orbit(ST, 10.6, lerp(0.32, -0.55, ease(u * 1.3)), lerp(0.14, 0.02, ease(u * 1.4))); }],
    [B.wrap, (t) => orbit(CC, lerp(10.5, 13.2, ease((t - B.wrap) / 4)), lerp(-0.2, 0.35, ease((t - B.wrap) / 7)), lerp(0.05, 0.36, ease((t - B.wrap) / 5)))],
    [B.land, (t) => orbit(CC, lerp(13.2, 15.0, ease((t - B.land) / 5)), 0.35 + 0.35 / 4 * (t - B.land), 0.4)],
    [B.train + 4.2, (t) => { const k = easeExp((t - (B.train + 4.2)) / 3.0); const a = orbit(CC, 14.5, 0.35 + 0.35 / 4 * (t - B.land), 0.4), b = nearW(3.4 * DIST);
      return { pos: a.pos.clone().lerp(b.pos, k), look: a.look.clone().lerp(b.look, k) }; }],
    [B.bloom + 1.5, (t) => { const d = nearW(3.4 * DIST - 0.35 * ease((t - B.bloom - 1.5) / 3)); d.pos.x += 0.06 * Math.sin((t - B.bloom) * 0.6); return d; }],
    [B.reveal, (t) => orbit(CC, lerp(9, 14, ease((t - B.reveal) / 4)), 0.9 + 0.08 * (t - B.reveal), lerp(0.3, 0.45, ease((t - B.reveal) / 4)))],
    [B.tease, (t) => orbit(CC, lerp(14, 16.5, ease((t - B.tease) / 5)), 0.9 + 0.08 * (t - B.reveal), 0.45)],
    [B.seam[0], () => recapCam(0)],
  ];
  const BLEND = 1.4;
  function camAt(t) {
    let i = shots.length - 1; while (shots[i][0] > t) i--;
    let c = shots[i][1](t);
    if (i > 0) { const w = ease((t - shots[i][0]) / (i === shots.length - 1 ? B.seam[1] - B.seam[0] - 0.25 : BLEND));
      if (w < 1) { const p = shots[i - 1][1](t); c = { pos: p.pos.lerp(c.pos, w), look: p.look.lerp(c.look, w) }; } }
    return c;
  }

  // ------------------------------------------------------------ word state through training
  function wordState(i, t) {
    const w = WORDS[i];
    let n = 0, f = 0;
    if (t >= B.train) { const p = (t - B.train) / PULSE; n = Math.min(M.STEPS - 1, Math.floor(p)); f = t >= B.train + M.STEPS * PULSE ? 1 : easeOut((p - n) / 0.75); if (t >= B.train + M.STEPS * PULSE) n = M.STEPS - 1; }
    const a = w.peaks[n], b = w.peaks[Math.min(M.STEPS, n + (t >= B.train ? 1 : 0))];
    let dx = b.x - a.x; if (dx > 0.5) dx -= 1; if (dx < -0.5) dx += 1;
    const x = (a.x + dx * f + 1) % 1, amp = lerp(a.amp, b.amp, f);
    const right = M.circDist(x, w.xt) <= M.TOL;
    return { x, amp, right };
  }

  // ================================================================ update
  const v3 = new THREE.Vector3();
  function update(t) {
    const cam = camAt(t); camera.position.copy(cam.pos); camera.lookAt(cam.look);
    const seamW = ease((t - B.seam[0]) / (B.seam[1] - B.seam[0] - 0.25));        // 1 = back to frame 1 exactly
    const recapA = Math.max(1 - ease((t - B.theta) / 1.5), seamW);

    // Part I's world
    const curveA = Math.max(recapA, win(t, B.wrap + 0.6, B.seam[0] + 0.6, 1.6, 0.6) * (1 + 0.35 * win(t, B.reveal, B.tease + 2, 1.5, 2)));
    const flick = t > B.problem && t < B.train ? 0.22 * ease((t - B.problem) / 1) * ease((B.train - t) / 0.6) * (0.5 + 0.5 * Math.sin(t * 7.3) * Math.sin(t * 3.1)) : 0;
    curveTube.material.opacity = 0.55 * curveA * (1 - flick) * (1 - 0.5 * win(t, B.card[0] - 0.4, B.card[1] + 0.4, 0.6, 0.6)); curveTube.visible = curveTube.material.opacity > 0.003;
    pts.material.opacity = 0.9 * recapA + 0.22 * win(t, B.land, B.seam[0], 2, 0.5) * (1 - seamW); pts.visible = pts.material.opacity > 0.003;
    waterPts.material.opacity = recapA * (1 - 0.6 * ease((t - B.theta - 1.2) / 1.2)) + seamW * 0; waterPts.visible = waterPts.material.opacity > 0.003;
    if (seamW > 0) waterPts.material.opacity = seamW, waterPts.visible = true;

    // theta blooms out of WATER's dot, turns, then unfolds into the bars
    const thA = win(t, B.theta + 0.4, B.bars + 0.8, 1.6, 0.8);
    thetaGroup.visible = thA > 0.003; floor.visible = thetaGroup.visible; thetaGlow.visible = thetaGroup.visible;
    if (thetaGroup.visible) {
      const grow = easeExp((t - B.theta - 0.4) / 2.2), toStage = ease((t - (B.bars - 0.8)) / 1.4);
      const at = PW.clone().addScaledVector(nW, 0.9 * grow).add(new THREE.Vector3(0, 0.35 * grow, 0)).lerp(ST.clone().add(new THREE.Vector3(0, 1.0, 0)), toStage);
      thetaGroup.position.copy(at); thetaGroup.scale.setScalar((0.02 + grow * 0.78 * (1 + 0.6 * toStage)) * (1 - 0.85 * ease((t - B.bars - 0.2) / 0.8)));
      thetaGroup.rotation.set(0.15 * Math.sin(t * 0.7), (t - B.theta) * 0.9, 0);
      thMat.opacity = thA; thMat.emissiveIntensity = 0.45 + 0.5 * grow;
      floor.position.copy(at).add(new THREE.Vector3(0, -0.85 * thetaGroup.scale.x, 0)); floor.scale.setScalar(thetaGroup.scale.x); floor.material.opacity = 0.45 * thA;
      key.position.copy(at).add(new THREE.Vector3(1.5, 5, 2)); key.target.position.copy(at);
      thetaGlow.position.copy(at); thetaGlow.scale.setScalar(1.5 * thetaGroup.scale.x); thetaGlow.material.opacity = 0.22 * thA;
    }

    // 32 bars rise from the baseline, one tick each, labelled theta_1..theta_32
    for (let k = 0; k < 32; k++) {
      const tk = B.bars + 0.3 + k * 0.19, rise = easeOut((t - tk) / 0.5);
      const a = win(t, tk, B.waves + 0.8 + k * 0.05, 0.25, 0.6);
      const h = thW0[k] * BAR_SCALE * rise;
      bars[k].visible = a > 0.003 && Math.abs(h) > 1e-3;
      bars[k].scale.set(1, Math.max(Math.abs(h), 1e-3), 1); bars[k].position.set(barX(k), ST.y + h / 2, 0);
      bars[k].material.opacity = a;
      barLbl[k].visible = a > 0.003; barLbl[k].material.opacity = a * 0.9;
      barLbl[k].position.set(barX(k), ST.y + (thW0[k] >= 0 ? -0.2 : 0.2), 0.1);
    }

    // each bar becomes its sine wave; then the 32 waves stack into psi
    const morphOn = t > B.waves - 0.2 && t < B.interf + 0.6;
    for (let k = 0; k < 32; k++) {
      const l = comps[k]; l.visible = morphOn;
      if (!morphOn) continue;
      const m = easeExp((t - B.waves - k * 0.06) / 2.2);                       // bar -> wave
      const stack = easeExp((t - B.sup - (31 - k) * 0.03) / 3.0);              // row -> stack
      const yRow = lerp(rowY(k), ST.y, stack);
      const amp = thW0[k] * lerp(ROW_SCALE, ROW_SCALE, stack);
      const fade = 1 - 0.8 * ease((t - B.sup - 2.2) / 2.0) - 0.2 * ease((t - B.interf) / 0.5);
      l.material.opacity = Math.max(0, fade) * ease((t - B.waves + 0.2) / 0.3);
      setLine(l, (u) => {
        const wv = v3.set(stageX(u), yRow + amp * Math.sin(2 * Math.PI * M.F[k] * u + M.PHI[k]), 0);
        if (m >= 1) return wv;
        const bx = barX(k), by = ST.y + thW0[k] * BAR_SCALE * u;           // the bar, as a vertical segment
        return new THREE.Vector3(lerp(bx, wv.x, m), lerp(by, wv.y, m), 0);
      }, () => cTmp.copy(cWeight).multiplyScalar(0.55));
    }
    // the superposed wave: brightness IS |psi| (slow bloom: 3 s, exponential)
    const sumA = win(t, B.sup + 2.2, B.interf + 0.5, 1.2, 0.5);
    sumLine.visible = sumA > 0.003;
    if (sumLine.visible) {
      const glow = easeExp((t - B.sup - 3.0) / 3.0);
      sumLine.material.opacity = sumA;
      setLine(sumLine, (u, j) => v3.set(stageX(u), ST.y + psiW0[j] * SUM_SCALE * ease((t - B.sup - 1.5) / 2), 0.02),
        (u, j) => { const a = Math.abs(psiW0[j]) / mxPsi0; return bright(cGold, a * (0.35 + 0.65 * glow)); });
    }

    // interference: two real sinusoids, one from each side
    const iOn = t > B.interf - 0.1 && t < B.wrap + 0.5;
    ia.visible = ib.visible = isum.visible = interfGlow.visible = iOn;
    if (iOn) {
      const sa = easeExp((t - B.interf) / 3.0) , sb = easeExp((t - B.interf - 0.5) / 3.0);
      const offA = (1 - sa) * -SW, offB = (1 - sb) * SW;
      const fadeAB = 1 - 0.65 * ease((t - B.interf - 3.6) / 1.0);
      const out = ease((B.wrap + 0.4 - t) / 0.6);
      ia.material.opacity = fadeAB * out; ib.material.opacity = fadeAB * out;
      setLine(ia, (u) => v3.set(stageX(u) + offA, ST.y + 0.75 * M.interfA(u), -0.25), () => cTmp.copy(cCurve).multiplyScalar(0.8));
      setLine(ib, (u) => v3.set(stageX(u) + offB, ST.y + 0.75 * M.interfB(u), 0.25), () => cTmp.copy(cWeight).multiplyScalar(0.9));
      const sumOn = ease((t - B.interf - 3.4) / 1.2);
      isum.material.opacity = sumOn * out;
      // the envelope of the sum decides colour: constructive -> white and bright, cancelled -> dim grey line
      setLine(isum, (u) => v3.set(stageX(u), ST.y + 0.75 * (M.interfA(u) + M.interfB(u)) * sumOn, 0),
        (u) => { const env = Math.abs(Math.cos(Math.PI * (M.INTERF.fB - M.INTERF.fA) * u));
          return env > 0.3 ? bright(cWhite, env * 0.86) : cTmp.setRGB(0.16, 0.18, 0.22).multiplyScalar(0.6 + env); });
      const cx = stageX(0.0); // the constructive stretch sits at u = 0 / 1 (cos = 1); show the one on screen at u = 1
      interfGlow.position.set(stageX(1.0) - 0.12, ST.y, 0.05);
      const gl = ease((t - B.interf - 4.2) / 1.8) * out; interfGlow.material.opacity = 0.5 * gl; interfGlow.scale.setScalar(0.3 + 1.0 * gl);
    }

    // the golden wave wraps onto the closed curve; its peak becomes WATER's dot
    const wrapOn = t > B.wrap - 0.1 && t < B.land + 3;
    wrapLine.visible = wrapOn;
    if (wrapOn) {
      const w = easeExp((t - B.wrap - 0.4) / 3.2);
      wrapLine.material.opacity = ease((t - B.wrap) / 0.5) * (1 - ease((t - B.land - 0.5) / 2.2));
      const nn = wrapLine.userData.n;
      setLine(wrapLine, (u) => {
        const pv = M.psi(thW0, u);
        const a = new THREE.Vector3(stageX(u), ST.y + pv * SUM_SCALE, 0.02);
        const b = euler(u).addScaledVector(outward(u), pv * 0.9 / mxPsi0);
        return a.lerp(b, w);
      }, (u) => bright(cGold, Math.abs(M.psi(thW0, u)) / mxPsi0));
    }
    const dotA = win(t, B.wrap + 3.4, B.land + 0.8, 0.5, 0.8) + 0;
    peakDot.visible = dotA > 0.003;
    if (peakDot.visible) { const pulse = 1 + 0.35 * Math.sin((t - B.wrap - 3.4) * 5) * Math.exp(-(t - B.wrap - 3.4) * 0.6);
      peakDot.position.copy(euler(water.peaks[0].x)); peakDot.scale.setScalar(0.42 * pulse); peakDot.material.opacity = dotA; }

    // the landscape: 67 words, each a stacked wave pointing at its own peak
    const landA = win(t, B.land, B.seam[0] + 0.3, 1.8, 0.7);
    spikes.visible = wordDots.visible = landA > 0.003;
    if (spikes.visible) {
      const P = new Float32Array(67 * 6), Cc = new Float32Array(67 * 6), dp = wordDots.geometry.attributes.position.array, dc = wordDots.geometry.attributes.color.array;
      for (let i = 0; i < 67; i++) {
        const st = wordState(i, t), base = euler(st.x), n = outward(st.x);
        const appear = ease((t - B.land - 0.2 - i * 0.025) / 0.6);
        const h = (0.25 + 0.95 * st.amp / mxAmpAll) * appear;
        const tip = base.clone().addScaledVector(n, h);
        P.set([base.x, base.y, base.z, tip.x, tip.y, tip.z], 6 * i);
        // neutral blue until the problem is posed; then gold = in its slot, purple = not yet
        const judged = t >= B.problem - 0.5;
        let col = i === M.WATER ? cTarget : (!judged ? cVocab : (st.right ? cGold : cWeight));
        const glow = (st.right ? 0.75 : 0.85) * (1 + 0.5 * win(t, B.reveal, B.tease + 3, 1.5, 3) * (st.right ? 1 : 0));
        cTmp.copy(col).multiplyScalar(glow);
        Cc.set([cTmp.r * 0.35, cTmp.g * 0.35, cTmp.b * 0.35, cTmp.r, cTmp.g, cTmp.b], 6 * i);
        dp.set([base.x, base.y, base.z], 3 * i); dc.set([cTmp.r, cTmp.g, cTmp.b], 3 * i);
      }
      const back = 1 - 0.85 * win(t, B.bloom, B.reveal + 0.5, 1.0, 1.5) - 0.7 * win(t, B.card[0] - 0.4, B.card[1] + 0.4, 0.6, 0.6);
      spikeGeo.setPositions(P); spikeGeo.setColors(Cc); spikeMat.opacity = landA * back;
      wordDots.geometry.attributes.position.needsUpdate = true; wordDots.geometry.attributes.color.needsUpdate = true; wordDots.material.opacity = landA * back;
    }
    targets.material.opacity = 0.7 * win(t, B.problem + 0.4, B.train + M.STEPS * PULSE + 0.6, 0.8, 0.8); targets.visible = targets.material.opacity > 0.003;

    // the bloom: WATER's 32 waves align, then light unfolds where |psi| is largest
    const locOn = t > B.bloom - 0.2 && t < B.reveal + 2;
    localSum.visible = locOn; local.forEach((l) => (l.visible = locOn));
    if (locOn) {
      const al = easeExp((t - B.bloom - 0.3) / 1.6);
      const th = thW0.map((a, k) => lerp(a, thW8[k], al));
      const span = 0.075, lA = win(t, B.bloom, B.reveal + 1.5, 0.8, 1.2);
      const mx = Math.max(maxAbs(th), 1e-6), pAt = (u) => M.psi(th, u);
      const pMax = Math.abs(pAt(water.xt));
      for (let k = 0; k < 32; k++) {
        const l = local[k]; l.material.opacity = 0.65 * lA * (1 - 0.5 * ease((t - B.burst) / 1.0));
        const fan = new THREE.Vector3(0, 0, 1).applyAxisAngle(new THREE.Vector3(1, 0, 0), (k - 15.5) * 0.035);
        setLine(l, (u) => { const x = water.xt + (u - 0.5) * 2 * span;
          return euler(x).addScaledVector(outward(x), 0.32 * th[k] / mx * Math.sin(2 * Math.PI * M.F[k] * x + M.PHI[k])).addScaledVector(fan, 0.04 * (k - 15.5) / 15.5); },
          () => cTmp.copy(cWeight).multiplyScalar(0.6));
      }
      localSum.material.opacity = lA;
      setLine(localSum, (u) => { const x = water.xt + (u - 0.5) * 2 * span; return euler(x).addScaledVector(outward(x), 0.34 * pAt(x) / pMax * (0.7 + 0.3 * al)); },
        (u) => { const x = water.xt + (u - 0.5) * 2 * span; return bright(cGold, Math.abs(pAt(x)) / pMax * (0.5 + 0.5 * al)); });
    }
    // FAST bloom: 0.8 s burst, 1.5 s settle; gone within 3 s
    const bt = t - B.burst, burst = bt < 0 ? 0 : bt < 0.8 ? easeOut(bt / 0.8) : 1 - ease((bt - 0.8) / 1.5) * 0.65;
    const bAlive = bt >= 0 && bt < 2.95;
    const peakPos = euler(water.xt).addScaledVector(nW, 0.34);
    petals.visible = bAlive; halos.forEach((h) => (h.visible = bAlive)); dust.visible = bAlive;
    if (bAlive) {
      const fade = 1 - ease((bt - 2.2) / 0.75);
      const tang = euler(water.xt + 1e-3).sub(euler(water.xt - 1e-3)).normalize();
      const a1 = new THREE.Vector3().crossVectors(tang, nW).normalize(), a2 = new THREE.Vector3().crossVectors(tang, a1).normalize();
      const rot = 0.5 * easeOut(bt / 2.0), mtx = new THREE.Matrix4(), q = new THREE.Quaternion(), up = new THREE.Vector3(0, 1, 0);
      for (let i = 0; i < N_PET; i++) {
        const ang = 2 * Math.PI * i / N_PET + rot, len = (0.22 + 0.34 * petRand[i][1]) * burst;
        const dir = a1.clone().multiplyScalar(Math.cos(ang)).addScaledVector(a2, Math.sin(ang)).addScaledVector(tang, 0.35 * Math.sin(3 * ang)).normalize();
        q.setFromUnitVectors(up, dir);
        mtx.compose(peakPos, q, new THREE.Vector3(1, Math.max(len, 1e-3), 1)); petals.setMatrixAt(i, mtx);
      }
      petals.instanceMatrix.needsUpdate = true; petals.material.opacity = 0.95 * fade;
      halos.forEach((h, i) => { h.position.copy(peakPos); h.scale.setScalar([0.12, 0.28, 0.55][i] * (0.4 + burst)); h.material.opacity = [0.32, 0.14, 0.06][i] * burst * fade; });
      const dpp = dust.geometry.attributes.position.array, dcc = dust.geometry.attributes.color.array;
      for (let i = 0; i < N_DUST; i++) {
        const age = bt - dustV[i].birth, life = clamp01(1 - age / 2.0), on = age > 0 && age < 2.0;
        const p = peakPos.clone().addScaledVector(dustV[i].v, on ? age * dustV[i].speed * 0.55 : 0);
        dpp.set([p.x, p.y, p.z], 3 * i); const c = on ? life * life : 0; dcc.set([c, c * 0.85, c * 0.55], 3 * i);
      }
      dust.geometry.attributes.position.needsUpdate = true; dust.geometry.attributes.color.needsUpdate = true; dust.material.opacity = 1;
    }

    // HUD
    for (const it of items) {
      const a = win(t, it.t0, it.t1, it.fin, it.fout), m = it.m; m.visible = a > 0.003; if (!m.visible) continue;
      m.material.opacity = a; let s = 1;
      if (it.slam) { const r = clamp01((t - it.t0) / 0.3); s = 1 + 0.32 * (1 - r) * (1 - r); }
      m.scale.set(s, s, 1); m.position.x = it.x;
      if (it.wipe) {                                              // the equation draws on, left to right
        const f = Math.max(0.001, ease((t - it.t0) / it.wipe)); m.material.map.repeat.x = f; m.scale.x = f * s;
        m.position.x = it.x - it.w / 2 * (1 - f);
      }
    }
    api.bloom = 0.55 + 0.2 * win(t, B.sup + 3, B.interf, 2, 0.8) + 0.15 * (bt > -0.2 && bt < 3 ? burst : 0) + 0.12 * win(t, B.reveal, B.tease + 4, 2, 2);
  }
  const api = { scene, camera, hud, hudCam, update, shadows: true, bloom: 0.55, bloomRadius: 0.4, bloomThreshold: 0.34,
    facts: { wrongAtStart: wrongIdx.length, words: WORDS.length, waterX: water.xt, peaks0: water.peaks[0].x } };
  return api;
}
