# Sealed secrets for the prod namespace.
#
# Generate each secret with kubeseal:
#
#   kubectl create secret generic postgres-secret \
#     --from-literal=username=postgres \
#     --from-literal=password=<strong-password> \
#     --dry-run=client -o yaml \
#     | kubeseal --format yaml \
#     > k8s/overlays/prod/sealed-secrets/postgres-secret.yaml
#
# Required secrets:
#   - postgres-secret        (keys: username, password)
#   - zitadel-secret         (keys: masterkey)
#   - minio-secret           (keys: access-key, secret-key)
#   - backend-secret         (keys: database-url, zitadel-client-id)
#
# After sealing, add each file to the kustomization.yaml resources list.
#
# Never commit unsealed Secret manifests to Git.
