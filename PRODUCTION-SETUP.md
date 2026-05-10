# 🚀 KOKORIKO Backend - Production Setup Guide

## État actuel ✅

- ✅ Backend déployé avec PM2
- ✅ Nginx configuré comme reverse proxy
- ✅ App accessible sur `http://kokorikobackend.yingr-ai.com`
- ⏳ À faire : SSL/HTTPS, Monitoring, Backups

---

## 1️⃣ Configuration SSL/HTTPS avec Let's Encrypt

### Pourquoi SSL/HTTPS ?
- 🔒 Chiffrer les données en transit
- 🔐 Sécuriser les authentifications
- 📊 Améliorer le SEO et la confiance

### Installation

Sur le serveur :

```bash
cd /home/debian/apps/kokorikobackend

# Rendre le script executable
chmod +x setup-ssl.sh

# Lancer la configuration
bash setup-ssl.sh
```

**Qu'est-ce que ça fait :**
1. Installe Certbot (gestionnaire de certificats)
2. Génère un certificat SSL gratuit pour `kokorikobackend.yingr-ai.com`
3. Configure Nginx pour rediriger HTTP → HTTPS
4. Ajoute les headers de sécurité
5. Active le renouvellement automatique

**Test :**
```bash
# Vérifier le certificat
curl -I https://kokorikobackend.yingr-ai.com/

# Voir la documentation sécurisée
https://kokorikobackend.yingr-ai.com/docs
```

**Renouvellement automatique** :
- Certbot renouvelle automatiquement 30 jours avant expiration
- Certificat valide 90 jours
- Zéro downtime

---

## 2️⃣ Monitoring avec PM2 Plus

### Pourquoi PM2 Plus ?
- 📊 Monitoring temps réel (CPU, RAM, erreurs)
- 🚨 Alertes automatiques
- 📈 Historique des performances
- 🔄 Auto-restart en cas de crash

### Installation

Sur le serveur :

```bash
cd /home/debian/apps/kokorikobackend

# Rendre le script executable
chmod +x setup-monitoring.sh

# Lancer la configuration
bash setup-monitoring.sh
```

**Démarche :**
1. Script te demande ta clé API PM2
2. Crée un compte gratuit à https://pm2.io/
3. Copie ta clé API
4. Colle dans le script

**Accès au dashboard :**
```
https://pm2.io/monitoring
```

**Commandes utiles :**
```bash
# Voir l'état en temps réel
pm2 monitoring

# Voir les logs
pm2 logs kokoriko-backend

# Info détaillée
pm2 info kokoriko-backend

# Redémarrer
pm2 restart kokoriko-backend

# Arrêter
pm2 stop kokoriko-backend
```

**Alertes configurées :**
- 🔴 Mémoire > 500MB → Auto-restart
- 🟡 CPU > 90% → Alerte
- ☠️ App crash → Auto-restart

---

## 3️⃣ Backups MongoDB Réguliers

### Pourquoi des backups ?
- 💾 Protection contre la perte de données
- 🔄 Récupération en cas de problème
- 📋 Conformité réglementaire

### Installation

Sur le serveur :

```bash
cd /home/debian/apps/kokorikobackend

# Rendre le script executable
chmod +x backup-mongodb.sh

# Tester une fois
bash backup-mongodb.sh

# Vérifier que ça a fonctionné
ls -lh backups/
```

### Configuration automatique (Cron)

Ajouter un backup automatique chaque jour à 2h du matin :

```bash
# Éditer crontab
crontab -e

# Ajouter cette ligne :
0 2 * * * /home/debian/apps/kokorikobackend/backup-mongodb.sh >> /home/debian/apps/kokorikobackend/logs/backup.log 2>&1

# Vérifier que c'est enregistré
crontab -l
```

**Exemple de cron :**
```
# Hourly backup
0 * * * * /home/debian/apps/kokorikobackend/backup-mongodb.sh

# Daily backup at 2 AM
0 2 * * * /home/debian/apps/kokorikobackend/backup-mongodb.sh

# Weekly backup every Sunday at 3 AM
0 3 * * 0 /home/debian/apps/kokorikobackend/backup-mongodb.sh
```

