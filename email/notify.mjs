// Internal lead notifications sent to hello@raiseylab.com (NOT the email the visitor receives).
// Same Raisey Lab visual identity as the results email, laid out as an operational lead sheet.
// Everything the visitor typed is escaped; the Scan part is recomputed from scores only (validate/compose), never
// taken from the browser. Reply-To on the actual message is set by the Worker to the lead's address.
import * as K from './kit.mjs';
import { validate, compose, typo } from './render.mjs';

const { esc, C, SERIF, SANS } = K;

// Short English labels (from the on-screen Scan options) for the internal sheet.
const GROWTH = { patients: 'More qualified patients', visibility: 'My visibility', authority: 'My medical authority', social: 'My social presence',
  retention: 'Patient retention', treatment: 'A specific treatment or procedure', team: 'My clinic / team', market: 'A new location or market' };
const INTEREST = { 'first-conversation': 'Request a first conversation', founder: 'Talk to the founder', 'founding-partner': 'Become a founding partner',
  'presence-scan': 'Start the Raisey Scan', 'presence-review': 'Insights: request a Raisey Lab Review', 'service-digital': 'Service: Digital Presence',
  'service-website': 'Service: Website & Patient Journey', 'service-ongoing': 'Service: Ongoing Presence', 'service-growth': 'Service: Growth & Authority' };
const GROUP = { tier1: 'Physicians & surgeons', tier2: 'Nurse prescribers & nurses', tier3: 'Allied & dental', tier4: 'Other' };
const LANG = { en: 'English', fr: 'French' };

const clean = (v, max) => String(v ?? '').replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/g, '').trim().slice(0, max);
const oneLine = (v, max) => clean(v, max).replace(/\s+/g, ' ');

export function parisDate(d = new Date()) {
  return new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Paris', day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }).format(d) + ' (Paris)';
}

