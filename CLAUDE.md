# saildays-web

Veřejné repo se statickým webem Saildays (saildays.app): `index.html`, `privacy/index.html` (en), `cs/privacy/index.html` (cs). Žádný build, CSS inline, žádné skripty.

- Nasazení: `./deploy.sh` (FTP na Blueboard, kořen `saildays_app/www/`). Push do gitu web nenasadí. Přístup v `~/.config/saildays/ftp.properties` (Secret Manager `saildays-ftp-properties`), nikdy do gitu.
- Zdroj aplikace je v soukromém `RujzlKarel/Saildays`; sem nepatří nic z něj.
- Zásady musí odpovídat chování aplikace (data jen v telefonu, záloha Androidu, export jen na pokyn, bez reklam a analytiky). Při změně aplikace upravit obě jazykové verze a datum účinnosti a spustit `./check.sh`.
- Nikdy dlouhá pomlčka, jen `-`.
