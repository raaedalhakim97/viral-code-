// scene_smart_lookup.js — "What If Words Could Learn Inside a Curve?"
// Real 3D (three.js) rebuild of the manimgl Smart Lookup film, 9:16.
// 95.0s @ 30fps = 2850 frames, nine beats:
//   1 hook   2 words->numbers->space   3 word universe   4 the equation
//   5 2D->3D Euler curve   6 2,144 points   7 learning loop   8 stats   9 outro
//
// A scene module exports FPS, DURATION and build(THREE, W, H) -> {scene,
// camera, hud, hudCam, update(t)}. It owns no clock: the renderer calls
// update(t) with t in seconds, so frame N is always the same image.
export const FPS = 30;
export const DURATION = 95.0;

const BG = 0x05070f;
const COL = { curve: 0x2ee6c8, target: 0xff8a2b, vocab: 0x3b6fd4,
              weights: 0x9b5cf6, ink: 0xeaf2ff, dim: 0x1b2740 };
const CSS = { curve: '#2EE6C8', target: '#FF8A2B', vocab: '#3B6FD4',
              weights: '#9B5CF6', ink: '#EAF2FF', dim: '#1B2740' };

const clamp01 = (x) => Math.min(1, Math.max(0, x));
const smooth = (x) => { x = clamp01(x); return x * x * (3 - 2 * x); };
const lerp = (a, b, k) => a + (b - a) * k;
// 0 -> 1 over fin seconds after a, 1 -> 0 over fout seconds before b
const win = (t, a, b, fin = 0.3, fout = 0.3) =>
  smooth((t - a) / fin) * smooth((b - t) / fout);

