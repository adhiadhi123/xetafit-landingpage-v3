# XETAFIT — Landing Page

**Fizz your way to wellness.** A single-product landing page for XETAFIT Apple
Cider Vinegar Effervescent Tablets, Pack of 4. Built with **HTML and CSS** only. No JavaScript, frameworks or build step.

The copy follows `XETAFIT_Landing_Page_Content_V9_Benefits_Update.pdf` (Content V9)
and the CTA plan matches it. The **visual and motion system** is a rebuild modelled
on the supplied beverage-site reference recording, coloured with a three-colour
palette (2026-11-15): Fresh Apple Green page, Deep Botanical Green contrast panels
and navigation, Pure White product cards, heavy sans headlines with an editorial serif, a floating capsule header, giant
low-opacity serif lettering and numbered editorial layouts. Only XETAFIT's own
logo, packaging and photography are used; nothing from the reference brand.

---

## 1. Run it

No build step.

- **Quickest:** double-click `index.html`.
- **Closer to production:**
  ```bash
  cd xetafit-landing
  python -m http.server 8080      # then open http://localhost:8080
  ```

Fonts (DM Sans, Cormorant Garamond) load from Google Fonts. Offline, the page
falls back to system fonts.

## 2. Project structure

```text
xetafit-landing/
├── index.html            12 sections (V9 order) + footer
├── certificate.html      Certificate of Analysis details (batch NX3649)
├── css/
│   ├── style.css         tokens, components, header + menu, phone-first section layouts, certificate page
│   ├── responsive.css    tablet / desktop compositions (640 · 760 · 960 · 1100 · 1440 px, short desktops)
│   ├── animations.css    all motion: hero sequence, reveals, scroll zoom, lettering drift, breathing, nav highlight
│   └── benefits.css      05 Benefits: product stage and its screw-cap sequence (part generated, see §4c)
├── assets/
│   ├── source/           xetafit-tube-front.png: the studio packshot every product image is built from
│   ├── images/           product, tablet and bubble renders, photographs, certificate previews
│   └── documents/        original COA PDF (byte-identical copy)
└── tools/
    ├── render_product.py      builds all product + tablet renders from assets/source (see §5b)
    ├── render_props.py        ray-traces glass/prop renders and the hero bubble sprites (see §5c)
    ├── compose_comparison.py  places the tube render into the finished-drink photo for 08 (see §5c)
    ├── build_hero_layers.py   the hero opening layers: cap, open tube, inner wall, tablet frame strips (see §4b)
    ├── build_benefits_layers.py  05 Benefits: open tube, inside wall, cap rotation frames, tablet strip + CSS motion (see §4c)
    ├── split_words.py        wraps every headline word in a mask for the rolling text reveal (see §4)
    ├── make_fizz.py           generates the hero bubble markup and writes it into index.html
    ├── make_responsive.py     smaller copies of the large images for srcset
    ├── extract_logo.py        cuts the official logo out of the brand's creative (see §3)
    └── prepare_assets.py      builds the certificate previews
```

## 3. Design system

**Colour.** Three colours only, set as variables in `css/style.css` and
contrast-checked (WCAG). Everything else is one of them at reduced opacity
(`rgba(var(--color-contrast-rgb), a)`, white with alpha) or a tint mixed from them.

| Token | Value | Use | Contrast |
|---|---|---|---|
| `--color-primary` | `#8FC52E` Fresh Apple Green | page background, open sections, product stages, accents and purchase buttons on deep green | deep green text 5.9:1 |
| `--color-secondary` | `#FFFFFF` Pure White | product container, step / review / comparison cards, light panels (06, 11), text on deep green | deep green text 12.1:1 |
| `--color-contrast` | `#173D2B` Deep Botanical Green | text on green and white, contrast panels (02, 05, 08, 10), lifestyle / final / safety cards, header capsules, logo plate, footer, purchase buttons on light surfaces | white text 12.1:1 |
| `--color-primary-soft` | primary 14% on white (`#EFF7E2`) | inset areas on white: pack stage, pack chips, certificate table | deep green 11:1 |
| `--color-contrast-muted` | deep green 80% on white (`#456455`) | secondary text on white | 6.5:1 |
| `--color-contrast-line` | deep green 12% on white (`#E3E8E6`) | table hairlines, disabled Add to cart | muted text 5.3:1 |
| `--color-contrast-raised` | deep green + 15% primary (`#29512B`) | logo plate hover, footer logo plate | white 9.1:1 |

