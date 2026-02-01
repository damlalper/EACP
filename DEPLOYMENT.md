# EACP Deployment Guide

## Quick Start with Docker Compose

### Prerequisites
- Docker and Docker Compose installed
- 4GB+ free disk space
- 2GB+ RAM available

### Start Services

```bash
# Make scripts executable
chmod +x docker-compose.sh
chmod +x docker-build.sh

# Start all services
./docker-compose.sh up

# Check service status
./docker-compose.sh ps
```

### Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| EACP API | http://localhost:8000 | - |
| Chroma Vector DB | http://localhost:8001 | - |
| Ollama LLM | http://localhost:11434 | - |
| Redis Cache | localhost:6379 | - |
| Prometheus Metrics | http://localhost:9090 | - |
| Grafana Dashboard | http://localhost:3000 | admin/admin |

### View Logs

```bash
# View all services
docker-compose logs -f

# View specific service
./docker-compose.sh logs eacp-app
./docker-compose.sh logs chroma
./docker-compose.sh logs ollama
```

### Stop Services

```bash
./docker-compose.sh down
```

### Clean Up

```bash
# Remove all containers and volumes
./docker-compose.sh clean
```

---

## Kubernetes Deployment

### Prerequisites
- kubectl configured and connected to cluster
- Kubernetes 1.20+
- Container registry access (Docker Hub, ACR, GCR, etc.)

### Build and Push Image

```bash
# Build image
./docker-build.sh eacp latest myregistry.azurecr.io

# Or use docker directly
docker build -t myregistry.azurecr.io/eacp:latest .
docker push myregistry.azurecr.io/eacp:latest
```

### Deploy to Kubernetes

```bash
# Make deploy script executable
chmod +x k8s/deploy.sh

# Deploy to default context
./k8s/deploy.sh

# Or specify context
./k8s/deploy.sh my-cluster-context
```

### Configure Secrets

```bash
# Edit secrets (update with your API keys)
kubectl edit secret eacp-secrets -n eacp

# Or apply secrets from file
kubectl apply -f k8s/secrets.yaml

# Then edit
kubectl edit secret eacp-secrets -n eacp
```

### Verify Deployment

```bash
# Check deployment status
kubectl get deployment -n eacp
kubectl get pods -n eacp
kubectl get svc -n eacp

# View logs
kubectl logs -f deployment/eacp-app -n eacp

# Port forward to access locally
kubectl port-forward svc/eacp-service 8000:8000 -n eacp
```

### Scale Deployment

```bash
# Manual scaling
kubectl scale deployment eacp-app --replicas=5 -n eacp

# Automatic scaling (already configured)
kubectl get hpa -n eacp
```

### Monitor with Prometheus & Grafana

```bash
# Port forward Prometheus
kubectl port-forward svc/prometheus 9090:9090 -n monitoring

# Port forward Grafana
kubectl port-forward svc/grafana 3000:3000 -n monitoring

# Access at http://localhost:3000 (admin/admin)
```

### Clean Up

```bash
# Delete namespace and all resources
kubectl delete namespace eacp
```

---

## GitHub Actions CI/CD

The `.github/workflows/ci-cd.yml` workflow automatically:

1. **Lint & Format Check** - Black, isort, flake8
2. **Unit Tests** - pytest with coverage
3. **Build Docker Image** - Multi-stage build to registry
4. **Security Scan** - Trivy and GitGuardian
5. **Deploy to K8s** - Automatic deployment on main branch push

### Setup

1. Add secrets to GitHub repository:
   - `KUBE_CONFIG`: Base64-encoded kubeconfig
   - `GITGUARDIAN_API_KEY`: GitGuardian API key (optional)

2. Enable GitHub Container Registry:
   - Go to Settings → Actions → General
   - Enable "Allow GitHub Actions to create and approve pull requests"

3. Configure Kubernetes access:
   - Update kubeconfig in workflow or use KUBE_CONFIG secret

### Run Workflow Manually

```bash
# Trigger workflow via GitHub CLI
gh workflow run ci-cd.yml

# Or push to trigger automatically
git push origin main
```

---

## Local Development

### Without Docker

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export EACP_ENV=development

# Run application
python main.py

# Run monitoring example
python examples/monitoring_example.py

# Run fine-tuning example
python examples/fine_tuning_example.py
```

### With Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

---

## Troubleshooting

### Docker Issues

```bash
# Check Docker daemon
docker ps

# Clean up images
docker system prune -a

# Rebuild images
./docker-compose.sh build

# View specific container logs
docker logs container_name
```

### Kubernetes Issues

```bash
# Check cluster status
kubectl cluster-info
kubectl get nodes

# Debug pod
kubectl describe pod pod_name -n eacp
kubectl logs pod_name -n eacp

# Check events
kubectl get events -n eacp --sort-by='.lastTimestamp'

# Check resource availability
kubectl top nodes
kubectl top pods -n eacp
```

### Common Issues

**Port already in use:**
```bash
# Find process using port
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Change port in docker-compose.yml
```

**Out of memory:**
```bash
# Increase Docker memory
Docker Desktop → Preferences → Resources → Memory (set to 4GB+)

# Increase K8s pod limits in k8s/deployment.yaml
```

**Connection refused:**
```bash
# Ensure services are running
docker-compose ps
kubectl get pods -n eacp

# Check service endpoints
kubectl get endpoints -n eacp
```

---

## Production Checklist

- [ ] Update all API keys in k8s/secrets.yaml
- [ ] Configure TLS/SSL certificates
- [ ] Set up proper ingress controller
- [ ] Enable network policies
- [ ] Configure persistent storage
- [ ] Set up monitoring and alerting
- [ ] Enable audit logging
- [ ] Configure RBAC
- [ ] Set resource quotas
- [ ] Enable pod security policies
- [ ] Configure rate limiting
- [ ] Set up backup and disaster recovery