function rng(seed) {                       // mulberry32: same scatter every render
  let s = seed >>> 0;
  return () => {
    s = (s + 0x6D2B79F5) >>> 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function euler(t) {
  const r = Math.exp(Math.cos(t));
  return [r * Math.cos(t), r * Math.sin(t), Math.sin(2 * t)];
}

// ---------------------------------------------------------------- text ----
// runs: [{t, s=1 (size factor), r=0 (rise, in em)}]. One line per runs-array.
function textCanvas(lines, o = {}) {
  const size0 = o.size || 48, weight = o.weight || 'bold', font = o.font || 'sans-serif';
  const color = o.color || CSS.ink, align = o.align || 'center', maxW = o.maxW || 0;
  const SS = 2;                                           // 2x supersample
  const norm = lines.map((l) => (typeof l === 'string' ? [{ t: l }] : l));
  const meas = (size) => {
    const c = document.createElement('canvas').getContext('2d');
    return norm.map((runs) => runs.reduce((w, r) => {
      c.font = `${r.i ? 'italic ' : ''}${weight} ${size * (r.s || 1) * SS}px ${font}`;
      return w + c.measureText(r.t).width / SS;
    }, 0));
  };
  let size = size0, widths = meas(size);
  if (maxW && Math.max(...widths) > maxW) {
    size = size0 * maxW / Math.max(...widths); widths = meas(size);
  }
  const lh = (o.lineH || 1.35) * size;
  const pad = Math.ceil(size * 0.45);
  const w = Math.ceil(Math.max(...widths)) + pad * 2;
  const h = Math.ceil(lh * norm.length + pad * 0.6) + pad;
  const cv = document.createElement('canvas');
  cv.width = w * SS; cv.height = h * SS;
  const g = cv.getContext('2d');
  g.scale(SS, SS);
  g.fillStyle = color; g.textBaseline = 'alphabetic';
  const starts = [], rws = [];
  norm.forEach((runs, li) => {
    starts[li] = []; rws[li] = [];
    let x = align === 'left' ? pad : (w - widths[li]) / 2;
    const y = pad * 0.5 + lh * li + size * 1.0;
    runs.forEach((r, ri) => {
      g.font = `${r.i ? 'italic ' : ''}${weight} ${size * (r.s || 1)}px ${font}`;
      g.fillText(r.t, x, y - (r.r || 0) * size);
      const rw = g.measureText(r.t).width;
      starts[li][ri] = x; rws[li][ri] = rw; x += rw;
    });
  });
  return { cv, w, h, starts, rws, size, pad };
}

function panelCanvas(w, h, stroke, fill, inner) {          // a card / box
  const SS = 2, cv = document.createElement('canvas');
  cv.width = w * SS; cv.height = h * SS;
  const g = cv.getContext('2d'); g.scale(SS, SS);
  const r = 14, x = 3, y = 3, ww = w - 6, hh = h - 6;
  g.beginPath();
  g.moveTo(x + r, y); g.arcTo(x + ww, y, x + ww, y + hh, r);
  g.arcTo(x + ww, y + hh, x, y + hh, r); g.arcTo(x, y + hh, x, y, r);
  g.arcTo(x, y, x + ww, y, r); g.closePath();
  g.fillStyle = fill; g.fill();
  g.lineWidth = 3; g.strokeStyle = stroke; g.stroke();
  if (inner) inner(g, w, h);
  return { cv, w, h };
}

export function build(THREE, W, H) {
  if (Math.abs(W / H - 9 / 16) > 0.01) throw new Error('scene is laid out for 9:16');
  const A = THREE.AdditiveBlending;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(BG);
  scene.fog = new THREE.FogExp2(BG, 0.02);
  const camera = new THREE.PerspectiveCamera(38, W / H, 0.1, 400);

  // HUD: orthographic, units are pixels, origin at the centre, y up.
  const hud = new THREE.Scene();
  // fixed 1080x1920 units whatever the render size, so a half-res preview is a true half-res
  const hudCam = new THREE.OrthographicCamera(-540, 540, 960, -960, -10, 10);

  // ------------------------------------------------------------ helpers --
  const sprite = (() => {
    const cv = document.createElement('canvas'); cv.width = cv.height = 64;
    const g = cv.getContext('2d');
    const gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.35, 'rgba(255,255,255,0.55)');
    gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 64, 64);
    return new THREE.CanvasTexture(cv);
  })();

  // A Layer is a group whose every material can be faded together.
  function Layer() {
    const g = new THREE.Group(), mats = [];
    return {
      g,
      add(o) {
        g.add(o);
        o.traverse((n) => { if (n.material) mats.push({ m: n.material, b: n.material.opacity }); });
        return o;
      },
      set(a) { for (const x of mats) x.m.opacity = x.b * a; g.visible = a > 0.003; },
    };
  }
  const layer = () => { const L = Layer(); scene.add(L.g); L.set(0); return L; };

  function points(n, size, color, op = 1) {
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(n * 3), 3));
    const mat = new THREE.PointsMaterial({
      size, map: sprite, color, transparent: true, opacity: op, depthWrite: false,
      blending: A, sizeAttenuation: true });
    return new THREE.Points(geo, mat);
  }
  function setPts(p, arr) {
    const a = p.geometry.attributes.position.array;
    for (let i = 0; i < arr.length; i++) a[i] = arr[i];
    p.geometry.attributes.position.needsUpdate = true;
  }

  function cyl(r, color, op) {
    return new THREE.Mesh(new THREE.CylinderGeometry(r, r, 1, 6, 1, true),
      new THREE.MeshBasicMaterial({ color, transparent: true, opacity: op, blending: A, depthWrite: false }));
  }
  const _y = new THREE.Vector3(0, 1, 0), _d = new THREE.Vector3();
  function place(m, a, b) {
    _d.subVectors(b, a); const L = _d.length();
    m.position.copy(a).addScaledVector(_d, 0.5); m.scale.set(1, Math.max(L, 1e-4), 1);
    m.quaternion.setFromUnitVectors(_y, _d.normalize());
  }

  // a label that lives in the 3D world (so it takes part in the bloom)
  function label(str, o = {}) {
    const t = textCanvas([str], { size: o.size || 56, color: o.color || CSS.ink, weight: o.weight || 'bold' });
    const tex = new THREE.CanvasTexture(t.cv); tex.colorSpace = THREE.SRGBColorSpace;
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({
      map: tex, transparent: true, depthTest: false, depthWrite: false }));
    const k = (o.height || 0.5) / t.h;
    sp.scale.set(t.w * k, t.h * k, 1);
    return sp;
  }

  // a flat HUD item with its own timing
  const items = [];
  function hudItem(info, x, y, o = {}) {
    const tex = new THREE.CanvasTexture(info.cv); tex.colorSpace = THREE.SRGBColorSpace;
    const mesh = new THREE.Mesh(new THREE.PlaneGeometry(info.w, info.h),
      new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthTest: false, toneMapped: false }));
    mesh.position.set(x, y, 0); mesh.visible = false;
    hud.add(mesh);
    // everything on the HUD must sit inside the platform safe box
    const hw = info.w / 2 * (o.zoom ? 1 : 1);
    if (!o.zoom && !o.free) {
      if (x - hw < -500 || x + hw > 500 || y + info.h / 2 > 820 || y - info.h / 2 < -690)
        throw new Error(`HUD item outside the safe box: x=${x} y=${y} w=${info.w} h=${info.h}`);
    }
    const it = Object.assign({ mesh, x, y, w: info.w, h: info.h, t0: 0, t1: 1, fin: 0.3, fout: 0.3 }, o);
    items.push(it);
    return it;
  }
  const hudText = (lines, x, y, o = {}, to = {}) => hudItem(textCanvas(lines, to), x, y, o);

  // =============================================================== world ==
  // always-on dust: gives every shot some parallax to read against
  const DUST = 700;
  const dust = points(DUST, 0.10, COL.vocab, 0.5);
  { const r = rng(5), a = new Float32Array(DUST * 3);
    for (let i = 0; i < DUST; i++) {
      a[i * 3] = (r() - 0.5) * 60; a[i * 3 + 1] = (r() - 0.5) * 70; a[i * 3 + 2] = -45 + r() * 75;
    }
    setPts(dust, a); scene.add(dust); }

  // ---- beat 1: the dot ---------------------------------------------------
  const dotL = layer();
  const dotCore = points(1, 0.55, COL.curve, 1); setPts(dotCore, [0, 0, 0]); dotL.add(dotCore);
  const dotHalo = points(1, 2.4, COL.curve, 0.30); setPts(dotHalo, [0, 0, 0]); dotL.add(dotHalo);

  // ---- beat 2: keywords + numbers + the launch ---------------------------
  const kwL = layer();
  const kwNames = ['WATER', 'MOLECULE', 'HYDROGEN', 'CHEMICAL', 'COMPOUND'];
  const kwPos = kwNames.map((_, i) => {
    const a = i * Math.PI * 2 / 5 + 0.4; return [1.65 * Math.cos(a), 3.2 * Math.sin(a) + 0.3, 0];
  });
  const kwSprites = [], numSprites = [];
  { const r = rng(11);
    kwNames.forEach((w, i) => {
      const s = label(w, { color: CSS.target, height: 0.62, size: 60 });
      s.position.set(...kwPos[i]); kwL.add(s); kwSprites.push(s);
      const nums = Array.from({ length: 4 }, () => {
        const v = (r() * 1.98 - 0.99); return (v >= 0 ? '+' : '−') + Math.abs(v).toFixed(2);
      }).join('  ');
      const n = label(nums, { color: CSS.vocab.replace('3B6FD4', '6F9BEA'), height: 0.30, size: 40, weight: 'normal' });
      n.position.set(kwPos[i][0], kwPos[i][1] - 0.62, 0); kwL.add(n); numSprites.push(n);
    }); }
  const scL = layer();
  const scatter = points(60, 0.34, COL.curve, 0.85); scL.add(scatter);
  const scBase = new Float32Array(180), scVel = new Float32Array(180);
  { const r = rng(7);
    for (let i = 0; i < 60; i++) {
      scBase[i * 3] = (r() - 0.5) * 6; scBase[i * 3 + 1] = (r() - 0.5) * 9; scBase[i * 3 + 2] = (r() - 0.5) * 4;
      scVel[i * 3] = (r() - 0.5) * 0.9; scVel[i * 3 + 1] = (r() - 0.5) * 0.9; scVel[i * 3 + 2] = (r() - 0.5) * 0.5;
    } }

  // ---- beat 3: the word universe ----------------------------------------
  const uniL = layer();
  const US = 0.55, UC = [0.5, 0.15, 0.5], UPREAD = 1.7;   // UPREAD: label legibility, same link topology                 // scale, box centre
  const uni = new THREE.Group(); uni.scale.setScalar(US);
  uni.position.set(-UC[0] * US, -UC[1] * US, -UC[2] * US);
  uniL.add(uni);
  const uO = new THREE.Vector3(-4, -2.5, -1.5);
  const axEnd = [new THREE.Vector3(5, -2.5, -1.5), new THREE.Vector3(-4, 2.8, -1.5), new THREE.Vector3(-4, -2.5, 2.5)];
  const axes = axEnd.map((e) => { const c = cyl(0.025, 0x5a78b0, 0.6); uni.add(c); place(c, uO, e); return c; });
  const axLbl = ['x', 'y', 'z'].map((s, i) => {
    const l = label(s, { height: 0.5, size: 60, weight: 'normal' });
    l.position.copy(axEnd[i]).add(new THREE.Vector3(0.0, 0.0, 0)).addScaledVector(axEnd[i].clone().sub(uO).normalize(), 0.45);
    uni.add(l); return l;
  });
  let uPos = [];
  { const r = rng(42);
    for (let i = 0; i < 67; i++) uPos.push(new THREE.Vector3(
      lerp(-3, 4.5, r()), lerp(-2, 2.3, r()), lerp(-1.2, 2.2, r())));
    const cen = new THREE.Vector3(1.2, 0.5, 0.6);
    [[0, 0, 0], [0.7, 0.35, 0.15], [-0.55, 0.45, 0.25], [0.35, -0.55, 0.15], [-0.35, -0.45, -0.1]]
      .forEach((o, i) => { uPos[i] = cen.clone().add(new THREE.Vector3(...o).multiplyScalar(UPREAD)); }); }
  const blues = points(62, 0.30, COL.vocab, 0.9);
  setPts(blues, uPos.slice(5).flatMap((v) => [v.x, v.y, v.z])); uni.add(blues);
  const oranges = points(5, 0.62, COL.target, 1);
  setPts(oranges, uPos.slice(0, 5).flatMap((v) => [v.x, v.y, v.z])); uni.add(oranges);
  const uNames = ['WATER', 'CHEMICAL', 'COMPOUND', 'H2O', 'POLAR'];
  const uLbl = uNames.map((n, i) => {
    const l = label(n, { color: CSS.target, height: 0.62, size: 60 });
    l.position.copy(uPos[i]).add(new THREE.Vector3(0, 0.55, 0)); uni.add(l); return l;
  });
  const conns = [];
  for (let i = 0; i < 5; i++) for (let j = i + 1; j < 5; j++)
    if (uPos[i].distanceTo(uPos[j]) < 1.3 * UPREAD) {
      const c = cyl(0.022, COL.curve, 0.8); uni.add(c); place(c, uPos[i], uPos[j]); conns.push(c);
    }
  const ringPts = Array.from({ length: 60 }, (_, k) => {
    const a = k / 60 * Math.PI * 2;
    return new THREE.Vector3(1.2 + 1.05 * UPREAD * Math.cos(a), 0.5 + 1.05 * UPREAD * Math.sin(a), 0.6 + 0.15 * Math.sin(3 * a));
  });
  const ring = new THREE.Mesh(
    new THREE.TubeGeometry(new THREE.CatmullRomCurve3(ringPts, true), 200, 0.022, 6, true),
    new THREE.MeshBasicMaterial({ color: COL.curve, transparent: true, opacity: 0.8, blending: A, depthWrite: false }));
  uni.add(ring);
  // the pieces appear on their own clocks, so each one gets its own fader
  const uniParts = [
    { o: axes, a: 17.4, b: 27.6 }, { o: axLbl, a: 18.0, b: 27.6 },
    { o: [blues], a: 18.4, b: 27.6, fin: 1.6 }, { o: [oranges], a: 20.2, b: 27.6, fin: 0.9 },
    { o: uLbl, a: 21.2, b: 27.6 }, { o: conns, a: 22.4, b: 27.6, fin: 1.0 },
    { o: [ring], a: 23.8, b: 27.6, fin: 1.0 },
  ];
  uniParts.forEach((p) => { p.mats = p.o.flatMap((x) => { const m = []; x.traverse((n) => { if (n.material) m.push({ m: n.material, b: n.material.opacity }); }); return m; }); });

  // ---- beat 5: the complex plane and the curve ---------------------------
  const SC = 2.0, ZS = 1.3;
  const planeL = layer();
  const reAx = cyl(0.03, 0x5a78b0, 0.6), imAx = cyl(0.03, 0x5a78b0, 0.6);
  planeL.add(reAx); planeL.add(imAx);
  place(reAx, new THREE.Vector3(-1.4, 0, 0), new THREE.Vector3(5.6, 0, 0));
  place(imAx, new THREE.Vector3(0, -3.4, 0), new THREE.Vector3(0, 3.4, 0));
  const reLbl = label('Re', { height: 0.85, size: 60, weight: 'normal' }); reLbl.position.set(5.2, -0.65, 0); planeL.add(reLbl);
  const imLbl = label('Im', { height: 0.85, size: 60, weight: 'normal' }); imLbl.position.set(0.55, 3.55, 0); planeL.add(imLbl);
  const radL = layer();
  const radLine = radL.add(cyl(0.05, COL.weights, 0.9));
  const traceDot = radL.add(points(1, 0.6, COL.target, 1));

  const curveL = layer();
  let tube = null, lastZ = -1, curveObj = null;
  function curveAt(zs) {
    const pts = [];
    for (let i = 0; i < 240; i++) {
      const c = euler(i / 240 * Math.PI * 2);
      pts.push(new THREE.Vector3(SC * c[0], SC * c[1], SC * zs * c[2]));
    }
    return new THREE.CatmullRomCurve3(pts, true);
  }
  function setZ(zs) {
    if (Math.abs(zs - lastZ) < 1e-4) return;
    lastZ = zs; curveObj = curveAt(zs);
    const geo = new THREE.TubeGeometry(curveObj, 600, 0.02, 6, true);
    if (!tube) {
      tube = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({
        color: COL.curve, transparent: true, opacity: 0.42, blending: A, depthWrite: false }));
      curveL.add(tube);
    } else { tube.geometry.dispose(); tube.geometry = geo; }
  }
  setZ(0.001);
  const TUBE_IDX = 600 * 6 * 6;                           // index count of the full tube

  // ---- beat 6: the 2,144 points -----------------------------------------
  const N = 2144;
  const partL = layer();
  const P = (() => {
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(N * 3), 3));
    geo.setAttribute('color', new THREE.BufferAttribute(new Float32Array(N * 3), 3));
    return new THREE.Points(geo, new THREE.PointsMaterial({
      size: 0.2, map: sprite, vertexColors: true, transparent: true, opacity: 1,
      depthWrite: false, blending: A, sizeAttenuation: true }));
  })();
  partL.add(P);
  const pStart = new Float32Array(N * 3), pTarget = new Float32Array(N * 3), pTarget0 = new Float32Array(N * 3);
  { const r = rng(9);
    for (let i = 0; i < N; i++) {
      pStart[i * 3] = (r() - 0.5) * 16; pStart[i * 3 + 1] = (r() - 0.5) * 22; pStart[i * 3 + 2] = (r() - 0.5) * 12;
      const c = euler(i / N * Math.PI * 2);
      pTarget[i * 3] = SC * c[0]; pTarget[i * 3 + 1] = SC * c[1]; pTarget[i * 3 + 2] = SC * ZS * c[2];
    } }
  const cBlue = new THREE.Color(COL.vocab), cTeal = new THREE.Color(COL.curve), cTmp = new THREE.Color();
  const cOrange = new THREE.Color(COL.target), cPurple = new THREE.Color(COL.weights);
  const hotL = layer();
  const hotW = hotL.add(points(32, 0.62, COL.target, 1));
  const hotP = hotL.add(points(10, 0.8, COL.weights, 1));
  const WORDS = [[0, 32, 52.5, 54.9, 'WATER'], [32, 64, 55.3, 57.7, 'MOLECULE'], [64, 96, 58.1, 60.5, 'HYDROGEN']];
  const SHIFT_IDX = [0, 5, 10, 15, 20, 25, 40, 50, 60, 70];
  const SHIFT_BY = 22;                                    // samples along the curve

  // ================================================================== HUD ==
  // timings are absolute seconds; everything inside the 860px-wide safe column
  const SAFE_W = 780;
  // beat 1
  hudText(['THIS IS WATER.'], 0, 40, { t0: -0.1, t1: 4.3, fin: 0.30, fout: 0.35, slam: true }, { size: 116, maxW: SAFE_W });
  // beat 2
  const paraLines = ['Water is a polar molecule.', 'Two hydrogen atoms bond', 'to one oxygen atom, forming',
    'a chemical compound essential', 'to all known life.'];
  const paraTex = textCanvas(paraLines, { size: 52, weight: 'normal', align: 'left', lineH: 1.5, maxW: 740 });
  const para = hudItem(paraTex, 0, 250, { t0: 4.6, t1: 12.4, fin: 1.6, fout: 0.6, dimAt: 8.2, dimTo: 0.2 });
  const cursorTex = (() => {
    const cv = document.createElement('canvas'); cv.width = cv.height = 96; const g = cv.getContext('2d');
    g.fillStyle = CSS.ink; g.beginPath(); g.arc(48, 48, 9, 0, 7); g.fill();
    g.strokeStyle = 'rgba(234,242,255,0.6)'; g.lineWidth = 3; g.beginPath(); g.arc(48, 48, 26, 0, 7); g.stroke();
    return { cv, w: 96, h: 96 };
  })();
  const cursor = hudItem(cursorTex, 0, 0, { t0: 6.7, t1: 8.4, fin: 0.3, fout: 0.25, free: true });
  const rippleTex = (() => {
    const cv = document.createElement('canvas'); cv.width = cv.height = 128; const g = cv.getContext('2d');
    g.strokeStyle = CSS.target; g.lineWidth = 5; g.beginPath(); g.arc(64, 64, 56, 0, 7); g.stroke();
    return { cv, w: 128, h: 128 };
  })();
  const ripple = hudItem(rippleTex, 0, 0, { t0: 7.6, t1: 8.3, fin: 0.05, fout: 0.65, free: true });
  const curTarget = { x: -paraTex.w / 2 + 92, y: 250 + paraTex.h / 2 - 48 };
  // beat 4 — the equation, then the zoom through it
  const eqRuns = [[{ t: 'z(θ) = ', i: 1 }, { t: 'e', i: 1 }, { t: 'cos θ', s: 0.58, r: 0.55, i: 1 }],
    [{ t: '(cos θ + i sin θ)', i: 1 }]];
  const eqTex = textCanvas(eqRuns, { size: 104, weight: 'normal', font: 'serif', maxW: 740, lineH: 1.5 });
  const EQ_Y = 130;
  const eq = hudItem(eqTex, 0, EQ_Y, { t0: 29.0, t1: 33.6, fin: 0.35, fout: 0.55, slam: true,
    zoomFrom: 31.6, zoomTo: 33.6, zoomK: 4.6,
    // aim the zoom at the e of e^cos, which is the thing being explained
    pivot: [-eqTex.w / 2 + eqTex.starts[0][1] + eqTex.rws[0][1] / 2,
            EQ_Y + eqTex.h / 2 - (eqTex.pad * 0.5 + eqTex.size * 0.62)] });
  // beat 5 — the parametric form
  const e3 = (a, b) => [{ t: `${a} = e`, i: 1 }, { t: 'cos θ', s: 0.6, r: 0.5, i: 1 }, { t: ` ${b}`, i: 1 }];
  hudText([e3('x', 'cos θ'), e3('y', 'sin θ'), [{ t: 'z = sin 2θ', i: 1 }]],
    0, 610, { t0: 43.4, t1: 47.6, fin: 0.7, fout: 0.5 }, { size: 56, weight: 'normal', font: 'serif', align: 'left', lineH: 1.4, maxW: 700 });
  // beat 6 — the three word labels
  const popLbl = WORDS.map((w) => hudText([w[4]], 0, 620, { t0: w[2] + 0.9, t1: w[3] - 0.2, fin: 0.4, fout: 0.5 },
    { size: 70, color: CSS.target, maxW: 700 }));
  hudText(['2,144 points'], 0, 700, { t0: 51.0, t1: 52.2, fin: 0.4, fout: 0.4 }, { size: 52, weight: 'normal', maxW: 700 });
  // beat 7 — the learning loop
  const qTex = textCanvas(['WHAT IS WATER?'], { size: 78, maxW: SAFE_W });
  const qIt = hudItem(qTex, 0, 470, { t0: 64.6, t1: 68.5, fin: 0.05, fout: 0.5, type: [64.6, 66.4] });
  hudText(['Water is a polar molecule,', 'H2O — a chemical compound.'], 0, 270,
    { t0: 66.8, t1: 68.5, fin: 0.9, fout: 0.5 }, { size: 44, weight: 'normal', maxW: 720, lineH: 1.45 });
  const boxes = [['QUESTION', CSS.ink], ['ANSWER', CSS.ink], ['ERROR', CSS.target], ['UPDATE WEIGHTS', CSS.weights]];
  boxes.forEach(([s, c], i) => {
    const info = panelCanvas(520, 96, c, 'rgba(5,7,15,0.82)', (g, w, h) => {
      g.fillStyle = c; g.font = 'bold 40px sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle';
      g.fillText(s, w / 2, h / 2 + 2);
    });
    hudItem(info, 0, 380 - i * 170, { t0: 69.0 + i * 0.3, t1: 76.8, fin: 0.5, fout: 0.6 });
    if (i < 3) hudText(['↓'], 0, 380 - i * 170 - 85, { t0: 70.0 + i * 0.3, t1: 76.8, fin: 0.5, fout: 0.6 },
      { size: 62, color: CSS.ink });
  });
  // beat 8 — the stats
  [['67', 'vocabulary words', CSS.curve], ['32', 'components per word', CSS.vocab],
   ['516/516', 'training questions', CSS.target], ['74.4%', 'accuracy · unseen test', CSS.weights]]
    .forEach(([n, l, c], i) => {
      const t0 = 79.0 + i * 2.4;
      const info = panelCanvas(760, 430, c, 'rgba(5,7,15,0.86)', (g, w, h) => {
        g.textAlign = 'center'; g.textBaseline = 'alphabetic';
        let fs = 200; g.font = `bold ${fs}px sans-serif`;
        const mw = g.measureText(n).width; if (mw > w - 80) { fs = fs * (w - 80) / mw; g.font = `bold ${fs}px sans-serif`; }
        g.fillStyle = c; g.fillText(n, w / 2, h / 2 + fs * 0.26);
        g.fillStyle = CSS.ink; g.font = 'normal 44px sans-serif'; g.fillText(l, w / 2, h - 62);
      });
      hudItem(info, 0, 200, { t0, t1: t0 + 2.1, fin: 0.28, fout: 0.3, slam: true });
    });
  // beat 9 — outro
  hudText(['SMART LOOKUP'], 0, 320, { t0: 89.0, t1: 93.3, fin: 0.9, fout: 0.8 }, { size: 98, maxW: SAFE_W });
  ['From Words to Numbers.', 'From Numbers to Geometry.', 'From Geometry to Learning.'].forEach((s, i) =>
    hudText([s], 0, 130 - i * 78, { t0: 90.0 + i * 0.5, t1: 93.3, fin: 0.7, fout: 0.8 }, { size: 46, weight: 'normal', maxW: 760 }));
  hudText(['TO BE CONTINUED...'], 0, -150, { t0: 91.8, t1: 93.3, fin: 0.6, fout: 0.8 }, { size: 40, color: CSS.curve, maxW: 760 });

  // ============================================================== camera ==
  const orbit = (c, rad, ang, el) => ({
    pos: [c[0] + rad * Math.sin(ang) * Math.cos(el), c[1] + rad * Math.sin(el), c[2] + rad * Math.cos(ang) * Math.cos(el)],
    look: c, fov: 38 });
  const C5 = [1.6, 0.3, 0];
  const shots = [
    { t0: 0, f: (t) => ({ pos: [0, 0, 15 - 1.2 * smooth(t / 5)], look: [0, 0, 0], fov: 38 }) },
    { t0: 4.4, f: (t) => ({ pos: [0.35 * Math.sin(t * 0.35), 0.2 * Math.sin(t * 0.5), 15 + 9.5 * smooth((t - 12.6) / 2.6)],
        look: [0, 0.3, 0], fov: 38 }) },
    { t0: 16.6, f: (t) => orbit([0, 0, 0], 14.8, -0.6 + 0.07 * (t - 16.6), 0.30 + 0.05 * Math.sin((t - 16.6) * 0.4)) },
    { t0: 28.6, f: (t) => ({ pos: [0, 0.3, 22 - 18.5 * smooth((t - 28.6) / 5.4)], look: [0, 0.3, -10], fov: 38 }) },
    { t0: 34.6, f: (t) => {
      const u = t - 41.4;
      const ang = u < 0 ? 0 : -0.7 * smooth(u / 2.5) - 0.03 * Math.max(0, u - 2.5);
      const el = 0.28 * smooth(u / 2.5) + 0.05 * Math.sin(Math.max(0, u) * 0.18);
      return orbit(C5, 21.8 - 1.4 * Math.sin(Math.PI * clamp01((t - 34.6) / 54)), ang, el);
    } },
    { t0: 93.0, f: (t) => ({ pos: [0, 0, 15], look: [0, 0, 0], fov: 38 }) },
  ];
  const BLEND = 1.2;
  function camAt(t) {
    let i = shots.length - 1; while (shots[i].t0 > t) i--;
    let c = shots[i].f(t);
    if (i > 0) {
      const w = smooth((t - shots[i].t0) / BLEND);
      if (w < 1) {
        const p = shots[i - 1].f(t);
        c = { pos: c.pos.map((v, k) => lerp(p.pos[k], v, w)), look: c.look.map((v, k) => lerp(p.look[k], v, w)), fov: lerp(p.fov, c.fov, w) };
      }
    }
    return c;
  }

  // ============================================================== update ==
  function update(t) {
    // camera
    const c = camAt(t);
    camera.position.set(...c.pos); camera.lookAt(...c.look);
    if (camera.fov !== c.fov) { camera.fov = c.fov; camera.updateProjectionMatrix(); }
    dust.rotation.y = t * 0.012;
    dust.material.opacity = 0.5 * (1 - 0.5 * win(t, 17, 28, 1, 1));

    // beat 1 — the dot, and the loop point at the very end
    const pulse = 1 + 0.25 * Math.sin(t * 4.2);
    const aDot = Math.max(win(t, -1, 4.6, 0.01, 0.8), win(t, 93.6, 96, 0.5, 0.01));
    dotL.g.visible = aDot > 0.003;
    dotCore.material.opacity = aDot;
    dotHalo.material.size = 2.4 * pulse * (1 + 0.9 * smooth((t - 0.1) / 1.6));
    dotHalo.material.opacity = 0.30 * aDot * (1 - smooth((t - 0.3) / 1.6));

    // beat 2
    kwL.set(1);
    kwSprites.forEach((s, i) => { s.material.opacity = win(t, 8.6 + i * 0.15, 12.4, 0.5, 0.5); });
    numSprites.forEach((s, i) => { s.material.opacity = win(t, 10.6 + i * 0.15, 12.4, 0.6, 0.5); });
    kwL.g.visible = t > 8.5 && t < 12.9;
    kwL.g.rotation.y = 0.35 * Math.sin((t - 8.6) * 0.5);
    scL.set(win(t, 13.0, 16.4, 0.9, 0.6));
    { const a = scatter.geometry.attributes.position.array, k = clamp01((t - 13.0) / 3.4);
      for (let i = 0; i < 180; i++) a[i] = scBase[i] + scVel[i] * (t - 13.0) * 1.0 + scVel[i] * 5 * k * k;
      scatter.geometry.attributes.position.needsUpdate = true; }

    // beat 3
    uniL.set(win(t, 17.0, 28.0, 0.4, 0.7));
    uniParts.forEach((p) => {
      const a = win(t, p.a, p.b, p.fin || 0.8, 0.9);
      for (const x of p.mats) x.m.opacity = x.b * a;
    });
    axes.forEach((m, i) => place(m, uO, uO.clone().lerp(axEnd[i], smooth((t - 17.4) / 1.2))));

    // beat 5 — the plane, the trace, then the lift into 3D
    const zs = 0.001 + (ZS - 0.001) * smooth((t - 41.4) / 2.6);
    setZ(zs);
    const reveal = clamp01((t - 36.0) / 3.8);
    tube.geometry.setDrawRange(0, Math.floor(reveal * 600) * 36);
    planeL.set(win(t, 35.0, 41.8, 0.8, 0.8));
    radL.set(win(t, 35.8, 41.8, 0.4, 0.7));
    { const tip = curveObj.getPointAt(Math.min(reveal, 0.9999));
      setPts(traceDot, [tip.x, tip.y, tip.z]);
      place(radLine, new THREE.Vector3(0, 0, 0), tip); }
    // the tube: drawn on in beat 5, dimmed while the points arrive, then back up
    const tubeA = reveal > 0 ? Math.max(win(t, 35.8, 93.4, 0.4, 0.8)) : 0;
    const tubeLevel = t < 47.0 ? 1 : lerp(0.34, 1, smooth((t - 50.5) / 2.0));
    curveL.set(tubeA * (t < 47.0 ? 1 : tubeLevel));

    // beat 6/7/8/9 — the 2,144 points
    const fly = smooth((t - 47.0) / 4.4);
    // overall opacity of the cloud across the film
    let cloud = 0;
    if (t >= 47) cloud = 0.95;
    if (t >= 64.0) cloud = lerp(0.95, 0.32, smooth((t - 64.0) / 0.6));
    if (t >= 79.0) cloud = lerp(0.32, 0.20, smooth((t - 79.0) / 0.5));
    if (t >= 88.6) cloud = lerp(0.20, 0.9, smooth((t - 88.6) / 0.6));
    cloud *= smooth((t - 47.0) / 0.5) * smooth((93.7 - t) / 0.8);
    partL.set(cloud);
    if (cloud > 0.003) {
      const pos = P.geometry.attributes.position.array, col = P.geometry.attributes.color.array;
      const shiftW = win(t, 73.0, 76.0, 1.6, 0.9);
      const shiftCol = win(t, 72.0, 76.5, 0.8, 0.7);
      const shiftSet = new Map(SHIFT_IDX.map((k, n) => [k, n]));
      for (let i = 0; i < N; i++) {
        const k = smooth(fly * 1.35 - (i / N) * 0.35);
        let tx = pTarget[i * 3], ty = pTarget[i * 3 + 1], tz = pTarget[i * 3 + 2];
        let word = 0;
        for (const w of WORDS) if (i >= w[0] && i < w[1]) word = win(t, w[2], w[3], 0.9, 0.6);
        cTmp.copy(cBlue).lerp(cTeal, k);
        if (word > 0) cTmp.lerp(cOrange, word);
        if (shiftSet.has(i)) {
          const j = (i + Math.round(SHIFT_BY * shiftW) + N) % N;
          tx = lerp(tx, pTarget[j * 3], 1); ty = lerp(ty, pTarget[j * 3 + 1], 1); tz = lerp(tz, pTarget[j * 3 + 2], 1);
          cTmp.lerp(cPurple, shiftCol);
        }
        pos[i * 3] = pStart[i * 3] + (tx - pStart[i * 3]) * k;
        pos[i * 3 + 1] = pStart[i * 3 + 1] + (ty - pStart[i * 3 + 1]) * k;
        pos[i * 3 + 2] = pStart[i * 3 + 2] + (tz - pStart[i * 3 + 2]) * k;
        col[i * 3] = cTmp.r; col[i * 3 + 1] = cTmp.g; col[i * 3 + 2] = cTmp.b;
      }
      P.geometry.attributes.position.needsUpdate = true;
      P.geometry.attributes.color.needsUpdate = true;
      // overlays: the same points drawn bigger, so a word is a visible stretch of curve
      let wa = 0, w0 = 0;
      for (const w of WORDS) { const a = win(t, w[2], w[3], 0.9, 0.6); if (a > wa) { wa = a; w0 = w[0]; } }
      const hw = hotW.geometry.attributes.position.array;
      for (let j = 0; j < 32; j++) for (let a = 0; a < 3; a++) hw[j * 3 + a] = pos[(w0 + j) * 3 + a];
      hotW.geometry.attributes.position.needsUpdate = true;
      hotW.material.opacity = 0.95 * wa;
      const hp = hotP.geometry.attributes.position.array;
      SHIFT_IDX.forEach((k, j) => { for (let a = 0; a < 3; a++) hp[j * 3 + a] = pos[k * 3 + a]; });
      hotP.geometry.attributes.position.needsUpdate = true;
      hotP.material.opacity = shiftCol;
      hotL.g.visible = wa > 0.003 || shiftCol > 0.003;
    } else hotL.g.visible = false;

    // HUD
    for (const it of items) {
      let a = win(t, it.t0, it.t1, it.fin, it.fout);
      if (it.dimAt !== undefined && t > it.dimAt) a *= lerp(1, it.dimTo, smooth((t - it.dimAt) / 0.4));
      const m = it.mesh;
      m.visible = a > 0.003;
      if (!m.visible) continue;
      m.material.opacity = a;
      let s = 1, px = it.x, py = it.y;
      if (it.slam) { const r = clamp01((t - it.t0) / 0.3); s = 1 + 0.38 * (1 - r) * (1 - r); }
      if (it.zoomFrom !== undefined) {
        const z = smooth((t - it.zoomFrom) / (it.zoomTo - it.zoomFrom));
        s *= 1 + (it.zoomK - 1) * z * z;
        px = it.pivot[0] + (it.x - it.pivot[0]) * s; py = it.pivot[1] + (it.y - it.pivot[1]) * s;
      }
      m.scale.set(s, s, 1);
      m.position.set(px, py, 0);
      if (it.type) {                                         // typed text: wipe in, in character steps
        const n = 14, f = Math.floor(n * clamp01((t - it.type[0]) / (it.type[1] - it.type[0])) + 0.0001) / n;
        const tex = m.material.map; tex.repeat.x = Math.max(f, 0.001); tex.offset.x = 0;
        m.scale.x = Math.max(f, 0.001) * s;
        m.position.x = it.x - it.w / 2 * (1 - Math.max(f, 0.001));
        tex.needsUpdate = false;
      }
    }
    // the cursor travels to the word, then taps it
    { const k = smooth((t - 6.9) / 0.6);
      cursor.mesh.position.set(lerp(210, curTarget.x, k), lerp(430, curTarget.y, k), 0);
      ripple.mesh.position.set(curTarget.x, curTarget.y, 0);
      ripple.mesh.scale.setScalar(0.4 + 2.2 * smooth((t - 7.6) / 0.7)); }
  }
  const api = { scene, camera, hud, hudCam, bloom: 0.5,
    update(t) { update(t); api.bloom = 0.5 - 0.2 * win(t, 8.2, 29.0, 0.8, 0.8); } };
  return api;
}
