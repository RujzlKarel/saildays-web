# saildays-web

Statický web aplikace Saildays pro Android (`https://saildays.app`): úvodní stránka v pěti jazycích (EN na `/`, CS `/cs/`, DE `/de/`, FR `/fr/`, ES `/es/`) a zásady ochrany soukromí anglicky a česky. Web generuje jeden Python skript ze standardní knihovny (`tools/build.py`) z textů v `content/`, výstup `dist/` se nasazuje na Cloudflare Pages. Zdroj aplikace je v soukromém repu `RujzlKarel/Saildays`; sem nepatří nic z něj.

| URL | Zdroj |
|---|---|
| `/` (en, x-default), `/cs/`, `/de/`, `/fr/`, `/es/` | `content/<jazyk>.json` + šablona v `tools/build.py` |
| `/privacy/` (en), `/cs/privacy/` (cs) | `content/privacy/en.html`, `content/privacy/cs.html` (jen `<main>`, hlavičku a patičku přidá build) |
| `/404.html` | build (věta ve všech 5 jazycích, `noindex`) |
| `/robots.txt`, `/sitemap.xml`, `/_headers`, `/_worker.js`, ikony, `site.webmanifest` | build (sitemap 5 úvodních + 2 zásady s `hreflang`; `_headers` cache pro `/img/*`, `/assets/*` 7 dní a `/js/*` 1 h, HTML bez cache; `_worker.js` je malý Pages Worker jen na přesměrování www → bez www 301, protože `_redirects` v Pages neumí přesměrování podle hostu a pravidla zóny by chtěla další oprávnění tokenu; ostatní požadavky předává statickým souborům) |
| `/img/*`, `/js/cookie-consent.js` | kopie z `img/` a `js/` (fotky `img/photo-*.webp` vyrábí `tools/photos.sh`, viz Fotky) |
| `/assets/site.css`, `/assets/fonts/*.woff2` | `assets/` (písmo viz níž) |

## Jak generovat a prohlédnout

    python3 tools/build.py            # výstup do dist/ (dist/ je v .gitignore)
    ./check.sh                        # kontrola dist/
    cd dist && python3 -m http.server 8766

Pak `http://localhost:8766/` (cesty jsou od kořene, proto server spouštět v `dist/`). Pro screenshoty a lokální prohlížení stavět s `SAILDAYS_ANALYTICS= python3 tools/build.py`, jinak stránka načte GTM a po odsouhlasení cookie lišty posílá hity do GA4. Stavba potřebuje jen Python 3.8+; při prvním běhu stáhne písmo (viz Písmo).

Starý ručně psaný web z hostingu Blueboard (do 14. 11. 2026) je smazaný; od té doby existuje jen `tools/build.py` + `content/` a hosting Cloudflare Pages. Ikony, `robots.txt` a `site.webmanifest` v kořeni jsou zdroje, které build kopíruje do `dist/`.

## Jazyky a texty

- Texty webu jsou v `content/<jazyk>.json`. Všech pět souborů musí mít stejné klíče a stejné délky polí, u funkcí stejné `id` a `visual`; `tools/build.py` to kontroluje a jinak spadne. Krátké HTML (`<b>`, `<a>`) je v textech dovolené, `{email}` a `{privacy}` jsou zástupné značky.
- **DE, FR a ES jsou strojový překlad (Claude, 14. 11. 2026) bez rodilého korektora.** Oslovení podle textů aplikace: EN you, CS vy, DE du, FR vous, ES tú. Francouzština má před `: ; ? !` nezlomitelnou mezeru (U+00A0), build to hlídá. Terminologie aplikace (Logbuch / journal de bord / cuaderno de bitácora, Skipper / skipper / patrón) je z `Saildays/app/src/main/res/values-*/strings.xml`.
- Zásady ochrany soukromí jsou jen anglicky a česky; DE/FR/ES odkazují na anglické s „(EN)" (hlavička, patička, sekce soukromí, cookie lišta). Při změně zásad upravit `content/privacy/en.html` i `cs.html` a datum účinnosti.
- Ukázkové údaje v typografických objektech (list PDF deníku, motohodiny, časová osa) odpovídají ukázkové plavbě Kornati 2026 ze screenshotů aplikace.
- Žádná dlouhá pomlčka (em dash, en dash), jen `-`; build i `check.sh` to kontrolují.

## Vzhled

