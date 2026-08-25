# d² = a² + b² − 2ab cos C — two delivery stops, one warehouse

Episode 5 of **"WHERE MATH ACTUALLY GETS USED"**. Same shell: the number is
pinned at the **top of the frame for the whole video**. Callback: this is
the same formula proved from first principles in `law_of_cosines.py` —
here it's the actual tool logistics companies run to consolidate stops.

- **Output:** 1080×1920, 60fps, **60.000000s** — 150 beats = 37.5 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The spine

```
d² = a² + b² − 2ab cos C
```

A hub H has two stops: A is 8 km out, B is 5 km out, and the angle between
those two routes (measured at the hub) is 60°. Instead of driving back to
the hub between them, go straight from A to B.

---

## The exact number

```
d² = 8² + 5² − 2·8·5·cos 60° = 89 − 40 = 49
d = 7 km
```

Via the hub: 8 + 5 = **13 km**. Direct: **7 km**. A **46% shorter route** —
and the integers are not a coincidence. 8, 5, 60°, 7 is a whole-number
solution to the law of cosines, chosen so the math stays exact on screen.

### Verified at import

```
cos 60° == 1/2 exactly (Fraction)     d² == 49 exactly     d == 7 exactly
saved == 6 km == 46.2% of the via-hub trip
```

---

## Structure

| Beats | |
| --- | --- |
| 0–12 | **d² = a² + b² − 2ab cos C** — *two delivery stops, one warehouse* |
| 12–44 | Hub to A: 8 km. Hub to B: 5 km. Angle: 60°. Via hub: 13 km |
| 44–96 | Direct A→B: 8²+5²−2·8·5·cos60°=49, d=7 km. 46% shorter |
| 96–117 | *8, 5, 60°, 7 — a whole-number solution, not luck* |
| 117–132 | *This is why we learned the law of cosines. Logistics runs on it, daily.* |
| 132–138 | share ask |
| 138–150 | The eye |

---

## Caption

```
d² = a² + b² − 2ab cos C. Two delivery stops, one warehouse — skip the hub,
save the trip.

Hub to A: 8 km. Hub to B: 5 km. Angle between routes: 60°. Via the hub:
8 + 5 = 13 km, out and back every time.

Skip the hub — drive A straight to B. 8² + 5² − 2·8·5·cos 60° = 49. cos 60°
is exactly one half, so the algebra is exact. d = √49 = 7 km.

13 kilometers becomes 7. 46% shorter, same two stops.

8, 5, 60°, 7 — a whole-number solution, not luck. This is literally route
optimization.

This is why we learned the law of cosines. Logistics companies run on it,
daily.

#maths #mathtok #logistics #routeoptimization #business #trigonometry #satisfying
```

**YouTube title:** `The law of cosines makes this delivery route 46% shorter`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl route_consolidation.py RouteConsolidation -w -r 1080x1920
python3 cinegrade.py videos/RouteConsolidation.mp4 route_consolidation.mp4
```

## Changing it

`HA, HB, ANG` at the top — any whole-number law-of-cosines solution at a
60°, 90°, or 120° angle (where `cos` is a clean fraction) keeps `D2` exact
via `Fraction` and lets `D` stay an integer.
