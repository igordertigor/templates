"""
Post-generation hook.

Two responsibilities:
1. Remove directories and files for features that were disabled at prompt time.
2. Clean up consecutive blank lines left behind by Jinja2 conditional blocks in
   YAML files (harmless but untidy).
"""

import re
import shutil
from pathlib import Path

ROOT = Path.cwd()

# ── Feature flags ─────────────────────────────────────────────────────────────

ADD_FRONTEND = "{{ cookiecutter.add_frontend }}" == "y"
ADD_STRAWBERRY = "{{ cookiecutter.add_strawberry }}" == "y"
ADD_ARQ = "{{ cookiecutter.add_arq }}" == "y"
USE_STAGE_NAMESPACE = "{{ cookiecutter.use_stage_namespace }}" == "y"
AUTH_DEVICE_FLOW = "{{ cookiecutter.auth_device_flow }}" == "y"
AUTH_CLIENT_CREDS = "{{ cookiecutter.auth_client_credentials }}" == "y"


# ── Helpers ───────────────────────────────────────────────────────────────────


def remove(path: str) -> None:
    target = ROOT / path
    if target.is_dir():
        shutil.rmtree(target)
    elif target.is_file():
        target.unlink(missing_ok=True)


def clean_blank_lines(path: Path) -> None:
    """Replace 3+ consecutive blank lines with a single blank line."""
    text = path.read_text(encoding="utf-8")
    cleaned = re.sub(r"\n{3,}", "\n\n", text)
    # Also strip leading blank lines at the top of the file
    cleaned = cleaned.lstrip("\n")
    if cleaned != text:
        path.write_text(cleaned, encoding="utf-8")


def clean_yaml_files(root: Path) -> None:
    for yaml_file in root.rglob("*.yaml"):
        clean_blank_lines(yaml_file)
    for yaml_file in root.rglob("*.yml"):
        clean_blank_lines(yaml_file)


def clean_python_files(root: Path) -> None:
    """Clean up blank lines in Python files too for disabled-block stubs."""
    for py_file in root.rglob("*.py"):
        clean_blank_lines(py_file)


# ── Remove disabled features ──────────────────────────────────────────────────

if not ADD_FRONTEND:
    remove("frontend")
    remove("k8s/base/frontend")

if not ADD_STRAWBERRY:
    remove("backend/app/graphql")
    if ADD_FRONTEND:
        remove("frontend/codegen.ts")
        remove("frontend/tsconfig.node.json")  # codegen.ts is its only non-vite entry
        remove("frontend/src/graphql")

if not ADD_ARQ:
    remove("backend/app/worker")
    remove("k8s/base/redis")
    remove("k8s/base/worker")

if not USE_STAGE_NAMESPACE:
    remove("k8s/overlays/stage")
    remove("flux/clusters/my-cluster/apps-stage.yaml")

if not AUTH_DEVICE_FLOW:
    remove("backend/app/auth/device.py")

# ── Restore tsconfig.node.json if strawberry was removed but frontend kept ────
# vite.config.ts still needs it even without codegen.ts
if ADD_FRONTEND and not ADD_STRAWBERRY:
    tsconfig_node = ROOT / "frontend" / "tsconfig.node.json"
    if not tsconfig_node.exists():
        tsconfig_node.write_text(
            "{\n"
            '  "compilerOptions": {\n'
            '    "tsBuildInfoFile": "./node_modules/.tmp/tsconfig.node.tsbuildinfo",\n'
            '    "target": "ES2022",\n'
            '    "lib": ["ES2023"],\n'
            '    "module": "ESNext",\n'
            '    "skipLibCheck": true,\n'
            '    "moduleResolution": "bundler",\n'
            '    "allowImportingTsExtensions": true,\n'
            '    "isolatedModules": true,\n'
            '    "moduleDetection": "force",\n'
            '    "noEmit": true,\n'
            '    "strict": true,\n'
            '    "noUnusedLocals": true,\n'
            '    "noUnusedParameters": true,\n'
            '    "noFallthroughCasesInSwitch": true,\n'
            '    "noUncheckedSideEffectImports": true\n'
            "  },\n"
            '  "include": ["vite.config.ts"]\n'
            "}\n",
            encoding="utf-8",
        )

# ── Clean up blank lines left by Jinja2 conditionals ─────────────────────────

clean_yaml_files(ROOT)
clean_python_files(ROOT)

# ── Done ──────────────────────────────────────────────────────────────────────

print("")
print("✓ Project generated: {{ cookiecutter.project_slug }}")
print("")
print("Next steps:")
print("  1. cd {{ cookiecutter.project_slug }}")
print("  2. cp .env.example .env        # fill in secrets")
print("  3. just up                     # start backing services")
print("  4. just migrate                # run database migrations")
print("  5. just dev-backend            # start the API (http://localhost:8000)")
if ADD_FRONTEND:
    print(
        "  6. just dev-frontend           # start the frontend (http://localhost:5173)"
    )
print("")
print("See README.md for Zitadel setup and Flux bootstrap instructions.")
print("")
