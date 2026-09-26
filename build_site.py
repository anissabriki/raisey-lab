#!/usr/bin/env python3
"""Builds the deployable site into ./dist for GitHub Pages. Python 3 standard library only.

    python3 build_site.py                 # preview build: warns about anything missing
    python3 build_site.py --production    # release build: FAILS while launch requirements are missing

Inputs (all PUBLIC, never secrets):
    site.config.json                      committed settings (legal entity, address, siteUrl, ...)
    env FORM_ENDPOINT, CONTACT_EMAIL, SITE_URL, BASE_PATH, SITE_CONFIG   optional overrides (GitHub Actions *variables*)

What it does: regenerates French + legal pages from the English source, copies ONLY publishable files into dist/,
injects the form endpoint, adds a Content-Security-Policy + referrer meta (GitHub Pages cannot send HTTP headers),
canonical/hreflang (clean URLs: EN /  FR /fr/), robots.txt, sitemap.xml, CNAME, .nojekyll; conservative JSON-LD when siteUrl is set;
then runs safety gates (locked section, broken or case-mismatched links, secret patterns, localhost references, canonical/hreflang
reciprocity, noindex on legal pages, sitemap content, launch requirements).
The approved design is never touched: dist HTML differs from the source only by the injected values above.
"""
import glob
import html
import json, os, re, shutil, subprocess, sys
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
PROD = '--production' in sys.argv
# Preview deployment (e.g. https://<user>.github.io/<repo>/): same production build, but never indexed, no custom-domain
# CNAME, and forms may be unconnected. Set PREVIEW_DEPLOY=1 (GitHub repository variable) — remove it for the real launch.
PREVIEW = os.environ.get('PREVIEW_DEPLOY', '').strip() == '1'
CFG_PATH = os.environ.get('SITE_CONFIG', 'site.config.json')
cfg = json.load(open(CFG_PATH, encoding='utf-8'))


def get(key, env):
    return (os.environ.get(env, '') or '').strip() or (cfg.get(key) or '').strip()


form = get('formEndpoint', 'FORM_ENDPOINT')
email = get('contactEmail', 'CONTACT_EMAIL')
site = get('siteUrl', 'SITE_URL').rstrip('/')
base = (get('basePath', 'BASE_PATH') or '/')
domain = (cfg.get('customDomain') or '').strip()
errors, warnings = [], []


def need(ok, msg):
    (errors if PROD else warnings).append(msg) if not ok else None


