#!/usr/bin/env python3
"""Generátor webu saildays.app do dist/ (Cloudflare Pages).

Texty bere z content/<jazyk>.json (EN, CS, DE, FR, ES; stejné klíče a délky polí všude, jinak stavba spadne),
zásady z content/privacy/<jazyk>.html (jen EN a CS), styl z assets/site.css, písmo Archivo z assets/fonts/
(woff2 z Google Fonts, OFL; mimo git, při prvním běhu se stáhne), obrázky z img/, cookie lištu z js/.
Výstup: dist/index.html, dist/<jazyk>/index.html, dist/privacy/, dist/cs/privacy/, 404.html, robots.txt,
sitemap.xml, _headers, _worker.js (www -> bez www), ikony, manifest.

Jen standardní knihovna Pythonu.

    python3 tools/build.py            # výstup do dist/
    SAILDAYS_ANALYTICS= python3 tools/build.py   # bez GTM (lokální náhledy a screenshoty)
"""
import hashlib
import html
import json
import os
import re
import shutil
import sys
import urllib.request
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CONTENT = os.path.join(ROOT, "content")
ASSETS = os.path.join(ROOT, "assets")
FONTS = os.path.join(ASSETS, "fonts")
PLAY_URL = "https://play.google.com/store/apps/details?id=app.saildays"
DIST = os.path.join(ROOT, "dist")

CONFIG = {
    "site_url": os.environ.get("SAILDAYS_SITE_URL", "https://saildays.app"),
    # GTM s Consent Mode v2 (README, sekce Měření a cookies). Prázdné SAILDAYS_ANALYTICS= měření vypne.
    "analytics": os.environ.get("SAILDAYS_ANALYTICS", "GTM-5BL8T5LD") or None,
    "og_image": "/img/og.png",
    "theme_color": "#0b3a5c",
}

WORKER_JS = """export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.hostname === "www.saildays.app") {
      url.hostname = "saildays.app";
      return Response.redirect(url.toString(), 301);
    }
    return env.ASSETS.fetch(request);
  },
};
"""

LANGS = ["en", "cs", "de", "fr", "es"]
# Stránky, které nejsou ve všech jazycích; z ostatních jazyků vede odkaz na anglickou verzi s „(EN)"
TEXT_LANGS = {"privacy": ["en", "cs"]}
OG_LOCALE = {"en": "en_US", "cs": "cs_CZ", "de": "de_DE", "fr": "fr_FR", "es": "es_ES"}
# Jazyky, jejichž písmena nejsou v podmnožině latin (preload latin-ext navíc)
LATIN_EXT_LANGS = {"cs"}
# 21 jazyků aplikace (Saildays/README.md), vlastními názvy, stejné ve všech verzích webu
APP_LANGUAGES = ["English", "Čeština", "Deutsch", "Français", "Español", "Italiano", "Nederlands", "Polski",
                 "Português", "Dansk", "Svenska", "Norsk", "Suomi", "Slovenčina", "Hrvatski", "Slovenščina",
                 "Ελληνικά", "Türkçe", "Magyar", "日本語", "한국어"]
MAP_ATTR = "Map data &copy; OpenStreetMap contributors, OpenMapTiles, OpenFreeMap, OpenSeaMap"
# Archivo (proměnné písmo, OFL) z Google Fonts, podmnožiny latin a latin-ext; verze v25 (14. 11. 2026)
FONT_URLS = {
    "archivo-latin.woff2": "https://fonts.gstatic.com/s/archivo/v25/k3kQo8UDI-1M0wlSfdnoLmvDIaI.woff2",
    "archivo-latin-ext.woff2": "https://fonts.gstatic.com/s/archivo/v25/k3kQo8UDI-1M0wlSfdfoLmvDIaK18A.woff2",
}
# Snímky aplikace: pro DE/FR/ES zatím anglické (screenshoty v těch jazycích ještě nejsou); platí i pro fotky photo-*
SHOT_LANG = {"en": "en", "cs": "cs", "de": "en", "fr": "en", "es": "en"}
# Za kterou funkcí (index v content features) je pás s fotkou telefonu u kormidla (mapa)
BAND_AFTER = 2
DASHES = re.compile("[–—]|&mdash;|&ndash;|&#821[12];")

