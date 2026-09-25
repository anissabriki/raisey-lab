#!/usr/bin/env python3
"""Generates the Insights section from content/insights.md with index.html's design tokens, header and footer
(same approach as build_legal.py: the CSP only allows inline CSS, so each page carries the shared base CSS).

    python3 build_insights.py

Writes insights/index.html (listing) and insights/<slug>/index.html (one per article).
Copy is rendered exactly as written in content/insights.md; only typographic quotes/apostrophes are applied.
Reading time = words / 220, rounded up, computed here and hard-coded in the pages.
Canonical, og:url and JSON-LD use siteUrl from site.config.json (or env SITE_URL) when it is set.
"""
import html, json, math, os, re, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
cfg = json.load(open(os.environ.get('SITE_CONFIG', 'site.config.json'), encoding='utf-8'))
SITE = ((os.environ.get('SITE_URL', '') or '').strip() or (cfg.get('siteUrl') or '').strip()).rstrip('/')
BASE = (os.environ.get('BASE_PATH', '') or '').strip() or (cfg.get('basePath') or '/')
ROOT_URL = (SITE + BASE) if SITE else BASE          # absolute once the domain is set; root-relative until then
WPM = 220
NEWSLETTER = bool(cfg.get('newsletterEnabled'))            # Insights subscribe form: hidden until a newsletter provider exists
BYLINE = 'Anissa Briki'                            # TODO: confirm the byline name with the client before launch

LISTING = {
    'title': 'Insights — Aesthetic Medicine, Brand & Digital | Raisey Lab',
    'description': 'Essays on aesthetic medicine, beauty culture, consumer behaviour and digital strategy, for aesthetic practices in London, Paris, Dubai and beyond.',
    'h1': 'Notes from inside aesthetic medicine.',
    'lead': 'Raisey Lab Insights: essays on aesthetic medicine, beauty culture, consumer behaviour and digital strategy — for practices in London, Paris, Dubai and beyond.',
    'featured': '02',
    'next_no': '05', 'next_title': 'A Good Doctor Knows When to Say No',
    'subscribe': 'Receive new Insights as they’re published.',
    'thanks': 'Thank you — you’ll receive the next Insight.',
    'explore': 'Or explore how we work with practices',
}

# ---------------------------------------------------------------- shared chrome from index.html (as build_legal.py)
SRC = open('index.html', encoding='utf-8').read()
CSS_ALL = SRC[SRC.index('<style>') + 7:SRC.index('</style>')]
CSS_BASE = CSS_ALL[CSS_ALL.index('/* ============ FONTS'):CSS_ALL.index('/* ============ 01 HERO')]
CSS_FOOT = CSS_ALL[CSS_ALL.index('.site-footer{'):]
FORM_CSS = '\n'.join(l for l in CSS_ALL.splitlines() if re.match(r'\.(input|field)\b[^{]*\{', l) and 'fp-' not in l)
SPRITE = ''   # the old circular symbol is deprecated; no SVG sprite
ICONS = ''    # no favicon until the official & monogram files are supplied

