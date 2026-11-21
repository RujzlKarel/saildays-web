# Saildays - produktový kontext webu

Sepsáno 14. 11. 2026 Claude z briefu majitele (Karel byl na cestě, rozhovor neproběhl); položky označené *(předpoklad)* jsou odvozené z podkladů aplikace (`Saildays/README.md`, `store/listing-*.md`, `docs/konkurence.md`), ne potvrzené majitelem.

## Co to je

Saildays je lodní deník pro Android, který se píše sám: nahrává trasu, zapisuje změny kurzu, ptá se na zastavení a vyplutí. Placená jednorázově (4,99 USD, v Česku 129,99 Kč, bez předplatného), bez účtu, bez reklam, data jen v telefonu. Vydává Nice One s.r.o., Brno. Web `saildays.app` je jediná veřejná stránka aplikace, v Google Play je od 21. 11. 2026 (https://play.google.com/store/apps/details?id=app.saildays).

## Pro koho

Rekreační jachtaři a skipperi na charterech v Chorvatsku a ve Středomoří, čeští i zahraniční (web v EN, CS, DE, FR, ES; aplikace ve 21 jazycích). Lidé, kteří dnes vedou papírový deník nebo ho nevedou vůbec, protože u kormidla není čas psát. *(předpoklad)* Část z nich potřebuje doklad námořní praxe (míle) k průkazu.

## Co má návštěvník udělat

1. **Hlavní akce:** nainstalovat aplikaci z Google Play. Tlačítko „Get it on Google Play" (v úvodu i v sekci `#get`) vede přímo do obchodu (`PLAY_URL` v `tools/build.py`).
2. **Druhá akce:** přečíst si, co aplikace umí (`#features`).

## Důkazy (jen ověřené v podkladech)

- Jednorázový nákup bez předplatného, bez účtu, bez reklam a analytiky v aplikaci.
- Data zůstávají v telefonu; z internetu se stahují jen mapové dlaždice (OpenFreeMap, OpenSeaMap).
- Automatický zápis změn kurzu (30° a víc), návrhy zastavení a vyplutí v notifikaci.
- Verze 1.1: PDF deník ve vzhledu papírového s podpisovou linkou velitele, motohodiny, pauza záznamu a úprava začátku/konce plavby, 21 jazyků.
- Export ZIP (GPX + JSON + fotky) a PDF.

## Tón

Věcný, námořnický, bez marketingových frází a superlativů. Krátké věty, konkrétní čísla (30°, 10 minut, 200 MB). Formulace přednostně z `store/listing-en.md` a `listing-cs.md`. Oslovení: EN you, CS vy, DE du, FR vous, ES tú (jako texty aplikace).

## Co web nesmí

- Slibovat funkce, které aplikace nemá (import počasí, kotevní hlídka, sync, iOS).
- Tvrdit, že je v Google Play, dokud není.
- Používat smyšlené recenze, loga, čísla uživatelů.
- Dlouhé pomlčky.
- Falešné screenshoty: pro funkce bez snímku (PDF, motohodiny, pauza) jen typografické řešení.
- Zásady ochrany soukromí měnit obsahově (jen EN a CS, DE/FR/ES odkazují na EN).
