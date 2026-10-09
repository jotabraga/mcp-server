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