CSS = '''
/* Insights */
.ins{padding-block:clamp(40px,6vw,88px) clamp(56px,8vw,112px)}
.ins .wrap{max-width:1080px}
.crumbs{font:600 12px/1.4 var(--sans);letter-spacing:.16em;text-transform:uppercase;color:var(--muted);margin-bottom:clamp(20px,3.4vw,40px)}
.crumbs ol{display:flex;flex-wrap:wrap;gap:0 10px;list-style:none;padding:0;margin:0}
.crumbs li+li::before{content:"/";margin-right:10px;color:var(--muted)}
.crumbs a{color:var(--muted);text-decoration:none;display:inline-flex;min-height:44px;align-items:center}
.crumbs a:hover,.crumbs a:focus-visible{color:var(--rasp)}
.crumbs [aria-current]{display:inline-flex;min-height:44px;align-items:center;color:var(--ink)}
.ins-label{font:600 12px/1.4 var(--sans);letter-spacing:.18em;text-transform:uppercase;color:var(--p-red-ink)}
.ins-num{display:block;font-family:var(--serif);font-weight:400;line-height:.9;color:var(--muted);font-variant-numeric:lining-nums}
.ins-meta{font-size:14px;color:var(--muted)}
.ins-hero h1{font-size:clamp(2.4rem,1rem + 4.4vw,4.6rem);line-height:1.03;letter-spacing:-.03em;max-width:13em}
.ins-lead{margin-top:clamp(20px,3vw,32px);max-width:40em;font-size:clamp(1.05rem,.98rem + .35vw,1.3rem);line-height:1.6;color:var(--ink)}
.ins-feat{position:relative;margin-top:clamp(48px,7vw,96px);padding-block:clamp(32px,4.4vw,56px);border-top:1px solid var(--line-strong);display:grid;gap:14px 48px}
@media (min-width:900px){.ins-feat{grid-template-columns:minmax(0,3fr) minmax(0,9fr)}}
.ins-feat .ins-num{font-size:clamp(4rem,2rem + 6vw,7.5rem)}
.ins-feat h2{font-size:clamp(2rem,1.2rem + 2.6vw,3.4rem);line-height:1.06;letter-spacing:-.025em;margin-top:14px;max-width:17em}
.ins-feat p.ex{margin-top:16px;max-width:40em;color:var(--muted);font-size:clamp(1rem,.96rem + .2vw,1.12rem)}
.ins-feat .ins-meta{margin-top:14px}
.ins-feat .more{display:inline-flex;align-items:center;gap:10px;min-height:44px;margin-top:10px;font:600 14px/1.2 var(--sans);color:var(--ink);border-bottom:1.5px solid currentColor}
.ins-feat h2 a,.ins-row h2 a{color:var(--ink);text-decoration:none;transition:color .3s var(--ease)}
.ins-feat h2 a::after,.ins-row h2 a::after{content:"";position:absolute;inset:0}
.ins-feat h2 a:focus-visible,.ins-row h2 a:focus-visible{outline:none}
.ins-feat:has(a:focus-visible),.ins-row:has(a:focus-visible){outline:2px solid var(--rasp);outline-offset:4px}
.ins-feat:hover h2 a,.ins-feat:focus-within h2 a,.ins-feat:hover .more,.ins-feat:focus-within .more{color:var(--rasp)}
.ins-list{list-style:none;padding:0;margin:0}
.ins-row{position:relative;display:grid;grid-template-columns:clamp(64px,9vw,128px) minmax(0,1fr) 40px;gap:6px clamp(16px,3vw,40px);padding-block:clamp(24px,3.2vw,40px);border-top:1px solid var(--line-strong)}
.ins-row .ins-num{font-size:clamp(2.4rem,1.5rem + 2.4vw,3.6rem)}
.ins-row h2{font-size:clamp(1.45rem,1.1rem + 1.2vw,2.15rem);line-height:1.12;letter-spacing:-.02em;margin-top:8px;max-width:22em}
.ins-row p.ex{margin-top:10px;max-width:44em;color:var(--muted);font-size:16px}
.ins-row .ins-meta{margin-top:10px;font-size:13px}
.ins-row .go{align-self:center;justify-self:end;display:inline-flex;color:var(--rasp);opacity:0;transform:translateX(-12px);transition:opacity .3s var(--ease),transform .3s var(--ease)}
.ins-row:hover h2 a,.ins-row:focus-within h2 a{color:var(--rasp)}
.ins-row:hover .go,.ins-row:focus-within .go{opacity:1;transform:none}
@media (max-width:699px){.ins-row{grid-template-columns:minmax(0,1fr)}.ins-row .go{display:none}.ins-row .ins-num{margin-bottom:10px}}
.ins-next{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 18px;padding-block:clamp(22px,2.8vw,32px);border-top:1px dashed var(--line-strong);color:var(--muted)}
.ins-next .ins-label{color:var(--muted)}
.ins-next .t{font-family:var(--serif);font-size:clamp(1.2rem,1rem + .7vw,1.55rem);line-height:1.2;color:var(--muted)}
.ins-sub{margin-top:clamp(56px,7vw,96px);padding-top:clamp(28px,3.4vw,40px);border-top:1px solid var(--line-strong);max-width:680px}
.ins-sub .l{font-family:var(--serif);font-size:clamp(1.3rem,1.05rem + .8vw,1.75rem);line-height:1.25;color:var(--ink)}
.ins-sub .row{display:flex;flex-wrap:wrap;gap:12px;margin-top:18px}
.ins-sub .input{flex:1 1 260px;width:auto}
.ins-sub .status{margin-top:12px;font-size:14px;color:var(--muted);min-height:1.4em}
.ins-sub .status[data-s=error]{color:var(--err,#a3243b)}
.ins-sub .done{font-family:var(--serif);font-size:clamp(1.15rem,1rem + .5vw,1.4rem);color:var(--ink);margin-top:18px}
.ins-sub .priv{margin-top:6px;font-size:13px;color:var(--muted)}
.ins-sub .priv a{color:var(--muted)}
.ins-explore{display:inline-flex;align-items:center;gap:8px;min-height:44px;margin-top:18px;font-size:14px;color:var(--muted);text-underline-offset:.3em}
.ins-explore:hover,.ins-explore:focus-visible{color:var(--rasp)}
.ins-explore-row{margin-top:clamp(40px,5vw,64px)}
.ins .btn,.art-end .btn{--b:var(--p-burgundy);--f:var(--optical);border-color:var(--p-burgundy)}
.art-end .btn{min-height:64px;padding:20px 36px;font-size:16px;gap:18px}
.art-head{max-width:900px}
.art-head .ins-label{display:block}
.art-head h1{font-size:clamp(2.2rem,1rem + 3.6vw,3.9rem);line-height:1.05;letter-spacing:-.028em;margin-top:16px}
.art-stand{margin-top:clamp(18px,2.6vw,28px);max-width:36em;font-size:clamp(1.15rem,1rem + .5vw,1.45rem);line-height:1.55;color:var(--ink)}
.art-head .ins-meta{margin-top:18px}
.art-fig{max-width:560px;margin:clamp(32px,4vw,48px) 0 0}
.art-fig img{display:block;width:100%;height:auto;aspect-ratio:2/3;background:var(--blush)}
.art-body{max-width:680px;margin-top:clamp(40px,5vw,64px);font-size:clamp(17px,1rem + .2vw,19px);line-height:1.7;color:var(--ink)}
.art-body>*+*{margin-top:1.15em}
.art-body h2{font-size:clamp(1.5rem,1.15rem + 1vw,2rem);line-height:1.16;letter-spacing:-.02em;margin-top:2.2em}
.art-body h2+*{margin-top:.75em}
.art-body blockquote{margin-block:1.9em;padding-left:clamp(18px,2.4vw,28px);border-left:1.5px solid var(--p-red);font-family:var(--serif);font-style:italic;font-size:clamp(1.35rem,1.1rem + .9vw,1.8rem);line-height:1.35;color:var(--p-red-ink)}
.art-body a{color:var(--ink);text-decoration-line:underline;text-decoration-thickness:1px;text-decoration-color:var(--muted);text-underline-offset:.22em;transition:color .2s}
.art-body a:hover,.art-body a:focus-visible{color:var(--rasp);text-decoration-color:var(--rasp)}
.art-src{max-width:680px;margin-top:clamp(40px,5vw,56px);padding-top:20px;border-top:1px solid var(--line);font-size:14px;line-height:1.6;color:var(--muted)}
.art-src h2{font:600 12px/1.4 var(--sans);letter-spacing:.18em;text-transform:uppercase;color:var(--muted)}
.art-src ul{list-style:none;padding:0;margin-top:10px;display:grid;gap:8px}
.art-src a{color:var(--muted);text-underline-offset:.2em}
.art-src a:hover,.art-src a:focus-visible{color:var(--rasp)}
.art-end{max-width:680px;margin-top:clamp(40px,5vw,64px);padding-top:clamp(28px,3.4vw,40px);border-top:1px solid var(--line-strong)}
.art-end .q{font-family:var(--serif);font-size:clamp(1.3rem,1.05rem + .8vw,1.75rem);line-height:1.25;margin-bottom:20px}
.art-end .tl{font-size:15px}
.art-end .soon{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 16px}
.art-end .soon .t{font-family:var(--serif);font-size:clamp(1.3rem,1.05rem + .8vw,1.75rem);line-height:1.2}
.art-end .sub{margin-top:20px;font-size:15px;color:var(--muted)}
.art-end .sub a{color:var(--muted);text-underline-offset:.3em;white-space:nowrap}
.art-end .sub a:hover,.art-end .sub a:focus-visible{color:var(--rasp)}
.art-pn{max-width:900px;margin-top:clamp(48px,6vw,80px);border-top:1px solid var(--line-strong);display:grid;gap:0 32px}
@media (min-width:700px){.art-pn{grid-template-columns:1fr 1fr}}
.art-pn>*{display:block;padding-block:20px;text-decoration:none;color:var(--ink)}
.art-pn .d{display:block;font:600 12px/1.4 var(--sans);letter-spacing:.16em;text-transform:uppercase;color:var(--muted);margin-bottom:6px}
.art-pn .t{font-family:var(--serif);font-size:clamp(1.15rem,1rem + .5vw,1.4rem);line-height:1.2;transition:color .3s var(--ease)}
.art-pn a:hover .t,.art-pn a:focus-visible .t{color:var(--rasp)}
.art-pn .nx{text-align:right}
@media (max-width:699px){.art-pn .nx{text-align:left;border-top:1px solid var(--line)}}
.art-pn .soon,.art-pn .soon .t{color:var(--muted)}
.art-back{display:inline-flex;align-items:center;min-height:44px;margin-top:12px;font:600 14px/1.2 var(--sans);color:var(--ink);text-underline-offset:.3em}
.art-back:hover,.art-back:focus-visible{color:var(--rasp)}
@media (prefers-reduced-motion:reduce){.ins-row .go,.ins-feat h2 a,.ins-row h2 a,.art-pn .t{transition:none}.ins-row .go{transform:none}}
'''


