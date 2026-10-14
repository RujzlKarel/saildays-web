# saildays-web

Veřejné repo se statickým webem Saildays (saildays.app): úvodní stránka `index.html` (en) a `cs/index.html` (cs), zásady `privacy/index.html` (en) a `cs/privacy/index.html` (cs), obrázky v `img/`. Žádný build, CSS inline (v obou úvodních stránkách stejný blok), žádné skripty.

- Nasazení: `./deploy.sh` (FTP na Blueboard, kořen `saildays_app/www/`). Push do gitu web nenasadí. Přístup v `~/.config/saildays/ftp.properties` (Secret Manager `saildays-ftp-properties`), nikdy do gitu.
- Zdroj aplikace je v soukromém `RujzlKarel/Saildays`; sem nepatří nic z něj.
- Úvodní stránky drž v obou jazycích obsahově stejné (stejné sekce a obrázky) a popisuj jen to, co aplikace opravdu umí. Screenshoty viz README, sekce Screenshoty.
- Zásady musí odpovídat chování aplikace (data jen v telefonu, záloha Androidu, export jen na pokyn, bez reklam a analytiky). Při změně aplikace upravit obě jazykové verze a datum účinnosti a spustit `./check.sh`.
- Nikdy dlouhá pomlčka, jen `-`.
