// Email-safe building blocks shared by the Raisey Scan results email and the internal lead notifications.
// Built for Gmail (web/app), Outlook (Windows desktop/Word engine, web, mobile) and Apple Mail:
// tables for layout, inline long-hand styles, bgcolor attributes, font fallbacks, an Outlook fixed-width (MSO) container,
// table-based badges, a VML button for Outlook, and a hidden preheader. No web fonts, no flexbox/grid, no background images.

export const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

// Raisey Lab art direction (site tokens): ivory page, optical-cream card, stone lines, dark ink, burgundy anchor, pale-lavender panel.
export const C = { page: '#f3eee6', card: '#faf8f4', line: '#d9cfc4', ink: '#1c1819', muted: '#6b625e', accent: '#4f1a2a', white: '#ffffff', panel: '#e8e5ec' };
export const SERIF = "Georgia,'Times New Roman',Times,serif";
export const SANS = 'Arial,Helvetica,sans-serif';
export const TIER = { established: ['#dde6ea', '#3f5963'], potential: ['#e8e5ec', '#4b4257'], elevate: ['#e7e0d6', '#4f1a2a'] };   // clinical blue · lavender · stone

const WIDTH = 560;

/** Brand signature: the RAISEY LAB wordmark in letter-spaced serif caps, like the site header. Text only: the old circular
 *  symbol is deprecated, and the official & monogram will be added here once its final files are supplied. */
export function brand({ size = 15, lh = 20, margin = '0 0 4px' } = {}) {
  return `<p style="margin:${margin};font-family:${SERIF};font-size:${size}px;line-height:${lh}px;letter-spacing:.3em;text-transform:uppercase;color:${C.ink};mso-line-height-rule:exactly">Raisey Lab</p>`;
}

/** Full HTML document: head resets + Outlook settings, hidden preheader, page background, centred card. */
export function doc({ lang = 'en', title = '', preheader = '', body = '', pad = '36px 32px' }) {
  const spacer = '&#8199;&#847; '.repeat(40);           // stops clients pulling body text into the inbox preview
  return `<!DOCTYPE html>
<html lang="${esc(lang)}" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="x-apple-disable-message-reformatting">
<meta name="format-detection" content="telephone=no,date=no,address=no,email=no,url=no">
<meta name="color-scheme" content="light">
<meta name="supported-color-schemes" content="light">
<title>${esc(title)}</title>
<!--[if mso]><noscript><xml><o:OfficeDocumentSettings><o:AllowPNG/><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml></noscript><![endif]-->
<style>
  body,table,td,a{-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%}
  table,td{mso-table-lspace:0pt;mso-table-rspace:0pt}
  table{border-collapse:collapse}
  img{border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic}
  a[x-apple-data-detectors]{color:inherit!important;text-decoration:none!important;font-size:inherit!important;font-family:inherit!important;font-weight:inherit!important;line-height:inherit!important}
  u + #body a{color:inherit;text-decoration:none}
  @media only screen and (max-width:600px){
    .rl-outer{padding:20px 10px!important}
    .rl-pad{padding:28px 20px!important}
    .rl-stack{display:block!important;width:100%!important;padding-left:0!important}
    .rl-stack-k{padding-bottom:0!important}
    .rl-stack-v{border-top:0!important;padding-top:2px!important}
  }
</style>
</head>
<body id="body" style="margin:0;padding:0;background-color:${C.page};word-spacing:normal" bgcolor="${C.page}">
<div style="display:none;font-size:1px;line-height:1px;max-height:0;max-width:0;opacity:0;overflow:hidden;mso-hide:all">${esc(preheader)}${spacer}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="${C.page}" style="background-color:${C.page}">
<tr><td align="center" class="rl-outer" style="padding:32px 16px">
<!--[if mso]><table role="presentation" width="${WIDTH}" align="center" cellpadding="0" cellspacing="0" border="0"><tr><td><![endif]-->
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="${C.card}" style="max-width:${WIDTH}px;width:100%;background-color:${C.card};border:1px solid ${C.line}">
<tr><td class="rl-pad" style="padding:${pad}">
${body}
</td></tr>
</table>
<!--[if mso]></td></tr></table><![endif]-->
</td></tr>
</table>
</body>
</html>`;
}

