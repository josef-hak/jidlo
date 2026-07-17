# Jídlo — Katalog potravin

Osobní web pro evidenci potravin s nutričními hodnotami. Staticky generováno pomocí Hugo z YAML dat.

## Lokální vývoj

```bash
# 1. Generovat content z YAML dat
docker compose --profile build run --rm build-data

# 2. Spustit dev server (hot reload)
docker compose up hugo
```

Web: http://localhost:8080

## Přidání nové potraviny

Vytvořit YAML soubor v příslušné kategorii `data/<kategorie>/<slug>.yml`:

```yaml
nazev: Název potraviny
znacka: Výrobce
popis: "Krátký popis."
slozeni: "Složení produktu."
obrazky:
  - imgs/foto-slozeni.jpg
  - imgs/foto-produkt.jpg
nutrice:
  energie_kj: 0
  energie_kcal: 0
  bilkoviny: 0
  sacharidy: 0
  cukry: 0
  vlaknina: 0
  tuky: 0
  nasycene_mk: 0
  sul: 0
```

Fotky uložit do `data/<kategorie>/imgs/`. Po přidání spustit `build-data` a rebuild.

## Produkce (VPS)

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Nginx s předgenerovaným HTML na `172.17.0.1:8084`.

```bash
kubectl apply -f k8s/jidlo.yml
```

## Struktura

```
├── hugo.toml                    # Hugo konfigurace
├── build.py                     # YAML → Hugo content + kopie fotek
├── data/                        # zdrojová data (YAML + fotky)
│   ├── mlecne-vyrobky/
│   ├── maso-a-uzeniny/
│   ├── ovoce/
│   └── ...
├── layouts/                     # Hugo šablony
│   ├── _default/baseof.html     # hlavička + patička
│   ├── index.html               # homepage = katalog
│   ├── potravina/single.html    # detail potraviny
│   └── partials/food-card.html  # karta potraviny
├── static/                      # CSS, JS, SVG ikony
│   ├── css/style.css
│   ├── js/catalog.js
│   └── imgs/*.svg
├── docker-compose.hugo.yml      # dev server
├── docker-compose.prod.yml      # produkce (nginx)
├── Dockerfile                   # multi-stage build
└── k8s/jidlo.yml                # Kubernetes Ingress
```

## Nutriční hodnoty

EU deklarace na 100 g: energie (kJ/kcal), bílkoviny, sacharidy (cukry), vláknina, tuky (nasycené MK), sůl.
