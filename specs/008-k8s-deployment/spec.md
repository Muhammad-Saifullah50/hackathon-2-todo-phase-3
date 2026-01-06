# Feature Specification: Kubernetes Deployment for TodoMore Application

**Feature Branch**: `008-k8s-deployment`
**Created**: 2026-01-05
**Status**: Draft
**Input**: "Deploy the TodoMore application to Kubernetes for local development with minikube"

## User Scenarios & Testing

### User Story 1 - Deploy Application to Local Minikube (Priority: P1)

As a developer, I want to deploy the TodoMore application to my local minikube cluster so that I can test the full application stack in a Kubernetes environment before production deployment.

**Why this priority**: This is the foundational requirement for all local Kubernetes testing. Without a working deployment, no other K8s-related testing is possible.

**Independent Test**: Can be tested by running `kubectl apply -f k8s/` and verifying all pods are running with `kubectl get pods`.

**Acceptance Scenarios**:

1. **Given** minikube is running and ingress addon is enabled, **When** I apply the K8s manifests, **Then** all three services (frontend, backend, MCP) should be deployed successfully.

2. **Given** the deployment is applied, **When** I run `kubectl get pods`, **Then** I should see all pods in Running state.

3. **Given** the services are deployed, **When** I run `kubectl get svc`, **Then** I should see ClusterIP services for all three services.

---

### User Story 2 - Access Application via Ingress (Priority: P1)

As a developer, I want to access the TodoMore application through a single URL so that I can test the full application flow including authentication and API calls.

**Why this priority**: The ingress is the primary entry point for the application. Without it, users cannot access the application externally.

**Independent Test**: Can be tested by adding `127.0.0.1 todomore.local` to `/etc/hosts` and navigating to `http://todomore.local`.

**Acceptance Scenarios**:

1. **Given** the Ingress is configured, **When** I access `http://todomore.local`, **Then** the frontend should be served.

2. **Given** the Ingress is configured, **When** I access `http://todomore.local/api/...`, **Then** requests should be routed to the backend service.

3. **Given** the Ingress is configured, **When** I access `http://todomore.local/mcp/...`, **Then** requests should be routed to the MCP server.

---

### User Story 3 - Services Communicate via Kubernetes DNS (Priority: P1)

As a developer, I want services to communicate with each other using Kubernetes DNS names instead of localhost so that the application works correctly in a distributed environment.

**Why this priority**: The current configuration uses localhost which only works on a single machine. K8s requires service DNS for inter-service communication.

**Independent Test**: Can be tested by verifying environment variables are correctly set and API calls succeed between services.

**Acceptance Scenarios**:

1. **Given** the frontend is deployed, **When** it makes API calls, **Then** it should use `http://todomore-backend:9000` (not localhost).

2. **Given** the backend is deployed, **When** it needs to call the MCP server, **Then** it should use `http://todomore-mcp:8000`.

3. **Given** Better Auth is configured, **When** users authenticate, **Then** cookies should be set for the correct domain.

---

### User Story 4 - Configuration Managed via ConfigMaps and Secrets (Priority: P2)

As a developer, I want sensitive configuration (API keys, database URLs) stored in Kubernetes Secrets and non-sensitive config in ConfigMaps so that I can manage application configuration securely and easily.

**Why this priority**: Security best practice for managing sensitive data in Kubernetes. Enables rotation of credentials without rebuilding images.

**Independent Test**: Can be tested by verifying pods start with correct environment variables from ConfigMaps/Secrets.

**Acceptance Scenarios**:

1. **Given** K8s ConfigMaps and Secrets are created, **When** pods start, **Then** they should have the correct environment variables.

2. **Given** secrets are stored in K8s, **When** I run `kubectl get pods -o yaml`, **Then** I should NOT see secret values in plaintext.

---

### User Story 5 - Zero Downtime Updates (Priority: P3)

As a developer, I want to update the application without downtime so that I can iterate quickly during development without interrupting testing.

**Why this priority**: Nice-to-have for local development. More important for production but not critical for minikube testing.

**Independent Test**: Can be tested by updating an image tag and verifying pods are replaced without extended downtime.

**Acceptance Scenarios**:

1. **Given** the application is deployed, **When** I update a deployment image, **Then** rolling updates should replace pods gradually.

