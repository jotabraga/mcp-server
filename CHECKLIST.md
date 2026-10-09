# MCP Server — Checklist de Implementação

Novo MCP server construído desde o início com as 5 melhorias identificadas na análise do
`lia-mcp-server`. Cada melhoria vira um bloco abaixo. Marcar `[x]` conforme concluído.

Princípio norteador: só construir o que é necessário, reusar stdlib/libs já presentes, e deixar
cada peça de lógica não-trivial com pelo menos um teste que falha se ela quebrar.

---

## 0. Fundação do projeto
- [x] `pyproject.toml` com metadados corretos (nome, descrição, autor reais) — não deixar placeholders
- [x] Dependências base: `mcp`, `starlette`, `uvicorn`, `python-dotenv`, `requests`
- [x] Dependências de dev: `pytest`, `respx` para mock de HTTP
- [x] Config `[tool.pytest.ini_options]` (`testpaths`, `python_files`)
- [x] `.env.example` documentando TODAS as envs necessárias
- [x] `.gitignore` (venv, `__pycache__`, `.env`, lock se biblioteca)
- [x] `README.md` com como rodar (stdio e HTTP) e como testar

## 1. Autenticação na camada HTTP (segurança — prioridade máxima)
- [x] Middleware Starlette que valida credencial em TODA rota HTTP (`/invoke`, `/tools/*`, `/sse`, `/messages`)
- [x] Estratégia de auth definida: bearer token por header
- [x] Rejeitar com `401` quando ausente/inválido; nunca executar tool sem auth
- [x] Segredo/chave vem de env, nunca hardcoded
- [x] Teste: requisição sem credencial → 401; com credencial válida → 200
- [x] Transporte SSE sob o mesmo middleware (SSE + /messages montados e testados sob auth)

## 2. Entrypoint único + dispatch de tool centralizado (manutenibilidade)
- [x] `src/dispatch.py` com `execute_tool(name, arguments) -> str` como única fonte da lógica
- [x] `stdio` e `http`/`sse` compartilham `execute_tool` e o mesmo MCP Server (zero lógica duplicada)
- [x] Tratamento de erro consistente nos dois caminhos (mesma mensagem, mesmo truncation)
- [x] Registry de tools como `dict[name -> tool]` para lookup O(1) (em vez de loop linear)
- [x] Injeção de dependências via `requires_services` — sem case especial por nome de tool
- [x] Teste: tool conhecida executa; tool desconhecida retorna erro previsível
- [x] Teste: exceção dentro do tool é capturada e truncada
- [x] Teste: injeção de dependências (com e sem provider)

## 3. Cache do token de autenticação (performance/resiliência)
- [x] Serviço de auth cacheia o token e só renova quando expira (usar `expires_in`)
- [x] Cache em memória com TTL
- [x] Retry em 5xx com limite e timeout explícitos (não loop silencioso)
- [x] Teste: segunda chamada dentro do TTL NÃO faz novo request HTTP (mock conta chamadas)
- [x] Teste: token expirado dispara renovação
- [ ] Backend Redis opcional para cache compartilhado entre réplicas (upgrade path documentado no código)

## 4. Testes unitários + CI (qualidade)
- [x] `truncate_response`: texto curto inalterado; texto > limite cortado com aviso; edge case mensagem > limite
- [x] Dispatch: achar/não achar tool, repasse de `run_context`, injeção de serviços
- [x] Schema de cada tool do registry validado por teste parametrizado
- [x] Mock de HTTP para serviços que chamam APIs externas (sem rede nos testes)
- [x] Workflow GitHub Actions rodando `pytest` em push/PR
- [x] Todos os testes unitários rodam sem rede, sem DB, sem segredos reais

## 5. Config central + logging + sem side-effects no import (robustez)
- [x] Módulo `settings` central validando envs obrigatórias no boot (falha cedo com mensagem clara)
- [x] `logging.basicConfig` chamado UMA vez só (via `configure_logging`, idempotente)
- [x] Serviços pesados criados no `lifespan` via `ServiceProvider` lazy, NUNCA no topo do módulo
- [x] Importar qualquer módulo não dispara efeitos colaterais (teste em subprocess com env limpo)
- [x] Usar `lifespan` do Starlette em vez de `@app.on_event` (deprecado)
- [x] Teste automatizado de "import sem side-effects"

---

## Definição de pronto (global)
- [x] `pytest` verde, sem rede (28 passed)
- [x] Nenhum segredo hardcoded; todas as envs em `.env.example`
- [x] Camada HTTP (REST + SSE) não executa nada sem autenticação
- [x] stdio e HTTP compartilham a mesma lógica de dispatch
- [x] README atualizado

## Pendências conhecidas (fase futura)
- Portar os tools reais do `lia-mcp-server` (vector search, canvas, routines, code interpreter, ...)
- Backend Redis opcional para o cache de token entre réplicas
- Instanciar vector DB / embedding no `lifespan` quando o tool de busca for portado
