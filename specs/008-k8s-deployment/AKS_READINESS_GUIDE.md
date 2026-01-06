# TodoMore AKS Production Readiness Guide

This document captures the production-ready design for deploying TodoMore (frontend, backend, MCP server) onto Azure Kubernetes Service (AKS). It explains required Azure resources, Kubernetes manifests, operational concerns, and validation steps.

## 1. Target Architecture Overview

```
Users ──► Azure Application Gateway / nginx-ingress (TLS)
          └──► Frontend Deployment (Next.js)
                └──► Backend Deployment (FastAPI)
                      └──► External PostgreSQL (Neon or Azure DB)
                └──► MCP Deployment (MCP Server)
All pods ─► Azure Key Vault CSI driver for secrets
Images ───► Azure Container Registry (ACR)
Logs/metrics ─► Azure Monitor + Log Analytics
```

Key principles:
- All sensitive data sourced from Azure Key Vault via CSI driver; no plaintext secrets checked into git.
- Images built and pushed to ACR with immutable tags (e.g., `v1.0.0`).
- Deployments run ≥2 replicas, with HPAs, PDBs, and topology spreading for resilience.
- TLS termination handled by nginx ingress + cert-manager (or Application Gateway) with Let’s Encrypt automation.
- Network policies enforce least-privilege communication between components.

## 2. Required Azure Resources

| Resource | Purpose | Notes |
|----------|---------|-------|
| Resource Group (`todomore-<env>-rg`) | Logical container | One per environment recommended |
| Azure Container Registry (`todomore<env>acr`) | Private image hosting | Attach to AKS for image pulls |
| Azure Key Vault (`todomore-<env>-kv`) | Secret storage | Enable purge protection; store DB URL, API keys, JWT secret |
| AKS Cluster (`todomore-<env>-aks`) | Orchestration platform | Use managed identity, Azure CNI, monitoring add-on |
| Log Analytics Workspace | Centralized logs/metrics | Linked to AKS via Container Insights |
| Optional: Azure Application Gateway (WAF) | L7 ingress | Alternative to nginx-ingress |

### CLI sketch
```bash
az group create --name todomore-prod-rg --location eastus
az acr create --resource-group todomore-prod-rg --name todomoreprodacr --sku Standard
az keyvault create --resource-group todomore-prod-rg --name todomore-prod-kv
az aks create --resource-group todomore-prod-rg --name todomore-prod-aks \
  --node-count 3 --enable-managed-identity --attach-acr todomoreprodacr \
  --enable-addons monitoring --network-plugin azure
```

## 3. Kubernetes Manifests (High-Level)

### Base resources (shared via `k8s/base`)
- `00-namespace.yaml`: namespace stub (overridden per env via overlays).
- `01-configmap.yaml`: minimal defaults (ENVIRONMENT, LOG_LEVEL, CORS origins). Env-specific overrides provided via Kustomize overlays.
- `02-secret.yaml`: placeholder secret; actual sensitive data mounted from Key Vault.
- `04-secretprovider.yaml`: ServiceAccount + AzureIdentity + AzureIdentityBinding + SecretProviderClass referencing Key Vault secrets.
- Workload deployments (`10-backend`, `11-mcp`, `12-frontend`):
  - Use `todomoreprodacr.azurecr.io/...:vX.Y.Z` images with `IfNotPresent` policy.
  - Reference `todomore-app` ServiceAccount and `aadpodidbinding: todomore-workload` label.
  - Mount Key Vault secrets via CSI at `/mnt/secrets-store`.
  - Enforce securityContext (runAsNonRoot, readOnlyRootFilesystem, drop ALL capabilities) and anti-affinity/topology spread.
  - Configure environment variables with production URLs (`https://todomore.example.com`).
  - Include updated probes, resource requests/limits, and replica counts ≥2.
- `20-ingress.yaml`: TLS-enabled ingress with hosts `todomore.example.com`, `api.todomore.example.com`, `mcp.todomore.example.com`; cert-manager annotations and 10 MB body limit.
- `30-hpa.yaml`: HPAs (backend 2–10 pods @70% CPU, etc.).
- `31-pdb.yaml`: minAvailable=1 per deployment.
- `32-network-policies.yaml`: default deny plus whitelisted ingress/egress (allow ingress-nginx, inter-service traffic, DNS, HTTPS).
- `40-cert-issuer.yaml`: Let’s Encrypt staging + prod ClusterIssuers (email `ops@example.com`).

### Overlays (`k8s/overlays/dev` and `k8s/overlays/prod`)
- `dev` overlay:
  - Namespace `todomre-dev`, replicas scaled down (1), dev images (e.g., `:dev-latest`).
  - Ingress host bound to dev domain or localhost; staging ClusterIssuer.
  - ConfigMap overrides for `ENVIRONMENT=development`, `LOG_LEVEL=DEBUG`, CORS pointing to dev frontend.
