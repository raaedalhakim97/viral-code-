// scene_elise.js — "THE SHAPE OF FÜR ELISE". 16:9, 60 fps.
//
// A note is a spinning vector: y = A e^{-t/tau} sin(2 pi f t) is the shadow of an arrow
// of length A e^{-t/tau} turning f times a second. Every arrow on screen is one note of
// elise_score.json, the same score the audio is rendered from, so a vector appears on
// the frame its note sounds. Real notes spin too fast to see; every frequency is divided
// by the same SLOW factor, so all pitch ratios stay exact. Instrument vector chains use
// the overtone strengths measured from the recorded samples (harmonics.json).
import { Line2 } from 'three/addons/lines/Line2.js';
import { LineGeometry } from 'three/addons/lines/LineGeometry.js';
import { LineMaterial } from 'three/addons/lines/LineMaterial.js';

export const FPS = 60;
export const DURATION = 62.0;

const BG = 0x05070f;
const COL = { RH: 0xffd166, LH: 0x2ee6c8, STR: 0x9b5cf6, VC: 0x3b8cff, HN: 0xff8a2b, ink: 0xeaf2ff };
const CSS = { ink: '#EAF2FF', gold: '#FFD166', tq: '#2EE6C8', vi: '#9B5CF6', dim: '#8A94A6', hn: '#FF8A2B', vc: '#3B8CFF' };
const SLOW = 110;                        // every frequency / 110: A4 = 4 turns a second
const T0 = 2.5;                          // the equation writes itself first; the first E sounds here
const TAU = 0.9, PEDAL = 0.9;            // piano decay (s) and how long the pedal lets a note ring past its length
// sections (seconds, video time)
const S = { open: [0, T0], rig: [T0, 12.6], roll: [12.6, 24.7], chord: [24.7, 33.4], chains: [33.4, 41.0],
            climax: [41.0, 48.4], coda: [48.4, 62.0] };

const clamp01 = (x) => Math.min(1, Math.max(0, x));
const ease = (x) => { x = clamp01(x); return x * x * (3 - 2 * x); };
const win = (t, a, b, fi = 0.5, fo = 0.5) => ease((t - a) / fi) * ease((b - t) / fo);
const hz = (m) => 440 * 2 ** ((m - 69) / 12);
const fvis = (m) => hz(m) / SLOW;

