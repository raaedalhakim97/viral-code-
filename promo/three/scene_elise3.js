// scene_elise3.js — "THE SHAPE OF FÜR ELISE · III": the complete piece, A B A C A.
// 16:9, 30 fps, from elise4_score.json (the same note list the audio is rendered from).
//
// Five stations float on a ring in one dark space, each facing outward, each showing one part
// of the piece on its own: I the theme as spinning vectors, II the F major part as chord knots,
// III the theme's return as spirals streaming back in time, IV the chord part's pounding A,
// V the theme one last time. At every seam the camera lifts off, flies along the ring and lands
// on the next station; at the end it rises over the ring and shows all five together.
// Real notes spin far too fast to see: every frequency is divided by SLOW, so all ratios stay exact.
import { Line2 } from 'three/addons/lines/Line2.js';
import { LineGeometry } from 'three/addons/lines/LineGeometry.js';
import { LineMaterial } from 'three/addons/lines/LineMaterial.js';

export const FPS = 30;
export const DURATION = 147.0;

const BG = 0x05070f;
const COL = { RH: 0xffd166, LH: 0x2ee6c8, STR: 0x9b5cf6, VC: 0x3b8cff, HN: 0xff8a2b, ink: 0xeaf2ff };
const CSS = { ink: '#EAF2FF', gold: '#FFD166', tq: '#2EE6C8', vi: '#9B5CF6', dim: '#8A94A6' };
const SLOW = 110, T0 = 2.5, TAU = 0.9, PEDAL = 0.9;

const clamp01 = (x) => Math.min(1, Math.max(0, x));
const ease = (x) => { x = clamp01(x); return x * x * (3 - 2 * x); };
const easeIO = (x) => { x = clamp01(x); return x < 0.5 ? 4 * x * x * x : 1 - (-2 * x + 2) ** 3 / 2; };
const easeOutBack = (x) => { x = clamp01(x); const c = 1.6; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2; };
const win = (t, a, b, fi = 0.5, fo = 0.5) => ease((t - a) / fi) * ease((b - t) / fo);
const hz = (m) => 440 * 2 ** ((m - 69) / 12);
const fvis = (m) => hz(m) / SLOW;