GLOBE_SVG = ('<svg class="globe" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" focusable="false" fill="none" '
             'stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="9.2"/><path d="M2.8 12h18.4M12 2.8c2.6 2.6 '
             '3.9 5.6 3.9 9.2s-1.3 6.6-3.9 9.2M12 2.8C9.4 5.4 8.1 8.4 8.1 12s1.3 6.6 3.9 9.2"/></svg>')

# Motiv lodě: plachta se sluncem a horizontem ze značky (jen patička), jinak jen „horizont" nad nadpisy sekcí (CSS .horizon)
SAIL_SVG = ('<svg class="footer-sail" viewBox="0 0 56 44" width="56" height="44" aria-hidden="true" focusable="false">'
            '<circle cx="17" cy="19" r="8" fill="var(--signal)"/>'
            '<path d="M22 4v28h22C44 20 36 10 22 4z" fill="currentColor"/>'
            '<path d="M8 40h40" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"/></svg>')
HORIZON = '<span class="horizon" aria-hidden="true"></span>'

CONSENT_HEAD = """<!-- Consent Mode v2: default denied, volba z cookie saildays_consent se obnovuje pred nactenim GTM -->
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('consent', 'default', {
  analytics_storage: 'denied',
  ad_storage: 'denied',
  ad_user_data: 'denied',
  ad_personalization: 'denied',
  wait_for_update: 500
});
(function () {
  var m = document.cookie.match(/(?:^|; )saildays_consent=([^;]*)/);
  if (!m) return;
  var g = m[1] === 'granted' ? 'granted' : 'denied';
  gtag('consent', 'update', {
    analytics_storage: g,
    ad_storage: g,
    ad_user_data: g,
    ad_personalization: g
  });
})();
</script>
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','%s');</script>
<!-- End Google Tag Manager -->"""


class BuildError(Exception):
    pass


def esc(s):
    return html.escape(str(s), quote=True)


def path_for(lang, slug=""):
    p = "/" if lang == "en" else "/%s/" % lang
    return p + (slug + "/" if slug else "")


def abs_url(path):
    return CONFIG["site_url"] + path


def page_langs(slug):
    return TEXT_LANGS.get(slug, LANGS)


def link_lang(lang, slug):
    return lang if lang in page_langs(slug) else "en"


def file_hash(path):
    with open(path, "rb") as fh:
        return hashlib.sha1(fh.read()).hexdigest()[:8]


# ---------------------------------------------------------------- obsah

def shape(v):
    """Tvar hodnoty: klíče slovníků a délky polí, bez textů (kontrola shody jazyků)."""
    if isinstance(v, dict):
        return {k: shape(x) for k, x in v.items() if k != "_comment"}
    if isinstance(v, list):
        return [shape(x) for x in v]
    if isinstance(v, bool):
        return v
    return "s"


def load_content():
    ui = {}
    for lang in LANGS:
        path = os.path.join(CONTENT, lang + ".json")
        if not os.path.exists(path):
            raise BuildError("chybí %s" % path)
        with open(path, encoding="utf-8") as fh:
            ui[lang] = json.load(fh)
        if DASHES.search(json.dumps(ui[lang], ensure_ascii=False)):
            raise BuildError("%s obsahuje dlouhou pomlčku" % path)
    ref = shape(ui["en"])
    for lang in LANGS[1:]:
        if shape(ui[lang]) != ref:
            raise BuildError("content/%s.json nemá stejnou strukturu (klíče, délky polí) jako en.json" % lang)
    for lang in LANGS:
        for i, f in enumerate(ui[lang]["features"]):
            if f["id"] != ui["en"]["features"][i]["id"] or f["visual"] != ui["en"]["features"][i]["visual"]:
                raise BuildError("content/%s.json: funkce %d nemá stejné id a visual jako en.json" % (lang, i + 1))
    # Francouzština: před : ; ? ! musí být nezlomitelná mezera (U+00A0 nebo U+202F), ne obyčejná a ne žádná
    fr = json.dumps({k: v for k, v in ui["fr"].items() if k != "_comment"}, ensure_ascii=False)
    for m in re.finditer(r"(?<=[\w)»' ])([;?!:])(?=[\s\",.<)]|$)", fr):
        if fr[m.start() - 1] not in "\u00a0\u202f":
            raise BuildError("content/fr.json: před znakem %s chybí nezlomitelná mezera: ...%s" % (
                m.group(1), fr[max(0, m.start() - 30):m.end()]))
    return ui


