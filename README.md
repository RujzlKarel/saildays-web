# saildays-web

Statický web aplikace Saildays pro Android: úvodní stránka a zásady ochrany soukromí.

| URL | Soubor |
|---|---|
| https://saildays.app/ | `index.html` |
| https://saildays.app/privacy/ (en) | `privacy/index.html` |
| https://saildays.app/cs/privacy/ (cs) | `cs/privacy/index.html` |

Zdroj aplikace je v soukromém repu `RujzlKarel/Saildays`. Tento repo je veřejný jen proto, že GitHub Pages ze soukromého repa vyžaduje placený plán. Obsahuje jen web, nic z aplikace.

## Nasazení

GitHub Pages ze větve `main`, kořen `/`. Každý push do `main` web přenasadí. Vlastní doména `saildays.app` (soubor `CNAME`).

## Kontrola

`./check.sh` ověří, že obě stránky existují, mají kontakt `privacy@saildays.app`, klíčová fakta (poloha jen v telefonu, záloha do vlastního účtu Google včetně možného nešifrování bez zámku obrazovky, export jen na pokyn, žádné reklamy ani analytika) a neobsahují dlouhé pomlčky.

## Krok pro majitele: DNS `saildays.app`

U registrátora domény nastavit:

| Typ | Název | Hodnota |
|---|---|---|
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| AAAA | @ | 2606:50c0:8000::153 |
| AAAA | @ | 2606:50c0:8001::153 |
| AAAA | @ | 2606:50c0:8002::153 |
| AAAA | @ | 2606:50c0:8003::153 |
| CNAME | www | rujzlkarel.github.io |

Po propsání DNS v GitHubu (Settings, Pages) zapnout Enforce HTTPS (`.app` HTTPS vyžaduje). Dále založit schránku nebo alias `privacy@saildays.app`. Kontrola: `curl -sI https://saildays.app/privacy/ | head -1` vrátí `HTTP/2 200`.
