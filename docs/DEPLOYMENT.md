# Deployment Guide

## Prerequisites

- Python 3.11+
- SQL Server 2019+ or Azure SQL Database
- ODBC Driver 18 for SQL Server
- Azure Communication Services account
- Domain name (for production)
- SSL certificate (for production)

## Environment Setup

### 1. Production Server Setup

#### Ubuntu/Debian
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install ODBC Driver
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt update
sudo ACCEPT_EULA=Y apt install msodbcsql18 unixodbc-dev -y
```

### 2. Application Setup

```bash
# Clone repository
git clone <repository-url>
cd portfolio-backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit with production values
```

### 3. Database Setup

```bash
# Run migrations
alembic upgrade head

# Create admin user
python scripts/create_admin.py

# (Optional) Seed sample data
python scripts/seed_data.py
```

## Docker Deployment

### Build and Run

```bash
# Build image
docker build -t portfolio-api:latest .

# Run container
docker run -d \
  --name portfolio-api \
  -p 8000:8000 \
  --env-file .env \
  portfolio-api:latest
```

### Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

## Production Deployment

### Using Systemd

Create `/etc/systemd/system/portfolio-api.service`:

```ini
[Unit]
Description=Portfolio API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/portfolio-backend
Environment="PATH=/var/www/portfolio-backend/venv/bin"
ExecStart=/var/www/portfolio-backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable portfolio-api
sudo systemctl start portfolio-api
sudo systemctl status portfolio-api
```

### Using Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile /var/log/portfolio/access.log \
  --error-logfile /var/log/portfolio/error.log
```

### Nginx Configuration

Create `/etc/nginx/sites-available/portfolio-api`:

```nginx
upstream portfolio_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://portfolio_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/portfolio-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Azure App Service

### Using Azure CLI

```bash
# Login to Azure
az login

# Create resource group
az group create --name portfolio-rg --location eastus

# Create App Service plan
az appservice plan create \
  --name portfolio-plan \
  --resource-group portfolio-rg \
  --sku B1 \
  --is-linux

# Create web app
az webapp create \
  --resource-group portfolio-rg \
  --plan portfolio-plan \
  --name portfolio-api \
  --runtime "PYTHON:3.11"

# Configure environment variables
az webapp config appsettings set \
  --resource-group portfolio-rg \
  --name portfolio-api \
  --settings @appsettings.json

# Deploy
az webapp up \
  --resource-group portfolio-rg \
  --name portfolio-api
```

### appsettings.json

```json
{
  "DATABASE_URL": "mssql+aioodbc://...",
  "SECRET_KEY": "your-secret-key",
  "AZURE_COMMUNICATION_CONNECTION_STRING": "...",
  "FRONTEND_URL": "https://yourdomain.com"
}
```

## Database Migration Strategy

### Zero-Downtime Migrations

```bash
# 1. Backup database
sqlcmd -S server -d database -Q "BACKUP DATABASE..."

# 2. Test migration on staging
alembic upgrade head

# 3. Deploy new code (backwards compatible)
git pull
pip install -r requirements.txt
sudo systemctl restart portfolio-api

# 4. Run migration
alembic upgrade head

# 5. Verify
curl https://api.yourdomain.com/health
```

## SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d api.yourdomain.com

# Auto-renewal (already configured by certbot)
sudo certbot renew --dry-run
```

## Monitoring

### Application Logs

```bash
# View logs
sudo journalctl -u portfolio-api -f

# Log rotation
sudo nano /etc/logrotate.d/portfolio-api
```

```
/var/log/portfolio/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
```

### Health Monitoring

```bash
# Add to crontab
*/5 * * * * curl -f https://api.yourdomain.com/health || systemctl restart portfolio-api
```

## Performance Tuning

### Gunicorn Workers

```bash
# Calculate workers: (2 x CPU cores) + 1
workers = (2 * $(nproc)) + 1
```

### Database Connection Pool

```python
# config.py
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 40
```

### Nginx Caching

```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=100m;

location /api/v1/projects/ {
    proxy_cache api_cache;
    proxy_cache_valid 200 5m;
    # ...
}
```

## Backup Strategy

### Database Backups

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
sqlcmd -S server -d database \
  -Q "BACKUP DATABASE portfoliodb TO DISK='/backups/db_$DATE.bak'"

# Keep last 7 days
find /backups -name "db_*.bak" -mtime +7 -delete
```

### Application Backups

```bash
# Backup application files
tar -czf /backups/app_$(date +%Y%m%d).tar.gz \
  /var/www/portfolio-backend \
  --exclude=venv \
  --exclude=__pycache__
```

## Security Checklist

- [ ] Change SECRET_KEY to strong random value
- [ ] Set DEBUG=False in production
- [ ] Use HTTPS only
- [ ] Configure CORS properly
- [ ] Enable firewall (ufw)
- [ ] Regular security updates
- [ ] Strong database passwords
- [ ] Rate limiting enabled
- [ ] SQL Server encryption enabled
- [ ] Regular backups configured

## Troubleshooting

### Application won't start

```bash
# Check logs
sudo journalctl -u portfolio-api -n 50

# Check Python version
python --version

# Verify environment variables
cat .env
```

### Database connection issues

```bash
# Test ODBC connection
odbcinst -q -d
isql -v "DRIVER={ODBC Driver 18 for SQL Server};SERVER=..."

# Check SQL Server accessibility
telnet server-name 1433
```

### High memory usage

```bash
# Monitor resources
htop
free -h

# Reduce workers
# Decrease connection pool size
```

## Rollback Procedure

```bash
# 1. Stop application
sudo systemctl stop portfolio-api

# 2. Restore database
sqlcmd -S server -d database \
  -Q "RESTORE DATABASE portfoliodb FROM DISK='/backups/db_backup.bak'"

# 3. Checkout previous version
git checkout <previous-commit>
pip install -r requirements.txt

# 4. Restart application
sudo systemctl start portfolio-api
```

## Support

For deployment issues, check:
- Application logs: `/var/log/portfolio/`
- System logs: `sudo journalctl -xe`
- Nginx logs: `/var/log/nginx/`