- `prod` overlay:
  - Namespace `todomre-prod`, replicas per production sizing (backend=3, frontend=2, mcp=2).
  - ConfigMap overrides for production CORS and environment.
  - References prod ClusterIssuer and real domain names.
  - Optionally includes additional resources (HPAs, PDBs, network policies) if you keep them only in prod.

### Directory Layout (recommended)
```
k8s/
  base/
    00-namespace.yaml
    ...
    40-cert-issuer.yaml
    kustomization.yaml
  overlays/
    dev/kustomization.yaml
    prod/kustomization.yaml
  scripts/
    build-and-push.sh
    deploy.sh
    validate.sh
```

## 4. Secret Management Flow
1. Store secrets in Key Vault with names: `database-url`, `openrouter-api-key`, `gemini-api-key`, `better-auth-secret`, `jwt-secret`.
2. Install Secrets Store CSI driver with Azure provider in AKS (`helm repo add csi-secrets-store-provider-azure ...`).
3. Create a user-assigned managed identity (`az identity create ...`) and grant it `get,list` permissions on Key Vault secrets.
4. Deploy `04-secretprovider.yaml` so pods labeled `aadpodidbinding: todomore-workload` automatically receive secrets under `/mnt/secrets-store/`.
5. Optional: enable secret sync to Kubernetes Secrets if other components require standard secrets API.

## 5. CI/CD & Image Strategy
- Build each component’s image with deterministic tag (git SHA or semver). Example script (`k8s/scripts/build-and-push.sh`):
```bash
ACR_URL=todomoreprodacr.azurecr.io
VERSION=v1.0.0
az acr login --name todomoreprodacr

docker build -t $ACR_URL/todomore-backend:$VERSION backend/
docker push $ACR_URL/todomore-backend:$VERSION
# Repeat for frontend + MCP
```
- Update deployment manifests (or use `kustomize edit set image ...`) to reference the new tag; consider GitOps (Argo CD/Flux) to automate.

## 6. Deployment Workflow
1. Ensure azure CLI logged in and AKS credentials retrieved:
```bash
az aks get-credentials --resource-group todomore-prod-rg --name todomore-prod-aks
```
2. Validate manifests locally:
```bash
kustomize build k8s/overlays/prod | kubeval -
kubectl apply -k k8s/overlays/prod --dry-run=client
```
3. Deploy:
```bash
kubectl apply -k k8s/overlays/prod
kubectl rollout status deployment/todomore-backend -n todomore-prod
```
4. Verify ingress + TLS once cert-manager provisions certificates (`kubectl describe ingress todomore-ingress -n todomore-prod`).

## 7. Post-Deployment Validation Checklist
- `kubectl get pods -n todomore-prod -o wide` (all pods Running and spread across nodes).
- `kubectl top pods/nodes` (resource utilization within bounds).
- `kubectl get hpa`, ensure metrics reported.
- `kubectl get pdb` and confirm no disruptions beyond policy.
- `kubectl get networkpolicy` and confirm intended rules present.
- `curl -v https://todomore.example.com` (valid TLS, correct responses). Use `curl -H "Host: api.todomore.example.com"` for API subdomain tests.
- Check logs/metrics in Azure Monitor (Log Analytics queries, Container Insights dashboards).
- Confirm secrets accessible: `kubectl exec deploy/todomore-backend -- ls /mnt/secrets-store`.

## 8. Runbooks
- **Image rollback:** `kubectl rollout undo deployment/todomore-backend -n todomore-prod`.
- **Secret rotation:** update value in Key Vault, restart deployment (`kubectl rollout restart deployment/todomore-backend -n todomore-prod`).
- **Scaling event:** modify HPA thresholds or `kubectl scale deployment ...` temporarily.
- **Certificate issues:** inspect `Certificate` and `Order` CRDs (`kubectl describe certificate todomore-tls -n todomore-prod`).

## 9. Monitoring & Alerting
- Enable Container Insights; configure Log Analytics alerts for pod restarts, HPA saturation, ingress 5xx rates.
- Optional: Deploy kube-prometheus-stack for Prometheus/Grafana dashboards (helpful for custom metrics).
- Instrument backend with Azure Monitor OpenTelemetry exporter (FastAPI instrumentation) for traces/metrics.

## 10. Outstanding Decisions
- Final production domain and TLS email (currently using `todomore.example.com` / `ops@example.com` placeholders).
- Choice between nginx-ingress vs Azure Application Gateway (WAF requirements).
- Whether to migrate PostgreSQL from Neon to Azure Database for PostgreSQL (private endpoint, GeoDR, backups).
- CI/CD platform (GitHub Actions, Azure DevOps) to codify build + deploy steps described above.

---

This guide should serve as the blueprint for implementing AKS-ready manifests and operational processes once you’re ready to proceed with full configuration changes.
