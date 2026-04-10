# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

---

## Stack

| Layer | Choice |
|---|---|
| API | FastAPI |
| ORM | SQLModel + Alembic |
{% if cookiecutter.add_strawberry == "y" %}
| GraphQL | Strawberry |
{% endif %}
{% if cookiecutter.add_arq == "y" %}
| Background tasks | arq + Redis |
{% endif %}
| Auth | Zitadel (OIDC) |
| Storage | MinIO |
| Database | PostgreSQL |
{% if cookiecutter.add_frontend == "y" %}
| Frontend | React + Vite + React Router v7 + Apollo Client + Mantine |
{% endif %}
| Local dev | Docker Compose |
| Deployment | Flux + Kustomize |

---

## First-time setup

### 1. Install dependencies

```bash
just install
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in all required values. At minimum:

- `POSTGRES_PASSWORD` — any strong password for local dev
- `ZITADEL_MASTERKEY` — exactly 32 characters, generate with:
  ```bash
  openssl rand -base64 32 | head -c 32
  ```
{% if cookiecutter.shared_db == "n" %}
- `ZITADEL_POSTGRES_PASSWORD` — password for the Zitadel Postgres instance
{% endif %}
- `MINIO_ROOT_PASSWORD` — any password for local dev

### 3. Start backing services

```bash
just up
```

This starts PostgreSQL, Zitadel, MinIO{% if cookiecutter.add_arq == "y" %}, and Redis{% endif %} via Docker Compose.

### 4. Set up Zitadel

Zitadel requires a one-time configuration via its admin UI. Visit http://localhost:8080 after `just up` completes.

#### Create a project

1. Log in with the initial admin credentials printed in the Zitadel container logs:
   ```bash
   docker compose logs zitadel | grep -i "initial"
   ```
2. Navigate to **Projects** → **New Project**
3. Name it `{{ cookiecutter.project_name }}`

#### Create applications

{% if cookiecutter.auth_user_pkce == "y" %}
**Web application (PKCE — for the frontend):**
1. Inside your project, click **New Application**
2. Name: `frontend`, Type: **Web**, Auth method: **PKCE**
3. Redirect URI: `http://localhost:5173/auth/callback`
4. Post-logout redirect URI: `http://localhost:5173`
5. Copy the **Client ID** and add it to `.env` as `ZITADEL_CLIENT_ID`
{% endif %}

{% if cookiecutter.auth_client_credentials == "y" %}
**API application (client credentials — for machine-to-machine):**
1. Inside your project, click **New Application**
2. Name: `backend-service`, Type: **API**, Auth method: **Private Key JWT** or **Basic**
3. Copy the **Client ID** and **Client Secret** — store them securely
{% endif %}

{% if cookiecutter.auth_device_flow == "y" %}
**Device flow application:**
1. Inside your project, click **New Application**
2. Name: `cli`, Type: **Native**
3. Enable **Device Authorization** grant type
4. Copy the **Client ID** and set it in your CLI configuration
{% endif %}

#### Production / stage environments

Repeat the application setup for each environment with the correct redirect URIs:
- Stage: `https://your-stage-domain/auth/callback`
- Prod: `https://your-prod-domain/auth/callback`

Zitadel should have its `ZITADEL_EXTERNALDOMAIN` set correctly per environment — this is handled by the Kustomize overlays in `k8s/overlays/`.

### 5. Run database migrations

```bash
just migrate
```

### 6. Start the development servers

```bash
# Backend only
just dev-backend

# Frontend only (separate terminal)
{% if cookiecutter.add_frontend == "y" %}
just dev-frontend
{% endif %}

# Or both together
just dev
```

- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs
{% if cookiecutter.add_strawberry == "y" %}
- GraphQL playground: http://localhost:8000/graphql
{% endif %}
{% if cookiecutter.add_frontend == "y" %}
- Frontend: http://localhost:5173
{% endif %}
- Zitadel: http://localhost:8080
- MinIO console: http://localhost:9001

---

## Database migrations

After changing `backend/app/tables.py`:

```bash
# Generate a migration
just migration "describe your change"

# Review the generated file in backend/migrations/versions/
# Then apply it
just migrate

# Roll back one step if needed
just migrate-down
```

**Important:** Always review auto-generated migrations before applying. Alembic's
autogenerate is reliable for adding/removing columns and tables but may miss
complex constraints or indexes. Check the generated file before committing.

