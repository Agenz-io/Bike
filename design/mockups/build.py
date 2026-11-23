"""Génère les 2 maquettes de hero (directions A et B) — dessin de vélo provisoire."""
import math, pathlib

HERE = pathlib.Path(__file__).parent

# --- géométrie (mm, y vers le bas, origine = axe roue arrière) ---
BB = (403, 72)
RA = (0, 0)
FA = (984, 0)
ST_TOP = (255, -427)
HT_TOP = (788, -488)
HT_BOT = (832, -345)
SADDLE = (199, -618)


def wheel(cx, cy):
    s = [f'<circle cx="{cx}" cy="{cy}" r="334" class="ln w2"/>',
         f'<circle cx="{cx}" cy="{cy}" r="314" class="ln"/>',
         f'<circle cx="{cx}" cy="{cy}" r="300" class="ln"/>',
         f'<circle cx="{cx}" cy="{cy}" r="282" class="ln thin"/>',
         f'<circle cx="{cx}" cy="{cy}" r="24" class="ln"/>',
         f'<circle cx="{cx}" cy="{cy}" r="8" class="ln"/>']
    for i in range(24):
        a = math.radians(i * 15)
        off = math.radians(9 if i % 2 else -9)
        x1, y1 = cx + 20 * math.cos(a + off), cy + 20 * math.sin(a + off)
        x2, y2 = cx + 282 * math.cos(a), cy + 282 * math.sin(a)
        s.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" class="ln hair"/>')
    return "\n".join(s)


def tube(p1, p2, w):
    return (f'<line x1="{p1[0]}" y1="{p1[1]}" x2="{p2[0]}" y2="{p2[1]}" class="tube-o" stroke-width="{w + 5}"/>'
            f'<line x1="{p1[0]}" y1="{p1[1]}" x2="{p2[0]}" y2="{p2[1]}" class="tube-i" stroke-width="{w - 1}"/>')


def bike():
    out = []
    out.append(f'<g id="roue-ar">{wheel(*RA)}</g>')
    out.append(f'<g id="roue-av">{wheel(*FA)}'
               f'<circle cx="{FA[0]}" cy="{FA[1]}" r="80" class="ln hidden"/></g>')
    # transmission
    out.append('<g id="groupe">'
               f'<circle cx="{BB[0]}" cy="{BB[1]}" r="104" class="ln w2"/>'
               f'<circle cx="{BB[0]}" cy="{BB[1]}" r="94" class="ln thin"/>'
               f'<circle cx="{BB[0]}" cy="{BB[1]}" r="40" class="ln"/>'
               '<circle cx="0" cy="0" r="58" class="ln"/><circle cx="0" cy="0" r="46" class="ln thin"/><circle cx="0" cy="0" r="36" class="ln thin"/>'
               f'<line x1="{BB[0]}" y1="{BB[1]-104}" x2="0" y2="-58" class="ln"/>'
               f'<line x1="{BB[0]}" y1="{BB[1]+104}" x2="34" y2="166" class="ln"/>'
               '<path d="M14 40 L40 160" class="ln w2"/>'
               '<circle cx="18" cy="70" r="15" class="ln"/><circle cx="34" cy="150" r="15" class="ln"/>'
               f'<path d="M{BB[0]} {BB[1]} L{BB[0]+58} {BB[1]+162}" class="ln crank"/>'
               f'<rect x="{BB[0]+30}" y="{BB[1]+156}" width="60" height="16" rx="3" class="ln fill"/>'
               '</g>')
    # cadre
    out.append('<g id="cadre">'
               + tube(BB, RA, 16) + tube((262, -400), RA, 14)
               + tube((826, -362), BB, 40) + tube((790, -468), (258, -412), 30)
               + tube(BB, ST_TOP, 30) + tube(HT_TOP, HT_BOT, 44)
               + f'<circle cx="{BB[0]}" cy="{BB[1]}" r="30" class="ln fill"/>'
               + '<circle cx="0" cy="0" r="12" class="ln fill"/>'
               '</g>')
    out.append('<g id="fourche">'
               f'<path d="M{HT_BOT[0]} {HT_BOT[1]} L852 -282" class="tube-o" stroke-width="42"/>'
               f'<path d="M{HT_BOT[0]} {HT_BOT[1]} L852 -282" class="tube-i" stroke-width="36"/>'
               '<path d="M852 -282 C 885 -170 920 -70 984 0" class="tube-o" stroke-width="24" fill="none"/>'
               '<path d="M852 -282 C 885 -170 920 -70 984 0" class="tube-i" stroke-width="18" fill="none"/>'
               '</g>')
    out.append('<g id="cockpit">'
               + tube(HT_TOP, (776, -530), 30)
               + '<path d="M770 -528 L884 -548" class="tube-o" stroke-width="30"/><path d="M770 -528 L884 -548" class="tube-i" stroke-width="24"/>'
               '<path d="M884 -548 L944 -552 C1012 -556 1018 -470 990 -432 C968 -402 934 -404 910 -410" class="ln bar"/>'
               '<path d="M930 -552 C940 -598 984 -600 994 -566 L986 -530" class="ln w2 fill"/>'
               '</g>')
    out.append('<g id="selle">'
               + tube(ST_TOP, SADDLE, 22)
               + '<path d="M110 -634 L300 -628 C312 -616 296 -604 270 -604 L160 -606 C130 -608 112 -618 110 -634Z" class="ln w2 fill"/>'
               '</g>')
    return "\n".join(out)


