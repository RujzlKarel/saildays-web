# saildays-web

Statický web aplikace Saildays pro Android: úvodní stránka a zásady ochrany soukromí, obojí anglicky a česky. Žádný build, CSS inline (stejný blok v obou úvodních stránkách), žádné skripty.

| URL | Soubor |
|---|---|
| https://saildays.app/ (en, x-default) | `index.html` |
| https://saildays.app/cs/ (cs) | `cs/index.html` |
| https://saildays.app/privacy/ (en) | `privacy/index.html` |
| https://saildays.app/cs/privacy/ (cs) | `cs/privacy/index.html` |

Zdroj aplikace je v soukromém repu `RujzlKarel/Saildays`. Obsahuje jen web, nic z aplikace.

## Nasazení

Hosting Blueboard (server KRIOS), kořen webu `saildays_app/www/` na FTP. Nasazení: `./deploy.sh` - spustí `check.sh`, nahraje soubory přes FTP s TLS (`lftp mirror -R`, bez `.sh`, `.md`, `.git`) a ověří, že všechny čtyři URL vrací 200.

Přístup v `~/.config/saildays/ftp.properties` (zdroj pravdy GCP Secret Manager, secret `saildays-ftp-properties`, stažení přes `secrets-pull.sh`):

```
SAILDAYS_FTP_HOST=krios.blueboard.cz
SAILDAYS_FTP_USER=...
SAILDAYS_FTP_PASSWORD=...
```

Hostitel je `krios.blueboard.cz`, ne `ftp.saildays.app`: certifikát FTP serveru platí jen pro něj. Doménu, DNS, mail a HTTPS certifikát spravuje Blueboard.

## Kontrola

`./check.sh` ověří úvodní stránky (`lang`, `hreflang` en / cs / x-default, `description`, `og:*`, favicon, přepínač jazyka, odkaz na zásady stejného jazyka, kontakt, Nice One s.r.o., atribuce map, žádný `<script` ani externí styl, existence všech odkazovaných `img/` souborů, `width`/`height` u obrázků, WebP do 150 kB, stejný počet sekcí a obrázků v obou jazycích). U zásad ověří, že obě stránky existují, mají kontakt `info@nice-one.cz`, klíčová fakta (poloha jen v telefonu, záloha do vlastního účtu Google včetně možného nešifrování bez zámku obrazovky, export jen na pokyn, žádné reklamy ani analytika) a neobsahují dlouhé pomlčky.

Žádná stránka nesmí obsahovat dlouhou pomlčku (em dash, en dash), jen `-`.

## Obrázky

Ve složce `img/`:

| Soubor | Co to je |
|---|---|
| `icon.svg`, `logo.svg` | značka z `Saildays/branding/` (ikona slouží i jako favicon) |
| `og.png` | náhled pro sdílení (`og:image`), 1200×630 |
| `shot-<obrazovka>-<jazyk>.webp` | screenshoty `log`, `map`, `note`, `export` × `en`, `cs`; 540×1200, hero používá `shot-log-*` |

## Screenshoty

Zatím jsou v `img/` náhradní screenshoty (tmavě modrá plocha s názvem obrazovky). Skutečné vzniknou z emulátoru do `~/GitHub/Saildays/store/screenshots/<jazyk>/` (1080×2400). Nahrazení, pro každou ze čtyř obrazovek a oba jazyky:

```
cd ~/GitHub/Saildays/store/screenshots/<jazyk> && cwebp -q 80 -resize 540 0 <png> -o ~/GitHub/saildays-web/img/shot-<name>-<jazyk>.webp
```

Názvy souborů musí zůstat stejné (`shot-log-en.webp` atd.), stránky na ně odkazují. Výsledek musí mít 540×1200 a do 150 kB, pak `./check.sh` a `./deploy.sh`.