---

{% if cookiecutter.add_strawberry == "y" and cookiecutter.add_frontend == "y" %}
## GraphQL type generation

After changing the Strawberry schema, regenerate TypeScript types:

```bash
# Backend must be running
just dev-backend &
just codegen
```

Generated types land in `frontend/src/graphql/__generated__/`. These are
committed to the repo so the frontend build does not require a running backend
in CI.

---

{% endif %}
{% if cookiecutter.add_arq == "y" %}
## Background tasks

Tasks are defined in `backend/app/worker/tasks.py` and registered in
`backend/app/worker/settings.py`.

```bash
# Run the worker locally
just worker
```

To enqueue a job from a FastAPI route:

```python
from arq import create_pool
from arq.connections import RedisSettings
from app.settings import settings

redis = await create_pool(RedisSettings.from_dsn(settings.redis_url))
await redis.enqueue_job("example_task", "hello")
```

---

{% endif %}
## Kubernetes deployment

### Prerequisites

- A running Kubernetes cluster (k3s, k3d, kind, or managed)
- [Flux CLI](https://fluxcd.io/flux/installation/) installed
- [kubeseal](https://github.com/bitnami-labs/sealed-secrets) installed
- Sealed Secrets controller running in your cluster:
  ```bash
  kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/latest/download/controller.yaml
  ```

### Seal your secrets

Before deploying, seal all secrets for each overlay. See the README in
`k8s/overlays/prod/sealed-secrets/` and `k8s/overlays/stage/sealed-secrets/`
for the exact commands.

```bash
# Example for postgres-secret in prod
kubectl create secret generic postgres-secret \
  --from-literal=username=postgres \
  --from-literal=password=<strong-password> \
  --namespace={{ cookiecutter.project_slug }}-prod \
  --dry-run=client -o yaml \
  | kubeseal --format yaml \
  > k8s/overlays/prod/sealed-secrets/postgres-secret.yaml
```

Add the sealed secret files to `k8s/overlays/prod/sealed-secrets/kustomization.yaml`.

### Flux bootstrap (one-time per cluster)

```bash
flux bootstrap github \
  --owner=your-org \
  --repository={{ cookiecutter.project_slug }} \
  --branch=main \
  --path=flux/clusters/my-cluster \
  --personal
```

After bootstrap, Flux reconciles everything under `flux/clusters/my-cluster/`
automatically. All further changes are made via Git.

### Updating image tags

Image tags are set in `k8s/overlays/prod/kustomization.yaml`. Update the
`newTag` field and push — Flux will roll out the new image:

```yaml
images:
  - name: {{ cookiecutter.project_slug }}-backend
    newTag: "abc1234"  # your image digest or tag
```

### Force immediate reconciliation

```bash
just flux-prod
{% if cookiecutter.use_stage_namespace == "y" %}
just flux-stage
{% endif %}
```

---

## Project structure

```
.
├── justfile                      # all common tasks
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI app factory
│   │   ├── settings.py           # pydantic-settings
│   │   ├── db.py                 # engine + session dependency
│   │   ├── tables.py             # ALL SQLModel table definitions
│   │   ├── crud/                 # generic + domain-specific CRUD
│   │   ├── routers/              # REST endpoints
{% if cookiecutter.add_strawberry == "y" %}
│   │   ├── graphql/              # Strawberry schema + resolvers
{% endif %}
│   │   ├── auth/                 # JWT validation + OAuth helpers
{% if cookiecutter.add_arq == "y" %}
│   │   └── worker/               # arq task definitions
{% endif %}
│   └── migrations/               # Alembic migrations
{% if cookiecutter.add_frontend == "y" %}
├── frontend/
│   └── src/
│       ├── auth/                 # oidc-client-ts setup
│       ├── pages/
│       ├── components/
│       └── graphql/              # queries, mutations, generated types
{% endif %}
├── k8s/
│   ├── base/                     # environment-agnostic manifests
│   └── overlays/
│       ├── local/                # kind/k3d with plain secrets
{% if cookiecutter.use_stage_namespace == "y" %}
│       ├── stage/                # namespace: {{ cookiecutter.project_slug }}-stage
{% endif %}
│       └── prod/                 # namespace: {{ cookiecutter.project_slug }}-prod
└── flux/
    └── clusters/my-cluster/      # Flux Kustomization resources
```
