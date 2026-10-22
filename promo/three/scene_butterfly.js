// scene_butterfly.js — THE BUTTERFLY EFFECT. Lorenz attractor in deep space.
// 9:16, 40.0s @ 30fps = 1200 frames.
//
// Story: two points start ONE BILLIONTH apart, obey the same three equations,
// and end up on opposite wings. Then 2,000 points a millionth apart spread
// across the whole butterfly. Every number on screen is computed here, live,
// from the same RK4 integration that draws the motion — nothing is typed in.
//
//   dx/dt = 10(y - x)    dy/dt = x(28 - z) - y    dz/dt = xy - (8/3)z
//
// Checked standalone first (lorenz_check.mjs): separation 1e-9 -> 1 at sim
// time 21.97, opposite wings at 26.89; implied growth rate 0.943 against the
// known Lorenz Lyapunov exponent of ~0.906.
import { Line2 } from 'three/addons/lines/Line2.js';
import { LineMaterial } from 'three/addons/lines/LineMaterial.js';
import { LineGeometry } from 'three/addons/lines/LineGeometry.js';

export const FPS = 30;
export const DURATION = 40.0;

const SIG = 10, RHO = 28, BET = 8 / 3, DT = 0.005;
const EPS = 1e-9;            // the pair
const CLOUD_N = 2000, CLOUD_R = 1e-6;
const T_CLOUD = 22.0;        // video second the cloud is released

const BG = 0x020309;
const TEAL = 0x2ee6c8, ORANGE = 0xff8a2b, VIOLET = 0x6c5cff;
const INK = '#EAF2FF', CTEAL = '#2EE6C8', CORANGE = '#FF8A2B', GREY = '#8A94A6';

