# K8s Deployment Quickstart

## Prerequisites

1. **Minikube running** with ingress addon enabled:
   ```bash
   minikube start
   minikube addons enable ingress
   ```

2. **Docker images** loaded into minikube:
   ```bash
   # Build images (if not already built)
   docker build -t todomore-frontend:latest ./frontend
   docker build -t todomore-backend:latest ./backend
   docker build -t todomore-mcp:latest ./mcp_server

   # Load into minikube
   minikube image load todomore-frontend:latest
   minikube image load todomore-backend:latest
   minikube image load todomore-mcp:latest
   ```

3. **kubectl** configured to access minikube

4. **/etc/hosts** entry mapped to your Minikube IP (ingress traffic is served from the VM, not localhost):
   ```bash
   MINIKUBE_IP=$(minikube ip)
   echo "$MINIKUBE_IP todomore.local" | sudo tee -a /etc/hosts
   ```

## Deploy to Kubernetes

```bash
# Apply all manifests
kubectl apply -f k8s/

# Wait for pods to be ready
kubectl wait --for=condition=Ready pods --all -n todomore --timeout=300s

# Check status
kubectl get all -n todomore
```

## Access the Application

1. **Get ingress IP** (for minikube, this is the minikube IP):
   ```bash
   minikube ip
   ```

2. **Access at**: `http://todomore.local`
   - If it doesn’t load, confirm your `/etc/hosts` entry uses the **Minikube IP** (run `minikube ip` and ensure the same value appears next to `todomore.local`).
   - Make sure your browser isn’t caching a previous DNS entry; open an incognito window or clear DNS cache if necessary.
   - You can also forward the ingress IP temporarily if you prefer: `kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 8080:80` and visit `http://localhost:8080`.

## Verify Deployment

```bash
# Check pods
kubectl get pods -n todomore

# Check services
kubectl get svc -n todomore

# Check ingress
kubectl get ingress -n todomore

# View logs
kubectl logs -n todomore -l app=todomore-frontend
kubectl logs -n todomore -l app=todomore-backend
kubectl logs -n todomore -l app=todomore-mcp
```

## Troubleshooting

### Pods not starting
```bash
kubectl describe pod <pod-name> -n todomore
kubectl logs <pod-name> -n todomore
```

### 503 Service Unavailable
- Check if ingress controller is running: `kubectl get pods -n ingress-nginx`
- Restart ingress controller if needed

### Can't access todomore.local
- Verify `/etc/hosts` entry: `grep todomore.local /etc/hosts`
- Clear browser cache or use incognito

## Clean Up

```bash
# Delete all resources
kubectl delete -f k8s/ --wait=true

# Optionally delete namespace (cascades deletion)
kubectl delete namespace todomore
```

## Configuration

### Updating Secrets

Edit `k8s/02-secret.yaml` with base64-encoded values:

```bash
# Encode a value
echo -n "your-secret-value" | base64

# Decode to verify
echo "YWJjZGVmZ2hpamtsbW5vcA==" | base64 -d
```

### Environment Variables

- Non-sensitive config: Edit `k8s/01-configmap.yaml`
- Sensitive config: Edit `k8s/02-secret.yaml`

After changes:
```bash
kubectl apply -f k8s/
kubectl rollout restart deployment/todomore-frontend -n todomore
kubectl rollout restart deployment/todomore-backend -n todomore
kubectl rollout restart deployment/todomore-mcp -n todomore
```