Rules: text on apple green is always deep green (white on apple green is only
2.1:1, so it is never used for text); apple green as text appears only on deep
green. Headline accents (`.h2 em`) are deep green on green and white surfaces and
apple green on deep green. The green-and-white packaging, the logo and every
photograph are never recoloured.

**Purchase accent (the one exception).** The five purchase CTAs in `<main>` use
*ember*, the only warm hue on the page, taken from the logo mark's orange
(`#F45A1E`) and reserved for purchase so they are the first thing the eye finds.
It lives only in `css/cta.css`: a fill gradient `#CC4510 → #BD3C0B → #A3320A`
(white text 4.7:1 at the lightest stop, measured on the rendered fill) with the
brighter logo orange used only for the glow outside the label. Nothing else on
the page uses it.

**Type.** DM Sans 800 capitals for headlines (tight tracking), with an italic
Cormorant Garamond accent (`.h2 em`, apple green on deep green). Editorial panels use all-serif
capitals (`.h2--serif`: Benefits, Lifestyle). Cormorant also sets product names,
step names, numerals and the giant background lettering (always lining figures).
DM Sans 400–700 for body, labels and buttons. All sizes use `clamp()`. The hero
headline is one line from 1100 px up, two lines on tablets, three on phones.

**Surfaces.** The page is apple green. A section is either *open* (on the green)
or a *panel*: a rounded deep-green or white block inset 8–14 px from the page edge,
so a strip of apple green shows between neighbouring blocks, as in the reference.
Each surface sets `--fg / --head / --em / --soft / --line / --focus` plus the
button and accent colours (`--cta-* / --alt-* / --accent / --on-accent /
--fg-rgb`), and every component reads those, so a component works on any surface.
(The class names `.panel--burgundy`, `.panel--cream`, `.btn--gold` and
`.btn--cream` are kept from the earlier palette; they now mean deep green, white,
purchase and white.)

| # | Section | Surface | Composition |
|---|---|---|---|
| 01 | Hero | apple green | one-line headline; copy + CTA · tube with two tablets · three facts; "Fizz. Sip. Repeat." marquee behind the tube |
| 02 | The switch | deep-green panel | copy + apple-green check list; tilted tube on an apple-green stage with the white "old way" card |
| 03 | Product + purchase | apple green | giant "Pack of 4 · 60 Tablets" lettering behind one large white container: pack image left, purchase column right |
| 04 | How it works | apple green | three white cards with the photographed drop / fizz / sip stages and dark number badges |
| 05 | Benefits | deep-green panel | tube centred, six benefits with apple-green serif numerals either side, ember CTA |
| 06 | Ingredients | white panel | tube on a green stage with "500 mg" lettering; "Per tablet" facts label with the sodium notice |
| 07 | Lifestyle | apple green | full campaign photograph with a deep-green card overlapping its lower left |
| 08 | Comparison | deep-green panel | white card (liquid ACV) vs apple-green card (XETAFIT), matching cream-studio photographs, apple-green "vs" disc |
| 09 | Reviews | apple green | four white placeholder cards (verified reviews only), ember CTA |
| 10 | Quality | deep-green panel | certificate preview on a paper stack + batch details, View certificate |
| 11 | FAQ | white panel | heading + always-visible deep-green safety card; native `<details>` list with hairline dividers |
| 12 | Final | apple green | deep-green card: headline, Buy now, four-pack photograph breaking out of the card top |

**Header.** Three floating capsules: the official logo on a deep-green plate
(the logo's white lettering is 2.1:1 on apple green and 12:1 on the plate, its
orange mark 3.6:1 on the plate, so the plate is needed), a centred deep-green
navigation group whose active link turns white as you scroll, and on the right
a certificate icon plus the white **Product** pill (both hover to apple green).
Below 960 px the navigation becomes a **Menu** capsule that opens a full-height
deep-green menu. It is CSS only: the menu shows while `#menu` is the URL target,
and following any link inside it changes the target, so it closes by itself.
Opening it does not move the page.

