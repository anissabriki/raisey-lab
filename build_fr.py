#!/usr/bin/env python3
"""Generates fr/index.html from index.html (English is the source of truth) and wires the EN | FR switch.
Run:  python3 build_fr.py
If an English string changes, the matching entry below fails loudly so the French copy is never silently stale.
Brand terms kept in English on purpose: "Raisey Scan", "Raisey Review".  City names use French exonyms (Londres, Dubaï)."""
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
    sub('<title>Raisey Lab — Digital presence for aesthetic doctors &amp; clinics</title>',
        '<title>Raisey Lab — Présence digitale pour médecins et cliniques esthétiques</title>')
    sub('content="Raisey Lab raises the visibility, authority and patient journey of aesthetic doctors and clinics. Start with the free 4-minute Raisey Scan."',
        'content="Raisey Lab fait de l’expertise médicale une présence digitale que les patients trouvent, à laquelle ils font confiance, et qu’ils choisissent. Commencez par un Raisey Scan gratuit."')
    sub('<meta property="og:title" content="Raisey Lab — You built the expertise. We raise its presence.">',
        '<meta property="og:title" content="Raisey Lab — Vous avez l’expertise. Nous élevons sa présence.">')
    sub('content="Visibility, authority and growth for aesthetic doctors and clinics. Paris · London · Dubai."',
        'content="Présence digitale pour médecins et cliniques esthétiques. Paris · Londres · Dubaï."')
    fr = fr.replace('href="data:image/svg+xml', 'href="data:image/svg+xml')  # favicon is inline, unchanged
    fr = fr.replace('href="fonts/', 'href="../fonts/').replace('url(fonts/', 'url(../fonts/')
    fr = re.sub(r'(?<![\w/.])images/', '../images/', fr)
    fr = re.sub(r'href="(favicon|apple-touch-icon)', r'href="../\1', fr)

    # ---------- chrome ----------
    fr = fr.replace('alt="Anissa Sabrina Briki, founder of Raisey Lab, seated on a cream sofa: editorial portrait captioned “Founder, Anissa”"', 'alt="Anissa Sabrina Briki, fondatrice de Raisey Lab, assise sur un canapé crème : portrait éditorial avec la mention « Founder, Anissa »"')
    fr = fr.replace('<label for="sf-website_url">Leave this field empty</label>', '<label for="sf-website_url">Laissez ce champ vide</label>').replace('<label for="cf-website_url">Leave this field empty</label>', '<label for="cf-website_url">Laissez ce champ vide</label>')
    fr = fr.replace('href="insights/index.html">Insights<', 'href="../insights/index.html" hreflang="en">Insights<')   # Insights are in English
    sub('<a class="skip" href="#main">Skip to content</a>', '<a class="skip" href="#main">Aller au contenu</a>')
    sub('aria-label="Raisey Lab, top"', 'aria-label="Raisey Lab, haut de page"')
    sub('<nav class="nav" aria-label="Main">', '<nav class="nav" aria-label="Principale">')
    sub('href="#work">Work<', 'href="#work">Études<')
    sub('href="#about">About<', 'href="#about">À propos<')
    sub('Start your Scan <i class="ar"></i>', 'Lancer mon Scan <i class="ar"></i>')
    sub('<nav aria-label="Footer">', '<nav aria-label="Pied de page">')
    sub('<span class="mt">Menu</span>', '<span class="mt">Menu</span>')

    # ---------- hero ----------
    sub('Aesthetic medicine — Visibility · Authority · Growth', 'Médecine esthétique — Visibilité · Autorité · Croissance')
    h1_old = re.search(r'<h1 class="rise" style="--i:1">.*?</h1>', fr, re.S).group(0)
    fr = fr.replace(h1_old, typo('<h1 class="rise" style="--i:1">Vous avez<br> l’expertise.<br> <span class="pun"><em>Nous la rendons<br> visible.</em></span></h1>'))
    sub('Your expertise, reputation and experience already exist. Raisey Lab raises their visibility, authority and trust, so the right patients choose you.',
        'Votre expertise, votre réputation et votre expérience existent déjà. Raisey Lab leur donne la visibilité et l’autorité qu’elles méritent, pour que les bons patients puissent vous trouver, vous faire confiance et vous choisir.')
    sub('Start my Raisey Scan <i class="ar"></i></a>\n      <a class="tl" href="#approach">Discover the studio</a>',
        'Démarrer mon Raisey Scan <i class="ar"></i></a>\n      <a class="tl" href="#approach">Découvrir le studio</a>')
    sub('aria-label="Paris, London, Dubai"><span>Paris</span><span>London</span><span>Dubai</span>',
        'aria-label="Paris, Londres, Dubaï"><span>Paris</span><span>Londres</span><span>Dubaï</span>')

    # ---------- 02 review ----------
    sub('<h2 class="h2" id="rv-h">How far could your practice rise?</h2>', '<h2 class="h2" id="rv-h">Que révèle votre présence digitale ?</h2>')
    sub('Six dimensions, four minutes, a first read straight away. Discover where your visibility, authority and patient journey have the greatest room to rise. No email required.',
        'Six dimensions. Quatre minutes. Une première lecture immédiate.<br> Mesurez l’écart entre l’expertise que vous avez construite et la présence que vos patients perçoivent. Identifiez vos priorités en matière de visibilité, d’autorité et d’expérience patient.')
    sub('aria-label="The six dimensions of the Raisey Scan"', 'aria-label="Les six dimensions du Raisey Scan"')
    for a, b in [('Medical Authority', 'Autorité médicale'), ('Digital Authority', 'Autorité digitale'), ('Brand Expression', 'Expression de marque'),
                 ('Discoverability', 'Visibilité'), ('Content Potential', 'Potentiel éditorial'), ('Patient Journey</span>', 'Parcours patient</span>')]:
        sub('<span class="dt">' + a, '<span class="dt">' + b) if not a.endswith('</span>') else sub('<span class="dt">' + a, '<span class="dt">' + b)
    sub('<p class="eyebrow">Your Raisey Scan</p>', '<p class="eyebrow">Votre Raisey Scan</p>')
    sub('Your results at a glance.', 'Vos résultats en un coup d’œil.')
    sub('A first read of your answers across six key dimensions.<span class="basis">Based on your answers · Not an audit of your digital presence</span>', 'Une première lecture de vos réponses sur six dimensions clés.<span class="basis">Basé sur vos réponses · Pas sur un audit de votre présence digitale</span>')
    sub('Understanding your results', 'Comprendre vos résultats')
    sub('Each dimension is read on three levels.', 'Chaque dimension se lit sur trois niveaux.')
    sub('Start the Raisey Scan <i class="ar"></i>', 'Lancer le Raisey Scan <i class="ar"></i>')
    sub('Free · Automated · Based on your answers · About 4 minutes', 'Gratuit · Automatisé · Basé sur vos réponses · Environ 4 minutes', 2)
    sub('The Raisey Scan needs JavaScript. You can request a first conversation in the last section below.',
        'Le Raisey Scan nécessite JavaScript. Vous pouvez demander un premier échange dans la dernière section, plus bas.')
    sub('</svg>Scan complete</p>', '</svg>Scan terminé</p>')
    sub('Where should we send your full Scan results?', 'Recevez votre Raisey Scan personnalisé.')
    sub('const SCAN_EMAIL_GATE = false;', 'const SCAN_EMAIL_GATE = true;')
    sub('Your full Raisey Scan results will be sent to this address. If you’d like to go further, the next step is a first conversation.',
        'Les résultats complets de votre Raisey Scan seront envoyés à cette adresse. Pour aller plus loin, l’étape suivante est un premier échange.')
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
    sub('<h3>Thank you. Your complete Scan results are on their way.</h3><p class="muted">They should reach you within a few minutes. Nothing yet? Check your spam folder.</p><p class="muted">The next step, if you wish, is a first conversation with Raisey Lab.</p><a class="tl" href="#contact" data-interest="first-conversation">Request a first conversation <i class="ar"></i></a>',
        '<h3>Merci. Les résultats complets de votre Scan arrivent.</h3><p class="muted">Comptez quelques minutes. Rien reçu ? Pensez à vérifier vos courriers indésirables.</p><p class="muted">L’étape suivante, si vous le souhaitez : un premier échange avec Raisey Lab.</p><a class="tl" href="#contact" data-interest="first-conversation">Demander un premier échange <i class="ar"></i></a>')

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

    # ---------- 03 approach ----------
    sub('<span class="t">Our approach</span>', '<span class="t">Notre approche</span>')
    sub('<span class="bl">Be found.</span> <span class="bl">Be trusted.</span> <span class="bl">Be chosen.</span>',
        '<span class="bl">Être trouvé.</span> <span class="bl">Inspirer confiance.</span> <span class="bl">Être choisi.</span>')
    sub('Built to help your practice rise.', 'Une présence plus forte pour un cabinet plus influent.')
    sub('<h3>Be found</h3><p>Raise your visibility across search, local and social, where patients are already looking.</p>',
        '<h3>Être trouvé</h3><p>Visible sur la recherche, en local et sur les réseaux — là où vos patients cherchent déjà.</p>')
    sub('<h3>Be trusted</h3><p>Let the authority you’ve earned be recognised at first glance.</p>',
        '<h3>Inspirer confiance</h3><p>Une présence digitale qui exprime, dès le premier regard, votre expertise et votre autorité.</p>')
    sub('<h3>Be chosen</h3><p>Strengthen trust at every step, and turn attention into consultations and long-term loyalty.</p>',
        '<h3>Être choisi</h3><p>Un parcours patient qui transforme l’hésitation en consultation, puis la consultation en fidélité.</p>')

    # ---------- 04 services (localized derivative of the locked English component) ----------
    sub('<p class="lab">Our expertise</p>', '<p class="lab">Notre expertise</p>')
    sub('<span class="l1">How we raise</span><span class="l2">your <em>presence.</em></span>', '<span class="l1">Comment nous bâtissons</span><span class="l2">votre <em>présence.</em></span>')
    sub('From visibility to patient experience, we connect the digital touchpoints that shape how your practice is found, perceived and chosen.',
        'De la visibilité à l’expérience patient, nous relions les points de contact digitaux qui décident de la façon dont votre cabinet est trouvé, perçu et choisi.')
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
    sub('Start my Raisey Scan <i class="ar"></i></a>\n    </div>\n  </div>\n</section>', 'Démarrer mon Raisey Scan <i class="ar"></i></a>\n    </div>\n  </div>\n</section>')

    # ---------- 05 studies ----------
    sub('<h2 id="work-h">Raisey Selected Studies</h2><span class="r">Independent strategic analyses</span>',
        '<h2 id="work-h">Études sélectionnées Raisey</h2><span class="r">Analyses stratégiques indépendantes</span>')
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
        sub('<h3>' + t_en + '</h3>', '<h3>' + t_fr + '</h3>')
        sub('aria-label="' + al_en + '"', 'aria-label="' + al_fr + '"')
        grp = lambda c: ''.join('<span class="st"><b>%s</b><i class="ar" aria-hidden="true"></i></span>' % x for x in c[:-1]) + '<b>%s</b>' % c[-1]
        old = grp(ch_en)
        new = grp(ch_fr)
        sub(old, new)
        sub('<p>' + p_en + '</p>', '<p>' + p_fr + '</p>')
    sub('aria-label="Raisey Selected Studies. Swipe, or use the arrow keys."', 'aria-label="Études sélectionnées Raisey. Faites défiler, ou utilisez les flèches du clavier."')
    sub('aria-label="Previous study"', 'aria-label="Étude précédente"')
    sub('aria-label="Next study"', 'aria-label="Étude suivante"')
    sub('</span> Senior dermatologist</p>', '</span> Dermatologue reconnu</p>')
    sub('</span> Boutique practice</p>', '</span> Cabinet confidentiel</p>')
    sub('</span> Nurse prescriber</p>', '</span> Infirmière en pratique avancée</p>')
    sub('</span> Niche specialist</p>', '</span> Spécialiste de niche</p>')
    sub('</span> Clinical point of view</p>', '</span> Vision clinique</p>')
    sub('</span> Hospital consultant</p>', '</span> Consultant hospitalier</p>')
    sub('Independent Studies are Raisey Lab’s own thinking: how a range of practitioner profiles could translate real expertise into greater visibility and authority. They are composite illustrations, not case studies of real clients or real individuals, and describe no actual person’s practice.',
        'Les Études indépendantes sont la réflexion propre de Raisey Lab : comment différents profils de praticiens pourraient transformer une expertise réelle en davantage de visibilité et d’autorité. Ce sont des illustrations composites — non des études de cas de clients ou de personnes réelles — et elles ne décrivent la pratique d’aucune personne existante.')

    # ---------- 06 founder ----------
    sub('<span class="t">Founder</span>', '<span class="t">Fondatrice</span>')
    sub('alt="Anissa Sabrina Briki, founder of Raisey Lab: close-up portrait on a cream background, captioned “Founder, Anissa” and “Strategy, growth, experience for aesthetic practices”"', 'alt="Anissa Sabrina Briki, fondatrice de Raisey Lab : portrait rapproché sur fond crème, avec les mentions « Founder, Anissa » et « Strategy, growth, experience for aesthetic practices »"')
    sub('Built from inside aesthetic medicine.', 'Née au cœur de la médecine esthétique.')
    sub('<p><span class="pq">“Exceptional medical expertise does not, on its own, create an exceptional digital presence.”</span></p>',
        '<p><span class="pq">« Une expertise médicale exceptionnelle ne crée pas, à elle seule, une présence digitale exceptionnelle. »</span></p>')
    sub('<p>Raisey Lab was born from this observation.</p>', '<p>C’est de ce constat qu’est née Raisey Lab.</p>')
    sub('<p>My experience at FILLMED Laboratories immersed me in the world of aesthetic medicine — working alongside practitioners, understanding the patient journey, and the challenges of growing a practice.</p><p>Before that, at Google and GroupM, I built my expertise in digital strategy and growth across beauty, luxury and international markets.</p><p>Raisey Lab was born at the intersection of these two worlds: an understanding of aesthetic medicine and expertise in digital growth.</p>\n        <p>Today, I work personally with every practice, with one ambition: to raise their visibility and authority to the level of their expertise.</p>',
        '<p>Mon expérience chez FILLMED Laboratories m’a plongée au cœur de la médecine esthétique — aux côtés des praticiens, au plus près des parcours patients et des enjeux de développement des cabinets.</p><p>Avant cela, chez Google et GroupM, j’ai construit mon expertise en stratégie et croissance digitale, entre beauté, luxe et marchés internationaux.</p><p>Raisey Lab est née à la rencontre de ces deux univers : la compréhension de la médecine esthétique et l’expertise du digital.</p>\n        <p>Aujourd’hui, j’accompagne chaque cabinet personnellement, avec une même ambition : élever sa visibilité et son autorité à la hauteur de son expertise.</p>')
    sub('<span class="muted">· Founder · Strategy &amp; Growth</span>', '<span class="muted">· Fondatrice · Stratégie &amp; Croissance</span>')
    sub('Talk to the founder <i class="ar"></i>', 'Échanger avec la fondatrice <i class="ar"></i>')
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
    sub('Raisey Lab is opening its first six partnerships. Each collaboration begins with a conversation to understand your practice, positioning and priorities — followed by a personalised Raisey Review to define what to raise, and in what order.',
        'Raisey Lab ouvre ses six premiers partenariats. Chaque collaboration commence par un échange pour comprendre votre pratique, votre positionnement et vos priorités — suivi d’un Raisey Review personnalisé pour définir ce qu’il faut élever, et dans quel ordre.')
    sub('<span class="m">Practices<br>only</span><span class="d">Founding<br>Partners</span>', '<span class="m">Six cabinets<br>seulement</span><span class="d">Partenaires<br>fondateurs</span>')
    sub('<b>01</b> — Know what to raise</span><h3>Your Raisey Review</h3><p>We look at what you’ve built, where it stands today, and what deserves to be raised next.</p>',
        '<b>01</b> — Partir de la bonne analyse</span><h3>Votre Raisey Review</h3><p>Après un premier échange, nous analysons l’état réel de votre présence digitale et définissons les écarts, les opportunités et les recommandations.</p>')
    sub('<b>02</b> — Built around your practice</span><h3>Founding Partner Conditions</h3><p>No predefined package. Your priorities, scope and strategy are shaped around what your practice actually needs, with preferred conditions reserved for our first six partners.</p>',
        '<b>02</b> — Sur mesure pour votre cabinet</span><h3>Conditions partenaire fondateur</h3><p>Pas d’offre toute faite. Vos priorités, votre périmètre et votre stratégie sont définis selon ce dont votre cabinet a réellement besoin, avec des conditions privilégiées réservées à nos six premiers partenaires.</p>')
    sub('<b>03</b> — Direct collaboration</span><h3>Work directly with the founder</h3><p>Strategy, creative direction and key decisions are handled directly with the founder of Raisey Lab — from the first conversation to implementation.</p>',
        '<b>03</b> — Un échange direct</span><h3>Travaillez directement avec la fondatrice</h3><p>Stratégie, direction créative et décisions clés se traitent directement avec la fondatrice de Raisey Lab — du premier échange jusqu’à la mise en œuvre.</p>')
    sub('<p class="lb">Founding partnership</p>', '<p class="lb">Partenariat fondateur</p>')
    sub('<span>Your expertise is already established.</span> <em>Now let’s raise it.</em>', '<span>Votre expertise est déjà établie.</span> <em>Construisons la présence qui lui ressemble.</em>')
    sub('Six founding partnerships across <span class="nb">Paris · London · Dubai.</span>', 'Six partenariats fondateurs entre <span class="nb">Paris · Londres · Dubaï.</span>')
    sub('Become a founding partner <i class="ar"></i>', 'Devenir partenaire fondateur <i class="ar"></i>')
    sub('<span>Raisey Scan</span><span>First conversation</span><span>Raisey Review</span><span>Transformation</span><span>Ongoing Growth</span>', '<span>Raisey Scan</span><span>Premier échange</span><span>Raisey Review</span><span>Transformation</span><span>Croissance continue</span>')

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
    sub('<a class="lg" href="privacy.html">Privacy Policy</a><a class="lg" href="privacy.html#legal-notice">Legal notice</a><span>Paris · London · Dubai · Expertise, elevated. © <span id="yr">2026</span> Raisey Lab. All rights reserved.</span>',
        '<a class="lg" href="confidentialite.html">Politique de confidentialité</a><a class="lg" href="confidentialite.html#mentions">Mentions légales</a><span>Paris · Londres · Dubaï · Un standard plus élevé de présence digitale. © <span id="yr">2026</span> Raisey Lab. Tous droits réservés.</span>')

    # ---------- JS copy ----------
    copy_fr = r'''const COPY = {
  form:{required:'Merci de renseigner ce champ.',email:'Merci de saisir une adresse e-mail valide.',send:'Votre demande n’a pas pu être envoyée. Merci de réessayer dans un instant.',sendScan:'Nous n’avons pas pu envoyer vos résultats. Merci de réessayer dans un instant.',sendScanEmail:'Nous n’avons pas pu envoyer vos résultats. Réessayez, ou écrivez à {email}.',orEmail:' Vous pouvez aussi écrire à {email}.',notConnected:'Ce formulaire n’est pas encore relié à une boîte mail : rien n’a été envoyé. (Définissez FORM_ENDPOINT avant la mise en ligne.)',sending:'Envoi…'},
  tiers:{established:{label:'Établi'},potential:{label:'Fort potentiel'},elevate:{label:'À renforcer'}},
  scan:{
    label:'Raisey Scan',
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
        html = html.replace('      </ul>\n      <a class="btn" href="#raisey-scan">', '      </ul>\n      ' + sw('m') + '\n      <a class="btn" href="#raisey-scan">', 1)
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