# ---------------------------------------------------------------- content parsing
def smart(s):
    """Typographic quotes/apostrophes (the site's convention); URLs are never touched."""
    urls = []
    s = re.sub(r'\]\([^)]*\)', lambda m: urls.append(m.group(0)) or ']\x00%d\x00' % (len(urls) - 1), s)
    s = re.sub(r'(^|[\s(\[—–])"', r'\1“', s).replace('"', '”')
    s = re.sub(r"(\w|[.,!?’”*\x00])'", r'\1’', s).replace("'", '‘')
    return re.sub(r'\]\x00(\d+)\x00', lambda m: urls[int(m.group(1))], s)


def inline(s, link):
    s = html.escape(smart(s), quote=False)
    s = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', lambda m: '<a href="%s">%s</a>' % (link(m.group(2)), m.group(1)), s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    return re.sub(r'(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])', r'<em>\1</em>', s)


def parse():
    txt = re.sub(r'<!--.*?-->', '', open('content/insights.md', encoding='utf-8').read(), flags=re.S)
    arts = []
    for no, chunk in re.findall(r'^## Article (\d+)\n(.*?)(?=^## Article |\Z)', txt, re.S | re.M):
        meta = {k.strip().lower(): v.strip().strip('`') for k, v in re.findall(r'^- \*\*([^*]+):\*\* (.+)$', chunk, re.M)}
        a = {'no': no.zfill(2), 'slug': meta['slug'], 'theme': meta['theme'], 'short': meta['short title (breadcrumb)'],
             'seo_title': meta['seo title'], 'description': meta['meta description'],
             'excerpt': meta.get('excerpt (listing and featured)') or meta['excerpt (listing)'],
             'title': re.search(r'^\*\*Title:\*\* (.+)$', chunk, re.M).group(1).strip(),
             'standfirst': re.search(r'^\*\*Standfirst:\*\* (.+)$', chunk, re.M).group(1).strip()}
        body = chunk[chunk.index('**Standfirst:**'):].split('\n', 1)[1]
        body, _, rest = body.partition('\n*CTA:*')
        a['cta'] = rest.split('\n', 1)[0].strip()
        src = re.search(r'^\*\*Sources\*\*\n(.*?)(?:\n---|\Z)', rest, re.S | re.M)
        a['sources'] = re.findall(r'^- (.+)$', src.group(1), re.M) if src else []
        a['blocks'] = [b.strip() for b in re.split(r'\n\s*\n', body.strip().rstrip('-').strip()) if b.strip()]
        words = ' '.join([a['standfirst']] + a['blocks'])
        a['words'] = len(re.findall(r"[\w’'-]+", re.sub(r'\]\([^)]*\)|[#>*\[]', ' ', words)))
        a['minutes'] = math.ceil(a['words'] / WPM)
        arts.append(a)
    return arts


