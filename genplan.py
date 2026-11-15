"""Generate schematic floor plans (EG, 1. OG) for Neißstraße 28 as inline SVG.

Geometry is traced from the construction drawing in "u" units (~1 cm), portrait
orientation: x = left outer wall -> right, y = back outer wall -> street.
Each floor is emitted twice: "tall" (street at the bottom) and "wide" (rotated
90 degrees, street on the left). Labels stay upright in both.
"""
import math
import re
import sys

def fac_out(x): return 2220 - 0.12 * x
def fac_in(x): return 2125 - 0.12 * x

OUTLINE = [(0, 0), (680, 0), (680, 805), (875, 805), (875, fac_out(875)), (0, fac_out(0))]
ANNEX = [(35, -245), (490, -245), (490, -185), (695, -185), (695, 0), (35, 0)]
HOF = [(65, -172), (470, -172), (470, 0), (65, 0)]

def rect(x1, y1, x2, y2): return [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
def facade(x1, x2, inset=0):
    return [(x1, fac_out(x1) + inset), (x2, fac_out(x2) + inset), (x2, fac_in(x2) - inset), (x1, fac_in(x1) - inset)]

def door(h, c, o):
    """Door leaf from hinge h to open end o, swing arc from o back to closed end c."""
    r = math.dist(h, c)
    cross = (o[0] - h[0]) * (c[1] - h[1]) - (o[1] - h[1]) * (c[0] - h[0])
    sweep = 1 if cross > 0 else 0
    return f"M{h[0]:g} {h[1]:g}L{o[0]:g} {o[1]:g}A{r:g} {r:g} 0 0 {sweep} {c[0]:g} {c[1]:g}"

def treads(x1, x2, y1, y2, n):
    step = (y2 - y1) / n
    return "".join(f"M{x1:g} {y1 + i * step:g}H{x2:g}" for i in range(n + 1))

def treads_x(x1, x2, y1, y2, n):
    step = (x2 - x1) / n
    return "".join(f"M{x1 + i * step:g} {y1:g}V{y2:g}" for i in range(n + 1))

def cabin(x1, y1, x2, y2):
    return f"M{x1} {y1}H{x2}V{y2}H{x1}ZM{x1} {y1}L{x2} {y2}M{x2} {y1}L{x1} {y2}"

def lerp(a, b, t): return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)

# --- Erdgeschoss -------------------------------------------------------------
g1_diag = ((300, 1455), (425, 1630))
hall_diag = ((340, 1455), (445, 1610))

