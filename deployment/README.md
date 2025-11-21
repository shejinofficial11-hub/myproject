# Jarvis AI Assistant - Deployment Guide

This guide provides comprehensive instructions for deploying Jarvis AI Assistant as a service in production environments.

## Deployment Options

### 1. Docker Deployment (Recommended)

Docker deployment provides the easiest and most portable way to run Jarvis in production.

**Prerequisites:**
- Docker 20.0+
- Docker Compose 2.0+

**Quick Start:**
```bash
# Clone the repository
git clone <repository-url>
cd myproject

# Make deployment script executable
chmod +x deployment/docker-deploy.sh

# Run deployment
./deployment/docker-deploy.sh
```

**Manual Docker Setup:**
```bash
# Create environment file
cp .env.example .env
# Edit .env with your API keys

# Build and start
docker-compose up --build -d

# Check status
docker ps
docker logs jarvis-assistant
```

### 2. Linux Systemd Service

Deploy Jarvis as a native Linux service using systemd.

**Prerequisites:**
- Ubuntu 20.04+ / CentOS 8+ / Debian 10+
- Python 3.9+
- Administrative privileges

**Automated Deployment:**
```bash
# Make script executable
chmod +x deployment/deploy-linux.sh

# Run deployment (requires sudo)
sudo ./deployment/deploy-linux.sh
```

**Manual Setup:**

1. **Create Jarvis User:**
```bash
sudo useradd -r -s /bin/false -d /opt/jarvis jarvis
```

2. **Install Dependencies:**
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-dev portaudio19-dev ffmpeg
```

3. **Install Application:**
```bash
sudo mkdir -p /opt/jarvis
sudo cp -r . /opt/jarvis/
sudo chown -R jarvis:jarvis /opt/jarvis
```

4. **Install Python Dependencies:**
```bash
cd /opt/jarvis
sudo -u jarvis python3 -m pip install -r requirements.txt
```

5. **Configure Environment:**
```bash
sudo mkdir -p /etc/jarvis
sudo cp .env.example /etc/jarvis/.env
sudo chown jarvis:jarvis /etc/jarvis/.env
sudo chmod 600 /etc/jarvis/.env
```

6. **Install Service:**
```bash
sudo cp deployment/jarvis.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable jarvis
sudo systemctl start jarvis
```

### 3. Windows Service

Deploy Jarvis as a Windows service.

**Prerequisites:**
- Windows 10/11 Pro or Server
- Python 3.9+
- Administrative privileges

**Automated Deployment:**
```cmd
# Run as Administrator
deployment\deploy-windows.bat
```

**Manual Setup:**

1. **Install Application:**
```cmd
mkdir C:\Jarvis
xcopy /E /I . C:\Jarvis
cd C:\Jarvis
```

2. **Install Dependencies:**
```cmd
python -m pip install -r requirements.txt
python -m pip install pywin32
```

3. **Configure Environment:**
```cmd
copy .env.example .env
# Edit .env with your API keys
```

4. **Install Service:**
```cmd
python deployment\jarvis-windows-service.py install
sc config JarvisAI start= auto
net start JarvisAI
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure the following:

```bash
# Required API Keys
OPENWEATHER_API_KEY=your_openweather_api_key
NEWS_API_KEY=your_news_api_key
GOOGLE_CALENDAR_API_KEY=your_google_calendar_api_key

# Application Settings
JARVIS_ENV=production
DEBUG=false
LOG_LEVEL=INFO

# Security
ENABLE_FACE_AUTH=true
ALLOW_REMOTE_ACCESS=false

# Feature Flags
ENABLE_WEATHER=true
ENABLE_CALENDAR=true
ENABLE_NOTES=true
ENABLE_NEWS=true
```

### API Keys Setup

1. **OpenWeatherMap API:**
   - Register at https://openweathermap.org/api
   - Get Free tier API key
   - Add to `OPENWEATHER_API_KEY`

2. **News API:**
   - Register at https://newsapi.org
   - Get Developer plan API key
   - Add to `NEWS_API_KEY`

3. **Google Calendar API:**
   - Create project at https://console.developers.google.com
   - Enable Google Calendar API
   - Create credentials
   - Add to `GOOGLE_CALENDAR_API_KEY`

## Management

### Linux/Unix Commands

```bash
# Service Management
sudo systemctl status jarvis          # Check status
sudo systemctl restart jarvis         # Restart service
sudo systemctl stop jarvis            # Stop service
sudo systemctl enable jarvis          # Enable auto-start
sudo systemctl disable jarvis         # Disable auto-start

# Logs
sudo journalctl -u jarvis -f          # Follow logs
sudo tail -f /var/log/jarvis/application.log  # Application logs

# Quick Commands
jarvis-status                         # Custom status command
jarvis-restart                        # Custom restart command
jarvis-logs                           # Custom log viewer
```

### Windows Commands

