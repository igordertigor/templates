{% if cookiecutter.use_stage_namespace == "y" %}
# Sealed secrets for the stage namespace.
#
# These are sealed separately from prod — the namespace is part of the
# encryption context, so prod secrets cannot be reused here.
#
#   kubectl create secret generic postgres-secret \
#     --from-literal=username=postgres \
#     --from-literal=password=<stage-password> \
#     --dry-run=client -o yaml \
#     | kubeseal --format yaml \
#     > k8s/overlays/stage/sealed-secrets/postgres-secret.yaml
#
# Required secrets:
#   - postgres-secret        (keys: username, password)
#   - authentik-secret       (keys: secret-key)
#   - minio-secret           (keys: access-key, secret-key)
#   - backend-secret         (keys: database-url, authentik-client-id)
#
# Stage secrets can use weaker passwords for convenience, but should still
# be kept out of plain-text Git commits.
{% endif %}