const clamp01 = (x) => Math.min(1, Math.max(0, x));
const smooth = (x) => { x = clamp01(x); return x * x * (3 - 2 * x); };
const lerp = (a, b, k) => a + (b - a) * k;
const win = (t, a, b, fi = 0.3, fo = 0.3) => smooth((t - a) / fi) * smooth((b - t) / fo);
function rng(seed) {
  let s = seed >>> 0;
  return () => { s = (s + 0x6D2B79F5) >>> 0; let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
const check = (ok, msg) => { if (!ok) throw new Error('CHECK FAILED: ' + msg); };

// ------------------------------------------------------------------ math --
// one RK4 step, in place, on x,y,z stored at o in a Float64Array
function step(a, o) {
  const x = a[o], y = a[o + 1], z = a[o + 2], h = DT;
  const k1x = SIG * (y - x), k1y = x * (RHO - z) - y, k1z = x * y - BET * z;
  let X = x + 0.5 * h * k1x, Y = y + 0.5 * h * k1y, Z = z + 0.5 * h * k1z;
  const k2x = SIG * (Y - X), k2y = X * (RHO - Z) - Y, k2z = X * Y - BET * Z;
  X = x + 0.5 * h * k2x; Y = y + 0.5 * h * k2y; Z = z + 0.5 * h * k2z;
  const k3x = SIG * (Y - X), k3y = X * (RHO - Z) - Y, k3z = X * Y - BET * Z;
  X = x + h * k3x; Y = y + h * k3y; Z = z + h * k3z;
  const k4x = SIG * (Y - X), k4y = X * (RHO - Z) - Y, k4z = X * Y - BET * Z;
  a[o] = x + h / 6 * (k1x + 2 * k2x + 2 * k3x + k4x);
  a[o + 1] = y + h / 6 * (k1y + 2 * k2y + 2 * k3y + k4y);
  a[o + 2] = z + h / 6 * (k1z + 2 * k2z + 2 * k3z + k4z);
}

// ---------------------------------------------------------------- text ----
function textCanvas(lines, o = {}) {
  const size0 = o.size || 48, weight = o.weight || 'bold', font = o.font || 'sans-serif';
  const color = o.color || INK, align = o.align || 'center', maxW = o.maxW || 0, SS = 2;
  const norm = lines.map((l) => (typeof l === 'string' ? [{ t: l }] : l));
  const meas = (size) => { const c = document.createElement('canvas').getContext('2d');
    return norm.map((runs) => runs.reduce((w, r) => {
      c.font = `${r.i ? 'italic ' : ''}${weight} ${size * (r.s || 1) * SS}px ${font}`;
      return w + c.measureText(r.t).width / SS; }, 0)); };
  let size = size0, widths = meas(size);
  if (maxW && Math.max(...widths) > maxW) { size = size0 * maxW / Math.max(...widths); widths = meas(size); }
  const lh = (o.lineH || 1.3) * size, pad = Math.ceil(size * 0.45);
  const w = Math.ceil(Math.max(...widths)) + pad * 2, h = Math.ceil(lh * norm.length + pad * 0.6) + pad;
  const cv = document.createElement('canvas'); cv.width = w * SS; cv.height = h * SS;
  const g = cv.getContext('2d'); g.scale(SS, SS); g.textBaseline = 'alphabetic';
  if (o.panel) {                          // soft dark backing so lines stay legible over the glow
    const r = 22; g.fillStyle = 'rgba(2,3,9,0.62)'; g.beginPath();
    g.moveTo(r, 0); g.arcTo(w, 0, w, h, r); g.arcTo(w, h, 0, h, r); g.arcTo(0, h, 0, 0, r); g.arcTo(0, 0, w, 0, r); g.fill();
  }
  norm.forEach((runs, li) => {
    let x = align === 'left' ? pad : (w - widths[li]) / 2;
    const y = pad * 0.5 + lh * li + size;
    runs.forEach((r) => {
      g.fillStyle = r.c || color;
      g.font = `${r.i ? 'italic ' : ''}${weight} ${size * (r.s || 1)}px ${font}`;
      g.fillText(r.t, x, y - (r.r || 0) * size); x += g.measureText(r.t).width;
    });
  });
  return { cv, w, h };
}

export function build(THREE, W, H) {
  if (Math.abs(W / H - 9 / 16) > 0.01) throw new Error('scene is laid out for 9:16');
  const A = THREE.AdditiveBlending;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(BG);
  const camera = new THREE.PerspectiveCamera(40, W / H, 0.05, 600);
  const hud = new THREE.Scene();
  const hudCam = new THREE.OrthographicCamera(-540, 540, 960, -960, -10, 10);

  // ------------------------------------------------ the clock: video -> sim
  // The divergence takes ~27 sim units; at one honest speed it is either a
  // blur or an hour. So the sim runs slow while the points are together,
  // fast-forwards (and SAYS so on screen) through the long quiet middle,
  // and slows again so the split itself is watchable.
  const R0 = 0.75, R2 = 2.0;
  let RMAX = 3.5;
  const rateOf = (t) => R0 + (RMAX - R0) * win(t, 2.6, 10.6, 1.5, 1.6)
                        + (R2 - R0) * smooth((t - (T_CLOUD - 1.5)) / 1.5);
  const SUB = 20;                                     // integrate rate at 600 Hz
  let sTab;
  const buildS = () => {
    sTab = new Float64Array(Math.round(DURATION * FPS) + 2);
    let s = 0;
    for (let f = 0; f < sTab.length; f++) {
      sTab[f] = s;
      for (let k = 0; k < SUB; k++) s += rateOf((f + (k + 0.5) / SUB) / FPS) / (FPS * SUB);
    }
  };
  const simAt = (t) => { const x = t * FPS, f = Math.min(Math.floor(x), sTab.length - 2);
    return lerp(sTab[f], sTab[f + 1], x - f); };

  // ------------------------------------------------ the pair
  const start = new Float64Array([1, 1, 1]);
  // land on the attractor first, and keep the last 2 sim units: that stretch is
  // the pair's SHARED past, so frame 0 already has a tail instead of a dot
  const PRE_N = 400, PRE = new Float64Array(3 * PRE_N);
  for (let i = 0; i < 4000; i++) { step(start, 0); if (i >= 4000 - PRE_N) PRE.set(start, 3 * (i - (4000 - PRE_N))); }
  // run the pair once to find WHEN they reach opposite wings
  const pairRun = (nSteps) => {
    const a = new Float64Array(3 * (nSteps + 1)), b = new Float64Array(3 * (nSteps + 1));
    a.set(start); b.set([start[0] + EPS, start[1], start[2]]);
    const ca = new Float64Array(a.subarray(0, 3)), cb = new Float64Array(b.subarray(0, 3));
    for (let k = 1; k <= nSteps; k++) {
      step(ca, 0); step(cb, 0);
      a.set(ca, 3 * k); b.set(cb, 3 * k);
    }
    return { a, b };
  };
  const MAXS = 90;                                     // sim units kept
  const NST = Math.round(MAXS / DT);
  const { a: PA, b: PB } = pairRun(NST);
  const dist = (k) => Math.hypot(PA[3 * k] - PB[3 * k], PA[3 * k + 1] - PB[3 * k + 1], PA[3 * k + 2] - PB[3 * k + 2]);
  // The split is the first moment they sit on opposite wings while already
  // more than 10 apart: one goes left, one goes right. (They do not STAY on
  // opposite wings — measured stretches are 0.7-2 sim units — so no caption
  // claims they do. What stays true is checked below: they never come back.)
  let kOne = -1, kWing = -1;
  for (let k = 0; k <= NST; k++) {
    if (kOne < 0 && dist(k) > 1) kOne = k;
    if (kWing < 0 && kOne >= 0 && Math.sign(PA[3 * k]) !== Math.sign(PB[3 * k]) && dist(k) > 10) { kWing = k; break; }
  }
  check(kOne > 0 && kWing > 0, 'the pair never separated');
  const S_WING = kWing * DT;
  // solve the fast-forward speed so the split lands at 12.6s of video
  const T_SPLIT = 12.6;
  { let lo = 1, hi = 8;
    for (let it = 0; it < 50; it++) { RMAX = (lo + hi) / 2; buildS(); (simAt(T_SPLIT) < S_WING ? (lo = RMAX) : (hi = RMAX)); }
    buildS(); }
  check(Math.abs(simAt(T_SPLIT) - S_WING) < 1e-3, 'clock solve failed');
  // 'DIFFERENT PATHS' must hold for as long as the pair is on screen
  { let mn = Infinity; const kEnd = Math.round(simAt(T_CLOUD + 1) / DT);
    for (let k = kWing; k <= kEnd; k++) mn = Math.min(mn, dist(k));
    check(mn > 1, `the pair re-converged to ${mn}`); var MIN_AFTER = mn; }
  check(simAt(DURATION) < MAXS, 'not enough trajectory stored');
  const state = (arr, s) => {                       // linear interp between RK4 steps
    if (s < 0) {
      const x = PRE_N - 1 + s / DT, k = Math.max(0, Math.floor(x)), f = Math.min(1, x - k);
      return [lerp(PRE[3 * k], PRE[3 * k + 3], f), lerp(PRE[3 * k + 1], PRE[3 * k + 4], f), lerp(PRE[3 * k + 2], PRE[3 * k + 5], f)];
    }
    const x = s / DT, k = Math.min(Math.floor(x), NST - 1), f = x - k;
    return [lerp(arr[3 * k], arr[3 * k + 3], f), lerp(arr[3 * k + 1], arr[3 * k + 4], f), lerp(arr[3 * k + 2], arr[3 * k + 5], f)];
  };

  // ------------------------------------------------ the cloud
  const sC0 = simAt(T_CLOUD), sEnd = simAt(DURATION);
  const c0 = state(PA, sC0);
  const cl = new Float64Array(CLOUD_N * 3);
  { const r = rng(17);
    for (let i = 0; i < CLOUD_N; i++) {               // uniform in a ball of radius CLOUD_R
      let x, y, z; do { x = r() * 2 - 1; y = r() * 2 - 1; z = r() * 2 - 1; } while (x * x + y * y + z * z > 1);
      cl[3 * i] = c0[0] + CLOUD_R * x; cl[3 * i + 1] = c0[1] + CLOUD_R * y; cl[3 * i + 2] = c0[2] + CLOUD_R * z;
    } }
  const F0 = Math.round(T_CLOUD * FPS), F1 = Math.round(DURATION * FPS);
  const cloudFrames = [];                              // positions per video frame, Float32
  { let simNow = sC0, f = F0;
    while (f <= F1) {
      const target = simAt(f / FPS);
      while (simNow + DT <= target + 1e-12) { for (let i = 0; i < CLOUD_N; i++) step(cl, 3 * i); simNow += DT; }
      cloudFrames.push(Float32Array.from(cl)); f++;
    } }
  // how spread is it, frame by frame (rms distance from the cloud's mean)
  const spread = cloudFrames.map((c) => {
    let mx = 0, my = 0, mz = 0; for (let i = 0; i < CLOUD_N; i++) { mx += c[3 * i]; my += c[3 * i + 1]; mz += c[3 * i + 2]; }
    mx /= CLOUD_N; my /= CLOUD_N; mz /= CLOUD_N; let v = 0;
    for (let i = 0; i < CLOUD_N; i++) v += (c[3 * i] - mx) ** 2 + (c[3 * i + 1] - my) ** 2 + (c[3 * i + 2] - mz) ** 2;
    return Math.sqrt(v / CLOUD_N); });
  const fEvery = spread.findIndex((v) => v > 8);
  check(fEvery > 0, 'the cloud never spread');
  const T_EVERY = (F0 + fEvery) / FPS;
  check(T_EVERY < 33.5, `the cloud spreads too late: ${T_EVERY}`);
  { const c = cloudFrames[cloudFrames.length - 1]; let left = 0;
    for (let i = 0; i < CLOUD_N; i++) if (c[3 * i] < 0) left++;
    check(left > 0.25 * CLOUD_N && left < 0.75 * CLOUD_N, `cloud not on both wings: ${left}/${CLOUD_N}`); }

  // ------------------------------------------------ world mapping
  // Lorenz (x, y, z) -> world (x, z - 24, y), scaled: the butterfly stands up
  const SC = 0.11;
  const wv = (p, out) => out.set(p[0] * SC, (p[2] - 24) * SC, p[1] * SC);

  // ------------------------------------------------ space
  const sprite = (() => { const cv = document.createElement('canvas'); cv.width = cv.height = 64;
    const g = cv.getContext('2d'); const gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.3, 'rgba(255,255,255,0.6)');
    gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, 64, 64);
    return new THREE.CanvasTexture(cv); })();
  { const N = 3000, r = rng(3), pos = new Float32Array(N * 3), col = new Float32Array(N * 3);
    for (let i = 0; i < N; i++) {
      const u = r() * 2 - 1, th = r() * Math.PI * 2, rad = 60 + r() * 140, s = Math.sqrt(1 - u * u);
      pos.set([rad * s * Math.cos(th), rad * u, rad * s * Math.sin(th)], 3 * i);
      const b = 0.25 + 0.75 * r() ** 3, tint = r();
      col.set([b * (0.75 + 0.25 * tint), b * 0.85, b], 3 * i);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('color', new THREE.BufferAttribute(col, 3));
    scene.add(new THREE.Points(g, new THREE.PointsMaterial({ size: 0.9, map: sprite, vertexColors: true,
      transparent: true, depthWrite: false, blending: A }))); }
  // nebula: a few huge soft colour washes far behind everything
  const neb = (() => { const cv = document.createElement('canvas'); cv.width = cv.height = 256;
    const g = cv.getContext('2d'); const gr = g.createRadialGradient(128, 128, 0, 128, 128, 128);
    gr.addColorStop(0, 'rgba(255,255,255,0.55)'); gr.addColorStop(0.45, 'rgba(255,255,255,0.18)');
    gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, 256, 256);
    return new THREE.CanvasTexture(cv); })();
  [[-70, 30, -120, 140, 0x3a1c9a], [80, -40, -140, 160, 0x0b5a6c], [10, 70, -170, 130, 0x5a1450], [-40, -80, 120, 150, 0x13306a]]
    .forEach(([x, y, z, s, c]) => { const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: neb, color: c,
      transparent: true, opacity: 0.55, depthWrite: false, blending: A }));
      sp.position.set(x, y, z); sp.scale.set(s, s, 1); scene.add(sp); });

  // ------------------------------------------------ the butterfly's ghost
  const ghost = (() => {
    const tmp = new Float64Array(start), pts = [], v = new THREE.Vector3();
    for (let k = 0; k < 9000; k++) { step(tmp, 0); if (k % 3 === 0) { wv(tmp, v); pts.push(v.x, v.y, v.z); } }
    const g = new LineGeometry(); g.setPositions(pts);
    const m = new LineMaterial({ color: VIOLET, linewidth: 1.4, transparent: true, opacity: 0.0,
      blending: A, depthWrite: false });
    m.resolution.set(W, H);
    const l = new Line2(g, m); scene.add(l); return l; })();

  // ------------------------------------------------ the pair: dots + trails
  const TRAIL = 1.6, TRAIL_V = 160;                    // sim units of tail, vertices
  function mover(color) {
    const g = new LineGeometry(); const z = new Array(TRAIL_V * 3).fill(0);
    g.setPositions(z); g.setColors(z);
    const m = new LineMaterial({ color: 0xffffff, linewidth: 4.5, vertexColors: true, transparent: true,
      blending: A, depthWrite: false });
    m.resolution.set(W, H);
    const line = new Line2(g, m); scene.add(line);
    const dot = new THREE.Points(new THREE.BufferGeometry().setAttribute('position', new THREE.BufferAttribute(new Float32Array(3), 3)),
      new THREE.PointsMaterial({ size: 0.42, map: sprite, color, transparent: true, depthWrite: false, blending: A }));
    scene.add(dot);
    return { line, dot, c: new THREE.Color(color), pos: new Float32Array(TRAIL_V * 3), col: new Float32Array(TRAIL_V * 3) };
  }
  const MA = mover(TEAL), MB = mover(ORANGE);
  const _v = new THREE.Vector3();
  function drawMover(M, arr, s, alpha) {
    for (let j = 0; j < TRAIL_V; j++) {
      const ss = s - TRAIL * (1 - j / (TRAIL_V - 1));
      wv(state(arr, ss), _v); M.pos.set([_v.x, _v.y, _v.z], 3 * j);
      const k = (j / (TRAIL_V - 1)) ** 1.6 * alpha;          // tail fades to black = invisible (additive)
      M.col.set([M.c.r * k, M.c.g * k, M.c.b * k], 3 * j);
    }
    M.line.geometry.setPositions(M.pos); M.line.geometry.setColors(M.col);
    M.dot.geometry.attributes.position.array.set(M.pos.subarray(3 * (TRAIL_V - 1)));
    M.dot.geometry.attributes.position.needsUpdate = true;
    M.dot.material.opacity = alpha; M.line.visible = M.dot.visible = alpha > 0.003;
  }

  // ------------------------------------------------ the cloud's points
  const cloudPts = (() => {
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(CLOUD_N * 3), 3));
    const col = new Float32Array(CLOUD_N * 3), ct = new THREE.Color(TEAL), co = new THREE.Color(ORANGE), cv = new THREE.Color(0xd6c8ff);
    for (let i = 0; i < CLOUD_N; i++) {
      const c = i % 3 === 0 ? ct : i % 3 === 1 ? co : cv; col.set([c.r, c.g, c.b], 3 * i); }
    g.setAttribute('color', new THREE.BufferAttribute(col, 3));
    const p = new THREE.Points(g, new THREE.PointsMaterial({ size: 0.075, map: sprite, vertexColors: true,
      transparent: true, depthWrite: false, blending: A }));
    scene.add(p); return p; })();

  // ================================================================== HUD
  const items = [];
  function hudItem(info, x, y, o = {}) {
    const tex = new THREE.CanvasTexture(info.cv); tex.colorSpace = THREE.SRGBColorSpace;
    const mesh = new THREE.Mesh(new THREE.PlaneGeometry(info.w, info.h),
      new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthTest: false, toneMapped: false }));
    mesh.position.set(x, y, 0); mesh.visible = false; hud.add(mesh);
    if (x - info.w / 2 < -500 || x + info.w / 2 > 500 || y + info.h / 2 > 830 || y - info.h / 2 < -680)
      throw new Error(`HUD item outside the safe box: x=${x} y=${y} w=${info.w} h=${info.h}`);
    const it = Object.assign({ mesh, x, y, w: info.w, h: info.h, t0: 0, t1: 1, fin: 0.3, fout: 0.3 }, o);
    items.push(it); return it;
  }
  const say = (lines, y, t0, t1, to = {}, o = {}) => hudItem(textCanvas(lines, Object.assign({ maxW: 780 }, to)), 0, y, Object.assign({ t0, t1 }, o));

  // the hook — on screen from frame 0
  say(['TWO POINTS.'], 680, -0.1, 4.6, { size: 104 }, { slam: true });
  say(['ONE BILLIONTH APART.'], 570, 0.35, 4.6, { size: 60, color: CTEAL });
  say(['SAME THREE RULES.'], 680, 4.9, 9.4, { size: 70 });
  // the split, timed off the simulation
  const T_ONE = (() => { let t = 0; while (simAt(t) < kOne * DT) t += 1 / FPS; return t; })();
  say(['NOW THEY DISAGREE.'], 680, T_SPLIT - 0.4, 17.8, { size: 78, color: CORANGE }, { slam: true });
  say([[{ t: 'SAME RULES. ', c: INK }, { t: 'DIFFERENT PATHS.', c: CORANGE }]], 585, T_SPLIT + 0.6, 17.8, { size: 54 });
  // the cloud
  say(['2,000 MORE POINTS.'], 680, T_CLOUD + 0.4, T_EVERY + 0.2, { size: 76 });
  say(['A MILLIONTH APART.'], 585, T_CLOUD + 0.9, T_EVERY + 0.2, { size: 54, color: CTEAL });
  say(['NOW: EVERYWHERE.'], 680, T_EVERY + 0.5, 34.4, { size: 84, color: CORANGE }, { slam: true });
  // the rules themselves, then the name of the thing
  const eqf = { size: 50, font: 'serif', weight: 'normal', align: 'left', lineH: 1.35 };
  say([[{ t: 'dx/dt = 10(y − x)', i: 1 }], [{ t: 'dy/dt = x(28 − z) − y', i: 1 }],
       [{ t: 'dz/dt = xy − (8/3)z', i: 1 }]], -540, 34.6, 39.6, Object.assign({ maxW: 640, panel: true }, eqf), { fin: 0.7 });
  say(['THE BUTTERFLY EFFECT'], 680, 34.8, 39.7, { size: 82 }, { slam: true });
  say(['@observer.collapse'], 575, 36.2, 39.7, { size: 40, weight: 'normal', color: GREY });

  // the live distance counter — redrawn only when its text changes
  const ctr = (() => {
    const cv = document.createElement('canvas'), Wc = 820, Hc = 240, SS = 2;
    cv.width = Wc * SS; cv.height = Hc * SS;
    const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace;
    const mesh = new THREE.Mesh(new THREE.PlaneGeometry(Wc, Hc),
      new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthTest: false, toneMapped: false }));
    mesh.position.set(0, -470, 0); hud.add(mesh);
    let last = '';
    return { mesh, draw(val, ff) {
      const key = val + '|' + ff; if (key === last) return; last = key;
      const g = cv.getContext('2d'); g.setTransform(SS, 0, 0, SS, 0, 0); g.clearRect(0, 0, Wc, Hc);
      { const r = 26, x0 = 70, x1 = Wc - 70; g.fillStyle = 'rgba(2,3,9,0.6)'; g.beginPath();
        g.moveTo(x0 + r, 6); g.arcTo(x1, 6, x1, Hc - 6, r); g.arcTo(x1, Hc - 6, x0, Hc - 6, r);
        g.arcTo(x0, Hc - 6, x0, 6, r); g.arcTo(x0, 6, x1, 6, r); g.fill(); }
      g.textAlign = 'center'; g.fillStyle = GREY; g.font = 'bold 34px sans-serif'; g.fillText('DISTANCE BETWEEN THEM', Wc / 2, 46);
      g.fillStyle = INK; g.font = 'bold 84px monospace'; g.fillText(val, Wc / 2, 140);
      if (ff) { g.fillStyle = CTEAL; g.font = 'bold 32px sans-serif'; g.fillText('▶▶  FAST-FORWARD', Wc / 2, 205); }
      tex.needsUpdate = true; } };
  })();
  const fmt = (d) => d < 1e-3 ? d.toFixed(9) : d < 10 ? d.toFixed(3) : d.toFixed(1);
  check(fmt(EPS) === '0.000000001', 'counter does not open on one billionth');

  // ================================================================ camera
  const centre = new THREE.Vector3(0, 0, 0), look = new THREE.Vector3(), cpos = new THREE.Vector3();
  function placeCamera(t, pA) {
    // The wings sit at x = y = +/-8.5, so the view that separates them best
    // looks down the (1,-1) diagonal (world angle -pi/4). Swing around that,
    // never orbit edge-on where the two wings collapse into a V.
    const ang = -Math.PI / 4 + 0.62 * Math.sin(0.16 * t + 0.4);
    const el = 0.18 + 0.08 * Math.sin(t * 0.13);
    // chase-cam riding with the pair, opening out to the whole butterfly
    const open = smooth((t - 2.2) / 6.5);
    const dist = lerp(2.6, 15.5, open) - 1.6 * smooth((t - T_CLOUD) / 10);
    look.copy(pA).lerp(centre, open);
    cpos.set(Math.sin(ang) * Math.cos(el), Math.sin(el), Math.cos(ang) * Math.cos(el)).multiplyScalar(dist).add(look);
    camera.position.copy(cpos); camera.lookAt(look);
  }

  // ================================================================ update
  const pA = new THREE.Vector3();
  function update(t) {
    const s = simAt(t);
    wv(state(PA, s), pA);
    placeCamera(t, pA);

    const pairA = smooth((t + 0.2) / 0.3) * (1 - 0.75 * smooth((t - (T_CLOUD - 0.5)) / 1.2)) * smooth((39.8 - t) / 0.6);
    drawMover(MA, PA, s, pairA);
    drawMover(MB, PB, s, pairA);
    ghost.material.opacity = 0.42 * smooth((t - (T_SPLIT + 1.0)) / 2.5);
    ghost.visible = ghost.material.opacity > 0.003;

    const ci = Math.round(t * FPS) - F0;
    if (ci >= 0 && ci < cloudFrames.length) {
      const a = cloudPts.geometry.attributes.position.array, c = cloudFrames[ci];
      for (let i = 0; i < CLOUD_N; i++) { a[3 * i] = c[3 * i] * SC; a[3 * i + 1] = (c[3 * i + 2] - 24) * SC; a[3 * i + 2] = c[3 * i + 1] * SC; }
      cloudPts.geometry.attributes.position.needsUpdate = true;
      // brightness follows the spread: 2,000 coincident additive sprites saturate into a white square
      cloudPts.material.opacity = smooth((t - T_CLOUD) / 0.5) * (0.004 + 0.95 * clamp01(spread[ci] / 2.5) ** 0.8);
      // grow the sprites a touch as they spread, so a tight ball still reads as many
      cloudPts.material.size = lerp(0.16, 0.075, smooth((t - T_CLOUD) / 6));
      cloudPts.visible = true;
    } else cloudPts.visible = false;

    // the counter: the real separation of the pair at this instant
    const k = Math.min(Math.round(s / DT), NST);
    const ffOn = rateOf(t) > 1.6 && t < T_SPLIT;
    ctr.draw(fmt(dist(k)), ffOn);
    ctr.mesh.material.opacity = win(t, 0.6, T_CLOUD - 1.0, 0.5, 0.8);
    ctr.mesh.visible = ctr.mesh.material.opacity > 0.003;

    for (const it of items) {
      const a = win(t, it.t0, it.t1, it.fin, it.fout), m = it.mesh;
      m.visible = a > 0.003; if (!m.visible) continue;
      m.material.opacity = a;
      let sc = 1; if (it.slam) { const r = clamp01((t - it.t0) / 0.3); sc = 1 + 0.38 * (1 - r) * (1 - r); }
      m.scale.set(sc, sc, 1);
    }
    api.bloom = lerp(0.6, 0.85, smooth((t - 6) / 4));
  }
  const api = { scene, camera, hud, hudCam, bloom: 0.85, update,
    facts: { S_WING, T_SPLIT, T_ONE, T_EVERY, MIN_AFTER, RMAX, sEnd, sOne: kOne * DT } };
  return api;
}
