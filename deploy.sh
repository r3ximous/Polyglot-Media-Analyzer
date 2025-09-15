#!/bin/bash

# Production deployment script for Polyglot Media Analyzer

echo "🚀 Deploying Polyglot Media Analyzer to production..."

# Check if we're on the right branch
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" != "main" ]; then
    echo "❌ Please deploy from the main branch. Current branch: $BRANCH"
    exit 1
fi

# Check if there are uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Please commit all changes before deploying."
    exit 1
fi

# Build Docker images
echo "🏗️ Building Docker images..."
docker build -f Dockerfile.backend -t polyglot-media-analyzer/backend:latest .
docker build -f Dockerfile.frontend -t polyglot-media-analyzer/frontend:latest .

# Tag images with version
VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo "v1.0.0")
docker tag polyglot-media-analyzer/backend:latest polyglot-media-analyzer/backend:$VERSION
docker tag polyglot-media-analyzer/frontend:latest polyglot-media-analyzer/frontend:$VERSION

echo "✅ Built images with tag: $VERSION"

# Check deployment type
if [ "$1" == "k8s" ]; then
    echo "☸️ Deploying to Kubernetes..."
    
    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
        echo "❌ kubectl is not installed. Please install kubectl first."
        exit 1
    fi
    
    # Apply Kubernetes configurations
    kubectl apply -f k8s/
    
    # Wait for deployment
    echo "⏳ Waiting for deployment to complete..."
    kubectl rollout status deployment/backend
    kubectl rollout status deployment/frontend
    
    # Get service URLs
    echo "🌐 Service URLs:"
    kubectl get services
    
else
    echo "🐳 Deploying with Docker Compose..."
    
    # Create production docker-compose file if it doesn't exist
    if [ ! -f docker-compose.prod.yml ]; then
        cp docker-compose.yml docker-compose.prod.yml
        echo "📝 Created docker-compose.prod.yml - please customize for production"
    fi
    
    # Deploy with Docker Compose
    docker-compose -f docker-compose.prod.yml down
    docker-compose -f docker-compose.prod.yml up -d
    
    echo "⏳ Waiting for services to start..."
    sleep 30
    
    # Health check
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is healthy"
    else
        echo "❌ Backend health check failed"
    fi
    
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend is accessible"
    else
        echo "❌ Frontend accessibility check failed"
    fi
fi

echo "🎉 Deployment complete!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"