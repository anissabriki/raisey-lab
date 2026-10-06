# -*- coding: utf-8 -*-
"""Builds the Expertise page (expertise/index.html + fr/expertise/index.html) from the home pages.

The Services bands (locked component) live in index.html inside <template id="expertise-src">, so build_fr.py
translates them with the rest of the page and _locked/verify.py keeps guarding them. This script keeps the
header, footer, booking popup, cookie banner and Kinassay Scan drawer of each home page, replaces the home
sections with the Services bands, and moves every relative link one folder down.
Run after build_fr.py (build_site.py does it).
"""
import os
import re
import sys

KEEP = {'main', 'services', 'kinassay-scan', 'scan', 'visibility', 'website', 'content', 'growth'}   # anchors that exist on the Expertise page
META = {
    'en': ('Expertise — How Kinassay Lab builds your presence',
           'Visibility & acquisition, website & patient journey, content & presence, strategy & growth: how Kinassay Lab builds the digital presence of aesthetic doctors and clinics.'),
    'fr': ('Expertise — Comment Kinassay Lab bâtit votre présence',
           'Visibilité & acquisition, site & parcours patient, contenu & présence, stratégie & croissance : comment Kinassay Lab bâtit la présence digitale des médecins et cliniques esthétiques.'),
}
# Opens the band named in the address (#visibility, #website, #content, #growth), e.g. from the homepage levers.
OPEN_JS = """<script>
(function(){var open=function(){var r=location.hash&&document.getElementById(location.hash.slice(1));if(!r||!r.classList.contains('row'))return;
  var b=r.querySelector('.r-btn');if(b&&b.getAttribute('aria-expanded')!=='true')b.click();
  r.scrollIntoView({block:'start'})};
  window.addEventListener('hashchange',open);if(document.readyState==='complete')open();else window.addEventListener('load',open)})();
</script>
"""


def fail(msg):
    sys.exit('build_expertise: ' + msg)


def build(src, out, lang):
    h = open(src, encoding='utf-8').read()
    m = re.search(r'<template id="expertise-src">\n(.*?)\n</template>', h, re.S)
    if not m:
        fail('no <template id="expertise-src"> in ' + src)
    bands = m.group(1)
    scan = re.search(r'<!-- =+ KINASSAY SCAN .*?</section>\n', h, re.S)
    if not scan:
        fail('Kinassay Scan drawer not found in ' + src)
    h, n = re.subn(r'(<main id="main">\n).*?(</main>)', lambda k: k.group(1) + bands + '\n\n' + scan.group(0) + k.group(2), h, count=1, flags=re.S)
    if n != 1:
        fail('<main> not found in ' + src)
    title, desc = META[lang]
    esc = lambda t: t.replace('&', '&amp;')
    for pat, val in ((r'<title>.*?</title>', '<title>%s</title>' % esc(title)),
                     (r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % esc(desc)),
                     (r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="%s">' % esc(title)),
                     (r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="%s">' % esc(desc))):
        h, n = re.subn(pat, val, h, count=1)
        if n != 1:
            fail('missing %s in %s' % (pat, src))
    h = re.sub(r'<link rel="preload" as="image"[^>]*>\n', '', h)                       # the home hero image is not on this page
    h = re.sub(r'<link rel="alternate" hreflang="[^"]+" href="[^"]+">\n', '', h)      # build_site.py adds the absolute pair

    other = '../fr/expertise/index.html' if lang == 'en' else '../../expertise/index.html'
    home_other = 'fr/index.html' if lang == 'en' else '../index.html'

    def move(v):
        if v.startswith(('http:', 'https:', 'mailto:', 'tel:', 'data:', '/')):
            return v
        if v.startswith('#'):
            return v if v[1:] in KEEP else '../index.html' + v
        if v.startswith('expertise/index.html'):
            return 'index.html' + v[len('expertise/index.html'):]
        if v == home_other:
            return other
        return '../' + v

    h = re.sub(r'\b(href|src)="([^"]*)"', lambda k: '%s="%s"' % (k.group(1), move(k.group(2))), h)
    h = re.sub(r'\bsrcset="([^"]*)"', lambda k: 'srcset="%s"' % re.sub(r'(^|,\s*)(?!https?:|data:|/)(\S)', r'\1../\2', k.group(1)), h)
    h = re.sub(r'url\((?![\'"]?(?:https?:|data:|/|#))', 'url(../', h)
    h = re.sub(r'href="index\.html"(?=>)', 'href="index.html" aria-current="page"', h)   # menu/footer "Services" = this page
    # keywords wrap between items, never before a "·" (mobile bands)
    h = re.sub(r'(<(?:span|p) class="p?-?sup">)(.*?)(</(?:span|p)>)', lambda k: k.group(1) + k.group(2).replace(' · ', '\u00a0· ') + k.group(3), h)
    h = h.replace('</body>', OPEN_JS + '</body>', 1)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(h)


build('index.html', os.path.join('expertise', 'index.html'), 'en')
build(os.path.join('fr', 'index.html'), os.path.join('fr', 'expertise', 'index.html'), 'fr')
print('expertise pages written')
