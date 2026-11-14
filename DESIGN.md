---
name: Saildays
description: Web lodního deníku Saildays, směr A2 „editorial katalog" převzatý z navyfaces.com v paletě Saildays
colors:
  porcelain: "#f2f5f8"
  porcelain-2: "#e6edf3"
  rule: "#d0dbe5"
  ink: "#0b3a5c"
  ink-2: "#4a6378"
  deep: "#0b3a5c"
  deep-2: "#0e4670"
  on-deep: "#eaf2f8"
  steel: "#a9c8de"
  steel-2: "#7fa6c2"
  sky: "#8fc8f0"
  accent: "#1971c2"
  accent-hover: "#1864ab"
  on-accent: "#ffffff"
  paper: "#fffdf6"
  paper-ink: "#1b2430"
  paper-muted: "#5a6270"
  paper-rule: "#c9c3b4"
  dark-bg: "#0b1620"
  dark-bg-2: "#0f1d2a"
  dark-rule: "#213447"
  dark-ink: "#e6eef5"
  dark-ink-2: "#9fb6c8"
  image-outline: "rgba(0, 0, 0, .1)"
  image-outline-on-deep: "rgba(255, 255, 255, .1)"
typography:
  display:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(2.8rem, 5.4vw, 5.8rem)"
    fontWeight: 850
    lineHeight: 0.92
    letterSpacing: "-0.035em"
    fontVariation: "'wdth' 112"
  headline:
    fontFamily: "Archivo, sans-serif"
    fontSize: "clamp(2rem, 4vw, 3.4rem)"
    fontWeight: 800
    lineHeight: 0.95
    fontVariation: "'wdth' 112"
  feature-name:
    fontFamily: "Archivo, sans-serif"
    fontSize: "clamp(2.2rem, 4.6vw, 4.2rem)"
    fontWeight: 800
    fontVariation: "'wdth' 112"
  body:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.6
  lead:
    fontFamily: "Archivo, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 400
  wordmark:
    fontFamily: "Archivo, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 800
    letterSpacing: "0.01em"
    fontVariation: "'wdth' 118"
  figure:
    fontFamily: "Archivo, sans-serif"
    fontSize: "clamp(1.8rem, 3vw, 2.8rem)"
    fontWeight: 800
  title:
    fontFamily: "Archivo, sans-serif"
    fontSize: "clamp(1.5rem, 2.4vw, 2rem)"
    fontWeight: 800
  step-title:
    fontFamily: "Archivo, sans-serif"
    fontSize: "clamp(1.35rem, 2vw, 1.7rem)"
    fontWeight: 800
  prose-display:
    fontFamily: "Archivo, sans-serif"
    fontSize: "clamp(2.4rem, 5vw, 4.4rem)"
    fontWeight: 800
  prose-headline:
    fontFamily: "Archivo, sans-serif"
    fontSize: "clamp(1.6rem, 2.6vw, 2.1rem)"
    fontWeight: 800
  nav:
    fontFamily: "Archivo, sans-serif"
    fontSize: "0.97rem"
  small:
    fontFamily: "Archivo, sans-serif"
    fontSize: "0.92rem"
  paper:
    fontFamily: "ui-monospace, SF Mono, Menlo, Consolas, monospace"
    fontSize: "clamp(0.7rem, 1.9vw, 0.88rem)"
  timeline:
    fontFamily: "ui-monospace, SF Mono, Menlo, Consolas, monospace"
    fontSize: "clamp(0.82rem, 1.8vw, 0.95rem)"
rounded:
  none: "0"
  icon: "8px"
  phone: "44px"
  screen: "32px"
spacing:
  gutter: "clamp(16px, 4vw, 56px)"
  section: "clamp(64px, 9vw, 128px)"
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.on-accent}"
    rounded: "{rounded.none}"
    padding: "14px 28px"
  button-primary-hover:
    backgroundColor: "{colors.accent-hover}"
---

# Design System: Saildays

