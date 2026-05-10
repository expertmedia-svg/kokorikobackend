#!/bin/bash

# MongoDB Backup Script for KOKORIKO
# Usage: bash backup-mongodb.sh
# Setup cron: 0 2 * * * /home/debian/apps/kokorikobackend/backup-mongodb.sh (Daily at 2 AM)

set -e

# Configuration
MONGO_URI="mongodb+srv://yingreai:gb5vXyTVZmRiQzGZ@cluster0.oabzk0z.mongodb.net/kokoriko_db"
DB_NAME="kokoriko_db"
BACKUP_DIR="/home/debian/apps/kokorikobackend/backups"
RETENTION_DAYS=30
SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"  # Optional

# Create backup directory
mkdir -p $BACKUP_DIR

# Create timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="kokoriko_backup_${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

echo "========================================="
echo "🔄 MongoDB Backup - $TIMESTAMP"
echo "========================================="

# Step 1: Create backup
echo "💾 Création du backup..."
mongodump --uri="$MONGO_URI" --out="$BACKUP_PATH"

# Step 2: Compress backup
echo "🗜️  Compression du backup..."
cd $BACKUP_DIR
tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
rm -rf "$BACKUP_NAME"

# Step 3: Get backup size
BACKUP_SIZE=$(du -h "${BACKUP_NAME}.tar.gz" | cut -f1)
echo "✅ Backup créé: ${BACKUP_NAME}.tar.gz (${BACKUP_SIZE})"

# Step 4: Cleanup old backups
echo "🧹 Suppression des anciens backups (>${RETENTION_DAYS} jours)..."
find $BACKUP_DIR -name "kokoriko_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete

# Step 5: Upload to remote storage (optional)
echo "☁️  Upload vers stockage distant..."

# Exemple avec AWS S3
# aws s3 cp "${BACKUP_NAME}.tar.gz" s3://your-bucket/kokoriko-backups/

# Exemple avec Google Cloud Storage
# gsutil cp "${BACKUP_NAME}.tar.gz" gs://your-bucket/kokoriko-backups/

# Step 6: Send notification
echo "📤 Envoi de la notification..."

if [ ! -z "$SLACK_WEBHOOK" ] && [ "$SLACK_WEBHOOK" != "https://hooks.slack.com/services/YOUR/WEBHOOK/URL" ]; then
    curl -X POST "$SLACK_WEBHOOK" \
      -H 'Content-Type: application/json' \
      -d "{
        \"text\": \"✅ MongoDB Backup Complété\",
        \"attachments\": [
          {
            \"color\": \"good\",
            \"fields\": [
              {
                \"title\": \"Database\",
                \"value\": \"$DB_NAME\",
                \"short\": true
              },
              {
                \"title\": \"Taille\",
                \"value\": \"$BACKUP_SIZE\",
                \"short\": true
              },
              {
                \"title\": \"Fichier\",
                \"value\": \"${BACKUP_NAME}.tar.gz\",
                \"short\": false
              },
              {
                \"title\": \"Timestamp\",
                \"value\": \"$TIMESTAMP\",
                \"short\": true
              }
            ]
          }
        ]
      }"
fi

echo ""
echo "========================================="
echo "🎉 Backup complété !"
echo "========================================="
echo "📁 Localisation: $BACKUP_PATH.tar.gz"
echo "💾 Taille: $BACKUP_SIZE"
echo ""

# Step 7: List recent backups
echo "📋 Derniers backups:"
ls -lh $BACKUP_DIR/*.tar.gz 2>/dev/null | tail -5