# ---------------------------------------------------------------- page chrome
def shell(depth, title, desc, url_path, og_type, body, ld, script=''):
    up = '../' * depth
    home = up + 'index.html'
    nav = [('#studio', 'Studio'), ('#raisey-scan', 'Raisey Scan'), ('#services', 'Services'), ('#work', 'Work'), ('#about', 'About')]
    ins = up + 'insights/index.html'
    nav_html = ''.join('<li><a href="%s%s">%s</a></li>' % (home, h, t) for h, t in nav) + \
        '<li><a class="on" href="%s" aria-current="%s">Insights</a></li>' % (ins, 'page' if url_path == 'insights/' else 'true')
    mob_html = nav_html.replace('<li><a href', '<li><a class="l" href').replace('<li><a class="on"', '<li><a class="l on"')
    foot = ''.join('<li><a href="%s%s">%s</a></li>' % (home, h, t) for h, t in nav) + \
        '<li><a href="%s">Insights</a></li><li><a href="%s#contact">Contact</a></li>' % (ins, home)
    sw = ('<div class="langsw h" role="group" aria-label="Language"><span aria-current="true" lang="en">EN</span><i aria-hidden="true"></i>'
          '<a href="%sfr/index.html" hreflang="fr" lang="fr" aria-label="Français">FR</a></div>' % up)
    url = ROOT_URL + url_path
    seo = ('<link rel="canonical" href="%s">\n<meta property="og:url" content="%s">\n' % (url, url)) if SITE else \
        '<!-- canonical + og:url: generated from SITE_URL (site.config.json -> siteUrl) once the domain is set -->\n'
    css = (CSS_BASE + CSS_FOOT + '\n' + FORM_CSS + CSS).replace('url(fonts/', 'url(%sfonts/' % up)
    return '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<meta name="theme-color" content="#f3eee6">
