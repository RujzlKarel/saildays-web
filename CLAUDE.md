# saildays-web

Veřejné repo se statickým webem Saildays (saildays.app): úvodní stránka `index.html` (en) a `cs/index.html` (cs), zásady `privacy/index.html` (en) a `cs/privacy/index.html` (cs), obrázky v `img/`. Žádný build, CSS inline (v obou úvodních stránkách stejný blok). Jediné skripty: Consent Mode + GTM `GTM-5BL8T5LD` (GA4 `G-9MD50SXETV`) inline v `<head>` a cookie lišta `js/cookie-consent.js`; jiné skripty `check.sh` odmítne. Detail v README, sekce Měření a cookies. ID nejsou tajná.

- Nasazení: `./deploy.sh` (FTP na Blueboard, kořen `saildays_app/www/`). Push do gitu web nenasadí. Přístup v `~/.config/saildays/ftp.properties` (Secret Manager `saildays-ftp-properties`), nikdy do gitu.
- Zdroj aplikace je v soukromém `RujzlKarel/Saildays`; sem nepatří nic z něj.
- Úvodní stránky drž v obou jazycích obsahově stejné (stejné sekce a obrázky) a popisuj jen to, co aplikace opravdu umí. Screenshoty viz README, sekce Screenshoty.
- Zásady musí odpovídat chování aplikace (data jen v telefonu, záloha Androidu, export jen na pokyn, bez reklam a analytiky). Analytika je jen na webu po souhlasu, popsaná v sekci Website / Web; při změně měření na webu ji upravit. Při změně aplikace upravit obě jazykové verze a datum účinnosti a spustit `./check.sh`.
- Nová stránka musí dostat stejný `<head>` blok (consent + GTM, ikony, `og:*`), `<noscript>` za `<body>` a cookie lištu na konci `<body>`, a patří do `sitemap.xml`.
- GTM kontejner upravovat a publikovat přes `~/GitHub/GTMTools` s `GTM_CONTAINER_ID=GTM-5BL8T5LD` (ne rujzl.cz GTM-T4L7WQ); na miniai navíc `GTM_TOKEN=~/GitHub/GA4Tool/gtm_token.json`.
- Nikdy dlouhá pomlčka, jen `-`.