def dims():
    return ('<g class="dim">'
            '<line x1="0" y1="360" x2="0" y2="430"/><line x1="984" y1="360" x2="984" y2="430"/>'
            '<line x1="0" y1="410" x2="984" y2="410" marker-start="url(#ar)" marker-end="url(#ar)"/>'
            '<text x="492" y="398" text-anchor="middle">EMPATTEMENT 1 002</text>'
            '<path d="M760 -620 L788 -488" stroke-dasharray="6 6"/>'
            '<text x="700" y="-640">73,0°</text>'
            '<path d="M403 72 L170 -720" stroke-dasharray="6 6"/>'
            '<text x="48" y="-700">73,5°</text>'
            '</g>')


SVG = f'''<svg class="bike" viewBox="-380 -760 1740 1220" role="img" aria-label="Dessin technique d'un vélo de route sur mesure, vue de profil">
<defs><marker id="ar" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="10" markerHeight="10" orient="auto-start-reverse"><path d="M0 2 L10 5 L0 8" fill="none" stroke="currentColor" stroke-width="1.5"/></marker></defs>
{bike()}
{dims()}
</svg>'''

CSS = '''
@font-face{font-family:Archivo;src:url(fonts/Archivo.woff2) format("woff2");font-weight:100 900;font-stretch:62% 125%}
@font-face{font-family:Instrument;src:url(fonts/Instrument_Sans.woff2) format("woff2");font-weight:400 700;font-stretch:75% 100%}
@font-face{font-family:SofiaXC;src:url(fonts/Sofia_Sans_Extra_Condensed.woff2) format("woff2");font-weight:1 1000}
@font-face{font-family:SofiaSC;src:url(fonts/Sofia_Sans_Semi_Condensed.woff2) format("woff2");font-weight:1 1000}
*{box-sizing:border-box;margin:0;padding:0}
body{font-variant-numeric:tabular-nums}
.hero{position:relative;width:1440px;height:900px;overflow:hidden;background:var(--bg);color:var(--ink)}
.bike{color:var(--ink)}
.ln{fill:none;stroke:currentColor;stroke-width:2.2}
.ln.w2{stroke-width:3.4}.ln.thin{stroke-width:1.4}.ln.hair{stroke-width:.9;opacity:.8}
.ln.hidden{stroke-dasharray:8 7;stroke-width:1.6}
.ln.fill{fill:var(--bg)}.ln.crank{stroke-width:20;stroke-linecap:round}
.ln.bar{stroke-width:22;stroke-linecap:round}
.tube-o{stroke:currentColor;stroke-linecap:butt;fill:none}
.tube-i{stroke:var(--bg);stroke-linecap:butt;fill:none}
.dim line,.dim path{stroke:var(--dim);stroke-width:1.6;fill:none}
.dim text{fill:var(--dim);font:600 26px/1 var(--txt);font-stretch:82%;letter-spacing:.06em}

/* ---------- A ---------- */
.A{--bg:#FF5A1F;--ink:#121212;--dim:#121212;--disp:Archivo;--txt:Instrument;font-family:Instrument,sans-serif;font-stretch:82%}
.A .sheet{position:absolute;inset:20px;border:1.5px solid var(--ink)}
.A .sheet i{position:absolute;width:14px;height:14px;border-color:var(--ink);border-style:solid}
.A nav{position:absolute;top:20px;left:20px;right:20px;height:56px;display:grid;grid-template-columns:1fr auto 1fr;align-items:center;padding:0 24px;border-bottom:1.5px solid var(--ink);font-size:15px;font-weight:500}
.A nav .wm{font:800 22px/1 Archivo;font-stretch:62%;text-transform:uppercase;letter-spacing:.02em}
.A nav ul{display:flex;gap:28px;list-style:none}
.A nav .cta{justify-self:end;font-weight:600}
.A h1{position:absolute;left:64px;right:64px;top:108px;display:flex;justify-content:space-between;align-items:flex-end}
.A h1 .name{display:block;font:900 112px/.86 Archivo;font-stretch:62%;text-transform:uppercase;letter-spacing:-.01em}
.A h1 .line{display:block;font:500 26px/1.25 Instrument;font-stretch:82%;max-width:420px}
.A .bike{position:absolute;left:320px;top:232px;width:800px}
.A .cart{position:absolute;right:20px;bottom:20px;display:grid;grid-template-columns:repeat(4,auto);border-top:1.5px solid var(--ink);border-left:1.5px solid var(--ink);font-size:13px}
.A .cart div{padding:10px 18px;border-right:1.5px solid var(--ink)}
.A .cart div:last-child{border-right:0}
.A .cart b{display:block;font:800 20px/1.1 Archivo;font-stretch:62%;text-transform:uppercase;margin-top:4px}
.A .btn{position:absolute;left:64px;bottom:64px;background:var(--ink);color:var(--bg);padding:20px 28px;font:600 17px/1 Instrument;font-stretch:82%;display:flex;gap:40px}
.A .btn span:last-child{font-variant-numeric:tabular-nums}

/* ---------- B ---------- */
.B{--bg:#0F4A35;--ink:#ECEFEA;--dim:#F2D20A;--y:#F2D20A;--txt:SofiaSC;font-family:SofiaSC,sans-serif}
.B nav{position:absolute;top:0;left:0;right:0;height:84px;display:flex;align-items:center;justify-content:space-between;padding:0 48px;font-size:17px;font-weight:500}
.B nav ul{display:flex;gap:32px;list-style:none}
.B nav .wm{font:800 24px/1 SofiaXC;text-transform:uppercase;letter-spacing:.04em}
.B nav .cta{background:var(--y);color:#0D1117;padding:14px 20px;font-weight:700}
.B .lede{position:absolute;left:48px;top:150px;width:360px;font:500 24px/1.3 SofiaSC}
.B .lede small{display:block;font-size:14px;letter-spacing:.12em;text-transform:uppercase;color:var(--y);margin-bottom:14px;font-weight:700}
.B .meta{position:absolute;right:48px;top:150px;text-align:right;font:500 15px/1.6 SofiaSC;opacity:.85}
.B .bike{position:absolute;left:300px;top:96px;width:840px}
.B h1 .name{position:absolute;left:0;right:0;bottom:-14px;text-align:center;font:850 262px/.8 SofiaXC;text-transform:uppercase;color:var(--y);letter-spacing:-.005em;white-space:nowrap}
.B h1 .line{position:absolute;left:-9999px}

/* ---------- planche palette ---------- */
.board{width:1440px;padding:56px 64px 64px;background:#fff;color:#121212;font-family:Instrument,sans-serif;font-stretch:85%}
.board h2{font:900 44px/1 Archivo;font-stretch:62%;text-transform:uppercase;margin-bottom:8px}
.board p.sub{font-size:17px;max-width:900px;margin-bottom:32px;line-height:1.45}
.grid{display:grid;grid-template-columns:repeat(12,1fr);gap:12px}
.sw{height:150px;padding:14px;display:flex;flex-direction:column;justify-content:space-between;font-size:14px;font-weight:600}
.spec{grid-column:span 6;border:1.5px solid #121212;padding:22px;min-height:230px}
.spec .k{font-size:12px;letter-spacing:.1em;text-transform:uppercase;font-weight:600;margin-bottom:12px}
.seq{grid-column:span 12;display:flex;height:64px;margin-top:4px}
.seq div{flex:1;display:flex;align-items:end;padding:8px 10px;font-size:12px;font-weight:600}
.refs{grid-column:span 12;display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:4px}
.refs div{border-top:1.5px solid #121212;padding-top:10px;font-size:15px;line-height:1.4}
.refs b{display:block;font-size:16px;margin-bottom:4px}
'''

