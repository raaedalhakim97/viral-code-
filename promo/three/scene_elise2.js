// scene_elise2.js — "THE SHAPE OF FÜR ELISE · II". 16:9, 60 fps.
// The second part (F major) straight into the chord part (D minor), from elise3_score.json:
// the same note list the audio is rendered from, so everything here lands on its note.
//
// One continuous world. A big x-y plane is "now": it travels forward in time (z = t * ZS)
// and every piano note leaves its spiral behind it. The camera glides between flat 2D
// (face-on to the plane) and 3D (orbits, cranes, pull-backs), never cutting.
//   * A chord is one point moving in 3D: each of its three notes is one axis,
//     (sin 2 pi f1 t, sin 2 pi f2 t, sin 2 pi f3 t). Face-on you see x and y only, a flat
//     Lissajous figure; swing to 3D and the third note appears as depth.
//   * The pounding A of the chord part is a vector at the centre of the plane; every
//     strike sends a ring across it.
// Real notes spin far too fast to see; every frequency is divided by SLOW, so all pitch
// ratios stay exact.
import { Line2 } from 'three/addons/lines/Line2.js';
import { LineGeometry } from 'three/addons/lines/LineGeometry.js';
import { LineMaterial } from 'three/addons/lines/LineMaterial.js';

export const FPS = 60;
export const DURATION = 55.7;

const BG = 0x05070f;
const COL = { RH: 0xffd166, LH: 0x2ee6c8, STR: 0x9b5cf6, VC: 0x3b8cff, HN: 0xff8a2b, ink: 0xeaf2ff, DR: 0xeaf2ff };
const CSS = { ink: '#EAF2FF', gold: '#FFD166', tq: '#2EE6C8', vi: '#9B5CF6', dim: '#8A94A6', hn: '#FF8A2B' };
const SLOW = 110, T0 = 2.5, TAU = 0.9, PEDAL = 0.9, ZS = 2.4;

const clamp01 = (x) => Math.min(1, Math.max(0, x));
const ease = (x) => { x = clamp01(x); return x * x * (3 - 2 * x); };
const easeIO = (x) => { x = clamp01(x); return x < 0.5 ? 4 * x * x * x : 1 - (-2 * x + 2) ** 3 / 2; };
const easeOutBack = (x) => { x = clamp01(x); const c = 1.6; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2; };
const win = (t, a, b, fi = 0.5, fo = 0.5) => ease((t - a) / fi) * ease((b - t) / fo);
const hz = (m) => 440 * 2 ** ((m - 69) / 12);
const fvis = (m) => hz(m) / SLOW;

