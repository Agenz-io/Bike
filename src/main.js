/* Garnier Cycles · site de démonstration
 * Deux mécaniques de scroll seulement :
 *   1. vue éclatée du vélo (hero épinglé, démontage pièce par pièce puis remontage)
 *   2. compteurs des chiffres clés
 * + révélation sèche des grilles bento, FAQ à ouverture unique, formulaire factice.
 */
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import parts from './data/parts.json';

gsap.registerPlugin(ScrollTrigger);

const root = document.documentElement;
const byId = Object.fromEntries(parts.map((p) => [p.id, p]));

/* cadrages du dessin (unités = mm du dessin) */
const VB = {
  r: [-380, -800, 1760, 1240],      // assemblé, statique
  d: [-760, -1150, 2520, 1830],     // desktop : place pour l'éclaté dans les deux axes
  m: [-380, -1080, 1740, 2220],     // mobile : éclaté vertical
};

/* ordre de démontage */
const STEPS = {
  d: [['selle'], ['cockpit'], ['fourche'], ['roue-av', 'roue-ar'], ['groupe'], ['cadre']],
  m: [['selle', 'cockpit'], ['roue-av', 'roue-ar'], ['fourche', 'groupe'], ['cadre']],
};

const hero = document.querySelector('.hero');
const stage = document.getElementById('stage');
const svg = stage.querySelector('svg.bike');
const nomen = document.querySelector('.nomenclature');
const nomenHome = nomen.parentElement;
const hud = stage.querySelector('.hud');
const hudN = hud.querySelector('.hud-n');

const pad = (n) => String(n).padStart(2, '0');
const setVB = (vb) => svg.setAttribute('viewBox', vb.join(' '));
const noteEl = (id) => nomen.querySelector(`[data-note="${id}"]`);
const partEl = (id) => svg.querySelector(`[data-part="${id}"]`);

/* ------------------------------------------------------------------ scène */
function setupStage(mode) {
  const vb = VB[mode];
  setVB(vb);
  const inner = document.createElement('div');
  inner.className = 'stage-in';
  stage.prepend(inner);
  inner.append(svg);
  /* desktop : étiquettes posées sur le dessin · mobile : légende fixe en bas du hero */
  (mode === 'd' ? inner : stage).append(nomen);

  const NS = 'http://www.w3.org/2000/svg';
  const leaders = document.createElementNS(NS, 'g');
  leaders.setAttribute('class', 'leaders');
  svg.querySelector('.bike-root').append(leaders);

  parts.forEach((p) => {
    if (p.note === false) return;
    const el = noteEl(p.id);
    if (mode === 'd') {
      const [lx, ly] = p.label;
      if (p.align === 'right') el.style.right = `${100 - ((lx - vb[0]) / vb[2]) * 100}%`;
      else el.style.left = `${((lx - vb[0]) / vb[2]) * 100}%`;
      el.style.top = `${((ly - vb[1]) / vb[3]) * 100}%`;
      const [ax, ay] = [p.anchor[0] + p.offset[0], p.anchor[1] + p.offset[1]];
      const g = document.createElementNS(NS, 'g');
      g.setAttribute('class', 'leader-g');
      g.dataset.leader = p.id;
      g.innerHTML = `<circle class="leader-dot" cx="${ax}" cy="${ay}" r="7"/>`
        + `<line class="leader" x1="${ax}" y1="${ay}" x2="${lx}" y2="${ly}"/>`
        + `<line class="leader" x1="${lx}" y1="${ly}" x2="${lx + (p.align === 'right' ? -560 : 560)}" y2="${ly}"/>`;
      leaders.append(g);
    }
  });

  /* mobile : 1 ou 2 fiches côte à côte par étape */
  if (mode === 'm') {
    STEPS.m.forEach((ids) => {
      const noted = ids.filter((id) => byId[id].note !== false);
      noted.forEach((id, i) => {
        const el = noteEl(id);
        el.style.left = noted.length > 1 ? (i ? '52%' : '0') : '0';
        el.style.right = noted.length > 1 ? (i ? '0' : '52%') : '0';
      });
    });
  }

  const size = () => {
    const W = hero.clientWidth, H = hero.clientHeight;
    const a = vb[2] / vb[3];
    const line = hero.querySelector('.hero-line');
    const nameEl = hero.querySelector('.hero-name');
    const lineB = line.offsetTop + line.offsetHeight;
    /* fraction verticale occupée par le vélo assemblé (+ cotes) dans le cadrage */
    const f0 = (-780 - vb[1]) / vb[3], f1 = (440 - vb[1]) / vb[3];
    let w, h, top;
    if (mode === 'd') {
      const topLim = lineB - 40, botLim = nameEl.offsetTop - 8;
      h = (botLim - topLim) / (f1 - f0);
      w = Math.min(W * 0.92, h * a); h = w / a;
      top = topLim - f0 * h + Math.max(0, (botLim - topLim) - (f1 - f0) * h) / 2;
    } else {
      const navB = hero.querySelector('.nav').offsetHeight;
      const room = H - navB - 190;            /* place laissée à la légende en bas */
      w = Math.min(W, room * a); h = w / a;
      top = Math.max(navB, lineB + 6 - f0 * h);
      top = Math.min(top, H - 190 - h);
    }
    inner.style.width = `${w}px`;
    inner.style.height = `${h}px`;
    inner.style.top = `${top + h / 2}px`;
  };
  size();
  ScrollTrigger.addEventListener('refreshInit', size);

  return () => {
    ScrollTrigger.removeEventListener('refreshInit', size);
    leaders.remove();
    nomen.querySelectorAll('.note').forEach((n) => n.removeAttribute('style'));
    stage.prepend(svg);
    nomenHome.append(nomen);
    inner.remove();
    setVB(VB.r);
  };
}

