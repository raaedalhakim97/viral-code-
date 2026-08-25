# ×5 = ×10, then ÷2 — multiply anything by 5 without multiplying

Episode 3 of **"MENTAL MATH TRICKS"**. Same shell: the rule is pinned at
the **top of the frame for the whole video**.

- **Output:** 1080×1920, 60fps, **60.000000s** — 150 beats = 37.5 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The trick

Multiplying by 5 is multiplying by 10 (instant — add a zero), then cutting
that in half.

```
48 × 5:  48 × 10 = 480.  480 / 2 = 240.
48 × 5 = 240. Matches.
```

Works at any size — even numbers you couldn't multiply by 5 directly:

```
237 × 5:  237 × 10 = 2370.  2370 / 2 = 1185.
237 × 5 = 1185. Matches.
```

### Verified at import

```
48 * 5 == 240 exactly     237 * 5 == 1185 exactly
both trick results match real multiplication exactly
```

---

## Structure

| Beats | |
| --- | --- |
| 0–12 | **×5 = ×10, then ÷2** — *multiply anything by 5* |
| 12–44 | 48×10=480, ÷2=240. Checked against 48×5 |
| 44–96 | 237×10=2370, ÷2=1185. Checked against 237×5 |
| 96–117 | *why: 5 is exactly 10÷2, always* |
| 117–132 | *Halving beats multiplying by 5. Works on any number, instantly.* |
| 132–138 | share ask |
| 138–150 | The eye |

---

## Caption

```
Multiply anything by 5 — without ever multiplying by 5.

48 × 5: add a zero, that's ×10 — instant. 48 × 10 = 480. Now cut it in
half. 480 / 2 = 240. Check it — 48 × 5 = 240. Matches.

Try a bigger one. 237 × 5: still just adding a zero, still just halving.
237 × 10 = 2370. 2370 / 2 = 1185. Check it — 237 × 5 = 1185. Still
matches.

Why? 5 is exactly 10 ÷ 2. Always. ×10 then ÷2 IS ×5, every single time.

Halving beats multiplying by 5. Works on any number, instantly.

#maths #mathtok #mentalmath #lifehacks #mathtricks #satisfying
```

**YouTube title:** `Stop multiplying by 5 — do this instead`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl trick_times_5.py TrickTimes5 -w -r 1080x1920
python3 cinegrade.py videos/TrickTimes5.mp4 trick_times_5.mp4
```

## Changing it

`N1` and `N2` at the top — any numbers. `(n*10)//2 == n*5` is asserted
for both; the halving is always exact since `n*10` always ends in 0.