def t(ui, lang, key, **kw):
    s = ui[lang][key]
    for k, v in kw.items():
        s = s.replace("{%s}" % k, str(v))
    return s


# ---------------------------------------------------------------- kostra stránky

def head_block(ctx, lang, slug, title, description, here, langs, preload=None):
    head = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % esc(title),
        '<meta name="description" content="%s">' % esc(description),
    ]
    if slug == "404":
        head.append('<meta name="robots" content="noindex">')
    else:
        head.append('<link rel="canonical" href="%s">' % esc(abs_url(here)))
    if langs:
        head += ['<link rel="alternate" hreflang="%s" href="%s">' % (l, esc(abs_url(path_for(l, slug)))) for l in langs]
        head.append('<link rel="alternate" hreflang="x-default" href="%s">' % esc(abs_url(path_for("en", slug))))
    og = abs_url("%s?v=%s" % (CONFIG["og_image"], ctx["v"]["og"]))
    head += [
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="Saildays">',
        '<meta property="og:url" content="%s">' % esc(abs_url(here)),
        '<meta property="og:locale" content="%s">' % OG_LOCALE[lang],
    ]
    head += ['<meta property="og:locale:alternate" content="%s">' % OG_LOCALE[l] for l in (langs or []) if l != lang]
    head += [
        '<meta property="og:title" content="%s">' % esc(title),
        '<meta property="og:description" content="%s">' % esc(description),
        '<meta property="og:image" content="%s">' % esc(og),
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta name="theme-color" content="%s">' % CONFIG["theme_color"],
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:title" content="%s">' % esc(title),
        '<meta name="twitter:description" content="%s">' % esc(description),
        '<meta name="twitter:image" content="%s">' % esc(og),
        # otisk i u ikon: /img/* a kořenové soubory drží cache 7 dní, bez ?v= by po výměně značky zůstala stará favicona
        '<link rel="icon" href="/favicon.ico?v=%s" sizes="32x32">' % ctx["v"]["ico"],
        '<link rel="icon" type="image/svg+xml" href="/img/icon.svg?v=%s">' % ctx["v"]["icon"],
        '<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png?v=%s">' % ctx["v"]["ico"],
        '<link rel="apple-touch-icon" href="/apple-touch-icon.png?v=%s">' % ctx["v"]["ico"],
        '<link rel="manifest" href="/site.webmanifest">',
        '<link rel="preload" as="font" type="font/woff2" crossorigin href="/assets/fonts/archivo-latin.woff2">',
    ]
    if lang in LATIN_EXT_LANGS:
        head.append('<link rel="preload" as="font" type="font/woff2" crossorigin href="/assets/fonts/archivo-latin-ext.woff2">')
    head.append('<link rel="stylesheet" href="/assets/site.css?v=%s">' % ctx["v"]["css"])
    if preload:
        # LCP fotka úvodu: preload se stejným srcset/sizes jako <img>, jinak prohlížeč stáhne jinou variantu
        head.append('<link rel="preload" as="image" href="%s" imagesrcset="%s" imagesizes="%s" fetchpriority="high">' % preload)
    if CONFIG["analytics"]:
        head.append(CONSENT_HEAD % CONFIG["analytics"])
    else:
        head.append("<!-- měření vypnuté (SAILDAYS_ANALYTICS=) -->")
    return "\n".join(head)


