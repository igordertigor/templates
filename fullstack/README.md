# cookiecutter-fastapi-stack

A opinionated but flexible project template for production-ready web applications. The stack is chosen for developer ergonomics, self-hostability, and long-term maintainability over managed-service convenience.

## Philosophy

Most "backend-as-a-service" tools (Supabase, Firebase, etc.) offer convenience by making choices for you — often choices that conflict with your own preferences or that create hard dependencies on external platforms. This template instead gives you a well-structured starting point with a stack you own entirely, runnable locally via Docker Compose and deployable to any Kubernetes cluster via Flux + Kustomize.

The tradeoff is that you write a little more boilerplate upfront. The payoff is that nothing is magic, everything is inspectable, and you are never locked in.

---

## Stack

| Layer | Choice | Rationale |
|---|---|---|
| API | FastAPI | Async, type-safe, excellent DX |
| ORM | SQLModel | Pydantic + SQLAlchemy, minimal boilerplate |
| Migrations | Alembic | Standard, reliable |
| GraphQL (optional) | Strawberry | Type-safe, integrates with FastAPI cleanly |
| Background tasks (optional) | arq | Async, Redis-backed, fits naturally with FastAPI |
| Auth | Authentik | Self-hostable, OIDC/OAuth2, flexible flows |
| Storage | MinIO | S3-compatible, self-hostable |
| Database | PostgreSQL | |
| Frontend (optional) | React + Vite + React Router v7 + Mantine | Apollo Client (GraphQL) or TanStack Query (REST) |
| JS package manager | pnpm | Faster, stricter than npm |
| Python package manager | uv | Fast, modern, replaces pip + venv + pip-tools |
| Task runner | just | Simple, language-agnostic Makefile replacement |
| GitOps | Flux | Pull-based, K8s-native |
| Infra manifests | Kustomize | No templating language, plain YAML with overlays |
| Local dev | Docker Compose | |

---

## Prerequisites

