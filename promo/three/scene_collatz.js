// scene_collatz.js — THE COLLATZ CONJECTURE, as a glowing coral in space.
// 9:16, 40.0s @ 30fps = 1200 frames.
//
// Rule: even -> n/2, odd -> 3n+1. Every number tried falls to 1; no proof.
// Drawing (after Edmund Harriss's "Collatz coral"): walk each number's path
// BACKWARDS from 1; every step bends one way if the number is even and the
// other way if it is odd, plus a small twist so it lives in 3D. Shared tails
// become shared branches, so 1..10,000 grows into a single tree.
//
// Checked standalone first (collatz_check.mjs): 27 -> 111 steps, peak 9,232;
// longest under 10,000 is 6,171 with 261 steps; 21,664 distinct numbers.
// "Checked up to 2^68" is the published computer verification, not computed here.
import { LineSegments2 } from 'three/addons/lines/LineSegments2.js';
import { LineSegmentsGeometry } from 'three/addons/lines/LineSegmentsGeometry.js';
import { Line2 } from 'three/addons/lines/Line2.js';
import { LineGeometry } from 'three/addons/lines/LineGeometry.js';
import { LineMaterial } from 'three/addons/lines/LineMaterial.js';

export const FPS = 30;
export const DURATION = 40.0;

const NMAX = 10000, HERO = 27;
const BG = 0x020309;
const INK = '#EAF2FF', CTEAL = '#2EE6C8', CORANGE = '#FF8A2B', GREY = '#8A94A6';

// geometry of the coral
const STEP = 0.16;          // world length of one step
const TURN_EVEN = 0.135;
const TURN_ODD = -0.255;
const TWIST = 0.11;

// timeline (seconds)
const T_RULES = 2.4, T_WALK0 = 4.3, T_WALK1 = 16.8, T_CORAL0 = 20.0, T_CORAL1 = 28.5;