def gtm_noscript():
    if not CONFIG["analytics"]:
        return ""
    return ('<!-- Google Tag Manager (noscript) -->\n<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=%s" '
            'height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>\n'
            "<!-- End Google Tag Manager (noscript) -->\n") % CONFIG["analytics"]


def layout(ctx, lang, slug, title, description, main, body_class="", langs=None, preload=None):
    """Kostra stránky. `langs` = jazyky, ve kterých stránka existuje (hreflang, přepínač jen mezi nimi),
    None = podle page_langs(slug), False = bez jazykových verzí (404). `preload` = (href, imagesrcset, imagesizes)
    LCP obrázku (jen úvod)."""
    ui = ctx["ui"]
    if langs is None:
        langs = page_langs(slug)
    here = path_for(lang, slug) if slug != "404" else "/404.html"

    def page_link(target, label, cls=""):
        """Odkaz na stránku; když v jazyce stránky není (zásady v DE/FR/ES), vede na anglickou s „(EN)"."""
        l = link_lang(lang, target)
        if l != lang:
            label += " (EN)"
        return '<a%s href="%s"%s%s>%s</a>' % (
            ' class="%s"' % cls if cls else "", esc(path_for(l, target)),
            ' hreflang="en"' if l != lang else "", ' aria-current="page"' if target == slug else "", esc(label))

    switch_items, footer_langs = [], []
    if langs is not False:
        for l in LANGS:
            target = path_for(l, slug) if l in langs else path_for(l)
            cur = ' aria-current="true"' if l == lang else ""
            switch_items.append('<li><a href="%s" hreflang="%s" lang="%s"%s>%s</a></li>' % (
                esc(target), l, l, cur, esc(t(ui, l, "lang_name"))))
            footer_langs.append('<a href="%s" hreflang="%s" lang="%s"%s>%s</a>' % (
                esc(target), l, l, cur, esc(t(ui, l, "lang_name"))))
    lang_switch = ""
    if switch_items:
        lang_switch = ('<details class="lang-menu"><summary aria-label="%s: %s">%s<span aria-hidden="true">%s</span></summary>'
                       '<ul>%s</ul></details>') % (esc(t(ui, lang, "lang_label")), esc(t(ui, lang, "lang_name")),
                                                   GLOBE_SVG, lang.upper(), "".join(switch_items))
    nav = ('<a class="nav-features" href="%s">%s</a>%s%s' % (
        esc(path_for(lang) + "#features"), esc(t(ui, lang, "nav_features")),
        page_link("privacy", t(ui, lang, "nav_privacy"), "nav-privacy"), lang_switch))
    brand = ('<a class="brand" href="%s"><img src="/img/icon.svg?v=%s" alt="" width="32" height="32">'
             '<span>Saildays</span></a>') % (esc(path_for(lang)), ctx["v"]["icon"])
    footer = (
        '<footer class="site-footer"><div class="wrap footer-grid">'
        '<div>' + SAIL_SVG + '<p class="footer-brand">Saildays</p><p class="footer-note">%s</p>'
        '<p class="footer-tm">&copy; 2026 Nice One s.r.o., Brno</p>'
        '<p class="footer-tm">%s</p></div>'
        '<div class="footer-nav"><nav aria-label="Footer">%s%s</nav>%s</div>'
        "</div></footer>"
    ) % (esc(t(ui, lang, "footer_disclaimer")), MAP_ATTR,
         '<a href="%s">%s</a>' % (esc(path_for(lang) + "#features"), esc(t(ui, lang, "nav_features"))),
         page_link("privacy", t(ui, lang, "footer_privacy")),
         ('<nav class="footer-langs" aria-label="%s">%s</nav>' % (esc(t(ui, lang, "lang_label")), "".join(footer_langs)))
         if footer_langs else "")
    cookie = '<script src="/js/cookie-consent.js?v=%s"></script>' % ctx["v"]["cookie"]
    return (
        '<!doctype html>\n<html lang="%s">\n<head>\n%s\n</head>\n<body%s>\n%s'
        '<a class="skip" href="#main">%s</a>\n'
        '<header class="site-header"><div class="wrap header-row">%s'
        '<nav class="nav" aria-label="Main">%s</nav></div></header>\n'
        '<main id="main">\n%s\n</main>\n%s\n%s\n</body>\n</html>\n'
    ) % (lang, head_block(ctx, lang, slug, title, description, here, langs if langs else None, preload),
         ' class="%s"' % body_class if body_class else "", gtm_noscript(), esc(t(ui, lang, "skip")),
         brand, nav, main, footer, cookie)


