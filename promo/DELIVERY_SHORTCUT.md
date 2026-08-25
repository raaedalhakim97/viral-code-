# 3² + 4² = 5² — a delivery courier's route

Episode 3 of **"WHERE MATH ACTUALLY GETS USED"**. Same shell: the number is
pinned at the **top of the frame for the whole video**.

- **Output:** 1080×1920, 60fps, **60.000000s** — 150 beats = 37.5 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The spine

```
3² + 4² = 5²
```

A courier on a city grid can only legally drive along streets: 3 blocks
over, 4 blocks up, 7 blocks total. A straight path — a bike lane, an alley,
a park crossing — cuts the corner. The diagonal is exactly 5 blocks, by the
smallest whole-number right triangle there is.

---

## The exact number

```
streets:   3 + 4 = 7 blocks
diagonal:  sqrt(3² + 4²) = 5 blocks
```

7 down to 5 is a **28.6% shorter trip** — not an estimate, the exact ratio
of a genuine Pythagorean triple. Multiply by thousands of deliveries a day
and this is the actual reason routing apps score a path with a shortcut
higher than one without.

### Verified at import

```
3² + 4² == 5²                genuine Pythagorean triple
saved == 2 blocks exactly    28.6% shorter, not rounded up
```

---

## Structure

| Beats | |
| --- | --- |
| 0–12 | **3² + 4² = 5²** — *a delivery courier's route* |
| 12–44 | Streets only: 3 over + 4 up = 7 blocks |
| 44–96 | The diagonal shortcut: √(3²+4²) = 5 blocks, 28.6% shorter |
| 96–117 | *the smallest whole-number right triangle there is — real fuel and time* |
| 117–132 | *This is why we learned Pythagoras. Every routing app scores around it.* |
| 132–138 | share ask |
| 138–150 | The eye |

---

## Caption

```
3² + 4² = 5². A delivery courier's route — one shortcut, 2 fewer blocks.

Along streets: 3 blocks over, 4 blocks up. 7 blocks. That's the only legal
route.

But a bike lane cuts straight across. √(3² + 4²) = 5 blocks. The diagonal
isn't a guess — it's exact.

7 blocks becomes 5. Two fewer, every single trip. 28.6% shorter.

The smallest whole-number right triangle there is, on a million deliveries
a day. That's not a rounding error — that's real fuel and time.

This is why we learned Pythagoras.

#maths #mathtok #logistics #delivery #routing #geometry #satisfying
```

**YouTube title:** `Pythagoras cuts 2 of every 7 delivery blocks — the real math behind routing apps`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl delivery_shortcut.py DeliveryShortcut -w -r 1080x1920
python3 cinegrade.py videos/DeliveryShortcut.mp4 delivery_shortcut.mp4
```

## Changing it

`A, B, C` at the top — any Pythagorean triple. The assertions confirm the
triple is genuine and recompute the exact saved-blocks fraction with
`Fraction`, refusing to build if the "28.6%" claim drifts.