const SVGS = ['eq_note', 'eq_beat', 'eq_chord', 'eq_fourier'];
export async function buildAsync(THREE, W, H) {
  const svg = {};
  for (const name of SVGS) {
    const img = new Image(); img.src = `/tex_elise/${name}.svg`; await img.decode();
    const cv = document.createElement('canvas'); cv.width = Math.ceil(img.width * 7 / 1.333); cv.height = Math.ceil(img.height * 7 / 1.333);
    cv.getContext('2d').drawImage(img, 0, 0, cv.width, cv.height); svg[name] = cv;
  }
  const score = await (await fetch('/elise4_score.json')).json();
  return build(THREE, W, H, svg, score);
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

export function build(THREE, W, H, svg, score) {
  const A = THREE.AdditiveBlending;
  const scene = new THREE.Scene(); scene.background = new THREE.Color(BG);
  scene.fog = new THREE.FogExp2(BG, 0.018);
  const camera = new THREE.PerspectiveCamera(35, W / H, 0.05, 900);
  const HW = 960, HH = 540;
  const hud = new THREE.Scene(); const hudCam = new THREE.OrthographicCamera(-HW, HW, HH, -HH, -10, 10);
  const C = (h) => new THREE.Color(h), cTmp = new THREE.Color(), v3 = new THREE.Vector3();

  // ------------------------------------------------------------ the score and its landmarks
  const EV = score.events.map((e) => ({ ...e, t: e.t + T0 }));
  const BARS = score.bars.map((b) => b + T0);
  const secT = (key) => score.sections.find((s) => s.name.includes(key)).t + T0;
  const barIdx = (tt) => BARS.findIndex((b) => Math.abs(b - tt) < 1e-3);
  const S1 = 2.5, S2 = secT('Second part'), S3 = secT('Theme returns'), S4 = secT('chord part'), SW = secT('The sweep'),
        S5 = secT('last time'), SEND = secT('The end');
  const iS2 = barIdx(S2), iS4 = barIdx(S4);
  // the hand-crossing (bars 12-14) in the theme: four times in the piece; and the turns of the camera inside station I
  const CROSS = BARS.filter((b, i) => EV.some((e) => e.voice === 'LH' && e.midi >= 75 && e.t >= b - 1e-3 && e.t < b + 0.3))
    .filter((b, i, arr) => i === 0 || b - arr[i - 1] > 2.5);           // one per crossing (it spans two bars)
  for (const e of EV) {
    const next = EV.find((o) => o.midi === e.midi && o.voice === e.voice && o.t > e.t + 1e-6);
    e.sustained = e.voice !== 'RH' && e.voice !== 'LH';
    e.off = Math.min(next ? next.t : 1e9, e.t + e.dur + (e.sustained ? 0.25 : PEDAL));
  }
  const env = (e, s) => { if (s < e.t) return 0; const rel = clamp01(1 - (s - e.off) / 0.12);
    return (e.sustained ? ease((s - e.t) / 0.15) : Math.exp(-(s - e.t) / TAU)) * rel; };
  const theta = (e, s) => 2 * Math.PI * fvis(e.midi) * (s - e.t);
  const NOTES = EV.filter((e) => e.voice !== 'DR');
  const active = (s, voices, lo = -1, hi = 1e9) => NOTES.filter((e) => voices.includes(e.voice) && e.t >= lo && e.t < hi && e.t <= s && s < e.off + 0.12);

  // ------------------------------------------------------------ helpers
  const sprite = (() => { const cv = document.createElement('canvas'); cv.width = cv.height = 128; const g = cv.getContext('2d');
    const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(255,255,255,1)');
    gr.addColorStop(0.3, 'rgba(255,255,255,0.5)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, 128, 128);
    return new THREE.CanvasTexture(cv); })();
  function fatLine(n, width, parent = scene) {
    const g = new LineGeometry(); const z = new Float32Array(n * 3); g.setPositions(z); g.setColors(z);
    const m = new LineMaterial({ color: 0xffffff, linewidth: width, vertexColors: true, transparent: true, blending: A, depthWrite: false });
    m.resolution.set(W, H);
    const l = new Line2(g, m); l.frustumCulled = false; l.userData = { n, pos: new Float32Array(n * 3), col: new Float32Array(n * 3) }; parent.add(l); return l;
  }
  function setLine(l, fnPos, fnCol) {
    const { n, pos, col } = l.userData;
    for (let j = 0; j < n; j++) { const u = j / (n - 1); const p = fnPos(u, j); pos[3 * j] = p.x; pos[3 * j + 1] = p.y; pos[3 * j + 2] = p.z;
      const c = fnCol(u, j); col[3 * j] = c.r; col[3 * j + 1] = c.g; col[3 * j + 2] = c.b; }
    l.geometry.setPositions(pos); l.geometry.setColors(col);
  }
  const UP = new THREE.Vector3(0, 1, 0);
  const coneGeo = new THREE.ConeGeometry(0.075, 0.22, 14); coneGeo.translate(0, -0.11, 0);
  function arrow(parent, width = 3) {
    const shaft = fatLine(2, width, parent);
    const head = new THREE.Mesh(coneGeo, new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, blending: A, depthWrite: false }));
    parent.add(head);
    return {
      set(a, b, col, k = 1) {
        const d = new THREE.Vector3(b.x - a.x, b.y - a.y, b.z - a.z), len = d.length(); const on = len > 0.006 && k > 0.003;
        shaft.visible = head.visible = on; if (!on) return;
        cTmp.copy(col).multiplyScalar(k);
        setLine(shaft, (u) => v3.set(a.x + (b.x - a.x) * u, a.y + (b.y - a.y) * u, a.z + (b.z - a.z) * u), () => cTmp);
        head.position.copy(b); head.quaternion.setFromUnitVectors(UP, d.divideScalar(len));
        head.material.color.copy(col).multiplyScalar(k); head.scale.setScalar(Math.min(1, len / 0.3));
      },
      hide() { shaft.visible = head.visible = false; },
    };
  }
  const dot = (parent, size) => { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: sprite, color: 0xffffff, transparent: true, blending: A, depthWrite: false }));
    s.scale.setScalar(size); parent.add(s); return s; };
  function label3d(parent, str, o, pos, scale) {
    const cv = textCanvas(str, o); const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace;
    const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: t, transparent: true, depthWrite: false, fog: true }));
    s.scale.set(scale * cv.width / cv.height, scale, 1); s.position.copy(pos); parent.add(s); return s;
  }

  // ------------------------------------------------------------ the ring of stations
  const CENTER = new THREE.Vector3(0, 0, 0), R = 34, NST = 5;
  const stations = Array.from({ length: NST }, (_, i) => {
    const a = (i / NST) * Math.PI * 2, g = new THREE.Group();
    g.position.set(CENTER.x + R * Math.sin(a), 0, CENTER.z + R * Math.cos(a)); g.rotation.y = a;   // local +z points outward
    scene.add(g); g.updateMatrixWorld(true); return { g, a };
  });
  // the path between them: a faint ring under the stations, with a light that runs ahead during each flight
  const RING_Y = -5.2, ringLine = fatLine(361, 1.6), runner = dot(scene, 1.4);
  // each station's grid: a big x-y plane, edge to edge in its face-on frame
  const PX = 7.6, PY = 4.2;
  function grid(st) {
    const g = new THREE.Group(); st.g.add(g);
    const lines = [];
    for (let i = 0; i < 15; i++) lines.push({ l: fatLine(2, 1.0, g), a: [-7 + i, -PY], b: [-7 + i, PY], w: 0.07 });
    for (let i = 0; i < 9; i++) lines.push({ l: fatLine(2, 1.0, g), a: [-PX, -4 + i], b: [PX, -4 + i], w: 0.07 });
    lines.push({ l: fatLine(2, 2.0, g), a: [-PX, 0], b: [PX, 0], w: 0.42 }, { l: fatLine(2, 2.0, g), a: [0, -PY], b: [0, PY], w: 0.42 });
    return { g, lines };
  }
  function drawGrid(G, t, t0, k, pulse) {
    const d = easeIO((t - t0) / 1.8);
    G.lines.forEach((L) => { cTmp.copy(C(COL.ink)).multiplyScalar((L.w + (L.w > 0.3 ? 0.25 : 0.06) * pulse) * k);
      setLine(L.l, (u) => v3.set((L.a[0] + (L.b[0] - L.a[0]) * u) * (L.a[1] === L.b[1] ? d : 1), (L.a[1] + (L.b[1] - L.a[1]) * u) * (L.a[0] === L.b[0] ? d : 1), 0), () => cTmp); });
  }
  function beatPulse(t) { let p = 0; for (const b of BARS) { const a = t - b; if (a >= 0 && a < 1.2) p = Math.max(p, ease(a / 0.03) * Math.exp(-a / 0.28)); } return p; }

  // ------------------------------------------------------------ station I and V: the theme as tip-to-tail vectors
  function makeRig(st, origin) {
    const g = new THREE.Group(); st.g.add(g);
    return { g, origin, arrows: Array.from({ length: 10 }, () => arrow(g, 3.4)), wave: fatLine(800, 3.0, g), proj: fatLine(2, 1.2, g), tip: dot(g, 0.28), ring: fatLine(129, 1.4, g) };
  }
  const RNOTE = 1.0, WSPAN = 1.25;
  const rigTip = (R0, s, lo, hi) => { const act = active(s, ['RH', 'LH'], lo, hi).sort((a, b) => a.t - b.t).slice(-10); const p = R0.origin.clone();
    for (const e of act) { const r = RNOTE * env(e, s), th = theta(e, s); p.x += r * Math.cos(th); p.y += r * Math.sin(th); } return p; };
  const ySig = (s, lo, hi) => active(s, ['RH', 'LH'], lo, hi).reduce((acc, e) => acc + RNOTE * env(e, s) * Math.sin(theta(e, s)), 0);
  function drawRig(R0, t, k, lo, hi) {
    R0.g.visible = k > 0.003; if (!R0.g.visible) return;
    const O = R0.origin;
    cTmp.copy(C(COL.ink)).multiplyScalar(0.16 * k);
    setLine(R0.ring, (u) => v3.set(O.x + RNOTE * Math.cos(2 * Math.PI * u), O.y + RNOTE * Math.sin(2 * Math.PI * u), 0), () => cTmp);
    const act = active(t, ['RH', 'LH'], lo, hi).sort((a, b) => a.t - b.t);
    let p = O.clone();
    R0.arrows.forEach((ar, i) => {
      const e = act[act.length - R0.arrows.length + i] ?? null; if (!e) { ar.hide(); return; }
      const r = RNOTE * env(e, t), th = theta(e, t), q = new THREE.Vector3(p.x + r * Math.cos(th), p.y + r * Math.sin(th), 0);
      ar.set(p, q, C(COL[e.voice]), k * (0.35 + 0.65 * env(e, t))); p = q;
    });
    R0.tip.position.copy(p); R0.tip.material.opacity = k * (act.length ? 1 : 0);
    const WX0 = O.x + 1.9, WX1 = 7.2;
    setLine(R0.wave, (u) => v3.set(WX0 + (WX1 - WX0) * u, O.y + 0.85 * ySig(t - u * WSPAN, lo, hi), 0),
      (u) => cTmp.copy(C(COL.RH)).multiplyScalar(k * (0.15 + 0.85 * (1 - u) ** 2)));
    cTmp.copy(C(COL.ink)).multiplyScalar(0.25 * k);
    setLine(R0.proj, (u) => v3.set(p.x + (WX0 - p.x) * u, p.y + (O.y + 0.85 * ySig(t, lo, hi) - p.y) * u, 0), () => cTmp);
  }

  // ------------------------------------------------------------ stations II and IV: chords as one point moving in 3D
  const STR_EV = NOTES.filter((e) => e.voice === 'STR');
  const CHORDS = []; { const byT = new Map(); for (const e of STR_EV) { const kk = e.t.toFixed(3); if (!byT.has(kk)) byT.set(kk, []); byT.get(kk).push(e); }
    for (const grp of byT.values()) { if (grp.length < 3) continue; grp.sort((x, y) => x.midi - y.midi); const g3 = grp.slice(0, 3);
      CHORDS.push({ notes: g3.map((e) => e.midi), t: g3[0].t, off: Math.min(...g3.map((e) => e.off)) }); } }
  CHORDS.sort((x, y) => x.t - y.t);
  const RK = 2.3, PH = [0, Math.PI / 2, Math.PI / 4], SPAN = 3.0, KNOT_Y = 0.7, AXC = [COL.VC, COL.STR, COL.ink];
  const knotOf = (notes, s, out = new THREE.Vector3()) => out.set(...notes.map((m, i) => RK * Math.sin(2 * Math.PI * fvis(m) * s + PH[i])));
  function makeKnot(st) {
    const g = new THREE.Group(); g.position.y = KNOT_Y; st.g.add(g);
    return { g, K: [0, 1].map(() => ({ full: fatLine(900, 1.5, g), trail: fatLine(200, 3.6, g), pen: dot(g, 0.32), vec: arrow(g, 2.6), comp: [0, 1, 2].map(() => fatLine(2, 2.0, g)) })),
      zAxis: fatLine(2, 1.6, g), zLbl: label3d(g, 'z  (the third note)', { size: 40, weight: '400', color: CSS.vi }, new THREE.Vector3(0.2, 0.3, 3.4), 0.26) };
  }
  function drawKnot(KN, t, k, lo, hi, zk, hold = false) {
    KN.g.visible = k > 0.003; if (!KN.g.visible) return;
    let live = CHORDS.filter((c) => c.t >= lo && c.t < hi && c.t <= t && (hold || t < c.off + 0.5)).slice(-2);
    KN.K.forEach((K, i) => {
      const ch = live[live.length - 1 - i];
      const show = !!ch && !(hold && i > 0);
      [K.full, K.trail, K.pen].forEach((o) => (o.visible = show)); K.comp.forEach((l) => (l.visible = show)); if (!show) { K.vec.hide(); return; }
      const age = t - ch.t, grow = easeOutBack(age / 0.45), fade = (hold ? 1 : clamp01(1 - (t - ch.off) / 0.5)) * k;
      const sc = 0.35 + 0.65 * grow, lit = fade * (i === 0 ? 1 : 0.5), tt = hold ? ch.off : t;
      cTmp.copy(C(COL.STR)).multiplyScalar(0.5 * lit);
      setLine(K.full, (u) => knotOf(ch.notes, u * SPAN, v3).multiplyScalar(sc), () => cTmp);
      setLine(K.trail, (u) => knotOf(ch.notes, tt - u * 0.6, v3).multiplyScalar(sc), (u) => cTmp.copy(C(COL.ink)).lerp(C(COL.STR), 0.3).multiplyScalar(lit * (1 - u) ** 1.4));
      const p = knotOf(ch.notes, tt).multiplyScalar(sc);
      K.pen.position.copy(p); K.pen.material.opacity = lit; K.vec.set(new THREE.Vector3(), p, C(COL.ink), lit * 0.85);
      K.comp.forEach((l, j) => { cTmp.copy(C(AXC[j])).multiplyScalar(0.85 * lit);
        setLine(l, (u) => { const q = new THREE.Vector3(); q.setComponent(j, p.getComponent(j) * u); return q; }, () => cTmp); });
    });
    cTmp.copy(C(COL.STR)).multiplyScalar(0.55 * zk);
    setLine(KN.zAxis, (u) => v3.set(0, 0, -3.2 + 6.4 * u), () => cTmp); KN.zLbl.material.opacity = 0.9 * zk;
  }

  // ------------------------------------------------------------ station III (and IV's sweep): spirals streaming back in time
  const pitchX = (m) => (m - 64) * 0.17, RAD = { RH: 0.2, LH: 0.27 };
  function makeSpirals(st, lo, hi, zs, laneY) {
    const list = NOTES.filter((e) => (e.voice === 'RH' || e.voice === 'LH') && e.t >= lo && e.t < hi).map((e) => {
      const T = e.off + 0.12 - e.t, n = Math.max(8, Math.ceil(T * fvis(e.midi) * 26));
      const pos = new Float32Array(n * 3), col = new Float32Array(n * 3), c = C(COL[e.voice]);
      for (let j = 0; j < n; j++) {
        const s = e.t + T * j / (n - 1), a = env(e, s), r = RAD[e.voice] * (0.25 + 0.75 * a), th = theta(e, s);
        pos.set([pitchX(e.midi) + r * Math.cos(th), laneY + r * Math.sin(th), -(s - lo) * zs], 3 * j);
        const b = 0.1 + 0.62 * a; col.set([c.r * b, c.g * b, c.b * b], 3 * j);
      }
      const g = new LineGeometry(); g.setPositions(pos); g.setColors(col);
      const m = new LineMaterial({ color: 0xffffff, linewidth: e.voice === 'RH' ? 2.4 : 2.0, vertexColors: true, transparent: true, blending: A, depthWrite: false });
      m.resolution.set(W, H);
      const l = new Line2(g, m); l.frustumCulled = false; st.g.add(l); return { e, l, n, T };
    });
    return { list, lo, zs, laneY };
  }
  function drawSpirals(SP, t, k, hist) {
    for (const s of SP.list) {
      const on = k > 0.003 && s.e.t <= t && t - s.e.t < hist; s.l.visible = on; if (!on) continue;
      s.l.geometry.instanceCount = Math.max(1, Math.min(s.n - 1, Math.floor((t - s.e.t) / s.T * (s.n - 1))));
      s.l.material.opacity = k;
    }
  }

  // ------------------------------------------------------------ station IV: the pounding A, a ring on every strike
  function makePedal(st) {
    const g = new THREE.Group(); st.g.add(g);
    return { g, arrow: arrow(g, 4.0), tip: dot(g, 0.42), rings: Array.from({ length: 36 }, () => fatLine(97, 2.0, g)),
      lbl: label3d(g, 'A  ·  110 Hz', { size: 40, weight: '700', color: CSS.tq }, new THREE.Vector3(0, -2.05, 0), 0.3) };
  }
  const LH_C = NOTES.filter((e) => e.voice === 'LH' && e.t >= S4 && e.t < SW);
  const STRIKES = []; { let last = -1; for (const e of LH_C) if (e.t - last > 0.01) { STRIKES.push(e); last = e.t; } }
  function drawPedal(PD, t, k) {
    PD.g.visible = k > 0.003; if (!PD.g.visible) return;
    const e = active(t, ['LH'], S4, SW).sort((a, b) => a.midi - b.midi)[0];
    if (e) { const r = 1.7 * (0.3 + 0.7 * env(e, t)), th = theta(e, t), q = new THREE.Vector3(r * Math.cos(th), r * Math.sin(th), 0);
      PD.arrow.set(new THREE.Vector3(), q, C(COL.LH), k); PD.tip.position.copy(q); PD.tip.material.opacity = k * env(e, t);
    } else { PD.arrow.hide(); PD.tip.material.opacity = 0; }
    PD.lbl.material.opacity = k * win(t, S4 + 0.5, S4 + 6, 0.6, 0.8);
    let ri = 0;
    const ring = (age, life, r0, r1, col, w) => { if (ri >= PD.rings.length || age < 0 || age > life) return; const l = PD.rings[ri++], u = age / life;
      const Rr = r0 + (r1 - r0) * (1 - (1 - u) ** 2.4), a = (1 - u) ** 2 * k * w; l.visible = true; cTmp.copy(C(col)).multiplyScalar(a);
      setLine(l, (vv) => v3.set(Rr * Math.cos(2 * Math.PI * vv), Rr * Math.sin(2 * Math.PI * vv), 0), () => cTmp); };
    for (let i = STRIKES.length - 1; i >= 0 && ri < 24; i--) { const age = t - STRIKES[i].t; if (age > 1.0) continue; if (age < 0) continue; ring(age, 1.0, 0.4, 3.8, COL.LH, 0.55); }
    for (const ch of CHORDS) if (ch.t >= S4 && ch.t < SW) ring(t - ch.t, 1.6, 0.8, 7.5, COL.STR, 0.9);
    for (; ri < PD.rings.length; ri++) PD.rings[ri].visible = false;
  }

  // ------------------------------------------------------------ build the five stations
  const [st1, st2, st3, st4, st5] = stations;
  const G = stations.map(grid);
  const rig1 = makeRig(st1, new THREE.Vector3(-4.9, 0.9, 0)), rig5 = makeRig(st5, new THREE.Vector3(-4.9, 0.9, 0));
  const knot2 = makeKnot(st2), knot4 = makeKnot(st4);
  const ZS3 = 1.6, spir3 = makeSpirals(st3, S3, S4, ZS3, -1.2);
  const ZSW = 2.4, spirW = makeSpirals(st4, SW, S5, ZSW, -3.0);
  const ped4 = makePedal(st4);
  const TITLES = ['I  ·  THE THEME', 'II  ·  THE SECOND PART', 'III  ·  THE THEME RETURNS', 'IV  ·  THE CHORD PART', 'V  ·  THE THEME, ONE LAST TIME'];
  const stLabels = stations.map((st, i) => label3d(st.g, TITLES[i], { size: 48, spacing: 8, color: CSS.dim }, new THREE.Vector3(0, -4.9, 0.4), 0.55));

  // ------------------------------------------------------------ the camera: station shots, flights between them
  const P = (x, y, z, lx, ly, lz, fov = 35) => ({ pos: new THREE.Vector3(x, y, z), look: new THREE.Vector3(lx, ly, lz), fov });
  const face = (d, fov = 35, lx = 0, ly = 0) => P(lx, ly, d, lx, ly, 0, fov);
  const orbit = (ang, r, y, lz = -1.2, fov = 35) => P(r * Math.sin(ang), y, r * Math.cos(ang), 0, KNOT_Y * 0.5, lz, fov);
  const drift = (t, t0, a = 0.035) => a * (t - t0);
  const bI = (i) => BARS[i];
  // station I turns its view at each repeat: face, a 3/4 angle, closer, the other side
  const SHOT = [
    // I: the theme (bars 1-21 with repeats)
    { st: 0, t: 0.0, b: 0.1, f: (t) => face(16.5 - 2.2 * easeIO(t / 3)) },
    { st: 0, t: bI(8) - 0.4, b: 2.0, f: (t) => P(6.5 + drift(t, bI(8), -0.05), 1.6, 12.0, 0.6, 0.4, 0) },
    { st: 0, t: bI(16) - 0.4, b: 2.0, f: (t) => face(11.8 + drift(t, bI(16), 0.04), 35, -0.6, 0.6) },
    { st: 0, t: bI(30) - 0.4, b: 2.0, f: (t) => P(-6.8 + drift(t, bI(30), 0.05), 2.4, 11.6, -0.3, 0.4, 0) },
    // II: the second part
    { st: 1, t: S2, b: 0.0, f: (t) => face(14.0 - 0.9 * ease((t - S2) / 4), 35, 0, 0.5) },
    { st: 1, t: bI(iS2 + 4) - 1.1, b: 2.3, f: (t) => orbit(0.95 + drift(t, bI(iS2 + 4)), 13.6, 3.4) },
    { st: 1, t: bI(iS2 + 7) - 0.4, b: 2.0, f: (t) => orbit(1.15 + drift(t, bI(iS2 + 7), 0.12), 10.8, 2.0) },
    { st: 1, t: bI(iS2 + 11) - 0.6, b: 1.7, f: (t) => face(13.6, 35, 0, 0.5) },
    // III: the theme returns, the corridor of spirals
    { st: 2, t: S3, b: 0.0, f: (t) => { const z = -(t - S3) * ZS3; return P(-1.0, 1.4, z - 6.2, 0.8, -0.8, z + 3.0); } },
    { st: 2, t: S3 + 9.5, b: 2.2, f: (t) => { const z = -(t - S3) * ZS3; return P(5.5, 0.6, z - 4.0, 0.3, -1.0, z + 4.5); } },
    { st: 2, t: S3 + 16.0, b: 2.2, f: (t) => { const z = -(t - S3) * ZS3; return P(-3.5, 4.2, z - 5.0, 0.5, -1.2, z + 3.5); } },
    // IV: the chord part
    { st: 3, t: S4, b: 0.0, f: (t) => { const a = easeIO((t - S4) / 1.2); return face(9.5 + 12 * a, 54 - 24 * a, 0, 0.3); } },
    { st: 3, t: bI(iS4 + 1) + 0.5, b: 1.2, f: (t) => face(21.5 - 4.5 * ease((t - bI(iS4 + 1)) / 4.0), 30, 0, 0.3) },
    { st: 3, t: bI(iS4 + 5) - 0.4, b: 2.3, f: (t) => P(10.8 - drift(t, bI(iS4 + 5), 0.12), 2.4, 7.8, 0, 0.5, -1.2) },
    { st: 3, t: bI(iS4 + 9) - 0.2, b: 1.0, f: (t) => face(10.6 + 0.6 * ease((t - bI(iS4 + 9)) / 2.0), 35, 0, 0.4) },
    { st: 3, t: bI(iS4 + 9) + 2.0, b: 2.0, f: (t) => P(-9.8 + drift(t, bI(iS4 + 9), 0.1), 5.2, 8.2, 0, 0.4, -1.0) },
    { st: 3, t: bI(iS4 + 13) - 0.2, b: 2.2, f: (t) => P(1.5, 12.5 + drift(t, bI(iS4 + 13), 0.25), 7.5, 0, 0.3, -1.8) },
    { st: 3, t: SW - 0.4, b: 1.6, f: (t) => { const act = active(t, ['RH'], SW, S5).sort((a, b) => b.t - a.t); const x = act.length ? pitchX(act[0].midi) : 0;
        const z = -(t - SW) * ZSW; return P(x * 0.8 - 4.2, -1.8 + 0.2 * (x + 4), z + 7.0, x * 0.9, -2.0, z - 2.5); } },
    // V: the theme, one last time
    { st: 4, t: S5, b: 0.0, f: (t) => face(14.0 - 0.8 * ease((t - S5) / 6), 35, 0, 0.3) },
    { st: 4, t: S5 + 9.0, b: 2.0, f: (t) => P(-6.0 + drift(t, S5 + 9, 0.05), 1.8, 12.0, -0.4, 0.4, 0) },
    { st: 4, t: S5 + 17.0, b: 2.0, f: (t) => face(13.2 + drift(t, S5 + 17, -0.05), 35, -0.8, 0.5) },
  ];
  // flights: [start, end, from station, to station]; each lands on the first bar of the next part
  const FLY = [[S2 - 1.9, S2 + 0.25, 0, 1], [S3 - 1.4, S3 + 0.6, 1, 2], [S4 - 1.6, S4 + 0.4, 2, 3], [S5 - 1.3, S5 + 0.7, 3, 4]];
  const REVEAL = [SEND + 0.6, SEND + 4.6];
  const toWorld = (st, pose) => ({ pos: pose.pos.clone().applyMatrix4(st.g.matrixWorld), look: pose.look.clone().applyMatrix4(st.g.matrixWorld), fov: pose.fov });
  function stationPose(stI, t) {
    const list = SHOT.filter((s) => s.st === stI); let i = 0; while (i + 1 < list.length && list[i + 1].t <= t) i++;
    const cur = list[i].f(t); if (i === 0) return toWorld(stations[stI], cur);
    const prev = list[i - 1].f(t), a = list[i].b > 0 ? easeIO((t - list[i].t) / list[i].b) : 1;
    return toWorld(stations[stI], { pos: prev.pos.clone().lerp(cur.pos, a), look: prev.look.clone().lerp(cur.look, a), fov: prev.fov + (cur.fov - prev.fov) * a });
  }
  const stationAt = (t) => (t < S2 ? 0 : t < S3 ? 1 : t < S4 ? 2 : t < S5 ? 3 : 4);
  // high and oblique, not straight down: the stations stand upright, so from above they would be edge-on
  const overhead = { pos: stations[4].g.position.clone().setY(0).normalize().multiplyScalar(80).add(new THREE.Vector3(0, 34, 0)), look: CENTER.clone().add(new THREE.Vector3(0, -3, 0)), fov: 50 };
  let flying = null;
  function camAt(t) {
    flying = null;
    for (const [f0, f1, a, b] of FLY) if (t >= f0 && t < f1) {
      const u = easeIO((t - f0) / (f1 - f0)), A0 = stationPose(a, t), B0 = stationPose(b, t);     // both live, so take-off and landing are seamless
      // lift off and swing outward along the ring: a quadratic curve through a raised midpoint
      const mid = A0.pos.clone().add(B0.pos).multiplyScalar(0.5); const out = mid.clone().sub(CENTER).setY(0).normalize();
      mid.addScaledVector(out, 14).add(new THREE.Vector3(0, 9, 0));
      const pos = A0.pos.clone().multiplyScalar((1 - u) ** 2).addScaledVector(mid, 2 * u * (1 - u)).addScaledVector(B0.pos, u * u);
      const lu = easeIO((u - 0.15) / 0.7);
      flying = { a, b, u };
      return { pos, look: A0.look.clone().lerp(B0.look, lu), fov: A0.fov + (B0.fov - A0.fov) * u };
    }
    const base = stationPose(stationAt(t), t);
    if (t >= REVEAL[0]) { const u = easeIO((t - REVEAL[0]) / (REVEAL[1] - REVEAL[0]));
      return { pos: base.pos.clone().lerp(overhead.pos, u), look: base.look.clone().lerp(overhead.look, u), fov: base.fov + (overhead.fov - base.fov) * u }; }
    return base;
  }

  // ------------------------------------------------------------ note entrances: a flash of glow and lit smoke (world space)
  const hash = (i, k) => { let h = Math.imul(i * 374761393 + k * 668265263, 1274126177) >>> 0; h = Math.imul(h ^ (h >>> 13), 1103515245) >>> 0; return ((h ^ (h >>> 16)) >>> 0) / 4294967296; };
  function smokeTex(seed) {
    const N = 192, cv = document.createElement('canvas'); cv.width = cv.height = N; const g = cv.getContext('2d'), img = g.createImageData(N, N);
    const gridf = (x, y, o) => hash(((x & 255) + 256 * (y & 255)) + 65536 * o, seed);
    const vnoise = (x, y, o) => { const xi = Math.floor(x), yi = Math.floor(y), fx = x - xi, fy = y - yi, sx = fx * fx * (3 - 2 * fx), sy = fy * fy * (3 - 2 * fy);
      const a = gridf(xi, yi, o), b = gridf(xi + 1, yi, o), c = gridf(xi, yi + 1, o), d = gridf(xi + 1, yi + 1, o);
      return a + (b - a) * sx + (c - a) * sy + (a - b - c + d) * sx * sy; };
    for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
      let n = 0, amp = 0.5, fr = 3 / N; for (let o = 0; o < 5; o++) { n += amp * vnoise(x * fr, y * fr, o); amp *= 0.5; fr *= 2; }
      const r = Math.hypot(x - N / 2, y - N / 2) / (N / 2), fall = Math.max(0, 1 - r) ** 1.8, a = Math.max(0, Math.min(1, (n - 0.32) * 2.2)) * fall;
      const j = 4 * (y * N + x); img.data[j] = img.data[j + 1] = img.data[j + 2] = 255; img.data[j + 3] = Math.round(255 * a);
    }
    g.putImageData(img, 0, 0); return new THREE.CanvasTexture(cv);
  }
  const SMOKE_TEX = [11, 23, 37, 51].map(smokeTex);
  const haloTex = (() => { const cv = document.createElement('canvas'); cv.width = cv.height = 256; const g = cv.getContext('2d');
    const gr = g.createRadialGradient(128, 128, 0, 128, 128, 128);
    gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.18, 'rgba(255,255,255,0.55)'); gr.addColorStop(0.5, 'rgba(255,255,255,0.12)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 256, 256); return new THREE.CanvasTexture(cv); })();
  const pool = (n, texOf) => Array.from({ length: n }, (_, i) => { const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: texOf(i), transparent: true,
    blending: A, depthWrite: false, depthTest: false })); sp.visible = false; scene.add(sp); return sp; });
  const smokePool = pool(360, (i) => SMOKE_TEX[i % 4]), flashPool = pool(56, () => haloTex);
  const SMOKE_LIFE = 2.2, FLASH_LIFE = 0.9;
  const W_ = (st, p) => p.clone().applyMatrix4(st.g.matrixWorld);
  function birth(e) {
    const t = e.t;
    if (t < S2) { if (e.voice !== 'RH' && e.voice !== 'LH') return null; return { kind: 'rig', st: 0, rig: rig1, lo: 0, hi: S2, puffs: e.voice === 'RH' ? 3 : 2 }; }
    if (t < S3) { if (e.voice === 'STR') { const ch = CHORDS.find((c) => Math.abs(c.t - t) < 1e-3 && c.notes[0] === e.midi); if (!ch) return null;
        return { kind: 'knot', st: 1, p: W_(st2, knotOf(ch.notes, t).add(v3.set(0, KNOT_Y, 0))), puffs: 6 }; } return null; }
    if (t < S4) { if (e.voice !== 'RH' && e.voice !== 'LH') return null;
      return { kind: 'lane', st: 2, p: W_(st3, new THREE.Vector3(pitchX(e.midi) + RAD[e.voice], -1.2, -(t - S3) * ZS3)), puffs: e.voice === 'RH' ? 3 : 2 }; }
    if (t < S5) {
      if (t >= SW) { if (e.voice !== 'RH') return null; return { kind: 'lane', st: 3, p: W_(st4, new THREE.Vector3(pitchX(e.midi) + RAD.RH, -3.0, -(t - SW) * ZSW)), puffs: 2 }; }
      if (e.voice === 'STR') { const ch = CHORDS.find((c) => Math.abs(c.t - t) < 1e-3 && c.notes[0] === e.midi); if (!ch) return null;
        return { kind: 'knot', st: 3, p: W_(st4, knotOf(ch.notes, t).add(v3.set(0, KNOT_Y, 0))), puffs: 6, big: true }; }
      if (e.voice === 'LH' && STRIKES.includes(e) && LH_C.indexOf(e) % 6 === 0) return { kind: 'pedal', st: 3, p: W_(st4, new THREE.Vector3()), puffs: 2 };
      return null;
    }
    if (e.voice !== 'RH' && e.voice !== 'LH') return null;
    return { kind: 'rig', st: 4, rig: rig5, lo: S5, hi: 999, puffs: e.voice === 'RH' ? 3 : 2 };
  }
  NOTES.forEach((e, i) => { e.i = i; e.birth = birth(e); if (e.birth && e.birth.kind === 'rig') { const B = e.birth;
    B.p = W_(stations[B.st], rigTip(B.rig, e.t, B.lo, B.hi)); } });
  const BORN = NOTES.filter((e) => e.birth).sort((a, b) => a.t - b.t);
  function drawEntrances(t, kSt) {
    let si = 0, fi = 0; const lo = t - SMOKE_LIFE;
    for (const e of BORN) {
      if (e.t > t) break; if (e.t < lo) continue;
      const B = e.birth, k = kSt[B.st]; if (k < 0.003) continue;
      const age = t - e.t, c = C(COL[e.voice]);
      if (age < FLASH_LIFE && fi < flashPool.length) {
        const f = flashPool[fi++], a = ease(age / 0.04) * Math.exp(-age / 0.22);
        f.visible = true; f.position.copy(B.kind === 'rig' ? W_(stations[B.st], rigTip(B.rig, t, B.lo, B.hi)) : B.p);
        const big = B.kind === 'knot' ? (B.big ? 2.4 : 2.0) : B.kind === 'pedal' ? 1.8 : 1;
        const near = Math.min(1, f.position.distanceTo(camera.position) / 9);   // a flash next to the lens must not fill the frame
        f.scale.setScalar(1.1 * big * (1 + age) * near); f.material.color.copy(c).lerp(C(COL.ink), 0.45).multiplyScalar(a * k * (B.kind === 'knot' ? 1.25 : 1));
      }
      for (let w = 0; w < B.puffs && si < smokePool.length; w++) {
        const sp = smokePool[si++], r1 = hash(e.i, w), r2 = hash(e.i, w + 17), r3 = hash(e.i, w + 41);
        const life = SMOKE_LIFE * (0.7 + 0.3 * r3), u = age / life; if (u >= 1) { sp.visible = false; continue; }
        const grow = 1 - (1 - u) ** 2.2, spread = B.kind === 'knot' ? 2.2 : 1; sp.visible = true;
        sp.position.set(B.p.x + (r1 - 0.5) * 0.4 * spread + (r1 - 0.5) * 0.8 * grow * spread, B.p.y + (r2 - 0.3) * 0.2 + 1.0 * grow * (0.6 + 0.6 * r3), B.p.z + (r2 - 0.5) * 0.6 * grow);
        sp.scale.setScalar((0.45 + 1.8 * grow) * (B.kind === 'knot' ? 1.6 : 1) * Math.min(1, sp.position.distanceTo(camera.position) / 7)); sp.material.rotation = r1 * 6.283 + (r2 - 0.5) * 1.4 * u;
        sp.material.color.copy(c).lerp(C(COL.ink), 0.18).multiplyScalar(ease(age / 0.12) * (1 - u) ** 1.6 * 0.3 * k);
      }
    }
    for (; si < smokePool.length; si++) smokePool[si].visible = false;
    for (; fi < flashPool.length; fi++) flashPool[fi].visible = false;
  }

  // ------------------------------------------------------------ HUD
  const items = [];
  function hudPlane(cv, x, y, o = {}) {
    const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace;
    const sc = o.scale || 0.5, w = cv.width * sc, h = cv.height * sc;
    if (o.top !== undefined) y = o.top - h / 2;
    if (Math.abs(y) + h / 2 > HH - 8 || Math.abs(x) + w / 2 > HW - 8) throw new Error(`HUD item off frame: ${w.toFixed(0)}x${h.toFixed(0)} at ${x},${y}`);
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: t, transparent: true, depthTest: false, toneMapped: false }));
    m.position.set(x, y, 0); m.visible = false; hud.add(m);
    const it = Object.assign({ m, x, y, w, t0: 0, t1: 1, fin: 0.4, fout: 0.5 }, o); items.push(it); return it;
  }
  const cap = (s) => textCanvas(s, { size: 30, weight: '400', color: CSS.dim });
  const title = (s, glow) => textCanvas(s, { size: 58, spacing: 10, glow });
  hudPlane(textCanvas('THE SHAPE OF FÜR ELISE  ·  III', { size: 62, spacing: 12, glow: 'rgba(255,209,102,0.45)' }), 0, 0, { top: 505, t0: 0.3, t1: 4.2, slam: true });
  hudPlane(svg.eq_note, 0, 0, { top: 505, t0: 4.4, t1: 12.5, wipe: 1.4, scale: 1.0 });
  hudPlane(title('I  ·  THE THEME', 'rgba(255,209,102,0.4)'), 0, 0, { top: 505, t0: 13.0, t1: 16.5, slam: true });
  CROSS.forEach((b, i) => { if (b < S2) hudPlane(cap('the hands cross: E and D♯ pass from one to the other'), 0, -470, { t0: b - 0.2, t1: b + 3.3 }); });
  hudPlane(title('II  ·  THE SECOND PART  ·  F MAJOR', 'rgba(155,92,246,0.45)'), 0, 0, { top: 505, t0: S2 + 0.2, t1: S2 + 3.2, slam: true });
  hudPlane(svg.eq_chord, 0, 0, { top: 505, t0: S2 + 3.5, t1: bI(iS2 + 7) - 0.3, wipe: 1.0, scale: 0.85 });
  hudPlane(cap('each note of the chord is one axis: turn to 3D and the third note becomes depth'), 0, -470, { t0: S2 + 1.0, t1: bI(iS2 + 7) - 0.3 });
  hudPlane(title('III  ·  THE THEME RETURNS', 'rgba(255,209,102,0.4)'), 0, 0, { top: 505, t0: S3 + 0.5, t1: S3 + 3.6, slam: true });
  hudPlane(cap('every note leaves a spiral: the past streams away behind it'), 0, -470, { t0: S3 + 1.0, t1: S3 + 7.0 });
  hudPlane(title('IV  ·  THE CHORD PART  ·  D MINOR', 'rgba(46,230,200,0.4)'), 0, 0, { top: 505, t0: S4 + 0.05, t1: S4 + 3.4, slam: true });
  hudPlane(cap('the left hand: one low A, struck six times a bar'), 0, -470, { t0: S4 + 0.6, t1: S4 + 5.5 });
  hudPlane(svg.eq_fourier, 0, 0, { top: 505, t0: bI(iS4 + 13), t1: SW - 0.2, wipe: 1.4, scale: 0.85 });
  hudPlane(cap('A3 → E7, then down one semitone at a time'), 0, -470, { t0: SW + 0.3, t1: S5 - 1.6 });
  hudPlane(title('V  ·  THE THEME, ONE LAST TIME', 'rgba(255,209,102,0.4)'), 0, 0, { top: 505, t0: S5 + 0.7, t1: S5 + 3.8, slam: true });
  hudPlane(cap('Beethoven ends on a single A'), 0, -470, { t0: SEND - 0.4, t1: SEND + 2.6 });
  hudPlane(textCanvas('frequencies slowed 110×  ·  every pitch ratio exact', { size: 22, weight: '400', color: CSS.dim }), 630, 508, { t0: 4.4, t1: SEND });
  hudPlane(textCanvas('THE SHAPE OF FÜR ELISE  ·  III', { size: 66, spacing: 12, glow: 'rgba(255,209,102,0.45)' }), 0, 0, { top: 505, t0: SEND + 2.6, t1: 999, fin: 1.2 });
  hudPlane(textCanvas('L. van Beethoven  ·  Für Elise, WoO 59  ·  complete', { size: 26, weight: '400', color: CSS.dim }), 0, 0, { top: 398, t0: SEND + 3.0, t1: 999, fin: 1.2 });

  // ------------------------------------------------------------ update
  function update(t) {
    const pulse = beatPulse(t), reveal = ease((t - REVEAL[0]) / 2.5);
    // each station is lit while its part plays, and while the camera flies to or from it
    const kSt = [0, 1, 2, 3, 4].map((i) => {
      const spans = [[0, S2 + 0.3], [S2 - 1.9, S3 + 0.6], [S3 - 1.4, S4 + 0.4], [S4 - 1.6, S5 + 0.7], [S5 - 1.3, 999]][i];
      return Math.max(win(t, spans[0], spans[1], 0.6, 0.6), reveal * 0.85);
    });
    stations.forEach((st, i) => { drawGrid(G[i], t, i === 0 ? 0.1 : [0, S2 - 1.5, S3 - 1.0, S4 - 1.2, S5 - 1.0][i], 0.25 + 0.75 * kSt[i], i === stationAt(t) ? pulse : 0);
      stLabels[i].material.opacity = 0.15 + 0.6 * reveal; });
    drawRig(rig1, t, win(t, 2.0, S2 + 0.3, 0.5, 0.6), 0, S2);
    drawRig(rig5, t, win(t, S5 - 0.3, 999, 0.5, 1), S5, 999);
    const zk2 = win(t, bI(iS2 + 4) - 0.4, bI(iS2 + 7) - 0.6, 0.9, 0.6);
    drawKnot(knot2, t, Math.max(win(t, S2 - 0.2, S3 + 0.6, 0.3, 0.6), reveal), S2, S3, zk2 * (1 - reveal), t > S3);
    const zk4 = win(t, bI(iS4 + 5) + 0.6, bI(iS4 + 9) - 0.3, 0.9, 0.4) + win(t, bI(iS4 + 9) + 2.8, SW - 0.5, 0.9, 0.6);
    drawKnot(knot4, t, Math.max(win(t, bI(iS4 + 1) - 0.2, SW + 0.5, 0.3, 0.8), reveal), S4, SW, zk4 * (1 - reveal), t > SW + 0.5);
    drawSpirals(spir3, t, Math.max(win(t, S3 - 0.2, S4 + 0.4, 0.3, 0.6), reveal * 0.6), t > S4 ? 999 : 5.5);
    drawSpirals(spirW, t, Math.max(win(t, SW - 0.2, S5 + 0.7, 0.3, 0.6), reveal * 0.6), t > S5 ? 999 : 5.5);
    drawPedal(ped4, t, win(t, S4 - 0.1, SW + 0.4, 0.3, 0.9));
    // the ring path, and the light that runs along it during a flight
    const cam = camAt(t);
    camera.position.copy(cam.pos); camera.lookAt(cam.look);
    drawEntrances(t, kSt);
    cTmp.copy(C(COL.ink)).multiplyScalar(0.08 + 0.12 * (flying ? 1 : 0) + 0.25 * reveal);
    setLine(ringLine, (u) => v3.set(CENTER.x + R * Math.sin(2 * Math.PI * u), RING_Y, CENTER.z + R * Math.cos(2 * Math.PI * u)), () => cTmp);
    if (flying) { const a = (flying.a + ease(flying.u)) / NST * Math.PI * 2; runner.position.set(CENTER.x + R * Math.sin(a), RING_Y, CENTER.z + R * Math.cos(a));
      runner.material.opacity = Math.sin(Math.PI * flying.u); } else runner.material.opacity = 0;
    camera.position.copy(cam.pos); camera.lookAt(cam.look);
    if (Math.abs(camera.fov - cam.fov) > 1e-4) { camera.fov = cam.fov; camera.updateProjectionMatrix(); }
    scene.fog.density = 0.018 - 0.012 * reveal;
    for (const it of items) {
      const a = win(t, it.t0, it.t1, it.fin, it.fout), m = it.m; m.visible = a > 0.003; if (!m.visible) continue;
      m.material.opacity = a; let s = 1;
      if (it.slam) { const r = clamp01((t - it.t0) / 0.3); s = 1 + 0.3 * (1 - r) * (1 - r); }
      m.scale.set(s, s, 1); m.position.x = it.x;
      if (it.wipe) { const f = Math.max(0.001, ease((t - it.t0) / it.wipe)); m.material.map.repeat.x = f; m.scale.x = f * s; m.position.x = it.x - it.w / 2 * (1 - f); }
    }
    let hit = 0; for (const ch of CHORDS) if (ch.t >= S4 && ch.t < SW) { const a = t - ch.t; if (a >= 0 && a < 2) hit = Math.max(hit, Math.exp(-a / 0.35)); }
    api.bloom = (0.72 + 0.18 * win(t, bI(iS2 + 7), bI(iS2 + 11), 0.6, 0.8) + 0.25 * hit + 0.15 * win(t, SW, S5, 0.5, 0.8)) * (1 - 0.35 * reveal);
  }
  const api = { scene, camera, hud, hudCam, update, bloom: 0.72, bloomRadius: 0.45, bloomThreshold: 0.18,
    facts: { notes: NOTES.length, chords: CHORDS.length, crossings: CROSS.map((x) => +x.toFixed(2)), S: [S2, S3, S4, SW, S5, SEND].map((x) => +x.toFixed(2)) } };
  return api;
}