**Buttons.** Compact capsules with a small arrow, 42 px (50 px for `.btn--lg`):
`.btn--gold` purchase, `.btn--cream` information, `.btn--ghost` outline.
Purchase buttons in `<main>` (01 Buy now, 03 Buy now, 05 and 09 Get your 4-pack,
12 Buy now) are ember pills with white text on every surface (`css/cta.css`): a
glossy top edge, a soft logo-orange glow (plus a deep-green ground shadow on light
surfaces), and a glass shine: one narrow beam of light, tilted 15°, crosses the pill
left to right every 2.8 s (about 0.76 s of travel, then about 2 s of rest; first pass
1.6 s after load, as the hero CTA settles). The beam sits under the label and arrow,
is clipped to the pill, and animates only `transform`. Hover and keyboard focus slide the fill to
its richer end and bloom the glow (with a white halo on apple green, ember elsewhere);
press settles it with an inset shadow. Focus adds a 3 px ring, deep green on apple
green and white and white on deep green. The pills stay in place (no lift), as
`nav-liquid.css` keeps every CTA stationary for its water effect; the arrow still
moves 3 px. Reduced motion removes the shine and the fill slide. The header and menu
**Product** links are navigation and keep their own styles. Other buttons hover
to apple green on white surfaces and to white on apple-green and deep-green
surfaces (a white button on apple green turns deep green).

## 4. Motion (CSS only)

Native scrolling: no snapping, no scroll-jacking, no wheel handling, no JavaScript;
anchor links scroll smoothly and land clear of the header (`scroll-padding-top`).
Easing is `cubic-bezier(.22, 1, .36, 1)` throughout. Animated properties are
`transform`, `translate`, `rotate`, `scale` and `opacity`, plus `clip-path` for the
two ingredient photographs.

The editorial rhythm, in every section: eyebrow → **rolling headline** → copy →
product or photograph → CTA last. Each block plays once; nothing replays and
nothing hides again when you scroll back up.

| Motion | Where | How |
|---|---|---|
| Hero sequence | 01, on load | header drops in; headline lines rise out of masks one after another; copy and facts follow; the Buy now row arrives last |
| Rolling headlines | every section headline (02–12) and the six benefit titles | each word rises 0.85 s from behind its own mask, 65 ms after the previous word, so each line rolls up as a unit; wrapping is exactly the static layout's |
| Benefits opening | 05, once, when the product block is 40% in view | the cap unscrews and lifts off, one tablet rises out of the tube and hovers between tube and cap; benefits 01 → 06 follow as it clears the rim: number, rolling title, description (see §4c) |
| Product opening | 01, on load, once | the tube stands upright and settles; its cap lifts fully clear, two tablets come out one after the other, the cap closes (see §4b) |
| Hero idle | 01, from 3.3 s | the tube floats 8 px on a 6 s cycle over a floor shadow that widens and softens as it rises; each tablet floats 8–13 px on its own clock, independently of the tube |
| Marquee | 01 | "Fizz. Sip. Repeat." in giant serif at 13 % white, 64 s seamless right-to-left loop, behind the tube, clear of the copy and facts |
| Carbonation | 01 only | 104 rendered bubbles, about 15 new a second (about 10 on phones) |
| Section entrances | every section | play **once** when a block is 10vh into view. Text 0.68 s fade-up, staggered, held 0.2 s until the headline is mostly up; products 0.95 s; cards 0.75 s rise, staggered (04 steps, 09 reviews, 11 FAQ rows); photographs 1.25 s cinematic settle (1.08 → 1: 07, 12); the 06 ingredient photographs are uncovered by a rising clip while they settle from 1.14; the 08 sides move in towards each other; the 10 certificate scales in; product before details and Add to cart last (03); 12: headline, then photograph, then Buy now |
| Product scroll motion | 02 tube, 03 pack (`.reveal-product`) | while it crosses the viewport: rises 4 % into place, `scale` .97 → 1.03 at mid-viewport → 1.00 as it leaves. Transform only. (The 05 tube stays still: its opening must not move) |
| Scroll-linked zoom | photographs (`.zoom`: 10 certificate, 12 final photo) | `scale` 1.00 entering → peak at mid-viewport → 1.00 leaving: 1.05 / 1.03 inside their rounded frames |
| Lettering drift | 03, 12 | the giant background lettering slides sideways with the scroll, the two bands in opposite directions |
| Breathing | pack, final photograph | 1.00 → 1.02, 6.4–8 s a cycle, starting after the entrance, on its own nested wrapper |
| Light | product renders, campaign photographs | a soft light band sweeps each render every 10 s (masked to its silhouette); a slow daylight shift over the photos |
| Hover | buttons, header, cards, certificate | buttons 0.24 s; cards lift 3–4 px; the certificate straightens |
| Navigation / FAQ | header / 11 | the link of the section in view becomes a white capsule; answers open and close smoothly where `::details-content` is supported |

