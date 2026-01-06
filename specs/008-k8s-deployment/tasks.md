# Tasks: Kubernetes Deployment for TodoMore

**Input**: Design documents from `/specs/008-k8s-deployment/`
**Prerequisites**: plan.md, spec.md

**Tests**: No tests specified - infrastructure feature

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **K8s manifests**: `k8s/` at repository root
- **Documentation**: `specs/008-k8s-deployment/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create k8s directory structure

- [X] T001 Create k8s directory at repository root for Kubernetes manifests

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core configuration that MUST be complete before ANY deployment can work

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Create ConfigMap with non-sensitive environment variables in k8s/01-configmap.yaml (CORS_ORIGINS, LOG_LEVEL, ENVIRONMENT)
- [X] T003 Create Secret with sensitive configuration in k8s/02-secret.yaml (base64 encode: DATABASE_URL, API keys, auth secrets)

**Checkpoint**: Foundation ready - deployment manifests can now be created

---

## Phase 3: User Story 1 - Deploy Application to Local Minikube (Priority: P1) 🎯 MVP

**Goal**: Deploy three services (frontend, backend, MCP) to minikube namespace

**Independent Test**: Run `kubectl apply -f k8s/` and verify all pods are Running with `kubectl get pods -n todomore`

### Implementation for User Story 1

- [X] T005 [P] [US1] Create backend deployment and service in k8s/10-backend-deployment.yaml (image: saifullahmuhammad/todomore-backend:latest, port: 9000, CPU: 500m, Memory: 512Mi)
- [X] T006 [P] [US1] Create MCP server deployment and service in k8s/11-mcp-deployment.yaml (image: saifullahmuhammad/todomore-mcp:latest, port: 8000, CPU: 500m, Memory: 512Mi)
- [X] T007 [P] [US1] Create frontend deployment and service in k8s/12-frontend-deployment.yaml (image: saifullahmuhammad/todomore-frontend:latest, port: 3000, CPU: 500m, Memory: 512Mi)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Access Application via Ingress (Priority: P1)

**Goal**: Configure nginx-ingress to route external traffic to services

**Independent Test**: Add `127.0.0.1 todomore.local` to /etc/hosts and navigate to http://todomore.local

### Implementation for User Story 2

- [X] T008 [US2] Create ingress manifest in k8s/20-ingress.yaml (host: todomore.local, path routing: /api → backend, /mcp → MCP, / → frontend)
- [X] T009 [US2] Add ingress troubleshooting steps to specs/008-k8s-deployment/quickstart.md (503 Service Unavailable, ingress controller check)

**Checkpoint**: At this point, application should be accessible via http://todomore.local

---

## Phase 5: User Story 3 - Services Communicate via Kubernetes DNS (Priority: P1)

**Goal**: Configure environment variables to use K8s DNS names instead of localhost

**Independent Test**: Check pod environment variables with `kubectl exec -n todomore <pod> -- env | grep todomore`

### Implementation for User Story 3

- [X] T010 [US3] Update backend deployment to reference todomore-frontend:3000 and todomore-mcp:8000 in k8s/10-backend-deployment.yaml (CORS_ORIGINS, FRONTEND_URL, MCP_SERVER_URL)
- [X] T011 [US3] Update frontend deployment to reference todomore-backend:9000 in k8s/12-frontend-deployment.yaml (NEXT_PUBLIC_API_URL, NEXT_PUBLIC_BETTER_AUTH_URL)

**Checkpoint**: At this point, services communicate via K8s DNS and inter-service calls work

---

## Phase 6: User Story 4 - Configuration Managed via ConfigMaps and Secrets (Priority: P2)

**Goal**: Ensure sensitive data is in Secrets, non-sensitive in ConfigMaps

**Independent Test**: Run `kubectl get pods -n todomore -o yaml | grep secret` and verify secrets are not in plaintext

### Implementation for User Story 4

- [X] T012 [US4] Update backend deployment to use envFrom from todomore-config and todomore-secret in k8s/10-backend-deployment.yaml
- [X] T013 [US4] Update frontend deployment to use envFrom from todomore-config and todomore-secret in k8s/12-frontend-deployment.yaml

**Checkpoint**: At this point, configuration is properly separated between ConfigMaps and Secrets

---

## Phase 7: User Story 5 - Zero Downtime Updates (Priority: P3)

**Goal**: Configure rolling updates and health probes

**Independent Test**: Update image tag and verify pods are replaced gradually without extended downtime

### Implementation for User Story 5

- [X] T014 [US5] Configure liveness and readiness probes in k8s/10-backend-deployment.yaml (HTTP /health endpoint, initialDelaySeconds: 30, periodSeconds: 10)
- [X] T015 [US5] Configure liveness and readiness probes in k8s/11-mcp-deployment.yaml (HTTP /health endpoint, initialDelaySeconds: 30, periodSeconds: 10)
- [X] T016 [US5] Configure liveness and readiness probes in k8s/12-frontend-deployment.yaml (HTTP /health endpoint, initialDelaySeconds: 30, periodSeconds: 10)
- [X] T017 [US5] Configure startup probe with extended timeout in k8s/10-backend-deployment.yaml (HTTP /health, failureThreshold: 30, periodSeconds: 10 - 5 min total timeout)
- [X] T018 [US5] Configure rolling update strategy in all deployments (strategy: RollingUpdate, maxSurge: 1, maxUnavailable: 0)
- [X] T019 [US5] Set restartPolicy: Always on all deployments in k8s/10-backend-deployment.yaml, k8s/11-mcp-deployment.yaml, k8s/12-frontend-deployment.yaml

**Checkpoint**: At this point, all user stories should be independently functional with proper health checks and rolling updates

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and documentation

- [X] T020 [P] Add image pull policy: Always to all deployments in k8s/10-backend-deployment.yaml, k8s/11-mcp-deployment.yaml, k8s/12-frontend-deployment.yaml
- [X] T021 [P] Add labels (app: todomore-frontend/backend/mcp) to all deployments and services for proper pod selection
- [X] T022 Update quickstart.md with complete deployment steps including /etc/hosts entry
- [X] T023 Add troubleshooting section for common issues (pod startup failures, connectivity issues)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (T001) - BLOCKS all user stories
- **User Stories (Phase 3-7)**:
  - US1 (Phase 3) depends on Foundational (T002, T003)
  - US2 (Phase 4) depends on US1 deployments (T005, T006, T007)
  - US3 (Phase 5) depends on US1 deployments (modifies existing files)
  - US4 (Phase 6) depends on US1 deployments and Foundational (modifies existing files)
  - US5 (Phase 7) depends on US1 deployments (modifies existing files)
- **Polish (Phase 8)**: Depends on all user story deployments being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Depends on US1 (needs backend/ frontend services)
- **User Story 3 (P1)**: Depends on US1 (modifies deployment env vars)
- **User Story 4 (P2)**: Depends on US1 + Foundational (config already created, needs deployments)
- **User Story 5 (P3)**: Depends on US1 (adds probes and rolling update to deployments)

### Within Each User Story

- US1: Namespace (T004) → Deployments + Services (T005, T006, T007 in parallel)
- US2: Ingress manifest (T008) → Documentation (T009)
- US3: Backend env vars (T010) → Frontend env vars (T011)
- US4: Backend config (T012) → Frontend config (T013)
- US5: Probes (T014, T015, T016) → Startup probe (T017) → Rolling updates (T018) → Restart policy (T019)

### Parallel Opportunities

- T005, T006, T007 (US1 deployments) can run in parallel
- T010, T011 (US3 env vars) can run in parallel
- T012, T013 (US4 config) can run in parallel
- T014, T015, T016 (US5 probes) can run in parallel
- T020, T021 (Polish tasks) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all three deployments together (after namespace is created):
Task: "Create backend deployment and service in k8s/10-backend-deployment.yaml"
Task: "Create MCP server deployment and service in k8s/11-mcp-deployment.yaml"
Task: "Create frontend deployment and service in k8s/12-frontend-deployment.yaml"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational (T002, T003) - CRITICAL
3. Complete Phase 3: User Story 1 (T004, T005, T006, T007)
4. **STOP and VALIDATE**: Run `kubectl apply -f k8s/` and verify pods are Running
5. Test: `kubectl get pods -n todomore` shows all pods in Running state

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Validate pods running
3. Add User Story 2 → Test independently → Access via http://todomore.local
4. Add User Story 3 → Test independently → Verify K8s DNS communication
5. Add User Story 4 → Test independently → Verify ConfigMaps/Secrets working
6. Add User Story 5 → Test independently → Verify rolling updates and health checks

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Infrastructure manifests use existing Docker Hub images
- Environment values are base64 encoded in secrets, plaintext in configmaps
- All services use pullPolicy: Always (Docker Hub images)
- Resource limits: CPU 500m, Memory 512Mi per pod
- Health checks use /health endpoint (from existing Dockerfiles)