%(seo)s<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:type" content="%(ogt)s">
<meta property="og:site_name" content="Raisey Lab">
<meta property="og:locale" content="en_GB">
%(icons)s
<link rel="preload" href="%(up)sfonts/fraunces-latin-opsz-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="%(up)sfonts/inter-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<style>
%(css)s
</style>
<script type="application/ld+json">
%(ld)s
</script>
</head>
<body>
%(sprite)s
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap bar">
    <a class="brand" href="%(home)s#studio" aria-label="Raisey Lab">Raisey Lab</a>
    <nav class="nav" aria-label="Main"><ul>%(nav)s</ul></nav>
    <div style="display:flex;align-items:center;gap:16px">%(sw)s<a class="btn head-cta" href="%(home)s#raisey-scan">Start your Scan <i class="ar"></i></a>
      <button class="menu-btn" type="button" aria-expanded="false" aria-controls="mobile-nav"><span class="mt">Menu</span><svg viewBox="0 0 20 12" width="20" height="12" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path class="l1" d="M1 2h18"/><path class="l2" d="M1 10h18"/></svg></button>
    </div>
  </div>
  <div class="mobile" id="mobile-nav" hidden><div class="wrap"><ul>%(mob)s</ul>%(swm)s<a class="btn" href="%(home)s#raisey-scan">Start your Scan <i class="ar"></i></a></div></div>
</header>
<main id="main" class="ins"><div class="wrap">
%(body)s
</div></main>
<footer class="site-footer"><div class="wrap">
  <div class="f-row"><a class="brand" href="%(home)s#studio" style="font-size:20px">Raisey Lab</a>
  <nav aria-label="Footer"><ul>%(foot)s</ul></nav></div>
  <p class="f-legal"><a class="lg" href="%(up)sprivacy.html">Privacy Policy</a><a class="lg" href="%(up)sprivacy.html#legal-notice">Legal notice</a><span>Paris · London · Dubai · Expertise, elevated. © <span id="yr">2026</span> Raisey Lab. All rights reserved.</span></p>
