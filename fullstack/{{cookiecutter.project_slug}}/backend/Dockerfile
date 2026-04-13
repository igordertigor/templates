FROM python:{{ cookiecutter.python_version }}-slim AS base

WORKDIR /app

RUN pip install uv

COPY pyproject.toml .
COPY uv.lock* .

# -- Development ----------------------------------------------------------------
FROM base AS dev

RUN uv sync --frozen

COPY . .

CMD ["uv", "run", "fastapi", "dev", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]

# -- Production -----------------------------------------------------------------
FROM base AS prod

RUN uv sync --frozen --no-dev

COPY . .

CMD ["uv", "run", "fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
