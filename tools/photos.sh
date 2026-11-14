#!/usr/bin/env bash
# Fotky telefonu na lodi se skutecnym screenshotem aplikace -> img/photo-*.webp. Spustit znovu po kazde zmene
# screenshotu v Saildays/store/screenshots/<jazyk>/ (pak python3 tools/build.py, ./check.sh, ./deploy.sh).
#   tools/photos.sh            # EN + CS (DE/FR/ES ukazuji anglicke, SHOT_LANG v build.py)
#   tools/photos.sh cs         # jen jeden jazyk
# Zdrojove fotky s cernym displejem: media/photo/hero-3.png (ruka v kokpitu) a helm-2.png (drzak u kompasu),
# mimo git, kopie na Drivu Osobni/Jachting/Aplikace/web-media/photo/ (rclone copy --update gdrive:... media/).
# Orezy a kvalita jsou tady natvrdo, aby vysledek byl po novych screenshotech pixelove stejny (jen jine UI).
set -euo pipefail
cd "$(dirname "$0")/.."
PY=.venv/bin/python
SHOTS="${SAILDAYS_SHOTS:-$HOME/GitHub/Saildays/store/screenshots}"
[ -x "$PY" ] || { echo "chybi .venv: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"; exit 1; }
for f in media/photo/hero-3.png media/photo/helm-2.png; do
  [ -f "$f" ] || { echo "chybi $f (stahni z Drivu: rclone copy gdrive:Osobní/Jachting/Aplikace/web-media/photo/ media/photo/)"; exit 1; }
done
tmp=$(mktemp -d)
for l in ${1:-en cs}; do
  [ -f "$SHOTS/$l/01-log.png" ] || { echo "chybi $SHOTS/$l/01-log.png"; exit 1; }
  # hero: ruka s telefonem, orez 780x1170 (2:3), 780 px + 480 px pro mobil
  $PY tools/compose_phone.py media/photo/hero-3.png "$SHOTS/$l/01-log.png" "$tmp/hero-$l.png" \
    --crop 120,120,900,1290 --webp "img/photo-hero-$l" --widths 780,480 --quality 80
  # helm: telefon v drzaku u kompasu, cela fotka 3:2 pro desktop a vyrez kolem telefonu (896x1024) pro mobil
  $PY tools/compose_phone.py media/photo/helm-2.png "$SHOTS/$l/02-map.png" "$tmp/helm-$l.png" \
    --crop 0,0,1536,1024 --webp "img/photo-helm-$l" --widths 1400 --quality 76
  $PY tools/compose_phone.py media/photo/helm-2.png "$SHOTS/$l/02-map.png" "$tmp/helm-m-$l.png" \
    --crop 640,0,1536,1024 --webp "img/photo-helm-$l-m" --widths 640 --quality 78
done
rm -f "$tmp"/hero-en.png "$tmp"/hero-cs.png "$tmp"/helm-en.png "$tmp"/helm-cs.png "$tmp"/helm-m-en.png "$tmp"/helm-m-cs.png
rmdir "$tmp"
for f in img/photo-*.webp; do
  s=$(wc -c < "$f"); [ "$s" -le 153600 ] || { echo "FAIL: $f ma $s B (limit 150 kB, sniz --quality)"; exit 1; }
done
ls -la img/photo-*.webp
