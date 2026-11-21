#!/usr/bin/env python3
"""Gera os fragmentos SVG decorativos (montanhas low-poly, estrelas, pinheiros)
e os injeta no index.html entre os marcadores <!--GEN:nome--> ... <!--/GEN:nome-->.

Uso:  python3 tools/illustrations.py

O resultado é determinístico (seeds fixas): rodar de novo produz o mesmo HTML.
Só é preciso rodar este script se você quiser alterar as ilustrações geradas.
"""
from __future__ import annotations

import math
import pathlib
import random
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
HTML = ROOT / "index.html"

# Paletas (claro -> escuro)
LIT = ["#FFD884", "#FFBE5E", "#FFA552", "#F78C4A", "#E57246"]
SHADE = ["#7254C6", "#6246B4", "#553CA3", "#493392", "#3D2B80"]
BACK_LIT = ["#5A45AE", "#5240A2", "#4B3A96", "#44358A", "#3D307F"]
BACK_SHADE = ["#3F3087", "#392A7C", "#332671", "#2E2267", "#291F5E"]


def fmt(v: float) -> str:
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def pts(points) -> str:
    return " ".join(f"{fmt(x)},{fmt(y)}" for x, y in points)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def poly(points, color: str) -> str:
    # stroke da mesma cor evita frestas de anti-aliasing entre as facetas
    return f'<polygon points="{pts(points)}" fill="{color}" stroke="{color}"/>'


def mountain(rng, apex, base_y, left_x, right_x, ridge_x, lit=LIT, shade=SHADE, jitter=4.0):
    """Montanha low-poly: face iluminada (esquerda) + face na sombra (direita)."""
    A = apex
    L, R, R0 = (left_x, base_y), (right_x, base_y), (ridge_x, base_y)

    def j(p, k=1.0):
        return (p[0] + rng.uniform(-jitter, jitter) * k, p[1] + rng.uniform(-jitter, jitter) * k)

    Rm = j(lerp(A, R0, rng.uniform(0.42, 0.56)), 0.6)
    Lm = j(lerp(A, L, rng.uniform(0.36, 0.52)))
    Rbm = j(lerp(A, R, rng.uniform(0.36, 0.52)))
    C1 = j(((Lm[0] + L[0] + R0[0] + Rm[0]) / 4, (Lm[1] + L[1] + R0[1] + Rm[1]) / 4))
    C2 = j(((Rm[0] + R0[0] + R[0] + Rbm[0]) / 4, (Rm[1] + R0[1] + R[1] + Rbm[1]) / 4))
    lit_mid = [lit[1], lit[2]]
    rng.shuffle(lit_mid)
    shade_mid = [shade[1], shade[2]]
    rng.shuffle(shade_mid)
    return "\n".join(
        [
            poly([A, Lm, Rm], lit[0]),
            poly([Lm, C1, Rm], lit_mid[0]),
            poly([Lm, L, C1], lit_mid[1]),
            poly([Rm, C1, R0], lit[3]),
            poly([L, R0, C1], lit[4]),
            poly([A, Rm, Rbm], shade[0]),
            poly([Rm, C2, Rbm], shade_mid[0]),
            poly([Rm, R0, C2], shade_mid[1]),
            poly([Rbm, C2, R], shade[3]),
            poly([R0, R, C2], shade[4]),
        ]
    )


def range_(seed, specs, base_y, lit=LIT, shade=SHADE, jitter=4.0):
    rng = random.Random(seed)
    return "\n".join(
        mountain(rng, (ax, ay), base_y, lx, rx, rdx, lit, shade, jitter) for ax, ay, lx, rx, rdx in specs
    )


