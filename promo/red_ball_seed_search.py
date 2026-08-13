"""Find a seed whose red ball is genuinely hard to follow.

Hard means two things, and both are measurable:
  - it ROAMS (mean distance from its own average position is large), so it
    cannot be found by just staring at one part of the circle
  - it gets CROWDED often (another ball passes within a few ball-radii), which
    is the thing that actually makes the eye jump to the wrong one
"""
import numpy as np

FPS, R, BR, SPEED = 60, 1.0, 0.075, 0.60
N, RED = 9, 0
FRAMES = 1400
GAME0, GAME1 = 300, 1260          # the stretch that is shown all-white


def start(rng):
    """Place N balls inside, decently separated. Bounded attempts — a bad draw
    gives up and the seed is skipped rather than spinning forever."""
    p = []
    for _ in range(4000):
        q = rng.uniform(-0.80, 0.80, 2)
        if np.linalg.norm(q) > 0.80:
            continue
        if all(np.linalg.norm(q - o) > 0.26 for o in p):
            p.append(q)
            if len(p) == N:
                return np.array(p)
    return None


def sim(seed):
    rng = np.random.default_rng(seed)
    p = start(rng)
    if p is None:
        return None
    a = rng.uniform(0, 2 * np.pi, N)
    v = SPEED * np.stack([np.cos(a), np.sin(a)], 1)
    path = np.empty((FRAMES, N, 2))
    worst_speed = worst_refl = worst_r = 0.0
    bounces = np.zeros(N, int)
    dt = 1.0 / FPS
    for f in range(FRAMES):
        p = p + v * dt
        d = np.linalg.norm(p, axis=1)
        hit = d > R - BR
        if hit.any():
            n = p[hit] / d[hit, None]
            vb = v[hit]
            p[hit] = n * (R - BR)
            va = vb - 2 * (vb * n).sum(1)[:, None] * n
            worst_refl = max(worst_refl,
                             float(np.abs((vb * n).sum(1) + (va * n).sum(1)).max()))
            v[hit] = va
            bounces[hit] += 1
        path[f] = p
        worst_speed = max(worst_speed,
                          float(np.abs(np.linalg.norm(v, axis=1) - SPEED).max()))
        worst_r = max(worst_r, float(np.linalg.norm(p, axis=1).max()))
    return path, worst_speed, worst_r, worst_refl, bounces


best = None
for seed in range(150):
    out = sim(seed)
    if out is None:
        continue
    path, ws, wr, wf, bounces = out
    if ws > 1e-12 or wr > R - BR + 1e-9 or wf > 1e-12:
        continue
    game = path[GAME0:GAME1]
    d = np.linalg.norm(game[:, RED][:, None, :] - game, axis=-1)
    d[:, RED] = 9.9
    near = int((d.min(1) < 3.0 * BR).sum())
    spread = float(np.linalg.norm(game[:, RED] - game[:, RED].mean(0),
                                  axis=1).mean())
    # the red ball must not be the odd one out on bounce count either
    med = float(np.median(bounces))
    if spread < 0.34 or abs(bounces[RED] - med) > 3:
        continue
    if best is None or near > best[1]:
        best = (seed, near, round(spread, 3), int(bounces[RED]), med)
        print("  candidate:", best, flush=True)

print("BEST:", best)
