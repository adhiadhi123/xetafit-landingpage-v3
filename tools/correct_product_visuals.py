"""Replace every visible AI-drawn XETAFIT tube on the landing page with the approved pack.

The approved pack is the official packshot `assets/images/product-gallery/actual-product-official-v3.jpg`
(label: XETAFIT / Zeal It. Feel It. / WITH THE MOTHER / APPLE CIDER VINEGAR / Energize. Metabolize. /
Green Apple Flavor / With Pomegranate Extract, Vit B6, Vit B12 / 500 mg ACV with 6% Acetic Acid /
15 Effervescent Tablets / NUTRACEUTICAL FIZZ TABLETS FOR ADULTS).

The replaced tubes read "DAILY PLANT-BASED", "Enzyme, Antioxidants" and "Health Supplement
(with Natural Sweetener)". Each scene keeps its composition: the old tube is removed (inpainted
where the new one does not cover it), the official tube is scaled to the same height (at most 6 %
wider, so it covers the old silhouette), relit to the scene from the old label's white areas,
and anything in front of the tube (fingers, a tablet) is restored from the original.

Images (in assets/images, written in place; the -768/-900/-190 copies are regenerated):
  hero-tube.webp (+ -190, and tube-front.webp, the sheen mask with the same silhouette)
  lifestyle-workspace.webp, lifestyle-move-v2.webp, lifestyle-move-wide-v2.webp,
  lifestyle-refresh-v2.webp, lifestyle-recharge-v2.webp, comparison-xetafit-centered-v1.webp,
  quality-product-care-v1.webp, final-product-drink.webp

usage:  python tools/correct_product_visuals.py [output_dir]
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, 'assets', 'images')
SRC = os.path.join(ROOT, 'assets', 'source')
MASTER = os.path.join(IMG, 'product-gallery', 'actual-product-official-v3.jpg')


def official_tube():
    """Official tube cut from its white studio background. The base follows its own dark
    contact line (y ~1390 at the sides, ~1402 at the centre), so no studio white is kept
    at the corners; that matters on the warm and dark scenes used here."""
    rgb = np.asarray(Image.open(MASTER).convert('RGB'))
    top, bottom, left, right = 143, 1406, 590, 912
    crop = rgb[top:bottom, left:right]
    d = 765 - crop.astype(np.int32).sum(2)
    h, w = d.shape
    mask = np.zeros((h, w), np.float32)
    body_l, body_r = 607 - left, 892 - left
    for y in range(h):
        xs = np.where(d[y] > 40)[0]
        if not len(xs):
            continue
        l, r = int(xs.min()), int(xs.max())
        if top + y >= 1370:
            l, r = max(l, body_l), min(r, body_r)
        mask[y, l:r + 1] = 1
    cx, half = (607 + 892) / 2, (892 - 607) / 2
    for x in range(w):
        u = (x + left - cx) / half
        if abs(u) <= 1:
            mask[int(np.ceil(1386 + 18 * np.sqrt(1 - u * u) - top)):, x] = 0
    mask = cv2.erode(mask, np.ones((1, 3), np.uint8))
    alpha = cv2.GaussianBlur(mask, (0, 0), 0.6)
    img = Image.fromarray(np.dstack([crop, (alpha * 255).clip(0, 255).astype(np.uint8)]), 'RGBA')
    return img.crop(img.getbbox())


TUBE = official_tube()                                   # RGBA, cap top to base bottom
_A = np.asarray(TUBE.getchannel('A')) > 128
_row = np.where(_A[int(TUBE.height * .6)])[0]
OFF_BODY = _row.max() - _row.min() + 1                   # body width in the cutout
OFF_CX = (_row.max() + _row.min()) / 2


# ------------------------------------------------------------- lighting ---
def _terms(u, v):
    return np.stack([np.ones_like(u), u, u * u, v, v * v, u * v], -1)


def fit_white(rgb, mask, u, v):
    """Smooth per-channel model of the label's white paper: lighting + white balance."""
    sel = mask & ((rgb.max(-1) - rgb.min(-1)) < 32) & (rgb.mean(-1) > 45)
    X = _terms(np.clip(u[sel], -.95, .95), np.clip(v[sel], .1, .98))
    out = []
    for c in range(3):
        y = rgb[..., c][sel].astype(np.float64)
        keep = np.ones(len(y), bool)
        for _ in range(3):                                # drop darker text pixels
            k, *_ = np.linalg.lstsq(X[keep], y[keep], rcond=None)
            keep = (y - X @ k) > -0.06 * y.mean()
        out.append(k)
    return np.array(out)


