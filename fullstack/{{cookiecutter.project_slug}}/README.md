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
| Auth | Authentik (OIDC) |
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
- `AUTHENTIK_SECRET_KEY` — generate with:
  ```bash
  openssl rand -base64 60 | tr -d '\n'
  ```
{% if cookiecutter.shared_db == "n" %}
- `AUTHENTIK_POSTGRES_PASSWORD` — password for the Authentik Postgres instance
{% endif %}
- `MINIO_ROOT_PASSWORD` — any password for local dev

### 3. Start backing services

```bash
just up
```

This starts PostgreSQL, Authentik, MinIO{% if cookiecutter.add_arq == "y" %}, and Redis{% endif %} via Docker Compose.

{% if cookiecutter.shared_db == "y" %}
**Important:** If you see "database authentik does not exist" errors, it means the PostgreSQL volume already exists from a previous run. The init script only runs on **first volume creation**. Solutions:

**Option 1: Start fresh (if no important data):**
```bash
docker compose down -v  # Deletes all volumes
just up
```

**Option 2: Manually create the database:**
```bash
docker compose exec postgres psql -U postgres -c "CREATE DATABASE authentik;"
docker compose restart authentik-server authentik-worker
```
{% endif %}

### 4. Set up Authentik

Authentik requires a one-time configuration via its admin UI.

#### Initial setup

1. Visit http://localhost:8080/if/flow/initial-setup/ (note the trailing slash!)
2. Set a password for the default **akadmin** user
3. Log in at http://localhost:8080 with username `akadmin` and your password

#### Create an Application and Provider

1. Navigate to **Applications** → **Applications** → **Create**
2. Name: `{{ cookiecutter.project_name }}`
3. Slug: `{{ cookiecutter.project_slug }}` (this will be your `AUTHENTIK_APP_SLUG`)
4. Provider: **Create a new provider**
5. Choose **OAuth2/OpenID Provider**
6. Configure the provider:
   - **Name**: `{{ cookiecutter.project_name }} Provider`
   - **Authorization flow**: default-provider-authorization-implicit-consent
   - **Client type**: Confidential
   - **Client ID**: (auto-generated) — copy this to `.env` as `AUTHENTIK_CLIENT_ID`
   - **Client Secret**: (auto-generated) — save this securely
   - **Redirect URIs**: Add the following (one per line):
     ```
     http://localhost:5173/auth/callback
     http://localhost:8000/docs/oauth2-redirect
     ```
   - **Signing Key**: authentik Self-signed Certificate
7. Save the provider and application
8. Update your `.env` file:
   ```bash
   AUTHENTIK_APP_SLUG={{ cookiecutter.project_slug }}
   AUTHENTIK_CLIENT_ID=<client-id-from-authentik>
   ```

{% if cookiecutter.auth_client_credentials == "y" %}
#### For machine-to-machine (client credentials):
1. Create a **Service Account** user in Authentik
2. Create a separate Application with **Client Credentials** flow
3. Assign appropriate permissions/groups to the service account
{% endif %}

{% if cookiecutter.auth_device_flow == "y" %}
#### For device flow:
1. In your provider configuration, ensure **Device Code Flow** is enabled
2. The device authorization endpoint will be: `http://localhost:8080/application/o/{{ cookiecutter.project_slug }}/device/`
{% endif %}

#### Production / stage environments

Repeat the application setup for each environment with the correct redirect URIs:
- Stage: `https://your-stage-domain/auth/callback`
- Prod: `https://your-prod-domain/auth/callback`

Update the Kubernetes ConfigMaps and Secrets in `k8s/overlays/` with the environment-specific values.

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
- Authentik: http://localhost:8080
- MinIO console: http://localhost:9001

---

## Troubleshooting

### Authentik: "database authentik does not exist"

{% if cookiecutter.shared_db == "y" %}
If you see this error when starting Authentik, it means the `authentik` database wasn't created in the shared PostgreSQL instance. This can happen if you had an existing PostgreSQL volume before switching to Authentik.

**Solution: Manually create the database**
```bash
docker compose exec postgres psql -U postgres -c "CREATE DATABASE authentik;"
docker compose restart authentik-server authentik-worker
```

Alternatively, if you don't have important data yet:
```bash
docker compose down -v  # WARNING: Deletes all volumes!
docker compose up -d
```
{% endif %}

### Port conflicts

If you see "address already in use" errors:
- Authentik uses ports **8080** (HTTP) and **8443** (HTTPS)
- MinIO uses ports **9000** (API) and **9001** (Console)
- Backend uses port **8000**
- Frontend uses port **5173**
- PostgreSQL uses port **5432**

Check what's using a port:
```bash
lsof -i :8080  # Replace with the conflicting port
```

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