def stars(seed, n, x0, y0, x1, y1, rmin=0.6, rmax=1.7, twinkle=0.25):
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        r = rng.uniform(rmin, rmax)
        o = rng.uniform(0.3, 0.95)
        if rng.random() < twinkle:
            out.append(
                f'<circle class="tw" cx="{fmt(x)}" cy="{fmt(y)}" r="{r:.1f}" opacity="{o:.2f}" '
                f'style="animation-delay:-{rng.uniform(0, 5):.1f}s"/>'
            )
        else:
            out.append(f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="{r:.1f}" opacity="{o:.2f}"/>')
    return "\n".join(out)


def pine(x, base, h):
    w = h * 0.44
    p = [
        (x, base - h),
        (x + w * 0.30, base - h * 0.66), (x + w * 0.13, base - h * 0.66),
        (x + w * 0.45, base - h * 0.37), (x + w * 0.24, base - h * 0.37),
        (x + w * 0.60, base - h * 0.09),
        (x + w * 0.07, base - h * 0.09), (x + w * 0.07, base + 2), (x - w * 0.07, base + 2),
        (x - w * 0.07, base - h * 0.09),
        (x - w * 0.60, base - h * 0.09),
        (x - w * 0.24, base - h * 0.37), (x - w * 0.45, base - h * 0.37),
        (x - w * 0.13, base - h * 0.66), (x - w * 0.30, base - h * 0.66),
    ]
    return f'<polygon points="{pts(p)}"/>'


def hill_path(fn, width, bottom, step=16):
    xs = list(range(0, width + step, step))
    d = [f"M0 {fmt(fn(0))}"] + [f"L{x} {fmt(fn(x))}" for x in xs[1:]]
    return " ".join(d) + f" V{bottom} H0 Z"


# ---------------------------------------------------------------- Hero (portal)
def hero_back():
    specs = [
        (110, 292, -10, 230, 128),
        (255, 258, 140, 380, 270),
        (430, 246, 320, 560, 445),
        (560, 290, 470, 660, 575),
    ]
    return range_(11, specs, 412, BACK_LIT, BACK_SHADE, 3)


def hero_front():
    specs = [
        (398, 148, 250, 610, 432),  # pico mais alto (fundo)
        (522, 262, 420, 650, 538),
        (214, 186, 40, 372, 248),
        (78, 300, -40, 182, 96),
    ]
    return range_(7, specs, 414, LIT, SHADE, 4)


def hero_stars():
    return stars(3, 46, 70, 70, 530, 250, 0.5, 1.5, 0.35)


def page_stars(seed, n, w=1440, h=900):
    return stars(seed, n, 0, 0, w, h, 0.5, 1.6, 0.3)


# ---------------------------------------------------------------- Card logística
def card_logistics():
    specs = [
        (150, 78, 92, 236, 164),
        (66, 58, -10, 138, 84),
    ]
    return range_(21, specs, 142, LIT, SHADE, 2)


# ---------------------------------------------------------------- Contato (paisagem)
def h1(x):
    return 452 + 12 * math.sin(x / 150 + 0.6) + 7 * math.sin(x / 57 + 1.3)


def h2(x):
    return 494 + 10 * math.sin(x / 190 + 2.1) + 6 * math.sin(x / 63 + 0.4)


def contact_back():
    specs = [
        (70, 262, -140, 260, 96),
        (330, 196, 120, 540, 352),
        (600, 246, 420, 790, 626),
        (880, 184, 680, 1080, 902),
        (1150, 228, 960, 1330, 1172),
        (1390, 188, 1220, 1580, 1410),
    ]
    return range_(31, specs, 450, BACK_LIT, BACK_SHADE, 5)


def contact_front():
    specs = [
        (990, 112, 790, 1200, 1022),
        (712, 176, 520, 910, 744),
        (1250, 214, 1090, 1450, 1282),
        (430, 236, 250, 630, 460),
        (1440, 300, 1320, 1580, 1460),
        (150, 300, -50, 340, 176),
    ]
    return range_(37, specs, 470, LIT, SHADE, 6)


def contact_hills():
    rng = random.Random(41)
    out = [f'<path d="{hill_path(h1, 1440, 520)}" fill="#130D36"/>']
    trees = []
    x = 6
    while x < 1440:
        if not 250 < x < 520:  # espaço livre para a entrada da mina
            trees.append(pine(x, h1(x) + 4, rng.uniform(26, 58)))
        x += rng.uniform(14, 34)
    out.append('<g fill="#181040">' + "".join(trees) + "</g>")
    out.append(f'<path d="{hill_path(h2, 1440, 520)}" fill="#0C0826"/>')
    trees = []
    x = 0
    while x < 1440:
        if rng.random() < 0.82 and not 200 < x < 560:
            trees.append(pine(x, h2(x) + 6, rng.uniform(44, 96)))
        x += rng.uniform(18, 46)
    out.append('<g fill="#090619">' + "".join(trees) + "</g>")
    return "\n".join(out)


GENERATORS = {
    "hero-back": hero_back,
    "hero-front": hero_front,
    "hero-stars": hero_stars,
    "hero-bg-stars": lambda: page_stars(5, 110),
    "card-logistics": card_logistics,
    "contact-stars": lambda: page_stars(9, 140),
    "contact-back": contact_back,
    "contact-front": contact_front,
    "contact-hills": contact_hills,
}


def main():
    html = HTML.read_text(encoding="utf-8")
    for name, fn in GENERATORS.items():
        pattern = re.compile(rf"(<!--GEN:{re.escape(name)}-->)(.*?)(<!--/GEN:{re.escape(name)}-->)", re.S)
        if not pattern.search(html):
            print(f"  ! marcador não encontrado: {name}")
            continue
        html = pattern.sub(lambda m: m.group(1) + "\n" + fn() + "\n" + m.group(3), html)
        print(f"  ok {name}")
    HTML.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