## Overview

**Creative North Star: „Katalog loděnice"**

Totéž, co navyfaces.com (směr A2 „editorial katalog", schválený majitelem pro Navy a jeho slovy „udělat stejně jako web ciferníků" i pro Saildays): hodně vzduchu, jeden velký vizuál na plochu, odvážné široké písmo, plochy střídavě porcelán a navy, žádné karty, štítky ani mřížky. Místo ciferníku je objektem telefon se skutečným snímkem aplikace v CSS rámečku; funkce bez snímku (PDF deník, motohodiny, pauza) dostávají typografický objekt: list papírového deníku v monospace, účetní řádky s velkými čísly, časovou osu.

Paleta je Saildays, ne Navy: navy `#0b3a5c` z ikony je zároveň inkoust textu i barva celoplošných pásů, akcent je modrá `#1971c2` (theme aplikace) jen na hlavním tlačítku. Žádná oranžová. Na rozdíl od Navy má web tmavý režim (`prefers-color-scheme`), protože ho měl i dosavadní web a aplikace.

**Key Characteristics:**
- telefon se skutečným snímkem jako největší věc na obrazovce (hero až 400 px, listy funkcí 340 px),
- Archivo rozšířené a těžké na nadpisy, stejná rodina na text, monospace jen tam, kde jde o zápis deníku,
- list funkcí přes celou šířku, střídavě porcelán / navy,
- modrá jen na tlačítko „Coming soon on Google Play",
- žádné štítky nad nadpisy, pilulky, ikony ani karty; „Novinka 1.1" je podtitul pod nadpisem.

## Colors

Chladný porcelán a navy z ikony aplikace, jedna akcentová modrá z aplikace.