</div></footer>
<script>
(function(){const mb=document.querySelector('.menu-btn'),mp=document.getElementById('mobile-nav');
document.getElementById('yr').textContent=new Date().getFullYear();
const set=o=>{mb.setAttribute('aria-expanded',String(o));mb.querySelector('.mt').textContent=o?'Close':'Menu';mp.hidden=!o};
mb.addEventListener('click',()=>set(mb.getAttribute('aria-expanded')!=='true'));
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!mp.hidden){set(false);mb.focus()}});
mp.addEventListener('click',e=>{if(e.target.closest('a'))set(false)});
matchMedia('(min-width:1001px)').addEventListener('change',m=>{if(m.matches)set(false)});})();
</script>%(script)s
</body>
</html>
''' % dict(title=html.escape(title), desc=html.escape(desc), seo=seo, ogt=og_type, icons=ICONS.replace('href="', 'href="' + up), up=up, css=css,
           ld=json.dumps(ld, ensure_ascii=False, indent=1).replace('</', '<\\/'), sprite=SPRITE, home=home, nav=nav_html, sw=sw,
           swm=sw.replace('langsw h', 'langsw m'), mob=mob_html, body=body, foot=foot, script=script)


def crumbs(items):
    lis = ''.join(('<li><a href="%s">%s</a></li>' % (h, html.escape(t))) if h else '<li><span aria-current="page">%s</span></li>' % html.escape(t) for h, t in items)
    return '<nav class="crumbs" aria-label="Breadcrumb"><ol>%s</ol></nav>' % lis


def breadcrumb_ld(items):
    return {'@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': i, 'name': n, 'item': ROOT_URL + p}
                                                           for i, (p, n) in enumerate(items, 1)]}


def ld_graph(*nodes):
    return {'@context': 'https://schema.org', '@graph': list(nodes)}


PUBLISHER = {'@type': 'Organization', 'name': 'Raisey Lab', 'url': ROOT_URL}


# ---------------------------------------------------------------- pages
# Secondary, editorial founder portrait (final approved asset): shown whole (2:3) in the founder's own essay.
FOUNDER_FIG = ('<figure class="art-fig"><picture><source type="image/webp" srcset="../../images/founder-story-480.webp 480w, '
               '../../images/founder-story-768.webp 768w, ../../images/founder-story-1024.webp 1024w" sizes="(max-width:600px) calc(100vw - 40px), 560px">'
               '<img src="../../images/founder-story-768.jpg" alt="Anissa Sabrina Briki, founder of Raisey Lab, seated on a cream sofa: editorial portrait with the Raisey Lab signature" '
               'decoding="async" width="1024" height="1536"></picture></figure>\n')

def article(a, arts):
    i = arts.index(a)
    link = lambda u: ('../%s/index.html' % u.split('/insights/')[1].strip('/')) if u.startswith('/insights/') else u
    blocks = []
    for b in a['blocks']:
        if b.startswith('#### '):
            blocks.append('<h2>%s</h2>' % inline(b[5:], link))
        elif b.startswith('> '):
            blocks.append('<blockquote><p>%s</p></blockquote>' % inline(' '.join(l[2:] if l.startswith('> ') else l for l in b.splitlines()), link))
        else:
            blocks.append('<p>%s</p>' % inline(' '.join(b.splitlines()), link))
    home = '../../index.html'
    no = int(a['no'])
    if no == 1:
        end = '<p><a class="tl" href="%s#services">Explore our approach <i class="ar"></i></a></p>' % home
    elif no == 2:
        end = ('<p class="q">Understand your patient journey.</p>'
               '<a class="btn" href="%s#contact" data-interest="presence-review">Request a Raisey Lab Review <i class="ar"></i></a>' % home)
    elif no == 3:
        end = ('<p class="q">Growing your practice across markets?</p>'
               '<p><a class="tl" href="%s#services">Discover Brand &amp; Digital Strategy <i class="ar"></i></a></p>' % home)
    else:
        end = ('<div class="soon"><span class="ins-label">%s · Coming next</span><span class="t">%s</span></div>'
               '<p class="sub">What does your digital presence say about your philosophy? <a href="%s#contact">Request a Raisey Lab Review <span aria-hidden="true">→</span></a></p>'
               % (LISTING['next_no'], html.escape(LISTING['next_title']), home))
    prev = arts[i - 1] if i else None
    nxt = arts[i + 1] if i + 1 < len(arts) else None
    pn = ''
    pn += ('<a class="pv" href="../%s/index.html"><span class="d">← Previous · %s</span><span class="t">%s</span></a>' % (prev['slug'], prev['no'], html.escape(smart(prev['title'])))) if prev else '<span aria-hidden="true"></span>'
    pn += ('<a class="nx" href="../%s/index.html"><span class="d">Next · %s →</span><span class="t">%s</span></a>' % (nxt['slug'], nxt['no'], html.escape(smart(nxt['title'])))) if nxt else \
        '<div class="nx soon"><span class="d">Next · %s · Coming next</span><span class="t">%s</span></div>' % (LISTING['next_no'], html.escape(LISTING['next_title']))
    src = ''
    if a['sources']:
        src = '<section class="art-src" aria-labelledby="src-h"><h2 id="src-h">Sources</h2><ul>%s</ul></section>' % ''.join('<li>%s</li>' % inline(s, link) for s in a['sources'])
    path = 'insights/%s/' % a['slug']
    body = '''%s
