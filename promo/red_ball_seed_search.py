"""Find a seed whose red ball is genuinely hard to follow.

Run this whenever SPEED, N or the beat layout in red_ball.py changes — the
whole simulation changes with them, and a seed that was hard at one speed is
not necessarily hard at another.

    python3 red_ball_seed_search.py

Hard is two measurable things, and red_ball.py re-asserts both at import:
  ROAMS    mean distance from its own average position — it cannot be found
           by staring at one part of the circle
  CROWDED  fraction of frames with another ball within a few ball-radii —
           this is what actually makes the eye jump to the wrong ball
"""
import numpy as np

# keep these in step with red_ball.py
FPS, R, BR, SPEED = 60, 1.0, 0.075, 0.82
N, RED_I = 9, 0
BEAT_GO, BEAT_WHITE, BEAT_STOP = 6, 11, 45
B_SEC = 60.0 / 150.0

F_WHITE = int(round((BEAT_WHITE - BEAT_GO) * B_SEC * FPS))
F_STOP = int(round((BEAT_STOP - BEAT_GO) * B_SEC * FPS))
FRAMES = F_STOP + 1


def start(rng):
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
    ws = wf = wr = 0.0
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
            wf = max(wf, float(np.abs((vb * n).sum(1) + (va * n).sum(1)).max()))
            v[hit] = va
            bounces[hit] += 1
        path[f] = p
        ws = max(ws, float(np.abs(np.linalg.norm(v, axis=1) - SPEED).max()))
        wr = max(wr, float(np.linalg.norm(p, axis=1).max()))
    return path, ws, wr, wf, bounces


def main():
    best = None
    for seed in range(200):
        out = sim(seed)
        if out is None:
            continue
        path, ws, wr, wf, bounces = out
        if ws > 1e-12 or wr > R - BR + 1e-9 or wf > 1e-12:
            continue
        game = path[F_WHITE:F_STOP]
        d = np.linalg.norm(game[:, RED_I][:, None, :] - game, axis=-1)
        d[:, RED_I] = 9.9
        crowded = float((d.min(1) < 3.0 * BR).mean())
        roam = float(np.linalg.norm(game[:, RED_I] - game[:, RED_I].mean(0),
                                    axis=1).mean())
        if roam < 0.34 or abs(bounces[RED_I] - np.median(bounces)) > 3:
            continue
        # where the red ball sits at the freeze decides its number, and a
        # number on the very edge of the reading order is a giveaway
        order = np.argsort(path[-1, :, 0])
        label = int(np.where(order == RED_I)[0][0]) + 1
        if label in (1, N):
            continue
        if best is None or crowded > best[1]:
            best = (seed, round(crowded, 3), round(roam, 3),
                    int(bounces[RED_I]), label)
            print("  candidate: seed=%d crowded=%.2f roam=%.2f answer=%d"
                  % (best[0], best[1], best[2], best[4]), flush=True)
    print("BEST:", best)


if __name__ == "__main__":
    main()
