# saildays-web

Statický web aplikace Saildays pro Android: úvodní stránka a zásady ochrany soukromí, obojí anglicky a česky. Žádný build, CSS inline (stejný blok v obou úvodních stránkách). Jediné skripty jsou měření (GTM s Consent Mode) a cookie lišta, viz Měření a cookies.

| URL | Soubor |
|---|---|
| https://saildays.app/ (en, x-default) | `index.html` |
| https://saildays.app/cs/ (cs) | `cs/index.html` |
| https://saildays.app/privacy/ (en) | `privacy/index.html` |
| https://saildays.app/cs/privacy/ (cs) | `cs/privacy/index.html` |

Další soubory v kořeni webu:

| Soubor | K čemu |
|---|---|
| `404.html` | vlastní stránka 404 (en nahoře, cs pod ní, odkazy na `/` a `/cs/`, `noindex`) |
| `.htaccess` | `ErrorDocument 404 /404.html`, zákaz `*.md`, `*.sh`, `*.py`, `*.example`, `*.log`, `.env*`, `.htaccess`, přesměrování http na https (Blueboard to sám nedělá), gzip, cache (obrázky 7 dní bez `immutable`, protože screenshoty se nahrazují pod stejným názvem; JS 1 h; HTML a XML bez cache). Bez přesměrování na www, doména běží bez www. |
| `robots.txt`, `sitemap.xml` | vše povoleno; sitemap se 4 stránkami a `xhtml:link hreflang` |
| `favicon.ico`, `favicon-32x32.png`, `apple-touch-icon.png`, `img/icon-192.png`, `img/icon-512.png`, `site.webmanifest` | ikony z `Saildays/branding/icon-512.png` (`sips`, `.ico` je obal s PNG uvnitř), manifest s barvou `#0b3a5c` |
| `js/cookie-consent.js` | cookie lišta |

Zdroj aplikace je v soukromém repu `RujzlKarel/Saildays`. Obsahuje jen web, nic z aplikace.

## Nasazení

Hosting Blueboard (server KRIOS), kořen webu `saildays_app/www/` na FTP. Nasazení: `./deploy.sh` - spustí `check.sh`, nahraje soubory přes FTP s TLS (`lftp mirror -R`, bez `.sh`, `.md`, `.git`) a ověří, že všechny čtyři URL vrací 200, neexistující stránka 404 s vlastní stránkou, `404.html`, `robots.txt`, `sitemap.xml`, manifest, ikony a `js/cookie-consent.js` 200, `.htaccess` a `README.md` se nevydávají (403) a `http://` přesměruje 301 na https. lftp `mirror` nahrává i tečkové soubory, `.htaccess` se tedy přenese (vylučuje se jen `.git*` a `.env*`).

Přístup v `~/.config/saildays/ftp.properties` (zdroj pravdy GCP Secret Manager, secret `saildays-ftp-properties`, stažení přes `secrets-pull.sh`):

```
SAILDAYS_FTP_HOST=krios.blueboard.cz
SAILDAYS_FTP_USER=...
SAILDAYS_FTP_PASSWORD=...
```

Hostitel je `krios.blueboard.cz`, ne `ftp.saildays.app`: certifikát FTP serveru platí jen pro něj. Doménu, DNS, mail a HTTPS certifikát spravuje Blueboard.

## Měření a cookies

ID nejsou tajná (jsou vidět v kódu stránky):

| Co | ID |
|---|---|
| GTM kontejner | `GTM-5BL8T5LD` (účet RUJZL.cz 106789, kontejner 267115838), publikovaná verze 3 „Saildays web - consent trigger“ |
| GA4 | `G-9MD50SXETV` (Google tag v GTM, spouštění Initialization - All Pages; tag má druhý trigger `CE - consent_granted`: první souhlasený `page_view` se tak odešle na téže stránce, protože po `consent update` se tag jen s All Pages znovu nespustí) |

