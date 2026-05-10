# 🚀 Guide de Déploiement KOKORIKO Backend

## Prérequis

- Serveur Debian/Linux avec accès SSH
- PM2 installé (`npm install -g pm2`)
- Nginx installé (`sudo apt-get install nginx`)
- Python 3.9+ et pip
- Git
- MongoDB (local ou cloud)

## Étapes de Déploiement

### 1️⃣ Préparation sur le Serveur

```bash
# Connexion au serveur
ssh debian@57.130.47.13 -i ~/.ssh/finavi_rsa

# Créer le répertoire du projet
mkdir -p ~/projects/kokoriko-backend
cd ~/projects/kokoriko-backend

# Cloner le repository
git clone https://github.com/expertmedia-svg/kokorikobackend.git .
```

### 2️⃣ Configuration de l'Application

```bash
# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Copier et configurer les variables d'environnement
cp .env.production .env
nano .env  # Éditer avec tes vraies valeurs
```

**Variables essentielles à configurer** :
```
MONGODB_URL=mongodb://localhost:27017/kokoriko
SECRET_KEY=ta-clé-secrète-très-longue
OPENAI_API_KEY=sk-xxxxx (optionnel)
```

### 3️⃣ Lancer avec PM2

```bash
# Créer les répertoires de logs
mkdir -p logs

# Démarrer l'application
pm2 start ecosystem.config.js --name "kokoriko-backend"

# Sauvegarder la configuration PM2
pm2 save

# Activer le démarrage automatique
pm2 startup
pm2 save
```

### 4️⃣ Configurer Nginx

```bash
# Copier la configuration Nginx
sudo cp nginx.conf /etc/nginx/sites-available/kokorikobackend

# Activer le site
sudo ln -sf /etc/nginx/sites-available/kokorikobackend /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Tester la configuration
sudo nginx -t

# Recharger Nginx
sudo systemctl reload nginx
```

### 5️⃣ SSL/HTTPS (Recommandé)

```bash
# Installer Certbot
sudo apt-get install certbot python3-certbot-nginx

# Générer le certificat
sudo certbot certonly --nginx -d kokorikobackend.yingr-ai.com

# Éditer nginx.conf et décommenter les sections SSL
sudo nano /etc/nginx/sites-available/kokorikobackend

# Recharger Nginx
sudo systemctl reload nginx
```

## 📋 Commandes Utiles

```bash
# Voir le statut
pm2 status

# Voir les logs
pm2 logs kokoriko-backend

# Redémarrer l'application
pm2 restart kokoriko-backend

# Arrêter l'application
pm2 stop kokoriko-backend

# Supprimer l'application
pm2 delete kokoriko-backend

# Voir les logs Nginx
tail -f /var/log/nginx/kokoriko-api.error.log
tail -f /var/log/nginx/kokoriko-api.access.log
```

## 🔄 Mise à Jour

```bash
# Se connecter au serveur
ssh debian@57.130.47.13

# Aller au répertoire du projet
cd ~/projects/kokoriko-backend

# Activer l'environnement virtuel
source venv/bin/activate

# Mettre à jour le code
git pull origin main

# Mettre à jour les dépendances (si nécessaire)
pip install -r requirements.txt

# Redémarrer l'application
pm2 restart kokoriko-backend
```

## ✅ Vérification

```bash
# Vérifier que l'API répond
curl http://localhost:8010/

# Vérifier à travers Nginx
curl http://kokoriko-api.finavi.com/

# Voir le statut PM2
pm2 status
```

## 🔗 URLs

- **API Locale**: http://127.0.0.1:4223
- **API via Nginx**: http://kokorikobackend.yingr-ai.com
- **Docs Swagger**: http://kokorikobackend.yingr-ai.com/docs
- **ReDoc**: http://kokorikobackend.yingr-ai.com/redoc

## 📊 Architecture

```
Nginx (Port 80/443)
    ↓
Reverse Proxy (127.0.0.1:8010)
    ↓
Uvicorn (FastAPI)
    ↓
MongoDB
```

## 🆘 Troubleshooting

### L'application ne démarre pas
```bash
# Vérifier les logs PM2
pm2 logs kokoriko-backend

# Vérifier la syntaxe Python
python3 -m py_compile app/main.py

# Redémarrer en debug
pm2 start ecosystem.config.js --name "kokoriko-backend" --interpreter python3 --no-daemon
```

### Nginx renvoie 502
```bash
# Vérifier que le service Uvicorn est actif
pm2 status

# Vérifier le port 4223
netstat -tlnp | grep 4223

# Vérifier les logs Nginx
tail -f /var/log/nginx/kokorikobackend.error.log
```

### MongoDB non accessible
```bash
# Vérifier MongoDB
mongo --version

# Tester la connexion
mongosh "mongodb://localhost:27017/kokoriko"
```

## 📝 Notes de Sécurité

- ✅ Toujours utiliser HTTPS en production
- ✅ Ne pas committer les `.env` réels dans Git
- ✅ Utiliser des clés secrètes fortes
- ✅ Mettre en place des backups réguliers
- ✅ Monitorer les logs d'erreur
- ✅ Limiter les requêtes avec Nginx rate limiting

## 🎯 Prochaines Étapes

- [ ] Configurer les backups MongoDB
- [ ] Mettre en place la monitoring (PM2 Plus)
- [ ] Ajouter les logs centralisés
- [ ] Configurer les alertes
- [ ] Ajouter un healthcheck endpoint
