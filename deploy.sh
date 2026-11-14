#!/usr/bin/env bash
# Postavi web (tools/build.py), zkontroluje ho (check.sh) a nasadi dist/ na Cloudflare Pages, projekt `saildays`
# (ucet Nice One). Token: ~/.config/cloudflare/hosting-token.
#   ./deploy.sh            # produkce (branch main -> https://saildays.pages.dev, po prepnuti DNS https://saildays.app)
#   ./deploy.sh preview    # nahled (branch redesign -> https://redesign.saildays.pages.dev)
set -euo pipefail
cd "$(dirname "$0")"
ACCOUNT_ID=d8760638176f5e319063e9e5369dbfd8
PROJECT=saildays
TOKEN_FILE="$HOME/.config/cloudflare/hosting-token"
case "${1:-}" in
  "") BRANCH=main; BASE="https://$PROJECT.pages.dev";;
  preview) BRANCH=redesign; BASE="https://$BRANCH.$PROJECT.pages.dev";;
  *) echo "pouziti: ./deploy.sh [preview]"; exit 2;;
esac
[ -f "$TOKEN_FILE" ] || { echo "chybi $TOKEN_FILE"; exit 1; }
python3 tools/build.py
./check.sh
CLOUDFLARE_API_TOKEN=$(cat "$TOKEN_FILE") CLOUDFLARE_ACCOUNT_ID=$ACCOUNT_ID \
  npx -y wrangler@4 pages deploy dist --project-name="$PROJECT" --branch="$BRANCH" --commit-dirty=true
# Overeni: vsechny stranky 200, 404 vlastni stranka, soubory kolem webu, www presmerovani (jen na produkcni domene).
for u in / /cs/ /de/ /fr/ /es/ /privacy/ /cs/privacy/; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "$BASE$u")
  echo "$BASE$u $code"; [ "$code" = 200 ] || exit 1
done
expect() {
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "$2")
  echo "$2 $code (cekano $1)"; [[ "$code" =~ ^($1)$ ]] || exit 1
}
expect 404 "$BASE/neexistuje-xyz"
expect 200 "$BASE/robots.txt"
expect 200 "$BASE/sitemap.xml"
expect 200 "$BASE/site.webmanifest"
expect 200 "$BASE/favicon.ico"
expect 200 "$BASE/js/cookie-consent.js"
expect 200 "$BASE/assets/site.css"
expect 200 "$BASE/assets/fonts/archivo-latin.woff2"
expect '403|404' "$BASE/_headers"
curl -s --max-time 15 "$BASE/neexistuje-xyz" | grep -q "Page not found" || { echo "404 nevraci vlastni stranku"; exit 1; }
# www presmerovani se kontroluje az kdyz saildays.app obsluhuje Cloudflare (po prepnuti NS u registratora).
if [ "$BRANCH" = main ] && curl -sI --max-time 10 https://saildays.app/ | grep -qi "^server: cloudflare"; then
  expect 301 https://www.saildays.app/
  expect 200 https://saildays.app/
else
  [ "$BRANCH" = main ] && echo "saildays.app zatim neobsluhuje Cloudflare, kontrola www preskocena"
fi
echo "deploy OK: $BASE"
