#!/bin/bash

# EACP Kubernetes Deployment Script
# Deploys EACP to a Kubernetes cluster

set -e

NAMESPACE="eacp"
CONTEXT="${1:-default}"

echo "🚀 EACP Kubernetes Deployment"
echo "Namespace: $NAMESPACE"
echo "Context: $CONTEXT"

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if context exists
if ! kubectl config get-contexts | grep -q "$CONTEXT"; then
    echo "❌ Context '$CONTEXT' not found. Available contexts:"
    kubectl config get-contexts
    exit 1
fi

# Switch context
kubectl config use-context "$CONTEXT"

# Create namespace
echo "📦 Creating namespace..."
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml

# Update secrets (prompt user)
echo ""
echo "⚠️  Edit your secrets before deployment:"
echo "   kubectl edit secret eacp-secrets -n $NAMESPACE"
echo ""
read -p "Press Enter to continue..."

# Deploy applications
echo "🔧 Deploying applications..."
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/chroma-statefulset.yaml
kubectl apply -f k8s/network-policy.yaml

# Wait for deployment
echo "⏳ Waiting for deployment to be ready..."
kubectl rollout status deployment/eacp-app -n "$NAMESPACE" --timeout=5m

# Get service info
echo ""
echo "✅ Deployment successful!"
echo ""
echo "📊 Service Information:"
kubectl get services -n "$NAMESPACE"

echo ""
echo "🔗 Access points:"
echo "   API: kubectl port-forward svc/eacp-service 8000:8000 -n $NAMESPACE"
echo "   Chroma: kubectl port-forward svc/chroma 8000:8000 -n $NAMESPACE"

echo ""
echo "📝 View logs:"
echo "   kubectl logs -f deployment/eacp-app -n $NAMESPACE"

echo ""
echo "🗑️  To clean up:"
echo "   kubectl delete namespace $NAMESPACE"
