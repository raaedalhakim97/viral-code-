// scene_euler.js — 2,144 points fly into the Euler curve, camera orbits, bloom.
// A scene module exports build(THREE, W, H) -> { duration, update(t) } and
// owns nothing about time: the renderer calls update(t) once per frame, so
// every frame is reproducible and the video is exactly duration*fps frames.
export const FPS = 30;
export const DURATION = 8.0;

const N = 2144;
const BG = 0x05070f;

function euler(t) {
  const r = Math.exp(Math.cos(t));
  return [r * Math.cos(t), r * Math.sin(t), Math.sin(2 * t)];
}
const smooth = (x) => { x = Math.min(1, Math.max(0, x)); return x * x * (3 - 2 * x); };

// small seeded PRNG: same scatter on every render
function rng(seed) {
  let s = seed >>> 0;
  return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
}

export function build(THREE, W, H) {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(BG);
  scene.fog = new THREE.FogExp2(BG, 0.035);

  const camera = new THREE.PerspectiveCamera(38, W / H, 0.1, 200);

  // ---- the particles ------------------------------------------------------
  const rand = rng(9);
  const start = new Float32Array(N * 3);
  const target = new Float32Array(N * 3);
  const colors = new Float32Array(N * 3);
  const SCALE = 2.0, ZS = 1.3;
  for (let i = 0; i < N; i++) {
    start[i * 3]     = (rand() - 0.5) * 16;
    start[i * 3 + 1] = (rand() - 0.5) * 22;
    start[i * 3 + 2] = (rand() - 0.5) * 12;
    const c = euler((i / N) * Math.PI * 2);
    target[i * 3]     = SCALE * c[0];
    target[i * 3 + 1] = SCALE * c[1];
    target[i * 3 + 2] = SCALE * ZS * c[2];
  }
  const pos = new Float32Array(N * 3);
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

  // soft round sprite so the points read as glowing dots, not squares
  const cv = document.createElement('canvas');
  cv.width = cv.height = 64;
  const g = cv.getContext('2d');
  const grad = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  grad.addColorStop(0, 'rgba(255,255,255,1)');
  grad.addColorStop(0.35, 'rgba(255,255,255,0.55)');
  grad.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = grad; g.fillRect(0, 0, 64, 64);
  const sprite = new THREE.CanvasTexture(cv);

  const mat = new THREE.PointsMaterial({
    size: 0.2, map: sprite, vertexColors: true, transparent: true,
    depthWrite: false, blending: THREE.AdditiveBlending, sizeAttenuation: true,
  });
  const points = new THREE.Points(geo, mat);
  scene.add(points);

  // ---- the curve itself, a thin glowing tube that draws on after ----------
  const curvePts = [];
  for (let i = 0; i <= 400; i++) {
    const c = euler((i / 400) * Math.PI * 2);
    curvePts.push(new THREE.Vector3(SCALE * c[0], SCALE * c[1], SCALE * ZS * c[2]));
  }
  const curve = new THREE.CatmullRomCurve3(curvePts, true);
  const tubeGeo = new THREE.TubeGeometry(curve, 600, 0.02, 8, true);
  const tube = new THREE.Mesh(tubeGeo, new THREE.MeshBasicMaterial({
    color: 0x2ee6c8, transparent: true, opacity: 0.0, blending: THREE.AdditiveBlending,
  }));
  scene.add(tube);

  // a faint floor grid gives the parallax something to read against
  const grid = new THREE.GridHelper(40, 40, 0x1b2740, 0x0e1626);
  grid.position.y = -6.2;
  scene.add(grid);

  const A = new THREE.Color(0x3b6fd4), B = new THREE.Color(0x2ee6c8);
  const tmp = new THREE.Color();

  // timeline, seconds
  const T_FLY0 = 0.0, T_FLY1 = 4.4, T_TUBE = 4.4;
  const centre = new THREE.Vector3(1.6, 0.3, 0);

  function update(t) {
    const fly = smooth((t - T_FLY0) / (T_FLY1 - T_FLY0));
    for (let i = 0; i < N; i++) {
      // each point launches a little later than the last, so it streams in
      const k = smooth((fly * 1.35) - (i / N) * 0.35);
      for (let a = 0; a < 3; a++) {
        const j = i * 3 + a;
        pos[j] = start[j] + (target[j] - start[j]) * k;
      }
      tmp.copy(A).lerp(B, k);
      colors[i * 3] = tmp.r; colors[i * 3 + 1] = tmp.g; colors[i * 3 + 2] = tmp.b;
    }
    geo.attributes.position.needsUpdate = true;
    geo.attributes.color.needsUpdate = true;
    mat.opacity = 0.95;

    tube.material.opacity = 0.42 * smooth((t - T_TUBE) / 1.2);
    tube.visible = tube.material.opacity > 0.001;

    // camera: one slow continuous orbit with a gentle dolly-in
    const u = t / DURATION;
    const ang = -0.5 + u * Math.PI * 1.15;
    const rad = 25.0 - 3.5 * smooth(u * 1.4);
    const elev = 2.4 + 2.6 * Math.sin(u * Math.PI);
    camera.position.set(centre.x + rad * Math.sin(ang), elev, rad * Math.cos(ang));
    camera.lookAt(centre);
  }
  return { scene, camera, update };
}
