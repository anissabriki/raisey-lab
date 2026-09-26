// Renders the Raisey Scan results email (HTML + plain text) from STRUCTURED DATA ONLY.
// Pure function, no dependencies: runs unchanged in Node, a Cloudflare Worker, a Lambda or a Netlify/Vercel function.
//
// SECURITY: the browser never sends HTML. It sends scores and answer keys; this file turns them into the email using the
// copy in scan_copy.json. Anything else in the payload is ignored, so the endpoint cannot be used to send arbitrary content.
// The email is a one-off transactional message: no mailing-list subscription happens here or anywhere else.

import { DIMS, FACETS, dimensions, levelOf as level, tierOf, nuances } from '../scan_scoring.mjs';   // same scoring as the on-screen Scan
import * as K from './kit.mjs';                                  // email-safe HTML building blocks (Outlook/Gmail/Apple Mail)
export { DIMS };
const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const NB = ' ';
const typo = (s, lang) => (lang === 'fr' ? s.replace(/ ([?!:;])/g, NB + '$1') : s);
export { typo };                                                    // reused by the internal lead sheet (same typography)

/** Validates the untrusted payload. Returns { ok, errors, data } where data holds only whitelisted, typed values. */
export function validate(payload, copy) {
  const errors = [];
  const lang = payload && payload.lang === 'fr' ? 'fr' : 'en';
  const scan = (payload && payload.scan) || {};
  const scores = {};
  for (const k of FACETS) {
    const v = scan.scores && scan.scores[k];
    if (!Number.isInteger(v) || v < 0 || v > 3) errors.push('score ' + k + ' must be an integer 0-3');
    else scores[k] = v;
  }
  const dims = errors.length ? {} : dimensions(scores);   // recomputed here: client-sent dimension values are ignored
  const answers = scan.answers || {};
  const growth = (Array.isArray(answers.growth) ? answers.growth : []).filter(k => Object.hasOwn(copy[lang].obj, k));
  const trt = Array.isArray(answers.treatments) ? answers.treatments : [];
  const treatments = trt.filter(k => Object.hasOwn(copy[lang].trtLabels, k) || k === 'other' || k === 'none');
  const other = String((scan.other && scan.other.treatments) || '').replace(/[\u0000-\u001f<>]/g, '').trim().slice(0, 80);
  return { ok: errors.length === 0, errors, data: { lang, scores, dims, growth: [...new Set(growth)], treatments: [...new Set(treatments)], other } };
}

const list = (arr, and) => (arr.length < 2 ? arr.join('') : arr.slice(0, -1).join(', ') + ' ' + and + ' ' + arr[arr.length - 1]);

/** Builds the semantic content of the email (shared by the HTML and text renderers). */
export function compose(copy, data) {
  const c = copy[data.lang];
  const tier = tierOf(data.dims);
  const extra = {};                                   // nuance sentences, only from the user's own answers
  for (const n of nuances(data.scores)) extra[n.dim] = c.nuance[n.dim][n.key];
  const order = DIMS.map((k, i) => ({ k, i, v: data.dims[k] }));
  const strong = order.filter(d => level(d.v) !== 'elevate').sort((a, b) => b.v - a.v || a.i - b.i).slice(0, 2);
  let room = order.filter(d => level(d.v) === 'elevate').sort((a, b) => a.v - b.v || a.i - b.i).slice(0, 2);
  if (!room.length) { const low = order.slice().sort((a, b) => a.v - b.v || a.i - b.i)[0]; room = level(low.v) === 'potential' ? [low] : []; }
  const ctx = data.growth.map(k => c.obj[k]);
  if (data.treatments.length) {
    if (data.treatments.includes('none')) ctx.push(c.trt.none);
    else {
      const labels = data.treatments.filter(k => k !== 'other').map(k => c.trtLabels[k]);
      if (data.treatments.includes('other') && data.other) labels.push(data.other);
      if (labels.length) ctx.push(c.trt.list.replace('{treatments}', list(labels, c.trt.and)));
    }
  }
  const dimRow = d => ({ key: d.k, name: c.dim[d.k], status: c.tier[level(d.v)], lv: level(d.v), s1: c.I[d.k][level(d.v)][0], full: c.I[d.k][level(d.v)].join(' '), note: extra[d.k] || '' });
  return {
    tier, tierLabel: c.tier[tier], overall: c.diag[tier],
    dims: order.map(dimRow), strong: strong.map(dimRow), room: room.map(dimRow), ctx,
  };
}