# ---------------------------------------------------------------- 1. regenerate derived pages
env = dict(os.environ, SITE_CONFIG=CFG_PATH)
for script in ('build_fr.py', 'build_legal.py', 'build_insights.py'):
    r = subprocess.run([sys.executable, script], env=env, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit('FAILED: %s\n%s%s' % (script, r.stdout, r.stderr))

lock = subprocess.run([sys.executable, '_locked/verify.py'], capture_output=True, text=True)
if lock.returncode != 0:
    sys.exit('FAILED: the locked services section was modified.\n' + lock.stdout)

# ---------------------------------------------------------------- 2. launch requirements
if PREVIEW and not form:
    warnings.append('PREVIEW: FORM_ENDPOINT not set, forms will show their error message')
else:
    need(bool(form) and form.startswith('https://'), 'FORM_ENDPOINT missing or not https:// (forms cannot deliver leads)')
need(bool(email) and '@' in email, 'contactEmail missing (shown in privacy policy + form fallback)')
for k, label in (('legalName', 'legal entity name'), ('postalAddress', 'postal address')):
    need(bool((cfg.get(k) or '').strip()), k + ' missing in site.config.json (' + label + ', required on the legal pages)')
need(bool((cfg.get('emailProvider') or '').strip()), 'emailProvider missing in site.config.json (the service that sends the Scan results email must be named in the privacy policy)')
need(site.startswith('https://'), 'siteUrl missing or not https:// (needed for canonical/hreflang/sitemap)')
if base != '/':
    need(base.startswith('/') and base.endswith('/'), 'basePath must start and end with "/" (e.g. "/repo-name/")')
if form:
    fu = urlparse(form)
    if fu.username or fu.password or re.search(r'(?i)(key|token|secret|apikey|password)=', fu.query):
        errors.append('FORM_ENDPOINT looks like it embeds a secret (credentials/query key). Use a public form URL only.')

# ---------------------------------------------------------------- 3. SEO architecture (clean URLs)
HOME = {'index.html': '', 'fr/index.html': 'fr/'}            # page -> path under the site root (EN = /, FR = /fr/)
LANG = {'index.html': 'en', 'fr/index.html': 'fr'}
LEGAL = ['privacy.html', 'fr/confidentialite.html']          # noindex,follow, never in the sitemap, no canonical/hreflang
INSIGHTS = sorted(os.path.join(d, 'index.html') for d, _, fs in os.walk('insights') if 'index.html' in fs)   # English-only, indexable (build_insights.py)
PAGES = list(HOME) + LEGAL + ['404.html'] + INSIGHTS
ICONS = ['favicon.ico', 'favicon-96.png', 'apple-touch-icon.png', 'icon-192.png']   # official & monogram (from logo1.png)
CITIES = ['Paris', 'London', 'Dubai']                        # markets served, NOT offices (no LocalBusiness / address)
founder = (cfg.get('founderName') or 'Anissa Sabrina Briki').strip()
socials = [u for u in (cfg.get('socialProfiles') or []) if isinstance(u, str) and u.startswith('https://')]
FORBIDDEN_LD = re.compile(r'LocalBusiness|PostalAddress|"address"|aggregateRating|"review"|"Review"|"rating"|"geo"|openingHours|"telephone"|"Offer"|"CaseStudy"|"ratingValue"')


def clean_hrefs(h):
    """Internal links point at directories, not index.html (source keeps index.html so file:// preview works)."""
    return re.sub(r'href="([^"#]*?)index\.html((?:#[^"]*)?)"', lambda m: 'href="%s%s"' % (m.group(1) or './', m.group(2)), h)


def make_jsonld(p, origin, base, h=''):
    root = origin + base
    page = root + HOME[p]
    en = LANG[p] == 'en'
    meta = lambda pat: html.unescape((re.findall(pat, h) or [''])[0])
    org = {'@type': 'Organization', '@id': root + '#organization', 'name': 'Raisey Lab', 'url': root,
           'description': cfg.get('positioning') if en else (cfg.get('positioningFr') or cfg.get('positioning')),
           'logo': {'@type': 'ImageObject', 'url': root + 'icon-192.png', 'width': 192, 'height': 192},
           'image': root + 'images/og.jpg',
           'knowsAbout': cfg.get('knowsAbout') or [],
           'areaServed': [{'@type': 'City', 'name': c} for c in CITIES], 'founder': {'@id': root + '#founder'}}
    if email:
        org['email'] = email
    if socials:
        org['sameAs'] = socials
    person = {'@type': 'Person', '@id': root + '#founder', 'name': founder, 'alternateName': 'Anissa Briki',
              'jobTitle': 'Founder' if en else 'Fondatrice', 'worksFor': {'@id': root + '#organization'},
              'image': root + 'images/founder-about-768.jpg', 'knowsAbout': cfg.get('knowsAbout') or []}
    site_ = {'@type': 'WebSite', '@id': root + '#website', 'url': root, 'name': 'Raisey Lab', 'inLanguage': ['en', 'fr'],
             'publisher': {'@id': root + '#organization'}}
    webpage = {'@type': 'WebPage', '@id': page + '#webpage', 'url': page, 'name': meta(r'<title>(.*?)</title>'),
               'description': meta(r'<meta name="description" content="([^"]*)"'), 'inLanguage': LANG[p],
               'isPartOf': {'@id': root + '#website'}, 'about': {'@id': root + '#organization'},
               'primaryImageOfPage': {'@type': 'ImageObject', 'url': root + 'images/og.jpg'}}
    return {'@context': 'https://schema.org', '@graph': [org, person, site_, webpage]}


def render_seo(p, h, origin, base):
    """Strips the relative source alternates; adds absolute canonical/hreflang/og:url + JSON-LD to indexable pages only."""
    h = re.sub(r'<link rel="alternate" hreflang="[^"]+" href="[^"]+">\n?', '', h)
    if p in HOME and origin:
        root = origin + base
        tags = ('<link rel="canonical" href="%s">\n<link rel="alternate" hreflang="en" href="%s">\n<link rel="alternate" hreflang="fr" href="%s">\n'
                '<link rel="alternate" hreflang="x-default" href="%s">\n<meta property="og:url" content="%s">\n'
                '<meta property="og:site_name" content="Raisey Lab">\n<meta property="og:locale" content="%s">\n<meta property="og:locale:alternate" content="%s">\n') % (
            root + HOME[p], root, root + 'fr/', root, root + HOME[p], 'en_GB' if LANG[p] == 'en' else 'fr_FR', 'fr_FR' if LANG[p] == 'en' else 'en_GB')
        h = h.replace('<link rel="preload"', tags + '<link rel="preload"', 1)
        ld = json.dumps(make_jsonld(p, origin, base, h), ensure_ascii=False, indent=1).replace('</', '<\\/')
        h = h.replace('</head>', '<script type="application/ld+json">\n%s\n</script>\n</head>' % ld, 1)
    # Social preview image (absolute URL) on every page that has Open Graph tags; Twitter/X reads og:* plus the card type.
    if origin and 'property="og:title"' in h and 'og:image' not in h and os.path.exists('images/og.jpg'):
        fr = '<html lang="fr"' in h
        alt = ('Raisey Lab : « You built it. We raise it. » Visibilité, autorité, confiance, croissance.' if fr
               else 'Raisey Lab: “You built it. We raise it.” Visibility, authority, trust, growth.')
        img = ('<meta property="og:image" content="%simages/og.jpg">\n<meta property="og:image:width" content="1200">\n'
               '<meta property="og:image:height" content="630">\n<meta property="og:image:type" content="image/jpeg">\n'
               '<meta property="og:image:alt" content="%s">\n<meta name="twitter:card" content="summary_large_image">\n'
               '<meta name="twitter:image" content="%simages/og.jpg">\n<meta name="twitter:image:alt" content="%s">\n') % (
            origin + base, html.escape(alt), origin + base, html.escape(alt))
        h = h.replace('</head>', img + '</head>', 1)
    return h


def make_sitemap(origin, base, mods):
    root = origin + base
    alts = ('<xhtml:link rel="alternate" hreflang="en" href="%s"/><xhtml:link rel="alternate" hreflang="fr" href="%sfr/"/>'
            '<xhtml:link rel="alternate" hreflang="x-default" href="%s"/>') % (root, root, root)
    urls = ''.join('  <url><loc>%s</loc>%s%s</url>\n' % (root + HOME[p], ('<lastmod>%s</lastmod>' % mods[p]) if mods.get(p) else '', alts) for p in HOME)
    urls += ''.join('  <url><loc>%s</loc>%s</url>\n' % (root + p[:-len('index.html')], ('<lastmod>%s</lastmod>' % mods[p]) if mods.get(p) else '') for p in INSIGHTS)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + urls + '</urlset>\n')