EG = dict(
    key="eg",
    label="Grundriss Erdgeschoss: Von der Neißstraße betritt man links den Gastraum 1, rechts die Eingangshalle des Hauses. "
          "Hinter dem Gastraum führt eine Treppe ins 1. Obergeschoss; dahinter liegen Bar und Küche, ganz hinten Hof und Kühllager. "
          "Über einen Gang erreicht man den Vorraum des Aufzugs und die Kellertreppe.",
    annex=True,
    fills=[
        ("p-room", [(45, 75), (410, 75), (410, 155), (490, 155), (490, 95), (630, 95), (630, 625), (460, 625), (460, 555),
                    (415, 555), (415, 685), (260, 685), (260, 535), (200, 535), (200, 685), (45, 685)]),  # Küche
        ("p-room", [(45, 735), (415, 735), (415, 1010), (260, 1010), (260, 925), (45, 925)]),  # Bar
        ("p-room", rect(490, -155, 665, 0)),  # Kühllager
        ("p-hall", [(45, 925), (190, 925), (305, 1455), (45, 1455)]),  # Treppe
        ("p-hall", [(278, 1035), (425, 1035), (425, 1455), (340, 1455)]),  # Gang
        ("p-hall", rect(460, 860, 630, 1195)),  # Vorraum Aufzug
        ("p-hall", rect(440, 1215, 530, 1455)),  # Kellertreppe
        ("p-hall", [(340, 1455), (645, 1455), (645, 1145), (800, 1145), (800, fac_in(800)), (545, fac_in(545)),
                    (545, 1610), (445, 1610)]),  # Eingangshalle
        ("p-guest", [(45, 1455), (300, 1455), (425, 1630), (525, 1630), (525, fac_in(525)), (45, fac_in(45))]),  # Gastraum 1
        ("p-hall", rect(480, 675, 605, 830)),  # Aufzugskabine
    ],
    openings=[
        ("p-room", rect(280, -2, 400, 77)),  # Küche -> Hof
        ("p-room", rect(500, -2, 615, 97)),  # Küche -> Kühllager (Stufen)
        ("p-room", rect(95, 683, 185, 737)),  # Tür Küche/Bar
        ("p-room", rect(260, 683, 415, 737)),  # offener Durchgang Küche/Bar
        ("p-hall", rect(280, 1008, 360, 1037)),  # T30 Bar/Gang
        ("p-hall", rect(423, 1060, 462, 1170)),  # Gang/Vorraum
        ("p-hall", rect(500, 828, 585, 862)),  # Aufzugstür
        ("p-hall", [lerp(*g1_diag, 0.3), lerp(*g1_diag, 0.75), lerp(*hall_diag, 0.78), lerp(*hall_diag, 0.33)]),  # Gastraum/Halle
        ("p-guest", facade(120, 280, -2)),  # Eingang Gastraum
        ("p-hall", facade(585, 735, -2)),  # Hauseingang
    ],
    windows=[("front", 345, 505)],
    thin=[
        door((280, 75), (340, 75), (280, 135)), door((400, 75), (340, 75), (400, 135)),  # Hoftür, zweiflügelig
        door((185, 685), (95, 685), (185, 595)),  # Küche/Bar
        door((280, 1010), (360, 1010), (280, 930)),  # T30 Bar/Gang
        "M505 25H610M505 50H610M505 75H610",  # Stufen zum Kühllager
        treads(55, 180, 940, 1380, 18) + "M180 940V1380",  # Treppe ins OG
        treads(660, 800, 1150, 1695, 21),  # Treppenhaus
        treads(445, 525, 1225, 1445, 8),  # Kellertreppe
        cabin(480, 675, 605, 830),
    ],
    dashed=["M55 2045H300V" + f"{fac_in(300):g}"],  # Windfang
    labels=[
        dict(t=["Gastraum 1"], x=285, y=1860, cls="p-name", sub="28 Plätze"),
        dict(t=["Küche"], x=330, y=390, cls="p-name"),
        dict(t=["Bar"], x=230, y=830, cls="p-name"),
        dict(t=["Eingangs-", "halle"], x=672, y=1860, cls="p-name"),
        dict(t=["Hof"], x=268, y=-86, cls="p-small p-out"),
        dict(t=["Kühl-", "lager"], x=577, y=-78, cls="p-small"),
        dict(t=["Gang"], x=372, y=1240, cls="p-small", along=True),
        dict(t=["Vorraum"], x=545, y=1030, cls="p-small", along=True),
        dict(t=["Aufzug"], x=542, y=752, cls="p-small", halo=True, size=30),
        dict(t=["Keller"], x=485, y=1335, cls="p-small", along=True, halo=True, size=30),
        dict(t=["Treppe ins 1. OG"], x=117, y=1160, cls="p-small", along=True, halo=True),
        dict(t=["Treppenhaus"], x=730, y=1420, cls="p-small", along=True, halo=True),
    ],
    entrances=[(200, "Eingang"), (660, "Hauseingang")],
)