Směr A2 „editorial katalog" jako `navyfaces.com` (rozhodnutí majitele 14. 11. 2026: „udělat stejně jako web ciferníků"), v paletě Saildays: porcelán `#f2f5f8` a navy `#0b3a5c` z ikony, akcentová modrá `#1971c2` jen na hlavní tlačítko, signální oranžová `#ff6a13` ze značky jen jako slunce v horizontu nad nadpisy a v patičce. Úvod a pás ve funkcích jsou fotografie telefonu na plachetnici se skutečným snímkem aplikace (viz Fotky), ostatní funkce telefon se snímkem v CSS rámečku, funkce bez snímku (PDF deník, motohodiny, pauza) jako typografické objekty, žádné karty ani mřížky, tmavý režim podle systému. Tokeny a pravidla v `DESIGN.md`, produktový kontext v `PRODUCT.md`. Report z redesignu a screenshoty: `~/Downloads/webdesigner/saildays-2026-11-14/` na miniai.

## Písmo

Archivo (proměnné, OFL) jako na navyfaces.com, ale **lokálně** z `/assets/fonts/archivo-latin.woff2` a `archivo-latin-ext.woff2` - zásady ochrany soukromí Google Fonts nezmiňují, takže z cizí domény se nic nenačítá (`check.sh` hlídá). Soubory jsou v `.gitignore`; `tools/build.py` je při prvním běhu stáhne z Google Fonts (URL podmnožin v `FONT_URLS`, verze v25). Ručně:

    curl -sfL -o assets/fonts/archivo-latin.woff2 https://fonts.gstatic.com/s/archivo/v25/k3kQo8UDI-1M0wlSfdnoLmvDIaI.woff2
    curl -sfL -o assets/fonts/archivo-latin-ext.woff2 https://fonts.gstatic.com/s/archivo/v25/k3kQo8UDI-1M0wlSfdfoLmvDIaK18A.woff2

Stránky s češtinou předloadují i `latin-ext` (`LATIN_EXT_LANGS`).

## Nasazení (Cloudflare Pages)

Projekt `saildays` v účtu Nice One (account `d8760638176f5e319063e9e5369dbfd8`), token `~/.config/cloudflare/hosting-token`. Redesign je v produkci (branch `main`) od 14. 11. 2026. DNS zóna `saildays.app` je na Cloudflare (CNAME na `saildays.pages.dev`, mail se nepoužívá: bez MX, SPF `v=spf1 -all`, DMARC reject); změna nameserverů u registrátora (Blueboard, Administrace → Moje domény → saildays.app → DNS servery) zažádána 14. 11. 2026, registrace domény se převádí ke Cloudflare od 11. 12. 2026 (ICANN 60 dní). Postup v `~/GitHub/Saildays/docs/vydani.md`.

    ./deploy.sh preview   # náhled: branch redesign -> https://redesign.saildays.pages.dev
    ./deploy.sh           # produkce: branch main -> https://saildays.pages.dev = https://saildays.app

`deploy.sh` postaví web, spustí `check.sh`, nahraje `dist/` přes `npx wrangler@4 pages deploy` a ověří, že všech 7 stránek vrací 200, neexistující stránka 404 s vlastní stránkou, `robots.txt`, `sitemap.xml`, manifest, ikony, `js/cookie-consent.js`, styl a písmo 200, `_headers` se nevydává a (jen na produkční doméně, až poběží) `www` přesměruje 301. Náhledy na `*.pages.dev` dostávají od Cloudflare `X-Robots-Tag: noindex` samy, stránky proto žádné `noindex` nemají a canonical míří rovnou na `https://saildays.app/…`.

## Měření a cookies

ID nejsou tajná (jsou vidět v kódu stránky):

| Co | ID |
|---|---|
| GTM kontejner | `GTM-5BL8T5LD` (účet RUJZL.cz 106789, kontejner 267115838), publikovaná verze 3 „Saildays web - consent trigger" |
| GA4 | `G-9MD50SXETV` (Google tag v GTM, spouštění Initialization - All Pages; tag má druhý trigger `CE - consent_granted`: první souhlasený `page_view` se tak odešle na téže stránce, protože po `consent update` se tag jen s All Pages znovu nespustí) |

Na všech stránkách (7 + `404.html`) je v `<head>` inline blok: `gtag('consent','default')` vše `denied` s `wait_for_update: 500`, hned za ním obnovení volby z cookie `saildays_consent` (vracející se návštěvník) a pak GTM snippet, za `<body>` jeho `<noscript>` iframe. Na konci `<body>` se načítá `/js/cookie-consent.js?v=<otisk>` (build doplní otisk obsahu). Jiné skripty `check.sh` odmítne.

