"""Génère le dessin technique du vélo (SVG) — Garnier Cycles, site de démonstration.

Unités : millimètres réels (1 unité = 1 mm), y vers le bas, origine = axe de roue arrière.
Chaque pièce de la vue éclatée est un <g data-part="..."> séparé :
  cadre · fourche · roue-ar · roue-av · groupe · cockpit · selle   (+ cotes, non éclaté)
Sortie : src/partials/bike.svg
"""
import math, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "src" / "partials" / "bike.svg"

# ---------------------------------------------------------------- géométrie
SA, HA = 73.5, 73.0                     # angles de selle / direction
BB = (404.0, 70.0)                      # boîtier (bases 410, drop 70)
RA = (0.0, 0.0)
st_u = (-math.cos(math.radians(SA)), -math.sin(math.radians(SA)))   # BB -> haut du tube de selle
ht_u = (math.cos(math.radians(HA)), math.sin(math.radians(HA)))     # axe de direction, vers le bas
ht_n = (ht_u[1], -ht_u[0])                                          # perpendiculaire, vers l'avant


def add(p, v, k=1.0):
    return (p[0] + v[0] * k, p[1] + v[1] * k)


def along_st(l):
    return add(BB, st_u, l)


HT_TOP = (BB[0] + 390, BB[1] - 565)     # reach 390 / stack 565
HT_BOT = add(HT_TOP, ht_u, 160)
CROWN = add(HT_BOT, ht_u, 12)
_t = (-CROWN[1] - (-ht_n[1]) * 45) / ht_u[1]
FA = (CROWN[0] + ht_u[0] * _t + ht_n[0] * 45, 0.0)                  # axe roue avant
ST_TOP = along_st(560)
SADDLE = along_st(742)
STEM_C = add(HT_TOP, ht_u, -46)
WHEELBASE = round(FA[0])


def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def pts(*ps):
    return " ".join(f"{f(x)},{f(y)}" for x, y in ps)


def quad(p1, p2, w1, w2=None):
    w2 = w1 if w2 is None else w2
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    L = math.hypot(dx, dy)
    nx, ny = -dy / L, dx / L
    return [(p1[0] + nx * w1 / 2, p1[1] + ny * w1 / 2), (p2[0] + nx * w2 / 2, p2[1] + ny * w2 / 2),
            (p2[0] - nx * w2 / 2, p2[1] - ny * w2 / 2), (p1[0] - nx * w1 / 2, p1[1] - ny * w1 / 2)]


def tube(p1, p2, w1, w2=None, cls="ln fl"):
    return f'<polygon points="{pts(*quad(p1, p2, w1, w2))}" class="{cls}"/>'


def line(a, b, cls="ln"):
    return f'<line x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}" class="{cls}"/>'


def circ(c, r, cls="ln"):
    return f'<circle cx="{f(c[0])}" cy="{f(c[1])}" r="{f(r)}" class="{cls}"/>'


def inter(a1, a2, b1, b2):
    """intersection des droites (a1,a2) et (b1,b2)"""
    x1, y1 = a1; x2, y2 = a2; x3, y3 = b1; x4, y4 = b2
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(d) < 1e-9:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


def bead(sec_a, sec_b, sec_w, main_a, main_b, main_w):
    """cordon de soudure TIG : ondulations le long de la jonction tube secondaire / tube principal"""
    q = quad(sec_a, sec_b, sec_w)
    m = quad(main_a, main_b, main_w)
    # côté du tube principal qui fait face au tube secondaire (celui le plus proche de sec_b)
    sides = [(m[0], m[1]), (m[3], m[2])]
    side = min(sides, key=lambda s: abs((s[1][0] - s[0][0]) * (sec_b[1] - s[0][1]) - (s[1][1] - s[0][1]) * (sec_b[0] - s[0][0])) / math.hypot(s[1][0] - s[0][0], s[1][1] - s[0][1]))
    p = inter(q[0], q[1], *side)
    r = inter(q[3], q[2], *side)
    if not p or not r:
        return ""
    n = 7
    d = "M" + pts(p)
    for i in range(1, n + 1):
        a = (p[0] + (r[0] - p[0]) * (i - .5) / n, p[1] + (r[1] - p[1]) * (i - .5) / n)
        b = (p[0] + (r[0] - p[0]) * i / n, p[1] + (r[1] - p[1]) * i / n)
        # léger renflement vers le tube secondaire
        vx, vy = sec_b[0] - sec_a[0], sec_b[1] - sec_a[1]
        L = math.hypot(vx, vy)
        o = 5 if math.hypot(sec_a[0] - a[0], sec_a[1] - a[1]) < math.hypot(sec_b[0] - a[0], sec_b[1] - a[1]) else -5
        c = (a[0] + vx / L * o, a[1] + vy / L * o)
        d += f" Q{pts(c)} {pts(b)}"
    return f'<path d="{d}" class="ln weld"/>'


