#!/usr/bin/env python3
"""Vloží skutečný snímek aplikace do černého (vypnutého) displeje vygenerované fotky telefonu.

Fotky telefonu na lodi (media/photo/*.png, mimo git, kopie na Drivu) jsou vygenerované s úplně černým displejem;
na web nikdy nejde generované UI. Snímek obrazovky je vždy skutečný export z aplikace
(Saildays/store/screenshots/<jazyk>/0x-*.png, 1080x2160).

Postup: největší souvislá tmavá plocha fotky = displej; z jejího konvexního obalu čtyři rohy (extrémy ve směrech
úhlopříček), hrany se zpřesní proložením přímek body obrysu (střední část každé hrany, rohy jsou zaoblené) a rohy
jsou průsečíky přímek. Snímek se do čtyřúhelníku promítne homografií, zaoblené rohy displeje dostane maskou
(poloměr odhadnutý z rozdílu zaobleného a ostrého rohu), navrch se vrátí odlesky skla z původní fotky (screen).

    .venv/bin/python tools/compose_phone.py <foto.png> <snímek.png> <výstup.png>
        [--corners x,y,x,y,x,y,x,y]   rohy displeje ručně (TL, TR, BR, BL v pixelech fotky), když detekce selže
        [--thr 38]                     jas (max RGB), pod kterým je pixel „černý displej"
        [--radius 0.07]                zaoblení rohů jako podíl šířky snímku (přebije odhad)
        [--crop x0,y0,x1,y1]           ořez výsledku (pixely fotky)
        [--webp cesta/bez-pripony --widths 800,480 --quality 80]   WebP varianty pro web (šířky po ořezu)
        [--debug kontrola.png]         obrys nalezeného displeje (tyrkys), body obrysu (červeně), rohy (žlutě)

Jen Pillow + numpy (venv .venv, requirements.txt). Dávkově pro web: tools/photos.sh.
"""
import json
import math
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def largest_dark_component(lum, thr, scale=4):
    """Největší souvislá tmavá oblast (BFS na zmenšené masce) -> bounding box ve full-res a semínko."""
    h, w = lum.shape
    small = lum[::scale, ::scale] < thr
    sh, sw = small.shape
    seen = np.zeros_like(small, bool)
    best, best_n = None, 0
    for sy in range(sh):
        for sx in range(sw):
            if not small[sy, sx] or seen[sy, sx]:
                continue
            q = deque([(sy, sx)]); seen[sy, sx] = True
            pts = []
            while q:
                y, x = q.popleft(); pts.append((y, x))
                for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                    if 0 <= ny < sh and 0 <= nx < sw and small[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True; q.append((ny, nx))
            if len(pts) > best_n:
                best_n, best = len(pts), pts
    if not best or best_n < 200:
        raise SystemExit("displej nenalezen (žádná dostatečně velká tmavá plocha, zkus --thr nebo --corners)")
    ys = np.array([p[0] for p in best]); xs = np.array([p[1] for p in best])
    seed = (int(np.median(xs)) * scale, int(np.median(ys)) * scale)
    return seed


def fill_component(dark, seed):
    """Souvislá oblast tmavé masky kolem semínka ve full-res (PIL floodfill), jako bool pole."""
    img = Image.fromarray(np.where(dark, 255, 0).astype(np.uint8)).copy()  # fromarray sdílí buffer jen pro čtení
    sx, sy = seed
    if not dark[sy, sx]:
        ys, xs = np.nonzero(dark[max(0, sy - 30):sy + 30, max(0, sx - 30):sx + 30])
        if len(xs) == 0:
            raise SystemExit("semínko displeje neleží v tmavé ploše")
        sx, sy = xs[0] + max(0, sx - 30), ys[0] + max(0, sy - 30)
    ImageDraw.floodfill(img, (int(sx), int(sy)), 128)
    return np.asarray(img) == 128


def boundary(mask):
    """Body obrysu masky (pixel masky s aspoň jedním sousedem mimo)."""
    inner = mask & np.roll(mask, 1, 0) & np.roll(mask, -1, 0) & np.roll(mask, 1, 1) & np.roll(mask, -1, 1)
    ys, xs = np.nonzero(mask & ~inner)
    return np.stack([xs, ys], 1).astype(float)


def extreme_corners(pts):
    """Rohy čtyřúhelníku z extrémů v úhlopříčných směrech: TL, TR, BR, BL (pro natočení do ~40°)."""
    x, y = pts[:, 0], pts[:, 1]
    return np.array([pts[np.argmin(x + y)], pts[np.argmax(x - y)], pts[np.argmax(x + y)], pts[np.argmin(x - y)]])


def fit_line(p):
    """Přímka metodou nejmenších čtverců (PCA): bod a směrový vektor."""
    c = p.mean(0)
    _, _, vt = np.linalg.svd(p - c)
    return c, vt[0]


def intersect(l1, l2):
    (p1, d1), (p2, d2) = l1, l2
    A = np.array([d1, -d2]).T
    t = np.linalg.solve(A, p2 - p1)
    return p1 + t[0] * d1


def refine_corners(pts, corners, band=0.15, tol=None):
    """Hrany mezi rohy proložit přímkami ze středních 70 % obrysu (rohy jsou zaoblené), rohy = průsečíky."""
    lines = []
    for i in range(4):
        a, b = corners[i], corners[(i + 1) % 4]
        d = b - a; L = np.linalg.norm(d); d /= L
        n = np.array([-d[1], d[0]])
        rel = pts - a
        t = (rel * d).sum(1) / L
        dist = np.abs((rel * n).sum(1))
        tol_i = tol if tol else max(4.0, 0.03 * L)
        sel = (t > band) & (t < 1 - band) & (dist < tol_i)
        if sel.sum() < 10:
            raise SystemExit("hrana %d: málo bodů obrysu (%d), zadej --corners" % (i, sel.sum()))
        lines.append(fit_line(pts[sel]))
    sharp = np.array([intersect(lines[(i - 1) % 4], lines[i]) for i in range(4)])
    # odhad zaoblení rohu: vzdálenost zaobleného (extrémního) bodu od ostrého rohu po úhlopříčce = r (sqrt2 - 1)
    r_px = float(np.mean([np.linalg.norm(sharp[i] - corners[i]) for i in range(4)]) / (math.sqrt(2) - 1))
    return sharp, r_px


def homography(src, dst):
    """Homografie 3x3 ze 4 dvojic bodů src -> dst."""
    A, b = [], []
    for (u, v), (x, y) in zip(src, dst):
        A.append([u, v, 1, 0, 0, 0, -u * x, -v * x]); b.append(x)
        A.append([0, 0, 0, u, v, 1, -u * y, -v * y]); b.append(y)
    h = np.linalg.solve(np.array(A, float), np.array(b, float))
    return np.append(h, 1).reshape(3, 3)


def fit_aspect(shot, aspect):
    """Snímek 1080x2160 (1:2) na poměr displeje z fotky (telefony mají ~1:2.2): místo roztažení se doplní okraje
    opakováním krajního řádku / sloupce (stavová lišta nahoře a spodní lišta jsou jednobarevné, prodloužení není vidět)."""
    W, Hs = shot.size
    arr = np.asarray(shot)
    want_h = int(round(W * aspect))
    if want_h > Hs:
        top = (want_h - Hs) // 2; bot = want_h - Hs - top
        arr = np.concatenate([np.repeat(arr[:1], top, 0), arr, np.repeat(arr[-1:], bot, 0)], 0)
    elif want_h < Hs:
        want_w = int(round(Hs / aspect))
        left = (want_w - W) // 2; right = want_w - W - left
        arr = np.concatenate([np.repeat(arr[:, :1], left, 1), arr, np.repeat(arr[:, -1:], right, 1)], 1)
    return Image.fromarray(arr)


def warp(img, H_img_to_photo, size):
    """Obrázek promítnutý do fotky: Pillow chce mapování výstup -> vstup (inverzní homografii)."""
    T = np.linalg.inv(H_img_to_photo); T = T / T[2, 2]
    return img.transform(size, Image.PERSPECTIVE, tuple(T.flatten()[:8]), resample=Image.BICUBIC)


def compose(photo_path, shot_path, out_path, corners=None, thr=38, radius=None, crop=None, webp=None,
            widths=(800, 480), quality=80, debug=None):
    photo = Image.open(photo_path).convert("RGB")
    arr = np.asarray(photo).astype(float)
    lum = arr.max(axis=2)
    if corners is None:
        seed = largest_dark_component(lum, thr)
        comp = fill_component(lum < thr, seed)
        pts = boundary(comp)
        rough = extreme_corners(pts)
        corners, r_px = refine_corners(pts, rough)
        found = "detekce"
    else:
        corners = np.array(corners, float).reshape(4, 2)
        pts, r_px, found = np.zeros((0, 2)), 0.0, "ručně"
    shot = Image.open(shot_path).convert("RGB")
    disp_w = (np.linalg.norm(corners[1] - corners[0]) + np.linalg.norm(corners[2] - corners[3])) / 2
    disp_h = (np.linalg.norm(corners[3] - corners[0]) + np.linalg.norm(corners[2] - corners[1])) / 2
    shot = fit_aspect(shot, disp_h / disp_w)
    W, Hs = shot.size
    H = homography([(0, 0), (W, 0), (W, Hs), (0, Hs)], corners)
    scale = W / disp_w
    r = radius * W if radius is not None else min(max(r_px * scale, 0), 0.12 * W)
    # maska displeje: zaoblený obdélník v souřadnicích snímku (lehce zevnitř, ať nezůstane světlý lem), promítnutý stejně
    S = 2
    m = Image.new("L", (W * S, Hs * S), 0)
    ImageDraw.Draw(m).rounded_rectangle([S, S, W * S - S, Hs * S - S], radius=r * S, fill=255)
    m = m.resize((W, Hs), Image.LANCZOS)
    mask = np.asarray(warp(m, H, photo.size)).astype(float) / 255
    # odlesky skla z původní fotky: co je na černém displeji světlejší než černá
    inside = mask > 0.5
    base = np.percentile(lum[inside], 15) if inside.any() else 0
    gloss = np.clip(arr - base, 0, None) * 0.8
    gloss = np.asarray(Image.fromarray(gloss.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))).astype(float)
    warped = np.asarray(warp(shot, H, photo.size)).astype(float) * 0.96
    disp = 255 - (255 - warped) * (255 - gloss) / 255  # screen
    out = arr * (1 - mask[..., None]) + disp * mask[..., None]
    img = Image.fromarray(out.clip(0, 255).astype(np.uint8))
    if debug:
        dbg = img.copy(); dd = ImageDraw.Draw(dbg)
        for px, py in pts[::3]:
            dd.point((px, py), fill=(255, 0, 0))
        poly = [tuple(c) for c in corners]
        dd.line(poly + [poly[0]], fill=(0, 255, 255), width=2)
        for cx, cy in poly:
            dd.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], outline=(255, 255, 0), width=2)
        dbg.save(debug)
    if crop:
        img = img.crop(crop)
    img.save(out_path)
    if webp:
        for wdt in widths:
            o = img.resize((wdt, round(img.height * wdt / img.width)), Image.LANCZOS)
            name = "%s%s.webp" % (webp, "" if wdt == widths[0] else "-%d" % wdt)
            o.save(name, "WEBP", quality=quality, method=6)
            print("  %s %dx%d" % (name, o.width, o.height))
    info = {"photo": photo_path, "shot": shot_path, "corners": [[round(float(a), 1) for a in c] for c in corners],
            "radius_px_shot": round(float(r), 1), "found": found, "crop": crop}
    print(out_path, json.dumps(info, ensure_ascii=False))
    return corners


def parse_args(argv):
    opts = {"--corners": "", "--thr": "38", "--radius": "", "--crop": "", "--webp": "", "--widths": "800,480",
            "--quality": "80", "--debug": ""}
    for k in list(opts):
        if k in argv:
            i = argv.index(k); opts[k] = argv[i + 1]; del argv[i:i + 2]
    if len(argv) != 3:
        print(__doc__); sys.exit(2)
    return argv, opts


if __name__ == "__main__":
    args, o = parse_args(sys.argv[1:])
    compose(args[0], args[1], args[2],
            corners=[float(v) for v in o["--corners"].split(",")] if o["--corners"] else None,
            thr=float(o["--thr"]), radius=float(o["--radius"]) if o["--radius"] else None,
            crop=tuple(int(v) for v in o["--crop"].split(",")) if o["--crop"] else None,
            webp=o["--webp"] or None, widths=tuple(int(v) for v in o["--widths"].split(",")),
            quality=int(o["--quality"]), debug=o["--debug"] or None)
