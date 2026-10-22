// Standalone check of every number the Lorenz video will put on screen.
const S = 10, R = 28, B = 8 / 3, DT = 0.005;
const f = ([x, y, z]) => [S * (y - x), x * (R - z) - y, x * y - B * z];
function rk4(p) {
  const k1 = f(p), a = p.map((v, i) => v + 0.5 * DT * k1[i]);
  const k2 = f(a), b = p.map((v, i) => v + 0.5 * DT * k2[i]);
  const k3 = f(b), c = p.map((v, i) => v + DT * k3[i]);
  const k4 = f(c);
  return p.map((v, i) => v + DT / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]));
}
// start on the attractor: burn off the transient from a generic point
let p = [1, 1, 1];
for (let i = 0; i < 4000; i++) p = rk4(p);
const EPS = 1e-9;
let a = p.slice(), b = [p[0] + EPS, p[1], p[2]];
const d = (u, v) => Math.hypot(u[0] - v[0], u[1] - v[1], u[2] - v[2]);
let split = null, wingsDiffer = null;
for (let k = 1; k <= 12000; k++) {
  a = rk4(a); b = rk4(b);
  const s = k * DT, dd = d(a, b);
  if ([5, 10, 15, 20, 25, 30].includes(Math.round(s * 1000) / 1000)) console.log(`s=${s.toFixed(1)}  distance=${dd.toExponential(2)}`);
  if (split === null && dd > 1) split = s;
  if (wingsDiffer === null && split !== null && Math.sign(a[0]) !== Math.sign(b[0]) && dd > 10) wingsDiffer = s;
}
console.log('start (on attractor):', p.map(v => v.toFixed(4)).join(', '));
console.log('distance first exceeds 1 at sim time', split.toFixed(3));
console.log('points first on opposite wings (and >10 apart) at', wingsDiffer.toFixed(3));
console.log('implied growth rate ln(1e9)/t =', (Math.log(1e9) / split).toFixed(3), '(Lorenz max Lyapunov exponent is ~0.906)');
