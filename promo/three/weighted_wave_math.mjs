// weighted_wave_math.mjs — the mathematics of SMART LOOKUP Part II, and nothing else.
// Shared by the standalone check (weighted_wave_check.mjs) and the scene, so
// what is verified is exactly what is drawn.
//
// Each word i has K = 32 weights theta_i,k. Each weight drives one sinusoid:
//
//     psi_i(x) = sum_{k=1..32} theta_i,k * sin(2*pi*f_k*x + phi_k),   x in [0, 1)
//
// x is the position along the closed Euler curve (as a fraction of a lap), so
// psi must be periodic in x: f_k = k, whole numbers. The phases phi_k are fixed;
// only theta is ever learned. The curve never changes.
//
// The word sits where its superposed wave is strongest:
//     x_i = argmax_x |psi_i(x)|,   point = C(2*pi*x_i)
//
// Training: L(theta) = -psi(x_target)^2 on the unit sphere |theta| = 1.
//     theta <- theta - eta * grad L  =  theta + 2*eta*psi(x_t) * s(x_t),  then renormalise,
// where s_k(x) = sin(2*pi*k*x + phi_k). The fixed point is theta ∝ ±s(x_t): every
// component is then in phase at x_t (all 32 terms the same sign there), which is
// the "all 32 waves align" moment, and by Cauchy-Schwarz |psi| is largest there.

export const K = 32;
export const N_WORDS = 67;
export const N_POINTS = 2144;            // Part I: 67 words x 32 components
export const SAMPLES = 2144;             // x grid used for argmax (one per Part I point)
export const STEPS = 8;                  // the 8 training pulses
export const ETA = 0.022;           // small enough that the 8 pulses show steady progress, not one jump

export function rng(seed) {
  let s = seed >>> 0;
  return () => { s = (s + 0x6D2B79F5) >>> 0; let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
const r0 = rng(20260423);
export const PHI = Array.from({ length: K }, () => r0() * 2 * Math.PI);
export const F = Array.from({ length: K }, (_, k) => k + 1);

export const s = (x) => F.map((f, k) => Math.sin(2 * Math.PI * f * x + PHI[k]));
export const psi = (theta, x) => { let v = 0; for (let k = 0; k < K; k++) v += theta[k] * Math.sin(2 * Math.PI * F[k] * x + PHI[k]); return v; };
export const norm = (v) => { const n = Math.hypot(...v); return v.map((a) => a / n); };
export function argmaxAbs(theta) {
  let best = 0, bx = 0;
  for (let j = 0; j < SAMPLES; j++) { const x = j / SAMPLES, a = Math.abs(psi(theta, x)); if (a > best) { best = a; bx = x; } }
  return { x: bx, amp: best };
}
export const circDist = (a, b) => { const d = Math.abs(a - b) % 1; return Math.min(d, 1 - d); };
export function step(theta, xt) {
  const st = s(xt), p = psi(theta, xt);
  return norm(theta.map((th, k) => th + 2 * ETA * p * st[k]));
}

// the 67 words: targets spread round the curve; WATER sits where Part I lit it
export const WATER = 0;
export const X_WATER = 15.5 / N_POINTS;            // centre of Part I's first 32 points
// "In the right place" = inside the word's own slot: Part I gave each word 32 of
// the 2,144 points, so a word owns +/-16 points around its target. A sum of 32
// waves cannot place a peak more finely than that anyway: its own width is about
// 1/32 of a lap. The trained peaks land within 6 points (checked).
export const TOL = 16 / N_POINTS;

export function buildWords() {
  const r = rng(67);
  const words = [];
  for (let i = 0; i < N_WORDS; i++) {
    const xt = i === WATER ? X_WATER : ((i + 0.5) / N_WORDS + (r() - 0.5) * 0.6 / N_WORDS + 1) % 1;
    const sn = norm(s(xt));
    let theta;
    if (i === WATER) {
      // WATER starts in its place but weakly: aligned only partly with s(x_t)
      const noise = norm(Array.from({ length: K }, () => r() * 2 - 1));
      theta = norm(sn.map((a, k) => 0.62 * a + 0.78 * noise[k]));
    } else if (i % 5 < 2) {
      // about 40% start right
      const noise = norm(Array.from({ length: K }, () => r() * 2 - 1));
      theta = norm(sn.map((a, k) => 0.8 * a + 0.6 * noise[k]));
    } else {
      theta = norm(Array.from({ length: K }, () => r() * 2 - 1));   // the rest: random, wrong
    }
    const hist = [theta];
    for (let n = 0; n < STEPS; n++) hist.push(step(hist[hist.length - 1], xt));
    words.push({ i, xt, hist, peaks: hist.map(argmaxAbs) });
  }
  return words;
}

// the two waves of the interference beat: real sinusoids, slightly different
// frequencies, so one stretch of the plane adds and another cancels
export const INTERF = { fA: 6, fB: 7, amp: 1 };
export const interfA = (x) => INTERF.amp * Math.sin(2 * Math.PI * INTERF.fA * x);
export const interfB = (x) => INTERF.amp * Math.sin(2 * Math.PI * INTERF.fB * x);