# --- 1. Obergeschoss ---------------------------------------------------------
OG = dict(
    key="og",
    label="Grundriss 1. Obergeschoss: Zur Neißstraße liegen der große Gastraum 2 mit zwei Fenstern und der schmale Gastraum 3 mit einem Fenster, "
          "verbunden durch eine Tür. Dahinter kommt die Treppe aus dem Erdgeschoss an, daneben das Treppenhaus des Hauses mit Aufzug. "
          "Zum Hof liegen ein Flur, zwei Lagerräume und die WCs für Damen, Herren und Personal.",
    annex=False,
    fills=[
        ("p-room", rect(45, 95, 245, 415)),  # WC Herren
        ("p-room", rect(260, 95, 620, 315)),  # WC Damen
        ("p-room", rect(375, 335, 620, 465)),  # WC Personal
        ("p-hall", [(45, 430), (265, 430), (265, 330), (360, 330), (360, 530), (45, 530)]),  # WC-Flur
        ("p-hall", [(45, 595), (255, 595), (255, 925), (320, 925), (320, 1395), (55, 1395), (55, 925), (135, 925),
                    (135, 830), (45, 830)]),  # Flur + Treppe
        ("p-room", rect(270, 600, 435, 835)),  # Lager
        ("p-room", rect(710, 875, 830, 1010)),  # Lager 2
        ("p-hall", [(395, 875), (690, 875), (690, 1020), (557, 1020), (557, 1050), (830, 1050), (830, 1375),
                    (380, 1375), (380, 1050), (395, 1050)]),  # Treppenhaus
        ("p-guest", [(50, 1450), (555, 1450), (555, fac_in(555)), (50, fac_in(50))]),  # Gastraum 2
        ("p-guest", [(580, 1445), (830, 1445), (830, fac_in(830)), (580, fac_in(580))]),  # Gastraum 3
        ("p-hall", rect(480, 675, 605, 830)),  # Aufzugskabine
    ],
    openings=[
        ("p-hall", rect(70, 413, 160, 432)),  # WC Herren
        ("p-hall", rect(270, 313, 355, 332)),  # WC Damen
        ("p-hall", rect(358, 360, 377, 440)),  # WC Personal
        ("p-hall", rect(120, 528, 235, 597)),  # WC-Flur/Flur
        ("p-room", rect(253, 615, 272, 700)),  # Lager
        ("p-hall", rect(318, 1060, 382, 1130)),  # Tür zum Treppenhaus
        ("p-room", rect(725, 1008, 805, 1052)),  # Lager 2
        ("p-hall", rect(500, 828, 585, 877)),  # Aufzugstür
        ("p-guest", rect(210, 1393, 300, 1452)),  # Flur -> Gastraum 2
        ("p-guest", rect(553, 1730, 582, 1810)),  # Gastraum 2/3
    ],
    windows=[("front", 135, 260), ("front", 344, 448), ("front", 600, 705),
             ("back", 93, 186), ("back", 340, 432), ("back", 494, 586)],
    thin=[
        door((160, 430), (70, 430), (160, 510)),  # WC Herren
        door((355, 330), (270, 330), (355, 410)),  # WC Damen
        door((360, 440), (360, 360), (290, 440)),  # WC Personal (öffnet in den Flur)
        door((255, 700), (255, 615), (185, 700)),  # Lager
        door((380, 1130), (380, 1060), (445, 1130)),  # Treppenhaus
        door((555, 1810), (555, 1730), (475, 1810)),  # Gastraum 2/3
        treads(60, 200, 940, 1380, 18) + "M200 940V1380",  # Treppe aus dem EG
        treads(565, 695, 1205, 1370, 7) + treads(710, 825, 1150, 1370, 8) + "M702 1150V1370",  # Haustreppe
        cabin(480, 675, 605, 830),
    ],
    dashed=[],
    labels=[
        dict(t=["Gastraum 2"], x=300, y=1790, cls="p-name", sub="35 Plätze"),
        dict(t=["Gastraum 3"], x=705, y=1750, cls="p-name", along=True, sub="18 Plätze"),
        dict(t=["WC Damen"], x=440, y=205, cls="p-small"),
        dict(t=["WC", "Herren"], x=145, y=255, cls="p-small"),
        dict(t=["WC", "Personal"], x=497, y=400, cls="p-small", across=True),
        dict(t=["Flur"], x=150, y=712, cls="p-small"),
        dict(t=["Lager"], x=352, y=718, cls="p-small"),
        dict(t=["Lager"], x=770, y=942, cls="p-small", size=28),
        dict(t=["Aufzug"], x=542, y=752, cls="p-small", halo=True, size=30),
        dict(t=["Treppenhaus"], x=468, y=1212, cls="p-small", along=True),
        dict(t=["Treppe ins EG"], x=130, y=1160, cls="p-small", along=True, halo=True),
        dict(t=["Hof"], x=365, y=-110, cls="p-small p-out"),
    ],
    entrances=[],
)

