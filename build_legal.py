#!/usr/bin/env python3
"""Generates privacy.html (EN) and fr/confidentialite.html (FR, with mentions légales) from index.html's design tokens + site.config.json.
Run after any change to index.html or site.config.json:  python3 build_legal.py
DRAFT: the legal wording (bases, recipients, retention) has not been reviewed by a lawyer; see DEPLOY.md before launch."""
import json, re, sys, os, datetime, html

cfg = json.load(open(os.environ.get('SITE_CONFIG', 'site.config.json'), encoding='utf-8'))
# Environment overrides let CI inject public, non-secret values without editing the repo.
for _k, _e in (('contactEmail', 'CONTACT_EMAIL'), ('siteUrl', 'SITE_URL'), ('basePath', 'BASE_PATH')):
    if os.environ.get(_e, '').strip():
        cfg[_k] = os.environ[_e].strip()
src = open('index.html', encoding='utf-8').read()
css_all = src[src.index('<style>') + 7:src.index('</style>')]
css_base = css_all[css_all.index('/* ============ FONTS'):css_all.index('/* ============ 01 HERO')]
css_foot = css_all[css_all.index('.site-footer{'):]
sprite = ''   # the old circular symbol is deprecated; no SVG sprite
icon = re.search(r'<link rel="icon".*?<link rel="apple-touch-icon"[^>]*>', src, re.S).group(0)
missing = []


def val(key, label_en, label_fr, lang):
    v = (cfg.get(key) or '').strip()
    if v:
        return html.escape(v)
    missing.append(key)
    return '<span class="todo">[%s]</span>' % ('to be completed before launch' if lang == 'en' else 'à compléter avant la mise en ligne')


EXTRA_CSS = '''
.legal{padding-block:clamp(48px,7vw,104px) clamp(56px,8vw,112px)}
.legal .wrap{max-width:860px}
.legal h1{font-size:clamp(2.4rem,1rem + 4vw,4rem);line-height:1.04;letter-spacing:-.03em;margin-bottom:12px}
.legal .upd{color:var(--muted);font-size:14px;margin-bottom:clamp(32px,5vw,56px)}
.legal h2{font-size:clamp(1.5rem,1.1rem + 1.1vw,2rem);line-height:1.15;letter-spacing:-.02em;margin:clamp(32px,4.4vw,52px) 0 12px;padding-top:clamp(20px,3vw,32px);border-top:1px solid var(--line-strong)}
.legal p,.legal li{color:var(--muted);max-width:66ch}
.legal p+p,.legal ul{margin-top:12px}
.legal ul{list-style:disc;padding-left:1.2em;display:grid;gap:6px}
.legal a{color:var(--ink)}
.legal dl{display:grid;grid-template-columns:minmax(0,1fr);gap:4px 24px;margin-top:8px}
@media(min-width:640px){.legal dl{grid-template-columns:minmax(150px,1fr) minmax(0,3fr)}}
.legal dt{font:600 13px/1.5 var(--sans);color:var(--ink)}
.legal dd{margin:0 0 10px;color:var(--muted)}
.todo{color:var(--rasp);font-weight:600;border-bottom:1.5px dashed var(--rasp)}
.back-home{display:inline-flex;align-items:center;min-height:44px;font:600 14px/1.2 var(--sans);text-decoration:none;color:var(--ink);margin-bottom:24px}
.back-home:hover{color:var(--rasp)}
'''


