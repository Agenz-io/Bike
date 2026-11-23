import fs from 'node:fs';
import { resolve } from 'node:path';
import { defineConfig } from 'vite';

const root = new URL('.', import.meta.url).pathname;

/* Inclut les partiels générés (dessin SVG, nomenclature) et pose les espaces fines
 * insécables de la typographie française (milliers, unités, ponctuation haute). */
function frTypo(html) {
  return html.replace(/(<script[\s\S]*?<\/script>)|(<[^>]+>)|([^<]+)/g, (m, script, tag, text) => {
    if (!text) return m;
    return text
      .replace(/(\d) (\d{3})(?!\d)/g, '$1 $2')
      .replace(/(\d) (\d{3})(?!\d)/g, '$1 $2')
      .replace(/(\d) (€|g|kg|mm|cm|m|h|km|%|°|ans|semaines?|jours?|rayons|pouces|vélos)(?=[\s<.,;:)!?]|$)/g, '$1 $2')
      .replace(/ ([:;?!»])/g, ' $1')
      .replace(/« /g, '« ')
      .replace(/ · /g, ' · ');
  });
}

export default defineConfig({
  base: './',   /* chemins relatifs : fonctionne à la racine comme sous /Bike/ (GitHub Pages) */
  plugins: [{
    name: 'partials-and-typo',
    transformIndexHtml: {
      order: 'pre',
      handler(html) {
        const withPartials = html.replace(/<!--\s*@include (\S+)\s*-->/g, (_, f) => fs.readFileSync(resolve(root, 'src/partials', f), 'utf8'));
        return frTypo(withPartials);
      },
    },
  }],
  build: {
    rollupOptions: {
      input: { main: resolve(root, 'index.html'), mentions: resolve(root, 'mentions-legales.html') },
    },
  },
});
