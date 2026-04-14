# Authentik Blueprints

This directory contains [Authentik blueprints](https://docs.goauthentik.io/customize/blueprints/) that automate the configuration of Authentik for local development.

## What are Blueprints?

Blueprints are YAML files that declaratively define Authentik configurations. They allow you to:
- Automate the creation of applications, providers, flows, and policies
- Ensure consistent configuration across environments
- Version control your authentication setup
- Avoid manual clicking through the UI

## Included Blueprints

### `oauth2-application.yaml`

Creates the OAuth2/OIDC provider and application for {{ cookiecutter.project_name }}.

**What it creates:**
- OAuth2/OIDC Provider: `{{ cookiecutter.project_name }} Provider`
- Application: `{{ cookiecutter.project_name }}` (slug: `{{ cookiecutter.project_slug }}`)

**Configuration:**
- **Client ID**: Set from `AUTHENTIK_CLIENT_ID` environment variable
  - This is the public identifier for your OAuth2 application
  - Must be set before Authentik starts (blueprint uses it during creation)
  - Generate with: `openssl rand -hex 20`
- **Client Type**: Public
  - Suitable for browser-based SPAs that cannot securely store secrets
  - Uses PKCE (Proof Key for Code Exchange) for security
  - No client secret required
- **Redirect URIs**:
  - `http://localhost:5173/auth/callback` (frontend)
  - `http://localhost:8000/docs/oauth2-redirect` (API docs)
- **Token Validity**:
  - Access Code: 1 minute
  - Access Token: 5 minutes
  - Refresh Token: 30 days
- **Signing Key**: authentik Self-signed Certificate
- **Authorization Flow**: default-provider-authorization-implicit-consent

**Requirements:**
- `AUTHENTIK_CLIENT_ID` **must** be set in `.env` before starting Authentik
- The blueprint will fail to apply if `AUTHENTIK_CLIENT_ID` is missing or empty
- Generate with: `openssl rand -hex 20`

## How Blueprints are Applied

Blueprints in this directory are automatically discovered and applied by Authentik:

1. The `docker-compose.yml` mounts this directory to `/blueprints/custom` in both `authentik-server` and `authentik-worker`
2. Authentik watches this directory for changes
3. When Authentik starts, it applies all blueprints with `blueprints.goauthentik.io/instantiate: "true"` in their metadata
4. If you modify a blueprint, Authentik will re-apply it automatically (blueprints are idempotent)

## Modifying Blueprints

To customize the OAuth2 provider configuration:

1. Edit `oauth2-application.yaml`
2. Restart Authentik to apply changes:
   ```bash
   docker compose restart authentik-server authentik-worker
   ```

Common modifications:
- **Token validity**: Adjust `access_token_validity`, `refresh_token_validity`
- **Redirect URIs**: Add more URIs to `redirect_uris_dev`
- **Authorization flow**: Change to a custom flow (create it first in Authentik)

## Creating Additional Blueprints

To add more blueprints:

1. Create a new `.yaml` file in this directory
2. Follow the [blueprint structure](https://docs.goauthentik.io/customize/blueprints/v1/structure/)
3. Add the instantiate label to the metadata:
   ```yaml
   metadata:
     labels:
       blueprints.goauthentik.io/instantiate: "true"
   ```
4. Restart Authentik to apply

Example use cases:
- Custom authentication flows
- Additional OAuth2 providers for other services
- Default user groups and permissions
- Email configuration
- Branding and theming

## Exporting Existing Configurations

If you've manually configured something in Authentik and want to convert it to a blueprint:

1. Export from the Authentik admin UI:
   - For flows: **Flows** → select flow → click **Export** (download icon)
   - For global export: Run `ak export_blueprint` in the `authentik-worker` container

2. Clean up the exported YAML:
   - Remove hardcoded primary keys
   - Add context variables for environment-specific values
   - Use `!Find` and `!KeyOf` tags to reference other objects

3. Save to this directory and restart Authentik

## Troubleshooting

### Blueprint not applying

Check the Authentik worker logs:
```bash
docker compose logs authentik-worker | grep blueprint
```

Common issues:
- Missing required context variables (e.g., `AUTHENTIK_CLIENT_ID`)
  - Error message: "Failed to apply blueprint: 'AUTHENTIK_CLIENT_ID' is not defined"
  - Solution: Set `AUTHENTIK_CLIENT_ID` in your `.env` file
- Invalid YAML syntax
- References to non-existent objects (e.g., flows, certificates)
- Incorrect model names

### Blueprint applied but configuration is wrong

1. Check the blueprint instance status in Authentik:
   - Navigate to **Customization** → **Blueprints**
   - Find your blueprint and click on it
   - Check the **Last applied** timestamp and any error messages

2. Verify context variables:
   - Context variables from `.env` are only available if prefixed with `AUTHENTIK_`
   - Use `!Env VARIABLE_NAME` to access them in the blueprint

### Reset to default configuration

To remove the blueprint-created configuration:

1. Delete the application and provider from Authentik admin UI
2. Re-apply the blueprint:
   ```bash
   docker compose restart authentik-server authentik-worker
   ```

Or delete everything and start fresh:
```bash
docker compose down -v
docker compose up -d
```

## References

- [Authentik Blueprint Documentation](https://docs.goauthentik.io/customize/blueprints/)
- [Blueprint File Structure](https://docs.goauthentik.io/customize/blueprints/v1/structure/)
- [Blueprint YAML Tags](https://docs.goauthentik.io/customize/blueprints/v1/tags/)
- [Blueprint Models Reference](https://docs.goauthentik.io/customize/blueprints/v1/models/)
- [Example Blueprints](https://github.com/goauthentik/authentik/tree/main/blueprints/example)