const clamp01 = (x) => Math.min(1, Math.max(0, x));
const smooth = (x) => { x = clamp01(x); return x * x * (3 - 2 * x); };
const lerp = (a, b, k) => a + (b - a) * k;
const win = (t, a, b, fi = 0.3, fo = 0.3) => smooth((t - a) / fi) * smooth((b - t) / fo);
const check = (ok, msg) => { if (!ok) throw new Error('CHECK FAILED: ' + msg); };
function rng(seed) { let s = seed >>> 0; return () => { s = (s + 0x6D2B79F5) >>> 0; let t = Math.imul(s ^ (s >>> 15), 1 | s);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const fmtN = (n) => n.toLocaleString('en-US');

function textCanvas(lines, o = {}) {
  const size0 = o.size || 48, weight = o.weight || 'bold', font = o.font || 'sans-serif';
  const color = o.color || INK, maxW = o.maxW || 0, SS = 2;
  const norm = lines.map((l) => (typeof l === 'string' ? [{ t: l }] : l));
  const meas = (size) => { const c = document.createElement('canvas').getContext('2d');
    return norm.map((runs) => runs.reduce((w, r) => { c.font = `${weight} ${size * (r.s || 1) * SS}px ${font}`;
      return w + c.measureText(r.t).width / SS; }, 0)); };
  let size = size0, widths = meas(size);
  if (maxW && Math.max(...widths) > maxW) { size = size0 * maxW / Math.max(...widths); widths = meas(size); }
  const lh = (o.lineH || 1.3) * size, pad = Math.ceil(size * 0.45);
  const w = Math.ceil(Math.max(...widths)) + pad * 2, h = Math.ceil(lh * norm.length + pad * 0.6) + pad;
  const cv = document.createElement('canvas'); cv.width = w * SS; cv.height = h * SS;
  const g = cv.getContext('2d'); g.scale(SS, SS);
  if (o.panel) { const r = 22; g.fillStyle = 'rgba(2,3,9,0.6)'; g.beginPath(); g.moveTo(r, 0); g.arcTo(w, 0, w, h, r);
    g.arcTo(w, h, 0, h, r); g.arcTo(0, h, 0, 0, r); g.arcTo(0, 0, w, 0, r); g.fill(); }
  norm.forEach((runs, li) => { let x = (w - widths[li]) / 2; const y = pad * 0.5 + lh * li + size;
    runs.forEach((r) => { g.fillStyle = r.c || color; g.font = `${weight} ${size * (r.s || 1)}px ${font}`;
      g.fillText(r.t, x, y - (r.r || 0) * size); x += g.measureText(r.t).width; }); });
  return { cv, w, h };
}

export function build(THREE, W, H) {
  if (Math.abs(W / H - 9 / 16) > 0.01) throw new Error('scene is laid out for 9:16');
  const A = THREE.AdditiveBlending;
  const scene = new THREE.Scene(); scene.background = new THREE.Color(BG);
  const camera = new THREE.PerspectiveCamera(40, W / H, 0.02, 800);
  const hud = new THREE.Scene(); const hudCam = new THREE.OrthographicCamera(-540, 540, 960, -960, -10, 10);

  // ------------------------------------------------------------ the math
  const next = (n) => (n % 2 === 0 ? n / 2 : 3 * n + 1);    // safe: max value 27,114,424 < 2^53
  const parent = new Map(), depth = new Map([[1, 0]]);
  for (let n = 1; n <= NMAX; n++) {
    const path = []; let m = n;
    while (!depth.has(m)) { path.push(m); m = next(m); }
    let d = depth.get(m);
    for (let i = path.length - 1; i >= 0; i--) { d += 1; depth.set(path[i], d); parent.set(path[i], i > 0 ? path[i - 1] : m); }
  }
  // parent above is "towards the number we came from"; we need child -> next(child)
  const heroPath = []; { let m = HERO; heroPath.push(m); while (m !== 1) { m = next(m); heroPath.push(m); } }
  check(heroPath.length - 1 === 111, `27 should take 111 steps, got ${heroPath.length - 1}`);
  const PEAK = Math.max(...heroPath), PEAK_STEP = heroPath.indexOf(PEAK);
  check(PEAK === 9232, `27 should peak at 9232, got ${PEAK}`);
  check(depth.size === 21664, `expected 21,664 numbers, got ${depth.size}`);
  let MAXD = 0; for (const d of depth.values()) MAXD = Math.max(MAXD, d);
  check(MAXD === 261 && depth.get(6171) === 261, 'longest path under 10,000 should be 6,171 at 261 steps');
  for (let n = 1; n <= NMAX; n++) check(depth.has(n), `${n} never reached 1`);   // every one of them falls to 1

  // ------------------------------------------------------------ the coral
  // place nodes in order of depth: each number hangs off next(number)
  const nodes = [...depth.keys()].sort((a, b) => depth.get(a) - depth.get(b));
  const pos = new Map(), ori = new Map();
  const qE = new THREE.Quaternion(), qO = new THREE.Quaternion(), qT = new THREE.Quaternion();
  const Z = new THREE.Vector3(0, 0, 1), F = new THREE.Vector3(0, 1, 0);
  qT.setFromAxisAngle(F, TWIST);
  qE.setFromAxisAngle(Z, TURN_EVEN).multiply(qT);
  qO.setFromAxisAngle(Z, TURN_ODD).multiply(qT);
  pos.set(1, new THREE.Vector3(0, 0, 0)); ori.set(1, new THREE.Quaternion());
  const seg = [], segCol = [], segDepth = [];
  const cA = new THREE.Color(0x6c5cff), cB = new THREE.Color(0x2ee6c8), cC = new THREE.Color(0xd6c8ff), cc = new THREE.Color();
  const box = new THREE.Box3().setFromPoints([pos.get(1)]);
  for (const n of nodes) {
    if (n === 1) continue;
    const p = next(n);
    const q = ori.get(p).clone().multiply(n % 2 === 0 ? qE : qO);
    const v = pos.get(p).clone().add(F.clone().applyQuaternion(q).multiplyScalar(STEP));
    ori.set(n, q); pos.set(n, v); box.expandByPoint(v);
    const pp = pos.get(p); seg.push(pp.x, pp.y, pp.z, v.x, v.y, v.z);
    const f = depth.get(n) / MAXD;
    if (f < 0.5) cc.copy(cA).lerp(cB, f / 0.5); else cc.copy(cB).lerp(cC, (f - 0.5) / 0.5);
    // thousands of branches overlap near the root, and additive glow sums them
    // to white; so brightness rises with depth instead of falling
    const k = 0.16 + 0.5 * f ** 0.6;
    segCol.push(cc.r * k, cc.g * k, cc.b * k, cc.r * k, cc.g * k, cc.b * k);
    segDepth.push(depth.get(n));
  }
  const NSEG = segDepth.length;
  // segments are in depth order, so "everything up to depth D" is a prefix
  const prefixAt = new Int32Array(MAXD + 2);
  { let i = 0; for (let d = 0; d <= MAXD + 1; d++) { while (i < NSEG && segDepth[i] <= d) i++; prefixAt[d] = i; } }
  const coralGeo = new LineSegmentsGeometry(); coralGeo.setPositions(seg); coralGeo.setColors(segCol);
  const coralMat = new LineMaterial({ color: 0xffffff, linewidth: 1.0, vertexColors: true, transparent: true,
    blending: A, depthWrite: false, opacity: 0.85 });
  coralMat.resolution.set(W, H);
  const coral = new LineSegments2(coralGeo, coralMat); coral.frustumCulled = false; scene.add(coral);
  const centre = box.getCenter(new THREE.Vector3()), size = box.getSize(new THREE.Vector3());
  const R = 0.5 * size.length();

  // the hero: 27's path, from 27 down to 1
  const heroPts = heroPath.map((n) => pos.get(n));
  const heroGeo = new LineGeometry(); heroGeo.setPositions(heroPts.flatMap((v) => [v.x, v.y, v.z]));
  const heroMat = new LineMaterial({ color: 0xff8a2b, linewidth: 5, transparent: true, blending: A, depthWrite: false });
  heroMat.resolution.set(W, H);
  const hero = new Line2(heroGeo, heroMat); hero.frustumCulled = false; scene.add(hero);
  const sprite = (() => { const cv = document.createElement('canvas'); cv.width = cv.height = 64; const g = cv.getContext('2d');
    const gr = g.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, 'rgba(255,255,255,1)');
    gr.addColorStop(0.3, 'rgba(255,255,255,0.6)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 64, 64); return new THREE.CanvasTexture(cv); })();
  const head = new THREE.Points(new THREE.BufferGeometry().setAttribute('position', new THREE.BufferAttribute(new Float32Array(3), 3)),
    new THREE.PointsMaterial({ size: 0.28, map: sprite, color: 0xffb070, transparent: true, depthWrite: false, blending: A }));
  scene.add(head);
  const root = new THREE.Points(new THREE.BufferGeometry().setAttribute('position', new THREE.BufferAttribute(new Float32Array(3), 3)),
    new THREE.PointsMaterial({ size: 0.5, map: sprite, color: 0xffffff, transparent: true, depthWrite: false, blending: A }));
  scene.add(root);

  // ------------------------------------------------------------ space
  { const N = 3000, r = rng(3), p = new Float32Array(N * 3), c = new Float32Array(N * 3);
    for (let i = 0; i < N; i++) { const u = r() * 2 - 1, th = r() * Math.PI * 2, rad = 80 + r() * 160, s = Math.sqrt(1 - u * u);
      p.set([rad * s * Math.cos(th), rad * u, rad * s * Math.sin(th)], 3 * i);
      const b = 0.25 + 0.75 * r() ** 3; c.set([b * (0.75 + 0.25 * r()), b * 0.85, b], 3 * i); }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(p, 3)); g.setAttribute('color', new THREE.BufferAttribute(c, 3));
    scene.add(new THREE.Points(g, new THREE.PointsMaterial({ size: 1.1, map: sprite, vertexColors: true, transparent: true, depthWrite: false, blending: A }))); }
  const neb = (() => { const cv = document.createElement('canvas'); cv.width = cv.height = 256; const g = cv.getContext('2d');
    const gr = g.createRadialGradient(128, 128, 0, 128, 128, 128); gr.addColorStop(0, 'rgba(255,255,255,0.55)');
    gr.addColorStop(0.45, 'rgba(255,255,255,0.18)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 256, 256); return new THREE.CanvasTexture(cv); })();
  [[-90, 40, -150, 180, 0x2a1c8a], [100, -50, -170, 200, 0x0b4a5c], [10, 90, -200, 160, 0x4a1450], [-60, -100, 140, 190, 0x13306a]]
    .forEach(([x, y, z, s, c]) => { const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: neb, color: c, transparent: true,
      opacity: 0.55, depthWrite: false, blending: A })); sp.position.set(x, y, z).add(centre); sp.scale.set(s, s, 1); scene.add(sp); });

  // ================================================================= HUD
  const items = [];
  function hudItem(info, x, y, o = {}) {
    const tex = new THREE.CanvasTexture(info.cv); tex.colorSpace = THREE.SRGBColorSpace;
    const mesh = new THREE.Mesh(new THREE.PlaneGeometry(info.w, info.h),
      new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthTest: false, toneMapped: false }));
    mesh.position.set(x, y, 0); mesh.visible = false; hud.add(mesh);
    if (x - info.w / 2 < -500 || x + info.w / 2 > 500 || y + info.h / 2 > 830 || y - info.h / 2 < -680)
      throw new Error(`HUD item outside the safe box: x=${x} y=${y} w=${info.w} h=${info.h}`);
    const it = Object.assign({ mesh, t0: 0, t1: 1, fin: 0.3, fout: 0.3 }, o); items.push(it); return it;
  }
  const say = (lines, y, t0, t1, to = {}, o = {}) => hudItem(textCanvas(lines, Object.assign({ maxW: 780 }, to)), 0, y, Object.assign({ t0, t1 }, o));
  const T_PEAK = T_WALK0 + (T_WALK1 - T_WALK0) * PEAK_STEP / (heroPath.length - 1);

  say(['PICK ANY NUMBER.'], 680, -0.1, T_RULES + 0.2, { size: 92 }, { slam: true });
  say([[{ t: 'EVEN → ', c: INK }, { t: 'HALVE IT', c: CTEAL }]], 690, T_RULES + 0.3, T_WALK1 - 0.6, { size: 60 });
  say([[{ t: 'ODD → ', c: INK }, { t: '3n + 1', c: CORANGE }]], 600, T_RULES + 0.7, T_WALK1 - 0.6, { size: 60 });
  say([[{ t: 'PEAK: ', c: INK }, { t: fmtN(PEAK), c: CORANGE }]], -300, T_PEAK, T_PEAK + 2.6, { size: 64, panel: true }, { slam: true });
  say([`${heroPath.length - 1} STEPS.`], 690, T_WALK1, T_CORAL0 - 0.1, { size: 82 }, { slam: true });
  say(['BACK TO 1.'], 590, T_WALK1 + 0.6, T_CORAL0 - 0.1, { size: 64, color: CTEAL });
  say(['NOW EVERY NUMBER'], 690, T_CORAL0 + 0.1, 27.0, { size: 76 });
  say([`UP TO ${fmtN(NMAX)}.`], 595, T_CORAL0 + 0.5, 27.0, { size: 64, color: CTEAL });
  say([`${fmtN(depth.size)} NUMBERS.`], 690, 27.25, 29.45, { size: 76 });
  say(['ONE TREE. ONE ROOT: 1.'], 595, 27.65, 29.45, { size: 56, color: CTEAL });
  say(['CHECKED BY COMPUTER'], 690, 29.67, 34.3, { size: 70 });
  say([[{ t: 'UP TO 2' }, { t: '68', s: 0.6, r: 0.55 }, { t: ' ≈ 295 QUINTILLION.', c: CTEAL }]], 595, 30.07, 34.3, { size: 54 });
  say(['NOBODY CAN PROVE WHY.'], 690, 34.5, 39.7, { size: 78, color: CORANGE }, { slam: true });
  say(['THE COLLATZ CONJECTURE'], -470, 35.6, 39.7, { size: 64, panel: true });
  say(['@observer.collapse'], -580, 36.6, 39.7, { size: 38, weight: 'normal', color: GREY });

  // the walking counter: 27's current value and step
  const ctr = (() => {
    const cv = document.createElement('canvas'), Wc = 760, Hc = 250, SS = 2; cv.width = Wc * SS; cv.height = Hc * SS;
    const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace;
    const mesh = new THREE.Mesh(new THREE.PlaneGeometry(Wc, Hc), new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthTest: false, toneMapped: false }));
    mesh.position.set(0, -480, 0); hud.add(mesh); let last = '';
    return { mesh, draw(value, step, parity) {
      const key = value + '|' + step; if (key === last) return; last = key;
      const g = cv.getContext('2d'); g.setTransform(SS, 0, 0, SS, 0, 0); g.clearRect(0, 0, Wc, Hc);
      const r = 26, x0 = 60, x1 = Wc - 60; g.fillStyle = 'rgba(2,3,9,0.6)'; g.beginPath(); g.moveTo(x0 + r, 6);
      g.arcTo(x1, 6, x1, Hc - 6, r); g.arcTo(x1, Hc - 6, x0, Hc - 6, r); g.arcTo(x0, Hc - 6, x0, 6, r); g.arcTo(x0, 6, x1, 6, r); g.fill();
      g.textAlign = 'center'; g.fillStyle = GREY; g.font = 'bold 32px sans-serif'; g.fillText(`STEP ${step}`, Wc / 2, 50);
      g.fillStyle = value === 1 ? CTEAL : INK; g.font = 'bold 112px monospace'; g.fillText(fmtN(value), Wc / 2, 168);
      if (parity) { g.fillStyle = parity === 'even' ? CTEAL : CORANGE; g.font = 'bold 30px sans-serif';
        g.fillText(parity === 'even' ? 'EVEN → HALVE' : 'ODD → 3n + 1', Wc / 2, 222); }
      tex.needsUpdate = true; } };
  })();

  // ================================================================ camera
  // a smoothed track along 27's path so the chase-cam does not jitter
  const track = heroPts.map((_, i) => { const v = new THREE.Vector3(); let n = 0;
    for (let j = Math.max(0, i - 6); j <= Math.min(heroPts.length - 1, i + 6); j++) { v.add(heroPts[j]); n++; } return v.multiplyScalar(1 / n); });
  const heroBox = new THREE.Box3().setFromPoints(heroPts), heroC = heroBox.getCenter(new THREE.Vector3());
  const heroR = 0.5 * heroBox.getSize(new THREE.Vector3()).length();
  const FIT = (r) => r / (Math.tan(20 * Math.PI / 180) * (W / H)) * 1.15;
  const trackAt = (s) => { const i = Math.min(Math.floor(s), track.length - 2); return track[i].clone().lerp(track[i + 1], s - i); };
  const look = new THREE.Vector3(), cpos = new THREE.Vector3();
  function placeCamera(t, stepF) {
    const ang = 0.4 + 0.07 * t, el = 0.25 + 0.06 * Math.sin(0.2 * t);
    // phase 1: chase the walker; phase 2: the whole of 27's path; phase 3: the whole coral
    const chase = trackAt(Math.min(stepF, heroPts.length - 1));
    const w1 = smooth((t - (T_WALK1 - 0.6)) / 2.6), w2 = smooth((t - T_CORAL0) / (T_CORAL1 - T_CORAL0 + 1.5));
    look.copy(chase).lerp(heroC, w1).lerp(centre, w2);
    const d = lerp(lerp(3.2, FIT(heroR), w1), FIT(R) * 0.62, w2);
    cpos.set(Math.sin(ang) * Math.cos(el), Math.sin(el), Math.cos(ang) * Math.cos(el)).multiplyScalar(d).add(look);
    camera.position.copy(cpos); camera.lookAt(look);
  }

  // ================================================================ update
  function update(t) {
    const stepF = (heroPath.length - 1) * clamp01((t - T_WALK0) / (T_WALK1 - T_WALK0));
    const k = Math.floor(stepF);
    placeCamera(t, stepF);
    // 27's path draws itself from 27 towards 1
    heroGeo.instanceCount = Math.max(0, Math.min(k, heroPath.length - 1));
    const hp = trackAt(0).copy(heroPts[Math.min(k, heroPts.length - 1)]);
    if (k < heroPts.length - 1) hp.lerp(heroPts[k + 1], stepF - k);
    head.geometry.attributes.position.array.set([hp.x, hp.y, hp.z]); head.geometry.attributes.position.needsUpdate = true;
    head.material.opacity = smooth(t / 0.4) * (1 - smooth((t - T_WALK1) / 0.8));
    heroMat.opacity = 0.95 - 0.45 * smooth((t - T_CORAL0) / 3);
    root.material.opacity = smooth((t - (T_WALK1 - 0.3)) / 0.6) * (0.6 + 0.4 * Math.abs(Math.sin(t * 3)));
    // the coral grows out from 1, depth by depth
    const D = Math.floor(MAXD * smooth((t - T_CORAL0) / (T_CORAL1 - T_CORAL0)) ** 0.8);
    coralGeo.instanceCount = t < T_CORAL0 ? 0 : prefixAt[Math.min(D, MAXD)];
    coral.visible = coralGeo.instanceCount > 0;
    coralMat.opacity = 0.85 * smooth((t - T_CORAL0) / 0.6);

    const value = heroPath[Math.min(k, heroPath.length - 1)];
    ctr.draw(value, Math.min(k, heroPath.length - 1), k < heroPath.length - 1 ? (value % 2 === 0 ? 'even' : 'odd') : null);
    ctr.mesh.material.opacity = win(t, 0.2, T_CORAL0 - 0.3, 0.4, 0.6);
    ctr.mesh.visible = ctr.mesh.material.opacity > 0.003;
    for (const it of items) {
      const a = win(t, it.t0, it.t1, it.fin, it.fout), m = it.mesh; m.visible = a > 0.003; if (!m.visible) continue;
      m.material.opacity = a; let sc = 1; if (it.slam) { const r = clamp01((t - it.t0) / 0.3); sc = 1 + 0.38 * (1 - r) * (1 - r); }
      m.scale.set(sc, sc, 1);
    }
    api.bloom = lerp(0.8, 0.5, smooth((t - T_CORAL0) / 2));
  }
  const api = { scene, camera, hud, hudCam, bloom: 0.8, update,
    facts: { steps27: heroPath.length - 1, PEAK, PEAK_STEP, T_PEAK, nodes: depth.size, MAXD, NSEG, R, heroR } };
  return api;
}
