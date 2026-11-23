"""Planche de validation du dessin : vélo assemblé + vue éclatée statique annotée."""
import pathlib, json

ROOT = pathlib.Path(__file__).resolve().parent.parent
svg = (ROOT / "src/partials/bike.svg").read_text(encoding="utf-8")
parts = json.loads((ROOT / "src/data/parts.json").read_text(encoding="utf-8"))

CSS = """
@font-face{font-family:SofiaXC;src:url(../public/fonts/Sofia_Sans_Extra_Condensed.woff2) format("woff2");font-weight:1 1000}
@font-face{font-family:SofiaSC;src:url(../public/fonts/Sofia_Sans_Semi_Condensed.woff2) format("woff2");font-weight:1 1000}
*{margin:0;box-sizing:border-box}
body{background:#0F4A35;color:#ECEFEA;font-family:SofiaSC;font-variant-numeric:tabular-nums}
.frame{width:1440px;height:900px;position:relative;overflow:hidden;background:#0F4A35}
.frame h2{position:absolute;left:48px;top:40px;font:800 15px/1 SofiaSC;letter-spacing:.14em;text-transform:uppercase;color:#F2D20A}
.bike{position:absolute;left:50%;top:52%;transform:translate(-50%,-50%);width:1040px;color:#ECEFEA;overflow:visible}
.ex .bike{width:1000px;top:54%}
.ln{fill:none;stroke:currentColor;stroke-width:2.4;stroke-linejoin:round}
.ln.fl{fill:#0F4A35}
.ln.w2{stroke-width:3.6}.ln.thin{stroke-width:1.5}.ln.hair{stroke-width:1;opacity:.75}
.ln.hd{stroke-dasharray:9 7;stroke-width:1.6;fill:none}
.cl{fill:none;stroke:currentColor;stroke-width:1;stroke-dasharray:28 6 4 6;opacity:.45}
.cl .cl,.cl line{stroke:currentColor}
.ln.weld{stroke-width:1.4}
.ln.chain{stroke-width:1.4}.ln.pin{stroke-width:1;fill:currentColor}
.ln.barO{stroke-width:27;stroke-linecap:round}.ln.barI{stroke-width:21;stroke:#0F4A35;stroke-linecap:round}
.ln.leverO{stroke-width:13;stroke-linecap:round}.ln.leverI{stroke-width:8;stroke:#0F4A35;stroke-linecap:round}
.dim{fill:none;stroke:#F2D20A;stroke-width:1.8}.dim.dash{stroke-dasharray:10 8}
.dimt{fill:#F2D20A;font:700 30px/1 SofiaSC;letter-spacing:.06em}
.note{color:#F2D20A}
.note line{stroke:#F2D20A;stroke-width:1.6}
.note circle{fill:#F2D20A}
.note .t{fill:#ECEFEA;font:800 84px/1 SofiaXC;text-transform:uppercase;letter-spacing:.01em}
.note .k{fill:#F2D20A;font:700 30px/1 SofiaSC;letter-spacing:.12em;text-transform:uppercase}
.note .v{fill:#ECEFEA;font:500 36px/1 SofiaSC}
"""


def exploded(svg):
    s = svg.replace('viewBox="-380 -800 1760 1240"', 'viewBox="-860 -1220 2720 2000"')
    for p in parts:
        dx, dy = p["offset"]
        s = s.replace(f'<g data-part="{p["id"]}"', f'<g transform="translate({dx} {dy})" data-part="{p["id"]}"', 1)
    s = s.replace('<g class="cotes"', '<g style="display:none" class="cotes"')
    notes = []
    for p in parts:
        if p.get("note") is False:
            continue
        dx, dy = p["offset"]
        ax, ay = p["anchor"][0] + dx, p["anchor"][1] + dy
        lx, ly = p["label"]
        anchor = "end" if p.get("align") == "right" else "start"
        notes.append(f'<g class="note"><circle cx="{ax}" cy="{ay}" r="6"/><line x1="{ax}" y1="{ay}" x2="{lx}" y2="{ly+8}"/>'
                     f'<line x1="{lx}" y1="{ly+8}" x2="{lx + (-420 if anchor=="end" else 420)}" y2="{ly+8}"/>'
                     f'<text class="k" x="{lx}" y="{ly-96}" text-anchor="{anchor}">{p["num"]} · {p["weight"]}</text>'
                     f'<text class="t" x="{lx}" y="{ly-10}" text-anchor="{anchor}">{p["name"]}</text>'
                     f'<text class="v" x="{lx}" y="{ly+54}" text-anchor="{anchor}">{p["material"]}</text>'
                     f'<text class="v" x="{lx}" y="{ly+100}" text-anchor="{anchor}" opacity=".75">{p["role"]}</text></g>')
    return s.replace("</svg>", "".join(notes) + "</svg>")


html = (f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>{CSS}</style></head><body>'
        f'<section class="frame" id="assemble"><h2>Planche 00 · Élévation, côté transmission</h2>{svg}</section>'
        f'<section class="frame ex" id="eclate"><h2>Planche 01 · Nomenclature (vue éclatée statique)</h2>{exploded(svg)}</section>'
        f'</body></html>')
(ROOT / "design/bike-preview.html").write_text(html, encoding="utf-8")
print("ok")
