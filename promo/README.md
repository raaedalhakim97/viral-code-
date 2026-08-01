# Share Promo — animation source

`share_promo.py` renders the "SHARE THE KNOWLEDGE" promo: an overflowing glass,
one gold accent on the first crest over the brim, closing on the observer eye,
PAUSE / OBSERVE / LEARN, and a follow CTA.

- **Output:** `videos/SharePromo.mp4` — 1440×2560 (9:16), 60fps, ~19.4s
- **Engine:** [ManimGL](https://github.com/3b1b/manim) 1.7.2 (3Blue1Brown's manim, *not* Manim Community)

## The two CTAs

The video makes two asks, in this order:

| When | Ask | Copy |
| --- | --- | --- |
| Over the glass | Share | "You understood this. Someone you know should too." |
| Final ~2s | Follow | "Follow for more AI math" + `@observercollaps` |

The follow ask is the one carrying weight right now. The page converts views
into likes far better than into follows, so reach is not the bottleneck —
view→follow is. An ending that only signs off with the brand mark spends its
most valuable seconds asking for nothing.

The CTA is white, not gold, on purpose: the first crest drop over the brim is
the only gold in the piece, and that scarcity is what makes it read as an
accent. Adding a second gold element costs more than the CTA gains.

## Render

```bash
manimgl share_promo.py SharePromo -w
```

Resolution, fps, codec and background come from `custom_config.yml` in this
directory — ManimGL picks it up automatically from the working directory, so
run the command from inside `promo/`.

On a headless machine (CI, container, server with no display), ManimGL still
needs an X display to create its GL context:

```bash
xvfb-run -a -s "-screen 0 1600x1200x24" manimgl share_promo.py SharePromo -w
```

Quick preview pass while iterating — renders in seconds instead of minutes:

```bash
manimgl share_promo.py SharePromo -w -r 360x640
```

## Setup

```bash
# system: ffmpeg for encoding, xvfb for headless GL, pango/cairo to build manimpango
apt-get update
apt-get install -y ffmpeg xvfb libegl1 libgl1 libglx-mesa0 libgl1-mesa-dri \
                   libpango1.0-dev libcairo2-dev pkg-config build-essential

pip install manimgl
```

`libpango1.0-dev` and `libcairo2-dev` are not optional — without them
`pip install manimgl` fails while building `manimpango` with
`RequiredDependencyException: pangocairo >= 1.30.0 is required`.

## Fonts

`custom_config.yml` sets the text font to **DejaVu Sans**. ManimGL's stock
default is Consolas, which is not present on Linux; without an explicit font
the captions fall back to whatever fontconfig picks and the render is not
reproducible across machines. Change the font there, not in the script.

## ManimGL 1.7.2 API gotchas

These bit this scene and are worth knowing before editing it:

| Pattern | Why it breaks | Use instead |
| --- | --- | --- |
| `Scene.set_background_color(BLACK)` | method does not exist in 1.7.2 | `self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))` |
| `Circle(color=white)` | `Circle.__init__` hardcodes `stroke_color=RED`, which wins over `color=` | `Circle(stroke_color=white)` |
| `Dot(color=gold)` | `Dot.__init__` hardcodes `fill_color=WHITE`, which wins over `color=` | `Dot(fill_color=gold)` |
| `--fps 60` on the CLI | 1.7.2 passes the flag through as a string and then divides by it — `TypeError` | set `fps` in `custom_config.yml` |

The `Circle`/`Dot` ones fail silently: the shape renders in the default colour
instead of the one asked for, so the scene "works" but comes out wrong.

## Encoding

`custom_config.yml` uses `libx264` / `yuv420p`, which is CPU encoding and plays
everywhere. On a machine with an NVIDIA GPU, swap `video_codec` to
`h264_nvenc` for a much faster render.