**The reveal system** (`css/animations.css`), one transform per element:

| Class | Job |
|---|---|
| `.rv` | reveal-stagger container: sets `--seen` once it is 10vh into view; its children enter one after another |
| `.rv > *` | reveal-fade, the default entrance; `--reveal` picks another (`enter-left`, `enter-card`, `enter-cinema`, `clip-reveal` ...), `--rv-step` / `--rv-delay` set the rhythm |
| `.reveal-word` | rolling headline: words split by `python tools/split_words.py` into `<span class="w">` masks (re-run it after editing a headline); the heading keeps an `aria-label` with its plain text |
| `.reveal-image` | photograph uncovered by a rising clip while it settles |
| `.reveal-product` | scroll-linked product motion (.97 → 1.03 → 1) |
| `.zoom` / `.breathe` | scroll-linked photo zoom / slow loop |

Line by line without JavaScript: CSS cannot know where a balanced headline wraps,
and the wraps change with the width (e.g. "QUALITY YOU / CAN LOOK INTO." at 1440 px,
"QUALITY / YOU CAN / LOOK INTO." at 1280 px), so authored line wrappers would change
the layout. Every word gets its own mask instead, and the words roll up 65 ms apart:
each visual line rises as a unit, and the layout stays exactly the static one
(measured: identical headline boxes and line breaks at 1440, 1024, 768 and 390 px).

**"Play once when seen" without JavaScript:** `.rv` runs a scroll-driven animation
(`animation-timeline: view()`) whose only job is to set the registered property
`--seen` to 1. The entrances are time-based, so they finish and hold even if you stop
scrolling. They are held on their first frame only while `@container style(--seen: 0)`
positively matches: a browser that cannot evaluate that query never holds them, so
they play at load and nothing can stay hidden.

**Watch out:** `overflow: hidden` makes a scroll container, and `view()` inside it
would track that box instead of the page. Frames around zooming images use
`overflow: clip`.

| Situation | Result |
|---|---|
| Chrome / Edge 115+, Safari 26+ | full experience |
| Browsers without scroll-driven animations (e.g. current Firefox) | every section visible at once, no scroll zoom or drift; the hero sequence, marquee, bubbles, floating and breathing still run |
| Scroll-driven animations but no container style queries | the entrances play once at load; everything is visible by the time it is reached |
| `prefers-reduced-motion: reduce` | no animation, no bubbles, no smooth scrolling; everything visible |

Safety information (the sodium notice, the safety card) is never animated or hidden.

**Tested** in Chrome 157 (headless, DevTools protocol) at 1440×900, 1280×720,
1024×768, 960×800, 768×1024 and 390×844: no horizontal overflow; headline boxes and
line breaks identical to the static layout; rapid scrolling, natural scrolling,
scrolling back up and re-entering sections all end with all 164 entrances finished
and nothing faded, and nothing replays; the 05 cap, tablet and tube never overlap the
headline or a benefit; reduced motion leaves zero running animations. The two
fallbacks (no scroll-driven animations; no style queries) were simulated by
disabling those rules in a copy of the CSS: everything visible in both.
**Not yet tested:** Safari, Firefox, real touch devices, frame-rate profiling on
low-end phones.

### 4b. The hero product opening (CSS only, plays once)

| Time | What happens |
|---|---|
| 0–0.6 s | the closed tube stands upright and settles 6 px onto its floor shadow, which forms underneath |
| 0.6–1.3 s | the cap unseats and lifts fully clear (about 14 % of the art height, 4° tilt), then hovers over the open mouth; both tablets sit deep, so the mouth reads dark and open |
| 1.3–2.0 s | tablet 1 rises out of the opening behind the front lip, glides left above the rim, then floats down to its place (settled at 2.3 s) |
| 2.0–2.7 s | tablet 2 (one tablet lower in the tube) rises out, glides right above the rim, then floats down to the lower right (settled at 3.25 s) |
| 2.7–3.3 s | the cap comes back down, aligns with the mouth and seats; the closed tube takes over again |
| 3.3 s on | idle floating: tube 8 px / 6 s; tablets 9–13 px / 6.4 s and 8–12 px / 7.2 s (scaled with the art), independent of the tube; each tablet starts as it lands |