Cookie lišta (`js/cookie-consent.js`, vzor `RujzlWeb/js/cookie-consent.js`): texty podle `<html lang>` (en, cs, de, fr, es; de/fr/es strojový překlad), odkaz na zásady stejného jazyka (de/fr/es na anglické s „(EN)"), tlačítka „Accept all" / „Only necessary". Volba se ukládá na rok do cookie `saildays_consent` (`granted` / `denied`), posílá `consent update` a po přijetí `dataLayer.push({event: 'consent_granted'})`. Klik mimo kartu nebo Esc = jen nezbytné. Na stránce zásad se lišta ukáže jen jako karta dole, bez zatmavení.

Bez souhlasu odchází z GA4 jen anonymní ping bez cookies (`gcs=G100`), po souhlasu se ukládají `_ga`, `_ga_*`. Aplikace sama žádnou analytiku nemá; zásady to popisují v sekci Website / Web.

## Kontrola

`./check.sh` ověří v `dist/`: úvodní stránky všech 5 jazyků (`lang`, canonical, `hreflang` mezi všemi pěti + `x-default`, `description`, `og:*`, `twitter:card`, favicony, přepínač jazyků, odkaz na zásady správného jazyka a „(EN)" u DE/FR/ES, Nice One s.r.o. a **žádný e-mail ani `mailto:`** (rozhodnutí 14. 11. 2026, spam; v zásadách je adresa zapsaná slovně), atribuce map, odkaz do Google Play a sekce `#get`, žádný `meta robots`, existence odkazovaných obrázků včetně všech variant v `srcset`, `width`/`height` u obrázků, `fetchpriority="high"` a preload fotky úvodu, existence `img/photo-*.webp`, stejný počet `h2`, `h3` a obrázků ve všech jazycích), jen povolené skripty (inline consent blok, GTM snippet z `googletagmanager.com`, `/js/cookie-consent.js`; jiný `src`, jiná URL nebo iframe = FAIL), jen lokální styl a písmo (žádné `fonts.googleapis`, `@import`, `url(https:`), GTM `GTM-5BL8T5LD` všude a žádné jiné GTM ID, WebP do 150 kB, soubory kolem webu (`404.html`, `robots.txt`, `sitemap.xml` se 7 stránkami, `_headers`, `_worker.js`, manifest, ikony, písmo), cookie lištu s texty všech 5 jazyků, klíčová fakta zásad (poloha jen v telefonu, záloha do vlastního účtu Google, export jen na pokyn, OpenFreeMap a OpenSeaMap, `Pictures/Saildays`, rozpoznávání řeči, žádné reklamy ani analytika, Google Analytics a `saildays_consent` na webu) a žádné dlouhé pomlčky (i v `content/`).

## Obrázky

Ve složce `img/`:

| Soubor | Co to je |
|---|---|
| `icon.svg` | značka „slunce za plachtou", bitová kopie `Saildays/branding/icon.svg` (favicon SVG, ikona v hlavičce) |
| `icon-512.png` | bitová kopie `Saildays/branding/icon-512.png` (manifest, `purpose: any maskable`; prvky značky leží v bezpečné zóně) |
| `icon-192.png`, `/apple-touch-icon.png` (180), `/favicon-32x32.png`, `/favicon.ico` (16 + 32) | zmenšeniny `icon-512.png` (Pillow LANCZOS) |
| `logo.svg` | značka + wordmark „Saildays" v Archivo 800 / šířka 118 převedený na křivky (fontTools nad `assets/fonts/archivo-latin.woff2`); kopie v `Saildays/branding/logo.svg` |
| `og.png` | náhled pro sdílení (`og:image`), 1200×630, pro všechny jazyky; render `tools/og.html` headless Chromem (příkaz v hlavičce souboru) |
| `photo-hero-<jazyk>.webp`, `photo-hero-<jazyk>-480.webp` | fotka úvodu: ruka s telefonem v kokpitu, pohled od zádi k přídi, v displeji skutečný `01-log.png`; 780×1170 a 480×720 (`srcset`) |
| `photo-helm-<jazyk>.webp`, `photo-helm-<jazyk>-m.webp` | pás ve funkcích: telefon v držáku na sloupku kompasu od kormidla, v displeji `02-map.png`; 1400×933 a mobilní výřez 640×731 |
| `shot-<obrazovka>-<jazyk>.webp` | screenshoty `log`, `map`, `note`, `export` × `en`, `cs`; 540×1200 v CSS rámečku telefonu |

DE, FR a ES zatím ukazují anglické screenshoty i fotky (`SHOT_LANG` v `build.py`); až budou snímky v těch jazycích, stačí je přidat jako `shot-<obrazovka>-<jazyk>.webp`, pustit `tools/photos.sh <jazyk>` a rozšířit `SHOT_LANG`. Build přidává k obrázkům i faviconám otisk obsahu (`?v=`), takže se cache (7 dní na `/img/*`) po výměně snímku nebo značky obnoví sama; holé `/img/icon.svg` bez `?v=` může Cloudflare vracet staré až týden.

## Screenshoty

Skutečné screenshoty z aplikace, zdroj `~/GitHub/Saildays/store/screenshots/`: `web/<jazyk>/shot-<name>-<jazyk>.webp` (už oříznuté, 540×1200) se kopírují do `img/` beze změny. Názvy souborů musí zůstat, build na ně odkazuje. Každý WebP do 150 kB, pak `python3 tools/build.py`, `./check.sh` a `./deploy.sh`.

## Fotky (telefon na lodi se skutečným snímkem)

Fotky úvodu a pásu jsou vygenerované (OpenAI přes `impeccable generate-image`, 14. 11. 2026) **s úplně černým vypnutým displejem**; snímek aplikace do nich vkládá program, nikdy generátor. Zdrojové PNG s prompty (`<soubor>.png.json`) jsou v `media/photo/` **mimo git**, kopie na Drivu `Nice One s.r.o./Saildays/web-media/photo/` (`rclone copy --update media/ "gdrive:Nice One s.r.o./Saildays/web-media/"`). Použité: `hero-fwd-2.png` (ruka s telefonem v kokpitu, za ní loď dopředu k přídi, 1024×1536) a `helm-fwd-2.png` (telefon v držáku na sloupku kompasu, displej dozadu ke kormidelníkovi, ruka na kole, 1536×1024). **Obě z pohledu kormidelníka od zádi k přídi** - majitel 14. 11. 2026 odmítl první verzi `helm-2.png` (telefon natočený od přídě k zádi) jako nerealistickou. Ostatní kandidáti (`hero-1..3`, `hero-fwd-1`, `helm-1`, `helm-2`, `helm-fwd-1`, `helm-fwd-3`, `chart-1`) leží vedle; prompty v `prompt-*.txt` a `<soubor>.png.json`.

Nástroje potřebují Pillow a numpy (na miniai není numpy v systémovém Pythonu), proto venv v repu (`.venv/` v `.gitignore`):

    python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

**Po každé změně screenshotů aplikace** (`Saildays/scripts/screenshots.sh`) stačí jeden příkaz, pak build, check a deploy:

    tools/photos.sh            # EN + CS -> img/photo-hero-*.webp, img/photo-helm-*.webp (ořezy a kvalita natvrdo ve skriptu)
    tools/photos.sh cs         # jen jeden jazyk

`tools/compose_phone.py <foto.png> <snímek.png> <výstup.png> [--crop …] [--webp img/jméno --widths 780,480] [--debug kontrola.png] [--corners x,y,…]` najde ve fotce největší souvislou černou plochu (displej), z jejího obrysu čtyři rohy (extrémy úhlopříček, hrany zpřesněné proložením přímek, rohy = průsečíky), snímek promítne homografií, zaoblení rohů odhadne z rozdílu zaobleného a ostrého rohu, poměr stran displeje (~1:2.2) srovná doplněním krajních řádků snímku (ne roztažením) a navrch vrátí odlesky skla z fotky (screen). `--debug` vykreslí nalezený obrys, při selhání detekce jdou rohy zadat ručně `--corners` (TL, TR, BR, BL). Zdroj inspirace `Garmin/navy-web/tools/compose_watch.py`.

Kontrola po změně vzhledu: nadpis a tlačítko úvodu nesmí překrývat fotku a stránka nesmí mít vodorovný scroll na 360-1920 px ve všech jazycích: `node tools/overlap.mjs http://127.0.0.1:8765` nad lokálním serverem v `dist/` (Playwright z `~/.claude/skills/webdesigner/scripts/node_modules`).
