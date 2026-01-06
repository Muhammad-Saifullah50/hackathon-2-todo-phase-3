# Implementation Plan: Kubernetes Deployment for TodoMore

**Branch**: `008-k8s-deployment` | **Date**: 2026-01-05 | **Spec**: [link](./spec.md)
**Input**: Feature specification from `/specs/008-k8s-deployment/spec.md`

## Summary

Deploy the TodoMore full-stack application (frontend, backend, MCP server) to local minikube cluster with:
- Namespace isolation (`todomore`)
- Kubernetes Secrets for sensitive configuration (API keys, database URLs)
- ConfigMaps for non-sensitive environment variables
- ClusterIP services with proper K8s DNS names
- Ingress controller with path-based routing (`/api/*`, `/mcp/*`, `/*`)
- Liveness and readiness probes for all services

## Technical Context

**Orchestration**: Kubernetes (minikube for local development)
**Container Images**: Docker Hub (pull policy: Always)
  - `saifullahmuhammad/todomore-frontend:latest`
  - `saifullahmuhammad/todomore-backend:latest`
  - `saifullahmuhammad/todomore-mcp:latest`
**Ingress Controller**: nginx-ingress (minikube addon enabled)
**Configuration Storage**: Kubernetes ConfigMaps + Secrets
**Service Discovery**: Kubernetes DNS (`<service-name>.<namespace>.svc.cluster.local`)
**Access Method**: Ingress at `http://todomore.local` (requires `/etc/hosts` entry)

## Constitution Check

*Gate: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| XVII. Deployment & Infrastructure | ✅ PASS | Containerization already complete; K8s manifests needed |
| XV. Web Security | ✅ PASS | K8s Secrets will protect sensitive data |
| VIII. Security & Safety | ✅ PASS | Secrets not exposed in pod specs |
| XVIII. Monitoring & Observability | ✅ PASS | Health check endpoints already exist in Dockerfiles |

**No violations detected.** This feature is infrastructure-only and aligns with existing Docker containers.

## Project Structure

### Documentation (this feature)

```text
specs/008-k8s-deployment/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── k8s/                 # Phase 2 output (/sp.tasks command)
│   ├── 00-namespace.yaml
│   ├── 01-configmap.yaml
│   ├── 02-secret.yaml
│   ├── 10-backend-deployment.yaml
│   ├── 11-mcp-deployment.yaml
│   ├── 12-frontend-deployment.yaml
│   └── 20-ingress.yaml
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

The Kubernetes manifests will be created in a new `k8s/` directory at the repository root.

```text
k8s/                          # NEW - Kubernetes manifests
├── 00-namespace.yaml         # Namespace: todomore
├── 01-configmap.yaml         # Non-sensitive config
├── 02-secret.yaml            # Sensitive config (base64 encoded)
├── 10-backend-deployment.yaml    # Backend + Service
├── 11-mcp-deployment.yaml        # MCP Server + Service
├── 12-frontend-deployment.yaml   # Frontend + Service
└── 20-ingress.yaml          # Ingress with path routing
```

**Structure Decision**: Kubernetes manifests created in `k8s/` directory at repository root for easy deployment with `kubectl apply -f k8s/`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No complexity violations. This is a straightforward infrastructure deployment.

## Phase 0: Research

This infrastructure feature requires no research - standard Kubernetes patterns apply:
- ConfigMaps for non-sensitive config (environment variables)
- Secrets for sensitive data (base64 encoded in manifest, can be encrypted at rest)
- Deployments with replicas=1 for local development
- ClusterIP services for internal communication
- Ingress with nginx controller for external access

## Phase 1: Design

### K8s Resources to Create

| Resource | File | Purpose |
|----------|------|---------|
| Namespace | `00-namespace.yaml` | Isolates `todomore` resources |
| ConfigMap | `01-configmap.yaml` | Non-sensitive env vars (CORS origins, log levels) |
| Secret | `02-secret.yaml` | API keys, database URLs, auth secrets |
| Deployment + Service | `10-backend-deployment.yaml` | Backend API (port 9000) |
| Deployment + Service | `11-mcp-deployment.yaml` | MCP Server (port 8000) |
| Deployment + Service | `12-frontend-deployment.yaml` | Frontend (port 3000) |
| Ingress | `20-ingress.yaml` | Path-based routing |

### Environment Variable Mapping

| Service | Variable | Value |
|---------|----------|-------|
| Frontend | `NEXT_PUBLIC_API_URL` | `http://todomore-backend:9000` |
| Frontend | `NEXT_PUBLIC_BETTER_AUTH_URL` | `http://todomore-frontend:3000` |
| Backend | `CORS_ORIGINS` | `["http://todomore-frontend:3000"]` |
| Backend | `FRONTEND_URL` | `http://todomore-frontend:3000` |
| Backend | `MCP_SERVER_URL` | `http://todomore-mcp:8000/mcp/` |
| MCP | (no special config) | Uses default |

### Ingress Configuration

```yaml
rules:
- host: todomore.local
  http:
    paths:
    - path: /api
      pathType: Prefix
      backend:
        service:
          name: todomore-backend
          port: 9000
    - path: /mcp
      pathType: Prefix
      backend:
        service:
          name: todomore-mcp
          port: 8000
    - path: /
      pathType: Prefix
      backend:
        service:
          name: todomore-frontend
          port: 3000
```

## Phase 2: Implementation Tasks

Tasks will be generated by `/sp.tasks` command.