def page(lang):
    en = lang == 'en'
    up = '' if en else '../'
    home = 'index.html' if en else 'index.html'  # fr/index.html is the French home
    other = 'fr/confidentialite.html' if en else '../privacy.html'
    t = lambda a, b: a if en else b
    email = val('contactEmail', 'contact email', 'e-mail de contact', lang)
    name = val('legalName', 'legal entity', 'entité juridique', lang)
    addr = val('postalAddress', 'postal address', 'adresse postale', lang)
    prov = val('emailProvider', 'email provider', 'prestataire d’envoi des e-mails', lang)
    if not en and cfg.get('emailProvider'):   # French wording of the same processors (config value is English)
        prov = html.escape(cfg['emailProvider'].replace('(website hosting)', '(hébergement du site)').replace('(form processing)', '(traitement des formulaires)')
                           .replace('(email delivery)', '(envoi des e-mails)').replace('(email hosting)', '(messagerie)').replace(' and ', ' et '))
    host = val('host', 'hosting provider', 'hébergeur', lang)
    status = html.escape(cfg.get('legalStatus') or '')           # e.g. "EI" (entrepreneur individuel), from the business registry
    siren = html.escape(cfg.get('siren') or '')
    pub = name + (' ' + status if status else '')
    siren_row = ('<dt>SIREN</dt><dd>%s</dd>\n' % siren) if siren else ''
    ret = html.escape(cfg.get('retention') or '24 months') if en else html.escape((cfg.get('retention') or '24 months').replace('months', 'mois'))
    today = datetime.date.today()
    months_fr = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
    date = today.strftime('%-d %B %Y') if en else '%d %s %d' % (today.day, months_fr[today.month - 1], today.year)
    nav = [('#studio', 'Studio', 'Studio'), ('#raisey-scan', 'Raisey Scan', 'Raisey Scan'), ('#services', 'Services', 'Services'),
           ('#work', 'Work', 'Études'), ('#about', 'About', 'À propos')]
    nav_html = ''.join('<li><a href="%s%s">%s</a></li>' % (home, h, t(a, b)) for h, a, b in nav)
    mob_html = ''.join('<li><a class="l" href="%s%s">%s</a></li>' % (home, h, t(a, b)) for h, a, b in nav)
    ins = 'insights/index.html' if en else '../insights/index.html'   # Insights (English only)
    ins_hl = '' if en else ' hreflang="en"'
    nav_html += '<li><a href="%s"%s>Insights</a></li>' % (ins, ins_hl)
    mob_html += '<li><a class="l" href="%s"%s>Insights</a></li>' % (ins, ins_hl)
    if en:
        sw = ('<div class="langsw h" role="group" aria-label="Language"><span aria-current="true" lang="en">EN</span><i aria-hidden="true"></i>'
              '<a href="%s" hreflang="fr" lang="fr" aria-label="Français">FR</a></div>' % other)
    else:
        sw = ('<div class="langsw h" role="group" aria-label="Langue"><a href="%s" hreflang="en" lang="en" aria-label="English">EN</a><i aria-hidden="true"></i>'
              '<span aria-current="true" lang="fr">FR</span></div>' % other)
    sw_m = sw.replace('langsw h', 'langsw m')
    cta = t('Start your Scan', 'Lancer mon Scan')

    if en:
        title = 'Privacy Policy — Raisey Lab'
        body = '''
<a class="back-home" href="index.html">← Back to the site</a>
<h1>Privacy Policy</h1>
<p class="upd">Last updated: %(date)s</p>
<p>This page explains what personal data Raisey Lab collects when you take the Raisey Scan and ask for your results by email, or when you contact us, why, and what your rights are.</p>

<h2>Who is responsible</h2>
<dl><dt>Data controller</dt><dd>%(name)s (Raisey Lab, founder: Anissa Sabrina Briki)</dd>
<dt>Address</dt><dd>%(addr)s</dd><dt>Privacy contact</dt><dd>%(email)s</dd></dl>

<h2>What we collect</h2>
<p>Only what you type into our two forms, the Raisey Scan results request and the contact form:</p>
<ul><li><strong>Required:</strong> name of the doctor or clinic, email address, and (for the Raisey Scan results) your website or Instagram.</li>
<li><strong>Optional:</strong> specialty, phone number, and your message.</li>
<li><strong>Your Scan answers and first insight</strong>, attached to your results request, so we can send your full Scan results and, if we speak, start the first conversation from where you are.</li>
<li>Which button or service you came from (for example “Raisey Scan” or “founding partner”), so we can answer the right question.</li></ul>
<p>The Raisey Scan runs in your browser and reads only your answers: it does not examine your website, Google presence or social profiles. Your answers are not sent or stored anywhere unless you request your full results by email.</p>

<h2>Why we use it, and on what basis</h2>
<ul><li>To send you your complete Raisey Scan results by email and to reply to you: steps taken at your request (Article 6(1)(b) GDPR).</li>
<li>To arrange and hold a first conversation and, if you go on to a Raisey Review, to prepare it, which includes looking at your practice’s public website and digital presence: steps taken at your request (Article 6(1)(b) GDPR).</li>
<li>To follow up on that request with you as a professional contact: our legitimate interest (Article 6(1)(f) GDPR).</li></ul>
<p>We do not send newsletters or marketing emails unless you ask us separately, and we do not use your data for profiling or automated decisions. The results email is a one-off message and does not add you to a mailing list. The Raisey Scan gives an automated reading of your answers only; it has no legal or similarly significant effect on you.</p>

<h2>Who receives it</h2>
<p>Only Raisey Lab. The providers that host this website, deliver form submissions to us and send your Scan results email (%(prov)s) process data on our instructions. We never sell your data. If a provider processes data outside the European Economic Area or the UK, we rely on appropriate safeguards such as the European Commission’s standard contractual clauses.</p>

<h2>How long we keep it</h2>
<p>We keep your request and our exchanges for %(ret)s after our last contact, then delete or anonymise them, unless you become a client, in which case we keep what the law requires.</p>

<h2>Your rights</h2>
<p>You can ask to access, correct, erase, restrict or receive a copy of your data, and to object to its use, by writing to %(email)s. We reply within one month. You can also complain to your data-protection authority: in France the CNIL (cnil.fr), in the UK the ICO (ico.org.uk).</p>

<h2>Cookies and tracking</h2>
<p>This website does not use cookies, analytics, advertising pixels or third-party embeds, and its fonts are hosted on our own server. Because nothing is stored or tracked on your device, there is no cookie banner. If that ever changes, we will ask for your consent first and update this page.</p>

<h2 id="legal-notice">Legal notice</h2>
<dl><dt>Publisher</dt><dd>%(pub)s (Raisey Lab)</dd>
%(siren_row)s<dt>Address</dt><dd>%(addr)s</dd>
<dt>Publication director</dt><dd>Anissa Sabrina Briki</dd>
<dt>Contact</dt><dd>%(email)s</dd>
<dt>Hosting provider</dt><dd>%(host)s</dd></dl>
''' % dict(date=date, name=name, addr=addr, email=email, ret=ret, prov=prov, host=host, pub=pub, siren_row=siren_row)
        foot_legal = '<a class="lg" href="privacy.html">Privacy Policy</a><a class="lg" href="privacy.html#legal-notice">Legal notice</a>'
        rights = 'All rights reserved.'
        tag = 'Expertise, elevated.'
        places = 'Paris · London · Dubai'
        skip, lang_attr = 'Skip to content', 'en'
        menu_open, menu_close = 'Menu', 'Close'
    else:
        title = 'Politique de confidentialité — Raisey Lab'
        body = '''
<a class="back-home" href="index.html">← Retour au site</a>
<h1>Politique de confidentialité</h1>
<p class="upd">Dernière mise à jour : %(date)s</p>
<p>Cette page explique quelles données personnelles Raisey Lab collecte lorsque vous réalisez le Raisey Scan et demandez vos résultats par e-mail, ou que vous nous contactez, pourquoi, et quels sont vos droits.</p>

<h2>Responsable du traitement</h2>
<dl><dt>Responsable</dt><dd>%(name)s (Raisey Lab, fondatrice : Anissa Sabrina Briki)</dd>
<dt>Adresse</dt><dd>%(addr)s</dd><dt>Contact confidentialité</dt><dd>%(email)s</dd></dl>

<h2>Ce que nous collectons</h2>
<p>Uniquement ce que vous saisissez dans nos deux formulaires, la demande de résultats du Raisey Scan et le formulaire de contact :</p>
<ul><li><strong>Obligatoire :</strong> nom du praticien ou de la clinique, adresse e-mail et, pour les résultats du Raisey Scan, votre site web ou Instagram.</li>
<li><strong>Facultatif :</strong> spécialité, numéro de téléphone et votre message.</li>
<li><strong>Vos réponses au Scan et votre premier aperçu</strong>, joints à votre demande de résultats, pour que nous puissions vous envoyer vos résultats complets et, si nous échangeons, partir de votre situation lors du premier échange.</li>
<li>Le bouton ou le service dont vous êtes parti (par exemple « Raisey Scan » ou « partenaire fondateur »), afin de répondre à la bonne question.</li></ul>
<p>Le Raisey Scan s’exécute dans votre navigateur et ne lit que vos réponses : il n’examine ni votre site, ni votre présence Google, ni vos réseaux sociaux. Vos réponses ne sont ni envoyées ni conservées, sauf si vous demandez vos résultats complets par e-mail.</p>

<h2>Pourquoi, et sur quelle base légale</h2>
<ul><li>Pour vous envoyer par e-mail les résultats complets de votre Raisey Scan et vous répondre : mesures prises à votre demande (article 6.1.b du RGPD).</li>
<li>Pour convenir d’un premier échange et le tenir puis, si vous poursuivez avec un Raisey Review, le préparer, ce qui comprend l’examen du site web public et de la présence digitale de votre cabinet : mesures prises à votre demande (article 6.1.b du RGPD).</li>
<li>Pour assurer le suivi de cette demande avec vous en tant que contact professionnel : notre intérêt légitime (article 6.1.f du RGPD).</li></ul>
<p>Nous n’envoyons ni newsletter ni message commercial sans que vous nous le demandiez séparément, et nous n’utilisons pas vos données à des fins de profilage ou de décision automatisée. L’e-mail de résultats est un message unique : il ne vous ajoute à aucune liste de diffusion. Le Raisey Scan fournit une lecture automatisée de vos seules réponses ; elle n’a aucun effet juridique ni effet significatif similaire sur vous.</p>

<h2>Qui y a accès</h2>
<p>Uniquement Raisey Lab. Les prestataires qui hébergent ce site, nous transmettent les formulaires et envoient l’e-mail de résultats de votre Scan (%(prov)s) traitent les données sur nos instructions. Nous ne vendons jamais vos données. Si un prestataire traite des données hors de l’Espace économique européen ou du Royaume-Uni, nous nous appuyons sur des garanties appropriées, comme les clauses contractuelles types de la Commission européenne.</p>

<h2>Durée de conservation</h2>
<p>Nous conservons votre demande et nos échanges pendant %(ret)s après notre dernier contact, puis nous les supprimons ou les anonymisons, sauf si vous devenez client : nous conservons alors ce que la loi impose.</p>

<h2>Vos droits</h2>
<p>Vous pouvez demander l’accès, la rectification, l’effacement, la limitation ou la portabilité de vos données, et vous opposer à leur utilisation, en écrivant à %(email)s. Nous répondons sous un mois. Vous pouvez également saisir votre autorité de protection des données : en France, la CNIL (cnil.fr) ; au Royaume-Uni, l’ICO (ico.org.uk).</p>

<h2>Cookies et suivi</h2>
<p>Ce site n’utilise ni cookies, ni outil d’analyse, ni pixel publicitaire, ni contenu tiers intégré, et ses polices sont hébergées sur notre propre serveur. Comme rien n’est stocké ni suivi sur votre appareil, il n’y a pas de bandeau de cookies. Si cela devait changer, nous demanderions d’abord votre consentement et mettrions cette page à jour.</p>

<h2 id="mentions">Mentions légales</h2>
<dl><dt>Éditeur du site</dt><dd>%(pub)s (Raisey Lab)</dd>
%(siren_row)s<dt>Adresse</dt><dd>%(addr)s</dd>
<dt>Directrice de la publication</dt><dd>Anissa Sabrina Briki</dd>
<dt>Contact</dt><dd>%(email)s</dd>
<dt>Hébergeur</dt><dd>%(host)s</dd></dl>
''' % dict(date=date, name=name, addr=addr, email=email, ret=ret, host=host, prov=prov, pub=pub, siren_row=siren_row)
        foot_legal = '<a class="lg" href="confidentialite.html">Politique de confidentialité</a><a class="lg" href="confidentialite.html#mentions">Mentions légales</a>'
        rights = 'Tous droits réservés.'
        tag = 'L’expertise, élevée.'
        places = 'Paris · Londres · Dubaï'
        skip, lang_attr = 'Aller au contenu', 'fr'
        menu_open, menu_close = 'Menu', 'Fermer'

    css = css_base + css_foot + EXTRA_CSS
    if not en:
        css = css.replace('url(fonts/', 'url(../fonts/')
    fonts = ('<link rel="preload" href="%sfonts/fraunces-latin-opsz-normal.woff2" as="font" type="font/woff2" crossorigin>\n'
             '<link rel="preload" href="%sfonts/inter-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>') % (up, up)
    footer_nav = ''.join('<li><a href="%s%s">%s</a></li>' % (home, h, t(a, b)) for h, a, b in nav) + '<li><a href="%s"%s>Insights</a></li>' % (ins, ins_hl) + '<li><a href="%s#contact">Contact</a></li>' % home
    return '''<!doctype html>
<html lang="%(lang)s">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>%(title)s</title>
<meta name="robots" content="noindex,follow">
<meta name="theme-color" content="#f3eee6">
%(icon)s
<link rel="alternate" hreflang="en" href="%(en_href)s">
<link rel="alternate" hreflang="fr" href="%(fr_href)s">
%(fonts)s
<style>
%(css)s
</style>
</head>
<body>
%(sprite)s
<a class="skip" href="#main">%(skip)s</a>
<header class="site-header">
  <div class="wrap bar">
    <a class="brand" href="%(home)s#studio" aria-label="Raisey Lab">Raisey Lab</a>
    <nav class="nav" aria-label="%(navlabel)s"><ul>%(nav)s</ul></nav>
    <div style="display:flex;align-items:center;gap:16px">%(sw)s<a class="btn head-cta" href="%(home)s#raisey-scan">%(cta)s <i class="ar"></i></a>
      <button class="menu-btn" type="button" aria-expanded="false" aria-controls="mobile-nav"><span class="mt">%(mo)s</span><svg viewBox="0 0 20 12" width="20" height="12" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path class="l1" d="M1 2h18"/><path class="l2" d="M1 10h18"/></svg></button></div>
  </div>
  <div class="mobile" id="mobile-nav" hidden><div class="wrap"><ul>%(mob)s</ul>%(swm)s<a class="btn" href="%(home)s#raisey-scan">%(cta)s <i class="ar"></i></a></div></div>
</header>
<main id="main" class="legal"><div class="wrap">%(body)s</div></main>
<footer class="site-footer"><div class="wrap">
  <div class="f-row"><a class="brand" href="%(home)s#studio" style="font-size:20px">Raisey Lab</a>
  <nav aria-label="%(footlabel)s"><ul>%(fnav)s</ul></nav></div>
  <p class="f-legal">%(fl)s<span>%(places)s · %(tag)s © %(yr)d Raisey Lab. %(rights)s</span></p>
</div></footer>
<script>
(function(){const mb=document.querySelector('.menu-btn'),mp=document.getElementById('mobile-nav');
const set=o=>{mb.setAttribute('aria-expanded',String(o));mb.querySelector('.mt').textContent=o?'%(mc)s':'%(mo)s';mp.hidden=!o};
mb.addEventListener('click',()=>set(mb.getAttribute('aria-expanded')!=='true'));
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!mp.hidden){set(false);mb.focus()}});
mp.addEventListener('click',e=>{if(e.target.closest('a'))set(false)});
matchMedia('(min-width:1001px)').addEventListener('change',m=>{if(m.matches)set(false)});})();
</script>
</body>
</html>
''' % dict(lang=lang_attr, title=title, en_href=('privacy.html' if en else '../privacy.html'), fr_href=('fr/confidentialite.html' if en else 'confidentialite.html'),
           fonts=fonts, css=css, sprite=sprite, icon=(icon if en else icon.replace('href="', 'href="../')), skip=skip, home=home, navlabel=t('Main', 'Principale'), nav=nav_html, sw=sw, swm=sw_m, cta=cta, mo=menu_open, mc=menu_close,
           mob=mob_html, body=body, footlabel=t('Footer', 'Pied de page'), fnav=footer_nav, fl=foot_legal, places=places, tag=tag, yr=today.year, rights=rights)