def evaluate(coefs, u, v):
    X = _terms(np.clip(u, -.95, .95), np.clip(v, .1, .98))
    return np.stack([X @ coefs[c] for c in range(3)], -1)


OFF_FIT = None


def official_fit():
    global OFF_FIT
    if OFF_FIT is None:
        a = np.asarray(TUBE).astype(np.float64)
        h, w = a.shape[:2]
        yy, xx = np.mgrid[0:h, 0:w]
        u = (xx - OFF_CX) / (OFF_BODY / 2)
        v = yy / h
        body = (a[..., 3] > 250) & (v > .12)
        OFF_FIT = fit_white(a[..., :3], body, u, v)
    return OFF_FIT


# ------------------------------------------------------------ placement ---
def make_tube(height, body_w, scene=None, old_visible=None, top=0, cx=0.0, max_stretch=1.06):
    """Official tube at `height`, widened up to 6 % towards `body_w`, relit to the scene."""
    s = height / TUBE.height
    stretch = float(np.clip(body_w / (OFF_BODY * s), 1.0, max_stretch))
    w = round(TUBE.width * s * stretch)
    t = TUBE.resize((w, height), Image.LANCZOS)
    a = np.asarray(t).astype(np.float64)
    new_body = OFF_BODY * s * stretch
    if scene is not None:
        yy, xx = np.mgrid[0:height, 0:w]
        u = (xx - w / 2) / (new_body / 2)
        v = yy / height
        # model of the old tube's white paper in the scene
        sh, sw = scene.shape[:2]
        Y, X = np.mgrid[0:sh, 0:sw]
        old_u = (X - cx) / (new_body / 2)
        old_v = (Y - top) / height
        old = fit_white(scene, old_visible & (old_v > .12), old_u, old_v)
        ratio = evaluate(old, u, v) / np.maximum(evaluate(official_fit(), u, v), 1)
        a[..., :3] = a[..., :3] * np.clip(ratio, .25, 1.35)
    return Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA'), new_body


def rect_mask(shape, rects):
    m = np.zeros(shape[:2], bool)
    for x0, y0, x1, y1 in rects:
        m[y0:y1, x0:x1] = True
    return m


