#!/usr/bin/env bash
# Kontrola webu: uvodni stranky (en + cs), zasady (en + cs) a 404 - jazyk, hreflang, odkazy, kontakt, klicova fakta,
# jen povolene skripty (GTM + consent blok + /js/cookie-consent.js), og:*, favicony, robots/sitemap/.htaccess,
# existence obrazku, zadne dlouhe pomlcky.
GTM_ID=GTM-5BL8T5LD
cd "$(dirname "$0")" || exit 1
fail=0
bad() { echo "FAIL: $1"; fail=1; }
en=privacy/index.html; cs=cs/privacy/index.html
[ -f "$en" ] || bad "chybi $en"
[ -f "$cs" ] || bad "chybi $cs"
[ -f index.html ] || bad "chybi index.html"
need() { grep -q -i -- "$2" "$1" || bad "$1 neobsahuje: $2"; }
for f in "$en" "$cs"; do
  need "$f" "info@nice-one.cz"
  need "$f" "GPX"
  grep -q -E -- 'rel="stylesheet"' "$f" && bad "$f nacita externi styl"
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
[ "$(grep -c "<h2>" "$en")" = "$(grep -c "<h2>" "$cs")" ] || bad "nesedi pocet sekci h2"
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
# Uvodni stranky
home_en=index.html; home_cs=cs/index.html
[ -f "$home_cs" ] || bad "chybi $home_cs"
need "$home_en" '<html lang="en">'; need "$home_cs" '<html lang="cs">'
for f in "$home_en" "$home_cs"; do
  [ -f "$f" ] || continue
  need "$f" 'hreflang="en" href="https://saildays.app/"'
  need "$f" 'hreflang="cs" href="https://saildays.app/cs/"'
  need "$f" 'hreflang="x-default" href="https://saildays.app/"'
  need "$f" 'name="description"'
  need "$f" 'property="og:title"'
  need "$f" 'property="og:description"'
  need "$f" 'property="og:image" content="https://saildays.app/img/og.png"'
  need "$f" 'rel="icon"'
  need "$f" 'mailto:info@nice-one.cz'
  need "$f" 'Nice One s.r.o.'
  need "$f" 'Map data &copy; OpenStreetMap contributors, OpenMapTiles, OpenFreeMap, OpenSeaMap'
  grep -q -i -E -- 'rel="stylesheet"|@import' "$f" && bad "$f nacita externi styl"
  for i in $(grep -o -E '(src|href|content)="(https://saildays.app)?/?img/[^"]+"' "$f" | sed -E 's/^[a-z]+="(https:\/\/saildays.app)?\/?//; s/"$//' | sort -u); do
    [ -f "$i" ] || bad "$f odkazuje na chybejici $i"
  done
  grep -o '<img [^>]*>' "$f" | grep -v -E 'width="[0-9]+".*height="[0-9]+"' | grep -q . && bad "$f ma obrazek bez width/height"
done
need "$home_en" 'href="/privacy/"'; need "$home_en" 'href="/cs/"'; need "$home_en" "Coming soon on Google Play"
need "$home_cs" 'href="/cs/privacy/"'; need "$home_cs" 'href="/"'; need "$home_cs" "Brzy v Google Play"
[ "$(grep -c "<h2>" "$home_en")" = "$(grep -c "<h2>" "$home_cs")" ] || bad "uvodni stranky: nesedi pocet sekci h2"
[ "$(grep -c "<img " "$home_en")" = "$(grep -c "<img " "$home_cs")" ] || bad "uvodni stranky: nesedi pocet obrazku"
for f in img/*.webp; do
  [ -f "$f" ] || continue
  [ "$(wc -c < "$f")" -le 153600 ] || bad "$f je vetsi nez 150 kB"
done
# Soubory kolem webu
for f in 404.html .htaccess robots.txt sitemap.xml site.webmanifest favicon.ico favicon-32x32.png apple-touch-icon.png \
  img/icon-192.png img/icon-512.png js/cookie-consent.js; do
  [ -s "$f" ] || bad "chybi $f"
done
need .htaccess "ErrorDocument 404 /404.html"
need robots.txt "Sitemap: https://saildays.app/sitemap.xml"
for u in / /cs/ /privacy/ /cs/privacy/; do need sitemap.xml "<loc>https://saildays.app$u</loc>"; done
need sitemap.xml 'hreflang="cs"'
need 404.html 'href="/"'; need 404.html 'href="/cs/"'; need 404.html "noindex"
need js/cookie-consent.js "saildays_consent"; need js/cookie-consent.js "consent_granted"
# Mereni a skripty na vsech strankach vcetne 404
pages="$home_en $home_cs $en $cs 404.html"
for f in $pages; do
  [ -f "$f" ] || continue
  for p in 'property="og:title"' 'property="og:description"' 'property="og:image"' 'property="og:url"' 'property="og:locale"' \
    'property="og:type" content="website"' 'name="twitter:card" content="summary_large_image"'; do
    [ "$f" = 404.html ] || need "$f" "$p"
  done
  for p in 'href="/favicon.ico"' 'href="/apple-touch-icon.png"' 'href="/site.webmanifest"' \
    "gtm.js?id='+i+dl" "'dataLayer','$GTM_ID'" "ns.html?id=$GTM_ID" "gtag('consent', 'default'" "wait_for_update: 500" \
    'saildays_consent=' 'src="/js/cookie-consent.js'; do
    need "$f" "$p"
  done
  grep -o -E 'GTM-[A-Z0-9]+' "$f" | grep -v -x "$GTM_ID" | grep -q . && bad "$f obsahuje jine GTM ID nebo placeholder"
  # Povolene skripty: inline consent blok, inline GTM snippet, /js/cookie-consent.js. Jine src nebo URL ve skriptu = FAIL.
  python3 -I - "$f" <<'PY' || bad "$f obsahuje nepovoleny skript"
import re, sys
s = open(sys.argv[1], encoding="utf-8").read()
ok = True
for attrs, body in re.findall(r"<script([^>]*)>(.*?)</script>", s, re.S | re.I):
    src = re.search(r'src="([^"]+)"', attrs)
    if src:
        if not re.fullmatch(r"/js/cookie-consent\.js(\?v=\d+)?", src.group(1)) or body.strip():
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
# Zadne dlouhe pomlcky (em dash, en dash) ve strankach
for f in "$home_en" "$home_cs" "$en" "$cs" 404.html js/cookie-consent.js; do
  [ -f "$f" ] || continue
  grep -q -E -- $'\xe2\x80\x94|\xe2\x80\x93|&mdash;|&ndash;|&#821[12];' "$f" && bad "$f obsahuje dlouhou pomlcku"
done
[ $fail -eq 0 ] && echo "OK"
exit $fail
