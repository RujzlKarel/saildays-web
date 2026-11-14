#!/usr/bin/env bash
# Kontrola vygenerovaneho webu v dist/ (tools/build.py): uvodni stranky v 5 jazycich, zasady (en + cs) a 404.
# Jazyk, hreflang, odkazy, kontakt, klicova fakta zasad, jen povolene skripty (consent blok + GTM + /js/cookie-consent.js),
# jen lokalni styl, og:*, favicony, robots/sitemap/_headers/_redirects, existence obrazku, stejne sekce a obrazky
# ve vsech jazycich, zadne dlouhe pomlcky. Spousti se po `python3 tools/build.py`; deploy.sh ho vola sam.
GTM_ID=GTM-5BL8T5LD
LANGS="en cs de fr es"
cd "$(dirname "$0")" || exit 1
fail=0
bad() { echo "FAIL: $1"; fail=1; }
need() { grep -q -i -- "$2" "$1" || bad "$1 neobsahuje: $2"; }
D=dist
[ -d "$D" ] || { echo "FAIL: chybi $D (spust python3 tools/build.py)"; exit 1; }
home() { [ "$1" = en ] && echo "$D/index.html" || echo "$D/$1/index.html"; }
prefix() { [ "$1" = en ] && echo "/" || echo "/$1/"; }
# Zasady: obsah beze zmeny proti content/privacy/*.html (klicova fakta)
en=$D/privacy/index.html; cs=$D/cs/privacy/index.html
[ -f "$en" ] || bad "chybi $en"
[ -f "$cs" ] || bad "chybi $cs"
for f in "$en" "$cs"; do
  [ -f "$f" ] || continue
  need "$f" "info@nice-one.cz"
  need "$f" "GPX"
  need "$f" "Google Analytics"
  need "$f" "saildays_consent"
done
need "$en" '<html lang="en">'; need "$en" 'href="/cs/privacy/"'
need "$cs" '<html lang="cs">'; need "$cs" 'href="/privacy/"'
need "$en" "does not collect, store or share"
need "$en" "on your phone"
need "$en" "own Google account"
need "$en" "may not be end-to-end encrypted"
need "$en" "device transfer"
need "$en" "a ZIP file with your trip"
need "$en" "The developer of Saildays does not collect"
need "$cs" "přenos dat mezi zařízeními"
need "$cs" "soubor ZIP s plavbou"
[ "$(grep -c "<h2>" "$en")" = "$(grep -c "<h2>" "$cs")" ] || bad "zasady: nesedi pocet sekci h2"
need "$en" "Only when you tap"
need "$en" "no advertising, no analytics"
need "$en" "does not request background location"
need "$cs" "neshromažďuje, neukládá ani nesdílí"
need "$cs" "v telefonu"
need "$cs" "vlastního účtu Google"
need "$cs" "nemusí být zálohy šifrované"
need "$cs" "Pouze když klepnete"
need "$cs" "ani hlášení pádů"
need "$cs" "nežádá o přístup k poloze na pozadí"
need "$en" "OpenFreeMap"; need "$en" "OpenSeaMap"; need "$en" "Pictures/Saildays"; need "$en" "speech recognition"
need "$cs" "OpenFreeMap"; need "$cs" "OpenSeaMap"; need "$cs" "Pictures/Saildays"; need "$cs" "rozpoznávání řeči"
# Uvodni stranky ve vsech jazycich
ref_h2=""; ref_img=""
for l in $LANGS; do
  f=$(home "$l")
  [ -f "$f" ] || { bad "chybi $f"; continue; }
  need "$f" "<html lang=\"$l\">"
  need "$f" "rel=\"canonical\" href=\"https://saildays.app$(prefix "$l")\""
  for m in $LANGS; do need "$f" "hreflang=\"$m\" href=\"https://saildays.app$(prefix "$m")\""; done
  need "$f" 'hreflang="x-default" href="https://saildays.app/"'
  need "$f" 'name="description"'
  need "$f" 'rel="icon"'
  need "$f" 'mailto:info@nice-one.cz'
  need "$f" 'Nice One s.r.o.'
  need "$f" 'Map data &copy; OpenStreetMap contributors, OpenMapTiles, OpenFreeMap, OpenSeaMap'
  need "$f" 'href="#get"'; need "$f" 'id="get"'
  need "$f" 'class="lang-menu"'
  # odkaz na zasady: en a cs vlastni, ostatni anglicke s (EN)
  case "$l" in
    en) need "$f" 'href="/privacy/"'; grep -q 'href="/privacy/"[^>]*>[^<]*(EN)' "$f" && bad "$f ma u zasad (EN)";;
    cs) need "$f" 'href="/cs/privacy/"';;
    *) need "$f" 'href="/privacy/" hreflang="en"'; need "$f" '(EN)';;
  esac
  grep -o -E '(src|href|content)="(https://saildays.app)?/?img/[^"]+"' "$f" | sed -E 's/^[a-z]+="(https:\/\/saildays.app)?\///; s/"$//; s/\?v=[0-9a-f]+$//' | sort -u | while read -r i; do
    [ -f "$D/$i" ] || echo "FAIL: $f odkazuje na chybejici $i"
  done | grep . && fail=1
  grep -o '<img [^>]*>' "$f" | grep -v -E 'width="[0-9]+".*height="[0-9]+"' | grep -q . && bad "$f ma obrazek bez width/height"
  h2=$(grep -o "<h2" "$f" | wc -l | tr -d ' '); img=$(grep -o "<img " "$f" | wc -l | tr -d ' ')
  h3=$(grep -o "<h3" "$f" | wc -l | tr -d ' ')
  if [ -z "$ref_h2" ]; then ref_h2=$h2; ref_img=$img; ref_h3=$h3; else
    [ "$h2" = "$ref_h2" ] || bad "$f: jiny pocet sekci h2 ($h2) nez en ($ref_h2)"
    [ "$img" = "$ref_img" ] || bad "$f: jiny pocet obrazku ($img) nez en ($ref_img)"
    [ "$h3" = "$ref_h3" ] || bad "$f: jiny pocet nadpisu h3 ($h3) nez en ($ref_h3)"
  fi
