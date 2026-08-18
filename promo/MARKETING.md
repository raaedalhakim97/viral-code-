# @observer.collapse — marketing plan

Written after the 60-day analytics review, Aug 2026. This supersedes the growth
advice in `CHANNEL_BRIEF.md`, which was written before the paid-promotion split
was known and is wrong about where the bottleneck is.

---

## Scope — what this page is about, and what it is not

**Reset by the owner, Aug 2026.** The page's subject is the thing it is named
after: **observer collapse** — how an observer changes the environment it is
observing, and how what reaches an observer decides what it does.

> **An observer never acts on the world. It acts on the part of the world that
> reached it — and those are different objects.**

Everything shipped has to answer *"whose model of the world does this change,
and how would you measure it?"* If it cannot, it is a general-maths video, and
this is not a general-maths page.

**What that admits, all of it countable, none of it metaphor:**

- **occlusion and line of sight** — grids, position vectors, cross products
- **information availability** — the honest double slit: what *can* be known,
  not what a mind knows
- **delay and sampling** — the observer acts on where you were, not where you are
- **measurement cost** — to locate a thing you have to interact with it
- **the observer inside the viewer** — perception as a model, not a window

**Still in scope, because it is the same subject wearing different clothes:**
attention (a machine choosing what to look at), the dot product, `y = Wx + b`.
An AI is an observer with a measurable model, which makes it the most
convenient observer to film. It is no longer the *point* — it is one example.

**Out of scope, unchanged:** general-maths explainers with no observer in them.
`a² + b² = c²` and the screen-diagonal video stay rejected under the new rule
for the same reason they were rejected under the old one — nobody's model of the
world changes in them.

**The back catalogue is not off-brand, it is the funnel.** `red_ball`,
`the_sync`, `which_way` and the teaching episodes stay up and keep posting. They
are what brings people to a page that then shows them this. `which_way` in
particular is a straight lead-in: it ends on *your brain guessed and never told
you*, which is episode 01's thesis said sideways.

The precedent for enforcing this: `a² + b² = c²` and the screen-diagonal video
were well made, properly sourced and exact to the last digit, and were still
removed rather than left unposted — because an off-scope "Episode 2" sitting in
the repo pulls the whole series sideways. Recoverable from git history (commit
`4b0341d`) if ever wanted for a different channel.

**No AI voice.** A piper voiceover was tried on that same video and rejected on
listening: it reads as obviously synthetic, and on a page whose entire promise is
care, a cheap voice costs more than the transcript SEO it buys. Scenes ship
**silent**; the sound goes on in the TikTok editor and the searchable words live
in the caption and the `.srt`. `narrate_scene.py` stays for the long-form OIS
scenes and carries this note at the top. If narration ever comes back it is a
real human reading, not a model.

**The close depends on which series the video belongs to.**

**OBSERVER COLLAPSE** episodes close on the series card — *OBSERVER COLLAPSE /
episode one of many / follow — you are on somebody's grid* — and then the eye.
The ask here is a **follow**, not a share, and that is deliberate: these are
serial, and a viewer who understood episode 01 has a reason to want episode 02.
Nobody shares a thesis to one specific friend; they subscribe to it.

**WHY DID WE LEARN THIS?** episodes — the school series — keep their own close,
below, unchanged. It is the right ask for a video that just handed somebody
something they can teach, and it is not the right ask for this one.

First the line that series is named after — *"We learned this at school. Nobody
ever said what for."* Then, on its own beat before the sign-off:

> **Send this to your school friend — and tell them THIS is how it's solved.**

The first line is the identity. The second is the only ask, and it asks for the
one action that actually moves a page this size: **a share to one specific
person**, not a follow, not a like. It works here because the video has just
finished handing the viewer something they can teach — and the person they most
want to tell is whoever sat next to them while they were both failing to see the
point. 74 shares across 60 days is the number this line exists to move.

---

## Where the account actually is