HERO_A = f'''<section class="hero A" id="heroA">
<div class="sheet"></div>
<nav><span class="wm">Garnier Cycles</span><ul><li>Atelier</li><li>Procédé</li><li>Modèles</li><li>Tarifs</li><li>FAQ</li></ul><span class="cta">[ Réserver l’étude posturale ]</span></nav>
<h1><span class="name">Garnier Cycles</span><span class="line">Vélos sur mesure en acier et titane, construits pour un seul cycliste. Annecy, depuis 2015.</span></h1>
{SVG}
<a class="btn"><span>Réserver l’étude posturale</span><span>180 €</span></a>
<div class="cart"><div>Planche<b>00 / 11</b></div><div>Vue<b>Élévation côté transmission</b></div><div>Échelle<b>1:10</b></div><div>Dessiné pour<b>Un seul cycliste</b></div></div>
</section>'''

HERO_B = f'''<section class="hero B" id="heroB">
<nav><span class="wm">Garnier Cycles</span><ul><li>Atelier</li><li>Procédé</li><li>Modèles</li><li>Tarifs</li><li>FAQ</li></ul><span class="cta">Étude posturale · 180 €</span></nav>
<p class="lede"><small>Artisan cadreur · Annecy</small>Un vélo sur mesure, construit pour un seul cycliste. Acier ou titane, soudé à la main.</p>
<p class="meta">40 cadres par an<br>Nom du propriétaire gravé<br>sous le boîtier de pédalier</p>
{SVG}
<h1><span class="name">Garnier Cycles</span><span class="line">vélos sur mesure construits pour un seul cycliste</span></h1>
</section>'''


