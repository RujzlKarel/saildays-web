# saildays-web

Statický web aplikace Saildays pro Android: úvodní stránka a zásady ochrany soukromí.

| URL | Soubor |
|---|---|
| https://saildays.app/ | `index.html` |
| https://saildays.app/privacy/ (en) | `privacy/index.html` |
| https://saildays.app/cs/privacy/ (cs) | `cs/privacy/index.html` |

Zdroj aplikace je v soukromém repu `RujzlKarel/Saildays`. Obsahuje jen web, nic z aplikace.

## Nasazení

Hosting Blueboard (server KRIOS), kořen webu `saildays_app/www/` na FTP. Nasazení: `./deploy.sh` - spustí `check.sh`, nahraje soubory přes FTP s TLS (`lftp mirror -R`, bez `.sh`, `.md`, `.git`) a ověří, že všechny tři URL vrací 200.

Přístup v `~/.config/saildays/ftp.properties` (zdroj pravdy GCP Secret Manager, secret `saildays-ftp-properties`, stažení přes `secrets-pull.sh`):

```
SAILDAYS_FTP_HOST=krios.blueboard.cz
SAILDAYS_FTP_USER=...
SAILDAYS_FTP_PASSWORD=...
```

Hostitel je `krios.blueboard.cz`, ne `ftp.saildays.app`: certifikát FTP serveru platí jen pro něj. Doménu, DNS, mail a HTTPS certifikát spravuje Blueboard.

## Kontrola

`./check.sh` ověří, že obě stránky existují, mají kontakt `privacy@saildays.app`, klíčová fakta (poloha jen v telefonu, záloha do vlastního účtu Google včetně možného nešifrování bez zámku obrazovky, export jen na pokyn, žádné reklamy ani analytika) a neobsahují dlouhé pomlčky.

## Zbývá

Založit schránku nebo alias `privacy@saildays.app` v administraci Blueboardu.