- [cookiecutter](https://cookiecutter.readthedocs.io/) (`pip install cookiecutter` or `uv tool install cookiecutter`)
- [Docker](https://docs.docker.com/get-docker/) + [Docker Compose](https://docs.docker.com/compose/)
- [just](https://github.com/casey/just)
- [uv](https://github.com/astral-sh/uv)
- [pnpm](https://pnpm.io/) (if using frontend)
- [kubectl](https://kubernetes.io/docs/tasks/tools/) + [flux CLI](https://fluxcd.io/flux/installation/) (for K8s deployment)

---

## Usage

```bash
cookiecutter https://github.com/your-org/cookiecutter-fastapi-stack
```

Or locally:

```bash
cookiecutter path/to/cookiecutter-fastapi-stack
```

### Variables

| Variable | Default | Description |
|---|---|---|
| `project_name` | `my-project` | Human-readable project name |
| `project_slug` | derived | Used for namespaces, image names, directories |
| `project_description` | | Short description |
| `python_version` | `3.12` | Python version for uv + Dockerfile |
| `postgres_version` | `16` | PostgreSQL version |
| `add_frontend` | `y` | Include React + Vite + Mantine frontend |
| `add_strawberry` | `n` | Include Strawberry GraphQL endpoint (uses Apollo Client on frontend; if disabled, uses TanStack Query) |
| `add_arq` | `y` | Include arq worker + Redis |
| `shared_db` | `n` | Authentik shares app Postgres instance (separate DB) vs own instance |
| `use_stage_namespace` | `y` | Add stage overlay + Flux Kustomization alongside prod |
| `auth_user_pkce` | `y` | PKCE flow for browser-based user login |
| `auth_device_flow` | `n` | Device flow for CLI tools / browserless devices |
| `auth_client_credentials` | `n` | Client credentials for machine-to-machine auth |

---

## Project structure (after generation)

```
my-project/
├── justfile                  # all common tasks in one place
├── docker-compose.yml        # full local stack
├── docker-compose.override.yml  # local dev overrides (hot reload etc.)
├── .env.example              # copy to .env and fill in
├── backend/
│   ├── pyproject.toml        # uv-managed dependencies
│   ├── app/
│   │   ├── main.py           # FastAPI app factory
│   │   ├── settings.py       # pydantic-settings, reads from env
│   │   ├── db.py             # engine, get_session dependency
│   │   ├── tables.py         # ALL SQLModel table definitions (one file)
│   │   ├── crud/
│   │   │   ├── base.py       # generic CRUD[T] base class
│   │   │   └── users.py      # domain-specific overrides
│   │   ├── routers/          # REST endpoints, one file per domain
│   │   │   └── users.py
│   │   ├── graphql/          # Strawberry schema (if enabled)
│   │   │   ├── schema.py
│   │   │   ├── types.py
│   │   │   ├── queries.py
│   │   │   └── mutations.py
│   │   ├── auth/
│   │   │   ├── oidc.py       # JWT validation dependency
│   │   │   └── device.py     # device flow helper (if enabled)
│   │   └── worker/           # arq (if enabled)
│   │       ├── settings.py   # WorkerSettings
│   │       └── tasks.py
│   ├── migrations/
│   │   ├── env.py            # imports tables.py — required for Alembic
│   │   └── versions/
│   └── Dockerfile
├── frontend/                 # (if enabled)
│   ├── src/
│   │   ├── main.tsx
│   │   ├── router.tsx
│   │   ├── apollo.ts         # (if GraphQL enabled)
│   │   ├── query-client.ts   # (if GraphQL disabled - TanStack Query)
│   │   ├── auth/
│   │   │   └── oidc.ts       # oidc-client-ts, Authentik PKCE config
│   │   ├── pages/
│   │   ├── components/
│   │   ├── api/              # (if GraphQL disabled - REST API hooks)
│   │   │   └── users.ts
│   │   └── graphql/          # (if GraphQL enabled)
│   │       ├── queries/
│   │       └── mutations/
│   ├── codegen.ts            # (if GraphQL enabled)
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── package.json
├── k8s/
│   ├── base/                 # generic manifests, no env-specific values
│   │   ├── postgres/
│   │   ├── redis/            # (if arq enabled)
│   │   ├── minio/
│   │   ├── authentik/
│   │   ├── backend/
│   │   ├── worker/           # (if arq enabled)
│   │   └── frontend/         # (if frontend enabled)
│   └── overlays/
│       ├── local/            # for kind or k3d local cluster
│       ├── stage/            # namespace: my-project-stage
│       └── prod/             # namespace: my-project-prod
└── flux/
    └── clusters/
        └── my-cluster/
            ├── apps-prod.yaml
            └── apps-stage.yaml   # (if use_stage_namespace enabled)
```

---

## Local development

```bash
# Copy and fill in environment variables
cp .env.example .env

# Start all backing services
just up

# Run database migrations
just migrate

# Start backend dev server (hot reload)
just dev-backend

# Start frontend dev server (if enabled)
just dev-frontend

# Run both concurrently
just dev
```

---

## Database migrations

This project uses Alembic with SQLModel. A common gotcha: SQLModel does not register table metadata until the model classes are imported. The `migrations/env.py` file explicitly imports `app.tables` to ensure all tables are visible to Alembic before it inspects the metadata.

```bash
# Create a new migration after changing tables.py
just migration "add user roles"

# Apply migrations
just migrate

# Downgrade one step
just migrate-down
```

Always review auto-generated migrations before applying — Alembic's autogenerate is good but not perfect, particularly for indexes and constraints.

---

## Authentication

This template uses [Authentik](https://goauthentik.io/) as the identity provider. Authentik is self-hostable, OIDC-compliant, and supports all common OAuth2 flows. It runs as a separate service alongside your application.

### Flows

**PKCE (browser login)** — Used by the React frontend. The user is redirected to Authentik, authenticates, and is redirected back with a code that is exchanged for a JWT. The JWT is validated by FastAPI on every request.

**Device flow** — Used by CLI tools or devices without a browser. The device displays a short code and a URL; the user visits the URL on any device and approves the login. Useful if you ship a CLI alongside your application.

**Client credentials** — Used for machine-to-machine communication. A service authenticates with a client ID and secret and receives a JWT. No user is involved. Useful for background services, data pipelines, or external integrations.

All flows produce a JWT that FastAPI validates using Authentik's JWKS endpoint. The validation logic is in `app/auth/oidc.py` and exposed as a FastAPI dependency.

### Authentik setup

Authentik configuration is automated via blueprints for local development. The README in the generated project contains step-by-step instructions for the Authentik admin UI, including:

- Creating a project for your application
- Creating a web application (PKCE) for the frontend
- Creating an API application for the backend
- Configuring redirect URIs for stage and prod separately

---

## Kubernetes deployment

### Namespace strategy

Rather than separate clusters for stage and prod (which requires separate hardware), this template uses separate namespaces on the same cluster. This provides meaningful isolation for MVPs and single-node setups while keeping resource usage low.

```
my-project-prod     ← production namespace
my-project-stage    ← staging namespace
```

Both namespaces run independent copies of all services with their own databases and configuration. Authentik is configured with separate applications and redirect URIs per environment.

### Flux bootstrap (one-time per cluster)

```bash
flux bootstrap github \
  --owner=your-org \
  --repository=your-repo \
  --branch=main \
  --path=flux/clusters/my-cluster \
  --personal
```

This installs the Flux controllers into your cluster and begins reconciling everything under `flux/clusters/my-cluster/`. After this, all changes are made via Git — never via `kubectl apply` directly.

### Deploying a change

```bash
git add .
git commit -m "update backend image tag"
git push
# Flux reconciles automatically (default interval: 1 minute)

# Or force immediate reconciliation:
flux reconcile kustomization apps-prod
```

### Sealed Secrets

Secrets are managed via [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets). The `kubeseal` CLI encrypts secrets against your cluster's public key, producing a `SealedSecret` resource that is safe to commit to Git.

```bash
# Encrypt a secret
kubectl create secret generic my-secret \
  --from-literal=password=hunter2 \
  --dry-run=client -o yaml | \
  kubeseal --format yaml > k8s/base/backend/my-secret.yaml
```

---

## Data Fetching

### GraphQL (if Strawberry enabled)

When Strawberry is enabled, the frontend uses **Apollo Client** for GraphQL queries and **GraphQL Code Generator** to produce TypeScript types from your schema. This means your Python types propagate automatically to the frontend.

```bash
# Regenerate types after changing the schema
just codegen
```

Types are generated per query, not per model — a `GetUser` query and a `GetUserFull` query produce separate types reflecting exactly what each query returns. This is intentional: it keeps TypeScript honest about what data is actually available at each call site.

### REST API (if Strawberry disabled)

When Strawberry is disabled, the frontend uses **TanStack Query (React Query)** for data fetching, caching, and synchronization. The template includes:

- `src/query-client.ts`: QueryClient configuration with authentication
- `src/api/users.ts`: Example REST API hooks using `useQuery` and `useMutation`
- `authenticatedFetch()`: Helper that automatically attaches Authentik tokens to requests

Example usage:

```tsx
import { useCurrentUser, useUpdateUser } from "../api/users";

function MyComponent() {
  const { data: user, isLoading } = useCurrentUser();
  const updateUser = useUpdateUser();
  
  // ... use the data
}
```

TanStack Query provides automatic caching, background refetching, optimistic updates, and devtools for debugging. See the [TanStack Query docs](https://tanstack.com/query/latest) for more details.

---

## Contributing

Improvements and corrections welcome. Please open an issue before a large PR to discuss the approach.
