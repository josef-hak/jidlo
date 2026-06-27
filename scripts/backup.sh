#!/bin/bash
# Záloha databáze + nahraných fotek
# Použití: ./scripts/backup.sh [docker-compose-file]
#   Prod: ./scripts/backup.sh
#   Dev:  ./scripts/backup.sh docker-compose.yml
# Výstup: jidlo-backup-YYYY-MM-DD_HHMMSS.tar.gz

set -e

TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)
BACKUP_NAME="jidlo-backup-${TIMESTAMP}"
BACKUP_DIR="/tmp/${BACKUP_NAME}"

mkdir -p "${BACKUP_DIR}"

COMPOSE_FILE="-f ${1:-docker-compose.prod.yml}"

echo "Exportuji databázi..."
docker compose ${COMPOSE_FILE} exec -T db sh -c 'mysqldump -u wordpress -p"$MYSQL_PASSWORD" wordpress' > "${BACKUP_DIR}/database.sql"

echo "Kopíruji nahrané soubory..."
docker compose ${COMPOSE_FILE} cp wordpress:/var/www/html/wp-content/uploads "${BACKUP_DIR}/uploads" 2>/dev/null || echo "Žádné uploads."

echo "Balím archiv..."
tar -czf "${BACKUP_NAME}.tar.gz" -C /tmp "${BACKUP_NAME}"
rm -rf "${BACKUP_DIR}"

echo "Záloha uložena: ${BACKUP_NAME}.tar.gz"
