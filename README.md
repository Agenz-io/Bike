# Garnier Cycles — site de démonstration

Site vitrine d'un atelier de vélos sur mesure **fictif** (Annecy). Concept : « Construit pour un seul cycliste ».
Le vélo, dessiné en SVG technique, se démonte pièce par pièce au scroll, puis se remonte.

**Site de démonstration, entreprise fictive.** Noms, clients, avis, prix et coordonnées sont inventés.

## Stack
- Vite 5, HTML/CSS/JS sans framework
- GSAP 3 + ScrollTrigger : vue éclatée épinglée, compteurs, révélation des grilles bento
- Polices auto-hébergées : Sofia Sans Extra Condensed + Sofia Sans Semi Condensed (OFL)

## Commandes
```bash
npm install
npm run dev       # développement
npm run build     # régénère le dessin SVG puis construit dist/
npm run preview   # sert dist/
```

## Structure
- `index.html` : page unique (SEO, JSON-LD LocalBusiness + Product + FAQPage)
- `src/main.js` : animations (desktop, mobile allégé, prefers-reduced-motion)
- `src/styles.css` : direction « Vert usine »
- `scripts/build-bike.py` : génère `src/partials/bike.svg` et la nomenclature à partir de `src/data/parts.json`
- `public/images/` : emplacement des photos (placeholders dans la page en attendant)
- `design/` : directions, animations retenues (`animations.md`), registre `deja-fait.md`, captures