const style = o => Object.entries(o).filter(([, v]) => v !== undefined && v !== '').map(([k, v]) => k + ':' + v).join(';');

/** Paragraph. `html` must already be escaped. */
export function p(html, o = {}) {
  return `<p style="${style({
    margin: o.margin ?? '0 0 12px', 'font-family': o.family ?? SANS, 'font-size': (o.size ?? 15) + 'px', 'line-height': (o.lh ?? 24) + 'px',
    'font-weight': o.weight ?? 'normal', 'font-style': o.italic ? 'italic' : '', color: o.color ?? C.ink, 'letter-spacing': o.ls ?? '',
    'text-transform': o.upper ? 'uppercase' : '', 'mso-line-height-rule': 'exactly', 'border-top': o.borderTop ?? '', 'padding-top': o.padTop ?? '',
  })}">${html}</p>`;
}

/** Section heading (editorial serif). */
export function h2(text, o = {}) {
  return `<h2 style="${style({ margin: o.margin ?? '34px 0 10px', 'font-family': SERIF, 'font-size': (o.size ?? 22) + 'px', 'line-height': (o.lh ?? 27) + 'px', 'font-weight': 'normal', color: C.ink, 'mso-line-height-rule': 'exactly' })}">${esc(text)}</h2>`;
}

/** Small letter-spaced caps label. */
export function label(text, o = {}) {
  return p(esc(text), { size: 11, lh: 16, weight: 'bold', ls: '.14em', upper: true, color: o.color ?? C.muted, margin: o.margin ?? '0 0 6px' });
}

/** Result badge as a table cell (Outlook keeps the colour and padding; rounded corners degrade to square there). */
export function badge(text, lv) {
  const [bg, fg] = TIER[lv] || TIER.potential;
  return `<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="display:inline-table;vertical-align:middle"><tr><td bgcolor="${bg}" style="background-color:${bg};border-radius:999px;padding:4px 10px;font-family:${SANS};font-size:11px;line-height:13px;font-weight:bold;letter-spacing:.08em;color:${fg};mso-line-height-rule:exactly;white-space:nowrap">${esc(String(text).toUpperCase())}</td></tr></table>`;
}

/** Bulletproof button: VML rounded rectangle for Outlook on Windows, a padded link inside a coloured cell elsewhere. */
export function button(href, text, o = {}) {
  const bg = o.bg ?? C.accent, width = o.width ?? 320, h = o.height ?? 46;
  const safe = esc(href);
  return `<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:${o.margin ?? '22px 0 6px'}"><tr><td>
<!--[if mso]><v:roundrect href="${safe}" style="height:${h}px;v-text-anchor:middle;width:${width}px" arcsize="0%" stroke="f" fillcolor="${bg}"><w:anchorlock/><center style="color:#ffffff;font-family:${SANS};font-size:14px;font-weight:bold">${esc(text)}</center></v:roundrect><![endif]-->
<!--[if !mso]><!--><table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr><td bgcolor="${bg}" style="background-color:${bg}"><a href="${safe}" target="_blank" style="display:inline-block;padding:14px 22px;font-family:${SANS};font-size:14px;line-height:18px;font-weight:bold;color:#ffffff;text-decoration:none;mso-line-height-rule:exactly">${esc(text)}</a></td></tr></table><!--<![endif]-->
</td></tr></table>`;
}

/** Thin divider row. */
export const rule = (margin = '26px 0 0') => `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:${margin}"><tr><td style="border-top:1px solid ${C.line};font-size:0;line-height:0;height:1px">&nbsp;</td></tr></table>`;
