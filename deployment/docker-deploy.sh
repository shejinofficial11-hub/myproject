#!/bin/bash

# Jarvis AI Assistant - Docker Deployment Script
# This script deploys Jarvis using Docker containers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="jarvis-assistant"
NETWORK_NAME="jarvis-network"
DATA_DIR="$HOME/jarvis-data"
LOGS_DIR="$DATA_DIR/logs"

echo -e "${GREEN}🐳 Starting Jarvis AI Assistant Docker deployment${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Create data directories
echo -e "${YELLOW}Creating data directories...${NC}"
mkdir -p "$DATA_DIR"
mkdir -p "$LOGS_DIR"
mkdir -p "$DATA_DIR/recordings"
mkdir -p "$DATA_DIR/models"
mkdir -p "$DATA_DIR/temp"

# Set permissions
chmod -R 755 "$DATA_DIR"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env file with your API keys before starting${NC}"
fi

# Create docker network if it doesn't exist
echo -e "${YELLOW}Creating Docker network...${NC}"
if ! docker network inspect "$NETWORK_NAME" &> /dev/null; then
    docker network create "$NETWORK_NAME"
fi

# Stop and remove existing container
echo -e "${YELLOW}Removing existing container (if any)...${NC}"
if docker ps -a --format 'table {{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
    docker stop "$CONTAINER_NAME" || true
    docker rm "$CONTAINER_NAME" || true
fi

# Build and start with Docker Compose
echo -e "${YELLOW}Building and starting containers...${NC}"
docker-compose up --build -d

# Wait for container to be ready
echo -e "${YELLOW}Waiting for Jarvis to be ready...${NC}"
for i in {1..30}; do
    if curl -f http://localhost:8000 &> /dev/null; then
        echo -e "${GREEN}✅ Jarvis is ready!${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

if ! curl -f http://localhost:8000 &> /dev/null; then
    echo -e "\n${RED}❌ Jarvis failed to start properly${NC}"
    echo -e "${YELLOW}Check logs: docker logs $CONTAINER_NAME${NC}"
    exit 1
fi

# Show container status
echo -e "${GREEN}Container status:${NC}"
docker ps --filter name="$CONTAINER_NAME"

# Show useful commands
echo -e "\n${GREEN}🚀 Jarvis AI Assistant deployed successfully!${NC}"
echo -e "\n${YELLOW}Useful commands:${NC}"
echo -e "  • View logs: docker logs -f $CONTAINER_NAME"
echo -e "  • Stop: docker-compose down"
echo -e "  • Restart: docker-compose restart"
echo -e "  • View container: docker exec -it $CONTAINER_NAME bash"
echo -e "  • Database backup: docker exec $CONTAINER_NAME python backup_db.py"
echo -e "\n${YELLOW}Access URLs:${NC}"
echo -e "  • Jarvis Interface: http://localhost:8000"
echo -e "  • Health Check: http://localhost:8000/health"
echo -e "\n${YELLOW}Data directories:${NC}"
echo -e "  • Data: $DATA_DIR"
echo -e "  • Logs: $LOGS_DIR"
echo -e "\n${YELLOW}Don't forget to:${NC}"
echo -e "  1. Edit .env file with your API keys"
echo -e "  2. Restart: docker-compose restart"