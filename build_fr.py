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
    fr = fr.replace('href="insights/index.html">Insights<', 'href="../insights/index.html" hreflang="en">Insights<')   # Insights are in English
    sub('<a class="skip" href="#main">Skip to content</a>', '<a class="skip" href="#main">Aller au contenu</a>')
    sub('aria-label="Kinassay Lab, top"', 'aria-label="Kinassay Lab, haut de page"')
    sub('<nav class="nav" aria-label="Main">', '<nav class="nav" aria-label="Principale">')
    sub('href="#work">Studies<', 'href="#work">Études<')
    sub('href="#about">About<', 'href="#about">À propos<')
    sub('Book a first meeting <i class="ar"></i>', 'Réserver un premier rendez-vous <i class="ar"></i>')
    sub('<li><a href="#contact">Book a first meeting</a></li>', '<li><a href="#contact">Réserver un premier rendez-vous</a></li>')
    sub('<nav aria-label="Footer">', '<nav aria-label="Pied de page">')
    sub('<span class="mt">Menu</span>', '<span class="mt">Menu</span>')

    # ---------- hero + new homepage sequence (2026-09) ----------
    sub('<p class="eyebrow rise" style="--i:0">When aesthetic medicine meets digital.</p>', '<p class="eyebrow rise" style="--i:0">Quand la médecine esthétique rencontre le digital.</p>')
    sub('<h1 id="hx-h" class="rise" style="--i:1">Your expertise<br> deserves<br> <em>to be seen.</em></h1>', '<h1 id="hx-h" class="rise" style="--i:1">Votre expertise<br> mérite<br> <em>d’être vue.</em></h1>')
    sub('Kinassay Lab helps aesthetic doctors and clinics be found, trusted and chosen by the right patients, with a digital presence that matches their medical expertise.',
        'Kinassay Lab aide les médecins et cliniques esthétiques à être trouvés, à inspirer confiance et à être choisis par les bons patients, grâce à une présence digitale à la hauteur de leur expertise médicale.')
    sub('30 minutes · Free · No commitment', '30 minutes · Gratuit · Sans engagement')
    sub('<p class="hx-alt">Not ready to talk yet? <a href="#kinassay-scan" data-startdiag data-interest="presence-scan">Take the free Kinassay Scan</a> <span class="nb">(about 4 minutes)</span></p>',
        '<p class="hx-alt">Envie d’explorer d’abord ? <a href="#kinassay-scan" data-startdiag data-interest="presence-scan">Faites le Kinassay Scan gratuit</a> <span class="nb">(environ 4 minutes)</span></p>')
    sub('alt="Architectural detail of an aesthetic medicine clinic in warm natural light"', 'alt="Détail architectural d’une clinique de médecine esthétique dans une lumière naturelle chaude"')
    sub('<ol class="hx-steps" aria-label="The patient journey"><li>Search</li><li>Discover</li><li>Trust</li><li>Choose</li></ol>', '<ol class="hx-steps" aria-label="Le parcours patient"><li>Recherche</li><li>Découverte</li><li>Confiance</li><li>Choix</li></ol>')
    sub('aria-label="Close the Kinassay Scan">Close <span', 'aria-label="Fermer le Kinassay Scan">Fermer <span')
    sub('<p class="hx-eb hx-center">Prefer to explore first?</p>', '<p class="hx-eb hx-center">Envie d’explorer d’abord ?</p>')
    sub('<h2 id="hx-pillars-h" class="hx-scan-h hx-center">Take the free Kinassay Scan.</h2>', '<h2 id="hx-pillars-h" class="hx-scan-h hx-center">Faites le Kinassay Scan gratuit.</h2>')
    sub('<h3>Visibility</h3><p>SEO · Search<br> Being found</p>', '<h3>Visibilité</h3><p>SEO · Recherche<br> Être trouvé</p>')
    sub('<h3>Authority</h3><p>Expertise · Reputation<br> Trust</p>', '<h3>Autorité</h3><p>Expertise · Réputation<br> Confiance</p>')
    sub('<h3>Brand</h3><p>Positioning · Identity<br> Differentiation</p>', '<h3>Marque</h3><p>Positionnement · Identité<br> Différenciation</p>')
    sub('<h3>Patient Journey</h3><p>Website · UX<br> Conversion</p>', '<h3>Parcours patient</h3><p>Site web · UX<br> Conversion</p>')
    sub('<h3>Growth</h3><p>Acquisition · CRM<br> Retention</p>', '<h3>Croissance</h3><p>Acquisition · CRM<br> Fidélisation</p>')
    sub('<h3>Editorial Potential</h3><p>Content · Thought leadership<br> Differentiation</p>', '<h3>Potentiel éditorial</h3><p>Contenu · Prise de parole d’expert<br> Différenciation</p>')
    sub('aria-label="The six dimensions read by the Scan"', 'aria-label="Les six dimensions lues par le Scan"')

    # ---------- 02 review ----------
    sub('<p class="eyebrow">Your Kinassay Scan</p>', '<p class="eyebrow">Votre Kinassay Scan</p>')
    sub('Your results at a glance.', 'Vos résultats en un coup d’œil.')
    sub('A first read of your answers across six key dimensions.<span class="basis">Based on your answers · Not an audit of your digital presence</span>', 'Une première lecture de vos réponses sur six dimensions clés.<span class="basis">Basé sur vos réponses · Pas sur un audit de votre présence digitale</span>')
    sub('Understanding your results', 'Comprendre vos résultats')
    sub('Each dimension is read on three levels.', 'Chaque dimension se lit sur trois niveaux.')
    sub('<button class="btn" type="button" id="takeDiag">Start my Kinassay Scan <i class="ar"></i></button>', '<button class="btn" type="button" id="takeDiag">Démarrer mon Kinassay Scan <i class="ar"></i></button>')
    sub('<p class="hx-intro">Eleven questions about your practice. Your personalised reading across six dimensions, sent to you by email within minutes.</p>',
        '<p class="hx-intro">Onze questions sur votre cabinet. Votre lecture personnalisée sur six dimensions, envoyée par e-mail en quelques minutes.</p>')
    sub('Free · Automated · Based on your answers · About 4 minutes', 'Gratuit · Automatisé · Basé sur vos réponses · Environ 4 minutes')
    sub('The Kinassay Scan needs JavaScript. You can book a first meeting in the next section.',
        'Le Kinassay Scan nécessite JavaScript. Vous pouvez réserver un premier rendez-vous dans la section suivante.')
    sub('</svg>Scan complete</p>', '</svg>Scan terminé</p>')
    sub('Where should we send your full Scan results?', 'Recevez votre Kinassay Scan personnalisé.')
    # 2026-10: no email gate on the French site either: the first insight shows right after the questions (owner request)
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
    sub('Send my message <i class="ar"></i></button>', 'Envoyer mon message <i class="ar"></i></button>')
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
    for sid in ('sf-spec',):
        pat = re.compile(r'(<select class="input" id="%s" name="specialty">).*?(</select>)' % sid, re.S)
        if not pat.search(fr):
            sys.exit('select not found: ' + sid)
        fr = pat.sub(lambda m: m.group(1) + opts + m.group(2), fr)

    # ---------- 04 services (localized derivative of the locked English component) ----------
    sub('<p class="lab">Our expertise</p>', '<p class="lab">Notre expertise</p>')
    sub('<span class="l1">How we raise</span> <span class="l2">your <em>presence.</em></span>', '<span class="l1">Comment nous bâtissons</span> <span class="l2">votre <em>présence.</em></span>')
    sub('From visibility to patient experience, we build the digital strategy that shapes how an aesthetic practice is found, perceived and chosen.',
        'De la visibilité à l’expérience patient, nous bâtissons la stratégie digitale qui façonne la manière dont un cabinet esthétique est trouvé, perçu et choisi.')
    sub('<p class="mc"><span>Be found.</span><span>Be trusted.</span><span>Be chosen.</span></p>', '<p class="mc"><span>Être trouvé.</span><span>Inspirer confiance.</span><span>Être choisi.</span></p>')
    sub('<span class="nm">Visibility</span>', '<span class="nm">Présence digitale</span>')
    sub('Search · Google · Social · Reputation', 'Recherche · Google · Réseaux · Réputation')
    sub('Raise your visibility where patients are already looking.', 'Soyez visible là où vos patients cherchent déjà.')
    sub('<p class="p-stg">Be found</p>', '<p class="p-stg">Être trouvé</p>')
    sub('<span class="stg">Be found</span>', '<span class="stg">Être trouvé</span>')
    sub('<span class="stg">Build trust, shape the experience</span>', '<span class="stg">Inspirer confiance, soigner l’expérience</span>')
    sub('<span class="stg">Stay visible</span>', '<span class="stg">Rester visible</span>')
    sub('<span class="stg">Build authority</span>', '<span class="stg">Bâtir l’autorité</span>')
    sub('<li>Local search &amp; SEO</li><li>Google Business Profile</li><li>Social presence</li><li>Reviews &amp; reputation</li>',
        '<li>Référencement local et SEO</li><li>Fiche Google Business</li><li>Réseaux sociaux</li><li>Avis et e-réputation</li>')
    sub('<span class="nm">Website &amp; Patient Journey</span>', '<span class="nm">Site web et parcours patient</span>')
    sub('Positioning · UX/UI · Booking · SEO foundations', 'Positionnement · UX/UI · Rendez-vous · Bases SEO')
    sub('Turn expertise into an online experience patients can understand and trust.', 'Faites de votre expertise une expérience en ligne que les patients comprennent — et en laquelle ils ont confiance.')
    sub('<p class="p-stg">Build trust, shape the experience</p>', '<p class="p-stg">Inspirer confiance, soigner l’expérience</p>')
    sub('<li>Positioning &amp; brand direction</li><li>Website design &amp; build</li><li>Booking &amp; patient journey</li><li>SEO foundations</li>',
        '<li>Positionnement et identité de marque</li><li>Conception et développement du site</li><li>Prise de rendez-vous et parcours patient</li><li>Bases SEO</li>')
    sub('<span class="nm">Sustained Visibility</span>', '<span class="nm">Présence continue</span>')
    sub('Content · Social · Google · Reputation', 'Contenu · Réseaux · Google · Réputation')
    sub('Keep your practice visible, relevant and rising after launch.', 'Gardez votre présence visible, pertinente et cohérente, bien après le lancement.')
    sub('<p class="p-stg">Stay visible</p>', '<p class="p-stg">Rester visible</p>')
    sub('<li>Editorial content</li><li>Social presence</li><li>Google &amp; reviews</li><li>Performance reporting</li>',
        '<li>Contenu éditorial</li><li>Réseaux sociaux</li><li>Google et avis</li><li>Suivi des performances</li>')
    sub('<span class="nm">Growth &amp; Authority</span>', '<span class="nm">Croissance et autorité</span>')
    sub('Strategy · Analytics · Personal Brand · Content', 'Stratégie · Analytics · Marque personnelle · Contenu')
    sub('Turn visibility into lasting authority and measurable growth.', 'Transformez votre visibilité en autorité durable et en croissance mesurable.')
    sub('<p class="p-stg">Build authority</p>', '<p class="p-stg">Bâtir l’autorité</p>')
    sub('<li>Growth strategy</li><li>Analytics &amp; reporting</li><li>Personal brand</li><li>Thought-leadership content</li>',
        '<li>Stratégie de croissance</li><li>Analytics et reporting</li><li>Marque personnelle</li><li>Contenus d’expertise</li>')
    sub('Discuss this <i class="ar"></i>', 'En parler <i class="ar"></i>')
    sub('<p class="eb">Not sure where to start?</p>', '<p class="eb">Vous ne savez pas par où commencer ?</p>')
    sub('<h3>See what you can raise.</h3>', '<h3>Découvrez ce que révèlent vos réponses.</h3>')
    sub('Start my Kinassay Scan <i class="ar"></i></a>\n    </div>\n  </div>\n</section>', 'Démarrer mon Kinassay Scan <i class="ar"></i></a>\n    </div>\n  </div>\n</section>')

    # ---------- 05 studies ----------
    sub('<h2 id="work-h">Selected studies</h2><span class="r">Illustrative composite analyses · Not client results or real cases</span>',
        '<h2 id="work-h">Études sélectionnées</h2><span class="r">Analyses composites illustratives · Ni résultats clients, ni cas réels</span>')
    studies = [
        ('A Senior Dermatologist, 20 Years in Practice', 'Un dermatologue reconnu, 20 ans de carrière', 'Direction: Authority to Visibility to Legacy', 'Orientation : Autorité, Visibilité, Héritage',
         ['Authority', 'Visibility', 'Legacy'], ['Autorité', 'Visibilité', 'Héritage'],
         'Two decades of referrals and real standing among peers — none of it visible online. The study: authority built over a career has to be translated into content a search engine can read, or it stays invisible.',
         'Vingt ans de recommandations et une vraie estime de ses confrères — mais rien de tout cela n’existe en ligne. L’étude : une autorité construite sur toute une carrière doit être traduite en contenus qu’un moteur de recherche sait lire, faute de quoi elle reste invisible.'),
        ('A Boutique Aesthetic Practice, Mid-Career', 'Un cabinet esthétique confidentiel, à mi-parcours', 'Direction: Reputation to Positioning to Premium', 'Orientation : Réputation, Positionnement, Premium',
         ['Reputation', 'Positioning', 'Premium'], ['Réputation', 'Positionnement', 'Premium'],
         'Strong word-of-mouth, but a generic online presence that undercuts it. The study: coherent positioning is what lets an earned reputation support premium pricing instead of reading as entry-level.',
         'Un bouche-à-oreille solide, mais une présence en ligne banale qui le dessert. L’étude : c’est un positionnement cohérent qui permet à une réputation méritée de soutenir un positionnement premium, au lieu de passer pour une offre d’entrée de gamme.'),
        ('A Nurse Prescriber Building a New Client Base', 'Une infirmière en pratique avancée qui construit sa patientèle', 'Direction: Trust to Authority to Brand', 'Orientation : Confiance, Autorité, Marque',
         ['Trust', 'Authority', 'Brand'], ['Confiance', 'Autorité', 'Marque'],
         'Good reviews, scattered with no throughline. The study: formalising trust signals into a consistent narrative turns scattered proof into an actual brand a patient chooses on purpose.',
         'De bons avis, mais aucun fil conducteur. L’étude : structurer les signaux de confiance en un récit cohérent transforme des preuves éparses en une vraie marque, choisie par les patients en toute connaissance de cause.'),
        ('A Niche Specialist in a Rare Procedure', 'Un spécialiste de niche pour un geste rare', 'Direction: Expertise to Visibility to Acquisition', 'Orientation : Expertise, Visibilité, Acquisition',
         ['Expertise', 'Visibility', 'Acquisition'], ['Expertise', 'Visibilité', 'Acquisition'],
         'Deep expertise, invisible to the exact patients searching for it. The study: specific expertise needs equally specific visibility, or less-qualified providers capture the acquisition instead.',
         'Une expertise pointue, invisible aux patients qui la cherchent précisément. L’étude : une expertise précise appelle une visibilité tout aussi précise, sinon des praticiens moins qualifiés captent les patients à sa place.'),
        ('A Doctor With a Strong Clinical Point of View', 'Un médecin à la vision clinique affirmée', 'Direction: Point of view to Content to Reputation', 'Orientation : Point de vue, Contenu, Réputation',
         ['Point of view', 'Content', 'Reputation'], ['Point de vue', 'Contenu', 'Réputation'],
         'Genuine opinions on how a treatment should be done — none of it public. The study: an unexpressed point of view builds no reputation. Content is what turns it into one.',
         'De vraies convictions sur la manière de pratiquer un traitement — mais aucune n’est publique. L’étude : un point de vue qui ne s’exprime pas ne construit aucune réputation. C’est le contenu qui la lui donne.'),
        ('A Hospital-Affiliated Consultant', 'Un consultant rattaché à un hôpital', 'Direction: Institution to Voice to Influence', 'Orientation : Institution, Voix, Influence',
         ['Institution', 'Voice', 'Influence'], ['Institution', 'Voix', 'Influence'],
         'Visibility entirely borrowed from a faculty bio. The study: an individual voice alongside the institutional one is what lets influence outlast any single affiliation.',
         'Une visibilité entièrement empruntée à une fiche de faculté. L’étude : une voix personnelle aux côtés de la voix institutionnelle permet à l’influence de durer au-delà de toute affiliation.')]
    for t_en, t_fr, al_en, al_fr, ch_en, ch_fr, p_en, p_fr in studies:
        if '<h3>' + t_en + '</h3>' not in fr:
            continue   # study not on the homepage
        sub('<h3>' + t_en + '</h3>', '<h3>' + t_fr + '</h3>')
        sub('aria-label="' + al_en + '"', 'aria-label="' + al_fr + '"')
        grp = lambda c: ''.join('<span class="st"><b>%s</b><i class="ar" aria-hidden="true"></i></span>' % x for x in c[:-1]) + '<b>%s</b>' % c[-1]
        old = grp(ch_en)
        new = grp(ch_fr)
        sub(old, new)
        sub('<p>' + p_en + '</p>', '<p>' + p_fr + '</p>')
    sub('aria-label="Selected studies. Swipe, or use the arrow keys."', 'aria-label="Études sélectionnées. Faites défiler, ou utilisez les flèches du clavier."')
    sub('aria-label="Previous study"', 'aria-label="Étude précédente"')
    sub('aria-label="Next study"', 'aria-label="Étude suivante"')
    sub('</span> Senior dermatologist</p>', '</span> Dermatologue reconnu</p>')
    sub('</span> Boutique practice</p>', '</span> Cabinet confidentiel</p>')
    sub('</span> Niche specialist</p>', '</span> Spécialiste de niche</p>')
    fr = fr.replace('data-more="Read analysis" data-less="Close">Read analysis <i', 'data-more="Lire l’analyse" data-less="Réduire">Lire l’analyse <i')
    sub('alt="Bright aesthetic treatment room with a treatment chair and a round mirror"', 'alt="Salle de soins esthétique lumineuse avec un fauteuil de soin et un miroir rond"')
    sub('alt="Close-up of lips and skin in soft natural light"', 'alt="Gros plan sur des lèvres et une peau en lumière naturelle douce"')
    sub('alt="Treatment tray with instruments beside a treatment chair"', 'alt="Plateau d’instruments à côté d’un fauteuil de soin"')
    sub('These studies are Kinassay Lab’s own thinking: how a range of practitioner profiles could translate real expertise into greater visibility and authority. They are composite illustrations, not case studies of real clients or real individuals, and describe no actual person’s practice.',
        'Ces études sont la réflexion propre de Kinassay Lab : comment différents profils de praticiens pourraient transformer une expertise réelle en davantage de visibilité et d’autorité. Ce sont des illustrations composites — non des études de cas de clients ou de personnes réelles — et elles ne décrivent la pratique d’aucune personne existante.')

    # ---------- 06 founder ----------
    sub('<p class="note f-note">Roles held before founding Kinassay Lab. These are not client references.</p>', '<p class="note f-note">Postes occupés avant la création de Kinassay Lab. Il ne s’agit pas de références clients.</p>')
    sub('<span class="t">Why work with me</span>', '<span class="t">Pourquoi me faire confiance</span>')
    sub('<p>Kinassay Lab brings these two worlds together: an understanding of how aesthetic medicine and its patients work, and the digital skills to make a practice visible and trusted. I work personally with every practice.</p>',
        '<p>Kinassay Lab réunit ces deux univers : la compréhension de la médecine esthétique et de ses patients, et les compétences digitales pour rendre un cabinet visible et digne de confiance. J’accompagne personnellement chaque cabinet.</p>')
    sub('alt="Anissa Sabrina Briki, founder of Kinassay Lab: close-up portrait on a cream background, captioned “Founder, Anissa” and “Strategy, growth, experience for aesthetic practices”"', 'alt="Anissa Sabrina Briki, fondatrice de Kinassay Lab : portrait rapproché sur fond crème, avec les mentions « Founder, Anissa » et « Strategy, growth, experience for aesthetic practices »"')
    sub('Built from inside aesthetic medicine.', 'Née au cœur de la médecine esthétique.')
    sub('<p><span class="pq">“Exceptional medical expertise does not, on its own, create an exceptional digital presence.”</span></p>',
        '<p><span class="pq">« Une expertise médicale exceptionnelle ne crée pas, à elle seule, une présence digitale exceptionnelle. »</span></p>')
    sub('<p>I’m Anissa Sabrina Briki, founder of Kinassay Lab. At FILLMED Laboratories, I worked alongside aesthetic practitioners and saw the realities of growing a practice. Before that, at Google and GroupM, I built digital strategy and growth across beauty, luxury and international markets.</p>',
        '<p>Je suis Anissa Sabrina Briki, fondatrice de Kinassay Lab. Chez FILLMED Laboratories, j’ai travaillé aux côtés des praticiens de la médecine esthétique, au plus près de la réalité du développement d’un cabinet. Auparavant, chez Google et GroupM, j’ai construit des stratégies digitales et de croissance pour la beauté, le luxe et les marchés internationaux.</p>')
    sub('<a class="tl f-read" href="insights/why-i-created-raisey-lab/">Read my story: why I created Kinassay Lab <i class="ar"></i></a>', '<a class="tl f-read" href="../insights/why-i-created-raisey-lab/" hreflang="en">Lire mon histoire : pourquoi j’ai créé Kinassay Lab (en anglais) <i class="ar"></i></a>')
    sub('My LinkedIn profile <i class="ar"></i>', 'Mon profil LinkedIn <i class="ar"></i>')
    sub('aria-label="Three worlds"', 'aria-label="Trois univers"')
    sub('<p class="cs">Aesthetic medicine</p>', '<p class="cs">Médecine esthétique</p>')
    sub('<p class="cs">Digital growth&nbsp;· Beauty&nbsp;· Luxury</p>', '<p class="cs">Croissance digitale&nbsp;· Beauté&nbsp;· Luxe</p>')
    sub('<h3>Paris&nbsp;· London&nbsp;· International</h3>', '<h3>Paris&nbsp;· Londres&nbsp;· International</h3>')
    sub('<p class="cs">Multi-market experience</p>', '<p class="cs">Expérience multi-marchés</p>')
    sub('<figcaption class="f-cap"><span>You built it.</span> <em>We raise it.</em></figcaption>', '<figcaption class="f-cap"><span>Même expertise.</span> <em>Un rayonnement plus large.</em></figcaption>')

    # ---------- 08 contact ----------
    sub('<span class="t">First meeting</span>', '<span class="t">Premier rendez-vous</span>')
    sub('<h2 id="c-h">Book a first<br> meeting.</h2>', '<h2 id="c-h">Réserver un<br> premier <span class="nb">rendez-vous.</span></h2>')
    sub('Thirty minutes, free and without commitment, to talk about your practice and where you want it to go.',
        'Trente minutes, gratuites et sans engagement, pour parler de votre cabinet et de la direction que vous souhaitez lui donner.')
    sub('<li>Your practice, your positioning and your priorities</li>', '<li>Votre cabinet, votre positionnement et vos priorités</li>')
    sub('<li>How patients find and perceive you today</li>', '<li>La façon dont les patients vous trouvent et vous perçoivent aujourd’hui</li>')
    sub('<li>What to raise first, and whether a personalised Kinassay Review makes sense</li>', '<li>Ce qu’il faut renforcer en premier, et si un Kinassay Review personnalisé a du sens pour vous</li>')
    sub('Choose a time <i class="ar"></i>', 'Choisir un créneau <i class="ar"></i>')
    sub('Prefer to write first? Leave a message and we’ll reply within two business days.', 'Vous préférez écrire d’abord ? Laissez-nous un message : nous vous répondons sous deux jours ouvrés.')
    sub('Kinassay Lab is opening six founding partnerships across <span class="nb">Paris, London and Dubai.</span>', 'Kinassay Lab ouvre six partenariats fondateurs entre <span class="nb">Paris, Londres et Dubaï.</span>')
    sub('<label for="cf-name">Name <span', '<label for="cf-name">Nom <span')
    sub('placeholder="Dr. Amara Okafor" autocomplete="name" required data-err="Please add your name."', 'placeholder="Dr Marie Dupont" autocomplete="name" required data-err="Merci d’indiquer votre nom."')
    sub('<label for="cf-clinic">Clinic <span', '<label for="cf-clinic">Clinique <span')
    sub('placeholder="Okafor Aesthetics" autocomplete="organization" required data-err="Please add your clinic."', 'placeholder="Clinique Dupont Esthétique" autocomplete="organization" required data-err="Merci d’indiquer votre clinique."')
    sub('Phone <span class="o">(optional)</span>', 'Téléphone <span class="o">(facultatif)</span>')
    sub('placeholder="07…"', 'placeholder="06…"')
    sub('Required. Phone is optional. We use these details only to reply to you and arrange a first meeting. <a class="link" href="privacy.html">Privacy Policy</a>',
        'Obligatoire. Le téléphone est facultatif. Ces informations servent uniquement à vous répondre et à organiser un premier rendez-vous. <a class="link" href="confidentialite.html">Politique de confidentialité</a>')
    sub('<h3>Thank you. We’ll be in touch within two business days.</h3><p class="muted">Your message is with us.</p>', '<h3>Merci. Nous vous répondons sous deux jours ouvrés.</h3><p class="muted">Votre message est bien arrivé.</p>')
    sub('<h3>Expertise, elevated.</h3>', '<h3>Un avenir plus visible pour votre cabinet.</h3>')
    sub('<p class="mantra"><span>Be found</span><span>Be trusted</span><span>Be chosen</span></p>', '<p class="mantra"><span>Être trouvé</span><span>Inspirer confiance</span><span>Être choisi</span></p>')

    # ---------- footer ----------
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