### Primary
- **Akcentová modrá** (#1971c2): výhradně hlavní tlačítko (hero a kotva `#get`). Nikde jinde, ani na odkazech a fokusu. Hover #1864ab.

### Neutral
- **Porcelán** (#f2f5f8): podklad stránky. **Porcelán 2** (#e6edf3): patička.
- **Navy inkoust** (#0b3a5c): text a nadpisy na porcelánu i celoplošné pásy (sudé listy funkcí, sekce „brzy"). **Inkoust 2** (#4a6378): vedlejší text.
- Na navy: text **#eaf2f8**, vedlejší **ocel** (#a9c8de) a **ocel 2** (#7fa6c2). **Nebe** (#8fc8f0, z plachty v ikoně) jen pro tučné zvýraznění na navy.
- **Linka** (#d0dbe5): tenké dělicí čáry.
- **Papír** (#fffdf6), **inkoust papíru** (#1b2430), tlumený text papíru (#5a6270) a linka papíru (#c9c3b4): jen list PDF deníku, v obou režimech stejné.

### Dark mode
Porcelán → #0b1620, porcelán 2 → #0f1d2a, inkoust → #e6eef5, inkoust 2 → #9fb6c8, linka → #213447. Navy pásy zůstávají #0b3a5c (jsou světlejší než pozadí, rytmus drží). Akcent a papír beze změny.

**The One Signal Rule.** Modrá #1971c2 je na obrazovce nejvýš dvakrát a vždy znamená „do obchodu".

## Typography

**Display Font:** Archivo (proměnné, šířka 62.5-125, řez 100-900), lokální woff2 v `assets/fonts/` (OFL, stažené build skriptem z Google Fonts, mimo git)
**Body Font:** Archivo
**Mono Font:** ui-monospace, SF Mono, Menlo, Consolas (jen řádky deníku a časové osy)

**Character:** jedna rodina, hierarchie jen velikostí, šířkou a řezem. Nadpisy široké (wdth 112) a těžké (800-850), text normální šířky.

### Hierarchy
- **Display** (850, clamp 2.8-5.8rem, 0.92): h1 úvodu.
- **Headline** (800, clamp 2-3.4rem, 0.95): h2 sekcí.
- **Feature name** (800, clamp 2.2-4.2rem): h3 listů funkcí.
- **Figure** (800, clamp 1.8-2.8rem, tabular-nums): čísla motohodin.
- **Body** (400, 1.0625-1.125rem, 1.6): text do 34rem šířky v listech, 42rem v textových sekcích.
- **Wordmark** (800, wdth 118, 1.25rem): „Saildays" vedle ikony v hlavičce a patičce.

**The No Kicker Rule.** Nad nadpisem nikdy štítek; „New in 1.1" je podtitul pod nadpisem jako běžný text.

## Layout

Kontejner 1320 px s okrajem clamp(16-56 px). Hero ve dvou sloupcích (text 1.1fr, telefon 0.9fr), pod 820 px jeden sloupec v pořadí nadpis, telefon, text, tlačítko přes celou šířku. Listy funkcí: vizuál a text vedle sebe, u sudých listů prohozené a na navy; pod 820 px vizuál vždy nahoře. Textové sekce (jak to funguje, soukromí, jazyky) v jednom sloupci do 42rem. Hlavička jeden řádek i na 390 px v CS/DE/FR (odkaz na funkce se pod 480 px schová, přepínač jazyka je jen kód).

## Elevation & Depth

Plochý systém, hloubku má jen telefon: `0 1px 2px rgba(11,58,92,.12), 0 40px 80px -30px rgba(11,58,92,.55)` na porcelánu, na navy černý stín `0 40px 80px -30px rgba(0,0,0,.7)`. List papíru má měkký stín papíru na stole. Žádné stíny na tlačítkách ani plochách.

## Shapes

Všechno hranaté (tlačítka, pásy, přepínač jazyka), jediné zaoblení je rámeček telefonu (44 px vně, 32 px displej, padding 12 px, soustředně) a ikona v hlavičce (8 px). Obrázky mají 1px obrys (černý 10 % na světlé, bílý 10 % na navy).

## Components

### Buttons
- **Primary:** modrá, bílý text, hranaté, 52 px výška, 700, při stisku scale(.96). Na mobilu přes celou šířku.
- Vedlejší akce jsou podtržené odkazy (offset 4 px, při hoveru 2 px), ne tlačítka.

### Telefon (`.phone`)
Rámeček #0a1a28, padding 12 px, radius 44/32, uvnitř skutečný snímek 540×1200 (hero 540×1080). Žádné kreslené tlačítko ani výřez kamery.

### List funkce (`.spread`)
Vizuál (telefon, nebo typografický objekt) + jméno 2.2-4.2rem, volitelný podtitul, odstavec do 34rem.

### Typografické objekty
- **Papír** (`.paper`): list PDF deníku, monospace tabulka čas / poloha / kurz / rychlost / zápis, dole podpisové linky velitele a data.
- **Účet** (`.ledger`): řádky s linkou, popisek vlevo, číslo vpravo v display řezu s tabular-nums.
- **Osa** (`.timeline`): monospace řádky, přeškrtnutý řádek = odstraněný úsek.

### Přepínač jazyků
`<details>` s glóbem a kódem jazyka (EN), seznam 5 jazyků, funguje bez JS. V patičce všechny jazyky jako odkazy.

### Cookie lišta
Beze změny (`js/cookie-consent.js`), jen texty i v DE/FR/ES.

## Do's and Don'ts

### Do:
- **Do** ukazovat aplikaci jako skutečný snímek v telefonu, velký.
- **Do** střídat porcelán a navy celými pásy.
- **Do** funkce bez snímku řešit typograficky (papír, čísla, osa), ne obrázkem.

### Don't:
- **Don't** karty, pilulky, štítky nad nadpisy, mřížky, ikony u odstavců.
- **Don't** modrou mimo hlavní tlačítko, oranžovou vůbec.
- **Don't** generované nebo upravené snímky aplikace.
- **Don't** Google Fonts z cizí domény (zásady je nezmiňují), písmo jen lokálně.