### Stockage des backups

Actuellement : `/home/debian/apps/kokorikobackend/backups/`

**Options pour stockage distant :**

**AWS S3** :
```bash
# Installer AWS CLI
sudo apt-get install awscli

# Configurer
aws configure

# Modifier le script pour ajouter :
aws s3 cp "${BACKUP_NAME}.tar.gz" s3://your-bucket/kokoriko-backups/
```

**Google Cloud Storage** :
```bash
# Installer gsutil
sudo apt-get install google-cloud-sdk

# Configurer
gcloud init

# Modifier le script pour ajouter :
gsutil cp "${BACKUP_NAME}.tar.gz" gs://your-bucket/kokoriko-backups/
```

**Dropbox** :
```bash
# Installer Rclone
sudo apt-get install rclone

# Configurer
rclone config

# Modifier le script pour ajouter :
rclone copy "${BACKUP_NAME}.tar.gz" dropbox:/kokoriko-backups/
```

### Notification Slack (optionnel)

Pour recevoir une notification à chaque backup :

1. Crée un Webhook Slack
2. Remplace l'URL dans `backup-mongodb.sh`
3. Reçois une notif à chaque backup ✅

---

## 🔍 Checklist de Production

- [ ] SSL/HTTPS configuré
  ```bash
  curl -I https://kokorikobackend.yingr-ai.com/
  ```

- [ ] PM2 Plus connecté
  ```bash
  pm2 info kokoriko-backend
  ```

- [ ] Backup MongoDB fonctionnel
  ```bash
  ls -lh /home/debian/apps/kokorikobackend/backups/
  ```

- [ ] Cron backup activé
  ```bash
  crontab -l | grep backup
  ```

- [ ] Logs centralisés
  ```bash
  pm2 logs kokoriko-backend --lines 50
  ```

- [ ] Performances acceptables
  ```bash
  curl -w "@curl-format.txt" -o /dev/null -s https://kokorikobackend.yingr-ai.com/
  ```

---

## 📊 Monitoring Dashboard

**Voir l'état en temps réel :**

```bash
# Terminal
pm2 monitoring

# Web Dashboard
https://pm2.io/monitoring
```

**Métriques clés à surveiller :**
- 💾 Mémoire : < 300MB (optimal)
- 💻 CPU : < 30% (normal)
- 📊 Uptime : > 99%
- ⏱️ Response time : < 200ms

---

## 🆘 Troubleshooting

### L'app ne démarre pas

```bash
# Voir les erreurs
pm2 logs kokoriko-backend --err

# Vérifier le statut
pm2 status

# Redémarrer
pm2 restart kokoriko-backend
```

### Certificat SSL expiré

```bash
# Renouveler manuellement
sudo certbot renew

# Vérifier l'expiration
sudo certbot certificates
```

### Backup échoue

```bash
# Vérifier les permissions
ls -la /home/debian/apps/kokorikobackend/backups/

# Vérifier la connexion MongoDB
mongosh "mongodb+srv://yingreai:..."

# Tester le backup
bash backup-mongodb.sh -v  # verbose mode
```

---

## 🎯 Prochaines étapes

1. **Implémenter rate limiting** dans Nginx
   ```nginx
   limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
   ```

2. **Ajouter un health check** Kubernetes-ready
   ```bash
   curl http://localhost:4223/health
   ```

3. **Configurer les logs centralisés** (ELK, Splunk)
   ```
   Filebeat → Elasticsearch → Kibana
   ```

4. **Ajouter WAF** (Web Application Firewall)
   ```
   ModSecurity ou AWS WAF
   ```

5. **CI/CD automatisé** (GitHub Actions)
   ```
   Push → Test → Build → Deploy
   ```

---

## 📞 Support

Si tu as besoin d'aide :
- 📧 Email: admin@yingr-ai.com
- 🐛 Issues: https://github.com/your-repo/issues
- 💬 Discord: Rejoins notre serveur

---

**Last updated:** 2026-05-10  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
