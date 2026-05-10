#!/bin/bash

# KOKORIKO Backend Deployment Script
# Usage: bash deploy.sh

set -e

# Variables
PROJECT_NAME="kokoriko-backend"
PROJECT_DIR="/home/debian/projects/kokoriko-backend"
GIT_REPO="https://github.com/expertmedia-svg/kokorikobackend.git"
VENV_DIR="$PROJECT_DIR/venv"

echo "========================================="
echo "🚀 Déploiement KOKORIKO Backend"
echo "========================================="

# Step 1: Clone or update repository
if [ -d "$PROJECT_DIR" ]; then
    echo "📦 Mise à jour du repository..."
    cd "$PROJECT_DIR"
    git pull origin main
else
    echo "📦 Clonage du repository..."
    mkdir -p /home/debian/projects
    git clone "$GIT_REPO" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

# Step 2: Create/activate virtual environment
echo "🔧 Configuration virtualenv..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

# Step 3: Install dependencies
echo "📥 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# Step 4: Copy environment variables
echo "⚙️  Configuration des variables d'environnement..."
if [ ! -f "$PROJECT_DIR/.env" ]; then
    cp "$PROJECT_DIR/.env.production" "$PROJECT_DIR/.env"
    echo "⚠️  Édite .env avec tes vraies valeurs !"
    nano "$PROJECT_DIR/.env"
fi

# Step 5: Create logs directory
mkdir -p "$PROJECT_DIR/logs"

# Step 6: Stop existing PM2 process
echo "🛑 Arrêt du processus existant..."
pm2 delete "$PROJECT_NAME" 2>/dev/null || true

# Step 7: Start with PM2
echo "▶️  Démarrage de l'application..."
cd "$PROJECT_DIR"
pm2 start ecosystem.config.js --name "$PROJECT_NAME"
pm2 save

# Step 8: Setup Nginx
echo "⚙️  Configuration Nginx..."
sudo cp "$PROJECT_DIR/nginx.conf" "/etc/nginx/sites-available/kokorikobackend"
sudo ln -sf "/etc/nginx/sites-available/kokorikobackend" "/etc/nginx/sites-enabled/kokorikobackend"
sudo rm -f "/etc/nginx/sites-enabled/default"
sudo nginx -t
sudo systemctl reload nginx

# Step 9: Show status
echo ""
echo "========================================="
echo "✅ Déploiement terminé !"
echo "========================================="
pm2 status
echo ""
echo "📝 Logs:"
echo "   PM2: pm2 logs $PROJECT_NAME"
echo "   Nginx: tail -f /var/log/nginx/kokorikobackend.error.log"
echo ""
echo "🔗 API: http://localhost:4223"
echo "📡 Domain: http://kokorikobackend.yingr-ai.com"