# ---------------------------------------------------------------- pièces
def cadre():
    tt_a, tt_b = add(HT_TOP, ht_u, 24), along_st(520)
    dt_a = add(HT_BOT, ht_u, -22)
    ss_a = along_st(500)
    o = ['<g data-part="cadre" id="p-cadre">']
    # axes (traits mixtes)
    o.append('<g class="cl">' + line(BB, ST_TOP, "") + line(tt_a, tt_b, "") + line(dt_a, BB, "") +
             line(add(HT_TOP, ht_u, -30), add(HT_BOT, ht_u, 30), "") + line(BB, RA, "") + line(ss_a, RA, "") + "</g>")
    # haubans + bases (secondaires)
    o.append(tube(ss_a, add(RA, (14, -26)), 16, 12))
    o.append(tube(BB, add(RA, (22, -4)), 24, 14))
    # tube horizontal + oblique
    o.append(tube(tt_b, tt_a, 32))
    o.append(tube(BB, dt_a, 44.5))
    # patte arrière
    o.append(f'<path d="M-18 -22 L22 -34 L40 -10 L32 16 L-2 20 L-20 6 Z" class="ln fl"/>')
    o.append(circ(RA, 13, "ln fl") + circ(RA, 6))
    # tube de selle + douille de direction (principaux)
    o.append(tube(BB, ST_TOP, 32))
    o.append(tube(add(HT_TOP, ht_u, -2), add(HT_BOT, ht_u, 2), 48))
    o.append(tube(add(HT_TOP, ht_u, -8), add(HT_TOP, ht_u, 6), 54))       # cuvette haute
    o.append(tube(add(HT_BOT, ht_u, -6), add(HT_BOT, ht_u, 8), 54))       # cuvette basse
    o.append(tube(add(ST_TOP, st_u, -26), ST_TOP, 38))                     # collier
    # boîte de pédalier T47
    o.append(circ(BB, 27, "ln fl") + circ(BB, 21, "ln thin"))
    # cordons de soudure
    o.append(bead(tt_a, tt_b, 32, BB, ST_TOP, 32))
    o.append(bead(tt_b, tt_a, 32, HT_TOP, HT_BOT, 48))
    o.append(bead(BB, dt_a, 44.5, HT_TOP, HT_BOT, 48))
    o.append(bead(RA, ss_a, 16, BB, ST_TOP, 32))
    # renfort de dérailleur avant (patte brasée) + passage de gaine
    fd = along_st(150)
    o.append(tube(add(fd, (st_u[1], -st_u[0]), -14), add(fd, (st_u[1], -st_u[0]), -30), 34, 26))
    o.append(circ(add(dt_a, (-52, 66)), 4))
    # gravure sous le boîtier (texte trop petit à cette échelle : simple repère)
    o.append(f'<path d="M{f(BB[0]-14)} {f(BB[1]+34)} h28" class="ln thin"/>')
    o.append("</g>")
    return "\n".join(o)


def fourche():
    tip = FA
    o = ['<g data-part="fourche" id="p-fourche">']
    # pivot (caché dans la douille : traits interrompus) + au-dessus de la douille
    o.append(tube(STEM_C, add(HT_TOP, ht_u, -8), 28.6, 28.6))
    o.append(tube(add(HT_TOP, ht_u, -8), HT_BOT, 28.6, 38))
    # tê de fourche + fourreau (courbe)
    c1 = add(CROWN, ht_u, 22)
    o.append(f'<path d="M{pts(add(CROWN, ht_n, -24))} L{pts(add(CROWN, ht_n, 26))} '
             f'L{pts(add(c1, ht_n, 24))} C{pts(add(add(c1, ht_u, 150), ht_n, 30))} {pts(add(tip, (-6, -70)))} {pts(add(tip, (14, -14)))} '
             f'L{pts(add(tip, (-12, 10)))} C{pts(add(tip, (-40, -40)))} {pts(add(add(c1, ht_u, 150), ht_n, -6))} {pts(add(c1, ht_n, -22))} Z" class="ln fl"/>')
    o.append(f'<path d="M{pts(add(c1, ht_n, 1))} C{pts(add(add(c1, ht_u, 150), ht_n, 12))} {pts(add(tip, (-24, -60)))} {pts(add(tip, (0, -2)))}" class="cl"/>')
    o.append(circ(tip, 13, "ln fl") + circ(tip, 6))
    # étrier de frein (côté gauche, caché)
    o.append(f'<path d="M{pts(add(tip, (-58, -78)))} l40 -22 l26 44 l-40 22 Z" class="ln hd"/>')
    o.append("</g>")
    return "\n".join(o)