Na všech stránkách (4 + `404.html`) je v `<head>` inline blok: `gtag('consent','default')` vše `denied` s `wait_for_update: 500`, hned za ním obnovení volby z cookie `saildays_consent` (vracející se návštěvník) a pak GTM snippet, za `<body>` jeho `<noscript>` iframe. Na konci `<body>` se načítá `/js/cookie-consent.js?v=1` (při změně skriptu zvýšit `v`).

Cookie lišta (`js/cookie-consent.js`, vzor `RujzlWeb/js/cookie-consent.js`): texty podle `<html lang>` (en / cs), odkaz na zásady stejného jazyka, tlačítka „Accept all“ / „Only necessary“ (cs „Přijmout vše“ / „Jen nezbytné“). Volba se ukládá na rok do cookie `saildays_consent` (`granted` / `denied`), posílá `consent update` a po přijetí `dataLayer.push({event: 'consent_granted'})`. Klik mimo kartu nebo Esc = jen nezbytné. Na stránce zásad se lišta ukáže jen jako karta dole, bez zatmavení, aby šly zásady číst.

Bez souhlasu odchází z GA4 jen anonymní ping bez cookies (`gcs=G100`), po souhlasu se ukládají `_ga`, `_ga_*`. Aplikace sama žádnou analytiku nemá; zásady to popisují v sekci Website / Web.

## Kontrola

`./check.sh` ověří úvodní stránky (`lang`, `hreflang` en / cs / x-default, `description`, `og:*`, favicon, přepínač jazyka, odkaz na zásady stejného jazyka, kontakt, Nice One s.r.o., atribuce map, jen povolené skripty (inline consent blok, GTM snippet z `googletagmanager.com`, `/js/cookie-consent.js`; jiný `src`, jiná URL ve skriptu nebo jiný iframe = FAIL), GTM `GTM-5BL8T5LD` na všech stránkách a žádné jiné GTM ID ani placeholder, `og:*` a `twitter:card` na všech 4 stránkách, odkazy na favicony a manifest, existenci `404.html`, `.htaccess`, `robots.txt`, `sitemap.xml`, `site.webmanifest`, ikon a cookie lišty, žádný externí styl, existence všech odkazovaných `img/` souborů, `width`/`height` u obrázků, WebP do 150 kB, stejný počet sekcí a obrázků v obou jazycích). U zásad ověří, že obě stránky existují, mají kontakt `info@nice-one.cz`, klíčová fakta (poloha jen v telefonu, záloha do vlastního účtu Google včetně možného nešifrování bez zámku obrazovky, export jen na pokyn, mapové servery OpenFreeMap a OpenSeaMap, fotky v `Pictures/Saildays`, rozpoznávání řeči v telefonu, žádné reklamy ani analytika, zmínka o Google Analytics a cookie `saildays_consent` na webu) a neobsahují dlouhé pomlčky.

Žádná stránka nesmí obsahovat dlouhou pomlčku (em dash, en dash), jen `-`.

## Obrázky

Ve složce `img/`:

| Soubor | Co to je |
|---|---|
| `icon.svg`, `logo.svg` | značka z `Saildays/branding/` (ikona slouží i jako favicon) |
| `og.png` | náhled pro sdílení (`og:image`), 1200×630 |
| `shot-<obrazovka>-<jazyk>.webp` | screenshoty `log`, `map`, `note`, `export` × `en`, `cs`; 540×1200, `shot-hero-<jazyk>.webp` (540×1080, z `07-log-dark.png`) je jen v hero |

## Screenshoty

Skutečné screenshoty z aplikace, zdroj `~/GitHub/Saildays/store/screenshots/`: `web/<jazyk>/shot-<name>-<jazyk>.webp` (už oříznuté, 540×1200) se kopírují do `img/` beze změny; hero vzniká z `<jazyk>/07-log-dark.png` (1080×2160):

```
cwebp -q 80 -resize 540 0 07-log-dark.png -o ~/GitHub/saildays-web/img/shot-hero-<jazyk>.webp
```

`og.png` (1200×630) je `Saildays/store/feature-graphic.png` na pozadí `#0b3a5c`, šířka 1100, render headless Chrome. Názvy souborů musí zůstat, stránky na ně odkazují. Každý WebP do 150 kB, pak `./check.sh` a `./deploy.sh`.