export function renderEmail(copy, payload, opts = {}) {
  const v = validate(payload, copy);
  if (!v.ok) throw new Error('invalid payload: ' + v.errors.join('; '));
  const { data } = v, lang = data.lang, c = copy[lang], e = c.email, T = s => typo(s, lang);
  const m = compose(copy, data);
  const ctaUrl = opts.ctaUrl || '#', privacyUrl = opts.privacyUrl || '#';
  const subject = T(e.subject), preheader = T(e.preheader);
  const P = (t, o) => K.p(esc(T(t)), o);
  const muted = { color: K.C.muted };
  const row = d => `<tr><td style="padding:14px 0;border-top:1px solid ${K.C.line}">
<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:0 0 6px"><tr>
<td style="padding:0 10px 0 0;vertical-align:middle;font-family:${K.SERIF};font-size:17px;line-height:22px;color:${K.C.ink};mso-line-height-rule:exactly">${esc(d.name)}</td>
<td style="vertical-align:middle">${K.badge(d.status, d.lv)}</td></tr></table>
${P(d.full + (d.note ? ' ' + d.note : ''), { ...muted, margin: '0' })}</td></tr>`;
  const body = [
    K.brand({ margin: '0 0 28px' }),                                        // wordmark (e.sign = "Raisey Lab")
    ...(e.lead
      ? [P(e.hello),
         P(e.lead, { family: K.SERIF, size: 22, lh: 29, margin: '0 0 14px' }),   // editorial lead: what you can raise
         P(e.intro),
         P(e.disc, { ...muted, size: 13, lh: 20, margin: '0 0 4px' })]           // disclaimer: clear but secondary
      : [K.label(T(c.basis), { margin: '0 0 26px' }), P(e.hello), P(e.intro)]),   // French: original Presence-era structure
    K.h2(T(e.hOverall)),
    `<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding:0 0 8px">${K.badge(m.tierLabel, m.tier)}</td></tr></table>`,
    P(m.overall),
    K.h2(T(e.hDims)),
    `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">${m.dims.map(row).join('')}</table>`,
    m.strong.length ? K.h2(T(e.hStrong)) + m.strong.map(d => P(d.name + ' — ' + d.s1)).join('') : '',
    m.room.length ? K.h2(T(e.hRoom)) + m.room.map(d => P(d.name + ' — ' + d.full)).join('') : '',
    m.ctx.length ? K.h2(T(e.hContext)) + m.ctx.map(t => P(t)).join('') + P(e.ctxNote, { ...muted, italic: true }) : '',
    K.h2(T(e.hNext)),
    e.trio.map(t => P(t, { family: K.SERIF, size: 17, lh: 25, margin: '0 0 4px' })).join(''),
    P(e.timing, { ...muted, margin: '14px 0 12px' }),
    K.button(ctaUrl, T(e.cta) + ' →'),
    P(e.ctaNote, { ...muted, size: 13, lh: 20 }),
    K.p(esc(T(c.transp)), { ...muted, size: 13, lh: 21, margin: '30px 0 8px', borderTop: '1px solid ' + K.C.line, padTop: '18px' }),
    K.p(esc(T(e.footAuto)), { ...muted, size: 13, lh: 21, margin: '0 0 8px' }),
    K.p(esc(T(e.footWhy)) + ` <a href="${esc(privacyUrl)}" target="_blank" style="color:${K.C.ink};text-decoration:underline">${esc(e.privacy)}</a>`, { ...muted, size: 13, lh: 21, margin: '0' }),
  ].join('\n');
  const html = K.doc({ lang, title: subject, preheader, body });
  const COL = lang === 'fr' ? NB + ': ' : ': ';   // French typography: no-break space before a colon
  const text = [e.sign.toUpperCase(), ...(e.lead ? ['', T(e.hello), '', T(e.lead), '', T(e.intro), T(e.disc), ''] : [T(c.basis).toUpperCase(), '', T(e.hello), '', T(e.intro), '']),
    T(e.hOverall).toUpperCase(), m.tierLabel + '. ' + T(m.overall), '',
    T(e.hDims).toUpperCase(), ...m.dims.map(d => `- ${d.name} (${d.status})${COL}${T(d.full + (d.note ? ' ' + d.note : ''))}`), '',
    ...(m.strong.length ? [T(e.hStrong).toUpperCase(), ...m.strong.map(d => `- ${d.name}${COL}${T(d.s1)}`), ''] : []),
    ...(m.room.length ? [T(e.hRoom).toUpperCase(), ...m.room.map(d => `- ${d.name}${COL}${T(d.full)}`), ''] : []),
    ...(m.ctx.length ? [T(e.hContext).toUpperCase(), ...m.ctx.map(t => '- ' + T(t)), T(e.ctxNote), ''] : []),
    T(e.hNext).toUpperCase(), ...e.trio.map(T), T(e.timing), '', T(e.cta) + COL + ctaUrl, T(e.ctaNote), '',
    T(c.transp), T(e.footAuto), T(e.footWhy) + ' ' + e.privacy + COL + privacyUrl].join('\n');
  return { subject, preheader, html, text, tier: m.tier };
}
