// Checks every mathematical claim Part II makes, before a single frame renders.
import * as M from './weighted_wave_math.mjs';

const ok = (c, msg) => { if (!c) { console.error('FAIL:', msg); process.exitCode = 1; } else console.log('ok  ', msg); };
const W = M.buildWords();
ok(M.N_WORDS * M.K === M.N_POINTS, `67 words x 32 weights = ${M.N_WORDS * M.K} = Part I's 2,144 points`);
ok(M.F.every((f) => Number.isInteger(f)), 'every frequency is a whole number, so psi is periodic on the closed curve');
{ const th = W[0].hist[0]; ok(Math.abs(M.psi(th, 0.123) - M.psi(th, 1.123)) < 1e-9, 'psi(x) = psi(x + 1): one lap of the curve'); }

const right = (w, n) => M.circDist(w.peaks[n].x, w.xt) <= M.TOL;
const before = W.filter((w) => right(w, 0)).length, after = W.filter((w) => right(w, M.STEPS)).length;
ok(before > 0 && before < M.N_WORDS, `before training: ${before}/67 words sit in the right place (some right, some wrong)`);
ok(after === M.N_WORDS, `after ${M.STEPS} gradient steps: ${after}/67 sit in the right place`);
const water = W[M.WATER];
ok(right(water, 0), "WATER's peak is already in its place at the start (its dot in Part I)");
const align = (th) => { const st = M.s(water.xt); return th.filter((a, k) => Math.sign(a * st[k]) === Math.sign(M.psi(th, water.xt))).length; };
ok(align(water.hist[0]) < 32, `WATER before: ${align(water.hist[0])}/32 of its waves push the same way at its peak`);
ok(align(water.hist[M.STEPS]) === 32, `WATER after: ${align(water.hist[M.STEPS])}/32: all its waves align at the peak`);
ok(water.peaks[M.STEPS].amp > water.peaks[0].amp * 1.25, `WATER's peak grows ${(water.peaks[M.STEPS].amp / water.peaks[0].amp).toFixed(2)}x as it aligns`);
// monotone: training never makes psi(x_t)^2 worse, for every word
let mono = true;
for (const w of W) for (let n = 0; n < M.STEPS; n++) if (M.psi(w.hist[n + 1], w.xt) ** 2 < M.psi(w.hist[n], w.xt) ** 2 - 1e-12) mono = false;
ok(mono, 'every step lowers L = -psi(x_t)^2 for every word (gradient descent, no cheating)');
// interference: the same two sinusoids give a constructive stretch and a cancelled stretch
const sum = (x) => M.interfA(x) + M.interfB(x);
let hi = 0, lo = Infinity, hiX = 0, loX = 0;
for (let j = 0; j < 2000; j++) {
  const x = j / 2000; let env = 0;
  for (let d = -40; d <= 40; d++) env = Math.max(env, Math.abs(sum(x + d / 2000 / 7)));   // local envelope
  if (env > hi) { hi = env; hiX = x; } if (env < lo) { lo = env; loX = x; }
}
ok(hi > 1.9 && lo < 0.25, `interference: envelope reaches ${hi.toFixed(2)} (constructive, near 2) at x=${hiX.toFixed(2)} and ${lo.toFixed(2)} (cancelled) at x=${loX.toFixed(2)}`);
{ const miss = Math.max(...W.map((w) => M.circDist(w.peaks[M.STEPS].x, w.xt) * M.N_POINTS));
  ok(miss <= 6, `after training, the worst peak sits ${miss.toFixed(1)} points from its target (slot is +/-16)`); }
console.log('words per step in the right place:', W[0].hist.map((_, n) => W.filter((w) => right(w, n)).length).join(' '));