def wheel(part, c, rear=False):
    o = [f'<g data-part="{part}" id="p-{part}">']
    o.append(circ(c, 339, "ln w2") + circ(c, 314) + circ(c, 309, "ln thin") + circ(c, 274))
    # rayons : 24, croisés
    for i in range(24):
        a = math.radians(i * 15)
        b = a + math.radians(52 if i % 2 else -52)
        p1 = (c[0] + 26 * math.cos(b), c[1] + 26 * math.sin(b))
        p2 = (c[0] + 274 * math.cos(a), c[1] + 274 * math.sin(a))
        o.append(line(p1, p2, "ln hair"))
    # valve
    o.append(f'<rect x="{f(c[0]-3.5)}" y="{f(c[1]-274-34)}" width="7" height="34" class="ln fl"/>')
    # moyeu + disque (côté gauche, caché)
    o.append(circ(c, 80, "ln hd") + circ(c, 68, "ln hd"))
    o.append(circ(c, 30, "ln fl") + circ(c, 18, "ln thin") + circ(c, 9))
    o.append("</g>")
    return "\n".join(o)


def chain_run(a, b, cls="ln chain"):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    nx, ny = -dy / L * 4, dx / L * 4
    s = line((a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), cls) + line((a[0] - nx, a[1] - ny), (b[0] - nx, b[1] - ny), cls)
    k = int(L // 12.7)
    for i in range(1, k):
        p = (a[0] + dx * i / k, a[1] + dy * i / k)
        s += f'<circle cx="{f(p[0])}" cy="{f(p[1])}" r="1.6" class="ln pin"/>'
    return s


def tangent_top(c1, r1, c2, r2, side=-1):
    """tangente extérieure entre deux cercles (side=-1 : brin du dessus, +1 : brin du dessous)"""
    dx, dy = c2[0] - c1[0], c2[1] - c1[1]
    d = math.hypot(dx, dy)
    ang = math.atan2(dy, dx)
    beta = math.acos((r1 - r2) / d)
    cands = []
    for t in (ang - beta, ang + beta):
        cands.append(((c1[0] + r1 * math.cos(t), c1[1] + r1 * math.sin(t)), (c2[0] + r2 * math.cos(t), c2[1] + r2 * math.sin(t))))
    cands.sort(key=lambda ab: ab[0][1] + ab[1][1])
    return cands[0] if side < 0 else cands[1]


def groupe():
    o = ['<g data-part="groupe" id="p-groupe">']
    RING, COG = 101, 34
    PU, PL = (26, 58), (44, 136)                       # galets haut / bas du dérailleur
    # chaîne : brin tendu (plateau -> pignon) + brin mou (plateau -> galet bas)
    a, b = tangent_top(BB, RING, RA, COG, -1)
    o.append(chain_run(b, a))
    a2, b2 = tangent_top(BB, RING, PL, 13, +1)
    o.append(chain_run(a2, b2))
    a3, b3 = tangent_top(RA, COG, PU, 13, +1)
    o.append(chain_run(a3, b3, "ln chain thin"))
    # cassette 11-34 (12 pignons)
    for r in (64, 58, 52, 47, 42, 37, 33, 29, 26, 23):
        o.append(circ(RA, r, "ln thin" if r < 64 else "ln"))
    # dérailleur arrière
    o.append(f'<path d="M30 -20 L78 6 L74 34 L44 44 L34 30 Z" class="ln fl"/>')
    o.append(f'<path d="M{pts((PU[0]-14, PU[1]-12))} L{pts((PL[0]-16, PL[1]+10))} L{pts((PL[0]+14, PL[1]+16))} L{pts((PU[0]+16, PU[1]-4))} Z" class="ln fl"/>')
    o.append(circ(PU, 13, "ln fl") + circ(PU, 4) + circ(PL, 13, "ln fl") + circ(PL, 4))
    # plateaux 50/34 + étoile
    o.append(circ(BB, RING + 3, "ln w2 fl") + circ(BB, RING - 5, "ln thin") + circ(BB, 72, "ln") + circ(BB, 66, "ln thin"))
    for i in range(4):
        a = math.radians(45 + i * 90)
        o.append(line((BB[0] + 30 * math.cos(a), BB[1] + 30 * math.sin(a)), (BB[0] + 64 * math.cos(a), BB[1] + 64 * math.sin(a)), "ln w2"))
    # manivelle 172,5 mm + pédale
    ca = math.radians(72)
    pd = (BB[0] + 172.5 * math.cos(ca), BB[1] + 172.5 * math.sin(ca))
    o.append(tube(BB, pd, 40, 24))
    o.append(circ(BB, 22, "ln fl") + circ(BB, 8) + circ(pd, 8))
    o.append(f'<rect x="{f(pd[0]-48)}" y="{f(pd[1]-6)}" width="96" height="20" rx="4" class="ln fl"/>')
    # dérailleur avant (fourchette sur patte brasée)
    fd = along_st(150)
    n = (st_u[1], -st_u[0])
    p0 = add(fd, n, -34)
    o.append(f'<path d="M{pts(p0)} l-62 -2 c-8 0 -10 10 -4 16 l58 12 Z" class="ln fl"/>')
    o.append("</g>")
    return "\n".join(o)


def cockpit():
    o = ['<g data-part="cockpit" id="p-cockpit">']
    # entretoises + chapeau de jeu de direction
    for k in (-8, -18, -28):
        o.append(tube(add(HT_TOP, ht_u, k), add(HT_TOP, ht_u, k - 10), 36))
    o.append(tube(add(STEM_C, ht_u, 22), add(STEM_C, ht_u, -24), 42))
    o.append(tube(add(STEM_C, ht_u, -24), add(STEM_C, ht_u, -30), 34))
    # potence 110 mm (titane, soudée atelier)
    end = (STEM_C[0] + 110, STEM_C[1] - 4)
    o.append(tube(STEM_C, end, 34, 30))
    o.append(circ(end, 22, "ln fl") + circ(end, 15.9, "ln thin"))
    o.append(line(add(end, (0, -22)), add(end, (0, 22)), "ln thin"))
    # cintre (drop) : ruban + crochet
    bar = f"M{f(end[0])} {f(end[1])} L{f(end[0]+44)} {f(end[1]-2)} C{f(end[0]+102)} {f(end[1]-4)} {f(end[0]+114)} {f(end[1]+60)} {f(end[0]+104)} {f(end[1]+96)} C{f(end[0]+94)} {f(end[1]+128)} {f(end[0]+62)} {f(end[1]+132)} {f(end[0]+30)} {f(end[1]+126)}"
    o.append(f'<path d="{bar}" class="ln barO"/><path d="{bar}" class="ln barI"/>')
    # cocotte + levier
    hx, hy = end[0] + 60, end[1] - 4
    o.append(f'<path d="M{f(hx-8)} {f(hy+2)} C{f(hx-2)} {f(hy-22)} {f(hx+30)} {f(hy-34)} {f(hx+54)} {f(hy-36)} C{f(hx+66)} {f(hy-36)} {f(hx+68)} {f(hy-22)} {f(hx+62)} {f(hy-12)} C{f(hx+58)} {f(hy-4)} {f(hx+56)} {f(hy+6)} {f(hx+52)} {f(hy+12)} Z" class="ln fl"/>')
    o.append(f'<path d="M{f(hx+56)} {f(hy+8)} C{f(hx+72)} {f(hy+50)} {f(hx+66)} {f(hy+92)} {f(hx+50)} {f(hy+120)}" class="ln leverO"/>'
             f'<path d="M{f(hx+56)} {f(hy+8)} C{f(hx+72)} {f(hy+50)} {f(hx+66)} {f(hy+92)} {f(hx+50)} {f(hy+120)}" class="ln leverI"/>')
    o.append("</g>")
    return "\n".join(o)


def selle():
    o = ['<g data-part="selle" id="p-selle">']
    o.append(tube(add(ST_TOP, st_u, -40), SADDLE, 27.2))
    o.append(tube(add(BB, st_u, 470), add(ST_TOP, st_u, -40), 27.2))   # insertion (masquée par le cadre une fois monté)
    sx, sy = SADDLE
    o.append(f'<path d="M{f(sx-22)} {f(sy-6)} h44 v14 h-44 Z" class="ln fl"/>')                   # chariot
    o.append(f'<path d="M{f(sx-70)} {f(sy-8)} L{f(sx+80)} {f(sy-8)}" class="ln"/>')              # rails
    o.append(f'<path d="M{f(sx-110)} {f(sy-30)} C{f(sx-70)} {f(sy-40)} {f(sx+40)} {f(sy-30)} {f(sx+150)} {f(sy-26)} '
             f'C{f(sx+162)} {f(sy-24)} {f(sx+158)} {f(sy-12)} {f(sx+146)} {f(sy-12)} '
             f'L{f(sx+20)} {f(sy-12)} C{f(sx-60)} {f(sy-12)} {f(sx-100)} {f(sy-8)} {f(sx-116)} {f(sy-18)} '
             f'C{f(sx-122)} {f(sy-22)} {f(sx-118)} {f(sy-28)} {f(sx-110)} {f(sy-30)} Z" class="ln fl"/>')
    o.append("</g>")
    return "\n".join(o)


def cotes():
    y = 400
    o = ['<g class="cotes" id="cotes">']
    o.append(line((0, 360), (0, y + 18), "dim") + line((FA[0], 360), (FA[0], y + 18), "dim"))
    o.append(f'<line x1="0" y1="{y}" x2="{f(FA[0])}" y2="{y}" class="dim" marker-start="url(#arr)" marker-end="url(#arr)"/>')
    o.append(f'<text x="{f(FA[0]/2)}" y="{y-14}" text-anchor="middle" class="dimt">EMPATTEMENT {WHEELBASE} MM</text>')
    # angle de selle
    p = add(BB, st_u, 880)
    o.append(line(BB, p, "dim dash") + f'<text x="{f(p[0]-14)}" y="{f(p[1]-14)}" text-anchor="middle" class="dimt">73,5°</text>')
    # angle de direction
    q = add(HT_TOP, ht_u, -150)
    o.append(line(add(HT_BOT, ht_u, 60), q, "dim dash") + f'<text x="{f(q[0]+4)}" y="{f(q[1]-14)}" text-anchor="middle" class="dimt">73,0°</text>')
    o.append("</g>")
    return "\n".join(o)


DEFS = ('<defs><marker id="arr" viewBox="0 0 12 12" refX="6" refY="6" markerWidth="12" markerHeight="12" '
        'markerUnits="userSpaceOnUse" orient="auto-start-reverse"><path d="M0 2 L12 6 L0 10" class="dim"/></marker></defs>')

# ordre d'empilement : roues derrière, puis transmission, cadre, fourche, selle, cockpit
BODY = "\n".join([wheel("roue-ar", RA, True), wheel("roue-av", FA), fourche(), selle(), cadre(), groupe(), cockpit(), cotes()])

SVG = (f'<svg class="bike" viewBox="-380 -800 1760 1240" xmlns="http://www.w3.org/2000/svg" role="img" '
       f'aria-labelledby="bike-t"><title id="bike-t">Dessin technique d’un vélo de route sur mesure en titane, vue de profil côté transmission</title>'
       f'{DEFS}<g class="bike-root">{BODY}</g></svg>')

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(SVG, encoding="utf-8")
print(f"bike.svg : {len(SVG)//1024} ko · empattement {WHEELBASE} mm · axe AV x={FA[0]:.1f}")

# ---------------------------------------------------------------- nomenclature (HTML, lisible sans JS)
import json, html as _h
parts = json.loads((ROOT / "src/data/parts.json").read_text(encoding="utf-8"))
items = []
for p in sorted([p for p in parts if p.get("note") is not False], key=lambda p: p["num"]):
    items.append(
        f'<li class="note" data-note="{p["id"]}"{" data-align=\"right\"" if p.get("align") == "right" else ""}>'
        f'<span class="note-k">{p["num"]} · {_h.escape(p["weight"])}</span>'
        f'<span class="note-t">{_h.escape(p["name"])}</span>'
        f'<span class="note-v">{_h.escape(p["material"])}</span>'
        f'<span class="note-r">{_h.escape(p["role"])}</span></li>')
(ROOT / "src/partials/nomenclature.html").write_text(
    '<ol class="nomenclature" aria-label="Nomenclature du vélo">' + "".join(items) + "</ol>", encoding="utf-8")
print("nomenclature.html ok")