The flight paths were checked frame by frame against the real layer masks: once a
tablet is in front of the tube it never overlaps the tube wall, the cap or the other
tablet, and below the rim it keeps at least 2 % of the art height from the tube's sides.

**Layers** (`tools/build_hero_layers.py`, about 3 minutes; `--tubes` skips the tablets).
All tube layers share one 360 × 1369 canvas, so they register exactly:

| File | What it is |
|---|---|
| `hero-tube.webp`, `hero-tube-190.webp` | the closed tube at full source resolution, plus a pre-scaled copy for 1× screens (`srcset`) |
| `hero-cap.webp` | the cap alone, cut along the real cap/label seam, so it is pixel-identical to the cap on the closed tube |
| `hero-tube-open.webp` | the tube without its cap: label, front wall and front lip; the opening itself is transparent |
| `hero-tube-inner.webp` | what is seen through the opening: the far half of the rim and the shaded inner wall |
| `hero-tablet-1.webp`, `hero-tablet-2.webp` | 16 ray-traced frames each (320 px), from lying flat in the tube to the resting angle; CSS steps through them in flight |

The source photo never shows the tube without its cap, so the open state is built
from geometry, not invented artwork: the camera elevation (8.2°) is measured from
the cap's top ellipse, the opening is that ellipse at the body radius, the label's
own top green band continues up to the rim, and the rim and inner wall use the
studio shading measured on the white label paper. No printed detail is created or
changed. The tablets are the same 3D model, seed and spin as `tablet-a/b`, sized to
fit the tube (radius 0.89 × its inner radius).

**Stacking** inside `.hero__product`, back to front: inner wall (`.hero__well`) ·
tablets while inside (z-index 2) · open tube · closed tube · cap · tablets once their
lowest edge clears the front lip (z-index 6). Horizontal and vertical motion run on
separate wrappers (`.tab` and `.tab__y`), so each flight path is a smooth curve; the
idle bob (`.tab__bob`) and the frame strip (`.tab__img`) are nested inside. The idle
float of the tube runs on `.hero__closed` (the only tube layer visible after 3 s), so the
tablets drift independently instead of riding along with the tube. The lifted cap
hovers above both tablet paths and never touches them. All
distances are in `cqh` (1 % of the art height), so the sequence scales with every
breakpoint and never reaches the headline, CTA or facts.

**Sharpness.** The tube is no longer rotated or scroll-zoomed in the hero (both made
the browser resample the label). The packshot itself is 1024 × 1536 and the tube in
it is about 360 × 1370 px. That is enough for the hero at 2× pixel density, but a
**studio render of the tube at about 2000 px tall** would be the next step up, and
would rebuild every layer with `python tools/build_hero_layers.py`.

**Fallbacks.** Reduced motion: no sequence, the closed tube and both tablets are
shown at their final positions, nothing floats. The opening layers are preloaded;
the closed tube is always the base state, so the product never stays hidden.

### 4c. The Benefits opening (05, CSS only, plays once)

| Time | What happens |
|---|---|
| on entry | the headline rolls up word by word, then the lead (`.rv`, `.reveal-word`) |
| 0–0.1 s | the closed tube, cap on |
| 0.1–1.0 s | the cap turns (312° in all) and climbs its thread, one pitch per turn; the bridges in its groove travel round, which is what shows the rotation |
| 1.0–1.5 s | free of the thread, the cap lifts about 3 cm and tips 6°; the threaded neck, the rim and the dark opening appear |
| 1.06–1.9 s | the tablet, lying flat inside, rises through the opening (the front wall hides its lower part until it is out), then turns to its resting angle between the opening and the cap |
| 1.46–2.6 s | benefits 01 → 06, 0.09 s apart, from the moment the tablet clears the rim: the apple-green number rises, the title rolls up from its masks, the description follows |
| from 1.9 s | the tablet hovers (6 px, 5.2 s); the tube and the open cap stay still |