def replace(img, *, rects, top, bottom, cx=None, right=None, body_w, hidden=(), occluder=None,
            drawn=None, original=None, grow=9, shadow=0):
    """Swap one tube. `hidden`: rects of tubes in front (never inpainted, not used for light).
    `right`: align the new tube's right body edge instead of centring (partly hidden tubes)."""
    original = img if original is None else original
    scene = np.asarray(img.convert('RGB')).copy()
    orig = np.asarray(original.convert('RGB'))
    h, w = scene.shape[:2]
    old = rect_mask(scene.shape, rects) & ~rect_mask(scene.shape, hidden)
    height = bottom - top
    if cx is None:
        _, nb = make_tube(height, body_w)
        cx = right - nb / 2
    tube, nb = make_tube(height, body_w, orig.astype(np.float64), old, top, cx)
    x = round(cx - tube.width / 2)

    alpha = np.zeros((h, w), np.uint8)
    ta = np.asarray(tube.getchannel('A'))
    x0, x1 = max(0, x), min(w, x + tube.width)
    y0, y1 = max(0, top), min(h, top + tube.height)
    alpha[y0:y1, x0:x1] = ta[y0 - top:y1 - top, x0 - x:x1 - x]
    # Inpaint the whole old silhouette (also under the new tube), so the fill comes from the
    # true background only and the old label's white edge cannot bleed out as a halo.
    hole = cv2.dilate(old.astype(np.uint8), np.ones((grow, grow), np.uint8)) > 0
    hole &= ~rect_mask(scene.shape, hidden)
    if drawn is not None:
        hole &= ~drawn
    bgr = cv2.inpaint(cv2.cvtColor(scene, cv2.COLOR_RGB2BGR), hole.astype(np.uint8) * 255, 6,
                      cv2.INPAINT_TELEA)
    out = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)).convert('RGBA')
    if shadow:                                                # contact shadow on the surface
        layer = Image.new('RGBA', out.size, (0, 0, 0, 0))
        ry = max(2.0, height * .012)
        ImageDraw.Draw(layer).ellipse((cx - nb * .6, bottom - 2 * ry, cx + nb * .6, bottom + ry * .6),
                                      fill=(30, 24, 14, shadow))
        out = Image.alpha_composite(out, layer.filter(ImageFilter.GaussianBlur(max(1.5, height / 110))))
    out.alpha_composite(tube, (x, top))
    out = out.convert('RGB')
    if occluder is not None:                                  # fingers / tablet in front
        k = cv2.GaussianBlur(occluder.astype(np.float32), (0, 0), .9)[..., None]
        out = Image.fromarray((orig * k + np.asarray(out) * (1 - k)).round().astype(np.uint8))
    if drawn is not None:
        drawn |= alpha > 128
    return out


