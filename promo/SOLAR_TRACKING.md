# capture = cos θ — a $10,000 roof panel

Episode 1 of **"WHERE MATH ACTUALLY GETS USED"** — the sequel series to
"WHY DID WE LEARN THIS?". Same shell: the number is pinned at the **top of
the frame for the whole video**.

- **Output:** 1080×1920, 60fps, **60.000000s** — 150 beats = 37.5 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The spine

```
capture = cos θ
```

Lambert's cosine law: sunlight hitting a panel at angle θ off its normal
delivers power proportional to cos θ — not the full intensity. A fixed
roof panel doesn't face the sun all day; a tracking mount rotates to keep
θ near zero.

---

## The exact number

```
fixed panel,  θ = 60°:  cos 60° = 0.5   -> 50% capture
tracking,     θ =  0°:  cos  0° = 1.0   -> 100% capture
```

cos 60° is exactly one half — not a rounded approximation. Moving θ from
60° to 0° doesn't just improve capture, it **exactly doubles it**. At a
fixed $/kWh, that's a fixed panel earning ~$500/yr versus a tracked one
earning ~$1,000/yr on the same roof.

### Verified at import

```
cos 60° == 0.5 to 1e-9      cos 0° == 1.0 to 1e-9
capture ratio == 2.0 exactly — the "doubles" claim isn't rounded
```

---

## Structure

| Beats | |
| --- | --- |
| 0–12 | **capture = cos θ** — *a $10,000 roof panel* |
| 12–44 | Fixed panel: θ=60°, cos 60°=0.5, ~$500/yr |
| 44–96 | Tracking panel: θ=0°, cos 0°=1.0, ~$1,000/yr |
| 96–117 | *cos 60° is exactly one half — that's the whole tracking-mount pitch* |
| 117–132 | *This is why we learned cos θ. Tracking panels literally double revenue.* |
| 132–138 | share ask |
| 138–150 | The eye |

---

## Caption

```
capture = cos θ. A $10,000 roof panel — one number doubles what it earns.

A fixed panel: the sun sits 60° off its face. cos 60° = 0.5. Only half the
sunlight lands. About $500 a year.

A tracking mount rotates to face the sun directly. θ = 0°. cos 0° = 1.0.
Full sunlight. About $1,000 a year.

cos 60° is exactly one half. That's not an estimate — moving from 60° to
0° exactly doubles the capture, and the revenue.

This is why we learned cos θ. Tracking panels literally double revenue.

#maths #mathtok #solar #renewableenergy #business #trigonometry #satisfying
```

**YouTube title:** `The one-number reason solar tracking mounts double your revenue`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl solar_tracking.py SolarTracking -w -r 1080x1920
python3 cinegrade.py videos/SolarTracking.mp4 solar_tracking.mp4
```

## Changing it

`RATIO` is derived from `COS60`/`COS0` at import and asserted to equal 2.0.
Swap the angles and the revenue figures follow the same ratio.
