# sales(t) = 1000 + 400 sin(t) — a swimwear shop's whole year

Episode 4 of **"WHERE MATH ACTUALLY GETS USED"**. Same shell: the number is
pinned at the **top of the frame for the whole video**.

- **Output:** 1080×1920, 60fps, **60.000000s** — 150 beats = 37.5 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The spine

```
sales(t) = 1000 + 400 · sin(2πt / 12)
```

Retail demand that repeats every year — swimwear, heaters, holiday decor —
is modeled the same way a sound wave is: a baseline plus an amplitude,
oscillating over 12 months.

---

## The exact number

```
peak month   (sin = 1):   1000 + 400 = 1,400 units
trough month (sin = -1):  1000 − 400 =   600 units
```

An 800-unit swing between the best and worst month, on the same shop. A
retailer who orders the flat average every month either runs out during
the peak or pays to warehouse 400 extra units during the trough. The sine
model says exactly how much to shift, and when.

### Verified at import

```
sales at sin=1 == 1400 exactly      sales at sin=-1 == 600 exactly
swing == 800 units — the entire gap between best and worst month
```

---

## Structure

| Beats | |
| --- | --- |
| 0–12 | **sales(t) = 1000 + 400 sin(t)** — *a swimwear shop's whole year* |
| 12–44 | Order the flat average every month? baseline = 1,000 |
| 44–96 | The real curve: peak 1,400, trough 600, swing 800 |
| 96–117 | *order flat and you either stock out or overpay rent* |
| 117–132 | *This is why we learned sine waves. Retailers forecast entire seasons with it.* |
| 132–138 | share ask |
| 138–150 | The eye |

---

## Caption

```
sales(t) = 1000 + 400 sin(t). A swimwear shop's whole year — one curve,
every order decided.

Order the same amount every month? Baseline: 1,000 units. But real demand
doesn't stay flat.

Real demand swings — a sine wave, not a line. Peak month: 1,000 + 400 =
1,400. Trough month: 1,000 − 400 = 600.

An 800-unit swing between best and worst month, same shop.

Order flat, and you either stock out or overpay rent on unsold inventory.
The wave says exactly when to shift.

This is why we learned sine waves. Retailers forecast entire seasons with
it.

#maths #mathtok #retail #forecasting #inventory #business #satisfying
```

**YouTube title:** `One sine wave forecasts a retailer's entire year of demand`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl seasonal_sales.py SeasonalSales -w -r 1080x1920
python3 cinegrade.py videos/SeasonalSales.mp4 seasonal_sales.mp4
```

## Changing it

`BASE` and `AMP` at the top control the baseline and swing; peak/trough are
recomputed and asserted exact at import (`sin(90°)=1`, `sin(270°)=-1`).
