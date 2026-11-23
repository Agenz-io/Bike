"""Recadre et optimise les photos du site (WebP, plusieurs largeurs pour srcset).

Sources : design/images-sources/<nom>.<ext>  (fichiers fournis, non publiés)
Sortie  : public/images/<nom>-<largeur>.webp
Usage   : python3 scripts/optimize-images.py
"""
import json, pathlib
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "design" / "images-sources"
OUT = ROOT / "public" / "images"

# crop = (x0, y0, x1, y1) en pixels de la source, ou None ; widths = largeurs générées
IMAGES = {
    "atelier-soudure":    {"crop": (390, 0, 1209, 1024),  "ratio": (4, 5),  "widths": [480, 640, 800]},
    "atelier-outils":     {"crop": (350, 112, 1262, 1024), "ratio": (1, 1),  "widths": [400, 600, 900]},
    "tubes-acier-titane": {"crop": (0, 130, 1448, 944),   "ratio": (16, 9), "widths": [640, 960, 1440]},
    "peinture-cabine":    {"crop": None,                  "ratio": (3, 2),  "widths": [640, 1024, 1536]},
    "gravure-boitier":    {"crop": None,                  "ratio": (3, 2),  "widths": [640, 1024, 1536]},
    "etude-posturale":    {"crop": None,                  "ratio": (4, 5),  "widths": [480, 800, 1200]},
}


def find_source(name):
    for ext in (".webp", ".jpg", ".jpeg", ".png"):
        p = SRC / f"{name}{ext}"
        if p.exists():
            return p
    return None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report = {}
    for name, cfg in IMAGES.items():
        src = find_source(name)
        if not src:
            print(f"-- {name} : source absente, placeholder conservé")
            continue
        im = Image.open(src).convert("RGB")
        if cfg["crop"]:
            im = im.crop(cfg["crop"])
        rw, rh = cfg["ratio"]
        # recadrage centré au ratio exact
        w, h = im.size
        if w / h > rw / rh:
            nw = round(h * rw / rh); x0 = (w - nw) // 2; im = im.crop((x0, 0, x0 + nw, h))
        else:
            nh = round(w * rh / rw); y0 = (h - nh) // 2; im = im.crop((0, y0, w, y0 + nh))
        files = []
        for tw in cfg["widths"]:
            tw = min(tw, im.size[0])
            th = round(tw * rh / rw)
            out = OUT / f"{name}-{tw}.webp"
            im.resize((tw, th), Image.LANCZOS).save(out, "WEBP", quality=78, method=6)
            files.append({"w": tw, "h": th, "file": out.name, "ko": round(out.stat().st_size / 1024)})
        report[name] = files
        print(f"ok {name} : " + ", ".join(f"{f['w']}px {f['ko']} ko" for f in files))
    (OUT / "manifest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