<article data-article="%s">
<header class="art-head">
<p class="ins-label">Insight %s · %s</p>
<h1>%s</h1>
<p class="art-stand">%s</p>
<!-- TODO: publication date (not displayed until set) -->
<p class="ins-meta">By %s, Founder · %d min read</p><!-- TODO: confirm the byline name with the client before launch -->
</header>
%s<div class="art-body">
%s
</div>
%s
<div class="art-end">%s</div>
</article>
<nav class="art-pn" aria-label="Insights series">%s</nav>
<a class="art-back" href="../index.html">← All Insights</a>''' % (
        crumbs([(home, 'Home'), ('../index.html', 'Insights'), (None, a['short'])]), a['slug'], a['no'], html.escape(a['theme']),
        html.escape(smart(a['title'])), html.escape(smart(a['standfirst'])), BYLINE, a['minutes'], FOUNDER_FIG if a['slug'] == 'why-i-created-raisey-lab' else '', '\n'.join(blocks), src, end, pn)
    url = ROOT_URL + path
    ld = ld_graph({'@type': 'Article', 'headline': smart(a['title']), 'description': a['description'],
                   'author': {'@type': 'Person', 'name': BYLINE, 'jobTitle': 'Founder'}, 'publisher': PUBLISHER,
                   'mainEntityOfPage': {'@type': 'WebPage', '@id': url}, 'inLanguage': 'en', 'wordCount': a['words']},
                  breadcrumb_ld([('', 'Home'), ('insights/', 'Insights'), (path, a['short'])]))
    return path, shell(2, a['seo_title'], a['description'], path, 'article', body, ld)


def listing(arts):
    f = next(a for a in arts if a['no'] == LISTING['featured'])
    feat = '''<section class="ins-feat" aria-labelledby="feat-h">
<span class="ins-num" aria-hidden="true">%s</span>
<div><p class="ins-label">%s</p>
<h2 id="feat-h"><a href="%s/index.html">%s</a></h2>
<p class="ex">%s</p>
<p class="ins-meta">%d min read</p>
<span class="more" aria-hidden="true">Read the Insight <i class="ar"></i></span></div>
</section>''' % (f['no'], html.escape(f['theme']), f['slug'], html.escape(smart(f['title'])), html.escape(smart(f['excerpt'])), f['minutes'])
    rows = ''.join('''<li class="ins-row"><span class="ins-num" aria-hidden="true">%s</span><div><p class="ins-label">%s</p>
<h2><a href="%s/index.html"><span class="sr-only">%s. </span>%s</a></h2><p class="ex">%s</p><p class="ins-meta">%d min read</p></div><span class="go" aria-hidden="true"><i class="ar"></i></span></li>
''' % (a['no'], html.escape(a['theme']), a['slug'], a['no'], html.escape(smart(a['title'])), html.escape(smart(a['excerpt'])), a['minutes']) for a in arts)
    subscribe = ('<section class="ins-sub" aria-labelledby="sub-h">\n<p class="l" id="sub-h">%s</p>\n<form id="ins-subscribe" novalidate>\n<div class="row"><label class="sr-only" for="sub-email">Email address</label><input class="input" id="sub-email" name="email" type="email" autocomplete="email" placeholder="you@clinic.com" required>\n<button class="btn" type="submit">Subscribe</button></div>\n<p class="status" role="status" aria-live="polite"></p>\n<p class="priv"><a href="../privacy.html">Privacy Policy</a></p>\n</form>\n<p class="done" hidden tabindex="-1">%s</p>\n<a class="ins-explore" href="../index.html#services">%s <span aria-hidden="true">→</span></a>\n</section>' % (LISTING['subscribe'], LISTING['thanks'], LISTING['explore'])) if NEWSLETTER else ('<p class="ins-explore-row"><a class="ins-explore" href="../index.html#services">%s <span aria-hidden="true">→</span></a></p>' % LISTING['explore'])
    body = '''%s
