FROM node:24-bookworm-slim AS frontend
WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/index.html web/vite.config.js ./
COPY web/src ./src
COPY web/public ./public
RUN npm run build

FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONUNBUFFERED=1 \
    PORT=10000
COPY pyproject.toml uv.lock .python-version README.md ./
RUN uv sync --locked --no-dev --no-install-project
COPY src/phantom-strategies ./src/phantom-strategies
COPY db/*.feather ./db/
COPY --from=frontend /web/dist ./web/dist
RUN useradd --create-home app
USER app
EXPOSE 10000
CMD ["sh", "-c", "exec uv run --no-sync uvicorn web_app:app --app-dir src/phantom-strategies --host 0.0.0.0 --port \"$PORT\" --workers 1 --no-proxy-headers"]