# ---------------------------------------------------------------- stavební kameny úvodu

def phone(ctx, lang, name, alt):
    """Telefon se skutečným snímkem aplikace (img/shot-<name>-<jazyk>.webp, 540x1200) v CSS rámečku (listy funkcí)."""
    return '<div class="phone"><img src="%s" width="540" height="1200" alt="%s" loading="lazy" decoding="async"></div>' % (
        img_path("shot-%s-%s.webp" % (name, SHOT_LANG[lang])), esc(alt))


def img_path(fname):
    path = os.path.join(ROOT, "img", fname)
    if not os.path.exists(path):
        raise BuildError("chybí img/%s (tools/photos.sh)" % fname)
    return "/img/%s?v=%s" % (fname, file_hash(path))


def photo_hero(ctx, lang, alt):
    """Fotka úvodu: telefon v ruce v kokpitu se skutečným snímkem deníku (tools/photos.sh -> img/photo-hero-<jazyk>.webp).
    Vrací (html, preload) - preload má stejný srcset a sizes, ať prohlížeč stáhne tutéž variantu."""
    l = SHOT_LANG[lang]
    big, small = img_path("photo-hero-%s.webp" % l), img_path("photo-hero-%s-480.webp" % l)
    srcset = "%s 780w, %s 480w" % (big, small)
    sizes = "(max-width: 820px) 100vw, 46vw"
    html_ = ('<div class="hero-photo"><img src="%s" srcset="%s" sizes="%s" width="780" height="1170" alt="%s" '
             'loading="eager" fetchpriority="high" decoding="async"></div>') % (big, srcset, sizes, esc(alt))
    return html_, (big, srcset, sizes)


def photo_band(ctx, lang, alt):
    """Pás přes celou šířku: telefon v držáku u kompasu s mapou dne; na mobilu užší výřez kolem telefonu."""
    l = SHOT_LANG[lang]
    wide, narrow = img_path("photo-helm-%s.webp" % l), img_path("photo-helm-%s-m.webp" % l)
    return ('<figure class="band"><picture><source media="(max-width: 820px)" srcset="%s" width="640" height="731">'
            '<img src="%s" width="1400" height="933" alt="%s" loading="lazy" decoding="async"></picture></figure>') % (
        narrow, wide, esc(alt))


def paper(ui, lang):
    P = ui[lang]["paper"]
    rows = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % esc(c) for c in r) for r in P["rows"])
    return (
        '<div class="paper" role="img" aria-label="%s"><div class="paper-head"><span class="paper-title">%s</span>'
        '<span>%s</span><span>%s</span></div>'
        '<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>'
        '<div class="paper-sign"><span>%s</span><span>%s</span></div><div class="paper-foot">%s</div></div>'
    ) % (esc(t(ui, lang, "features")[3]["title"]), esc(P["title"]), esc(P["trip"]), esc(P["day"]),
         "".join("<th>%s</th>" % esc(c) for c in P["cols"]), rows, esc(P["sig_skipper"]), esc(P["sig_date"]), esc(P["page"]))


def ledger(ui, lang):
    rows = "".join('<div class="ledger-row"><dt>%s</dt><dd>%s</dd></div>' % (esc(k), esc(v)) for k, v in ui[lang]["ledger"]["rows"])
    return '<dl class="ledger">%s</dl>' % rows