// ---------------------------------------------------------------- assets
const SVGS = ['eq_note', 'eq_beat', 'eq_chord', 'eq_series', 'eq_fourier'];
export async function buildAsync(THREE, W, H) {
  const svg = {};
  for (const name of SVGS) {
    const img = new Image(); img.src = `/tex_elise/${name}.svg`; await img.decode();
    const cv = document.createElement('canvas'); cv.width = Math.ceil(img.width * 7 / 1.333); cv.height = Math.ceil(img.height * 7 / 1.333);
    cv.getContext('2d').drawImage(img, 0, 0, cv.width, cv.height); svg[name] = cv;
  }
  const score = await (await fetch('/elise_score.json')).json();
  const harm = await (await fetch('/harmonics.json')).json();
  return build(THREE, W, H, svg, score, harm);
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

export function build(THREE, W, H, svg, score, harm) {
  const A = THREE.AdditiveBlending;
  const scene = new THREE.Scene(); scene.background = new THREE.Color(BG);
  scene.fog = new THREE.FogExp2(BG, 0.075);         // old notes fade into the dark instead of stacking into a glare
  const camera = new THREE.PerspectiveCamera(35, W / H, 0.01, 400);
  const HW = 960, HH = 540;
  const hud = new THREE.Scene(); const hudCam = new THREE.OrthographicCamera(-HW, HW, HH, -HH, -10, 10);
  const C = (h) => new THREE.Color(h), cTmp = new THREE.Color();

  // ------------------------------------------------------------ the score
  const EV = score.events.map((e) => ({ ...e, t: e.t + T0 }));
  // a piano note rings until the same key is struck again, or until its length + the pedal
  for (const e of EV) {
    const next = EV.find((o) => o.midi === e.midi && o.voice === e.voice && o.t > e.t + 1e-6);
    const sustained = e.voice !== 'RH' && e.voice !== 'LH';
    e.off = Math.min(next ? next.t : 1e9, e.t + e.dur + (sustained ? 0.25 : PEDAL));
    e.sustained = sustained;
  }
  const env = (e, s) => {                                   // the arrow's length over time
    if (s < e.t) return 0;
    const rel = clamp01(1 - (s - e.off) / 0.12);                 // a damper does not cut to zero in one frame
    if (e.sustained) return ease((s - e.t) / 0.15) * rel;
    return Math.exp(-(s - e.t) / TAU) * rel;
  };
  const theta = (e, s) => 2 * Math.PI * fvis(e.midi) * (s - e.t);
  const active = (s, voices) => EV.filter((e) => voices.includes(e.voice) && e.t <= s && s < e.off + 0.12);

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
  const v3 = new THREE.Vector3();
  // an arrow: a fat shaft and a small cone head, both in the plane of its group
  const UP = new THREE.Vector3(0, 1, 0);
  const coneGeo = new THREE.ConeGeometry(0.045, 0.13, 12); coneGeo.translate(0, -0.065, 0);
  function arrow(parent, width = 3) {
    const shaft = fatLine(2, width, parent);
    const head = new THREE.Mesh(coneGeo, new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, blending: A, depthWrite: false }));
    parent.add(head);
    return {
      set(a, b, col, k = 1) {
        const az = a.z ?? 0, bz = b.z ?? 0;
        const d = new THREE.Vector3(b.x - a.x, b.y - a.y, bz - az), len = d.length(); const on = len > 0.004 && k > 0.003;
        shaft.visible = head.visible = on; if (!on) return;
        cTmp.copy(col).multiplyScalar(k);
        setLine(shaft, (u) => v3.set(a.x + (b.x - a.x) * u, a.y + (b.y - a.y) * u, az + (bz - az) * u), () => cTmp);
        head.position.set(b.x, b.y, bz); head.quaternion.setFromUnitVectors(UP, d.divideScalar(len));
        head.material.color.copy(col).multiplyScalar(k); head.scale.setScalar(Math.min(1, len / 0.18));
      },
      hide() { shaft.visible = head.visible = false; },
    };
  }
  function ring(parent, r, col, k) {
    const l = fatLine(129, 1.2, parent); cTmp.copy(C(col)).multiplyScalar(k);
    setLine(l, (u) => v3.set(r * Math.cos(2 * Math.PI * u), r * Math.sin(2 * Math.PI * u), 0), () => cTmp); return l;
  }
  function label3d(parent, str, o, pos, scale) {
    const cv = textCanvas(str, o); const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace;
    const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: t, transparent: true, depthWrite: false, depthTest: false }));
    s.scale.set(scale * cv.width / cv.height, scale, 1); s.position.copy(pos); parent.add(s); return s;
  }

  // ------------------------------------------------------------ 1. the rig: x-y plane, notes as tip-to-tail vectors, the shadow is the wave
  const rig = new THREE.Group(); scene.add(rig);
  const P0 = new THREE.Vector3(-3.0, -0.25, 0), RNOTE = 0.62, WX0 = -1.15, WX1 = 4.7, WSPAN = 1.25;   // wave shows the last 1.25 s
  const axisX = fatLine(2, 1.4, rig), axisY = fatLine(2, 1.4, rig);
  const rigRing = ring(rig, RNOTE, COL.ink, 0.12); rigRing.position.copy(P0);
  const rigArrows = Array.from({ length: 10 }, () => arrow(rig, 3.2));
  const wave = fatLine(700, 2.6, rig);
  const proj = fatLine(2, 1.0, rig);
  const tipDot = new THREE.Sprite(new THREE.SpriteMaterial({ map: sprite, color: 0xffffff, transparent: true, blending: A, depthWrite: false }));
  tipDot.scale.setScalar(0.16); rig.add(tipDot);
  const lx = label3d(rig, 'x', { size: 44, weight: '400', color: CSS.dim }, new THREE.Vector3(P0.x + 1.25, P0.y - 0.16, 0), 0.22);
  const ly = label3d(rig, 'y', { size: 44, weight: '400', color: CSS.dim }, new THREE.Vector3(P0.x - 0.16, P0.y + 1.25, 0), 0.22);
  const ySig = (s, voices) => active(s, voices).reduce((acc, e) => acc + RNOTE * env(e, s) * Math.sin(theta(e, s)), 0);
  function drawRig(t, voices, k) {
    rig.visible = k > 0.003; if (!rig.visible) return;
    const axk = k * clamp01((t - 0.2) / 1.0);
    cTmp.copy(C(COL.ink)).multiplyScalar(0.3 * axk);
    setLine(axisX, (u) => v3.set(P0.x - 1.1 + 2.3 * u * ease(t / 1.2), P0.y, 0), () => cTmp);
    setLine(axisY, (u) => v3.set(P0.x, P0.y - 1.1 + 2.3 * u * ease(t / 1.2), 0), () => cTmp);
    lx.material.opacity = ly.material.opacity = axk;
    rigRing.material.opacity = k;
    const act = active(t, voices).sort((a, b) => a.t - b.t);
    let p = P0.clone();
    rigArrows.forEach((ar, i) => {
      const e = act[act.length - rigArrows.length + i] ?? null;      // the newest notes, oldest at the root of the chain
      if (!e) { ar.hide(); return; }
      const r = RNOTE * env(e, t), th = theta(e, t);
      const q = new THREE.Vector3(p.x + r * Math.cos(th), p.y + r * Math.sin(th), 0);
      ar.set(p, q, C(COL[e.voice]), k * (0.35 + 0.65 * env(e, t))); p = q;
    });
    tipDot.position.copy(p); tipDot.material.opacity = k * (act.length ? 1 : 0);
    const scale = 1;
    setLine(wave, (u) => v3.set(WX0 + (WX1 - WX0) * u, P0.y + scale * ySig(t - u * WSPAN, voices), 0),
      (u) => { const a = 1 - u; return cTmp.copy(C(COL.RH)).multiplyScalar(k * (0.15 + 0.85 * a * a)); });
    cTmp.copy(C(COL.ink)).multiplyScalar(0.25 * k);
    setLine(proj, (u) => v3.set(p.x + (WX0 - p.x) * u, p.y + (P0.y + ySig(t, voices) - p.y) * u, 0), () => cTmp);
  }

  // ------------------------------------------------------------ 2. the roll: every note a decaying spiral; x = pitch, depth = time
  const roll = new THREE.Group(); scene.add(roll);
  const ZS = 2.4;                                             // depth units per second
  const pitchX = (m) => -(m - 62) * 0.105;            // the camera looks back along time, so -x is screen right: low notes left, like a piano
  const RAD = { RH: 0.13, LH: 0.2, STR: 0.27, VC: 0.34, HN: 0.3 }, YOFF = { RH: 0.0, LH: 0.0, STR: 0.75, VC: -0.75, HN: 1.3 };
  const spirals = EV.map((e) => {
    const T = e.off + 0.12 - e.t, n = Math.max(8, Math.ceil(T * fvis(e.midi) * 28));
    const pos = new Float32Array(n * 3), col = new Float32Array(n * 3), c = C(COL[e.voice]);
    for (let j = 0; j < n; j++) {
      const s = e.t + T * j / (n - 1), r = RAD[e.voice] * (0.25 + 0.75 * env(e, s)), th = theta(e, s), a = env(e, s);
      pos.set([pitchX(e.midi) + r * Math.cos(th), YOFF[e.voice] + r * Math.sin(th), -s * ZS], 3 * j);
      const b = 0.1 + 0.62 * a; col.set([c.r * b, c.g * b, c.b * b], 3 * j);
    }
    const g = new LineGeometry(); g.setPositions(pos); g.setColors(col);
    const m = new LineMaterial({ color: 0xffffff, linewidth: e.sustained ? 1.6 : 2.2, vertexColors: true, transparent: true, blending: A, depthWrite: false });
    m.resolution.set(W, H);
    const l = new Line2(g, m); l.frustumCulled = false; roll.add(l);
    return { e, l, n, T };
  });
  const nowLine = fatLine(2, 1.5, roll);
  // the spectrum on the "now" plane: every sounding note's overtones, at their pitch (log frequency)
  const N_SPEC = 260, specLine = fatLine(N_SPEC, 2.4, roll);
  const HARM = { RH: harm.piano.harmonics, LH: harm.piano.harmonics, STR: harm.violin.harmonics, VC: harm.cello.harmonics, HN: harm.horn.harmonics };
  function spectrumAt(t) {
    const sp = new Float32Array(N_SPEC), m0 = 30, m1 = 100;
    for (const e of active(t, ['RH', 'LH', 'STR', 'VC', 'HN'])) {
      const a = env(e, t); HARM[e.voice].forEach((h, n) => {
        const mm = e.midi + 12 * Math.log2(n + 1), j = (mm - m0) / (m1 - m0) * (N_SPEC - 1);
        for (let d = -3; d <= 3; d++) { const jj = Math.round(j) + d; if (jj >= 0 && jj < N_SPEC) sp[jj] += a * h * Math.exp(-((jj - j) ** 2) / 1.2); }
      });
    }
    return { sp, m0, m1 };
  }
  function drawRoll(t, k, voices) {
    roll.visible = k > 0.003; if (!roll.visible) return;
    for (const s of spirals) {
      const on = voices.includes(s.e.voice) && s.e.t <= t && t - s.e.t < 5.5;
      s.l.visible = on; if (!on) continue;
      s.l.geometry.instanceCount = Math.max(1, Math.min(s.n - 1, Math.floor((t - s.e.t) / s.T * (s.n - 1))));
      s.l.material.opacity = k;
    }
    cTmp.copy(C(COL.ink)).multiplyScalar(0.35 * k);
    setLine(nowLine, (u) => v3.set(pitchX(30) + (pitchX(100) - pitchX(30)) * u, -1.0, -t * ZS), () => cTmp);
    const { sp, m0, m1 } = spectrumAt(t), mx = 1.6;
    setLine(specLine, (u, j) => v3.set(pitchX(m0 + (m1 - m0) * u), -1.0 + Math.min(1.1, sp[j] * 0.45), -t * ZS),
      (u, j) => cTmp.copy(C(COL.ink)).lerp(C(COL.RH), 0.5).multiplyScalar(k * (0.25 + 0.75 * Math.min(1, sp[j] / mx))));
  }

  // ------------------------------------------------------------ 3. chords: each note of the chord is one axis (x, y, z);
  // the chord is a single point moving in 3D, (sin 2 pi f1 t, sin 2 pi f2 t, sin 2 pi f3 t). Its path is the chord's shape:
  // whole-number ratios (just intonation 10:12:15, 4:5:6) close into a knot; equal temperament almost does, and the
  // slow drift you see is real.
  const chord = new THREE.Group(); scene.add(chord);
  const CHORDS = [{ name: 'A MINOR', notes: [57, 60, 64], x: -2.35 }, { name: 'E MAJOR', notes: [56, 59, 64], x: 2.35 }];
  const RK = 1.05, PH = [0, Math.PI / 2, Math.PI / 4];
  const knot = (ch, s) => new THREE.Vector3(...ch.notes.map((m, i) => RK * Math.sin(2 * Math.PI * fvis(m) * s + PH[i])));
  CHORDS.forEach((ch) => {
    ch.g = new THREE.Group(); ch.g.position.set(ch.x, -0.05, 0); chord.add(ch.g);
    ch.period = 5 / fvis(ch.notes[0]);
    ch.full = fatLine(1800, 1.3, ch.g); ch.trail = fatLine(240, 3.2, ch.g);
    ch.axes = [0, 1, 2].map(() => fatLine(2, 1.0, ch.g)); ch.comp = [0, 1, 2].map(() => fatLine(2, 1.6, ch.g));
    ch.vec = arrow(ch.g, 2.4);
    ch.pen = new THREE.Sprite(new THREE.SpriteMaterial({ map: sprite, color: 0xffffff, transparent: true, blending: A, depthWrite: false }));
    ch.pen.scale.setScalar(0.18); ch.g.add(ch.pen);
    ch.label = label3d(chord, ch.name, { size: 40, spacing: 10, color: CSS.vi }, new THREE.Vector3(ch.x, -1.9, 0), 0.2);
  });
  const AXC = [COL.VC, COL.STR, COL.STR];
  function drawChords(t, k) {
    chord.visible = k > 0.003; if (!chord.visible) return;
    const strs = active(t, ['STR']); const held = new Set(strs.map((e) => e.midi));
    CHORDS.forEach((ch) => {
      const on = ch.notes.every((m) => held.has(m)) ? 1 : 0, lit = k * (0.3 + 0.7 * on);
      ch.g.rotation.set(0.42, 0.5 + 0.22 * t, 0);
      cTmp.copy(C(COL.STR)).multiplyScalar(0.42 * lit);
      setLine(ch.full, (u) => knot(ch, u * ch.period), () => cTmp);
      setLine(ch.trail, (u) => knot(ch, t - u * 0.7), (u) => cTmp.copy(C(COL.ink)).lerp(C(COL.STR), 0.3).multiplyScalar(lit * (1 - u) ** 1.4));
      const p = knot(ch, t);
      ch.axes.forEach((l, i) => { cTmp.copy(C(COL.ink)).multiplyScalar(0.16 * k);
        setLine(l, (u) => { const v = new THREE.Vector3(); v.setComponent(i, -RK * 1.15 + 2.3 * RK * u); return v; }, () => cTmp); });
      // the point's three coordinates: one per note, each the note's own sine
      ch.comp.forEach((l, i) => { cTmp.copy(C(AXC[i])).multiplyScalar(0.8 * lit);
        setLine(l, (u) => { const v = new THREE.Vector3(); v.setComponent(i, p.getComponent(i) * u); return v; }, () => cTmp); });
      ch.vec.set(new THREE.Vector3(), p, C(COL.ink), lit * 0.9);
      ch.pen.position.copy(p); ch.pen.material.opacity = lit;
      ch.label.material.opacity = 0.35 + 0.65 * on * k;
    });
  }

  // ------------------------------------------------------------ 4. instrument chains: the same A3, measured overtones, as vector chains
  const chains = new THREE.Group(); scene.add(chains);
  const INST = [['PIANO', 'piano', COL.RH, CSS.gold], ['VIOLIN', 'violin', COL.STR, CSS.vi], ['CELLO', 'cello', COL.VC, CSS.vc], ['HORN', 'horn', COL.HN, CSS.hn]];
  INST.forEach((it, i) => {
    const g = new THREE.Group(); g.position.set(-3.75 + 2.5 * i, 0.45, 0); chains.add(g);
    const a = harm[it[1]].harmonics, sum = a.reduce((x, y) => x + y, 0), sc = 0.95 / sum;
    it.g = g; it.a = a.map((x) => x * sc);
    it.arrows = it.a.map(() => arrow(g, 2.2));
    it.curve = fatLine(600, 2.0, g); it.wave = fatLine(400, 1.8, g);
    label3d(chains, it[0], { size: 40, spacing: 10, color: it[3] }, new THREE.Vector3(g.position.x, -1.95, 0), 0.19);
  });
  const CHAIN_F = 0.4;                                        // chain panel: A3 turns 0.4 times a second (slowed 550x), shown in full
  const chainTip = (a, ph) => a.reduce((p, r, n) => ({ x: p.x + r * Math.cos((n + 1) * ph), y: p.y + r * Math.sin((n + 1) * ph) }), { x: 0, y: 0 });
  const level = (voices, t) => active(t, voices).reduce((m, e) => Math.max(m, env(e, t)), 0);
  const PANEL_V = [['RH', 'LH'], ['STR'], ['VC'], ['HN']];
  function drawChains(t, k) {
    chains.visible = k > 0.003; if (!chains.visible) return;
    const ph = 2 * Math.PI * CHAIN_F * t;
    INST.forEach((it, ii) => {
      const c = C(it[2]), lv = 0.35 + 0.65 * level(PANEL_V[ii], t);
      setLine(it.curve, (u) => { const q = chainTip(it.a, 2 * Math.PI * u); return v3.set(q.x, q.y, 0); }, () => cTmp.copy(c).multiplyScalar((0.25 + 0.45 * lv) * k));
      let p = { x: 0, y: 0 };
      it.a.forEach((r, n) => { const q = { x: p.x + r * Math.cos((n + 1) * ph), y: p.y + r * Math.sin((n + 1) * ph) };
        if (r > 0.004) it.arrows[n].set(p, q, n === 0 ? C(COL.ink) : c, k * lv * (n === 0 ? 0.95 : 0.8)); else it.arrows[n].hide(); p = q; });
      // the waveform the chain draws: its y over one period, laid out below
      setLine(it.wave, (u) => v3.set(-1.0 + 2.0 * u, -1.45 + 0.32 * chainTip(it.a, ph - 2 * Math.PI * u).y, 0),
        (u) => cTmp.copy(c).multiplyScalar(k * (0.25 + 0.75 * (1 - u))));
    });
  }

  // ------------------------------------------------------------ note entrances: a flash of glow and a breath of lit smoke
  // Every note, the instant it sounds, flashes where it is born and lets off a few soft wisps in its colour that
  // rise, widen and vanish. Nothing is stored between frames: each wisp is a function of (note, wisp index, t).
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
    g.putImageData(img, 0, 0); const t = new THREE.CanvasTexture(cv); return t;
  }
  const SMOKE_TEX = [11, 23, 37, 51].map(smokeTex);
  const haloTex = (() => { const cv = document.createElement('canvas'); cv.width = cv.height = 256; const g = cv.getContext('2d');
    const gr = g.createRadialGradient(128, 128, 0, 128, 128, 128);
    gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.18, 'rgba(255,255,255,0.55)'); gr.addColorStop(0.5, 'rgba(255,255,255,0.12)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 256, 256); return new THREE.CanvasTexture(cv); })();
  const pool = (n, texOf) => Array.from({ length: n }, (_, i) => { const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: texOf(i), transparent: true,
    blending: A, depthWrite: false, depthTest: false })); sp.visible = false; scene.add(sp); return sp; });
  const smokePool = pool(320, (i) => SMOKE_TEX[i % 4]), flashPool = pool(48, () => haloTex);
  const SMOKE_LIFE = 2.2, FLASH_LIFE = 0.9;
  const PUFFS = { RH: 3, LH: 4, STR: 5, VC: 3, HN: 3 };
  const sectionOf = (time) => time < S.roll[0] ? 'rig' : time < S.chord[0] ? 'roll' : time < S.chains[0] ? 'chord'
    : time < S.climax[0] ? 'chains' : time < S.coda[0] ? 'roll' : 'rig';
  const rigTip = (s) => { const act = active(s, ['RH']).sort((a, b) => a.t - b.t).slice(-10); const p = P0.clone();
    for (const e of act) { const r = RNOTE * env(e, s), th = theta(e, s); p.x += r * Math.cos(th); p.y += r * Math.sin(th); } return p; };
  const tmpObj = new THREE.Object3D();
  // where (in world space) a note is born, or null if nothing on screen stands for it then
  function birth(e) {
    const sec = sectionOf(e.t);
    if (sec === 'rig') return e.voice === 'RH' ? { sec, p: rigTip(e.t) } : null;
    if (sec === 'roll') return { sec, p: new THREE.Vector3(pitchX(e.midi) + RAD[e.voice], YOFF[e.voice], -e.t * ZS) };
    if (sec === 'chord') {
      const ch = CHORDS.find((c) => e.voice === 'STR' && c.notes[0] === e.midi); if (!ch) return null;
      tmpObj.position.copy(ch.g.position); tmpObj.rotation.set(0.42, 0.5 + 0.22 * e.t, 0); tmpObj.scale.set(1, 1, 1); tmpObj.updateMatrix();
      return { sec, p: knot(ch, e.t).applyMatrix4(tmpObj.matrix) };
    }
    const it = INST[{ RH: 0, LH: 0, STR: 1, VC: 2, HN: 3 }[e.voice]];
    const q = chainTip(it.a, 2 * Math.PI * CHAIN_F * e.t);
    return { sec, p: new THREE.Vector3(it.g.position.x + q.x, it.g.position.y + q.y, 0) };
  }
  EV.forEach((e, i) => { e.i = i; e.birth = birth(e); });
  const EV_BY_T = EV.filter((e) => e.birth).sort((a, b) => a.t - b.t);
  function drawEntrances(t, kSec) {
    let si = 0, fi = 0;
    const lo = t - SMOKE_LIFE;
    for (const e of EV_BY_T) {
      if (e.t > t) break; if (e.t < lo) continue;
      const age = t - e.t, k = kSec[e.birth.sec], c = C(COL[e.voice]); if (k < 0.003) continue;
      const loud = e.sustained ? 0.8 : 1.0;
      // glow: fast in, then an exponential fall; never linear
      if (age < FLASH_LIFE && fi < flashPool.length) {
        const f = flashPool[fi++], a = ease(age / 0.04) * Math.exp(-age / 0.22);
        f.visible = true; f.position.copy(e.birth.sec === 'rig' ? rigTip(t) : e.birth.p);     // in the x-y plane the glow rides the spinning tip
        f.scale.setScalar((e.voice === 'RH' ? 0.8 : 1.05) * (1 + 1.0 * age));
        f.material.color.copy(c).lerp(C(COL.ink), 0.45).multiplyScalar(a * k * loud * (e.birth.sec === 'chord' ? 2.4 : 1));
        if (e.birth.sec === 'chord') f.scale.multiplyScalar(1.6);
      }
      // smoke: a few wisps per note, each with its own drift, size, spin and texture
      for (let w = 0; w < PUFFS[e.voice] && si < smokePool.length; w++) {
        const sp = smokePool[si++], r1 = hash(e.i, w), r2 = hash(e.i, w + 17), r3 = hash(e.i, w + 41);
        const life = SMOKE_LIFE * (0.7 + 0.3 * r3), u = age / life; if (u >= 1) { sp.visible = false; continue; }
        const grow = 1 - (1 - u) ** 2.2;                                         // widens fast, then slows
        sp.visible = true;
        sp.position.set(e.birth.p.x + (r1 - 0.5) * 0.25 + (r1 - 0.5) * 0.5 * grow,
                        e.birth.p.y + (r2 - 0.3) * 0.12 + 0.75 * grow * (0.6 + 0.6 * r3),
                        e.birth.p.z + (r2 - 0.5) * 0.3 * grow);
        sp.scale.setScalar((0.3 + 1.25 * grow) * (e.voice === 'RH' ? 0.85 : 1.15));
        sp.material.rotation = r1 * 6.283 + (r2 - 0.5) * 1.4 * u;
        const a = ease(age / 0.12) * (1 - u) ** 1.6 * 0.3 * k * loud;
        sp.material.color.copy(c).lerp(C(COL.ink), 0.18).multiplyScalar(a);
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
  hudPlane(svg.eq_note, 0, 0, { top: 470, t0: 0.15, t1: S.rig[0] + 2.2, wipe: T0 - 0.3, scale: 1.0 });
  hudPlane(svg.eq_beat, 0, 0, { top: 470, t0: S.rig[0] + 2.4, t1: S.rig[1] - 0.4, wipe: 1.2, scale: 0.9 });
  hudPlane(textCanvas('E + D♯  ring together:  the arrows drift apart and back', { size: 30, weight: '400', color: CSS.dim }), 0, -455, { t0: S.rig[0] + 2.6, t1: S.rig[1] - 0.6 });
  const capSlow = () => textCanvas('frequencies slowed 110×  ·  every pitch ratio exact', { size: 22, weight: '400', color: CSS.dim });
  hudPlane(capSlow(), 630, 508, { t0: S.rig[0], t1: S.chord[1] });
  hudPlane(capSlow(), 630, 508, { t0: S.climax[0], t1: S.climax[1] });
  // end card
  hudPlane(textCanvas('THE SHAPE OF FÜR ELISE', { size: 66, spacing: 12, glow: 'rgba(255,209,102,0.45)' }), 0, 0, { top: 500, t0: 57.6, t1: 63, fin: 1.2 });
  hudPlane(textCanvas('L. van Beethoven  ·  Für Elise, WoO 59  ·  every note drawn as a vector', { size: 26, weight: '400', color: CSS.dim }), 0, 0, { top: 392, t0: 58.3, t1: 63, fin: 1.2 });
  hudPlane(textCanvas('HARMONY IS A SHAPE', { size: 72, spacing: 10, glow: 'rgba(155,92,246,0.45)' }), 0, 0, { top: 500, t0: S.chord[0] + 0.3, t1: S.chord[0] + 4.0, slam: true });
  hudPlane(svg.eq_chord, 0, 0, { top: 500, t0: S.chord[0] + 4.3, t1: S.chord[1] - 0.4, wipe: 1.0, scale: 0.85 });
  hudPlane(textCanvas('SAME NOTE  ·  A3  ·  220 Hz  ·  DIFFERENT CHAIN', { size: 46, spacing: 4 }), 0, 0, { top: 505, t0: S.chains[0] + 0.3, t1: S.chains[0] + 3.4, slam: true });
  hudPlane(svg.eq_series, 0, 0, { top: 515, t0: S.chains[0] + 3.6, t1: S.chains[1] - 0.4, wipe: 1.2, scale: 0.8 });
  hudPlane(textCanvas('overtone strengths measured from the recorded samples', { size: 24, weight: '400', color: CSS.dim }), 0, -505, { t0: S.chains[0] + 0.5, t1: S.chains[1] - 0.3 });
  hudPlane(svg.eq_fourier, 0, 0, { top: 505, t0: S.climax[0] + 0.5, t1: S.climax[1] - 0.2, wipe: 1.6, scale: 0.85 });

  // ------------------------------------------------------------ camera
  const camPos = new THREE.Vector3(), camLook = new THREE.Vector3();
  function rollCam(t, wide) {
    // stand just ahead of "now" and look back along time: each note is born at the front and streams away
    const z = -t * ZS;
    return wide ? [new THREE.Vector3(-1.2, 2.6, z - 6.4), new THREE.Vector3(1.0, 0.2, z + 5.0)]
                : [new THREE.Vector3(-0.9, 1.6, z - 4.6), new THREE.Vector3(1.0, 0.0, z + 3.6)];
  }
  const flat = [new THREE.Vector3(0.4, 0, 9.4), new THREE.Vector3(0.4, 0, 0)];

  function update(t) {
    const kRig = Math.max(win(t, S.open[0] - 1, S.rig[1], 0.5, 0.6), win(t, S.coda[0], 99, 0.6, 0.5));
    const kRoll = Math.max(win(t, S.roll[0], S.roll[1], 0.6, 0.6), win(t, S.climax[0], S.climax[1], 0.6, 0.6));
    const kChord = win(t, S.chord[0], S.chord[1], 0.6, 0.6), kChains = win(t, S.chains[0], S.chains[1], 0.6, 0.6);
    drawRig(t, ['RH'], kRig);
    drawRoll(t, kRoll, t < S.chord[0] ? ['RH', 'LH'] : ['RH', 'LH', 'STR', 'VC', 'HN']);
    drawChords(t, kChord);
    drawChains(t, kChains);
    drawEntrances(t, { rig: kRig, roll: kRoll, chord: kChord, chains: kChains });
    let cam = flat;
    const secOf = [S.open, S.rig, S.chord, S.chains, S.coda].find((w) => t >= w[0] && t < w[1]) || S.rig;
    const dolly = ease((t - secOf[0]) / (secOf[1] - secOf[0]));
    if (secOf === S.open) cam = [new THREE.Vector3(0.4, 0, 9.4), new THREE.Vector3(0.4, 0, 0)];
    else cam = [new THREE.Vector3(0.4 + 0.35 * Math.sin(0.21 * t), 0.15 * Math.sin(0.17 * t), 9.9 - 0.9 * dolly), new THREE.Vector3(0.4, 0, 0)];
    if (secOf === S.rig && t < S.rig[0] + 1.2) { const a = ease((t - S.rig[0]) / 1.2); cam[0].lerp(new THREE.Vector3(0.4, 0, 9.4), 1 - a); }
    if (t >= S.roll[0] && t < S.roll[1]) cam = rollCam(t, false);
    if (t >= S.climax[0] && t < S.climax[1]) { const n = rollCam(t, false), w = rollCam(t, true), a = ease((t - S.climax[0]) / 4.5);
      cam = [n[0].lerp(w[0], a), n[1].lerp(w[1], a)]; }
    camera.position.copy(cam[0]); camera.lookAt(cam[1]);
    for (const it of items) {
      const a = win(t, it.t0, it.t1, it.fin, it.fout), m = it.m; m.visible = a > 0.003; if (!m.visible) continue;
      m.material.opacity = a; let s = 1;
      if (it.slam) { const r = clamp01((t - it.t0) / 0.3); s = 1 + 0.3 * (1 - r) * (1 - r); }
      m.scale.set(s, s, 1); m.position.x = it.x;
      if (it.wipe) { const f = Math.max(0.001, ease((t - it.t0) / it.wipe)); m.material.map.repeat.x = f; m.scale.x = f * s; m.position.x = it.x - it.w / 2 * (1 - f); }
    }
  }
  return { scene, camera, hud, hudCam, update, bloom: 0.75, bloomRadius: 0.45, bloomThreshold: 0.18,
    facts: { notes: EV.length, end: score.end + T0, sections: score.sections.map((s) => [s.name, +(s.t + T0).toFixed(2)]) } };
}
