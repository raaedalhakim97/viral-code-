# sideways = T sin θ — a 1,000 kg crane lift

Episode 2 of **"WHERE MATH ACTUALLY GETS USED"**. Same shell: the number is
pinned at the **top of the frame for the whole video**.

- **Output:** 1080×1920, 60fps, **60.000000s** — 150 beats = 37.5 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The spine

```
sideways = T sin θ
```

A crane's lifting cable carries tension T. If the cable leans θ off true
vertical, that tension splits: `T cos θ` holds the load up, `T sin θ` pulls
it — and the crane — **sideways**. Riggers calculate this before every
lift, because sideways force is what tips an unanchored crane.

---

## The exact number

```
straight up,  θ =  0°:  sin  0° = 0     -> 0 kg sideways
leaning,      θ = 30°:  sin 30° = 0.5   -> 500 kg sideways
```

sin 30° is exactly one half. On a 1,000 kg lift, a 30° lean puts 500 kg of
pure sideways pull on the rigging — half the entire load, doing nothing to
hold it up.

### Verified at import

```
sin 0° == 0.0 to 1e-9        sin 30° == 0.5 to 1e-9
sideways force at 30° == 500 kg — exactly half the 1,000 kg load
```

---

## Structure

| Beats | |
| --- | --- |
| 0–12 | **sideways = T sin θ** — *a 1,000 kg crane lift* |
| 12–44 | Straight up: θ=0°, sin 0°=0, 0 kg sideways |
| 44–96 | Leaning 30°: sin 30°=0.5, 500 kg sideways |
| 96–117 | *sin 30° is exactly one half — riggers run this before every lift* |
| 117–132 | *This is why we learned sin θ. Riggers calculate it before every lift.* |
| 132–138 | share ask |
| 138–150 | The eye |

---

## Caption

```
sideways = T sin θ. A 1,000 kg crane lift — one angle decides if it tips.

Cable straight up, θ = 0°. sin 0° = 0. Every kilogram of tension holds the
load up. Nothing pulling the crane off balance.

Now the cable leans 30° off vertical. sin 30° = 0.5. Half the tension now
pulls sideways. 500 kg — half the load's weight — doing nothing to hold it
up.

That's what tips an unanchored crane. Riggers run this number before every
single lift.

This is why we learned sin θ.

#maths #mathtok #construction #safety #engineering #trigonometry #satisfying
```

**YouTube title:** `The angle that tips a crane — 500 kg of sideways force from sin 30°`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl crane_rigging.py CraneRigging -w -r 1080x1920
python3 cinegrade.py videos/CraneRigging.mp4 crane_rigging.mp4
```

## Changing it

`LOAD_KG` and the lean angle at the top — the sideways-force assertion
uses a `1e-6` tolerance (not exact equality) because `math.sin` of a
non-multiple-of-90° angle is never bit-exact in floating point, even when
the true value is a clean fraction like 1/2.