def timeline(ui, lang):
    rows = "".join('<li%s><span class="tl-when">%s</span><span class="tl-text">%s</span></li>' % (
        ' class="tl-removed"' if r["removed"] else "", esc(r["when"]), esc(r["text"])) for r in ui[lang]["timeline"]["rows"])
    return '<ol class="timeline">%s</ol>' % rows


def feature_spread(ctx, lang, f, i):
    ui = ctx["ui"]
    v = f["visual"]
    if v.startswith("shot-"):
        visual = phone(ctx, lang, v[5:], f["alt"])
        kind = "phone"
    elif v == "paper":
        visual, kind = paper(ui, lang), "paper"
    elif v == "ledger":
        visual, kind = ledger(ui, lang), "ledger"
    elif v == "timeline":
        visual, kind = timeline(ui, lang), "timeline"
    else:
        raise BuildError("neznámý visual %s" % v)
    sub = '<p class="sub">%s</p>' % esc(f["sub"]) if f["sub"] else ""
    # střídání porcelán / navy podle pořadí funkce (ne nth-child: seznam je kvůli pásu s fotkou rozdělený na dva <ol>)
    return (
        '<li class="spread spread-%s%s" id="%s"><div class="wrap spread-grid">'
        '<div class="spread-visual">%s</div>'
        '<div class="spread-text"><h3>%s</h3>%s<p>%s</p></div>'
        "</div></li>"
    ) % (kind, " spread-deep" if i % 2 else "", esc(f["id"]), visual, esc(f["title"]), sub, f["text"])


def page_home(ctx, lang):
    ui = ctx["ui"]
    L = ui[lang]
    spreads = [feature_spread(ctx, lang, f, i) for i, f in enumerate(L["features"])]
    # pás s fotkou (telefon u kormidla s mapou) za listem mapy; druhý <ol> pokračuje v číslování
    cut = BAND_AFTER + 1
    spreads_html = ('<ol class="spreads">%s</ol>\n%s\n<ol class="spreads" start="%d">%s</ol>' % (
        "".join(spreads[:cut]), photo_band(ctx, lang, L["photo_helm_alt"]), cut + 1, "".join(spreads[cut:])))
    hero_photo, preload = photo_hero(ctx, lang, L["photo_hero_alt"])
    steps ="".join('<li><h3>%s</h3><p>%s</p></li>' % (esc(s["title"]), s["text"]) for s in L["steps"])
    priv = "".join('<li><strong>%s</strong> %s</li>' % (esc(p["strong"]), p["text"]) for p in L["privacy_items"])
    priv_l = link_lang(lang, "privacy")
    priv_link = '<a href="%s"%s>%s%s</a>' % (esc(path_for(priv_l, "privacy")), ' hreflang="en"' if priv_l != lang else "",
                                             esc(L["privacy_link"]), " (EN)" if priv_l != lang else "")
    langs_list = " &middot; ".join('<span lang="%s">%s</span>' % (c, esc(n)) if c else esc(n) for n, c in
                                   zip(APP_LANGUAGES, ["en", "cs", "de", "fr", "es", "it", "nl", "pl", "pt", "da", "sv",
                                                       "nb", "fi", "sk", "hr", "sl", "el", "tr", "hu", "ja", "ko"]))
    main = (
        '<section class="hero"><div class="wrap hero-grid">'
        '<div class="hero-text"><h1>%(h1)s</h1>'
        '<div class="hero-copy"><p>%(lead)s</p>'
        '<p class="act"><a class="btn btn-primary" href="%(play)s">%(cta)s</a><a class="more" href="#features">%(more)s</a></p>'
        '<p class="note">%(note)s</p></div></div>'
        '%(photo)s'
        "</div></section>\n"
        '<section class="line-head" id="features"><div class="wrap">%(hz)s<h2>%(f_h2)s</h2><p>%(f_lead)s</p></div></section>\n'
        '%(spreads)s\n'
        '<section class="how" id="how"><div class="wrap">%(hz)s<h2>%(how_h2)s</h2><ol class="steps">%(steps)s</ol></div></section>\n'
        '<section class="private" id="privacy"><div class="wrap">%(hz)s<h2>%(p_h2)s</h2><ul class="claims">%(priv)s</ul>'
        '<p class="note">%(p_note)s</p></div></section>\n'
        '<section class="langs" id="languages"><div class="wrap">%(hz)s<h2>%(l_h2)s</h2><p>%(l_text)s</p>'
        '<p class="lang-list">%(l_list)s</p></div></section>\n'
        '<section class="get" id="get"><div class="wrap get-grid"><div>%(hz)s<h2>%(g_h2)s</h2></div><div><p>%(g_text)s</p>'
        '<p class="act"><a class="btn btn-primary" href="%(play)s">%(cta)s</a></p></div></div></section>'
    ) % {
        "play": PLAY_URL, "h1": esc(L["hero_h1"]), "lead": L["hero_lead"], "cta": esc(L["hero_cta"]), "more": esc(L["hero_more"]),
        "note": esc(L["hero_note"]), "photo": hero_photo, "hz": HORIZON,
        "f_h2": esc(L["features_h2"]), "f_lead": L["features_lead"], "spreads": spreads_html,
        "how_h2": esc(L["how_h2"]), "steps": steps, "p_h2": esc(L["privacy_h2"]), "priv": priv,
        "p_note": t(ui, lang, "privacy_note", privacy=priv_link), "l_h2": esc(L["langs_h2"]), "l_text": L["langs_text"],
        "l_list": langs_list, "g_h2": esc(L["get_h2"]), "g_text": L["get_text"],
    }
    return layout(ctx, lang, "", L["title"], L["description"], main, body_class="page-home", preload=preload)


