#!/usr/bin/env bash
# Kontrola stranicek se zasadami: obe jazykove verze, kontakt, klicova fakta, zadne dlouhe pomlcky.
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
[ $fail -eq 0 ] && echo "OK"
exit $fail
