#!/bin/bash

# Setup PM2 Plus Monitoring for KOKORIKO Backend
# Usage: bash setup-monitoring.sh

set -e

echo "========================================="
echo "📊 Configuration PM2 Plus Monitoring"
echo "========================================="

# Step 1: Link to PM2 Plus
echo "🔗 Connexion à PM2 Plus..."
echo ""
echo "1. Visite: https://pm2.io/"
echo "2. Crée un compte gratuit"
echo "3. Copie ta clé API"
echo ""
read -p "Colle ta clé API PM2: " PM2_API_KEY

# Step 2: Connect PM2
echo ""
echo "⚙️  Connexion de PM2..."
pm2 link $PM2_API_KEY $(pm2 info kokoriko-backend | grep "instance_uid" | awk '{print $NF}')

# Step 3: Save PM2 config
echo "💾 Sauvegarde de la configuration PM2..."
pm2 save
pm2 startup

# Step 4: Update ecosystem config with monitoring
echo "📝 Configuration du monitoring avancé..."

cat > /home/debian/apps/kokorikobackend/ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'kokoriko-backend',
      cwd: '/home/debian/apps/kokorikobackend',
      script: './start.sh',
      interpreter: 'bash',
      error_file: './logs/err.log',
      out_file: './logs/out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      exec_mode: 'fork',

      // Monitoring
      min_uptime: '10s',
      listen_timeout: 3000,
      kill_timeout: 5000,

      // Environment
      env: {
        NODE_ENV: 'production'
      },

      // Clustering (optionnel - augmente performance)
      instances: 1,  // Changer à 'max' pour utiliser tous les cores CPU

      // Health checks
      instance_var: 'INSTANCE_ID',

      // Restart strategy
      max_restarts: 10,
      min_uptime: '10s',
    }
  ],

  // Monitoring global
  monitor: true,
  instance_uid: 'kokoriko-backend',
};
EOF

# Step 5: Restart with new config
echo "🔄 Redémarrage avec la nouvelle configuration..."
pm2 restart ecosystem.config.js

# Step 6: Create alerting config
echo "🚨 Configuration des alertes..."

cat > /home/debian/apps/kokorikobackend/.pm2-alerts.json << 'EOF'
{
  "rules": [
    {
      "name": "High Memory Usage",
      "threshold": 500,
      "value": "memory",
      "action": "restart"
    },
    {
      "name": "High CPU Usage",
      "threshold": 90,
      "value": "cpu",
      "action": "alert"
    },
    {
      "name": "App Crashed",
      "trigger": "crash",
      "action": "restart"
    }
  ],
  "webhooks": {
    "restart": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    "crash": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  }
}
EOF

# Step 7: Show status
echo ""
echo "========================================="
echo "✅ PM2 Plus configuré !"
echo "========================================="
echo ""
echo "📊 Dashboard:"
echo "   https://pm2.io/monitoring"
echo ""
echo "📋 Commandes utiles:"
echo "   pm2 monitoring                    # Voir l'état"
echo "   pm2 logs kokoriko-backend         # Voir les logs"
echo "   pm2 info kokoriko-backend         # Info détaillée"
echo "   pm2 save                          # Sauvegarder"
echo ""
pm2 status
