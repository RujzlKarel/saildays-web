#!/usr/bin/env bash
# Nahraje web na hosting Blueboard (FTP, koren webu saildays_app/www/).
# Pristup: ~/.config/saildays/ftp.properties (SAILDAYS_FTP_HOST/_USER/_PASSWORD), v GCP Secret Manageru jako saildays-ftp-properties.
set -euo pipefail
cd "$(dirname "$0")"
./check.sh
conf="$HOME/.config/saildays/ftp.properties"
[ -f "$conf" ] || { echo "chybi $conf (secrets-pull.sh)"; exit 1; }
set -a; . "$conf"; set +a
lftp -u "$SAILDAYS_FTP_USER","$SAILDAYS_FTP_PASSWORD" -e "set ftp:ssl-force yes; set net:max-retries 3; set net:timeout 20; mirror -R --no-perms --verbose=1 --exclude-glob .git/ --exclude-glob .git* --exclude-glob *.sh --exclude-glob *.md --exclude-glob .env* ./ saildays_app/www/; bye" "$SAILDAYS_FTP_HOST"
for u in https://saildays.app/ https://saildays.app/cs/ https://saildays.app/privacy/ https://saildays.app/cs/privacy/; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "$u")
  echo "$u $code"; [ "$code" = 200 ] || exit 1
done
# Ocekavane kody: 404 stranka, robots, sitemap, ikony, cookie lista; .htaccess a interni soubory se nevydavaji;
# http presmeruje na https.
expect() {
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "$2")
  echo "$2 $code (cekano $1)"; [[ "$code" =~ ^($1)$ ]] || exit 1
}
expect 404 https://saildays.app/neexistuje-xyz
expect 200 https://saildays.app/404.html
expect 200 https://saildays.app/robots.txt
expect 200 https://saildays.app/sitemap.xml
expect 200 https://saildays.app/site.webmanifest
expect 200 https://saildays.app/favicon.ico
expect 200 https://saildays.app/apple-touch-icon.png
expect 200 https://saildays.app/js/cookie-consent.js
expect '403|404' https://saildays.app/.htaccess
expect '403|404' https://saildays.app/README.md
expect 301 http://saildays.app/
curl -s --max-time 15 https://saildays.app/neexistuje-xyz | grep -q "Page not found" || { echo "404 nevraci vlastni stranku"; exit 1; }
echo "deploy OK"
