#!/bin/bash
set -e

# Arguments
BRANCH=${1:-dev}
PORT=${2:-8001}
APP_NAME=${3:-alumnx-vector-db-dev}
REPO_DIR="/home/ubuntu/$APP_NAME"

echo "Deploying $APP_NAME (Branch: $BRANCH) on Port: $PORT..."

# Initialize directory if not exists
if [ ! -d "$REPO_DIR" ]; then
    echo "Creating directory $REPO_DIR and cloning repo..."
    git clone https://github.com/alumnx-ai-labs/alumnx-vector-db.git "$REPO_DIR"
fi

# Navigate to repo
cd "$REPO_DIR"

# Pull latest changes
git fetch origin
git checkout "$BRANCH"
git pull origin "$BRANCH"

# Standardize environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Install dependencies (using uv if available, otherwise pip)
if command -v uv > /dev/null; then
    uv sync
else
    ./venv/bin/pip install -r requirements.txt
fi

# Migrate from PM2 to Docker if necessary
if pm2 describe "$APP_NAME" > /dev/null 2>&1; then
    echo "Stopping and deleting PM2 process $APP_NAME for Docker migration..."
    pm2 delete "$APP_NAME"
    pm2 save
fi

# Deploy using Docker Compose
export HOST_PORT="$PORT"
export CONTAINER_NAME="$APP_NAME"

echo "Running Docker Compose up for $APP_NAME on port $HOST_PORT..."
docker compose up -d --build

# Cleanup old images to save space
echo "Cleaning up dangling images..."
docker image prune -f

echo "Deployment of $APP_NAME via Docker completed successfully!"
