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
- [x] Middleware Starlette que valida credencial em TODA rota HTTP (`/invoke`, `/tools/*`)
- [x] Estratégia de auth definida: bearer token por header
- [x] Rejeitar com `401` quando ausente/inválido; nunca executar tool sem auth
- [x] Segredo/chave vem de env, nunca hardcoded
- [x] Teste: requisição sem credencial → 401; com credencial válida → 200
- [ ] Transporte SSE sob o mesmo middleware (SSE ainda não implementado neste server)

## 2. Entrypoint único + dispatch de tool centralizado (manutenibilidade)
- [x] `src/dispatch.py` com `execute_tool(name, arguments) -> str` como única fonte da lógica
- [x] `stdio` e `http` entrypoints apenas chamam `execute_tool` (zero lógica duplicada)
- [x] Tratamento de erro consistente nos dois caminhos (mesma mensagem, mesmo truncation)
- [x] Registry de tools como `dict[name -> tool]` para lookup O(1) (em vez de loop linear)
- [x] Teste: tool conhecida executa; tool desconhecida retorna erro previsível
- [x] Teste: exceção dentro do tool é capturada e truncada
- [ ] Injeção de dependências no construtor dos tools (fica para quando portar tools com deps, ex. vector DB)

## 3. Cache do token de autenticação (performance/resiliência)
- [x] Serviço de auth cacheia o token e só renova quando expira (usar `expires_in`)
- [x] Cache em memória com TTL
- [x] Retry em 5xx com limite e timeout explícitos (não loop silencioso)
- [x] Teste: segunda chamada dentro do TTL NÃO faz novo request HTTP (mock conta chamadas)
- [x] Teste: token expirado dispara renovação
- [ ] Backend Redis opcional para cache compartilhado entre réplicas (upgrade path)

## 4. Testes unitários + CI (qualidade)
- [x] `truncate_response`: texto curto inalterado; texto > limite cortado com aviso; edge case mensagem > limite
- [x] Dispatch: achar/não achar tool, repasse de `run_context`
- [x] Mock de HTTP para serviços que chamam APIs externas (sem rede nos testes)
- [x] Todos os testes unitários rodam sem rede, sem DB, sem segredos reais
- [ ] Schema de cada tool validado por teste (feito só para o echo; expandir ao portar mais tools)
- [ ] Workflow GitHub Actions rodando `pytest` em push/PR

## 5. Config central + logging + sem side-effects no import (robustez)
- [x] Módulo `settings` central validando envs obrigatórias no boot (falha cedo com mensagem clara)
- [x] `logging.basicConfig` chamado UMA vez só (via `configure_logging`, idempotente)
- [x] Importar qualquer módulo não dispara efeitos colaterais (verificado)
- [x] Usar `lifespan` do Starlette em vez de `@app.on_event` (deprecado)
- [ ] Serviços pesados (embedding/vector DB) no `lifespan` — pendente até portar esses serviços
- [ ] Teste automatizado de "import sem side-effects" (hoje verificado manualmente)

---

## Definição de pronto (global)
- [x] `pytest` verde, sem rede (17 passed)
- [x] Nenhum segredo hardcoded; todas as envs em `.env.example`
- [x] Camada HTTP não executa nada sem autenticação
- [x] stdio e HTTP compartilham a mesma lógica de dispatch
- [x] README atualizado