/* ------------------------------------------------------------------ 1 · vue éclatée */
function buildExploded(mode) {
  const steps = STEPS[mode];
  const off = (id) => (mode === 'd' ? byId[id].offset : byId[id].mobile);
  const textOut = [hero.querySelector('.hero-k'), hero.querySelector('.hero-meta'), hero.querySelector('.hero-line'), hero.querySelector('.hero-hint')].filter(Boolean);
  const name = hero.querySelector('.hero-name');
  const cotes = svg.querySelector('#cotes');
  const allNotes = [...nomen.querySelectorAll('.note')];
  const leaderOf = (id) => svg.querySelector(`[data-leader="${id}"]`);

  const tl = gsap.timeline({
    defaults: { ease: 'power3.inOut' },
    scrollTrigger: {
      trigger: hero,
      pin: true,
      start: 'top top',
      end: mode === 'd' ? '+=430%' : '+=300%',
      scrub: 0.3,
      snap: { snapTo: 'labelsDirectional', duration: { min: 0.12, max: 0.35 }, delay: 0.1, ease: 'power2.inOut', inertia: false },
      invalidateOnRefresh: true,
    },
  });

  tl.addLabel('assemble');
  /* le texte du hero se retire d'un bloc, sans fondu progressif de décor */
  tl.to(textOut, { y: -24, autoAlpha: 0, duration: 0.45, ease: 'power2.in', stagger: 0.03 }, 0)
    .to(name, { yPercent: 60, autoAlpha: 0, duration: 0.45, ease: 'power2.in' }, 0)
    .to(cotes, { autoAlpha: 0, duration: 0.25, ease: 'none' }, 0)
    .to(hud, { autoAlpha: 1, duration: 0.2, ease: 'none' }, 0.35);

  const marks = [];           // temps où chaque étape est complète (pour le compteur de nomenclature)
  let shown = [];             // fiches visibles (mobile : on remplace à chaque étape)
  let count = 0;

  steps.forEach((ids, i) => {
    const t0 = tl.duration() + (i === 0 ? 0.05 : 0.15);
    const moving = ids.filter((id) => id !== 'cadre');
    const notes = ids.filter((id) => byId[id].note !== false).map(noteEl);

    if (mode === 'm' && shown.length) tl.to(shown, { autoAlpha: 0, duration: 0.2, ease: 'none' }, t0);
    /* déplacement : chaque pièce suit son axe, mouvement net, sans dépassement */
    moving.forEach((id, k) => {
      const [x, y] = off(id);
      tl.to(partEl(id), { x, y, duration: 1, ease: 'power3.inOut' }, t0 + k * 0.08);
    });
    /* le cadre ne bouge pas : il passe en jaune le temps de son annotation */
    if (ids.includes('cadre')) tl.to(partEl('cadre'), { color: '#F2D20A', duration: 0.3, ease: 'none' }, t0);

    const tNote = t0 + (moving.length ? 0.85 : 0.2);
    if (mode === 'd') {
      ids.forEach((id) => { const l = leaderOf(id); if (l) tl.fromTo(l, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.15, ease: 'none' }, tNote); });
    }
    tl.fromTo(notes, { autoAlpha: 0, x: mode === 'd' ? -10 : 0, y: mode === 'm' ? 10 : 0 },
      { autoAlpha: 1, x: 0, y: 0, duration: 0.3, ease: 'power2.out' }, tNote + 0.05);
    count += notes.length;
    marks.push({ t: tNote + 0.05, n: Math.min(count, 6) });
    tl.addLabel(`piece-${i + 1}`, tNote + 0.35);
    shown = notes;
  });

  /* temps d'arrêt sur la vue éclatée */
  tl.to({}, { duration: 0.6 });
  tl.addLabel('eclate');

  /* remontage : tout se remet en place, dans l'ordre inverse */
  const tBack = tl.duration();
  const leaders = [...svg.querySelectorAll('.leader-g')];
  tl.to([...allNotes, ...leaders], { autoAlpha: 0, duration: 0.25, ease: 'none' }, tBack)
    .to(partEl('cadre'), { color: '#ECEFEA', duration: 0.25, ease: 'none' }, tBack);
  const order = steps.flat().filter((id) => id !== 'cadre').reverse();
  order.forEach((id, k) => tl.to(partEl(id), { x: 0, y: 0, duration: 0.8, ease: 'power3.inOut' }, tBack + 0.2 + k * 0.09));
  const tDone = tl.duration();
  tl.to(hud, { autoAlpha: 0, duration: 0.15, ease: 'none' }, tDone - 0.2)
    .to(cotes, { autoAlpha: 1, duration: 0.2, ease: 'none' }, tDone)
    .to(name, { yPercent: 0, autoAlpha: 1, duration: 0.45, ease: 'power2.out' }, tDone)
    .to(textOut.filter((e) => !e.classList.contains('hero-hint')), { y: 0, autoAlpha: 1, duration: 0.45, ease: 'power2.out', stagger: 0.03 }, tDone);
  tl.addLabel('remonte');
  tl.to({}, { duration: 0.25 });

  /* compteur de nomenclature : 00 → 06 */
  let last = -1;
  tl.eventCallback('onUpdate', () => {
    const t = tl.time();
    let n = 0;
    for (const m of marks) if (t >= m.t) n = m.n;
    if (t >= tBack) n = 6;
    if (n !== last) { hudN.textContent = pad(n); last = n; }
  });
  return tl;
}