def board(title, sub, swatches, specs, seq, refs):
    sw = "".join(f'<div class="sw" style="grid-column:span {s[3]};background:{s[0]};color:{s[2]}"><span>{s[1]}</span><span>{s[0].upper()}</span></div>' for s in swatches)
    sp = "".join(f'<div class="spec"><div class="k">{k}</div>{v}</div>' for k, v in specs)
    sq = "".join(f'<div style="background:{c};color:{t}">{n}</div>' for c, t, n in seq)
    rf = "".join(f'<div><b>{a}</b>{b}</div>' for a, b in refs)
    return f'<section class="board"><h2>{title}</h2><p class="sub">{sub}</p><div class="grid">{sw}{sp}<div class="seq">{sq}</div><div class="refs">{rf}</div></div></section>'


BOARD_A = board(
    "Direction A — Planche d’atelier",
    "Le site est un jeu de planches techniques numérotées (00 à 11). Cadre de feuille, cartouche, cotes, étiquettes entre crochets. Orange signal en ouverture, puis noir et vert usine en alternance. Le vélo est dessiné au trait noir comme sur un plan.",
    [("#FF5A1F", "Orange signal — hero, CTA", "#121212", 4), ("#121212", "Noir carbone", "#F4F5F2", 3), ("#1E5B45", "Vert usine", "#F4F5F2", 3), ("#F4F5F2", "Blanc froid — texte sur sombre", "#121212", 2)],
    [("Titres — Archivo ExtraCondensed 900 (wdth 62)", '<div style="font:900 96px/.9 Archivo;font-stretch:62%;text-transform:uppercase">Cadre titane<br>3Al-2,5V</div>'),
     ("Texte & cotes — Instrument Sans Condensed (wdth 82)", '<div style="font:500 20px/1.45 Instrument;font-stretch:82%;max-width:520px">Tubes Columbus et Reynolds choisis selon votre poids et votre pratique. Chiffres tabulaires pour les cotes :</div><div style="font:600 44px/1.1 Instrument;font-stretch:82%;margin-top:14px;font-variant-numeric:tabular-nums">73,5° · 1 002 mm · 1 640 g</div>')],
    [("#FF5A1F", "#121212", "00 Hero"), ("#121212", "#F4F5F2", "01 Vue éclatée"), ("#1E5B45", "#F4F5F2", "02 Atelier"), ("#FF5A1F", "#121212", "03 Procédé"), ("#121212", "#F4F5F2", "04 Acier/Titane"), ("#1E5B45", "#F4F5F2", "05 Modèles"), ("#121212", "#F4F5F2", "06 Options"), ("#FF5A1F", "#121212", "07 Fiche client"), ("#1E5B45", "#F4F5F2", "08 Avis"), ("#121212", "#F4F5F2", "09 Étude"), ("#FF5A1F", "#121212", "10 FAQ")],
    [("hardwareoperations.com", "La pièce mécanique isolée comme un objet de galerie : masse contre vide, aucun décor."),
     ("eduardbodak.com", "Titre ultra-condensé en capitales, repères de coin type coordonnées, grille bento calme."),
     ("turnoev.com", "Libellés entre crochets [ ], orange industriel brûlé sur noir, vue fil de fer.")])

