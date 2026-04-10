{% if cookiecutter.add_frontend == "y" %}
FROM node:22-alpine AS base

RUN npm install -g pnpm
WORKDIR /app
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile

# ── Development ───────────────────────────────────────────────────────────────
FROM base AS dev
COPY . .
CMD ["pnpm", "dev"]

# ── Build ─────────────────────────────────────────────────────────────────────
FROM base AS build
COPY . .
RUN pnpm build

# ── Production (nginx) ────────────────────────────────────────────────────────
FROM nginx:alpine AS prod
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
{% endif %}