/* ------------------------------------------------------------------ 2 · compteurs */
function setupCounters() {
  const els = [...document.querySelectorAll('.count')];
  const fmts = new Map();
  const fmt = (dec) => {
    if (!fmts.has(dec)) fmts.set(dec, new Intl.NumberFormat('fr-FR', { minimumFractionDigits: dec, maximumFractionDigits: dec }));
    return fmts.get(dec);
  };
  const finals = els.map((el) => el.textContent);
  /* groupés par grille : les chiffres d'une même planche partent ensemble, en cascade */
  const groups = new Map();
  els.forEach((el) => {
    const g = el.closest('.bento') || el;
    if (!groups.has(g)) groups.set(g, []);
    groups.get(g).push(el);
  });
  groups.forEach((list, g) => {
    list.forEach((el) => { el.textContent = fmt(+el.dataset.dec || 0).format(0); });
    ScrollTrigger.create({
      trigger: g,
      start: 'top 75%',
      once: true,
      onEnter: () => {
        list.forEach((el, i) => {
          const to = +el.dataset.to, dec = +el.dataset.dec || 0, f = fmt(dec);
          const o = { v: 0 };
          /* comme un compteur à rouleaux : valeurs par crans, pas de glissé continu */
          gsap.to(o, {
            v: to, duration: 1.3, delay: 0.12 * i, ease: 'steps(26)',
            onUpdate: () => { el.textContent = f.format(o.v); },
            onComplete: () => { el.textContent = f.format(to); },
          });
        });
      },
    });
  });
  return () => els.forEach((el, i) => { el.textContent = finals[i]; });
}