<header class="ins-hero"><h1>%s</h1><p class="ins-lead">%s</p></header>
%s
<section class="ins-series" aria-label="The series" style="margin-top:clamp(48px,6vw,80px)">
<ol class="ins-list">
%s</ol>
<p class="ins-next"><span class="ins-label">%s · Coming next</span><span class="t">%s</span></p>
</section>
%s''' % (crumbs([('../index.html', 'Home'), (None, 'Insights')]), LISTING['h1'], html.escape(LISTING['lead']), feat, rows,
                   LISTING['next_no'], html.escape(LISTING['next_title']), subscribe)
    script = '''
<script>
(function(){
'use strict';
// Same form service as the contact form: build_site.py injects the public endpoint at build time.
// TODO: connect to email provider (the endpoint must add "insights-subscribe" submissions to the Insights mailing list)
const FORM_ENDPOINT = '';
const DEV = ['localhost','127.0.0.1',''].includes(location.hostname) || location.protocol === 'file:';
const f=document.getElementById('ins-subscribe'), i=document.getElementById('sub-email'), st=f.querySelector('.status'), done=f.nextElementSibling, b=f.querySelector('button');
f.addEventListener('submit',async e=>{
  e.preventDefault(); st.textContent=''; st.dataset.s='';
  if(!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(i.value.trim())){st.dataset.s='error';st.textContent='Please enter a valid email address.';i.setAttribute('aria-invalid','true');i.focus();return}
  i.removeAttribute('aria-invalid');
  if(!FORM_ENDPOINT){st.dataset.s='error';st.textContent=DEV?'This form is not connected to an email provider yet, so nothing was sent. (Set FORM_ENDPOINT before launch.)':'Subscription is not available yet. Please try again later.';return}
  b.disabled=true;
  try{
    const r=await fetch(FORM_ENDPOINT,{method:'POST',headers:{'Content-Type':'application/json',Accept:'application/json'},body:JSON.stringify({source:'insights-subscribe',email:i.value.trim(),lang:'en',sentAt:new Date().toISOString()})});
    if(!r.ok) throw new Error('send-failed');
    f.hidden=true; done.hidden=false; done.focus();
  }catch(err){st.dataset.s='error';st.textContent='We couldn’t subscribe you. Please try again in a moment.';b.disabled=false}
});
})();
</script>'''
    url = ROOT_URL + 'insights/'
    ld = ld_graph({'@type': 'CollectionPage', '@id': url, 'url': url, 'name': LISTING['title'], 'description': LISTING['description'],
                   'inLanguage': 'en', 'publisher': PUBLISHER,
                   'mainEntity': {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': n, 'url': ROOT_URL + 'insights/%s/' % a['slug'],
                                                                           'name': smart(a['title'])} for n, a in enumerate(arts, 1)]}},
                  breadcrumb_ld([('', 'Home'), ('insights/', 'Insights')]))
    return 'insights/', shell(1, LISTING['title'], LISTING['description'], 'insights/', 'website', body, ld, script if NEWSLETTER else '')


def build():
    arts = parse()
    shutil.rmtree('insights', ignore_errors=True)
    pages = [listing(arts)] + [article(a, arts) for a in arts]
    for path, h in pages:
        os.makedirs(path, exist_ok=True)
        open(os.path.join(path, 'index.html'), 'w', encoding='utf-8').write(h)
    return [p for p, _ in pages], arts


if __name__ == '__main__':
    paths, arts = build()
    for a in arts:
        print('%s  %-45s %4d words  %d min' % (a['no'], a['slug'], a['words'], a['minutes']))
    print('written:', ', '.join(p + 'index.html' for p in paths))
