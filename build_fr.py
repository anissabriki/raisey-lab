#!/usr/bin/env python3
"""Generates fr/index.html from index.html (English is the source of truth) and wires the EN | FR switch.
Run:  python3 build_fr.py
If an English string changes, the matching entry below fails loudly so the French copy is never silently stale.
Brand terms kept in English on purpose: "Kinassay Scan", "Kinassay Review".  City names use French exonyms (Londres, Dubaï)."""
import re, sys, os
import scan_copy

SRC = 'index.html'
NB = ' '


def typo(s):
    """French typography: no-break space before ? ! : ;  (visible copy only)."""
    for p in ('?', '!', ':', ';'):
        s = s.replace(' ' + p, NB + p)
    return s


def main():
    en = open(SRC, encoding='utf-8').read()
    synced = scan_copy.inject_scoring(scan_copy.inject(en, 'en'))   # copy block <- scan_copy.json, scoring <- scan_scoring.mjs
    if synced != en:
        open(SRC, 'w', encoding='utf-8').write(synced)
        en = synced
    fr = en

    def sub(old, new, count=None):
        nonlocal fr
        if old not in fr:
            sys.exit('MISSING English string (copy changed?): ' + old[:90])
        fr = fr.replace(old, typo(new)) if count is None else fr.replace(old, typo(new), count)

    # ---------- head ----------
    sub('<html lang="en">', '<html lang="fr">')
    sub('<title>Kinassay Lab — Aesthetic Medicine Digital Strategy</title>',
        '<title>Kinassay Lab — Stratégie digitale en médecine esthétique</title>')
    sub('content="A digital strategy studio born inside aesthetic medicine. Kinassay Lab raises the visibility, authority and patient journey of aesthetic doctors and clinics."',
        'content="Kinassay Lab, studio de stratégie digitale né de la médecine esthétique : visibilité, autorité et parcours patient des médecins et cliniques esthétiques."')
    sub('<meta property="og:title" content="Kinassay Lab — You built the expertise. We raise its presence.">',
        '<meta property="og:title" content="Kinassay Lab — Vous avez l’expertise. Nous élevons sa présence.">')
    sub('content="Visibility, authority and growth for aesthetic doctors and clinics. Paris · London · Dubai."',
        'content="Présence digitale pour médecins et cliniques esthétiques. Paris · Londres · Dubaï."')
    fr = fr.replace('href="data:image/svg+xml', 'href="data:image/svg+xml')  # favicon is inline, unchanged
    fr = fr.replace('href="fonts/', 'href="../fonts/').replace('url(fonts/', 'url(../fonts/')
    fr = re.sub(r'(?<![\w/.])images/', '../images/', fr)
    fr = re.sub(r'href="(favicon|apple-touch-icon)', r'href="../\1', fr)

    # ---------- chrome ----------
    fr = fr.replace('alt="Anissa Sabrina Briki, founder of Kinassay Lab, seated on a cream sofa: editorial portrait captioned “Founder, Anissa”"', 'alt="Anissa Sabrina Briki, fondatrice de Kinassay Lab, assise sur un canapé crème : portrait éditorial avec la mention « Founder, Anissa »"')
    fr = fr.replace('<label for="sf-website_url">Leave this field empty</label>', '<label for="sf-website_url">Laissez ce champ vide</label>').replace('<label for="cf-website_url">Leave this field empty</label>', '<label for="cf-website_url">Laissez ce champ vide</label>')
    sub('aria-label="Kinassay Lab, top"', 'aria-label="Kinassay Lab, haut de page"')
    sub('<nav class="nav" aria-label="Main">', '<nav class="nav" aria-label="Principale">')
    sub('href="#work">Profiles<', 'href="#work">Profils<')
    sub('href="#about">About<', 'href="#about">À propos<')
    sub('Book a first meeting <i class="ar"></i>', '<span>Réserver un premier <span class="nb">rendez-vous</span></span> <i class="ar"></i>')
    sub('<a class="ck-more" data-ck-more href="privacy.html">', '<a class="ck-more" data-ck-more href="confidentialite.html">')
    sub('<nav aria-label="Footer">', '<nav aria-label="Pied de page">')
    sub('<span class="mt">Menu</span>', '<span class="mt">Menu</span>')

    # ---------- hero + new homepage sequence (2026-09) ----------
    sub('<p class="eyebrow rise" style="--i:0">When aesthetic medicine meets digital.</p>', '<p class="eyebrow rise" style="--i:0">Quand la médecine esthétique rencontre le digital.</p>')
    sub('<h1 id="hx-h" class="rise" style="--i:1">Your expertise<br> deserves<br> <em>to be seen.</em></h1>', '<h1 id="hx-h" class="rise" style="--i:1">Votre expertise<br> mérite<br> <em>d’être vue.</em></h1>')
    sub('We help aesthetic doctors and clinics build the visibility, authority and digital presence that turn medical expertise into patient trust.',
        'Nous aidons les médecins et cliniques esthétiques à bâtir la visibilité, l’autorité et la présence digitale qui transforment l’expertise médicale en confiance patient.')
    fr = fr.replace('Start my Kinassay Scan <i class="ar"></i></a>\n        <p class="hx-micro">About 4 minutes · Free · No commitment</p>', 'Démarrer mon Kinassay Scan <i class="ar"></i></a>\n        <p class="hx-micro">Environ 4 minutes · Gratuit · Sans engagement</p>')
    fr = fr.replace('Start my Kinassay Scan <i class="ar"></i></a>\n      <p class="hx-micro">About 4 minutes · Free · No commitment</p>', 'Démarrer mon Kinassay Scan <i class="ar"></i></a>\n      <p class="hx-micro">Environ 4 minutes · Gratuit · Sans engagement</p>')
    sub('30 minutes · Free · No commitment', '30 minutes · Gratuit · Sans engagement')
    sub('<p class="hx-alt">Not ready to talk yet? <a href="#kinassay-scan" data-startdiag data-interest="presence-scan">Take the free Kinassay Scan</a> <span class="nb">(about 4 minutes)</span></p>',
        '<p class="hx-alt">Envie d’explorer d’abord ? <a href="#kinassay-scan" data-startdiag data-interest="presence-scan">Faites le Kinassay Scan gratuit</a> <span class="nb">(environ 4 minutes)</span></p>')
    sub('alt="Architectural detail of an aesthetic medicine clinic in warm natural light"', 'alt="Détail architectural d’une clinique de médecine esthétique dans une lumière naturelle chaude"')
    sub('<ol class="hx-steps" aria-label="The patient journey"><li>Search</li><li>Discover</li><li>Trust</li><li>Choose</li></ol>', '<ol class="hx-steps" aria-label="Le parcours patient"><li>Recherche</li><li>Découverte</li><li>Confiance</li><li>Choix</li></ol>')
    sub('alt="Quiet consultation room in an aesthetic medicine clinic"', 'alt="Salle de consultation calme dans une clinique de médecine esthétique"')
    sub('<h2 id="hx-journey-h">The consultation isn’t<br> the beginning of the patient journey.</h2>', '<h2 id="hx-journey-h">La consultation n’est pas<br> le début du parcours patient.</h2>')
    sub('<p>Patients are choosing long <u>before</u> they enter your clinic.<br> We shape everything that happens <u>before</u> the appointment.</p>', '<p>Les patients choisissent bien <u>avant</u> d’entrer dans votre cabinet.<br> Nous façonnons tout ce qui se joue <u>avant</u> le rendez-vous.</p>')
    sub('<h3>Visibility</h3><p>SEO · Search<br> Being found</p>', '<h3>Visibilité</h3><p>SEO · Recherche<br> Être trouvé</p>')
    sub('<h3>Authority</h3><p>Expertise · Reputation<br> Trust</p>', '<h3>Autorité</h3><p>Expertise · Réputation<br> Confiance</p>')
    sub('<h3>Brand</h3><p>Positioning · Identity<br> Differentiation</p>', '<h3>Marque</h3><p>Positionnement · Identité<br> Différenciation</p>')
    sub('<h3>Patient Journey</h3><p>Website · UX<br> Conversion</p>', '<h3>Parcours patient</h3><p>Site web · UX<br> Conversion</p>')
    sub('<h3>Growth</h3><p>Acquisition · CRM<br> Retention</p>', '<h3>Croissance</h3><p>Acquisition · CRM<br> Fidélisation</p>')
    sub('<p class="hx-eb">From diagnosis to direction.</p>', '<p class="hx-eb">De l’analyse à la direction.</p>')
    sub('<h2 id="hx-studio-h">A strategic and creative studio for aesthetic doctors and clinics.</h2>', '<h2 id="hx-studio-h">Un studio stratégique et créatif pour les médecins et cliniques esthétiques.</h2>')
    sub('We combine industry expertise, data, strategy and high-end content to help you be found, trusted and chosen by the right patients.',
        'Nous réunissons expertise du secteur, données, stratégie et contenus haut de gamme pour que les bons patients vous trouvent, vous fassent confiance et vous choisissent.')
    sub('<a class="tl" href="expertise/index.html">Explore our services <i class="ar"></i></a>', '<a class="tl" href="expertise/index.html">Découvrir nos services <i class="ar"></i></a>')
    sub('alt="Architectural interior of an aesthetic medicine clinic"', 'alt="Intérieur architectural d’une clinique de médecine esthétique"')
    sub('<p class="hx-eb">Ready to see the full picture?</p>', '<p class="hx-eb">Prêt à voir le tableau complet ?</p>')
    sub('<h2 id="hx-final-h">Take the Kinassay Scan.</h2>', '<h2 id="hx-final-h">Faites le Kinassay Scan.</h2>')
    sub('A clear, personalised reading of your answers across six dimensions, with priorities to act on.', 'Une lecture claire et personnalisée de vos réponses sur six dimensions, avec des priorités concrètes.')

    # ---------- 02 review ----------
    sub('<p class="eyebrow">Your Kinassay Scan</p>', '<p class="eyebrow">Votre Kinassay Scan</p>')
    sub('Your results at a glance.', 'Vos résultats en un coup d’œil.')
    sub('A first read of your answers across six key dimensions.<span class="basis">Based on your answers · Not an audit of your digital presence</span>', 'Une première lecture de vos réponses sur six dimensions clés.<span class="basis">Basé sur vos réponses · Pas sur un audit de votre présence digitale</span>')
    sub('Understanding your results', 'Comprendre vos résultats')
    sub('Each dimension is read on three levels.', 'Chaque dimension se lit sur trois niveaux.')
    sub('<button class="btn" type="button" id="takeDiag">Start my Kinassay Scan <i class="ar"></i></button>', '<button class="btn" type="button" id="takeDiag">Démarrer mon Kinassay Scan <i class="ar"></i></button>')
    sub('aria-label="Close the Kinassay Scan">Close <span', 'aria-label="Fermer le Kinassay Scan">Fermer <span')
    sub('<p class="b3-eb">Our approach</p>', '<p class="b3-eb">Notre approche</p>')
    sub('<h2 id="pl-h" class="b3-h">We build your presence around three levers.</h2>', '<h2 id="pl-h" class="b3-h">Nous construisons votre présence autour de 3 leviers.</h2>')
    for en_, fr_ in (('<dt>Visibility</dt>', '<dt>Visibilité</dt>'), ('<dt>Authority</dt>', '<dt>Autorité</dt>'), ('<dt>Growth</dt>', '<dt>Croissance</dt>'),
                     ('Exist where your patients are looking for you: search, local search, social and digital presence.', 'Exister là où vos patients vous cherchent : recherche, référencement local, réseaux et présence digitale.'),
                     ('Let patients perceive your expertise and your approach before the consultation.', 'Faire percevoir votre expertise et votre approche avant même la consultation.'),
                     ('Turn that trust into bookings, then into loyalty.', 'Transformer cette confiance en prise de rendez-vous, puis en fidélité.'),
                     ('See how we work on<br> your visibility', 'Découvrir comment<br> nous travaillons la visibilité'),
                     ('See how we build<br> your authority', 'Découvrir comment<br> nous renforçons votre autorité'),
                     ('See how we drive<br> your growth', 'Découvrir comment<br> nous stimulons votre croissance'),
                     ('<span>Where does your digital presence stand?</span>', '<span>Où en est votre présence digitale ?</span>'),
                     ('Identify your opportunities for visibility, authority and growth in a few minutes.', 'Identifiez en quelques minutes vos opportunités de visibilité, d’autorité et de croissance.'),
                     ('Take my Kinassay Scan <i class="ar"></i>', 'Faire mon Kinassay Scan <i class="ar"></i>'),
                     ('Free · About 4 minutes · Results by email within minutes', 'Gratuit · Environ 4 minutes · Résultats par e-mail en quelques minutes')):
        sub(en_, fr_)
    sub('aria-label="The six dimensions read by the Scan"', 'aria-label="Les six dimensions lues par le Scan"')
    sub('<p class="hx-eb hx-center">Prefer to explore first?</p>', '<p class="hx-eb hx-center">Envie d’explorer d’abord ?</p>')
    sub('<h2 id="hx-pillars-h" class="hx-scan-h hx-center">Take the free Kinassay Scan.</h2>', '<h2 id="hx-pillars-h" class="hx-scan-h hx-center">Faites le Kinassay Scan gratuit.</h2>')
    sub('<p class="hx-intro">Eleven questions about your practice. Your personalised reading across six dimensions, sent to you by email within minutes.</p>',
        '<p class="hx-intro">Onze questions sur votre cabinet. Votre lecture personnalisée sur six dimensions, envoyée par e-mail en quelques minutes.</p>')
    sub('The Kinassay Scan needs JavaScript. You can book a first meeting in the next section.',
        'Le Kinassay Scan nécessite JavaScript. Vous pouvez réserver un premier rendez-vous dans la section suivante.')
    sub('<h3>Editorial Potential</h3><p>Content · Thought leadership<br> Differentiation</p>', '<h3>Potentiel éditorial</h3><p>Contenu · Prise de parole d’expert<br> Différenciation</p>')
    sub('Free · Automated · Based on your answers · About 4 minutes', 'Gratuit · Automatisé · Basé sur vos réponses · Environ 4 minutes')
    sub('</svg>Scan complete</p>', '</svg>Scan terminé</p>')
    sub('Where should we send your full Scan results?', 'Recevez votre Kinassay Scan personnalisé.')
    sub('Your full Kinassay Scan results will be sent to this address. If you’d like to go further, the next step is a first meeting.',
        'Les résultats complets de votre Kinassay Scan seront envoyés à cette adresse. Pour aller plus loin, l’étape suivante est un premier rendez-vous.')
    sub('Doctor or clinic name <span', 'Nom du praticien ou de la clinique <span')
    sub('placeholder="e.g. Dr Marie Dupont"', 'placeholder="ex. Dr Marie Dupont"')
    sub('data-err="Please add your name or clinic."', 'data-err="Merci d’indiquer votre nom ou celui de votre clinique."')
    sub('<label for="sf-email">Email <span', '<label for="sf-email">E-mail <span')
    sub('placeholder="you@clinic.com" autocomplete="email" required data-err="Please add your email." data-err2="That email doesn’t look right."',
        'placeholder="vous@clinique.fr" autocomplete="email" required data-err="Merci d’indiquer votre e-mail." data-err2="Cet e-mail semble incorrect."')
    sub('<label for="cf-email">Email <span', '<label for="cf-email">E-mail <span')
    sub('Specialty <span class="o">(optional)</span>', 'Spécialité <span class="o">(facultatif)</span>')
    sub('Website or Instagram <span', 'Site web ou Instagram <span')
    sub('placeholder="e.g. yourclinic.com or @handle"', 'placeholder="ex. votreclinique.fr ou @compte"')
    sub('data-err="Please add your website or Instagram."', 'data-err="Merci d’indiquer votre site web ou Instagram."')
    sub('Send me my results <i class="ar"></i>', 'Recevoir mes résultats <i class="ar"></i>')
    sub('Request a first conversation <i class="ar"></i></button>', 'Demander un premier échange <i class="ar"></i></button>')
    sub('<span class="nb">Free · No commitment ·</span> <span class="nb">Full results by email within minutes</span>',
        '<span class="nb">Gratuit · Sans engagement ·</span> <span class="nb">Résultats complets par e-mail sous quelques minutes</span>')
    sub('Required. Everything else is optional. We use these details, together with your Scan answers, only to send your Scan results and to reply to you. <a class="link" href="privacy.html">Privacy Policy</a>',
        'Obligatoire. Le reste est facultatif. Ces informations, avec vos réponses au Scan, servent uniquement à vous envoyer vos résultats et à vous répondre. <a class="link" href="confidentialite.html">Politique de confidentialité</a>')
    sub('<h3>Thank you. Your complete Scan results are on their way.</h3><p class="muted">They should reach you within a few minutes. Nothing yet? Check your spam folder.</p><p class="muted">The next step, if you wish: a 30-minute debrief with the founder to read your results together. Free, no commitment.</p>',
        '<h3>Merci. Les résultats complets de votre Scan arrivent.</h3><p class="muted">Comptez quelques minutes. Rien reçu ? Pensez à vérifier vos courriers indésirables.</p><p class="muted">L’étape suivante, si vous le souhaitez : un débrief de 30 minutes avec la fondatrice pour lire vos résultats ensemble. Gratuit, sans engagement.</p>')
    sub('Book my 30-minute debrief <i class="ar"></i>', 'Réserver mon débrief de 30 minutes <i class="ar"></i>')

    # specialty selects: French labels, canonical English values (CRM stays consistent across languages)
    groups = [
        ('Médecins et chirurgiens', 'tier1', [('Aesthetic Physician', 'Médecin esthétique'), ('Anesthesiologist', 'Anesthésiste-réanimateur'), ('Cosmetic Surgeon', 'Chirurgien esthétique'),
            ('Dermatologist', 'Dermatologue'), ('Facial Plastic Surgeon', 'Chirurgien plasticien de la face'), ('Gynecologist', 'Gynécologue'), ('Internal Medicine', 'Médecin interniste'),
            ('MD (general)', 'Médecin généraliste'), ('Oculoplastic Surgeon', 'Chirurgien oculo-plasticien'), ('Pediatrician', 'Pédiatre'), ('Plastic Surgeon', 'Chirurgien plasticien')]),
        ('Infirmiers et infirmières', 'tier2', [('Nurse Practitioner', 'Infirmier(ère) en pratique avancée (IPA)'), ('Registered Nurse', 'Infirmier(ère) diplômé(e) d’État (IDE)')]),
        ('Paramédical et dentaire', 'tier3', [('Dental Surgeon', 'Chirurgien-dentiste'), ('Mesotherapist', 'Mésothérapeute'), ('Pharmacist', 'Pharmacien'), ('Physician Assistant', 'Assistant médical')]),
        ('Autre', 'tier4', [('Beautician', 'Esthéticien(ne)'), ('Medical office staff', 'Personnel de cabinet médical'), ('Nutritionist', 'Nutritionniste'), ('Industry representative / other', 'Représentant de l’industrie / autre')])]
    opts = '<option value="" selected>Choisissez votre spécialité</option>'
    for g, t, items in groups:
        opts += '<optgroup label="%s">' % g + ''.join('<option value="%s" data-tier="%s">%s</option>' % (v, t, l) for v, l in items) + '</optgroup>'
    for sid in ('sf-spec', 'cf-spec'):
        pat = re.compile(r'(<select class="input" id="%s" name="specialty">).*?(</select>)' % sid, re.S)
        if not pat.search(fr):
            sys.exit('select not found: ' + sid)
        fr = pat.sub(lambda m: m.group(1) + opts + m.group(2), fr)

    # ---------- 04 services → Expertise page (localized derivative of the locked English component; owner brief 2026-10-06) ----------
    sub('<p class="lab">Our expertise</p>', '<p class="lab">Notre expertise</p>')
    sub('<span class="l1">How we build</span> <span class="l2">your <em>presence.</em></span>', '<span class="l1">Comment nous bâtissons</span> <span class="l2">votre <em>présence.</em></span>')
    sub('From visibility to patient experience, we build the digital strategy that shapes how an aesthetic practice is <span class="hl">found, perceived and chosen.</span>',
        'De la visibilité à l’expérience patient, nous bâtissons la stratégie digitale qui façonne la manière dont un cabinet esthétique est <span class="hl">trouvé, perçu et choisi.</span>')
    svc = [('Visibility &amp; acquisition', 'Visibilité &amp; acquisition', 'Be found', 'Être trouvé',
            'Google · Local SEO · Social · Reputation', 'Google · SEO local · Social · Réputation',
            'Be found by the right patients.', 'Être trouvé par les bons patients.',
            '<li>Acquisition strategy</li><li>SEO &amp; local search</li><li>Google Business Profile</li><li>Google Ads</li><li>Meta Ads</li><li>Social media strategy</li><li>Reputation &amp; reviews</li><li>Performance analysis</li>',
            '<li>Stratégie d’acquisition</li><li>SEO et référencement local</li><li>Google Business Profile</li><li>Google Ads</li><li>Meta Ads</li><li>Stratégie social media</li><li>Réputation et avis</li><li>Analyse des performances</li>'),
           ('Website &amp; patient journey', 'Site &amp; parcours patient', 'Turn interest', 'Transformer l’intérêt',
            'Positioning · UX/UI · SEO · Conversion · Booking', 'Positionnement · UX/UI · SEO · Conversion · Rendez-vous',
            'Turn interest into appointments.', 'Transformer l’intérêt en rendez-vous.',
            '<li>Website strategy &amp; architecture</li><li>Positioning</li><li>UX/UI</li><li>Treatment pages</li><li>SEO</li><li>Online booking</li><li>Conversion optimisation</li><li>Analytics &amp; tracking</li>',
            '<li>Stratégie et architecture du site</li><li>Positionnement</li><li>UX/UI</li><li>Pages traitements</li><li>SEO</li><li>Prise de rendez-vous</li><li>Optimisation de conversion</li><li>Analytics et tracking</li>'),
           ('Content &amp; presence', 'Contenu &amp; présence', 'Build trust', 'Construire la confiance',
            'Content · Social · Email · CRM · Loyalty', 'Contenu · Social · Email · CRM · Fidélisation',
            'Build trust over time.', 'Construire la confiance dans le temps.',
            '<li>Editorial strategy</li><li>Content creation</li><li>Social media</li><li>Email marketing</li><li>CRM</li><li>Automations</li><li>Educational content</li><li>Nurturing</li><li>Loyalty</li>',
            '<li>Stratégie éditoriale</li><li>Création de contenu</li><li>Réseaux sociaux</li><li>Email marketing</li><li>CRM</li><li>Automatisations</li><li>Contenu éducatif</li><li>Nurturing</li><li>Fidélisation</li>'),
           ('Strategy &amp; growth', 'Stratégie &amp; croissance', 'Accelerate growth', 'Accélérer la croissance',
            'Strategy · Data · Analytics · Authority · Growth', 'Stratégie · Data · Analytics · Autorité · Croissance',
            'Make your digital presence a growth lever.', 'Faire de la présence digitale un levier de croissance.',
            '<li>Digital audit</li><li>Growth strategy</li><li>Analytics &amp; dashboards</li><li>Continuous optimisation</li><li>Digital authority</li><li>Practitioner positioning</li><li>Competitive analysis</li><li>Strategic support</li>',
            '<li>Audit digital</li><li>Stratégie de croissance</li><li>Analytics et dashboards</li><li>Optimisation continue</li><li>Autorité digitale</li><li>Positionnement du praticien</li><li>Analyse concurrentielle</li><li>Accompagnement stratégique</li>')]
    for nm, nm_fr, stg, stg_fr, sp, sp_fr, ds, ds_fr, cap, cap_fr in svc:
        sub('<span class="nm">%s</span><span class="stg">%s</span><span class="sup">%s</span><span class="ds">%s</span>' % (nm, stg, sp, ds),
            '<span class="nm">%s</span><span class="stg">%s</span><span class="sup">%s</span><span class="ds">%s</span>' % (nm_fr, stg_fr, sp_fr, ds_fr))
        sub('<p class="p-stg">%s</p><p class="p-sup">%s</p><p class="p-ds">%s</p>\n            <ul class="cap">%s</ul>' % (stg, sp, ds, cap),
            '<p class="p-stg">%s</p><p class="p-sup">%s</p><p class="p-ds">%s</p>\n            <ul class="cap">%s</ul>' % (stg_fr, sp_fr, ds_fr, cap_fr))
    sub('<p class="eb">Not sure where to start?</p>', '<p class="eb">Vous ne savez pas par où commencer ?</p>')
    sub('<h3>Discover the strengths and opportunities of your digital presence in a few minutes.</h3>',
        '<h3>Découvrez les forces et les opportunités de votre présence digitale en quelques minutes.</h3>')

    # ---------- Expertise page FAQ (owner-approved 2026-10-06) ----------
    sub('<p class="lab">Frequently asked questions</p><h1 id="faq-h">Digital strategy for aesthetic medicine, <em>in short.</em></h1>', '<p class="lab">Questions fréquentes</p><h1 id="faq-h">La stratégie digitale en médecine esthétique, <em>en bref.</em></h1>')
    for en_, fr_ in (
        ('What is Kinassay Lab?', 'Qu’est-ce que Kinassay Lab ?'),
        ('Kinassay Lab is a digital strategy studio born inside aesthetic medicine. We work with aesthetic doctors and clinics in Paris, London and Dubai to build how they are found, perceived and chosen online.',
         'Kinassay Lab est un studio de stratégie digitale né de la médecine esthétique. Nous accompagnons les médecins et cliniques esthétiques à Paris, Londres et Dubaï pour bâtir la manière dont ils sont trouvés, perçus et choisis en ligne.'),
        ('Who do you work with?', 'Avec qui travaillez-vous ?'),
        ('Aesthetic doctors, independent practices and aesthetic clinics who want a digital presence that reflects the quality of their medical work.',
         'Avec des médecins esthétiques, des cabinets indépendants et des cliniques esthétiques qui veulent une présence digitale à la hauteur de la qualité de leur pratique médicale.'),
        ('What does your support cover?', 'Que comprend votre accompagnement ?'),
        ('Four areas: visibility &amp; acquisition (local SEO, Google Business Profile, Google and Meta ads, reputation), website &amp; patient journey, content &amp; presence (social media, email, CRM), and strategy &amp; growth (digital audit, analytics, practitioner positioning).',
         'Quatre domaines : visibilité &amp; acquisition (SEO local, Google Business Profile, publicité Google et Meta, réputation), site &amp; parcours patient, contenu &amp; présence (réseaux sociaux, email, CRM) et stratégie &amp; croissance (audit digital, analytics, positionnement du praticien).'),
        ('Where should a practice start?', 'Par où un cabinet doit-il commencer ?'),
        ('With the Kinassay Scan: a free questionnaire of about 4 minutes that reads your digital presence across six dimensions. Your results arrive by email within minutes.',
         'Par le Kinassay Scan : un questionnaire gratuit d’environ 4 minutes qui analyse votre présence digitale sur six dimensions. Vos résultats arrivent par e-mail en quelques minutes.'),
        ('How does a first meeting work?', 'Comment se passe un premier rendez-vous ?'),
        ('It is a 30-minute video call, free and without commitment, to understand your practice, your goals and where your digital presence stands.',
         'C’est un échange de 30 minutes en visio, gratuit et sans engagement, pour comprendre votre cabinet, vos objectifs et l’état de votre présence digitale.'),
        ('Do you work in French and English?', 'Travaillez-vous en français et en anglais ?'),
        ('Yes. We work in both languages, with practices in France, the United Kingdom and the United Arab Emirates.',
         'Oui. Nous travaillons dans les deux langues, avec des cabinets en France, au Royaume-Uni et aux Émirats arabes unis.')):
        sub(en_, fr_)

    # ---------- 05 studies ----------
    sub('<h2 id="work-h">Do you recognise yourself?</h2><span class="r">Three situations we often see</span>', '<h2 id="work-h">Vous <span class="nb">reconnaissez-vous ?</span></h2><span class="r">Trois situations que nous rencontrons souvent</span>')
    sub('aria-label="Three situations. Swipe, or use the arrow keys."', 'aria-label="Trois situations. Faites défiler, ou utilisez les flèches du clavier."')
    sub('aria-label="Previous situation"', 'aria-label="Situation précédente"')
    sub('aria-label="Next situation"', 'aria-label="Situation suivante"')
    sub('</span> Established expertise</p>', '</span> Expertise reconnue</p>')
    sub('</span> Boutique practice</p>', '</span> Cabinet confidentiel</p>')
    sub('</span> Clinical point of view</p>', '</span> Vision clinique</p>')
    sub('<h3>Twenty years of practice, invisible online.</h3>', '<h3>Vingt ans de pratique, invisibles en ligne.</h3>')
    sub('<h3>A strong reputation, an ordinary online presence.</h3>', '<h3>Une belle réputation, une présence en ligne banale.</h3>')
    sub('<h3>A clear point of view that nobody sees.</h3>', '<h3>Un vrai point de vue, que personne ne voit.</h3>')
    sub('Referrals and real standing among your peers, yet none of it shows when a patient searches for you. Authority built over a career has to be translated into content a search engine can read, or it stays invisible.',
        'Des recommandations et une vraie estime de vos confrères, mais rien de tout cela n’apparaît quand un patient vous cherche. Une autorité construite sur toute une carrière doit être traduite en contenus qu’un moteur de recherche sait lire, sinon elle reste invisible.')
    sub('Word of mouth works, but your website and social media undersell it. Coherent positioning is what lets an earned reputation support a premium practice instead of reading as entry-level.',
        'Le bouche-à-oreille fonctionne, mais votre site et vos réseaux ne sont pas à la hauteur. C’est un positionnement cohérent qui permet à une réputation méritée de porter un cabinet haut de gamme, au lieu de passer pour une offre d’entrée de gamme.')
    sub('You have real convictions about how a treatment should be done, and none of them are public. An unexpressed point of view builds no reputation. Content is what turns it into one.',
        'Vous avez de vraies convictions sur la manière de pratiquer un traitement, mais aucune n’est publique. Un point de vue qui ne s’exprime pas ne construit aucune réputation. C’est le contenu qui la lui donne.')
    sub('aria-label="Direction: Authority to Visibility to Legacy"', 'aria-label="Orientation : Autorité, Visibilité, Héritage"')
    sub('aria-label="Direction: Reputation to Positioning to Premium"', 'aria-label="Orientation : Réputation, Positionnement, Premium"')
    sub('aria-label="Direction: Point of view to Content to Reputation"', 'aria-label="Orientation : Point de vue, Contenu, Réputation"')
    for en_, fr_ in (('Authority', 'Autorité'), ('Visibility', 'Visibilité'), ('Legacy', 'Héritage'), ('Reputation', 'Réputation'), ('Positioning', 'Positionnement'), ('Point of view', 'Point de vue'), ('Content', 'Contenu')):
        fr = fr.replace('<b>%s</b>' % en_, '<b>%s</b>' % fr_)
    fr = fr.replace('data-more="Read more" data-less="Close">Read more <i', 'data-more="Lire la suite" data-less="Réduire">Lire la suite <i')
    sub('alt="Bright aesthetic treatment room with a treatment chair and a round mirror"', 'alt="Salle de soins esthétique lumineuse avec un fauteuil de soin et un miroir rond"')
    sub('alt="Close-up of lips and skin in soft natural light"', 'alt="Gros plan sur des lèvres et une peau en lumière naturelle douce"')
    sub('alt="Conference room with a screen reading “Aesthetic Medicine Today”"', 'alt="Salle de conférence avec un écran « Aesthetic Medicine Today »"')
    sub('<p class="st-q">Recognise yourself? Let’s talk.</p>', '<p class="st-q">Vous vous reconnaissez ? Parlons-en.</p>')
    sub('These situations are illustrative composites drawn from Kinassay Lab’s experience of the sector. They are not client case studies and describe no real person’s practice.',
        'Ces situations sont des illustrations composites, tirées de l’expérience de Kinassay Lab dans le secteur. Ce ne sont pas des études de cas clients et elles ne décrivent la pratique d’aucune personne réelle.')

    # ---------- 06 founder ----------
    sub('<span class="t">Founder</span>', '<span class="t">Fondatrice</span>')
    sub('alt="Anissa Sabrina Briki, founder of Kinassay Lab: close-up portrait on a cream background, captioned “Founder, Anissa” and “Strategy, growth, experience for aesthetic practices”"', 'alt="Anissa Sabrina Briki, fondatrice de Kinassay Lab : portrait rapproché sur fond crème, avec les mentions « Founder, Anissa » et « Strategy, growth, experience for aesthetic practices »"')
    sub('Built from inside aesthetic medicine.', 'Née au cœur de la médecine esthétique.')
    sub('<p><span class="pq">“Exceptional medical expertise does not, on its own, create an exceptional digital presence.”</span></p>',
        '<p><span class="pq">« Une expertise médicale exceptionnelle ne crée pas, à elle seule, une présence digitale exceptionnelle. »</span></p>')
    sub('<p>Kinassay Lab was born from this observation.</p>', '<p>C’est de ce constat qu’est née Kinassay Lab.</p>')
    sub('<p>My experience at FILLMED Laboratories immersed me in the world of aesthetic medicine — working alongside practitioners, understanding the patient journey, and the challenges of growing a practice.</p><p>Before that, at Google and GroupM, I built my expertise in digital strategy and growth across beauty, luxury and international markets.</p><p>Kinassay Lab was born at the intersection of these two worlds: an understanding of aesthetic medicine and expertise in digital growth.</p>\n        <p>Today, I work personally with every practice, with one ambition: to raise their visibility and authority to the level of their expertise.</p>',
        '<p>Mon expérience chez FILLMED Laboratories m’a plongée au cœur de la médecine esthétique — aux côtés des praticiens, au plus près des parcours patients et des enjeux de développement des cabinets.</p><p>Avant cela, chez Google et GroupM, j’ai construit mon expertise en stratégie et croissance digitale, entre beauté, luxe et marchés internationaux.</p><p>Kinassay Lab est née à la rencontre de ces deux univers : la compréhension de la médecine esthétique et l’expertise du digital.</p>\n        <p>Aujourd’hui, j’accompagne chaque cabinet personnellement, avec une même ambition : élever sa visibilité et son autorité à la hauteur de son expertise.</p>')
    sub('<span class="muted">· Founder · Strategy &amp; Growth</span>', '<span class="muted">· Fondatrice · Stratégie &amp; Croissance</span>')
    sub('Talk to the founder <i class="ar"></i>', 'Échanger avec la fondatrice <i class="ar"></i>')
    sub('<a class="tl f-read" href="insights/why-i-created-raisey-lab/">Why I created Kinassay Lab <i class="ar"></i></a>', '<a class="tl f-read" href="insights/pourquoi-j-ai-cree-kinassay-lab/">Pourquoi j’ai créé Kinassay Lab <i class="ar"></i></a>')
    sub('My LinkedIn profile <i class="ar"></i>', 'Mon profil LinkedIn <i class="ar"></i>')
    sub('<a class="tl" href="insights/aesthetic-medicine-patient-journey/">How patients really choose a practice <i class="ar"></i></a>', '<a class="tl" href="insights/parcours-patient-medecine-esthetique/">Comment les patients choisissent vraiment un praticien <i class="ar"></i></a>')
    sub('aria-label="Three worlds"', 'aria-label="Trois univers"')
    sub('<p class="cs">Aesthetic medicine</p>', '<p class="cs">Médecine esthétique</p>')
    sub('<p class="cs">Digital growth&nbsp;· Beauty&nbsp;· Luxury</p>', '<p class="cs">Croissance digitale&nbsp;· Beauté&nbsp;· Luxe</p>')
    sub('<h3>Paris&nbsp;· London&nbsp;· International</h3>', '<h3>Paris&nbsp;· Londres&nbsp;· International</h3>')
    sub('<p class="cs">Multi-market experience</p>', '<p class="cs">Expérience multi-marchés</p>')
    sub('<figcaption class="f-cap"><span>You built it.</span> <em>We raise it.</em></figcaption>', '<figcaption class="f-cap"><span>Même expertise.</span> <em>Un rayonnement plus large.</em></figcaption>')

    # ---------- 07 founding partners ----------
    sub('<span class="t"><span class="fp-lt">Founding partners</span><span class="fp-dash"> — </span><span class="nb">Paris · London · Dubai</span></span>', '<span class="t"><span class="fp-lt">Partenaires fondateurs</span><span class="fp-dash"> — </span><span class="nb">Paris · Londres · Dubaï</span></span>')
    sub('aria-label="Founding partner benefits. Swipe, or use the arrows."', 'aria-label="Avantages partenaires fondateurs. Faites défiler, ou utilisez les flèches."')
    sub('aria-label="Previous"', 'aria-label="Précédent"')
    sub('aria-label="Next"', 'aria-label="Suivant"')
    sub('<span class="a">A closer way</span> <span class="b">of working.</span>', '<span class="a">Une manière de travailler</span> <span class="b">plus proche.</span>')
    sub('Six practices. Direct collaboration.<br>Growth built around your practice.', 'Six cabinets. Une collaboration directe.<br>Une croissance pensée autour de votre cabinet.')
    sub('Kinassay Lab is opening its first six partnerships. Each collaboration begins with a conversation to understand your practice, positioning and priorities — followed by a personalised Kinassay Review to define what to raise, and in what order.',
        'Kinassay Lab ouvre ses six premiers partenariats. Chaque collaboration commence par un échange pour comprendre votre pratique, votre positionnement et vos priorités — suivi d’un Kinassay Review personnalisé pour définir ce qu’il faut élever, et dans quel ordre.')
    sub('<span class="m">Practices<br>only</span><span class="d">Founding<br>Partners</span>', '<span class="m">Six cabinets<br>seulement</span><span class="d">Partenaires<br>fondateurs</span>')
    sub('<b>01</b> — Know what to raise</span><h3>Your Kinassay Review</h3><p>We look at what you’ve built, where it stands today, and what deserves to be raised next.</p>',
        '<b>01</b> — Partir de la bonne analyse</span><h3>Votre Kinassay Review</h3><p>Après un premier échange, nous analysons l’état réel de votre présence digitale et définissons les écarts, les opportunités et les recommandations.</p>')
    sub('<b>02</b> — Built around your practice</span><h3>Founding Partner Conditions</h3><p>No predefined package. Your priorities, scope and strategy are shaped around what your practice actually needs, with preferred conditions reserved for our first six partners.</p>',
        '<b>02</b> — Sur mesure pour votre cabinet</span><h3>Conditions partenaire fondateur</h3><p>Pas d’offre toute faite. Vos priorités, votre périmètre et votre stratégie sont définis selon ce dont votre cabinet a réellement besoin, avec des conditions privilégiées réservées à nos six premiers partenaires.</p>')
    sub('<b>03</b> — Direct collaboration</span><h3>Work directly with the founder</h3><p>Strategy, creative direction and key decisions are handled directly with the founder of Kinassay Lab — from the first conversation to implementation.</p>',
        '<b>03</b> — Un échange direct</span><h3>Travaillez directement avec la fondatrice</h3><p>Stratégie, direction créative et décisions clés se traitent directement avec la fondatrice de Kinassay Lab — du premier échange jusqu’à la mise en œuvre.</p>')
    sub('<p class="lb">Founding partnership</p>', '<p class="lb">Partenariat fondateur</p>')
    sub('<span>Your expertise is already established.</span> <em>Now let’s raise it.</em>', '<span>Votre expertise est déjà établie.</span> <em>Construisons la présence qui lui ressemble.</em>')
    sub('Six founding partnerships across <span class="nb">Paris · London · Dubai.</span>', 'Six partenariats fondateurs entre <span class="nb">Paris · Londres · Dubaï.</span>')
    sub('Become a founding partner <i class="ar"></i>', 'Devenir partenaire fondateur <i class="ar"></i>')
    sub('<span>Kinassay Scan</span><span>First conversation</span><span>Kinassay Review</span><span>Transformation</span><span>Ongoing Growth</span>', '<span>Kinassay Scan</span><span>Premier échange</span><span>Kinassay Review</span><span>Transformation</span><span>Croissance continue</span>')

    # ---------- 08 contact ----------
    sub('<span class="t">Let’s raise what you’ve built</span>', '<span class="t">Construisons votre présence</span>')
    sub('<h2 id="c-h">Tell us what<br> you’ve built.</h2>', '<h2 id="c-h">Parlons de votre cabinet.</h2>')
    sub('Tell us a little about your clinic and we’ll reply within two business days to arrange a first conversation.', 'Présentez-nous votre clinique en quelques lignes : nous vous répondons sous deux jours ouvrés pour convenir d’un premier échange.')
    sub('<label for="cf-name">Name <span', '<label for="cf-name">Nom <span')
    sub('placeholder="Dr. Amara Okafor" autocomplete="name" required data-err="Please add your name."', 'placeholder="Dr Marie Dupont" autocomplete="name" required data-err="Merci d’indiquer votre nom."')
    sub('<label for="cf-clinic">Clinic <span', '<label for="cf-clinic">Clinique <span')
    sub('placeholder="Okafor Aesthetics" autocomplete="organization" required data-err="Please add your clinic."', 'placeholder="Clinique Dupont Esthétique" autocomplete="organization" required data-err="Merci d’indiquer votre clinique."')
    sub('Phone <span class="o">(optional)</span>', 'Téléphone <span class="o">(facultatif)</span>')
    sub('placeholder="07…"', 'placeholder="06…"')
    sub('What would you most like to improve? <span class="o">(optional)</span>', 'Qu’aimeriez-vous améliorer en priorité ? <span class="o">(facultatif)</span>')
    sub('placeholder="Type your message…"', 'placeholder="Votre message…"')
    sub('Required. Everything else is optional. We use these details only to reply to your enquiry and to arrange a first conversation. <a class="link" href="privacy.html">Privacy Policy</a>',
        'Obligatoire. Le reste est facultatif. Ces informations servent uniquement à répondre à votre demande et à convenir d’un premier échange. <a class="link" href="confidentialite.html">Politique de confidentialité</a>')
    sub('<h3>Thank you. We’ll be in touch within two business days.</h3><p class="muted">Your message is with us.</p>', '<h3>Merci. Nous vous répondons sous deux jours ouvrés.</h3><p class="muted">Votre message est bien arrivé.</p>')
    sub('<h3>Expertise, elevated.</h3>', '<h3>Un avenir plus visible pour votre cabinet.</h3>')
    sub('<p class="mantra"><span>Be found</span><span>Be trusted</span><span>Be chosen</span></p>', '<p class="mantra"><span>Être trouvé</span><span>Inspirer confiance</span><span>Être choisi</span></p>')

    # ---------- footer ----------
    sub('<li><a href="#contact">Contact</a></li>', '<li><a href="#contact">Contact</a></li>')
    sub('<a class="lg" href="privacy.html">Privacy Policy</a><a class="lg" href="privacy.html#legal-notice">Legal notice</a><span>Paris · London · Dubai · Expertise, elevated. © <span id="yr">2026</span> Kinassay Lab. All rights reserved.</span>',
        '<a class="lg" href="confidentialite.html">Politique de confidentialité</a><a class="lg" href="confidentialite.html#mentions">Mentions légales</a><span>Paris · Londres · Dubaï · Un standard plus élevé de présence digitale. © <span id="yr">2026</span> Kinassay Lab. Tous droits réservés.</span>')

    # ---------- JS copy ----------
    copy_fr = r'''const COPY = {
  form:{required:'Merci de renseigner ce champ.',email:'Merci de saisir une adresse e-mail valide.',send:'Votre demande n’a pas pu être envoyée. Merci de réessayer dans un instant.',sendScan:'Nous n’avons pas pu envoyer vos résultats. Merci de réessayer dans un instant.',sendScanEmail:'Nous n’avons pas pu envoyer vos résultats. Réessayez, ou écrivez à {email}.',orEmail:' Vous pouvez aussi écrire à {email}.',notConnected:'Ce formulaire n’est pas encore relié à une boîte mail : rien n’a été envoyé. (Définissez FORM_ENDPOINT avant la mise en ligne.)',sending:'Envoi…'},
  tiers:{established:{label:'Établi'},potential:{label:'Fort potentiel'},elevate:{label:'À renforcer'}},
  scan:{
    label:'Kinassay Scan',
    progress:'Question {n} sur {total}',back:'Retour',next:'Continuer',finish:'Voir mon premier aperçu',restart:'Refaire le Scan',other:'Précisez',
    q:[
      {id:'medical',dim:'medical',facet:'medical',t:'single',q:'Lorsqu’un nouveau patient tape votre nom en ligne, que retient-il en premier, selon vous ?',o:[['expertise','Mon expertise et ce pour quoi l’on me reconnaît',3],['treatments','Les traitements que je propose',2],['practical','Surtout des informations pratiques',1],['depends','Cela dépend d’où il me trouve',1],['unsure','Je ne sais pas ce qu’il voit en premier',0]]},
      {id:'digital',dim:'digital',facet:'digital',t:'single',q:'Quand avez-vous travaillé pour la dernière fois sur votre présence Google et vos avis patients ?',o:[['month','Au cours du dernier mois',3],['recent','Ces 3 à 6 derniers mois',2],['old','Il y a plus de 6 mois',1],['unmanaged','Des avis arrivent, mais nous ne les gérons pas activement',1],['unsure','Je ne sais pas',0]]},
      {id:'brand',dim:'brand',facet:'brand',t:'single',q:'Votre présence en ligne reflète-t-elle fidèlement votre cabinet d’aujourd’hui ?',o:[['aligned','Oui — elle correspond à ce que nous sommes aujourd’hui',3],['mostly','Globalement, mais certains éléments ont vieilli',2],['image','Les informations sont là, mais l’image gagnerait à être plus forte',1],['evolved','Pas vraiment — nous avons évolué depuis',0],['never','Je n’y ai jamais vraiment réfléchi',0]]},
      {id:'search',dim:'search',facet:'search',t:'single',q:'Savez-vous comment vos nouveaux patients vous découvrent ?',o:[['tracked','Oui — nous le suivons précisément',3],['idea','J’en ai une bonne idée, mais nous ne le mesurons pas précisément',2],['wom','Surtout par le bouche-à-oreille',1],['several','Ils semblent venir de plusieurs sources',1],['dontknow','Je ne sais pas vraiment',0]]},
      {id:'content',dim:'content',facet:'contentPov',t:'single',q:'Quand avez-vous partagé en ligne, pour la dernière fois, votre propre point de vue médical ?',o:[['month','Au cours du dernier mois',3],['quarter','Ces 3 derniers mois',2],['older','Il y a plus de 3 mois',1],['clinic','Nous publions surtout des traitements, des résultats ou l’actualité du cabinet',1],['rare','Je publie rarement du contenu',0]]},
      {id:'strategy',dim:'content',facet:'contentStrategy',t:'single',q:'Lorsque vous créez du contenu pour votre cabinet, qu’est-ce qui guide principalement ce que vous publiez ?',o:[['clear','Une stratégie éditoriale claire, construite autour de mon expertise et de mes objectifs',3],['themes','Quelques territoires éditoriaux définis que nous développons régulièrement',2],['clinic','Les traitements, résultats et actualités du cabinet',1],['trends','Les tendances, l’inspiration ou les sujets du moment',1],['none','Nous publions sans ligne éditoriale définie / nous publions rarement',0]]},
      {id:'journey',dim:'journey',facet:'journeyBooking',t:'single',q:'Un patient vous découvre ce soir et souhaite un rendez-vous. Que se passe-t-il ensuite ?',o:[['direct','Il comprend l’offre et réserve directement',3],['followup','Il demande un rendez-vous et mon équipe le rappelle rapidement',2],['contact','Il doit appeler ou nous écrire',1],['depends','Cela dépend d’où il nous a trouvés',1],['unsure','Je ne suis pas tout à fait sûr(e)',0]]},
      {id:'lead',dim:'journey',facet:'journeyLead',t:'single',q:'Lorsqu’un patient potentiel vous contacte sans prendre rendez-vous immédiatement, que se passe-t-il généralement ensuite ?',o:[['process','Il entre dans un processus de suivi structuré',3],['manual','Notre équipe le relance, mais principalement manuellement',2],['depends','Le suivi dépend de la demande ou de la personne qui la reçoit',1],['wait','Nous attendons généralement que le patient revienne vers nous',1],['unsure','Je ne sais pas précisément ce qui se passe après la demande',0]]},
      {id:'crm',dim:'journey',facet:'journeyRelationship',t:'single',q:'Au-delà du rendez-vous, comment entretenez-vous la relation avec vos patients et prospects ?',o:[['structured','Nous avons une stratégie CRM et relationnelle structurée, avec des suivis ciblés et des campagnes e-mail',3],['regular','Nous communiquons régulièrement, mais avec peu de segmentation ou d’automatisation',2],['appointments','Nous communiquons principalement autour des rendez-vous ou de certains traitements',1],['manual','Le suivi est surtout manuel et ponctuel',1],['none','Nous n’avons pas encore de stratégie de suivi ou d’e-mailing structurée',0]]},
      {id:'growth',t:'multi',q:'Que souhaiteriez-vous développer en priorité dans les 12 prochains mois ?',hint:'Plusieurs choix possibles.',o:[['patients','Plus de patients qualifiés'],['visibility','Ma visibilité'],['authority','Mon autorité médicale'],['social','Ma présence sur les réseaux sociaux'],['retention','La fidélisation de mes patients'],['treatment','Un traitement ou un acte en particulier'],['team','Mon cabinet ou mon équipe'],['market','Un nouveau lieu d’exercice ou un nouveau marché']]},
      {id:'treatments',t:'multi',q:'Quels traitements ou actes aimeriez-vous développer en priorité ?',hint:'Plusieurs choix possibles.',o:[['botox','Botox / Neuromodulateurs'],['fillers','Injections de comblement (fillers)'],['skinboosters','Skin boosters'],['regenerative','Traitements régénératifs'],['lasers','Lasers et dispositifs à énergie'],['body','Soins du corps'],['hair','Traitements capillaires'],['dermatology','Dermatologie'],['surgery','Chirurgie'],['other','Autre',null,'other'],['none','Aucun en particulier — je veux développer l’ensemble du cabinet',null,'exclusive']]}
    ],
    result:{
      title:'Votre premier aperçu',dims:'Par dimension',
      leg:{elevate:'Une vraie marge de progression.',potential:'De bonnes bases, avec de la marge pour aller plus loin.',established:'Un atout solide à exploiter.'},
      disclaimer:'Une première lecture qualitative, fondée sur vos propres réponses. Ce n’est pas une mesure médicale, clinique ou scientifique.',
      /* SCAN_COPY:begin (generated from scan_copy.json — do not edit here) */
      /* SCAN_COPY:end */
    }
  }
};'''
    m = re.search(r'const COPY = \{.*?\n\};', fr, re.S)
    if not m:
        sys.exit('COPY block not found')
    fr = fr[:m.start()] + copy_fr + fr[m.end():]
    fr = scan_copy.inject(fr, 'fr')
    if "o?'Close':'Menu'" not in fr:
        sys.exit('menu label code not found')
    fr = fr.replace("o?'Close':'Menu'", "o?'Fermer':'Menu'")
    fr = fr.replace("/* ---------- copy (English; a French dictionary can replace this object) ---------- */", "/* ---------- copy (français) ---------- */")

    # ---------- FR-only typographic tweaks (longer words) ----------
    fr_css = None  # French uses exactly the English styles; no overrides needed

    # ---------- language switch + alternates (both pages) ----------
    def add_switch(html, cur):
        en_href = 'index.html' if cur == 'en' else '../index.html'
        fr_href = 'fr/index.html' if cur == 'en' else 'index.html'
        def sw(cls):
            e = '<span aria-current="true" lang="en">EN</span>' if cur == 'en' else '<a href="%s" hreflang="en" lang="en" aria-label="English">EN</a>' % en_href
            f = '<span aria-current="true" lang="fr">FR</span>' if cur == 'fr' else '<a href="%s" hreflang="fr" lang="fr" aria-label="Français">FR</a>' % fr_href
            return '<div class="langsw %s" role="group" aria-label="%s">%s<i aria-hidden="true"></i>%s</div>' % (cls, 'Langue' if cur == 'fr' else 'Language', e, f)
        html = html.replace('    <div style="display:flex;align-items:center;gap:16px">\n      <a class="btn head-cta"', '    <div style="display:flex;align-items:center;gap:16px">\n      ' + sw('h') + '\n      <a class="btn head-cta"', 1)
        html = html.replace('      </ul>\n      <a class="btn" href="#contact" data-book>', '      </ul>\n      ' + sw('m') + '\n      <a class="btn" href="#contact" data-book>', 1)
        alts = ('<link rel="alternate" hreflang="en" href="%s">\n<link rel="alternate" hreflang="fr" href="%s">\n<link rel="alternate" hreflang="x-default" href="%s">\n'
                % (en_href, fr_href, en_href))
        html = html.replace('<link rel="icon"', alts + '<link rel="icon"', 1)
        css = '''.langsw{display:inline-flex;align-items:center;gap:2px;font:600 12px/1 var(--sans);letter-spacing:.14em}
.langsw a,.langsw span{display:inline-flex;align-items:center;justify-content:center;min-width:40px;min-height:44px;text-decoration:none;color:var(--muted)}
.langsw [aria-current]{color:var(--ink)}
.langsw i{width:1px;height:14px;background:var(--line-strong)}
.langsw a:hover{color:var(--rasp)}
.langsw.m{display:none;margin-top:18px}
@media (max-width:1000px){.langsw.h{display:none}.mobile .langsw.m{display:inline-flex}}
'''
        if '.langsw{' not in html:
            html = html.replace('/* ============ HEADER ============ */', css + '/* ============ HEADER ============ */', 1)
        return html

    fr = re.sub(r'\s*<div class="langsw [hm]".*?</div>', '', fr, flags=re.S)
    fr = re.sub(r'<link rel="alternate" hreflang="[^"]+" href="[^"]+">\n', '', fr)
    if 'class="langsw' not in en:
        en2 = add_switch(en, 'en')
        open(SRC, 'w', encoding='utf-8').write(en2)
        # regenerate FR from the switched English so both stay in sync
        fr = add_switch(fr, 'fr')
    else:
        fr = add_switch(fr, 'fr')

    os.makedirs('fr', exist_ok=True)
    open('fr/index.html', 'w', encoding='utf-8').write(fr)
    print('fr/index.html written (%d chars)' % len(fr))


if __name__ == '__main__':
    main()
