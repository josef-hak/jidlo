# Jídlo — Katalog potravin

Osobní WordPress web pro evidenci potravin s nutričními hodnotami. Mobilní formulář pro rychlé přidání — vyfotit etiketu, zadat hodnoty, hotovo.

## Lokální vývoj

```bash
docker compose up
```

- Web: http://localhost:8080
- Admin: http://localhost:8080/wp-admin (admin / AdminAdmin.123)

## Produkce (VPS)

```bash
cp .env.prod.example .env
nano .env  # vyplnit hesla
docker compose -f docker-compose.prod.yml up -d
```

WordPress běží na `172.17.0.1:8084`.

Ingress (Traefik + Let's Encrypt):

```bash
kubectl apply -f k8s/jidlo.yml
```

Vytvoří Service, Endpoints a Ingress pro `jidlo.jhak.cz` s automatickým TLS certifikátem.

## Struktura

```
├── docker-compose.yml          # lokální dev
├── docker-compose.prod.yml     # produkce
├── k8s/jidlo.yml               # Kubernetes Service + Ingress
├── .env.prod.example           # šablona produkčních hesel
├── .htaccess                   # rewrite rules + upload limit 20MB
├── seed.sh                     # ukázkové potraviny (spustí se při první instalaci)
└── jidlo/                      # WordPress theme
    ├── style.css
    ├── functions.php
    ├── front-page.php          # homepage = katalog
    ├── single-potravina.php    # detail potraviny
    ├── archive-potravina.php   # archive/kategorie
    ├── inc/
    │   ├── cpt-potravina.php   # Custom Post Type + taxonomie
    │   ├── meta-boxes.php      # nutriční hodnoty v admin
    │   └── ajax-handlers.php   # AJAX pro frontend formulář
    ├── page-templates/
    │   └── template-pridat.php # mobilní formulář pro přidání
    └── assets/js/
        ├── food-form.js        # upload fotky + odeslání
        └── catalog.js          # hledání a filtr kategorií
```

## Záloha a obnova

```bash
./scripts/backup.sh                              # vytvoří jidlo-backup-*.tar.gz
./scripts/restore.sh jidlo-backup-2026-06-27.tar.gz  # obnoví ze zálohy
```

Zálohuje databázi (mysqldump) + nahrané fotky (wp-content/uploads).

## Nutriční hodnoty

EU deklarace na 100 g: energie (kJ/kcal), tuky, nasycené MK, sacharidy, cukry, vláknina, bílkoviny, sůl.
