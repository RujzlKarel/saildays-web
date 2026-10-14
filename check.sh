#!/usr/bin/env bash
# Kontrola webu: uvodni stranky (en + cs) a zasady (en + cs) - jazyk, hreflang, odkazy, kontakt, klicova fakta,
# zadne skripty ani externi styly, existence obrazku, zadne dlouhe pomlcky.
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
  grep -q -E -- "<script|rel=\"stylesheet\"" "$f" && bad "$f nacita externi zdroje"
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
  grep -q -i -- "<script" "$f" && bad "$f obsahuje <script"
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
# Zadne dlouhe pomlcky (em dash, en dash) ve strankach
for f in "$home_en" "$home_cs" "$en" "$cs"; do
  [ -f "$f" ] || continue
  grep -q -E -- $'\xe2\x80\x94|\xe2\x80\x93|&mdash;|&ndash;|&#821[12];' "$f" && bad "$f obsahuje dlouhou pomlcku"
done
[ $fail -eq 0 ] && echo "OK"
exit $fail
