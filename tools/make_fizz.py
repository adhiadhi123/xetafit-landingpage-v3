"""
Generates the hero carbonation markup (deterministic: the HTML only changes when a
setting here changes) and writes it into index.html between the fizz-field tags.

    python tools/make_fizz.py           # rewrite the hero field in index.html
    python tools/make_fizz.py --print   # print the markup and the stats only

Only the hero carries bubbles. Each bubble is an <i> with its own:
  --x  horizontal position (% of the hero)       --y  start height (% from the bottom)
  --h  rise distance (cqh, % of the field height) --s  diameter (px)
  --d  duration of one rise                       --t  negative delay (mid-flight at load)
  --o  peak opacity                               --w  sideways drift (px)
css/animations.css (fizz-rise, fizz-drift) moves it.

New bubbles per second = sum(1 / duration). The target is 18-22 per second;
the stats line printed below reports the actual figure (and the mobile figure,
where every third bubble is hidden).
"""
import random
import re
import sys
from pathlib import Path

SEED = 2611
COUNT = 136
STREAMS = 5                 # loose chains from "nucleation points", 4 bubbles each
SIZES = [                   # share, px range, opacity range, speed (cqh / s)
    (0.60, (4.0, 5.0), (0.82, 1.00), (5.5, 8.0)),     # small
    (0.30, (7.0, 9.0), (0.72, 0.92), (7.0, 10.0)),    # medium
    (0.10, (11.0, 14.0), (0.62, 0.82), (8.5, 11.5)),  # large
]


def pick_size(rnd):
    u, acc = rnd.random(), 0.0
    for share, s, o, v in SIZES:
        acc += share
        if u <= acc:
            return s, o, v
    return SIZES[-1][1:]


def start_height(rnd):
    # more bubbles in the lower and middle parts of the hero
    u = rnd.random()
    if u < 0.50:
        return rnd.uniform(0, 10)
    if u < 0.85:
        return rnd.uniform(10, 40)
    return rnd.uniform(40, 60)


def bubble(rnd, x=None, y=None, size=None):
    s_rng, o_rng, v_rng = size or pick_size(rnd)
    s = rnd.uniform(*s_rng)
    x = rnd.uniform(1.5, 98.5) if x is None else x
    y = start_height(rnd) if y is None else y
    h = min(rnd.uniform(32, 78), 94 - y)
    d = h / rnd.uniform(*v_rng)
    return dict(x=x, y=y, h=h, s=s, d=d, t=-rnd.uniform(0, d), o=rnd.uniform(*o_rng),
                w=rnd.uniform(2.0, 7.0) * rnd.choice((-1, 1)), k=rnd.choice(("b1", "b2", "b3")))


def field():
    rnd = random.Random(SEED)
    out = []
    for _ in range(STREAMS):                       # chains: same spot, staggered starts
        sx, small = rnd.uniform(4, 96), SIZES[0][1:]
        first = bubble(rnd, x=sx, y=rnd.uniform(0, 4), size=small)
        for j in range(4):
            b = bubble(rnd, x=sx + rnd.uniform(-0.6, 0.6), y=first["y"], size=small)
            b["h"], b["d"] = first["h"], first["d"] * rnd.uniform(0.94, 1.06)
            b["t"] = -(first["d"] * (j + rnd.uniform(0.15, 0.55)) / 4)
            out.append(b)
    while len(out) < COUNT:
        out.append(bubble(rnd))
    rnd.shuffle(out)
    return out


def markup(bubbles):
    return "\n".join(
        f'    <i class="{b["k"]}" style="--x:{b["x"]:.1f}%;--y:{b["y"]:.1f}%;--h:{b["h"]:.0f}cqh;'
        f'--s:{b["s"]:.1f}px;--d:{b["d"]:.2f}s;--t:{b["t"]:.2f}s;--o:{b["o"]:.2f};--w:{b["w"]:.1f}px"></i>'
        for b in bubbles)


def stats(bubbles):
    rate = sum(1 / b["d"] for b in bubbles)
    mobile = sum(1 / b["d"] for i, b in enumerate(bubbles, 1) if i % 3)
    sizes = [b["s"] for b in bubbles]
    return (f"{len(bubbles)} bubbles, {rate:.1f} new per second (mobile {mobile:.1f}), "
            f"{min(sizes):.1f}-{max(sizes):.1f} px, durations "
            f"{min(b['d'] for b in bubbles):.1f}-{max(b['d'] for b in bubbles):.1f} s")


if __name__ == "__main__":
    bubbles = field()
    html = markup(bubbles)
    if "--print" in sys.argv:
        print(html)
    else:
        page = Path(__file__).resolve().parent.parent / "index.html"
        src = page.read_text(encoding="utf-8")
        new, n = re.subn(r'(<div class="fizz-field fizz-field--hero" aria-hidden="true">\n).*?(\n  </div>)',
                         lambda m: m.group(1) + html + m.group(2), src, count=1, flags=re.S)
        assert n == 1, "hero fizz field not found"
        page.write_text(new, encoding="utf-8")
        print("index.html updated")
    print(stats(bubbles))
