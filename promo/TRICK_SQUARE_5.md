# n5² always ends in 25 — square any number ending in 5

Episode 2 of **"MENTAL MATH TRICKS"**. Same shell: the rule is pinned at
the **top of the frame for the whole video**.

- **Output:** 1080×1920, 60fps, **60.000000s** — 150 beats = 37.5 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The trick

Any number ending in 5, squared, always ends in 25. The digits before that
25: take the leading part, multiply it by itself plus one.

```
35: leading part is 3. 3 × 4 = 12. Answer: 1225.
35 × 35 = 1225. Matches.
```

A bigger example, to prove it isn't a coincidence for small numbers:

```
95: leading part is 9. 9 × 10 = 90. Answer: 9025.
95 × 95 = 9025. Matches.
```

### Verified at import

```
35² == 1225 exactly     95² == 9025 exactly
both trick results match real squaring exactly
```

---

## Structure

| Beats | |
| --- | --- |
| 0–12 | **n5² always ends in 25** — *square any number ending in 5* |
| 12–44 | 35: 3×4=12 → 1225. Checked against 35×35 |
| 44–96 | 95: 9×10=90 → 9025. Checked against 95×95 |
| 96–117 | *why: (10a+5)² = 100·a·(a+1) + 25, always* |
| 117–132 | *Try it on any number ending in 5. The last two digits are always 25.* |
| 132–138 | share ask |
| 138–150 | The eye |

---

## Caption

```
Square any number ending in 5, instantly. It always ends in 25.

35: the leading part is 3. Take 3 × (3+1) = 12. Stick 25 on the end: 1225.
Check it — 35 × 35 = 1225. Matches.

Try a bigger one. 95: leading part 9. 9 × 10 = 90. Answer: 9025.
Check it — 95 × 95 = 9025. Still matches.

Why? (10a+5)² = 100·a·(a+1) + 25. The algebra always ends in +25.

Try it on any number ending in 5. The last two digits are always 25.

#maths #mathtok #mentalmath #lifehacks #mathtricks #satisfying
```

**YouTube title:** `Square any number ending in 5 in 2 seconds — no calculator`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl trick_square_5.py TrickSquare5 -w -r 1080x1920
python3 cinegrade.py videos/TrickSquare5.mp4 trick_square_5.mp4
```

## Changing it

`N1`/`A1` and `N2`/`A2` at the top — any numbers ending in 5.
`sq5_trick()` is asserted to match real squaring for both.
