# sin(90° − θ) = cos θ — why is it called CO-sine?

Companion to `cofunction.py`. Continues **"WHY DID WE LEARN THIS?"**, same
shell, same 3-4-5 triangle as `soh_cah_toa.py` — equation pinned at the
**top of the frame for the whole video**.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The spine

```
sin(90° − θ) = cos θ
```

Nobody ever explains the name. This video's entire job is to make the name
stop being arbitrary.

---

## One triangle, both acute angles — not just one

Every right triangle has two acute angles, and they always sum to 90°. Every
previous episode marked one of them and ignored the other. This one draws
**both**, on the same 3-4-5 triangle used in `soh_cah_toa.py`:

```
θ:  the marked angle           φ = 90° − θ:  its complement
```

---

## What swaps and what doesn't

θ's opposite side is φ's adjacent side, and vice versa — the hypotenuse is
the only side both angles share. Swap opposite and adjacent and the ratios
swap with them:

```
θ:  sin θ = 3/5     cos θ = 4/5
φ:  sin φ = 4/5     cos φ = 3/5
```

`sin φ` and `cos θ` are not *similar* — they are the **exact same fraction,
4/5, read off the exact same side**. That's not a coincidence to memorise.
It's what "the sine of the OTHER angle" literally means — and it's the whole
reason the second ratio is called co-(mplementary)-sine.

### Verified at import

```
θ's opposite is φ's adjacent, and vice versa    swapped, not recomputed
sin φ == cos θ  and  cos φ == sin θ              the exact same fractions
θ + φ really do sum to a right angle             90°, not close to it
```

---

## Structure

| Beats | |
| --- | --- |
| 0–8 | **sin(90° − θ) = cos θ** — *why is it called CO-sine?* |
| 8–26 | One triangle, both acute angles marked: θ and φ = 90° − θ |
| 26–62 | sin θ = 3/5, cos θ = 4/5 · sin φ = 4/5, cos φ = 3/5 · sin φ = cos θ |
| 62–78 | φ is ninety minus θ. *"the sine of the complement." co-sine.* |
| 78–88 | *We learned this at school. Nobody ever said what for.* |
| 88–92 | share ask |
| 92–100 | The eye |

---

## Caption

```
sin(90° − θ) = cos θ. Why is it called CO-sine?

Every right triangle has two acute angles. They always add to 90°. Nobody
ever draws both. This one does — θ, and its complement, φ.

For θ: opposite is 3, adjacent is 4. sin θ = 3/5, cos θ = 4/5.

For φ, the same two sides swap roles. sin φ = 4/5, cos φ = 3/5.

Now look: sin φ = 4/5 = cos θ. The exact same fraction. The exact same
side.

φ is ninety degrees minus θ. So sin(90° − θ) = cos θ.

"The sine of the complement." Co-sine. That's the whole name.

We learned this at school. Nobody ever said what for.

#maths #mathtok #trigonometry #cosine #geometry #school #satisfying
```

**YouTube title:** `Why is it called CO-sine? One triangle, both angles, one swap`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl cofunction.py Cofunction -w -r 1080x1920
python3 cinegrade.py videos/Cofunction.mp4 cofunction.mp4
```

## Changing it

`OPP, ADJ, HYP` at the top — any Pythagorean triple. The assertions
recompute `sin`/`cos` for both θ and its complement φ as exact `Fraction`s
and refuse to build unless `sin φ == cos θ` and `cos φ == sin θ` hold
exactly, and unless θ and φ truly sum to a right angle.
