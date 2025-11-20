#!/bin/bash

# Jarvis AI Assistant - Linux Deployment Script
# This script installs and configures Jarvis as a systemd service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="jarvis"
APP_USER="jarvis"
APP_DIR="/opt/jarvis"
SERVICE_NAME="jarvis"

echo -e "${GREEN}🚀 Starting Jarvis AI Assistant deployment for Linux${NC}"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root${NC}"
   exit 1
fi

# Create Jarvis user
echo -e "${YELLOW}Creating Jarvis user...${NC}"
if ! id "$APP_USER" &>/dev/null; then
    useradd -r -s /bin/false -d "$APP_DIR" "$APP_USER"
fi

# Install system dependencies
echo -e "${YELLOW}Installing system dependencies...${NC}"
apt-get update
apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    portaudio19-dev \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    libgtk-3-0 \
    pkg-config \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    libffi-dev \
    libssl-dev

# Create application directory
echo -e "${YELLOW}Creating application directory...${NC}"
mkdir -p "$APP_DIR"
mkdir -p "/var/log/$APP_NAME"
mkdir -p "/etc/$APP_NAME"

# Copy application files
echo -e "${YELLOW}Copying application files...${NC}"
cp -r . "$APP_DIR/"
chown -R "$APP_USER:$APP_USER" "$APP_DIR"

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
cd "$APP_DIR"
sudo -u "$APP_USER" python3 -m pip install --upgrade pip
sudo -u "$APP_USER" python3 -m pip install -r requirements.txt
sudo -u "$APP_USER" python3 -m pip install python-dotenv

# Setup environment file
echo -e "${YELLOW}Setting up environment configuration...${NC}"
if [ ! -f "/etc/$APP_NAME/.env" ]; then
    cp .env.example "/etc/$APP_NAME/.env"
    chown "$APP_USER:$APP_USER" "/etc/$APP_NAME/.env"
    chmod 600 "/etc/$APP_NAME/.env"
    echo -e "${YELLOW}Please edit /etc/$APP_NAME/.env with your API keys${NC}"
fi

# Install systemd service
echo -e "${YELLOW}Installing systemd service...${NC}"
cp deployment/jarvis.service "/etc/systemd/system/"
systemctl daemon-reload

# Enable and start the service
echo -e "${YELLOW}Enabling and starting Jarvis service...${NC}"
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"

# Setup log rotation
echo -e "${YELLOW}Setting up log rotation...${NC}"
cat > "/etc/logrotate.d/$APP_NAME" << EOF
/var/log/$APP_NAME/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    copytruncate
    su $APP_USER $APP_USER
}
EOF

# Setup firewall rules (optional)
echo -e "${YELLOW}Setting up firewall rules...${NC}"
if command -v ufw &> /dev/null; then
    ufw allow 8000/tcp
    echo "Firewall rules added for port 8000"
fi

# Create startup script
echo -e "${YELLOW}Creating management scripts...${NC}"
cat > "/usr/local/bin/$APP_NAME-status" << EOF
#!/bin/bash
systemctl status $SERVICE_NAME
EOF

cat > "/usr/local/bin/$APP_NAME-restart" << EOF
#!/bin/bash
systemctl restart $SERVICE_NAME
EOF

cat > "/usr/local/bin/$APP_NAME-logs" << EOF
#!/bin/bash
tail -f /var/log/$APP_NAME/application.log
EOF

chmod +x "/usr/local/bin/$APP_NAME-"*

# Check service status
sleep 3
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo -e "${GREEN}✅ Jarvis AI Assistant deployed successfully!${NC}"
    echo -e "${GREEN}Service status: $(systemctl is-active $SERVICE_NAME)${NC}"
    echo ""
    echo -e "${YELLOW}Useful commands:${NC}"
    echo -e "  • Status: $APP_NAME-status"
    echo -e "  • Restart: $APP_NAME-restart"
    echo -e "  • Logs: $APP_NAME-logs"
    echo -e "  • Config: /etc/$APP_NAME/.env"
    echo -e "  • Application: $APP_DIR"
    echo ""
    echo -e "${YELLOW}Don't forget to:${NC}"
    echo -e "  1. Edit /etc/$APP_NAME/.env with your API keys"
    echo -e "  2. Restart service: $APP_NAME-restart"
else
    echo -e "${RED}❌ Failed to start Jarvis service${NC}"
    echo -e "${YELLOW}Check logs: journalctl -u $SERVICE_NAME -f${NC}"
    exit 1
fi