**Why it is a separate render.** The studio packshot is seen from about the middle of
the tube: its base curves like a smile (seen from above), every edge of its cap like a
frown (seen from below). From that viewpoint an open tube's mouth is physically
invisible, so it cannot be cut out of the photo. `tools/build_benefits_layers.py`
(about 1 min) builds one consistent view from 14° above the product instead:

* **Label and base:** the photographed pixels, re-projected column by column (the tube
  is a cylinder, so a column keeps its place on the label and only moves vertically).
  The packshot's own viewing angle is measured from printed straight lines: logo
  baseline −1.7°, divider line +4.1°, label edge +6.3°. No printed detail is created,
  removed or moved along the label.
* **Cap, collar ring, threaded neck, rim, inside wall:** solids of revolution, ray-cast
  from the profile measured on the packshot's silhouette and shaded with the white
  plastic light measured on its collar ring. The collar ring (the wide white band)
  stays on the tube, like a tamper ring; the cap is the ridged part above it.
* **Rotation:** the cap is round except for the 15 bridges in its groove (measured every
  24°). `benefit-cap.webp` holds 6 frames per bridge spacing; the pattern repeats, so the
  generated `bx-spin` keyframes show any angle with 6 frames, one key per display frame,
  never more than ⅓ of a spacing per frame (so it cannot appear to turn backwards).
  Below 640 px the bridges are about 1 px and the spin frames are skipped.
* **Tablet:** the site's ray-marched tablet, re-rendered for this camera, flat in frame 0
  and at rest in frame 15 (`benefit-tablet.webp`).

| File | What it is |
|---|---|
| `benefit-tube.webp` | tube, collar ring, threaded neck and the front half of the rim; the opening is transparent |
| `benefit-tube-inner.webp` | the far half of the rim and the inside wall seen through the opening |
| `benefit-cap.webp` | 6 cap frames, stacked |
| `benefit-tablet.webp` | 16 tablet frames, side by side |

**Stage.** All layers share one coordinate system (`.bx`, a size container; `cqh`/`cqw`
are 1% of it), so the cap, opening and tablet stay registered at every size. Back to
front: shadow · inside wall · tablet · tube · cap. Entrance and loop motion run on
separate nested wrappers (`.bx__tab-rise`, `.bx__tab-float`, frame strips inside
`overflow: clip` boxes); only `translate`, `rotate` and `opacity` animate. The script
also writes the layer placement and the eased keyframes into `css/benefits.css`
between the `@generated` markers, and checks the clearances on the way (tablet above
the rim while it turns; cap at least 12 px above the tablet at all times).
`python tools/build_benefits_layers.py --css` rewrites only the motion after a timing change.

**Trigger and fallbacks** follow the site's reveal system (§4): `.formula` sets `--seen`
once it is 40% into the viewport (phones and tablets: the product and each benefits
column on their own); the default styles are the final composition; the sequence is
held on its first frame only while `@container style(--seen: 0)` positively matches.

## 5. Integration points (search the HTML for `INTEGRATION POINT`)