const SVGS = ['eq_chord', 'eq_beat', 'eq_fourier'];
export async function buildAsync(THREE, W, H) {
  const svg = {};
  for (const name of SVGS) {
    const img = new Image(); img.src = `/tex_elise/${name}.svg`; await img.decode();
    const cv = document.createElement('canvas'); cv.width = Math.ceil(img.width * 7 / 1.333); cv.height = Math.ceil(img.height * 7 / 1.333);
    cv.getContext('2d').drawImage(img, 0, 0, cv.width, cv.height); svg[name] = cv;
  }
  const score = await (await fetch('/elise3_score.json')).json();
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
  scene.fog = new THREE.FogExp2(BG, 0.05);
  const camera = new THREE.PerspectiveCamera(35, W / H, 0.01, 600);
  const HW = 960, HH = 540;
  const hud = new THREE.Scene(); const hudCam = new THREE.OrthographicCamera(-HW, HW, HH, -HH, -10, 10);
  const C = (h) => new THREE.Color(h), cTmp = new THREE.Color(), v3 = new THREE.Vector3();

  // ------------------------------------------------------------ the score and its clock
  const EV = score.events.map((e) => ({ ...e, t: e.t + T0 }));
  const BARS = score.bars.map((b) => b + T0);
  const bar = (i) => BARS[i];
  // landmarks (bar indices from arrange3.py): B1, cascade, trill, chord part, its turns, the sweep, the fall, the end
  const M = { B1: bar(0), climb: bar(4), casc: bar(7), trill: bar(11), lead: bar(15), C: bar(16), C60: bar(17), C64: bar(21),
              C68: bar(25), C72: bar(29), C76: bar(33), sweep: bar(34), fall: bar(37), end: bar(39), lastA: bar(40), chord: bar(41),
              stop: score.end + T0 };
  for (const e of EV) {
    const next = EV.find((o) => o.midi === e.midi && o.voice === e.voice && o.t > e.t + 1e-6);
    e.sustained = e.voice !== 'RH' && e.voice !== 'LH';
    e.off = Math.min(next ? next.t : 1e9, e.t + e.dur + (e.sustained ? 0.25 : PEDAL));
  }
  const env = (e, s) => {
    if (s < e.t) return 0;
    const rel = clamp01(1 - (s - e.off) / 0.12);
    return (e.sustained ? ease((s - e.t) / 0.15) : Math.exp(-(s - e.t) / TAU)) * rel;
  };
  const theta = (e, s) => 2 * Math.PI * fvis(e.midi) * (s - e.t);
  const NOTES = EV.filter((e) => e.voice !== 'DR');
  const active = (s, voices) => NOTES.filter((e) => voices.includes(e.voice) && e.t <= s && s < e.off + 0.12);
  const inC = (s) => s >= M.C && s < M.end;

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
  function label3d(parent, str, o, pos, scale) {
    const cv = textCanvas(str, o); const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace;
    const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: t, transparent: true, depthWrite: false, depthTest: false }));
    s.scale.set(scale * cv.width / cv.height, scale, 1); s.position.copy(pos); parent.add(s); return s;
  }
  const dot = (parent, size) => { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: sprite, color: 0xffffff, transparent: true, blending: A, depthWrite: false }));
    s.scale.setScalar(size); parent.add(s); return s; };

  // ------------------------------------------------------------ the plane: "now", a big x-y space that travels with time
  const plane = new THREE.Group(); scene.add(plane);
  const PX = 7.6, PY = 4.2;                                   // half-extents: edge to edge in the face-on frame
  const axX = fatLine(2, 2.0, plane), axY = fatLine(2, 2.0, plane);
  const gridV = Array.from({ length: 15 }, () => fatLine(2, 1.0, plane)), gridH = Array.from({ length: 9 }, () => fatLine(2, 1.0, plane));
  const ticks = Array.from({ length: 24 }, () => fatLine(2, 1.4, plane));
  const lblX = label3d(plane, 'x', { size: 44, weight: '400', color: CSS.dim }, new THREE.Vector3(PX - 0.25, -0.3, 0), 0.32);
  const lblY = label3d(plane, 'y', { size: 44, weight: '400', color: CSS.dim }, new THREE.Vector3(0.3, PY - 0.25, 0), 0.32);
  const lblZ = label3d(plane, 'z  (the third note)', { size: 40, weight: '400', color: CSS.vi }, new THREE.Vector3(0.0, 0.0, 0), 0.26);
  const zAxis = fatLine(2, 1.6, plane);
  function beatPulse(t) {                                     // a flash on every bar line, fast in and exponential out
    let p = 0; for (const b of BARS) { const a = t - b; if (a >= 0 && a < 1.2) p = Math.max(p, ease(a / 0.03) * Math.exp(-a / 0.28)); }
    return p;
  }
  function drawPlane(t) {
    plane.position.z = t * ZS;
    const draw = easeIO((t - 0.1) / 2.2), pulse = beatPulse(t), k = 1 - 0.55 * win(t, M.chord + 1.0, 99, 1.5, 1);
    cTmp.copy(C(COL.ink)).multiplyScalar((0.42 + 0.3 * pulse) * k);
    setLine(axX, (u) => v3.set(-PX * draw + 2 * PX * draw * u, 0, 0), () => cTmp);
    setLine(axY, (u) => v3.set(0, -PY * draw + 2 * PY * draw * u, 0), () => cTmp);
    gridV.forEach((l, i) => { const x = -7 + i, d = easeIO((t - 0.4 - 0.05 * Math.abs(x)) / 1.4);
      cTmp.copy(C(COL.ink)).multiplyScalar((0.07 + 0.08 * pulse) * k);
      setLine(l, (u) => v3.set(x, (-PY + 2 * PY * u) * d, 0), () => cTmp); });
    gridH.forEach((l, i) => { const y = -4 + i, d = easeIO((t - 0.5 - 0.06 * Math.abs(y)) / 1.4);
      cTmp.copy(C(COL.ink)).multiplyScalar((0.07 + 0.08 * pulse) * k);
      setLine(l, (u) => v3.set((-PX + 2 * PX * u) * d, y, 0), () => cTmp); });
    ticks.forEach((l, i) => { const onX = i < 15, v = onX ? -7 + i : -4 + (i - 15); const d = ease((t - 1.2 - 0.03 * i) / 0.4);
      cTmp.copy(C(COL.ink)).multiplyScalar(0.35 * d * k);
      setLine(l, (u) => onX ? v3.set(v, (-0.1 + 0.2 * u) * d, 0) : v3.set((-0.1 + 0.2 * u) * d, v, 0), () => cTmp); });
    lblX.material.opacity = lblY.material.opacity = ease((t - 1.6) / 0.6) * k;
    // the depth axis is only worth naming while a chord's third note is drawn as depth
    // only in the 3D shots of the knot; face-on the depth axis points straight at the camera
    const zk = win(t, M.climb - 0.4, M.casc - 0.6, 0.9, 0.6) + win(t, M.C64 + 0.6, M.C68 - 0.3, 0.9, 0.4) + win(t, M.C68 + 2.8, M.sweep - 0.5, 0.9, 0.6);
    cTmp.copy(C(COL.STR)).multiplyScalar(0.55 * zk);
    setLine(zAxis, (u) => v3.set(0, 0, -3.2 + 6.4 * u), () => cTmp);
    lblZ.position.set(0.15, 0.25, 3.5); lblZ.material.opacity = 0.9 * zk;
  }

  // ------------------------------------------------------------ piano spirals: the history behind the plane
  const LANE_Y = -3.0;                                       // the keyboard lane along the bottom of the plane
  const pitchX = (m) => (m - 64) * 0.17;
  const RAD = { RH: 0.2, LH: 0.27 };
  const spirals = NOTES.filter((e) => e.voice === 'RH' || e.voice === 'LH').map((e) => {
    const T = e.off + 0.12 - e.t, n = Math.max(8, Math.ceil(T * fvis(e.midi) * 26));
    const pos = new Float32Array(n * 3), col = new Float32Array(n * 3), c = C(COL[e.voice]);
    for (let j = 0; j < n; j++) {
      const s = e.t + T * j / (n - 1), a = env(e, s), r = RAD[e.voice] * (0.25 + 0.75 * a), th = theta(e, s);
      pos.set([pitchX(e.midi) + r * Math.cos(th), LANE_Y + r * Math.sin(th), s * ZS], 3 * j);
      const b = 0.1 + 0.62 * a; col.set([c.r * b, c.g * b, c.b * b], 3 * j);
    }
    const g = new LineGeometry(); g.setPositions(pos); g.setColors(col);
    const m = new LineMaterial({ color: 0xffffff, linewidth: e.voice === 'RH' ? 2.4 : 2.0, vertexColors: true, transparent: true, blending: A, depthWrite: false });
    m.resolution.set(W, H);
    const l = new Line2(g, m); l.frustumCulled = false; scene.add(l);
    return { e, l, n, T };
  });
  function drawSpirals(t, histSec, dim = 1) {
    for (const s of spirals) {
      const on = s.e.t <= t && t - s.e.t < histSec; s.l.visible = on; if (!on) continue;
      s.l.material.opacity = dim;
      s.l.geometry.instanceCount = Math.max(1, Math.min(s.n - 1, Math.floor((t - s.e.t) / s.T * (s.n - 1))));
    }
  }

  // ------------------------------------------------------------ the chord: one point moving in 3D, drawn on the plane
  const KNOT_Y = 0.7;                                      // the knot lives above the keyboard lane, never on it
  const knotG = new THREE.Group(); knotG.position.y = KNOT_Y; plane.add(knotG);
  const RK = 2.3, PH = [0, Math.PI / 2, Math.PI / 4], SPAN = 3.0;
  const knotOf = (notes, s, out = new THREE.Vector3()) => out.set(...notes.map((m, i) => RK * Math.sin(2 * Math.PI * fvis(m) * s + PH[i])));
  const KN = [0, 1].map(() => ({ full: fatLine(900, 1.5, knotG), trail: fatLine(200, 3.6, knotG), pen: dot(knotG, 0.32),
    vec: arrow(knotG, 2.6), comp: [0, 1, 2].map(() => fatLine(2, 2.0, knotG)) }));
  const STR_EV = NOTES.filter((e) => e.voice === 'STR');
  // a chord = the string notes struck together (same onset); its three lowest notes are its three axes
  const CHORDS = []; { const byT = new Map(); for (const e of STR_EV) { const k = e.t.toFixed(3); if (!byT.has(k)) byT.set(k, []); byT.get(k).push(e); }
    for (const grp of byT.values()) { if (grp.length < 3) continue; grp.sort((x, y) => x.midi - y.midi); const g3 = grp.slice(0, 3);
      CHORDS.push({ notes: g3.map((e) => e.midi), t: g3[0].t, off: Math.min(...g3.map((e) => e.off)) }); } }
  CHORDS.sort((x, y) => x.t - y.t);
  const AXC = [COL.VC, COL.STR, COL.ink];
  function drawKnot(t, k) {
    knotG.visible = k > 0.003; if (!knotG.visible) return;
    const live = CHORDS.filter((c) => c.t <= t && t < c.off + 0.5).slice(-2);
    KN.forEach((K, i) => {
      const ch = live[live.length - 1 - i];
      if (!ch) { K.full.visible = K.trail.visible = K.pen.visible = false; K.vec.hide(); K.comp.forEach((l) => (l.visible = false)); return; }
      [K.full, K.trail, K.pen].forEach((o) => (o.visible = true)); K.comp.forEach((l) => (l.visible = true));
      const age = t - ch.t, grow = easeOutBack(age / 0.45), fade = clamp01(1 - (t - ch.off) / 0.5) * k;
      const sc = (0.35 + 0.65 * grow), lit = fade * (i === 0 ? 1 : 0.5);
      cTmp.copy(C(COL.STR)).multiplyScalar(0.5 * lit);
      setLine(K.full, (u) => knotOf(ch.notes, u * SPAN, v3).multiplyScalar(sc), () => cTmp);
      setLine(K.trail, (u) => knotOf(ch.notes, t - u * 0.6, v3).multiplyScalar(sc),
        (u) => cTmp.copy(C(COL.ink)).lerp(C(COL.STR), 0.3).multiplyScalar(lit * (1 - u) ** 1.4));
      const p = knotOf(ch.notes, t).multiplyScalar(sc);
      K.pen.position.copy(p); K.pen.material.opacity = lit;
      K.vec.set(new THREE.Vector3(), p, C(COL.ink), lit * 0.85);
      K.comp.forEach((l, j) => { cTmp.copy(C(AXC[j])).multiplyScalar(0.85 * lit);
        setLine(l, (u) => { const q = new THREE.Vector3(); q.setComponent(j, p.getComponent(j) * u); return q; }, () => cTmp); });
    });
  }

  // ------------------------------------------------------------ the rig: tip-to-tail vectors, their shadow is the wave (trill, ending)
  const rig = new THREE.Group(); plane.add(rig);
  const P0 = new THREE.Vector3(-4.9, 0.9, 0), RNOTE = 1.05, WX0 = -3.0, WX1 = 7.2, WSPAN = 1.2;
  const rigArrows = Array.from({ length: 8 }, () => arrow(rig, 3.4));
  const wave = fatLine(800, 3.0, rig), proj = fatLine(2, 1.2, rig), tipDot = dot(rig, 0.28);
  const rigRing = fatLine(129, 1.4, rig);
  const rigTipAt = (s) => { const act = active(s, ['RH']).sort((a, b) => a.t - b.t).slice(-8); const p = P0.clone();
    for (const e of act) { const r = RNOTE * env(e, s), th = theta(e, s); p.x += r * Math.cos(th); p.y += r * Math.sin(th); } return p; };
  const ySig = (s) => active(s, ['RH']).reduce((acc, e) => acc + RNOTE * env(e, s) * Math.sin(theta(e, s)), 0);
  function drawRig(t, k) {
    rig.visible = k > 0.003; if (!rig.visible) return;
    cTmp.copy(C(COL.ink)).multiplyScalar(0.16 * k);
    setLine(rigRing, (u) => v3.set(P0.x + RNOTE * Math.cos(2 * Math.PI * u), P0.y + RNOTE * Math.sin(2 * Math.PI * u), 0), () => cTmp);
    const act = active(t, ['RH']).sort((a, b) => a.t - b.t);
    let p = P0.clone();
    rigArrows.forEach((ar, i) => {
      const e = act[act.length - rigArrows.length + i] ?? null; if (!e) { ar.hide(); return; }
      const r = RNOTE * env(e, t), th = theta(e, t), q = new THREE.Vector3(p.x + r * Math.cos(th), p.y + r * Math.sin(th), 0);
      ar.set(p, q, C(COL[e.voice]), k * (0.35 + 0.65 * env(e, t))); p = q;
    });
    tipDot.position.copy(p); tipDot.material.opacity = k * (act.length ? 1 : 0);
    setLine(wave, (u) => v3.set(WX0 + (WX1 - WX0) * u, P0.y + ySig(t - u * WSPAN), 0),
      (u) => cTmp.copy(C(COL.RH)).multiplyScalar(k * (0.15 + 0.85 * (1 - u) ** 2)));
    cTmp.copy(C(COL.ink)).multiplyScalar(0.25 * k);
    setLine(proj, (u) => v3.set(p.x + (WX0 - p.x) * u, p.y + (P0.y + ySig(t) - p.y) * u, 0), () => cTmp);
  }

  // ------------------------------------------------------------ the pounding A: a vector at the centre, a ring on every strike
  const pedalG = new THREE.Group(); plane.add(pedalG);
  const pedalArrow = arrow(pedalG, 4.0), pedalDot = dot(pedalG, 0.42);
  const pedalLbl = label3d(pedalG, 'A  ·  110 Hz', { size: 40, weight: '700', color: CSS.tq }, new THREE.Vector3(0, -2.05, 0), 0.3);
  const LH_C = NOTES.filter((e) => e.voice === 'LH' && inC(e.t));
  const PEDAL_STRIKES = []; { let last = -1; for (const e of LH_C) if (e.t - last > 0.01) { PEDAL_STRIKES.push(e); last = e.t; } }
  const ringsPool = Array.from({ length: 36 }, () => fatLine(97, 2.0, pedalG));
  function drawPedal(t, k) {
    pedalG.visible = k > 0.003; if (!pedalG.visible) return;
    const act = active(t, ['LH']).filter((e) => inC(e.t)).sort((a, b) => a.midi - b.midi);
    const e = act[0];
    if (e) { const r = 1.7 * (0.3 + 0.7 * env(e, t)), th = theta(e, t);
      const q = new THREE.Vector3(r * Math.cos(th), r * Math.sin(th), 0);
      pedalArrow.set(new THREE.Vector3(), q, C(COL.LH), k); pedalDot.position.copy(q); pedalDot.material.opacity = k * env(e, t);
    } else { pedalArrow.hide(); pedalDot.material.opacity = 0; }
    pedalLbl.material.opacity = k * win(t, M.C + 0.5, M.C64, 0.6, 0.8);
    // rings: every strike of the bass (thin, turquoise), every new chord of the strings (wide, violet)
    let ri = 0;
    const ring = (age, life, r0, r1, col, w) => {
      if (ri >= ringsPool.length || age < 0 || age > life) return; const l = ringsPool[ri++], u = age / life;
      const R = r0 + (r1 - r0) * (1 - (1 - u) ** 2.4), a = (1 - u) ** 2 * k * w; l.visible = true;
      cTmp.copy(C(col)).multiplyScalar(a);
      setLine(l, (v) => v3.set(R * Math.cos(2 * Math.PI * v), R * Math.sin(2 * Math.PI * v), 0), () => cTmp);
    };
    for (let i = PEDAL_STRIKES.length - 1; i >= 0 && ri < 24; i--) { const age = t - PEDAL_STRIKES[i].t; if (age > 1.0) break; ring(age, 1.0, 0.4, 3.8, COL.LH, 0.55); }
    for (const ch of CHORDS) if (inC(ch.t)) ring(t - ch.t, 1.6, 0.8, 7.5, COL.STR, 0.9);
    for (; ri < ringsPool.length; ri++) ringsPool[ri].visible = false;
  }

  // ------------------------------------------------------------ note entrances: a flash of glow and lit smoke
  const hash = (i, k) => { let h = Math.imul(i * 374761393 + k * 668265263, 1274126177) >>> 0; h = Math.imul(h ^ (h >>> 13), 1103515245) >>> 0; return ((h ^ (h >>> 16)) >>> 0) / 4294967296; };
  function smokeTex(seed) {
    const N = 192, cv = document.createElement('canvas'); cv.width = cv.height = N; const g = cv.getContext('2d'), img = g.createImageData(N, N);
    const grid = (x, y, o) => hash(((x & 255) + 256 * (y & 255)) + 65536 * o, seed);
    const vnoise = (x, y, o) => { const xi = Math.floor(x), yi = Math.floor(y), fx = x - xi, fy = y - yi, sx = fx * fx * (3 - 2 * fx), sy = fy * fy * (3 - 2 * fy);
      const a = grid(xi, yi, o), b = grid(xi + 1, yi, o), c = grid(xi, yi + 1, o), d = grid(xi + 1, yi + 1, o);
      return a + (b - a) * sx + (c - a) * sy + (a - b - c + d) * sx * sy; };
    for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
      let n = 0, amp = 0.5, fr = 3 / N;
      for (let o = 0; o < 5; o++) { n += amp * vnoise(x * fr, y * fr, o); amp *= 0.5; fr *= 2; }
      const r = Math.hypot(x - N / 2, y - N / 2) / (N / 2), fall = Math.max(0, 1 - r) ** 1.8;
      const a = Math.max(0, Math.min(1, (n - 0.32) * 2.2)) * fall;
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
  const rigOn = (s) => (s >= M.trill && s < M.C) || s >= M.end;
  // where a note is born (world space), or null if nothing on screen stands for it
  function birth(e) {
    const z = e.t * ZS;
    if (e.voice === 'RH' || (e.voice === 'LH' && !inC(e.t))) {
      if (rigOn(e.t) && e.voice === 'RH') return { kind: 'rig', p: rigTipAt(e.t).add(v3.set(0, 0, z)), puffs: 3 };
      return { kind: 'lane', p: new THREE.Vector3(pitchX(e.midi) + RAD[e.voice], LANE_Y, z), puffs: e.voice === 'RH' ? 3 : 4 };
    }
    if (e.voice === 'STR') { const ch = CHORDS.find((c) => Math.abs(c.t - e.t) < 1e-3 && c.notes[0] === e.midi); if (!ch) return null;
      return { kind: 'knot', p: knotOf(ch.notes, e.t).add(v3.set(0, KNOT_Y, z)), puffs: 6, big: inC(e.t) }; }
    if (e.voice === 'LH' && inC(e.t) && PEDAL_STRIKES.includes(e) && LH_C.indexOf(e) % 6 === 0) return { kind: 'pedal', p: new THREE.Vector3(0, 0, z), puffs: 2 };
    return null;
  }
  NOTES.forEach((e, i) => { e.i = i; e.birth = birth(e); });
  const BORN = NOTES.filter((e) => e.birth).sort((a, b) => a.t - b.t);
  function drawEntrances(t) {
    let si = 0, fi = 0; const lo = t - SMOKE_LIFE;
    for (const e of BORN) {
      if (e.t > t) break; if (e.t < lo) continue;
      const age = t - e.t, c = C(COL[e.voice]), B = e.birth;
      if (age < FLASH_LIFE && fi < flashPool.length) {
        const f = flashPool[fi++], a = ease(age / 0.04) * Math.exp(-age / 0.22);
        f.visible = true; f.position.copy(B.kind === 'rig' ? rigTipAt(t).add(v3.set(0, 0, t * ZS)) : B.p);
        const big = B.kind === 'knot' ? (B.big ? 2.4 : 2.0) : B.kind === 'pedal' ? 1.8 : 1;
        f.scale.setScalar(1.1 * big * (1 + 1.0 * age));
        f.material.color.copy(c).lerp(C(COL.ink), 0.45).multiplyScalar(a * (B.kind === 'knot' ? 1.25 : 1));
      }
      for (let w = 0; w < B.puffs && si < smokePool.length; w++) {
        const sp = smokePool[si++], r1 = hash(e.i, w), r2 = hash(e.i, w + 17), r3 = hash(e.i, w + 41);
        const life = SMOKE_LIFE * (0.7 + 0.3 * r3), u = age / life; if (u >= 1) { sp.visible = false; continue; }
        const grow = 1 - (1 - u) ** 2.2, spread = B.kind === 'knot' ? 2.2 : 1;
        sp.visible = true;
        sp.position.set(B.p.x + (r1 - 0.5) * 0.4 * spread + (r1 - 0.5) * 0.8 * grow * spread,
                        B.p.y + (r2 - 0.3) * 0.2 + 1.0 * grow * (0.6 + 0.6 * r3),
                        B.p.z + (r2 - 0.5) * 0.6 * grow);
        sp.scale.setScalar((0.45 + 1.8 * grow) * (B.kind === 'knot' ? 1.6 : 1));
        sp.material.rotation = r1 * 6.283 + (r2 - 0.5) * 1.4 * u;
        const a = ease(age / 0.12) * (1 - u) ** 1.6 * 0.3;
        sp.material.color.copy(c).lerp(C(COL.ink), 0.18).multiplyScalar(a);
      }
    }
    for (; si < smokePool.length; si++) smokePool[si].visible = false;
    for (; fi < flashPool.length; fi++) flashPool[fi].visible = false;
  }

  // ------------------------------------------------------------ HUD: titles that slam, equations that write, captions
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
  hudPlane(textCanvas('THE SHAPE OF FÜR ELISE  ·  II', { size: 64, spacing: 12, glow: 'rgba(255,209,102,0.45)' }), 0, 0, { top: 505, t0: 0.4, t1: M.B1 + 0.6, slam: true });
  hudPlane(textCanvas('THE SECOND PART  ·  F MAJOR', { size: 40, spacing: 10, color: CSS.vi }), 0, 0, { top: 500, t0: M.B1 + 0.2, t1: M.B1 + 2.6 });
  hudPlane(svg.eq_chord, 0, 0, { top: 505, t0: M.B1 + 2.8, t1: M.casc - 0.3, wipe: 1.0, scale: 0.85 });
  hudPlane(cap('each note of the chord is one axis: face-on you see two of them'), 0, -470, { t0: M.B1 + 0.8, t1: M.climb - 0.1 });
  hudPlane(cap('turn to 3D and the third note becomes depth'), 0, -470, { t0: M.climb + 0.1, t1: M.casc - 0.2 });
  hudPlane(svg.eq_beat, 0, 0, { top: 505, t0: M.trill + 0.3, t1: M.lead - 0.2, wipe: 1.2, scale: 0.9 });
  hudPlane(cap('E and D♯ ring together: the two arrows drift apart and back'), 0, -470, { t0: M.trill + 0.6, t1: M.lead - 0.3 });
  hudPlane(textCanvas('THE CHORD PART  ·  D MINOR', { size: 70, spacing: 10, glow: 'rgba(46,230,200,0.4)' }), 0, 0, { top: 505, t0: M.C + 0.05, t1: M.C60 + 2.4, slam: true });
  hudPlane(cap('the left hand: one low A, struck six times a bar'), 0, -470, { t0: M.C + 0.6, t1: M.C64 - 0.3 });
  hudPlane(cap('every new chord: one more knot, one more ring'), 0, -470, { t0: M.C64 + 0.2, t1: M.C68 - 0.3 });
  hudPlane(svg.eq_fourier, 0, 0, { top: 505, t0: M.C72 + 0.2, t1: M.sweep - 0.2, wipe: 1.4, scale: 0.85 });
  hudPlane(cap('A3 → E7, then down one semitone at a time'), 0, -470, { t0: M.sweep + 0.3, t1: M.end - 0.4 });
  hudPlane(textCanvas('frequencies slowed 110×  ·  every pitch ratio exact', { size: 22, weight: '400', color: CSS.dim }), 630, 508, { t0: M.B1, t1: M.chord });
  hudPlane(textCanvas('THE SHAPE OF FÜR ELISE  ·  II', { size: 66, spacing: 12, glow: 'rgba(255,209,102,0.45)' }), 0, 0, { top: 505, t0: M.chord + 0.6, t1: 99, fin: 1.2 });
  hudPlane(textCanvas('L. van Beethoven  ·  Für Elise, WoO 59  ·  the second part and the chord part', { size: 26, weight: '400', color: CSS.dim }), 0, 0, { top: 398, t0: M.chord + 1.2, t1: 99, fin: 1.2 });

  // ------------------------------------------------------------ camera: one rail, 2D <-> 3D, never a cut
  // poses are relative to "now" (the plane at z = t * ZS); the history lies behind it (smaller z)
  const P = (x, y, dz, lx, ly, ldz, fov = 35) => ({ pos: new THREE.Vector3(x, y, dz), look: new THREE.Vector3(lx, ly, ldz), fov });
  const face = (dz, fov = 35, lx = 0, ly = 0) => P(lx, ly, dz, lx, ly, 0, fov);
  const orbit = (ang, r, y, ldz = -2, fov = 35) => P(r * Math.sin(ang), y, r * Math.cos(ang), 0, 0, ldz, fov);
  const sweepX = (t) => { const act = active(t, ['RH']).sort((a, b) => b.t - a.t); return act.length ? pitchX(act[0].midi) : 2; };
  // [start, blend-in seconds, pose(t)]. Each shot has one subject; between shots the camera turns to a new
  // angle (slow, eased) and then holds, drifting only slightly.
  const drift = (t, t0, amt = 0.035) => amt * (t - t0);
  const SHOTS = [
    [0.0, 0.1, (t) => face(17 - 2.0 * easeIO(t / 3))],                                                   // the grid draws itself
    [M.B1, 1.4, (t) => face(14.0 - 0.9 * ease((t - M.B1) / 4.0), 35, 0, 0.5)],                           // 2D: the chord, flat
    [M.climb - 1.1, 2.3, (t) => orbit(0.95 + drift(t, M.climb), 13.6, 3.4, -1.2)],                       // turn: the third note is depth
    [M.casc - 0.5, 2.0, (t) => P(-8.2 + drift(t, M.casc, 0.25), 0.4, 4.2, 0.8, LANE_Y + 0.5, -6.5)],     // turn to the lane: the cascade
    [M.trill - 0.7, 1.7, (t) => face(13.8)],                                                              // 2D: the trill
    [M.lead, 0.9, (t) => face(15.5)],
    [M.C, 1.15, (t) => { const a = easeIO((t - M.C) / 1.15); return face(9.5 + 13 * a, 54 - 24 * a, 0, 0.3); }], // dolly-zoom into the chord part
    [M.C60 + 0.5, 1.2, (t) => face(21.5 - 4.5 * ease((t - M.C60) / 4.0), 30, 0, 0.3)],
    [M.C64 - 0.4, 2.3, (t) => P(10.8 - drift(t, M.C64, 0.12), 2.4, 7.8, 0, 0.5, -1.2)],                  // turn to the side: the knot in depth
    [M.C68 - 0.2, 1.0, (t) => face(10.6 + 0.6 * ease((t - M.C68) / 2.0), 35, 0, 0.4)],                    // punch in: the chord explodes
    [M.C68 + 2.0, 2.0, (t) => P(-9.8 + drift(t, M.C68, 0.1), 5.2, 8.2, 0, 0.4, -1.0)],                   // turn to the other side, higher
    [M.C72 - 0.2, 2.2, (t) => P(1.5, 12.5 + drift(t, M.C72, 0.25), 7.5, 0, 0.3, -1.8)],                  // turn to look down on it
    [M.sweep - 0.4, 1.6, (t) => { const x = sweepX(t); return P(x * 0.8 - 4.2, 0.8 + 0.2 * (x + 4), 7.0, x * 0.9, LANE_Y + 1.0, -2.5); }], // crane with the sweep
    [M.end - 0.5, 1.4, (t) => face(14.5)],                                                                 // 2D: home
    [M.chord, 3.8, (t) => { const a = easeIO((t - M.chord) / 4.8); return P(4 + 17 * a, 1.5 + 6.5 * a, 12 - 20 * a, 0, -1.5, -6 - 30 * a, 35 + 15 * a); }], // the whole piece, side-on
  ];
  const tmpA = { pos: new THREE.Vector3(), look: new THREE.Vector3(), fov: 35 };
  function camAt(t) {
    let i = 0; while (i + 1 < SHOTS.length && SHOTS[i + 1][0] <= t) i++;
    const cur = SHOTS[i][2](t), prev = i > 0 ? SHOTS[i - 1][2](t) : cur, a = i > 0 ? easeIO((t - SHOTS[i][0]) / SHOTS[i][1]) : 1;
    tmpA.pos.copy(prev.pos).lerp(cur.pos, a); tmpA.look.copy(prev.look).lerp(cur.look, a); tmpA.fov = prev.fov + (cur.fov - prev.fov) * a;
    return tmpA;
  }

  function update(t) {
    drawPlane(t);
    const finale = ease((t - M.chord) / 3.5);
    // one subject per shot: the spirals lead in the cascade, the sweep and the finale; the knot everywhere else
    const spF = 0.2 + 0.8 * Math.max(win(t, M.casc - 0.5, M.trill - 0.3, 1.0, 0.9), win(t, M.sweep - 0.4, M.end, 1.0, 0.9), ease((t - M.chord) / 2.0));
    const knF = Math.max(win(t, M.B1 - 0.2, M.casc, 0.3, 1.0), 0.12 * win(t, M.casc, M.trill, 0.5, 0.5), win(t, M.C60 - 0.2, M.sweep, 0.3, 1.0));
    drawSpirals(t, 5.5 + 60 * finale, spF * (1 - 0.45 * finale));
    scene.fog.density = 0.05 - 0.04 * finale;
    drawKnot(t, knF);
    drawRig(t, Math.max(win(t, M.trill - 0.3, M.C + 0.2, 0.5, 0.5), win(t, M.end - 0.3, 99, 0.5, 1)));
    drawPedal(t, win(t, M.C - 0.1, M.sweep + 0.4, 0.3, 0.9));
    drawEntrances(t);
    const cam = camAt(t), z = t * ZS;
    camera.position.set(cam.pos.x, cam.pos.y, z + cam.pos.z); camera.lookAt(cam.look.x, cam.look.y, z + cam.look.z);
    if (Math.abs(camera.fov - cam.fov) > 1e-4) { camera.fov = cam.fov; camera.updateProjectionMatrix(); }
    for (const it of items) {
      const a = win(t, it.t0, it.t1, it.fin, it.fout), m = it.m; m.visible = a > 0.003; if (!m.visible) continue;
      m.material.opacity = a; let s = 1;
      if (it.slam) { const r = clamp01((t - it.t0) / 0.3); s = 1 + 0.3 * (1 - r) * (1 - r); }
      m.scale.set(s, s, 1); m.position.x = it.x;
      if (it.wipe) { const f = Math.max(0.001, ease((t - it.t0) / it.wipe)); m.material.map.repeat.x = f; m.scale.x = f * s; m.position.x = it.x - it.w / 2 * (1 - f); }
    }
    // more glow on the big moments: the cascade, each chord explosion, the sweep; never a linear ramp
    let hit = 0; for (const ch of CHORDS) if (inC(ch.t)) { const a = t - ch.t; if (a >= 0 && a < 2) hit = Math.max(hit, Math.exp(-a / 0.35)); }
    api.bloom = (0.72 + 0.18 * win(t, M.casc, M.trill, 0.6, 0.8) + 0.25 * hit + 0.15 * win(t, M.sweep, M.end, 0.5, 0.8)) * (1 - 0.4 * finale);
  }
  const api = { scene, camera, hud, hudCam, update, bloom: 0.72, bloomRadius: 0.45, bloomThreshold: 0.18,
    facts: { notes: NOTES.length, chords: CHORDS.length, strikes: PEDAL_STRIKES.length, landmarks: Object.fromEntries(Object.entries(M).map(([k, v]) => [k, +v.toFixed(2)])) } };
  return api;
}