| | |
| --- | --- |
| Posts | ~40 |
| Followers | ~101 |
| Organic views per post | **100–200**, consistently |
| Breakout posts | 5 — 15.6K, 5,693, 3,227, 2,345, 1,498 |
| 60-day totals (mostly paid) | 42.1K views, 3K likes, 96 comments, 74 shares |
| Profile views | 470 |

Two things this rules out.

**It is not suppression.** A restricted account does not produce a 15.6K video.
Distribution works; it just rarely fires.

**It is not the video format.** The 100–200 band predates every video in this
repo. Image posts, carousels and 48-second manim renders all land in the same
place. Nothing built here broke anything, and nothing built here fixed anything
either.

## The diagnosis

The account is playing the hardest available game: cold-starting a niche
educational page on the platform with the shortest content half-life and the
weakest search surface — while forty finished videos sit unused everywhere else.

TikTok decides in about 72 hours and then the post is dead. YouTube Shorts and
Reels keep surfacing evergreen explainers for months. The library is an asset
being spent on one platform.

---

## Parts or one long video — the answer is both, split by platform

Asked directly: should OBSERVER COLLAPSE ship as 40-second parts, or as one
video long enough to explain itself? **Both, and the split is not a compromise.**

**Shorts, Reels, TikTok — keep the 40-second parts.** Watch-through rate is the
dominant ranking signal, and at ~100 followers every video is discovered cold.
A two-minute cut completes at maybe 20%; a forty-second one completes at 60–80%.
Merging them would reduce how many people meet the idea at all.

**YouTube — one full cut.** YouTube ranks on watch *time*, not percentage, and a
two-minute piece is a normal format there. It is also the searchable, evergreen
asset, and the thing to link from the bio. `observer_collapse_full.mp4`,
built by `build_series.sh`: **121.6 s, 7296 frames.**

```
open 4.0 + room 34.4 + bridge 3.2 + delay 34.4 + bridge 3.2 + scan 34.4 + outro 8.0
```

Each episode is trimmed at **34.400 s — beat 86, exactly 2064 frames** — the
point where every episode in this shell hands over to its follow card. Three
sign-offs in a row is the only thing wrong with a naive concatenation, so the
long cut carries **one** signature at the end.

### Two things the parts get wrong for cold viewers, and the fix

**Drop the episode numbers from the on-screen cards.** A stranger who sees "03"
reads it as *you missed something*, which is a scroll trigger. The series name
alone identifies it; keep the numbering in captions and YouTube titles, where it
helps returning viewers instead of taxing new ones.

**Post them strongest-first, not in numerical order.** `the_scan` is the only one
that stops a scroll inside one second — a human body assembling out of laser
returns. `the_room` needs eight seconds before anything happens, which is fatal
cold and fine once someone already trusts the page. Recommended order:

```
the_scan  ->  the_delay  ->  the_room
```

Once the numbers are off the cards, order is free, and every episode is an
entry point rather than a middle chapter. Comprehension does not come from
length — it comes from each part being complete on its own and ending on the
same thesis.

---

## Move 1 — multiply surface area (this week, zero new production)

Upload the existing library to **YouTube Shorts** and **Instagram Reels**.

This is the highest-leverage action available and it requires no new work. Same
files, three to four times the shots on goal, and on YouTube each upload keeps
working for months instead of days.

Rules:

- **Upload the clean source files, never a TikTok download.** A watermark gets
  a Short throttled. Every video in this repo is watermark-free at
  `promo/<name>.mp4`; the older image posts need re-exporting from wherever
  they were made.
- **Space them out** — five to eight a day, not forty at once.
- **Best performers first**, so the channel's early signal is its strongest work.

## Move 2 — stop the paid promotion

It bought 42.1K views and close to zero durable followers, and it did something
worse: it made the analytics unreadable. Two months of data cannot answer "which
video worked" because the view counts are bought.

The information about what resonates is worth more right now than the reach.

## Move 3 — title for search, not for the feed