| What | Where | Status |
|---|---|---|
| **Add to cart** | `#buy` → `<form class="cart">` | **Inactive by design.** The button is `disabled` and a visible note says the store is not connected. To activate: set `action` (e.g. Shopify `/cart/add`), put the **four-pack variant ID** in `name="id"`, then remove `disabled` and the `.cart-status` note. Only the four-pack may be added. |
| **Live price / stock / delivery** | `#buy` → `<dl class="live">` | Placeholders (`.pending`). Fill server-side or via store templating. No price is hard-coded. |
| **Customer reviews** | `#reviews` → `<ul class="review-track">` | Four labelled placeholders. Replace them with verified, permission-cleared reviews only (exact text, reviewer name as displayed, platform, date), then delete the `.dev-note`. |
| **Logo** | header and footer of both pages | Official logo in place (256 × 68 raster cut from the brand's creative by `tools/extract_logo.py`). Swap `assets/images/xetafit-logo.png` for the official SVG when available. |

### CTA plan (V9), as built

| Section | CTA | Target |
|---|---|---|
| 01 Hero | Buy now (+ Pack of 4 card) | `#buy` |
| 03 Product | Add to cart | store (inactive until connected) |
| 05 Benefits | Get your 4-pack | `#buy` |
| 09 Reviews | Get your 4-pack | `#buy` |
| 10 Quality | View certificate | `certificate.html` (which links the original PDF) |
| 12 Final | Buy now (+ Pack of 4 card) | `#buy` |

The header has no Buy Now button, because V9 allows Buy Now only in scenes
01 and 12. Its right-hand pill is the "Product" navigation link to `#buy`.

## 5b. Product renders (one master asset, reused everywhere)

Every product image on the page comes from **one** studio packshot,
`assets/source/xetafit-tube-front.png`, via `tools/render_product.py`:

```bash
pip install numpy pillow opencv-python-headless
python tools/render_product.py                 # everything (~1 min)
python tools/render_product.py --tubes         # tube views, shadows, four-pack only
python tools/render_product.py --tablets       # the two tablets only
python tools/render_product.py my-photo.png    # rebuild from a different packshot
```

| File | What it is | Used in |
|---|---|---|
| `tube-front.webp` | master front view with a geometric anti-aliased matte (no white fringe) | the hero light-sweep mask |
| `tube-angle.webp` | the same tube turned 24° on its axis: label re-projected on a 3D cylinder under the same studio light | 06 ingredients, 08 comparison composite |
| `tube-tilt.webp` | the turned tube leaning 24° | 02 the switch |
| `tube-shadow.webp` / `tube-shadow-soft.webp` | the real ground shadow lifted from the studio shot (contact line + falloff) / a diffused version for floating tubes | under every single tube |
| `pack4.webp` (+ `pack4-640.webp`) | four tubes in a receding row, each label turned slightly, with ground shadows and occlusion shadows between tubes | 03 product container |
| `tablet-a.webp`, `tablet-b.webp` | two effervescent tablets ray-marched in 3D: pale mint, chalky, porous, green flecks, lit like the tube | 02 switch, 06 ingredients (the hero uses the same two tablets as frame strips, §4b) |

The tube is a surface of revolution, so its outline, cap and base are identical
at any rotation and only the label moves. The script reads each label point
from the source, removes the source's own studio shading (measured on the white
label areas) and applies the shading of its new position. The lights stay fixed
while the tube turns. Label areas the source never shows (the far side, past
~65°) continue each row's band colour. Shadows are separate images placed in
tube-relative percentages (`.tube__shadow` in `css/style.css`, numbers from
`tools/render-placement.json`). No CSS `drop-shadow` is used on product images.

**Limits, honestly:** this is image-based 3D, not a modelled CAD render. The
front view is the supplied packshot itself. Turned views are accurate for small
turns, but the far side of the label is synthesised from the band colours. For
full 360° accuracy, supply the flat label artwork (dieline) or photos from more angles.

## 5c. Realistic props and the fizz atmosphere

No illustrated elements remain: the SVG glass plates, the line-art bottle,
jigger, plate, laptop and bag icons, and the CSS-drawn bubbles, ripples and foam
are all gone. `tools/render_props.py` (about 1.5 min) ray-traces the replacements
with refraction, Fresnel reflections from studio softboxes, total internal
reflection, Beer-Lambert absorption and scattering in the drink:

| File | What it is | Used in |
|---|---|---|
| `glass-water.webp`, `glass-drink.webp`, `glass-shine.webp`, `glass-fizz.webp`, `glass-mask.webp` | the tumbler as registered layers (rendered on the earlier forest green) | not used |
| `glass-drink-arch.webp` | the finished drink on the earlier lifestyle arch colour | not used |
| `shot-amber.webp` | shot glass of liquid ACV (transparent; sits on the `--color-primary-soft` tile) | 02 the switch ("the old way") |
| `plinth.webp` | clay plinth with contact shadow | not used |
| `bubble-1..3.webp` | hero carbonation sprites: thin bright meniscus ring, warm inner edge, specular point (`python tools/render_props.py --bubbles` rebuilds only these) | 01 hero |
| `tablet-c.webp` | a third tablet render, lying flat (from `render_product.py`) | not used |

Each render sits on the exact colour of the area it is placed on, so edges never show.

**Carbonation (hero only).** The other sections get their sparkle from light
and movement on existing visuals, not from particles (see §4). To change the
bubble count, sizes or speeds, edit the settings at the top of
`tools/make_fizz.py` and run it: it rewrites the hero field in `index.html` and
prints the resulting bubbles per second.