```cmd
# Service Management
net start JarvisAI                     # Start service
net stop JarvisAI                      # Stop service
sc query JarvisAI                      # Check status

# Logs
type "C:\Jarvis\logs\jarvis.log"      # View logs
```

### Docker Commands

```bash
# Container Management
docker-compose ps                      # Check status
docker-compose restart                 # Restart
docker-compose stop                    # Stop
docker-compose start                   # Start
docker-compose down                    # Stop and remove

# Logs
docker logs -f jarvis-assistant        # Follow logs
docker-compose logs -f jarvis          # Follow logs

# Management
docker exec -it jarvis-assistant bash  # Access container
```

## Health Monitoring

### Built-in Health Monitor

```bash
# Run health check
python deployment/health_monitor.py

# Continuous monitoring
python deployment/health_monitor.py --watch

# JSON output
python deployment/health_monitor.py --json

# Save report
python deployment/health_monitor.py --output health_report.json
```

### Auto-Restart Monitor

```bash
# Start monitor
python deployment/auto_restart.py

# Custom settings
python deployment/auto_restart.py --interval 30 --max-restarts 5

# Run as daemon (Linux)
python deployment/auto_restart.py --daemon
```

## Security

### Network Security

1. **Firewall Configuration:**
```bash
# Linux (ufw)
sudo ufw allow 8000/tcp
sudo ufw enable

# Linux (iptables)
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
```

2. **SSL/TLS:**
```bash
# Use reverse proxy (nginx/apache) with SSL
# Configure in production for secure access
```

### Application Security

1. **Environment Variables:**
   - Never commit `.env` file to version control
   - Use secure storage for API keys
   - Limit API key permissions

2. **File Permissions:**
```bash
# Linux
chmod 600 /etc/jarvis/.env
chown jarvis:jarvis /etc/jarvis/.env
```

3. **Service Isolation:**
   - Run as non-root user
   - Use chroot jail (advanced)
   - Limit file system access

## Backup and Recovery

### Database Backup

```bash
# Create backup script
cat > backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/jarvis/backup"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
sqlite3 /opt/jarvis/jarvis.db ".backup $BACKUP_DIR/jarvis_backup_$DATE.db"
# Keep only last 7 days
find $BACKUP_DIR -name "jarvis_backup_*.db" -mtime +7 -delete
EOF

chmod +x backup_db.sh
./backup_db.sh
```

### Config Backup

```bash
# Backup configuration
sudo cp /etc/jarvis/.env /etc/jarvis/.env.backup.$(date +%Y%m%d)
```

### Automated Backup (Cron)

```bash
# Add to crontab
crontab -e

# Backup database daily at 2 AM
0 2 * * * /opt/jarvis/backup_db.sh

# Backup config weekly
0 3 * * 0 cp /etc/jarvis/.env /etc/jarvis/.env.backup.$(date +\%Y\%m\%d)
```

## Troubleshooting

### Common Issues

1. **Service Won't Start:**
```bash
# Check logs
sudo journalctl -u jarvis -n 50

# Check permissions
ls -la /opt/jarvis/
ls -la /var/log/jarvis/

# Test manually
cd /opt/jarvis
python main.py
```

2. **Port Already in Use:**
```bash
# Check what's using port 8000
sudo netstat -tlnp | grep 8000
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>
```

3. **Permission Denied:**
```bash
# Fix ownership
sudo chown -R jarvis:jarvis /opt/jarvis/
sudo chmod -R 755 /opt/jarvis/

# Fix log directory
sudo chown -R jarvis:jarvis /var/log/jarvis/
```

4. **Missing Dependencies:**
```bash
# Reinstall Python packages
sudo -u jarvis python3 -m pip install -r requirements.txt --force-reinstall
```

### Performance Tuning

1. **Resource Limits:**
```bash
# Check resource usage
htop
iotop

# Set limits in systemd
sudo systemctl edit jarvis
```

2. **Database Optimization:**
```bash
# VACUUM database
sqlite3 jarvis.db "VACUUM;"

# Check database integrity
sqlite3 jarvis.db "PRAGMA integrity_check;"
```

## Support

For deployment issues:

1. Check logs for error messages
2. Run health monitor to diagnose problems
3. Verify all prerequisites are installed
4. Ensure API keys are valid and have proper permissions

## Updates

### Updating Jarvis

```bash
# Linux Service
sudo systemctl stop jarvis
cd /opt/jarvis
git pull
sudo -u jarvis python3 -m pip install -r requirements.txt
sudo systemctl start jarvis

# Docker
docker-compose pull
docker-compose up -d --build

# Windows Service
net stop JarvisAI
cd C:\Jarvis
git pull
python -m pip install -r requirements.txt
net start JarvisAI
```

### Database Migrations

```bash
# Backup before migration
./backup_db.sh

# Update database schema (if needed)
python backend/db.py  # This will create new tables
```