"""Correct product gallery images 02, 03 and 06 (v10 -> v11).

Facts used here were checked on 2026-11-18 against the official XETAFIT store
data for "Apple Cider Vinegar Effervescent Tablets - Green Apple & Pomegranate":

  * FSSAI Lic. No. 10715002000175
  * Per tablet: 500 mg ACV (6% acetic acid), pomegranate extract 100 mg,
    vitamin B6 1.9 mg (100% RDA), vitamin B12 1.1 mcg (50% RDA)
  * Flavour: "ACV with Green Apple Flavour" (no green tea extract listed)

Corrections
  02  AI-drawn tube ("500 ML PER TABLET", "Bangpoe", "& Green Tea Extract",
      "Helps Maintain Healthy Weight") -> official tube photograph.
  03  "Green Tea Extract" row -> "Green Apple Flavour" row; the bottom
      flavour pill (now a duplicate) -> FSSAI licence pill.
  06  Same AI-drawn tube -> official tube; "(Cyanocine)" / "(Cyanocobalamin)"
      removed (forms are not stated by the brand), B12 "1.11 mcg" -> "1.1 mcg",
      stray "15" removed, FSSAI licence line added under the table.
  07  Flat-lay tube label misspelt ("WITH THE MOTHES", "Vit B€") -> official tube.
  08  Pure-black heading and list text -> the deep green used by 02/03/06.
  09  Before/after tube small print garbled ("1300 mg ACV") -> official tube.

The official tube comes from actual-product-official-v3.jpg (unchanged).
The apple photo is assets/images/ingredient-apple.jpg (Pexels licence).

Usage:  python tools/correct_gallery_v11.py [output_dir]
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GALLERY = os.path.join(ROOT, 'assets', 'images', 'product-gallery')
MASTER = os.path.join(GALLERY, 'actual-product-official-v3.jpg')
APPLE = os.path.join(ROOT, 'assets', 'images', 'ingredient-apple.jpg')
FONT_DIR = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Windows', 'Fonts')

FSSAI = '10715002000175'
INK = (21, 48, 12)          # heading ink sampled from image 03
TEXT = (16, 18, 15)         # body ink sampled from image 03
TABLE_BG = (253, 254, 252)  # nutrition table fill in image 06


def font(name, cap_height):
    """Plus Jakarta Sans at the size whose capital height matches the artwork."""
    path = os.path.join(FONT_DIR, name)
    for size in range(8, 120):
        f = ImageFont.truetype(path, size)
        top = f.getbbox('H', anchor='ls')[1]
        if -top >= cap_height:
            return f
    raise ValueError(name)


# ---------------------------------------------------------------- tube ----
def official_tube():
    """Cut the official tube out of its white studio background (RGBA)."""
    rgb = np.asarray(Image.open(MASTER).convert('RGB'))
    top, bottom, left, right = 143, 1405, 590, 912
    crop = rgb[top:bottom, left:right]
    d = 765 - crop.astype(np.int32).sum(2)
    h, w = d.shape
    mask = np.zeros((h, w), np.float32)
    body_l, body_r = 607 - left, 892 - left
    for y in range(h):
        xs = np.where(d[y] > 40)[0]      # skip the 1-2 px white transition
        if not len(xs):
            continue
        l, r = int(xs.min()), int(xs.max())
        if top + y >= 1370:              # ignore the contact shadow around the base
            l, r = max(l, body_l), min(r, body_r)
        mask[y, l:r + 1] = 1
    # The base ends in a shallow ellipse: ~1393 at the sides, ~1403 at the centre.
    cx, half = (607 + 892) / 2, (892 - 607) / 2
    for x in range(w):
        u = (x + left - cx) / half
        if abs(u) <= 1:
            cut = 1393 + 10 * np.sqrt(1 - u * u) - top
            mask[int(np.ceil(cut)):, x] = 0
    mask = cv2.erode(mask, np.ones((1, 3), np.uint8))
    alpha = cv2.GaussianBlur(mask, (0, 0), 0.6)
    rgba = np.dstack([crop, (alpha * 255).clip(0, 255).astype(np.uint8)])
    img = Image.fromarray(rgba, 'RGBA')
    return img.crop(img.getbbox())


def replace_tube(img, old_boxes, top, bottom, cx, grow=11, shadow_alpha=82, shadow=(13, 9, 8)):
    """Inpaint the old tube, then stand the official tube in the same spot."""
    rgb = np.asarray(img.convert('RGB')).copy()
    h, w = rgb.shape[:2]
    old = np.zeros((h, w), np.uint8)
    for x0, y0, x1, y1 in old_boxes:
        old[y0:y1, x0:x1] = 255
    old = cv2.dilate(old, np.ones((grow, grow), np.uint8))   # include the old tube's glow
    bgr = cv2.inpaint(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), old, 6, cv2.INPAINT_TELEA)
    out = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)).convert('RGBA')

    tube = official_tube()
    th = bottom - top
    tw = round(tube.width * th / tube.height)
    tube = tube.resize((tw, th), Image.LANCZOS)
    x = round(cx - tw / 2)

    above, below, blur = shadow
    layer = Image.new('RGBA', out.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse(
        (cx - tw * 0.58, bottom - above, cx + tw * 0.58, bottom + below),
        fill=(28, 52, 20, shadow_alpha))
    out = Image.alpha_composite(out, layer.filter(ImageFilter.GaussianBlur(blur)))
    out.alpha_composite(tube, (x, top))
    return out.convert('RGB')


def replace_lying_tube(img, old_mask, center, cap_width, angle):
    """Flat-lay version: the official tube rotated `angle` degrees clockwise."""
    rgb = np.asarray(img.convert('RGB')).copy()
    old = cv2.dilate(old_mask.astype(np.uint8) * 255, np.ones((9, 9), np.uint8))
    bgr = cv2.inpaint(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), old, 6, cv2.INPAINT_TELEA)
    out = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)).convert('RGBA')

    tube = official_tube()
    length = round(tube.height * cap_width / tube.width)
    tube = tube.resize((cap_width, length), Image.LANCZOS)
    tube = tube.rotate(-angle, resample=Image.BICUBIC, expand=True)
    x, y = round(center[0] - tube.width / 2), round(center[1] - tube.height / 2)

    shade = Image.new('RGBA', tube.size, (52, 38, 22, 255))
    shade.putalpha(tube.getchannel('A').point(lambda v: int(v * 0.32)))
    shadow = Image.new('RGBA', out.size, (0, 0, 0, 0))
    shadow.alpha_composite(shade, (x - 5, y + 7))
    out = Image.alpha_composite(out, shadow.filter(ImageFilter.GaussianBlur(7)))
    out.alpha_composite(tube, (x, y))
    return out.convert('RGB')


def recolor_black_text(img, boxes, ink):
    """Re-ink neutral black lettering (anti-aliasing kept) inside the given boxes."""
    a = np.asarray(img.convert('RGB')).astype(np.float32)
    out = a.copy()
    lum = a.mean(2)
    bg = cv2.dilate(lum, np.ones((41, 41), np.uint8))          # local paper tone
    neutral = (a.max(2) - a.min(2)) < 20
    alpha = ((bg - lum) / np.maximum(bg - 4, 1)).clip(0, 1)
    ink = np.array(ink, np.float32)
    for x0, y0, x1, y1 in boxes:
        sl = (slice(y0, y1), slice(x0, x1))
        m = neutral[sl] & (alpha[sl] > 0.04)
        al = alpha[sl][..., None]
        new = bg[sl][..., None] * (1 - al) + ink * al
        out[sl][m] = new[m]
    return Image.fromarray(out.round().clip(0, 255).astype(np.uint8))


# --------------------------------------------------------------- helpers ---
def inpaint_mask(img, mask, radius=5):
    bgr = cv2.cvtColor(np.asarray(img.convert('RGB')), cv2.COLOR_RGB2BGR)
    bgr = cv2.inpaint(bgr, mask.astype(np.uint8) * 255, radius, cv2.INPAINT_TELEA)
    return Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))


def words(draw, x, y, text, f, fill, gap=0.36, center=False):
    """Draw on a baseline with a fixed word gap (in em); the italics run tight."""
    parts = text.split(' ')
    space = f.size * gap
    total = sum(draw.textlength(p, font=f) for p in parts) + space * (len(parts) - 1)
    if center:
        x -= total / 2
    for p in parts:
        draw.text((x, y), p, font=f, fill=fill, anchor='ls')
        x += draw.textlength(p, font=f) + space
    return total


def supersampled(size, draw_fn, scale=4):
    """Anti-aliased L mask drawn at 4x and reduced."""
    big = Image.new('L', (size[0] * scale, size[1] * scale), 0)
    draw_fn(ImageDraw.Draw(big), scale)
    return big.resize(size, Image.LANCZOS)


def apple_cutout(width):
    src = cv2.imread(APPLE)
    mask = np.zeros(src.shape[:2], np.uint8)
    bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(src, mask, (300, 270, 620, 445), bgd, fgd, 6, cv2.GC_INIT_WITH_RECT)
    fg = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 1, 0).astype(np.uint8)
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, labels, stats, _ = cv2.connectedComponentsWithStats(fg)
    keep = [i for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] > 4000]
    fg = np.isin(labels, keep).astype(np.float32)
    fg = cv2.erode(fg, np.ones((3, 3), np.uint8))
    alpha = cv2.GaussianBlur(fg, (0, 0), 1.0)
    rgb = cv2.cvtColor(src, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(np.dstack([rgb, (alpha * 255).astype(np.uint8)]), 'RGBA')
    img = img.crop(img.getbbox())
    return img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)


# ------------------------------------------------------------ image 02 ----
def fix_02(src):
    return replace_tube(
        src,
        old_boxes=[(492, 206, 758, 296), (503, 288, 748, 1196)],
        top=207, bottom=1198, cx=624.5)


# ------------------------------------------------------------ image 03 ----
def fix_03(src):
    img = src.convert('RGB')
    a = np.asarray(img).astype(np.int32)
    h, w = a.shape[:2]
    bg = np.array([250, 252, 248])

    # 1. Remove the green-tea disc, leaves and copy (keep the connector line).
    mask = np.zeros((h, w), bool)
    y0, y1, x0, x1 = 730, 1014, 186, 568
    region = np.abs(a[y0:y1, x0:x1] - bg).max(2) > 10
    mask[y0:y1, x0:x1] = region
    mask[832:860, 518:640] = False                       # connector + dot
    text = a[792:958, 640:936].sum(2) < 600              # "GREEN TEA EXTRACT" copy
    mask[792:958, 640:936] |= text
    mask = cv2.dilate(mask.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
    mask[832:860, 518:640] = False
    img = inpaint_mask(img, mask, 7)

    # 2. New disc in the same place and colours as the other ingredient discs.
    cx, cy, r = 378, 876, 134
    disc_mask = supersampled((w, h), lambda d, s: d.ellipse(
        ((cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s), fill=255))
    yy = np.arange(h, dtype=np.float32)[:, None]
    t = ((yy - (cy - r)) / (2 * r)).clip(0, 1)
    top_c, bot_c = np.array([227, 242, 201.]), np.array([214, 241, 162.])
    grad = (top_c * (1 - t[..., None]) + bot_c * t[..., None]).repeat(w, 1)
    disc = Image.fromarray(grad.astype(np.uint8)).convert('RGBA')
    disc.putalpha(disc_mask)
    img = img.convert('RGBA')
    img.alpha_composite(disc)

    # 3. Green apple + slices photograph, grounded with a soft shadow.
    apple = apple_cutout(268)
    ax = round(cx - apple.width / 2) + 6
    ay = round(cy - apple.height / 2) + 14
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse(
        (ax + 20, ay + apple.height - 22, ax + apple.width - 6, ay + apple.height + 8),
        fill=(40, 80, 20, 70))
    img = Image.alpha_composite(img, shadow.filter(ImageFilter.GaussianBlur(9)))
    img.alpha_composite(apple, (ax, ay))

    # 4. Copy, set in the same type, size and position as the row it replaces.
    d = ImageDraw.Draw(img)
    head = font('PlusJakartaSans-ExtraBold.ttf', 29)
    body = font('Inter_18pt-Italic.ttf', 18)     # matches the row copy's width
    d.text((648, 826), 'GREEN APPLE', font=head, fill=INK, anchor='ls')
    d.text((648, 864), 'FLAVOUR', font=head, fill=INK, anchor='ls')
    d.text((650, 900), 'A refreshing fruity taste,', font=body, fill=TEXT, anchor='ls')
    d.text((650, 927), 'without the sour vinegar shot', font=body, fill=TEXT, anchor='ls')

    # 5. Bottom pill: the flavour is now its own row, so the pill carries FSSAI.
    pill = font('PlusJakartaSans-BoldItalic.ttf', 18)
    label = f'FSSAI Lic. No. {FSSAI}'
    probe = ImageDraw.Draw(Image.new('L', (1, 1)))
    tw = words(probe, 0, 0, label, pill, 0)
    px0, py0, py1 = 121, 1158, 1214
    px1 = round(px0 + 22 + 30 + 12 + tw + 26)
    cover = supersampled(img.size, lambda dr, s: dr.rounded_rectangle(
        ((px0 - 9) * s, (py0 - 8) * s, (max(px1, 552) + 7) * s, (py1 + 13) * s),
        radius=36 * s, fill=255))
    fill = inpaint_mask(img, np.asarray(cover) > 0, 9).convert('RGBA')
    img = Image.composite(fill, img, cover)
    xs = np.arange(w, dtype=np.float32)[None, :]
    tx = ((xs - px0) / (px1 - px0)).clip(0, 1)
    left_c, right_c = np.array([198, 232, 118.]), np.array([216, 243, 163.])
    pg = (left_c * (1 - tx[..., None]) + right_c * tx[..., None]).repeat(h, 0)
    pill_img = Image.fromarray(pg.astype(np.uint8)).convert('RGBA')
    pill_img.putalpha(supersampled(img.size, lambda dr, s: dr.rounded_rectangle(
        (px0 * s, py0 * s, px1 * s, py1 * s), radius=28 * s, fill=255)))
    img.alpha_composite(pill_img)
    d = ImageDraw.Draw(img)
    icx, icy = px0 + 22 + 15, (py0 + py1) / 2
    badge = supersampled(img.size, lambda dr, s: (
        dr.ellipse(((icx - 14) * s, (icy - 14) * s, (icx + 14) * s, (icy + 14) * s),
                   outline=255, width=3 * s),
        dr.line([((icx - 7) * s, (icy + 0.5) * s), ((icx - 2) * s, (icy + 5.5) * s),
                 ((icx + 7.5) * s, (icy - 5.5) * s)], fill=255, width=3 * s, joint='curve')))
    ink = Image.new('RGBA', img.size, INK + (255,))
    ink.putalpha(badge)
    img.alpha_composite(ink)
    words(d, px0 + 22 + 30 + 12, py0 + (py1 - py0) / 2 + 9, label, pill, INK)
    return img.convert('RGB')


# ------------------------------------------------------------ image 06 ----
def fix_06(src):
    img = replace_tube(
        src,
        old_boxes=[(80, 124, 354, 216), (88, 208, 347, 1167)],
        top=122, bottom=1172, cx=217)
    a = np.asarray(img).copy()

    # B12 amount: "1.11 mcg" -> "1.1 mcg", re-centred on the amount column.
    num = a[847:887, 882:911].copy()    # "1.1"
    unit = a[847:887, 933:992].copy()   # "mcg"
    a[847:887, 876:998] = TABLE_BG
    width = num.shape[1] + 11 + unit.shape[1]
    x = round(936 - width / 2)
    a[847:887, x:x + num.shape[1]] = num
    a[847:887, x + num.shape[1] + 11:x + width] = unit

    a[803:844, 572:732] = TABLE_BG      # "(Cyanocine)"
    a[847:887, 584:800] = TABLE_BG      # "(Cyanocobalamin)"
    a[354:396, 1124:1168] = TABLE_BG    # stray "15"
    img = Image.fromarray(a)

    d = ImageDraw.Draw(img)
    f = font('PlusJakartaSans-SemiBold.ttf', 17)
    words(d, 793, 1062, f'FSSAI Lic. No. {FSSAI}', f, INK, gap=0.3, center=True)
    return img


# ------------------------------------------------------------ image 07 ----
def fix_07(src):
    """Flat lay: AI-drawn label reads "WITH THE MOTHES" and "Vit B€"."""
    img = src.convert('RGB')
    a = np.asarray(img).astype(np.int32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    tube_px = (((r - b) < 14) & (a.sum(2) > 420)) | ((g - r > 30) & (g - b > 45))
    m = cv2.morphologyEx(tube_px.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    _, labels = cv2.connectedComponents(m)
    tube = labels == labels[600, 575]                    # the lying tube
    (cx, cy), (w, h), _ = rect = cv2.minAreaRect(
        np.argwhere(tube)[:, ::-1].astype(np.float32))
    box = cv2.boxPoints(rect)
    poly = np.zeros(tube.shape, np.uint8)
    cv2.fillPoly(poly, [box.round().astype(np.int32)], 1)
    ends = sorted(box.tolist(), key=lambda p: p[1])
    top_c = np.mean(ends[:2], 0)
    bot_c = np.mean(ends[2:], 0)
    angle = np.degrees(np.arctan2(top_c[0] - bot_c[0], bot_c[1] - top_c[1]))
    return replace_lying_tube(img, tube | (poly > 0), (cx, cy), round(min(w, h)) + 2, angle)


# ------------------------------------------------------------ image 08 ----
def fix_08(src):
    """Pure-black lettering -> the deep green every other infographic uses."""
    return recolor_black_text(src, [(55, 55, 715, 140), (250, 335, 520, 1040)], INK)


# ------------------------------------------------------------ image 09 ----
def fix_09(src):
    """Before/after: AI-drawn label small print is garbled ("1300 mg ACV")."""
    return replace_tube(src, old_boxes=[(940, 629, 1039, 1041)],
                        top=630, bottom=1039, cx=989, grow=5, shadow_alpha=48, shadow=(5, 4, 3.5))


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else GALLERY
    os.makedirs(out_dir, exist_ok=True)
    for n, fn in (('02', fix_02), ('03', fix_03), ('06', fix_06),
                  ('07', fix_07), ('08', fix_08), ('09', fix_09)):
        src = Image.open(os.path.join(GALLERY, f'product-{n}-minimal-v10.png'))
        dst = os.path.join(out_dir, f'product-{n}-minimal-v11.png')
        fn(src).save(dst, optimize=True)
        print('wrote', dst)


if __name__ == '__main__':
    main()