def page404():
    base = (cfg.get('basePath') or '/').strip()
    if not base.startswith('/'): base = '/' + base
    if not base.endswith('/'): base += '/'
    css = css_base + css_foot + EXTRA_CSS + '.nf{min-height:52vh;display:grid;align-content:center;gap:16px}.nf h1{font-size:clamp(2.6rem,1rem + 5vw,5rem)}.nf p{max-width:44ch}.nf .btn{--b:var(--p-burgundy);--f:var(--optical);border-color:var(--p-burgundy);color:var(--f)}'
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<base href="%(base)s">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Page not found — Raisey Lab</title>
<meta name="robots" content="noindex">
<meta name="theme-color" content="#f3eee6">
%(icon)s
<link rel="preload" href="fonts/fraunces-latin-opsz-normal.woff2" as="font" type="font/woff2" crossorigin>
<style>
%(css)s
</style>
</head>
<body>
%(sprite)s
<header class="site-header"><div class="wrap bar"><a class="brand" href="index.html" aria-label="Raisey Lab">Raisey Lab</a></div></header>
<main class="legal"><div class="wrap nf">
<h1>This page doesn’t exist.</h1>
<p>The link may be old or mistyped. You can go back to the site.</p>
<p><a class="btn" href="index.html">Back to Raisey Lab <i class="ar"></i></a></p>
<h2 lang="fr" style="border:0;padding-top:24px;margin-top:8px">Cette page n’existe pas.</h2>
<p lang="fr">Le lien est peut-être ancien ou mal saisi. <a href="fr/index.html">Retourner au site en français</a>.</p>
</div></main>
</body>
</html>
""" % dict(base=base, icon=icon, css=css, sprite=sprite)


open('404.html', 'w', encoding='utf-8').write(page404())
open('privacy.html', 'w', encoding='utf-8').write(page('en'))
os.makedirs('fr', exist_ok=True)
open('fr/confidentialite.html', 'w', encoding='utf-8').write(page('fr'))
print('privacy.html + fr/confidentialite.html + 404.html written')
uniq = sorted(set(missing))
if uniq:
    print('\nTO COMPLETE BEFORE LAUNCH (site.config.json):', ', '.join(uniq))