done
need "$(home en)" "Coming soon on Google Play"
need "$(home cs)" "Brzy v Google Play"
for l in en cs; do [ -s "$D/img/shot-hero-$l.webp" ] || bad "chybi img/shot-hero-$l.webp"; done
[ -s "$D/img/og.png" ] || bad "chybi img/og.png"
for f in img/*.webp; do
  [ -f "$f" ] || continue
  [ "$(wc -c < "$f")" -le 153600 ] || bad "$f je vetsi nez 150 kB"
done
# Soubory kolem webu (Cloudflare Pages: _headers a _redirects misto .htaccess)
for f in 404.html robots.txt sitemap.xml _headers _redirects site.webmanifest favicon.ico favicon-32x32.png apple-touch-icon.png \
  img/icon-192.png img/icon-512.png img/icon.svg js/cookie-consent.js assets/site.css assets/fonts/archivo-latin.woff2 \
  assets/fonts/archivo-latin-ext.woff2; do
  [ -s "$D/$f" ] || bad "chybi $D/$f"
done
need "$D/robots.txt" "Sitemap: https://saildays.app/sitemap.xml"
for l in $LANGS; do need "$D/sitemap.xml" "<loc>https://saildays.app$(prefix "$l")</loc>"; done
for u in /privacy/ /cs/privacy/; do need "$D/sitemap.xml" "<loc>https://saildays.app$u</loc>"; done
[ "$(grep -c '<loc>' "$D/sitemap.xml")" = 7 ] || bad "sitemap nema 7 stranek"
need "$D/sitemap.xml" 'hreflang="cs"'; need "$D/sitemap.xml" 'hreflang="es"'
need "$D/_redirects" "https://www.saildays.app/\* https://saildays.app/:splat 301"
need "$D/_headers" "/img/\*"
need "$D/404.html" 'href="/"'; need "$D/404.html" 'href="/cs/"'; need "$D/404.html" "noindex"
for l in en cs de fr es; do need "$D/js/cookie-consent.js" "$l: {"; done
need "$D/js/cookie-consent.js" "saildays_consent"; need "$D/js/cookie-consent.js" "consent_granted"
# Staging nema byt noindex (nahledy pages.dev dostanou X-Robots-Tag od Cloudflare samy)
for l in $LANGS; do grep -q 'name="robots"' "$(home "$l")" && bad "$(home "$l") ma meta robots"; done
# Mereni a skripty na vsech strankach vcetne 404
pages="$(for l in $LANGS; do home "$l"; done) $en $cs $D/404.html"
for f in $pages; do
  [ -f "$f" ] || continue
  for p in 'property="og:title"' 'property="og:description"' 'property="og:image"' 'property="og:url"' 'property="og:locale"' \
    'property="og:type" content="website"' 'name="twitter:card" content="summary_large_image"'; do
    [ "$f" = "$D/404.html" ] || need "$f" "$p"
  done
  for p in 'href="/favicon.ico"' 'href="/apple-touch-icon.png"' 'href="/site.webmanifest"' \
    "gtm.js?id='+i+dl" "'dataLayer','$GTM_ID'" "ns.html?id=$GTM_ID" "gtag('consent', 'default'" "wait_for_update: 500" \
    'saildays_consent=' 'src="/js/cookie-consent.js'; do
    need "$f" "$p"
  done
  grep -o -E 'GTM-[A-Z0-9]+' "$f" | grep -v -x "$GTM_ID" | grep -q . && bad "$f obsahuje jine GTM ID nebo placeholder"
  # Styl jen lokalni (/assets/site.css), zadna cizi domena ani @import; pismo lokalni (zasady Google Fonts nezminuji)
  grep -o -E '<link[^>]*rel="stylesheet"[^>]*>' "$f" | grep -v -E 'href="/assets/site\.css(\?v=[0-9a-f]+)?"' | grep -q . && bad "$f nacita cizi styl"
  grep -q -i -E '@import|fonts\.googleapis|fonts\.gstatic' "$f" && bad "$f odkazuje na cizi pismo"
  # Povolene skripty: inline consent blok, inline GTM snippet, /js/cookie-consent.js. Jine src nebo URL ve skriptu = FAIL.
  python3 -I - "$f" <<'PY' || bad "$f obsahuje nepovoleny skript"
import re, sys
s = open(sys.argv[1], encoding="utf-8").read()
ok = True
for attrs, body in re.findall(r"<script([^>]*)>(.*?)</script>", s, re.S | re.I):
    src = re.search(r'src="([^"]+)"', attrs)
    if src:
        if not re.fullmatch(r"/js/cookie-consent\.js(\?v=[0-9a-f]+)?", src.group(1)) or body.strip():
            ok = False; print("  nepovoleny src:", src.group(1))
        continue
    urls = re.findall(r"https?://[^\x27\x22\s]+", body)
    if any(not u.startswith("https://www.googletagmanager.com/") for u in urls):
        ok = False; print("  nepovolena URL v inline skriptu:", urls)
    if "gtag('consent', 'default'" not in body and "googletagmanager.com/gtm.js" not in body:
        ok = False; print("  neznamy inline skript")
for src in re.findall(r'<iframe[^>]*src="([^"]+)"', s, re.I):
    if not src.startswith("https://www.googletagmanager.com/ns.html"):
        ok = False; print("  nepovoleny iframe:", src)
sys.exit(0 if ok else 1)
PY
done
grep -q -i -E 'fonts\.googleapis|@import|url\(https?:' "$D/assets/site.css" && bad "site.css nacita cizi zdroj"
# Zadne dlouhe pomlcky (em dash, en dash)
for f in $pages $D/js/cookie-consent.js $D/assets/site.css content/*.json content/privacy/*.html; do
  [ -f "$f" ] || continue
  grep -q -E -- $'\xe2\x80\x94|\xe2\x80\x93|&mdash;|&ndash;|&#821[12];' "$f" && bad "$f obsahuje dlouhou pomlcku"
done
[ $fail -eq 0 ] && echo "OK"
exit $fail
