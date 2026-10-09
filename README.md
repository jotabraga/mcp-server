# MCP Server

MCP server with a centralized tool dispatcher, authenticated HTTP transport, and validated
configuration.

## Key design points

- **One dispatch path.** Both the stdio and HTTP entrypoints call `src/dispatch.py::execute_tool`,
  so error handling and truncation never diverge between transports.
- **Authenticated HTTP.** Every HTTP route is guarded by a bearer-token middleware
  (`src/http/auth.py`). No tool runs without a valid token.
- **Validated config.** `src/settings.py` reads and validates environment variables once at
  startup and fails fast with a clear message.
- **Cached tokens.** `src/services/keycloak.py` caches the client-credentials token and renews
  it only near expiry.
- **No import side effects.** Importing a module never opens a connection or downloads a model;
  heavy work happens in the HTTP lifespan.

## Running

Install dependencies:

```sh
poetry install --with dev
```

stdio (for MCP clients):

```sh
poetry run python mcp_server.py
```

HTTP:

```sh
poetry run uvicorn --factory main:create_app --host 0.0.0.0 --port 8000
```

Set `MCP_API_KEY` first (see `.env.example`). HTTP clients must send
`Authorization: Bearer <MCP_API_KEY>`.

## Testing

```sh
poetry run pytest
```

All unit tests run without network, database, or real secrets.

## Health check

`GET /healthz` returns `{"status": "ok"}` and is intentionally unauthenticated, so Kubernetes
liveness/readiness probes work without a token.

## Deployment (infra)

The server is packaged as a Docker image and deployed to Kubernetes:

1. `.github/workflows/deploy.yml` builds the image, pushes it to ECR, and applies the manifest.
2. `k8s/build-deployment.yaml.sh` renders a Deployment + ClusterIP Service from env vars.
3. All secrets are injected at deploy time from GitHub Actions `secrets`/`vars` — none are
   stored in the repository.

The Service is `ClusterIP` (internal only): consumers reach it from inside the cluster at
`http://mcp-server.<namespace>:8000`, authenticating with the bearer token (`MCP_API_KEY`).

Required runtime dependencies (all via env): Keycloak, the IA API, Qdrant, a GitHub App, and
Redis. See `.env.example` for the full list.
