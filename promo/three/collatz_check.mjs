// Standalone check of every number the Collatz video will show.
const next = (n) => (n % 2n === 0n ? n / 2n : 3n * n + 1n);
function traj(n) { const s = [n]; while (n !== 1n) { n = next(n); s.push(n); } return s; }
const t27 = traj(27n);
console.log('27: steps', t27.length - 1, ' peak', t27.reduce((a, b) => (b > a ? b : a)));
console.log('27 first values:', t27.slice(0, 12).join(', '));
let best = [0n, 0];
for (let n = 1n; n <= 10000n; n++) { const L = traj(n).length - 1; if (L > best[1]) best = [n, L]; }
console.log('longest under 10,000:', best[0], 'with', best[1], 'steps');
console.log('2^68 =', (2n ** 68n).toLocaleString('en-US'));
// tree size if we draw 1..10000 (union of all trajectories)
const nodes = new Set(); let maxv = 0n;
for (let n = 1n; n <= 10000n; n++) for (const v of traj(n)) { nodes.add(v); if (v > maxv) maxv = v; }
console.log('distinct numbers visited by 1..10000:', nodes.size, ' largest value reached:', maxv.toLocaleString('en-US'));