BOARD_B = board(
    "Direction B — Vert usine",
    "Le site est un bâtiment d’atelier : grands aplats francs, nom monumental posé comme une enseigne au sol, vélo au trait blanc, cotes en jaune sécurité. Les sections alternent vert, jaune, noir bleuté et rouge minium.",
    [("#0F4A35", "Vert usine — hero", "#ECEFEA", 3), ("#F2D20A", "Jaune sécurité — cotes, CTA", "#0D1117", 3), ("#0D1117", "Noir bleuté", "#ECEFEA", 3), ("#D2381C", "Rouge minium", "#ECEFEA", 3)],
    [("Titres — Sofia Sans Extra Condensed 850", '<div style="font:850 104px/.85 SofiaXC;text-transform:uppercase">Cadre titane<br>3Al-2,5V</div>'),
     ("Texte & cotes — Sofia Sans Semi Condensed", '<div style="font:500 20px/1.45 SofiaSC;max-width:520px">Tubes Columbus et Reynolds choisis selon votre poids et votre pratique. Chiffres tabulaires pour les cotes :</div><div style="font:700 44px/1.1 SofiaSC;margin-top:14px;font-variant-numeric:tabular-nums">73,5° · 1 002 mm · 1 640 g</div>')],
    [("#0F4A35", "#ECEFEA", "00 Hero"), ("#0D1117", "#ECEFEA", "01 Vue éclatée"), ("#F2D20A", "#0D1117", "02 Atelier"), ("#0F4A35", "#ECEFEA", "03 Procédé"), ("#D2381C", "#ECEFEA", "04 Acier/Titane"), ("#0D1117", "#ECEFEA", "05 Modèles"), ("#F2D20A", "#0D1117", "06 Options"), ("#0F4A35", "#ECEFEA", "07 Fiche client"), ("#D2381C", "#ECEFEA", "08 Avis"), ("#F2D20A", "#0D1117", "09 Étude"), ("#0D1117", "#ECEFEA", "10 FAQ")],
    [("savvycal.com", "Aplat vert profond pleine page, titre en couleur acide : la couleur porte tout, sans photo."),
     ("frerejones.com", "Bento de spécimens : panneaux de couleurs franches juxtaposés, chacun avec une seule idée."),
     ("hardwareoperations.com", "Composant technique isolé, cadré avec beaucoup de vide autour.")])

html = f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Directions</title><style>{CSS}</style></head><body>{HERO_A}{BOARD_A}{HERO_B}{BOARD_B}</body></html>'
(HERE / "directions.html").write_text(html, encoding="utf-8")
print("ok")