def skin(original, box):
    """Fingers in front of a tube: warm skin tones inside `box` only."""
    a = np.asarray(original.convert('RGB')).astype(np.int32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = (r > 80) & (g > .42 * r) & (g < .9 * r) & (b < g) & (r - b > 28)
    keep = np.zeros_like(m)
    x0, y0, x1, y1 = box
    keep[y0:y1, x0:x1] = m[y0:y1, x0:x1]
    keep = cv2.morphologyEx(keep.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    keep = cv2.morphologyEx(keep, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(keep)
    return np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= 25])


# --------------------------------------------------------------- scenes ---
def hero():
    """Transparent cutout on the same 360 x 1369 canvas (the CSS rotates it)."""
    W, H = 360, 1369
    s = H / TUBE.height
    stretch = 353 / (TUBE.width * s)                 # old cap spanned x 3-355
    t = TUBE.resize((round(TUBE.width * s * stretch), H), Image.LANCZOS)
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    canvas.alpha_composite(t, (round((W - t.width) / 2), 0))
    return canvas


def workspace(im):
    return replace(im, rects=[(642, 31, 878, 112), (653, 92, 864, 903)], top=35, bottom=895,
                   cx=758.5, body_w=203, grow=13, shadow=85)


def compare(im):
    occ = np.zeros((im.height, im.width), bool)
    occ[834:894, 494:559] = True                     # the tablet in front of the base
    return replace(im, rects=[(538, 110, 752, 162), (549, 154, 740, 886)], top=115, bottom=880,
                   cx=645, body_w=184, occluder=occ, grow=13, shadow=70)


def recharge(im):
    return replace(im, rects=[(862, 306, 966, 346), (866, 338, 961, 679)], top=310, bottom=673,
                   cx=913.5, body_w=87, grow=11, shadow=70)


def quality(im):
    return replace(im, rects=[(645, 43, 871, 132), (657, 124, 862, 859)], top=48, bottom=853,
                   cx=759.5, body_w=195, shadow=45)


def move(im):
    return replace(im, rects=[(349, 503, 447, 542), (351, 535, 448, 849)], top=508, bottom=845,
                   cx=399, body_w=88, occluder=skin(im, (328, 610, 384, 862)))


def refresh(im):
    return replace(im, rects=[(431, 226, 522, 263), (435, 257, 519, 548)], top=230, bottom=544,
                   cx=477, body_w=75, occluder=skin(im, (404, 330, 470, 562)))


def final(im):
    orig = im
    drawn = np.zeros((im.height, im.width), bool)
    t1 = [(275, 76, 493, 122), (285, 114, 485, 871)]
    t2 = [(479, 98, 665, 142), (479, 134, 658, 856)]
    t3 = [(655, 116, 816, 157), (653, 149, 806, 846)]
    t4 = [(805, 136, 953, 177), (796, 169, 946, 834)]
    im = replace(im, rects=t4, hidden=t3, top=140, bottom=828, right=943, body_w=165,
                 drawn=drawn, original=orig, shadow=80)
    im = replace(im, rects=t3, hidden=t2, top=120, bottom=840, right=803, body_w=172,
                 drawn=drawn, original=orig, shadow=80)
    im = replace(im, rects=t2, hidden=t1, top=102, bottom=850, right=655, body_w=178,
                 drawn=drawn, original=orig, shadow=80)
    im = replace(im, rects=t1, top=80, bottom=865, cx=385, body_w=194, drawn=drawn, original=orig,
                shadow=80)
    return im


def wide(im):
    return replace(im, rects=[(829, 163, 861, 172), (830, 168, 860, 270)], top=166, bottom=267,
                   cx=845, body_w=25, occluder=skin(im, (800, 205, 870, 274)), grow=5)


def save(im, path, q=88):
    im.save(path, 'WEBP', quality=q, method=6)


def small(path, out, width):
    im = Image.open(path)
    im.resize((width, round(im.height * width / im.width)), Image.LANCZOS).save(
        out, 'WEBP', quality=84, method=6)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else IMG
    os.makedirs(out, exist_ok=True)
    jobs = [
        ('lifestyle-workspace.webp', workspace, None, [('lifestyle-workspace-768.webp', 768)]),
        ('comparison-xetafit-centered-v1.webp', compare, 'comparison-xetafit-centered-v1.png',
         [('comparison-xetafit-centered-v1-768.webp', 768)]),
        ('lifestyle-recharge-v2.webp', recharge, None, [('lifestyle-recharge-v2-768.webp', 768)]),
        ('quality-product-care-v1.webp', quality, 'quality-product-care-v1.png',
         [('quality-product-care-v1-768.webp', 768)]),
        ('lifestyle-move-v2.webp', move, None, [('lifestyle-move-v2-768.webp', 615)]),
        ('lifestyle-refresh-v2.webp', refresh, None, [('lifestyle-refresh-v2-768.webp', 768)]),
        ('final-product-drink.webp', final, None, [('final-product-drink-768.webp', 768)]),
        ('lifestyle-move-wide-v2.webp', wide, None, [('lifestyle-move-wide-v2-900.webp', 900)]),
    ]
    only = os.environ.get('ONLY')
    for name, fn, master, variants in jobs:
        if only and only not in name:
            continue
        src = os.path.join(SRC, master) if master else os.path.join(IMG, name)
        im = Image.open(src).convert('RGB')
        dst = os.path.join(out, name)
        save(fn(im), dst)
        for vname, vw in variants:
            small(dst, os.path.join(out, vname), vw)
        print('wrote', name, '+', ', '.join(v for v, _ in variants))
    if not only or 'hero' in only:
        h = hero()
        h.save(os.path.join(out, 'hero-tube.webp'), 'WEBP', quality=90, method=6)
        h.save(os.path.join(out, 'tube-front.webp'), 'WEBP', quality=90, method=6)   # sheen mask
        h.resize((190, 723), Image.LANCZOS).save(os.path.join(out, 'hero-tube-190.webp'), 'WEBP',
                                                 quality=90, method=6)
        print('wrote hero-tube.webp, hero-tube-190.webp, tube-front.webp')


if __name__ == '__main__':
    main()
