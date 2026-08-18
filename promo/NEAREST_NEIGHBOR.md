# How does AI draw a line between yes and no?

Companion to `nearest_neighbor.py`. Second of the five "trendy" AI-math videos
— from the trend-research doc's Voronoi-diagram pick, reframed as what it
actually is: a 1-nearest-neighbour classifier.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The identity this video is built on

A Voronoi diagram and a 1-nearest-neighbour classifier are not similar things —
they are **the same picture**. Colour every point in a plane by whichever of a
fixed set of examples it's closest to, and the cell boundaries that appear are
Voronoi edges. There is no model, no training, no loss function. "Which example
is closest" is the entire algorithm.

---

## Nine fixed points, one measured fact

Nine points (`np.random.default_rng(130)`), five gold and four sky, sit in a
plane. Colouring a 24×24 raster by nearest example produces the full decision
surface.

The points aren't arbitrary — that seed was chosen because it puts a Voronoi
**vertex** (where three cells meet) cleanly inside the frame. That vertex is not
decorative: it is measurably **0.744392 units from three different examples**,
to six decimal places, which is exactly why the boundary has a corner there
rather than a smooth curve.

```
distance to seed 1 (sky):  0.744392
distance to seed 5 (sky):  0.744392
distance to seed 8 (gold): 0.744392
```

### Verified at import

```
the flagged vertex really is a Voronoi vertex     scipy computes it, not us
it is equidistant from three DIFFERENT seeds       to better than 1e-6
the new point changes a visible slice of the map   9%, not nothing, not everything
every raster cell's colour equals its true nearest-seed class   no shortcuts
```

That last check matters most: `nearest_class()` is the one function that
decides every colour on screen, and the assertion re-runs it and compares
against what the video is about to draw. There is no separate "for the
animation" shortcut version of the classifier.

---

## Then one new example, and the map redraws itself

A tenth point drops into what was gold territory, tagged sky. **9% of the
raster changes colour.** That's the whole story of why nearest-neighbour needs
zero training time: there was never a model to retrain. Every "decision" is
made at the moment you ask, by measuring distance to the examples you already
have. Add an example and the map updates instantly — not because anything
learned something, but because the measurement changed.

> **nothing was retrained. nothing has a gradient.**
> **it only ever measured distance to what it had seen.**

---

## Structure

| Beats | |
| --- | --- |
| 0–8 | **HOW DOES AI DRAW A LINE BETWEEN YES AND NO?** — *it measures distance* |
| 8–22 | Nine points, two colours, no labels drawn |
| 22–42 | The raster fills in. *that picture is a nearest-neighbour classifier* |
| 42–58 | The tri-cell vertex: **0.744 = 0.744 = 0.744**, exactly |
| 58–76 | A tenth point drops in. **9%** of the map changes colour |
| 76–84 | *nothing was retrained... that's a 1-nearest-neighbour classifier* |
| 84–92 | **NEAREST NEIGHBOR — follow, the math behind AI** |
| 92–100 | The eye |

---

## Caption

```
How does an AI draw a line between "yes" and "no"?

It doesn't draw a line. It measures distance.

Nine examples. Two colours. No boundary drawn anywhere — just nine points.

Now colour every OTHER point in the plane by whichever example is closest to it.
That's it. That picture you're looking at is a working classifier. Zero training.

See that point where three regions meet? I checked it: it is 0.744392 units from
three completely different examples. Not "close." Equal, to six decimal places.
That's not a coincidence — it's exactly why the boundary has a corner there.

Now watch this. One new example drops in. 9% of the map just changed colour.
Nothing was retrained. Nothing has a gradient. The map changed because the
measurement changed — that's all a nearest-neighbour classifier ever does.

Every "AI drew a boundary" picture you've seen starts here.

#maths #mathtok #ai #machinelearning #voronoi #nearestneighbor #howaiworks
```

**YouTube title:** `How does AI draw a line between yes and no? (it doesn't — it measures)`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl nearest_neighbor.py NearestNeighbor -w -r 1080x1920
python3 cinegrade.py videos/NearestNeighbor.mp4 nearest_neighbor.mp4
```

## Changing it

`SEEDS`' random seed (130), `CLASS`, and `NEW_POINT` at the top. The assertions
recompute the flagged Voronoi vertex and the redraw percentage from scratch and
refuse to build if the seed no longer produces a clean interior vertex, if the
vertex isn't genuinely equidistant, or if the new point's redraw falls outside
a visible 3–60% range.
