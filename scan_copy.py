"""Single source of truth for the Presence Scan copy (interpretations, objective lines, results email).
scan_copy.json -> (a) the SCAN_COPY block inside index.html / fr/index.html, (b) email/render.mjs.
Edit the JSON, then run build_fr.py (or build_site.py): both pages are regenerated from it."""
import json, re, os

NB = ' '
HERE = os.path.dirname(os.path.abspath(__file__))
BEGIN, END = '/* SCAN_COPY:begin (generated from scan_copy.json — do not edit here) */', '/* SCAN_COPY:end */'
S_BEGIN, S_END = '/* SCAN_SCORING:begin (generated from scan_scoring.mjs — do not edit here) */', '/* SCAN_SCORING:end */'


def load():
    return json.load(open(os.path.join(HERE, 'scan_copy.json'), encoding='utf-8'))


def _typo(s):
    for p in ('?', '!', ':', ';'):
        s = s.replace(' ' + p, NB + p)
    return s


def js_block(lang):
    c = load()[lang]
    fr = lang == 'fr'
    t = _typo if fr else (lambda s: s)
    obj = {'dim': c['dim'],
           'I': {k: {lv: [t(x) for x in v] for lv, v in d.items()} for k, d in c['I'].items()},
           'diag': {k: t(v) for k, v in c['diag'].items()},
           'sig': {k: t(v) for k, v in c['sig'].items()},
           'transp': t(c['transp']), 'request': c['request']}
    body = ',\n      '.join('%s:%s' % (k, json.dumps(v, ensure_ascii=False)) for k, v in obj.items())
    return '%s\n      %s,\n      %s' % (BEGIN, body, END)


def inject(html, lang):
    """Replaces the marked region of a page with the generated block for `lang`."""
    i, j = html.find(BEGIN), html.find(END)
    if i < 0 or j < 0:
        raise SystemExit('SCAN_COPY markers not found')
    return html[:i] + js_block(lang) + html[j + len(END):]


def inject_scoring(html):
    """Inlines scan_scoring.mjs (minus `export`) between the SCAN_SCORING markers, so site and email share one scoring source."""
    src = open(os.path.join(HERE, 'scan_scoring.mjs'), encoding='utf-8').read()
    src = re.sub(r'^//.*\n', '', src, flags=re.M)                 # drop comment lines to keep the page light
    src = re.sub(r'^export ', '', src, flags=re.M).strip()
    i, j = html.find(S_BEGIN), html.find(S_END)
    if i < 0 or j < 0:
        raise SystemExit('SCAN_SCORING markers not found')
    return html[:i] + S_BEGIN + '\n' + src + '\n' + S_END + html[j + len(S_END):]