2. **Given** a pod is being replaced, **When** I check availability, **Then** the application should remain accessible throughout the update.

---

### Edge Cases

- What happens when a service fails to start due to missing configuration?
- How does the system handle when the database (Neon) is unreachable?
- How are liveness and readiness probes configured to detect failures?
- What happens when the Ingress controller is not running?

---

## Requirements

### Functional Requirements

- **FR-001**: System MUST deploy three services (frontend, backend, MCP server) to Kubernetes namespace `todomore`.
- **FR-002**: System MUST create ClusterIP services for each microservice with correct DNS names.
- **FR-003**: System MUST configure Ingress with path-based routing:
  - `/api/*` → backend service (port 9000)
  - `/mcp/*` → MCP service (port 8000)
  - `/*` → frontend service (port 3000, catch-all)
- **FR-004**: System MUST use Kubernetes ConfigMaps for non-sensitive configuration.
- **FR-005**: System MUST use Kubernetes Secrets for API keys, database URLs, and authentication secrets.
- **FR-006**: System MUST configure environment variables for inter-service communication using K8s DNS names:
  - `NEXT_PUBLIC_API_URL` → `http://todomore-backend:9000`
  - `NEXT_PUBLIC_BETTER_AUTH_URL` → `http://todomore-frontend:3000`
  - `CORS_ORIGINS` → `["http://todomore-frontend:3000"]`
  - `MCP_SERVER_URL` → `http://todomore-mcp:8000/mcp/`
- **FR-007**: System MUST configure liveness and readiness probes for all services.
- **FR-008**: System MUST require `/etc/hosts` entry `127.0.0.1 todomore.local` for local testing.
- **FR-009**: System MUST provide a single `kubectl apply` command to deploy all resources.
- **FR-010**: System MUST support accessing the application at `http://todomore.local`.
- **FR-011**: System MUST set CPU limits of 500m and memory limits of 512Mi for each pod.
- **FR-012**: System MUST use restartPolicy: Always to ensure containers restart on failure.
- **FR-013**: System MUST configure startup probes with extended timeouts to handle database connection delays.
- **FR-014**: System MUST document ingress controller failure troubleshooting in quickstart guide.

### Key Entities

- **Namespace**: `todomore` - Isolates all application resources.
- **ConfigMap**: `todomore-config` - Stores non-sensitive environment variables.
- **Secret**: `todomore-secret` - Stores API keys, database URLs, and auth secrets.
- **Deployment (3x)**: `todomore-frontend`, `todomore-backend`, `todomore-mcp` - Manages pod replicas.
- **Service (3x)**: `todomore-frontend`, `todomore-backend`, `todomore-mcp` - Provides stable network endpoints.
- **Ingress**: `todomore-ingress` - Routes external traffic to appropriate services.

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: All pods reach Running state within 5 minutes of applying manifests.
- **SC-002**: Frontend is accessible at `http://todomore.local` within 30 seconds of accessing the URL.
- **SC-003**: API calls from frontend to backend succeed with 200/201 status codes (no connection refused or DNS errors).
- **SC-004**: All inter-service communication (backend → MCP) functions correctly without localhost references.
- **SC-005**: Authentication flow works correctly with Better Auth cookies being set for the correct domain.
- **SC-006**: Secret values are not exposed in pod specifications or logs.

---

## Assumptions

- Docker images are already built and available in a registry accessible by minikube (or will be loaded via `minikube image load`).
- Minikube is already running with the ingress addon enabled.
- User has kubectl configured to access the minikube cluster.
- Neon PostgreSQL database is accessible from within the cluster (cloud-hosted, not local).
- The existing Dockerfiles (frontend, backend, mcp_server) are production-ready and require no modifications.

## Clarifications

### Session 2026-01-05

- Q: Should we specify CPU and memory limits for the pods? → A: Set reasonable defaults (CPU: 500m, Memory: 512Mi) for each service
- Q: How should we handle service failures and restart policies? → A: Use restartPolicy: Always to ensure containers restart on failure
- Q: What should happen if the Neon PostgreSQL database is unreachable? → A: Configure startup probes with extended timeouts to handle database connection delays
- Q: What should happen if the nginx-ingress controller is not running? → A: Document ingress controller failure troubleshooting in quickstart guide