def page_privacy(ctx, lang):
    path = os.path.join(CONTENT, "privacy", lang + ".html")
    with open(path, encoding="utf-8") as fh:
        body = fh.read()
    if DASHES.search(body):
        raise BuildError("%s obsahuje dlouhou pomlčku" % path)
    L = ctx["ui"][lang]
    main = '<div class="wrap prose-wrap"><article class="prose">%s</article></div>' % body
    return layout(ctx, lang, "privacy", L["privacy_title"], L["privacy_description"], main, body_class="page-text")


def page_404(ctx):
    ui = ctx["ui"]
    lines = "".join('<p%s>%s <a href="%s">%s</a></p>' % ("" if l == "en" else ' lang="%s"' % l,
                                                          esc(t(ui, l, "notfound_text")), path_for(l), esc(t(ui, l, "home")))
                    for l in LANGS)
    main = ('<div class="wrap prose-wrap"><article class="prose"><h1>%s</h1>%s</article></div>') % (
        esc(t(ui, "en", "notfound_title")), lines)
    return layout(ctx, "en", "404", t(ui, "en", "notfound_title") + " - Saildays", t(ui, "en", "notfound_text"), main,
                  body_class="page-text", langs=False)


# ---------------------------------------------------------------- soubory kolem webu

def sitemap(pages):
    today = date.today().isoformat()
    by_slug = {}
    for lang, slug in pages:
        by_slug.setdefault(slug, []).append(lang)
    urls = []
    for slug, langs in by_slug.items():
        alts = "".join('\n    <xhtml:link rel="alternate" hreflang="%s" href="%s"/>' % (l, esc(abs_url(path_for(l, slug))))
                       for l in langs)
        alts += '\n    <xhtml:link rel="alternate" hreflang="x-default" href="%s"/>' % esc(abs_url(path_for("en", slug)))
        for l in langs:
            urls.append("  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>%s\n  </url>" % (
                esc(abs_url(path_for(l, slug))), today, alts))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "\n".join(urls) + "\n</urlset>\n")