SIZES = {"p-name": 46, "p-small": 36}
SUB_SIZE = 34
CHAR_W = {"p-name": 0.56, "p-small": 0.6}

def pts(poly): return " ".join(f"{x:g},{y:g}" for x, y in poly)

def window_shapes(side, x1, x2):
    if side == "front":
        quad = facade(x1, x2, -2)
        mid = lambda x: (fac_out(x) + fac_in(x)) / 2
        glass = f"M{x1:g} {mid(x1):g}L{x2:g} {mid(x2):g}"
    else:
        quad = rect(x1, -2, x2, 97)
        glass = f"M{x1} 47.5H{x2}"
    return quad, glass

def render(floor, wide):
    k = floor["key"] + ("-w" if wide else "-t")
    T = (lambda x, y: (-y, x)) if wide else (lambda x, y: (x, y))
    out = []
    # bounds from geometry, then labels outside
    allp = list(OUTLINE) + ANNEX
    xs, ys = zip(*[T(*p) for p in allp])
    pad = 30
    minx, maxx, miny, maxy = min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad
    # Room outside the façade for the street label (and entrances)
    street_gap = 260 if floor["entrances"] else 150
    if wide:
        minx -= street_gap + (190 if floor["entrances"] else 0)
    else:
        maxy += street_gap
    vb = f"{minx:g} {miny:g} {maxx - minx:g} {maxy - miny:g}"
    out.append(f'<svg class="plan-{"wide" if wide else "tall"}" viewBox="{vb}" role="img" aria-label="{floor["label"]}">')
    g = []
    if floor["annex"]:
        g.append(f'<pattern id="hof-{k}" width="24" height="24" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><path class="p-hatch" d="M0 0V24"/></pattern>')
        g.append(f'<polygon class="p-wall" points="{pts(ANNEX)}"/>')
        g.append(f'<polygon class="p-yard" points="{pts(HOF)}"/>')
        g.append(f'<polygon fill="url(#hof-{k})" points="{pts(HOF)}"/>')
    else:
        g.append(f'<polygon class="p-below" points="{pts(rect(35, -245, 695, 0))}"/>')
    g.append(f'<polygon class="p-wall" points="{pts(OUTLINE)}"/>')
    for cls, poly in floor["fills"]:
        g.append(f'<polygon class="{cls}" points="{pts(poly)}"/>')
    for cls, poly in floor["openings"]:
        g.append(f'<polygon class="{cls}" points="{pts(poly)}"/>')
    glass = []
    for side, x1, x2 in floor["windows"]:
        quad, gl = window_shapes(side, x1, x2)
        cls = "p-guest" if side == "front" else "p-room"
        g.append(f'<polygon class="{cls}" points="{pts(quad)}"/>')
        glass.append(gl)
    g.append(f'<path class="p-thin" d="{"".join(floor["thin"])}"/>')
    g.append(f'<path class="p-glass" d="{"".join(glass)}"/>')
    if floor["dashed"]:
        g.append(f'<path class="p-dash" d="{"".join(floor["dashed"])}"/>')
    # entrance arrows (geometry space)
    for x, _ in floor["entrances"]:
        y0 = fac_out(x)
        g.append(f'<path class="p-arrow" d="M{x:g} {y0 + 95:g}V{y0 + 22:g}"/>')
        g.append(f'<path class="p-arrowhead" d="M{x - 16:g} {y0 + 44:g}L{x:g} {y0 + 14:g}L{x + 16:g} {y0 + 44:g}Z"/>')
    if wide:
        out.append('<g transform="rotate(90)">' + "".join(g) + "</g>")
    else:
        out.append("".join(g))
    # labels
    for lab in floor["labels"]:
        size = lab.get("size", SIZES[lab["cls"].split()[0]])
        lh = size * 1.08
        lx, ly = T(lab["x"], lab["y"])
        rot = -90 if (lab.get("along") and not wide) or (lab.get("across") and wide) else 0
        n = len(lab["t"])
        cls = lab["cls"] + (" p-halo" if lab.get("halo") else "")
        tf = f' transform="rotate({rot} {lx:g} {ly:g})"' if rot else ""
        # optional muted second line (seat count) below the name, block centred on (x, y)
        sub = lab.get("sub")
        shift = -(SUB_SIZE * 1.25) / 2 if sub else 0
        spans = []
        for i, line in enumerate(lab["t"]):
            by = ly + shift + (i - (n - 1) / 2) * lh + 0.35 * size
            spans.append(f'<tspan x="{lx:g}" y="{by:g}">{line}</tspan>')
        if sub:
            by = ly + shift + (n - 1) / 2 * lh + 0.35 * size + SUB_SIZE * 1.25
            spans.append(f'<tspan class="p-sub" font-size="{SUB_SIZE}" x="{lx:g}" y="{by:g}">{sub}</tspan>')
        out.append(f'<text class="{cls}" font-size="{size}" text-anchor="middle"{tf}>{"".join(spans)}</text>')
    # entrance labels
    for x, name in floor["entrances"]:
        y0 = fac_out(x)
        if wide:
            lx, ly = T(x, y0 + 112)
            out.append(f'<text class="p-small p-door" font-size="34" text-anchor="end" x="{lx:g}" y="{ly + 12:g}">{name}</text>')
        else:
            out.append(f'<text class="p-small p-door" font-size="34" text-anchor="middle" x="{x:g}" y="{y0 + 140:g}">{name}</text>')
    # street label along the façade
    sx = 437.5
    off = (street_gap - 45) if floor["entrances"] else 90
    sy = fac_out(sx) + off
    ang = math.degrees(math.atan2(fac_out(875) - fac_out(0), 875))
    if wide:
        lx, ly = T(sx, sy + (190 if floor["entrances"] else 0))
        out.append(f'<text class="p-street" font-size="40" text-anchor="middle" transform="rotate({ang - 90:.2f} {lx:g} {ly:g})" x="{lx:g}" y="{ly + 14:g}">Neißstraße</text>')
    else:
        out.append(f'<text class="p-street" font-size="40" text-anchor="middle" transform="rotate({ang:.2f} {sx:g} {sy:g})" x="{sx:g}" y="{sy + 14:g}">Neißstraße</text>')
    out.append("</svg>")
    return "".join(out)

def build():
    return {f["key"]: render(f, True) + "\n" + render(f, False) for f in (EG, OG)}

if __name__ == "__main__":
    target = sys.argv[1]
    src = open(target, encoding="utf-8").read()
    for key, svg in build().items():
        pat = re.compile(rf"(<!--plan:{key}-->)(.*?)(<!--/plan:{key}-->)", re.S)
        if not pat.search(src):
            sys.exit(f"marker plan:{key} missing")
        src = pat.sub(lambda m: m.group(1) + "\n" + svg + "\n" + m.group(3), src)
    open(target, "w", encoding="utf-8").write(src)
    print("ok", {k: len(v) for k, v in build().items()})