**Photographs.** Sections 04, 07, 08 and 12 use photographs (prompts in
`assets/images/*-prompt.txt` and `refinement-generation-notes.txt`):
`preparation-sequence.webp` (04, one file cropped three ways), `lifestyle-workspace.webp`
(07), `comparison-vinegar.webp` (08, left) and `final-product-drink.webp` (12). The two
large photos have 768 px copies for phones (`tools/make_responsive.py`).

**Comparison composite.** The XETAFIT side of 08 needs the tube beside a prepared
drink in the same cream studio light as the vinegar photo. `tools/compose_comparison.py`
builds `comparison-xetafit.webp` from the "sip" frame of `preparation-sequence.webp`
and `tube-angle.webp`: the tube is sized to about 1.1 × the tumbler, warm-graded to the
photo's light, softened to its sharpness and given a contact shadow and a soft cast
shadow. The label itself is not altered. Replace it with a real photograph of the
pack and a prepared glass when one exists.

## 6. Assets to replace before launch

1. **Packshot source.** Everything is built from `assets/source/xetafit-tube-front.png`
   (1024 × 1536). A real studio photo or official 3D render of the current pack,
   front-on on white at about 2000 px tall, can replace it. Re-run
   `tools/render_product.py` and every image on the page updates.
2. **Official logo SVG** (the header currently uses a 256 × 68 raster cut from the brand's creative: crisp on standard screens, slightly soft on high-density ones).
3. **Ingredient photography.** The brief asks for realistic green apples and
   pomegranate in section 06. The project has no such photographs, and none were
   invented, so 06 shows the tube and a tablet on red, and the only fruit is the
   artwork on the pack label. Supply a licensed or shot photograph (green apples,
   a split pomegranate, a tablet; on a plain background) and it can drop into the
   red stage in `.ing__stage`.
4. **A real XETAFIT + glass photograph** to replace the 08 composite (see §5c), and
   *(optional)* more lifestyle moments (morning, active, on the move).
5. **05 Benefits opening, for a fully photographic version** (see §4c). The neck, rim,
   inside wall and cap are renders matched to the packshot, because no photograph of
   the open product exists. Same camera, light and scale for all of: the tube with its
   cap removed (threaded neck, rim and opening visible, camera about 10–15° above the
   rim); the cap alone at the same angle; ideally a 24–36 frame turntable of the cap (or
   the 3D/CAD model of tube and cap). With those, `benefit-tube*.webp` and
   `benefit-cap.webp` can be replaced one for one; the stage and motion stay as they are.
6. **02 The switch: replace `switch-open-product-layers.png`.** Its open tube is not the
   authentic pack: the tagline reads "Zeaal it. Feelit." (the pack says "Zeal it. Feel
   it.") and the logo mark differs slightly. Either supply authentic open-tube and cap
   photographs (item 5), or switch 02 to the original tube (`tube-tilt.webp`) with one
   floating tablet.
7. Verified reviews (see §5).

## 7. Open questions for the client (unchanged from V9)

1. **Flavour name.** V9 says *Green Apple + Pomegranate flavour*; the pack art says *Green Apple Flavor*; the COA says *(green Apple)*. The site follows V9.
2. **Dose and daily limit.** Resolved 18 Nov 2026 from the official product page: "Drop 1 tablet in a glass of water (200–250 ml). Drink once the fizz settles. Up to 2 tablets a day." Used in the FAQ and Important product information.
3. **Four-pack SKU, live price, stock** (§5). Pack of 4 checked 18 Nov 2026 on the official store: ₹999 (regular ₹1,599), SKU `XF_ACVGRNAPL_4Pc`, variant `52622247067960`. The price is static in `#buy`; re-check it when the store price changes. FSSAI Lic. No. 10715002000175. Stock is not shown.
4. **COA batch.** NX3649 (mfd 08/2025, exp 01/2027) should match the stock being sold.
5. **"With The Mother"** is presented as the brand's description. The COA does not verify it, and the site says so.
   **Note:** the new packshot's label does *not* say "With The Mother". It reads "Daily Plant-Based",
   "Enzyme, Antioxidants" and "Health Supplement (with Natural Sweetener)", which differs from the
   earlier pack art ("With The Mother", "Energize. Metabolize."). Please confirm which label is
   current. If "With The Mother" is no longer on pack, the ingredients note should change. Also
   check that the label's "Antioxidants" wording is cleared, since the site copy itself makes no such claim.
6. **Review permissions** for customer reviews sourced from the official XETAFIT store.
