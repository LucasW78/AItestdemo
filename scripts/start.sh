#!/bin/bash

# AItestdemo startup script
set -e

echo "🚀 Starting AItestdemo..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "✅ Created .env file. Please edit it with your configuration."
fi

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Parse command line arguments
ENVIRONMENT=${1:-production}
COMMAND=${2:-up}

echo "📦 Environment: $ENVIRONMENT"
echo "🔧 Command: $COMMAND"

# Select docker-compose file based on environment
if [ "$ENVIRONMENT" = "dev" ] || [ "$ENVIRONMENT" = "development" ]; then
    COMPOSE_FILE="docker-compose.dev.yml"
    ENV_SUFFIX="_dev"
else
    COMPOSE_FILE="docker-compose.yml"
    ENV_SUFFIX=""
fi

echo "📄 Using docker-compose file: $COMPOSE_FILE"

# Create necessary directories
mkdir -p data/documents data/chroma_db data/temp

# Run docker-compose commands
case $COMMAND in
    "up")
        echo "🔨 Building and starting containers..."
        docker-compose -f $COMPOSE_FILE up --build -d
        echo "✅ Containers started successfully!"
        echo "🌐 Frontend: http://localhost:3000"
        echo "🔧 Backend API: http://localhost:8000"
        echo "📊 API Docs: http://localhost:8000/docs"
        echo "🗄️  Database: localhost:5432"
        echo "🔍 ChromaDB: http://localhost:8001"
        echo "💾 MinIO: http://localhost:9001"
        ;;
    "down")
        echo "🛑 Stopping containers..."
        docker-compose -f $COMPOSE_FILE down
        echo "✅ Containers stopped!"
        ;;
    "logs")
        echo "📋 Showing logs..."
        docker-compose -f $COMPOSE_FILE logs -f
        ;;
    "shell")
        echo "🐚 Opening backend shell..."
        docker-compose -f $COMPOSE_FILE exec backend bash
        ;;
    "db")
        echo "🗄️  Opening database shell..."
        docker-compose -f $COMPOSE_FILE exec db psql -U postgres -d aitestdemo
        ;;
    "clean")
        echo "🧹 Cleaning up..."
        docker-compose -f $COMPOSE_FILE down -v
        docker system prune -f
        echo "✅ Cleanup completed!"
        ;;
    "reset")
        echo "🔄 Resetting environment..."
        docker-compose -f $COMPOSE_FILE down -v
        docker volume prune -f
        echo "✅ Environment reset completed!"
        echo "💡 Run './scripts/start.sh $ENVIRONMENT up' to start fresh"
        ;;
    *)
        echo "❌ Unknown command: $COMMAND"
        echo "Usage: $0 [environment] [command]"
        echo "Environments: dev, development, prod, production"
        echo "Commands: up, down, logs, shell, db, clean, reset"
        exit 1
        ;;
esac

echo "🎉 Done!"