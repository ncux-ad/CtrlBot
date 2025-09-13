#!/bin/bash

# CtrlBot Docker Deployment Script
# This script deploys CtrlBot using Docker Compose

set -e

echo "🐳 Deploying CtrlBot with Docker..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Please create .env file with required configuration:"
    echo "  cp env.example .env"
    echo "  # Edit .env with your settings"
    exit 1
fi

echo -e "${YELLOW}Step 1: Loading environment variables...${NC}"
source .env

# Validate required variables
required_vars=("BOT_TOKEN" "ADMIN_IDS" "DB_PASSWORD")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}Error: $var is not set in .env file${NC}"
        exit 1
    fi
done

echo -e "${YELLOW}Step 2: Creating necessary directories...${NC}"
mkdir -p logs data

echo -e "${YELLOW}Step 3: Building Docker images...${NC}"
docker-compose build

echo -e "${YELLOW}Step 4: Starting services...${NC}"
docker-compose up -d

echo -e "${YELLOW}Step 5: Waiting for services to be ready...${NC}"
sleep 10

echo -e "${YELLOW}Step 6: Checking service status...${NC}"
docker-compose ps

echo -e "${GREEN}Deployment completed!${NC}"
echo ""
echo "Services:"
echo "  - CtrlBot: Running in container 'ctrlbot'"
echo "  - PostgreSQL: Running in container 'ctrlbot_postgres'"
echo "  - pgAdmin: Available at http://localhost:8080 (if enabled)"
echo ""
echo "Management commands:"
echo "  docker-compose logs -f ctrlbot     # View bot logs"
echo "  docker-compose restart ctrlbot     # Restart bot"
echo "  docker-compose stop                # Stop all services"
echo "  docker-compose down                # Stop and remove containers"
echo ""
echo "Database access:"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: ${DB_NAME:-ctrlbot_db}"
echo "  User: ${DB_USER:-ctrlbot}"
echo "  Password: [from .env file]"