def seo_check(pages, sitemap, origin, base, where):
    """Canonical/hreflang reciprocity, noindex on legal pages, sitemap content. Returns a list of problems."""
    bad, root = [], origin + base
    want = {'en': root, 'fr': root + 'fr/', 'x-default': root}
    for p, sub in HOME.items():
        h, u = pages[p], root + sub
        can = re.findall(r'<link rel="canonical" href="([^"]+)"', h)
        if can != [u]:
            bad.append('%s %s: canonical %s, expected [%s]' % (where, p, can, u))
        alts = re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', h)
        if dict(alts) != want or len(alts) != 3:
            bad.append('%s %s: hreflang set %s does not match %s' % (where, p, alts, want))
        m = re.search(r'<html lang="(\w+)"', h)
        if not m or want.get(m.group(1)) != u:
            bad.append('%s %s: <html lang> does not match its own hreflang/canonical URL' % (where, p))
        if 'noindex' in h:
            bad.append('%s %s: indexable page carries noindex' % (where, p))
        if re.findall(r'<meta property="og:url" content="([^"]+)"', h) != [u]:
            bad.append('%s %s: og:url is not the canonical URL' % (where, p))
        blocks = re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', h, re.S)
        if len(blocks) != 1:
            bad.append('%s %s: expected exactly one JSON-LD block' % (where, p))
        else:
            try:
                ld = json.loads(blocks[0].replace('<\\/', '</'))
                types = sorted(n['@type'] for n in ld['@graph'])
                if types != ['Organization', 'Person', 'WebPage', 'WebSite']:
                    bad.append('%s %s: unexpected JSON-LD types %s' % (where, p, types))
                if FORBIDDEN_LD.search(blocks[0]):
                    bad.append('%s %s: JSON-LD contains a forbidden claim (address, LocalBusiness, rating, review, offer...)' % (where, p))
            except Exception as e:
                bad.append('%s %s: JSON-LD invalid (%s)' % (where, p, e))
    for p in LEGAL + ['404.html']:
        h = pages[p]
        if 'noindex' not in h:
            bad.append('%s %s: must be noindex' % (where, p))
        if re.search(r'<link rel="(canonical|alternate)"', h):
            bad.append('%s %s: noindex page must not carry canonical/hreflang' % (where, p))
    locs = re.findall(r'<loc>([^<]+)</loc>', sitemap)
    if locs != [root, root + 'fr/'] + [root + p[:-len('index.html')] for p in INSIGHTS]:
        bad.append('%s sitemap: URLs %s, expected the two homes + the Insights pages' % (where, locs))
    for p in (INSIGHTS if where != 'selftest' else []):     # Insights (absolute URLs come from build_insights.py): canonical, one H1, valid JSON-LD, indexable
        h, u = pages[p], root + p[:-len('index.html')]
        if re.findall(r'<link rel="canonical" href="([^"]+)"', h) != [u] or re.findall(r'<meta property="og:url" content="([^"]+)"', h) != [u]:
            bad.append('%s %s: canonical/og:url is not %s' % (where, p, u))
        if len(re.findall(r'<h1\b', h)) != 1 or 'noindex' in h:
            bad.append('%s %s: needs exactly one <h1> and no noindex' % (where, p))
        try:
            ld = json.loads(re.search(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', h, re.S).group(1).replace('<\\/', '</'))
            types = sorted(n['@type'] for n in ld['@graph'])
            if types not in (['Article', 'BreadcrumbList'], ['BreadcrumbList', 'CollectionPage']) or root not in json.dumps(ld):
                bad.append('%s %s: unexpected JSON-LD %s' % (where, p, types))
        except Exception as e:
            bad.append('%s %s: JSON-LD invalid (%s)' % (where, p, e))
    if sitemap.count('hreflang="x-default"') != 2 or sitemap.count('hreflang="en"') != 2 or sitemap.count('hreflang="fr"') != 2:
        bad.append('%s sitemap: every URL needs en, fr and x-default alternates' % where)
    if 'privacy' in sitemap or 'confidentialite' in sitemap or '404' in sitemap:
        bad.append('%s sitemap: legal/404 pages must be excluded' % where)
    return bad


def git_date(p):
    try:
        r = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', p], capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else ''
    except OSError:
        return ''


# ---------------------------------------------------------------- 4. assemble dist/
shutil.rmtree('dist', ignore_errors=True)
os.makedirs('dist')
for p in PAGES:
    os.makedirs(os.path.dirname(os.path.join('dist', p)) or 'dist', exist_ok=True)
    shutil.copy(p, os.path.join('dist', p))
for d in ('fonts', 'images'):
    shutil.copytree(d, os.path.join('dist', d))
for f in ICONS:
    if os.path.exists(f):
        shutil.copy(f, os.path.join('dist', f))
    else:
        errors.append('missing icon file ' + f + ' (run python3 make_icons.py)')

form_origin = ''
if form:
    u = urlparse(form)
    form_origin = '%s://%s' % (u.scheme, u.netloc)
csp = ("default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src 'self' data:; font-src 'self'; "
       "connect-src 'self'%s; base-uri 'self'; form-action 'none'" % ((' ' + form_origin) if form_origin else ''))
harden = ('<meta http-equiv="Content-Security-Policy" content="%s">\n<meta name="referrer" content="strict-origin-when-cross-origin">\n' % csp)

built = {}
for p in PAGES:
    path = os.path.join('dist', p)
    h = open(path, encoding='utf-8').read()
    if p == os.path.join('insights', 'index.html') and "const FORM_ENDPOINT = '';" in h:
        h, n0 = re.subn(r"const FORM_ENDPOINT = '';", "const FORM_ENDPOINT = %s;" % json.dumps(form), h)
        if n0 != 1:
            sys.exit('FAILED: could not inject the form endpoint into ' + p)
    if p in HOME:
        h, n1 = re.subn(r"const FORM_ENDPOINT = '';", "const FORM_ENDPOINT = %s;" % json.dumps(form), h)
        h, n2 = re.subn(r"const CONTACT_EMAIL = '';", "const CONTACT_EMAIL = %s;" % json.dumps(email), h)
        if n1 != 1 or n2 != 1:
            sys.exit('FAILED: could not inject form settings into ' + p)
    h = render_seo(p, clean_hrefs(h), site, base)
    # CSP goes right after <meta charset> so it is in force before anything else is parsed
    h = h.replace('<meta charset="utf-8">\n', '<meta charset="utf-8">\n' + harden, 1)
    if 'Content-Security-Policy' not in h:
        sys.exit('FAILED: could not add CSP to ' + p)
    built[p] = h
    if PREVIEW:                                   # keep the preview copy out of search engines
        h = h.replace('<meta charset="utf-8">\n', '<meta charset="utf-8">\n<meta name="robots" content="noindex,nofollow">\n', 1)
    open(path, 'w', encoding='utf-8').write(h)

open('dist/.nojekyll', 'w').close()
if domain and not PREVIEW:                        # a preview must never claim the custom domain
    open('dist/CNAME', 'w').write(domain + '\n')
if site:
    open('dist/robots.txt', 'w').write('User-agent: *\nDisallow: /\n' if PREVIEW else 'User-agent: *\nAllow: /\n\nUser-agent: OAI-SearchBot\nAllow: /\n\nSitemap: %s%ssitemap.xml\n' % (site, base))
    sitemap = make_sitemap(site, base, {p: git_date(p) for p in list(HOME) + INSIGHTS})
    open('dist/sitemap.xml', 'w').write(sitemap)
    errors.extend(seo_check(built, sitemap, site, base, 'dist'))
else:
    warnings.append('no siteUrl: robots.txt, sitemap.xml, canonical, hreflang, og:url and JSON-LD were NOT generated (they need the final domain)')

# The canonical/hreflang/sitemap/JSON-LD logic is verified on EVERY build against a throw-away origin, so it cannot rot before the domain exists.
TEST = 'https://selftest.invalid'
probe = {p: render_seo(p, clean_hrefs(open(p, encoding='utf-8').read()), TEST, '/') for p in PAGES}
errors.extend(seo_check(probe, make_sitemap(TEST, '/', {}), TEST, '/', 'selftest'))

# JSON-LD gate: every block must parse, and key entities must carry their required fields (only truthful, configured data)
for f in sorted(glob.glob('dist/**/*.html', recursive=True)):
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', open(f, encoding='utf-8').read(), re.S):
        try:
            g = json.loads(blk.replace('<\\/', '</'))
        except Exception as e:
            errors.append('JSON-LD: invalid JSON in %s (%s)' % (f, e)); continue
        for node in g.get('@graph', [g]):
            t = node.get('@type'); need = {'Organization': ['name', 'url', 'logo', 'description'], 'Person': ['name'], 'WebSite': ['url', 'name'],
                                          'WebPage': ['url', 'name', 'inLanguage'], 'Article': ['headline', 'author', 'publisher', 'image'],
                                          'BreadcrumbList': ['itemListElement']}.get(t, [])
            miss = [k for k in need if not node.get(k)]
            if miss: errors.append('JSON-LD: %s in %s missing %s' % (t, f, ', '.join(miss)))
            if t in ('LocalBusiness', 'ProfessionalService') or node.get('address'):
                errors.append('JSON-LD: no LocalBusiness / address allowed (%s)' % f)

if not os.path.exists('images/og.jpg'):
    warnings.append('ASSET: no images/og.jpg (1200x630): link previews will have no image')
if not cfg.get('founderPhotoFinal'):
    warnings.append('ASSET: founder photo is still the placeholder (set "founderPhotoFinal": true once replaced)')
if not socials:
    warnings.append('ASSET: no socialProfiles in site.config.json (Organization sameAs left empty)')

# ---------------------------------------------------------------- 5. safety gates on the built output
SECRET = re.compile(r'sk_live|sk_test|AKIA[0-9A-Z]{12}|AIza[0-9A-Za-z_\-]{20}|ghp_[0-9A-Za-z]{20}|github_pat_|xox[bp]-|BEGIN [A-Z ]*PRIVATE KEY|(?i:api[_-]?key\s*[:=]\s*[\'"][^\'"]{8,})')


def exact_exists(path):
    cur = '.'
    for part in os.path.normpath(path).split(os.sep):
        if part in ('', '.'):
            continue
        if part == '..':
            cur = os.path.dirname(cur) or '.'
            continue
        if part not in os.listdir(cur):
            return False
        cur = os.path.join(cur, part)
    return True


for dirpath, _, files in os.walk('dist'):
    for f in files:
        full = os.path.join(dirpath, f)
        if not f.endswith(('.html', '.txt', '.xml')):
            continue
        txt = open(full, encoding='utf-8').read()
        if SECRET.search(txt):
            errors.append('possible secret/key pattern in ' + full)
        if re.search(r'https?://(localhost|127\.0\.0\.1)', txt):
            errors.append('localhost reference in ' + full)
        if f.endswith('.html'):
            plain = re.sub(r'<!--.*?-->|/\*.*?\*/', '', txt, flags=re.S)             # comments are not shipped copy
            if re.search(r'diagnostic', plain, re.I):
                errors.append('retired term "diagnostic" in ' + full + ' (the assessment is the Raisey Scan)')
            if re.search(r'(?:Presence|Raisey) Review[^.<>]{0,40}(free|gratuit|minutes|e-?mail|instant|automat|3\s?[–-]\s?5)|(free|gratuit|automat\w*|instant\w*)[^.<>]{0,40}(?:Presence|Raisey) Review', plain, re.I):
                errors.append('"Raisey Review" described as free/automated/instant/emailed in ' + full + ' (only the Raisey Scan is)')
            if re.search(r'\b3[ -]minutes?\b|Environ 3\b', plain):
                errors.append('outdated duration ("3 minutes") in ' + full + ' (the Scan is about 4 minutes)')
            if f in ('index.html',) and dirpath in ('dist', 'dist/fr'):
                if len(re.findall(r'<li><span class="dn">', plain)) != 6:
                    errors.append('the Scan must list exactly six dimensions in ' + full)
                if len(re.findall(r"\{id:'[a-z]+',dim:'[a-z]+',facet:'[a-zA-Z]+',t:'single'", plain)) != 9 or len(re.findall(r"\{id:'(?:growth|treatments)',t:'multi'", plain)) != 2:
                    errors.append('the Scan must have 9 scored questions + 2 context-only questions in ' + full)
            if re.search(r'href="[^"]*index\.html', txt):
                errors.append('internal link still points at index.html (should be a clean directory URL) in ' + full)
            b = dirpath if '404' not in f else 'dist'
            for h in set(re.findall(r'(?:href|src)="([^"#:]+?)(?:#[^"]*)?"', txt)) | set(re.findall(r'url\(([^)"\']+\.woff2)\)', txt)) | set(re.findall(r'srcset="([^"\s,]+)', txt)):
                if h.startswith(('data:', 'http', 'mailto', '#', '/')) or not h:
                    continue
                target = os.path.join(b, h)
                ok = exact_exists(target) and (not os.path.isdir(target) or exact_exists(os.path.join(target, 'index.html')))
                if not ok:
                    errors.append('broken or case-mismatched link in %s: %s' % (full, h))
total = sum(os.path.getsize(os.path.join(a, f)) for a, _, fs in os.walk('dist') for f in fs)

print('dist/ built: %d files, %.0f KB' % (sum(len(fs) for _, _, fs in os.walk('dist')), total / 1000))
for w in warnings:
    print('  WARN  ' + w)
for e in errors:
    print('  ERROR ' + e)
if errors:
    print('\nRefusing to produce a production build. Fix the items above (see DEPLOY.md).')
    sys.exit(1)
print('OK' + (' (production' + (', PREVIEW DEPLOY: noindex, no CNAME' if PREVIEW else '') + ')' if PROD else ' (preview: not launch-ready if warnings are listed)'))
