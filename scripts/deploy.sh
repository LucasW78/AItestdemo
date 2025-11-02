#!/bin/bash

# AItestdemo deployment script
set -e

echo "🚀 Deploying AItestdemo..."

# Configuration
ENVIRONMENT=${1:-production}
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "📦 Environment: $ENVIRONMENT"
echo "⏰ Timestamp: $TIMESTAMP"

# Create backup directory
mkdir -p $BACKUP_DIR

# Function to backup data
backup_data() {
    echo "💾 Backing up data..."

    # Backup database
    if docker-compose ps db | grep -q "Up"; then
        docker-compose exec db pg_dump -U postgres aitestdemo > "$BACKUP_DIR/db_backup_$TIMESTAMP.sql"
        echo "✅ Database backed up"
    fi

    # Backup ChromaDB
    if [ -d "./data/chroma_db" ]; then
        tar -czf "$BACKUP_DIR/chroma_backup_$TIMESTAMP.tar.gz" -C ./data chroma_db
        echo "✅ ChromaDB backed up"
    fi

    # Backup documents
    if [ -d "./data/documents" ]; then
        tar -czf "$BACKUP_DIR/documents_backup_$TIMESTAMP.tar.gz" -C ./data documents
        echo "✅ Documents backed up"
    fi
}

# Function to deploy
deploy() {
    echo "🔧 Starting deployment..."

    # Pull latest changes (if in git repository)
    if [ -d ".git" ]; then
        echo "📥 Pulling latest changes..."
        git pull origin main
    fi

    # Build and start services
    echo "🏗️  Building and starting services..."
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d

    # Wait for services to be healthy
    echo "⏳ Waiting for services to be healthy..."
    sleep 30

    # Check health status
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is healthy"
    else
        echo "❌ Backend is not healthy"
        exit 1
    fi

    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend is healthy"
    else
        echo "❌ Frontend is not healthy"
        exit 1
    fi

    echo "✅ Deployment completed successfully!"
}

# Function to rollback
rollback() {
    local ROLLBACK_TIMESTAMP=$1

    if [ -z "$ROLLBACK_TIMESTAMP" ]; then
        echo "❌ Please provide a timestamp to rollback to"
        echo "Usage: $0 rollback <timestamp>"
        exit 1
    fi

    echo "🔄 Rolling back to $ROLLBACK_TIMESTAMP..."

    # Stop services
    docker-compose down

    # Restore database
    if [ -f "$BACKUP_DIR/db_backup_$ROLLBACK_TIMESTAMP.sql" ]; then
        docker-compose up -d db
        sleep 10
        docker-compose exec -T db psql -U postgres -d aitestdemo < "$BACKUP_DIR/db_backup_$ROLLBACK_TIMESTAMP.sql"
        echo "✅ Database restored"
    fi

    # Restore ChromaDB
    if [ -f "$BACKUP_DIR/chroma_backup_$ROLLBACK_TIMESTAMP.tar.gz" ]; then
        rm -rf ./data/chroma_db
        tar -xzf "$BACKUP_DIR/chroma_backup_$ROLLBACK_TIMESTAMP.tar.gz" -C ./data
        echo "✅ ChromaDB restored"
    fi

    # Restore documents
    if [ -f "$BACKUP_DIR/documents_backup_$ROLLBACK_TIMESTAMP.tar.gz" ]; then
        rm -rf ./data/documents
        tar -xzf "$BACKUP_DIR/documents_backup_$ROLLBACK_TIMESTAMP.tar.gz" -C ./data
        echo "✅ Documents restored"
    fi

    # Start all services
    docker-compose up -d

    echo "✅ Rollback completed!"
}

# Function to cleanup old backups
cleanup_backups() {
    echo "🧹 Cleaning up old backups..."

    # Keep only last 7 days of backups
    find $BACKUP_DIR -name "*backup_*.sql" -mtime +7 -delete
    find $BACKUP_DIR -name "*backup_*.tar.gz" -mtime +7 -delete

    echo "✅ Old backups cleaned up"
}

# Main execution
case $2 in
    "deploy")
        backup_data
        deploy
        ;;
    "rollback")
        rollback $3
        ;;
    "backup")
        backup_data
        ;;
    "cleanup")
        cleanup_backups
        ;;
    *)
        echo "❌ Unknown command: $2"
        echo "Usage: $0 [environment] [command] [options]"
        echo "Commands: deploy, rollback <timestamp>, backup, cleanup"
        exit 1
        ;;
esac

echo "🎉 Deployment operations completed!"