def headers_file(html_paths):
    out = ["/*", "  X-Content-Type-Options: nosniff", "  Referrer-Policy: strict-origin-when-cross-origin", ""]
    for p in ("/img/*", "/assets/*"):
        out += [p, "  Cache-Control: public, max-age=604800", ""]
    out += ["/js/*", "  Cache-Control: public, max-age=3600, must-revalidate", ""]
    for p in html_paths:  # HTML bez cache, ať se změna textu projeví hned
        out += [p, "  Cache-Control: no-cache", ""]
    return "\n".join(out)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def ensure_fonts():
    os.makedirs(FONTS, exist_ok=True)
    for name, url in FONT_URLS.items():
        dst = os.path.join(FONTS, name)
        if os.path.exists(dst) and os.path.getsize(dst) > 1000:
            continue
        print("stahuji písmo", name)
        with urllib.request.urlopen(url, timeout=30) as r, open(dst, "wb") as fh:
            fh.write(r.read())


def build():
    ui = load_content()
    ensure_fonts()
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)
    # statické soubory: img/, js/, ikony, manifest, assets/ (styl + písma)
    shutil.copytree(os.path.join(ROOT, "img"), os.path.join(DIST, "img"))
    shutil.copytree(os.path.join(ROOT, "js"), os.path.join(DIST, "js"))
    os.makedirs(os.path.join(DIST, "assets", "fonts"))
    shutil.copy2(os.path.join(ASSETS, "site.css"), os.path.join(DIST, "assets", "site.css"))
    for name in FONT_URLS:
        shutil.copy2(os.path.join(FONTS, name), os.path.join(DIST, "assets", "fonts", name))
    for f in ("favicon.ico", "favicon-32x32.png", "apple-touch-icon.png", "site.webmanifest", "robots.txt"):
        shutil.copy2(os.path.join(ROOT, f), os.path.join(DIST, f))
    ctx = {"ui": ui, "v": {
        "css": file_hash(os.path.join(ASSETS, "site.css")),
        "cookie": file_hash(os.path.join(ROOT, "js", "cookie-consent.js")),
        "icon": file_hash(os.path.join(ROOT, "img", "icon.svg")),
        "ico": file_hash(os.path.join(ROOT, "img", "icon-512.png")),  # všechny PNG/ICO favicony jsou z téhož zdroje
        "og": file_hash(os.path.join(ROOT, "img", "og.png")),
    }}
    pages = []
    for lang in LANGS:
        write(os.path.join(DIST, path_for(lang).strip("/"), "index.html"), page_home(ctx, lang))
        pages.append((lang, ""))
    for lang in TEXT_LANGS["privacy"]:
        write(os.path.join(DIST, path_for(lang, "privacy").strip("/"), "index.html"), page_privacy(ctx, lang))
        pages.append((lang, "privacy"))
    write(os.path.join(DIST, "404.html"), page_404(ctx))
    write(os.path.join(DIST, "sitemap.xml"), sitemap(pages))
    write(os.path.join(DIST, "_headers"), headers_file([path_for(l, s) for l, s in pages] + ["/404.html"]))
    # www -> bez www: _redirects v Pages neumi presmerovani podle hostu a pravidla zony by chtela dalsi opravneni tokenu,
    # proto maly Pages Worker (advanced mode); vse ostatni obslouzi staticke soubory vcetne _headers a 404.html.
    write(os.path.join(DIST, "_worker.js"), WORKER_JS)
    # kontrola pomlček ve výstupu
    for dp, _, files in os.walk(DIST):
        for f in files:
            if f.endswith((".html", ".xml", ".css", ".js", ".txt")):
                with open(os.path.join(dp, f), encoding="utf-8") as fh:
                    if DASHES.search(fh.read()):
                        raise BuildError("%s obsahuje dlouhou pomlčku" % os.path.join(dp, f))
    print("hotovo: %d stránek v %s" % (len(pages) + 1, os.path.relpath(DIST, ROOT)))


if __name__ == "__main__":
    try:
        build()
    except BuildError as e:
        print("CHYBA:", e, file=sys.stderr)
        sys.exit(1)
