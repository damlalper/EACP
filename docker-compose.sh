#!/bin/bash

# Docker Compose orchestration script
# Manages EACP services locally with docker-compose

set -e

COMMAND="${1:-up}"

case "$COMMAND" in
  up)
    echo "🚀 Starting EACP services..."
    docker-compose up -d
    echo "✅ Services started"
    echo ""
    echo "🔗 Access points:"
    echo "   API: http://localhost:8000"
    echo "   Chroma: http://localhost:8001"
    echo "   Ollama: http://localhost:11434"
    echo "   Redis: localhost:6379"
    echo "   Prometheus: http://localhost:9090"
    echo "   Grafana: http://localhost:3000 (admin/admin)"
    ;;
  down)
    echo "⛔ Stopping EACP services..."
    docker-compose down
    echo "✅ Services stopped"
    ;;
  logs)
    docker-compose logs -f "${2:-eacp-app}"
    ;;
  ps)
    echo "📊 Running services:"
    docker-compose ps
    ;;
  build)
    echo "🔨 Building images..."
    docker-compose build
    echo "✅ Build complete"
    ;;
  pull)
    echo "📥 Pulling latest images..."
    docker-compose pull
    echo "✅ Pull complete"
    ;;
  restart)
    echo "🔄 Restarting services..."
    docker-compose restart "${2:-}"
    echo "✅ Restart complete"
    ;;
  clean)
    echo "🗑️  Removing volumes and containers..."
    docker-compose down -v
    echo "✅ Cleanup complete"
    ;;
  *)
    echo "Usage: $0 {up|down|logs|ps|build|pull|restart|clean} [service]"
    echo ""
    echo "Examples:"
    echo "  $0 up              # Start all services"
    echo "  $0 down            # Stop all services"
    echo "  $0 logs eacp-app   # View app logs"
    echo "  $0 restart redis   # Restart specific service"
    exit 1
    ;;
esac
