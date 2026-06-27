#!/bin/bash
# Obnovení ze zálohy
# Použití: ./scripts/restore.sh <backup-soubor.tar.gz> [docker-compose-file]
#   Prod: ./scripts/restore.sh jidlo-backup-2026-06-27.tar.gz
#   Dev:  ./scripts/restore.sh jidlo-backup-2026-06-27.tar.gz docker-compose.yml

set -e

if [ -z "$1" ]; then
    echo "Použití: $0 <backup-soubor.tar.gz> [docker-compose-file (default: docker-compose.prod.yml)]"
    exit 1
fi

BACKUP_FILE="$1"
COMPOSE_FILE="-f ${2:-docker-compose.prod.yml}"
BACKUP_DIR="/tmp/jidlo-restore"

rm -rf "${BACKUP_DIR}"
mkdir -p "${BACKUP_DIR}"

echo "Rozbaluji archiv..."
tar -xzf "${BACKUP_FILE}" -C "${BACKUP_DIR}" --strip-components=1

echo "Importuji databázi..."
docker compose ${COMPOSE_FILE} exec -T db sh -c 'mysql -u wordpress -p"$MYSQL_PASSWORD" wordpress' < "${BACKUP_DIR}/database.sql"

if [ -d "${BACKUP_DIR}/uploads" ]; then
    echo "Kopíruji nahrané soubory..."
    docker compose ${COMPOSE_FILE} cp "${BACKUP_DIR}/uploads" wordpress:/var/www/html/wp-content/uploads
fi

rm -rf "${BACKUP_DIR}"

echo "Obnovení dokončeno."
