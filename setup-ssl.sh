#!/bin/bash

# Configure SSL/HTTPS avec Let's Encrypt pour KOKORIKO Backend
# Usage: bash setup-ssl.sh

set -e

DOMAIN="kokorikobackend.yingr-ai.com"
EMAIL="admin@yingr-ai.com"  # Changer avec ton email

echo "========================================="
echo "🔒 Configuration SSL/HTTPS"
echo "========================================="

# Step 1: Install Certbot
echo "📦 Installation de Certbot..."
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx

# Step 2: Generate SSL Certificate
echo "🔐 Génération du certificat SSL..."
sudo certbot certonly --nginx \
  -d $DOMAIN \
  --non-interactive \
  --agree-tos \
  -m $EMAIL

# Step 3: Update Nginx Configuration with SSL
echo "⚙️  Configuration de Nginx avec SSL..."

NGINX_CONFIG="/etc/nginx/sites-available/kokorikobackend"

sudo tee $NGINX_CONFIG > /dev/null << 'EOF'
# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name kokorikobackend.yingr-ai.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name kokorikobackend.yingr-ai.com;

    # SSL Certificates
    ssl_certificate /etc/letsencrypt/live/kokorikobackend.yingr-ai.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/kokorikobackend.yingr-ai.com/privkey.pem;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:4223;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:4223;
    }

    # Logs
    access_log /var/log/nginx/kokorikobackend.access.log;
    error_log /var/log/nginx/kokorikobackend.error.log;
}
EOF

# Step 4: Test and reload Nginx
echo "✅ Test de la configuration Nginx..."
sudo nginx -t
sudo systemctl reload nginx

# Step 5: Setup auto-renewal
echo "🔄 Configuration du renouvellement automatique..."
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Step 6: Verify SSL
echo ""
echo "========================================="
echo "🎉 SSL/HTTPS configuré avec succès !"
echo "========================================="
echo ""
echo "📋 Vérification SSL:"
curl -I https://kokorikobackend.yingr-ai.com/
echo ""
echo "🔗 Accès sécurisé:"
echo "   https://kokorikobackend.yingr-ai.com"
echo "   https://kokorikobackend.yingr-ai.com/docs"
echo ""
echo "📅 Certificat valide jusqu'au:"
sudo certbot certificates -d kokorikobackend.yingr-ai.com
