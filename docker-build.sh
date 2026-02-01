#!/bin/bash

# Docker build and push script for EACP
# Usage: ./docker-build.sh [image_name] [image_tag] [registry]

set -e

IMAGE_NAME="${1:-eacp}"
IMAGE_TAG="${2:-latest}"
REGISTRY="${3:-}"

FULL_IMAGE="${REGISTRY:+$REGISTRY/}${IMAGE_NAME}:${IMAGE_TAG}"

echo "🐳 Building Docker image"
echo "Image: $FULL_IMAGE"
echo ""

# Check if Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    echo "❌ Dockerfile not found in current directory"
    exit 1
fi

# Build image
echo "🔨 Building..."
docker build \
    --tag "$FULL_IMAGE" \
    --label "version=$IMAGE_TAG" \
    --label "description=Enterprise Agent Collaboration Platform" \
    .

echo "✅ Build complete: $FULL_IMAGE"

# Ask to push
read -p "Push to registry? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -z "$REGISTRY" ]; then
        echo "❌ No registry specified. Use: ./docker-build.sh eacp latest myregistry.azurecr.io"
        exit 1
    fi
    
    echo "🚀 Pushing to $REGISTRY..."
    docker push "$FULL_IMAGE"
    echo "✅ Push complete"
fi

echo ""
echo "📝 To run locally:"
echo "   docker run -p 8000:8000 $FULL_IMAGE"
echo ""
echo "📝 To run with docker-compose:"
echo "   docker-compose up"
