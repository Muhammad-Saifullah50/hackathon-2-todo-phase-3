# TodoMore Local Dev Helm Chart

This chart lives in `charts/todomore-dev` and deploys the frontend, backend, and MCP services for local Kubernetes development (KIND, minikube, or AKS dev namespace).

## Components
- Backend/FastAPI deployment & service (port 9000)
- Frontend/Next.js deployment & service (port 3000)
- MCP server deployment & service (port 8000)
- Shared ConfigMap for common env vars
- Optional service account
- Single ingress host (`todomore.local`) routing `/`, `/api`, `/mcp`

Container images default to `todomore-<component>:dev-latest`; override via `values.yaml` or `--set` flags.

## Prerequisites
- Kubernetes cluster with nginx Ingress (or an ingress controller compatible with `ingress.class: nginx`)
- Host DNS entry pointing `todomore.local` to the ingress controller IP (e.g., add to `/etc/hosts`)
- Postgres reachable from the cluster; default uses `host.docker.internal` with `postgres/postgres`

## Installation
```bash
# from repo root
helm upgrade --install todomore-dev charts/todomore-dev \
  --namespace todomore-dev --create-namespace
```

Optional overrides:
```bash
helm upgrade --install todomore-dev charts/todomore-dev \
  --namespace todomore-dev --create-namespace \
  --values charts/todomore-dev/values.local.yaml
```

## Troubleshooting
- `kubectl get pods -n todomore-dev` to ensure all deployments are running.
- Tail logs per component: `kubectl logs deploy/todomore-dev-backend -n todomore-dev -f`.
- Verify ingress resolves: `curl -H "Host: todomore.local" http://<ingress-ip>/api/health`.

## Removal
```bash
helm uninstall todomore-dev -n todomore-dev
kubectl delete namespace todomore-dev # optional cleanup
```

Adjust `charts/todomore-dev/values.yaml` as needed for local overrides (alternate DB URL, resource limits, etc.).
