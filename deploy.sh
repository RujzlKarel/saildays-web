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
for u in https://saildays.app/ https://saildays.app/privacy/ https://saildays.app/cs/privacy/; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "$u")
  echo "$u $code"; [ "$code" = 200 ] || exit 1
done