/** Website / Instagram field -> safe https link (or plain text when it is not recognisable). */
function webLink(v) {
  const t = oneLine(v, 300);
  const handle = t.match(/^@([A-Za-z0-9._]{1,30})$/);
  if (handle) return `<a href="https://www.instagram.com/${esc(handle[1])}/" target="_blank" style="color:${C.accent};text-decoration:underline">${esc(t)}</a>`;
  const host = t.replace(/^https?:\/\//i, '');
  if (/^[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+(\/[^\s"'<>]*)?$/.test(host)) return `<a href="https://${esc(host)}" target="_blank" style="color:${C.accent};text-decoration:underline">${esc(t)}</a>`;
  return esc(t);
}
const mailLink = e => `<a href="mailto:${esc(e)}" style="color:${C.accent};text-decoration:underline">${esc(e)}</a>`;
const telLink = t => `<a href="tel:${esc(t.replace(/[^\d+]/g, ''))}" style="color:${C.accent};text-decoration:underline">${esc(t)}</a>`;

/** Two-column detail sheet; stacks on phones. Values must already be escaped HTML. */
function sheet(rows) {
  return `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:18px 0 0">${rows.filter(([, v]) => v).map(([k, v]) =>
    `<tr><td class="rl-stack rl-stack-k" width="150" valign="top" style="padding:10px 12px 10px 0;border-top:1px solid ${C.line};font-family:${SANS};font-size:11px;line-height:18px;font-weight:bold;letter-spacing:.12em;text-transform:uppercase;color:${C.muted};mso-line-height-rule:exactly">${esc(k)}</td>` +
    `<td class="rl-stack rl-stack-v" valign="top" style="padding:10px 0;border-top:1px solid ${C.line};font-family:${SANS};font-size:15px;line-height:22px;color:${C.ink};mso-line-height-rule:exactly">${v}</td></tr>`).join('')}</table>`;
}

function header(kind, title, sub) {
  return [
    `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
<td valign="middle">${K.brand({ size: 14, lh: 18, margin: '0' })}</td>
<td valign="middle" align="right" style="font-family:${SANS};font-size:11px;line-height:16px;font-weight:bold;letter-spacing:.14em;color:${C.accent};mso-line-height-rule:exactly">${esc(kind)}</td></tr></table>`,
    K.rule('14px 0 22px'),
    K.p(esc(title), { family: SERIF, size: 26, lh: 31, margin: '0 0 4px' }),
    sub ? K.p(sub, { color: C.muted, margin: '0' }) : '',
  ].join('\n');
}

function replyBlock(email, subject, phone) {
  const href = 'mailto:' + email + '?subject=' + encodeURIComponent(subject);
  return K.button(href, 'Reply to lead →', { width: 220, margin: '28px 0 8px' }) +
    K.p(`Or simply press Reply: this email’s Reply-To is ${mailLink(email)}.` + (phone ? ` Phone: ${telLink(phone)}.` : ''), { color: C.muted, size: 13, lh: 20, margin: '0' });
}

const footer = () => K.p('Internal notification from raiseylab.com · not sent to the lead.', { color: C.muted, size: 12, lh: 18, margin: '28px 0 0', borderTop: '1px solid ' + C.line, padTop: '14px' });

/** NEW RAISEY SCAN — lead sheet with result, six dimensions and shared context. */
export function renderScanNotification(copy, payload, { receivedAt = new Date() } = {}) {
  const v = validate(payload, copy);
  if (!v.ok) throw new Error('invalid payload: ' + v.errors.join('; '));
  const data = v.data;
  const m = compose(copy, { ...data, lang: 'en' });           // English labels for the internal sheet
  const mp = compose(copy, data);                             // exactly what the prospect received, in their language
  const T = t => typo(t, data.lang);
  const name = oneLine(payload.name, 120), email = oneLine(payload.email, 254).toLowerCase();
  const web = oneLine(payload.web, 300), specialty = oneLine(payload.specialty, 80), group = GROUP[oneLine(payload.practitioner_tier, 10)] || '';
  const date = parisDate(receivedAt);
  const growth = data.growth.map(k => GROWTH[k] || k);
  // Name + badge (English, as before), then the prospect's full analysis for that dimension (same text as their email).
  const dimRows = m.dims.map((d, i) => { const a = mp.dims[i];
    return `<tr><td style="padding:12px 0 4px;border-top:1px solid ${C.line};font-family:${SERIF};font-size:16px;line-height:21px;color:${C.ink};mso-line-height-rule:exactly">${esc(d.name)}</td>` +
      `<td align="right" style="padding:12px 0 4px;border-top:1px solid ${C.line}">${K.badge(d.status, d.lv)}</td></tr>` +
      `<tr><td colspan="2" style="padding:0 0 12px;font-family:${SANS};font-size:14px;line-height:22px;color:${C.muted};mso-line-height-rule:exactly">${esc(T(a.full + (a.note ? ' ' + a.note : '')))}</td></tr>`; }).join('');
  const lines = arr => arr.length ? arr.map(esc).join('<br>') : '—';
  const trtList = data.treatments.includes('none') ? ['No specific treatment, the practice overall']
    : data.treatments.filter(k => k !== 'other').map(k => copy.en.trtLabels[k]).concat(data.treatments.includes('other') ? ['Other'] : []);
  const replySubject = data.lang === 'fr' ? 'Votre Raisey Scan' : 'Your Raisey Scan';
  const body = [
    header('NEW RAISEY SCAN', name, `${mailLink(email)} · ${esc(LANG[data.lang])} · ${esc(date)}`),
    sheet([['Name / clinic', esc(name)], ['Email', mailLink(email)], ['Website / Instagram', webLink(web)], ['Specialty', esc(specialty)],
      ['Practitioner group', esc(group)], ['Language', esc(LANG[data.lang])], ['Received', esc(date)]]),
    K.h2('Overall result', { margin: '30px 0 10px' }),
    `<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding:0 0 8px">${K.badge(m.tierLabel, m.tier)}</td></tr></table>`,
    K.p(esc(m.overall), { color: C.muted, size: 14, lh: 22 }),
    K.h2('Six dimensions', { margin: '26px 0 6px' }),
    `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">${dimRows}</table>`,
    K.h2('Shared context', { margin: '26px 0 8px' }),
    sheet([['Wants to grow', lines(growth)], ['Treatments', lines(trtList)], ['Other (their words)', data.other ? esc(data.other) : '']]),
    mp.ctx.length ? K.p('As written in their results email (' + esc(LANG[data.lang]) + '):', { color: C.muted, size: 13, lh: 20, margin: '16px 0 6px' }) +
      mp.ctx.map(t => K.p(esc(T(t)), { size: 14, lh: 22, margin: '0 0 8px' })).join('') : '',
    K.p('The visitor received their full results email in ' + esc(LANG[data.lang]) + '.', { color: C.muted, size: 13, lh: 20, margin: '14px 0 0' }),
    replyBlock(email, replySubject, ''),
    footer(),
  ].join('\n');
  const subject = `New Raisey Scan — ${name} · ${m.tierLabel}`.slice(0, 180);
  const text = ['NEW RAISEY SCAN', '', `Name / clinic: ${name}`, `Email: ${email}`, `Website / Instagram: ${web}`, specialty && `Specialty: ${specialty}`, group && `Practitioner group: ${group}`,
    `Language: ${LANG[data.lang]}`, `Received: ${date}`, '', `OVERALL RESULT: ${m.tierLabel}`, m.overall, '', 'SIX DIMENSIONS', ...m.dims.flatMap((d, i) => [`- ${d.name}: ${d.status}`, '  ' + T(mp.dims[i].full + (mp.dims[i].note ? ' ' + mp.dims[i].note : ''))]), '',
    'SHARED CONTEXT', 'Wants to grow:', ...growth.map(g => '- ' + g), 'Treatments:', ...trtList.map(t => '- ' + t), ...(data.other ? ['Other (their words): ' + data.other] : []), ...(mp.ctx.length ? ['', 'As written in their results email:', ...mp.ctx.map(t => T(t))] : []), '', `Reply to lead: press Reply (Reply-To: ${email})`].filter(x => x !== false && x !== undefined).join('\n');
  return { subject, html: K.doc({ lang: 'en', title: subject, preheader: `${m.tierLabel} · ${email} · ${LANG[data.lang]}`, body }), text };
}

/** NEW ENQUIRY — contact form lead sheet. */
export function renderContactNotification(payload, { receivedAt = new Date() } = {}) {
  const f = { name: oneLine(payload.name, 120), clinic: oneLine(payload.clinic, 160), email: oneLine(payload.email, 254).toLowerCase(), phone: oneLine(payload.phone, 40),
    specialty: oneLine(payload.specialty, 80), group: GROUP[oneLine(payload.practitioner_tier, 10)] || '', interest: oneLine(payload.interest, 40),
    message: clean(payload.message, 3000), lang: payload.lang === 'fr' ? 'fr' : 'en' };
  const date = parisDate(receivedAt);
  const from = INTEREST[f.interest] || (f.interest ? f.interest : 'Contact section');
  const msg = f.message ? esc(f.message).replace(/\r?\n/g, '<br>') : `<span style="color:${C.muted}">No message.</span>`;
  const body = [
    header('NEW ENQUIRY', f.name, `${esc(f.clinic)} · ${esc(LANG[f.lang])} · ${esc(date)}`),
    sheet([['Name', esc(f.name)], ['Clinic', esc(f.clinic)], ['Email', mailLink(f.email)], ['Phone', f.phone ? telLink(f.phone) : ''], ['Specialty', esc(f.specialty)],
      ['Practitioner group', esc(f.group)], ['Came from', esc(from)], ['Language', esc(LANG[f.lang])], ['Received', esc(date)]]),
    K.h2('Message', { margin: '30px 0 10px' }),
    `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td bgcolor="${C.panel}" style="background-color:${C.panel};border-left:3px solid ${C.accent};padding:16px 18px;font-family:${SANS};font-size:15px;line-height:23px;color:${C.ink};mso-line-height-rule:exactly">${msg}</td></tr></table>`,
    replyBlock(f.email, f.lang === 'fr' ? 'Votre demande — Raisey Lab' : 'Your enquiry — Raisey Lab', f.phone),
    footer(),
  ].join('\n');
  const subject = `New enquiry — ${f.clinic} (${f.name})`.slice(0, 180);
  const text = ['NEW ENQUIRY', '', `Name: ${f.name}`, `Clinic: ${f.clinic}`, `Email: ${f.email}`, f.phone && `Phone: ${f.phone}`, f.specialty && `Specialty: ${f.specialty}`,
    f.group && `Practitioner group: ${f.group}`, `Came from: ${from}`, `Language: ${LANG[f.lang]}`, `Received: ${date}`, '', 'MESSAGE', f.message || 'No message.', '',
    `Reply to lead: press Reply (Reply-To: ${f.email})`].filter(x => x !== false && x !== undefined && x !== null).join('\n');
  return { subject, html: K.doc({ lang: 'en', title: subject, preheader: `${f.clinic} · ${f.email} · ${LANG[f.lang]}`, body }), text };
}