On TikTok a caption is decoration. On YouTube the title *is* the distribution.

Some of this library has genuine standing search demand and some has none:

| Video | Search demand | Why |
| --- | --- | --- |
| `no_calculator` (47500 ÷ 234) | **High** | People search for division tricks constantly |
| `rope_puzzle` | **High** | A famous puzzle people look up by name |
| `carwash_puzzle` | Medium | Riddle traffic, no fixed name |
| `dimensions` (1,536) | **Low** | Nobody searches this |
| `lost_in_the_middle` | Low | Term is known only inside the field |

Search-led topics compound. Trend-led topics spike and die. The mental-maths and
puzzle videos should carry the YouTube push; the AI-internals videos are for
TikTok where novelty beats searchability.

Titles are stated as the query someone would actually type:

- `47500 ÷ 234 in your head — no calculator (19 seconds)`
- `The rope around the Earth puzzle — the answer is not what you think`
- `Should you walk or drive to the car wash? Most people get this wrong`

## Move 4 — make the profile convert

470 people visited the profile and the account has ~101 followers. Every one of
those visits is expensive; the page they land on has to do work.

- The bio must say **what they get if they follow**, not what the page is about.
- The three pinned slots are the highest-value real estate on the account. Pin
  the 15.6K geometry video, the 5,693, and one recent piece — not three old ones.
- **`PART 4 / 7 "LEARNING"` is uploaded twice** (103 and 121 views). Delete one.

Suggested bio:

```
The math behind AI, drawn.
Geometry · puzzles · mental math
New video most days
```

## Move 5 — comments are the growth channel at this size

For an account under 1,000 followers this is more reliable than anything else,
and it costs time rather than money.

- **Reply to all 96 comments.** One afternoon. Every reply is a notification
  that pulls someone back, and reply threads are where profile taps come from.
- **Comment on large maths and AI accounts** — 3Blue1Brown reposts, Numberphile
  clips, big AI explainer pages. Not "great video." *Actually solve something* in
  the comment: give the second method, catch the edge case, do the arithmetic.
  A useful comment on a 500K-view video reaches more people than a post here does.

This is the one lever that works at 101 followers and stops mattering at 100,000.

## Move 6 — the algorithm already told you what it wants

The best post is circle geometry, at 15.6K. The next best visual is geometric
too, at 1,498. `CIRCLE GEOMETRY THE ADEVIC WAY` cleared the baseline at 203.

That is three separate signals pointing at the same thing, and the page has been
answering with embeddings and attention mechanisms. **Geometry is the proven
lane.** Make the AI content geometric or make it second.

---

## Two-week plan

| Days | Action |
| --- | --- |
| 1 | Kill paid promotion. Delete the duplicate PART 4/7. Rewrite bio, re-pin. |
| 1–2 | Create YouTube + Instagram accounts on the same handle. Upload the 8 best. |
| 2–10 | Upload the rest, 5–8 per day, search-led titles on the maths ones. |
| Daily | Reply to every comment. Leave 10 substantive comments on large accounts. |
| Daily | Post to TikTok as normal — but organic only, no spend. |
| 14 | Compare: TikTok vs Shorts vs Reels, views and follows per post. |

## What to measure at day 14

Not views. Views were never the problem — 42.1K of them produced nothing.

1. **Followers gained per platform.** This decides where the next month goes.
2. **Average watch time** on any one video. Still unknown, and it is the number
   that decides whether the 48-second format survives. If it is 3–5 seconds,
   everything gets re-cut to 15. If it is 20+, the format is fine.
3. **Profile visits → follows.** If this ratio is healthy, the job is purely
   getting more people to the profile. If it is poor, the profile is the problem.

---

## The honest summary

The content is not the problem. Forty posts at 100–200 views with five breakouts
is a *distribution* problem, and the fix is more surfaces and more comments —
not a better video. Building a forty-first is the most comfortable thing to do
and the least useful.