/* ------------------------------------------------------------------ révélation des bento */
function setupBento() {
  document.querySelectorAll('.bento').forEach((b) => {
    const tiles = [...b.children];
    gsap.set(tiles, { clipPath: 'inset(0% 0% 100% 0%)' });
    ScrollTrigger.create({
      trigger: b,
      start: 'top 82%',
      once: true,
      onEnter: () => gsap.to(tiles, {
        clipPath: 'inset(0% 0% 0% 0%)', duration: 0.6, ease: 'power3.inOut', stagger: 0.07,
        onComplete: () => gsap.set(tiles, { clearProps: 'clipPath' }),
      }),
    });
  });
}

/* ------------------------------------------------------------------ montage par media query */
const mm = gsap.matchMedia();
mm.add({
  d: '(min-width: 900px) and (prefers-reduced-motion: no-preference)',
  m: '(max-width: 899px) and (prefers-reduced-motion: no-preference)',
  r: '(prefers-reduced-motion: reduce)',
}, (ctx) => {
  const { d, m } = ctx.conditions;
  root.classList.toggle('motion-d', !!d);
  root.classList.toggle('motion-m', !!m);
  if (!d && !m) { setVB(VB.r); return undefined; }
  const mode = d ? 'd' : 'm';
  const undoStage = setupStage(mode);
  buildExploded(mode);
  const undoCounters = setupCounters();
  setupBento();
  return () => { undoStage(); undoCounters(); };
});

/* ------------------------------------------------------------------ bouton flottant */
const fab = document.querySelector('.fab');
ScrollTrigger.create({
  trigger: '#atelier',
  start: 'top 60%',
  endTrigger: '#etude',
  end: 'top 80%',
  onToggle: (self) => {
    fab.classList.toggle('on', self.isActive);
    fab.toggleAttribute('aria-hidden', !self.isActive);
    fab.tabIndex = self.isActive ? 0 : -1;
  },
});

/* ------------------------------------------------------------------ FAQ : une seule réponse ouverte */
const faq = document.querySelector('.faq');
faq?.addEventListener('toggle', (e) => {
  const d = e.target;
  if (!d.open) return;
  faq.querySelectorAll('details[open]').forEach((o) => { if (o !== d) o.open = false; });
}, true);

/* ------------------------------------------------------------------ menu mobile : se ferme au clic */
document.querySelectorAll('.nav-m a').forEach((a) => a.addEventListener('click', () => a.closest('details').removeAttribute('open')));

/* ------------------------------------------------------------------ formulaire (démo, non connecté) */
const form = document.getElementById('form-etude');
form?.addEventListener('submit', (e) => {
  e.preventDefault();
  if (!form.reportValidity()) return;
  const ok = form.querySelector('.form-ok');
  ok.hidden = false;
  form.querySelector('button[type="submit"]').disabled = true;
  ok.focus?.();
});

window.addEventListener('load', () => ScrollTrigger.refresh());
