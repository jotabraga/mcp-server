# MCP Server — Checklist de Implementação

Novo MCP server construído desde o início com as 5 melhorias identificadas na análise do
`lia-mcp-server`. Cada melhoria vira um bloco abaixo. Marcar `[x]` conforme concluído.

Princípio norteador: só construir o que é necessário, reusar stdlib/libs já presentes, e deixar
cada peça de lógica não-trivial com pelo menos um teste que falha se ela quebrar.

---

## 0. Fundação do projeto
- [ ] `pyproject.toml` com metadados corretos (nome, descrição, autor reais) — não deixar placeholders
- [ ] Dependências base: `mcp`, `starlette`, `uvicorn`, `python-dotenv`, `requests`
- [ ] Dependências de dev: `pytest`, `pytest-mock`, `respx` (ou `responses`) para mock de HTTP
- [ ] Config `[tool.pytest.ini_options]` (`testpaths`, `python_files`)
- [ ] `.env.example` documentando TODAS as envs necessárias
- [ ] `.gitignore` (venv, `__pycache__`, `.env`, lock se biblioteca)
- [ ] `README.md` com como rodar (stdio e HTTP) e como testar

## 1. Autenticação na camada HTTP (segurança — prioridade máxima)
- [ ] Middleware Starlette que valida credencial em TODA rota HTTP (`/invoke`, `/tools/*`, SSE)
- [ ] Estratégia de auth definida: bearer token (via Keycloak) **ou** API key por header
- [ ] Rejeitar com `401` quando ausente/inválido; nunca executar tool sem auth
- [ ] Segredo/chave vem de env, nunca hardcoded
- [ ] Teste: requisição sem credencial → 401; com credencial válida → 200
- [ ] Teste: `code_interpreter`/executores de código inacessíveis sem auth

## 2. Entrypoint único + dispatch de tool centralizado (manutenibilidade)
- [ ] `src/dispatch.py` com `execute_tool(name, arguments) -> str` como única fonte da lógica
- [ ] `stdio` e `http` entrypoints apenas chamam `execute_tool` (zero lógica duplicada)
- [ ] Tratamento de erro consistente nos dois caminhos (mesma mensagem, mesmo truncation)
- [ ] Injeção de dependências no construtor dos tools — eliminar o case especial `if name == "search_knowledge_base"`
- [ ] Registry de tools como `dict[name -> tool]` para lookup O(1) (em vez de loop linear)
- [ ] Teste: tool conhecida executa; tool desconhecida retorna erro previsível
- [ ] Teste: exceção dentro do tool é capturada e truncada igual nos dois entrypoints

## 3. Cache do token de autenticação (performance/resiliência)
- [ ] Serviço de auth cacheia o token e só renova quando expira (usar `expires_in`)
- [ ] Cache em memória com TTL (mínimo) ou Redis se o projeto já provisionar Redis
- [ ] Retry em 5xx com limite e timeout explícitos (não loop silencioso)
- [ ] Teste: segunda chamada dentro do TTL NÃO faz novo request HTTP (mock conta chamadas)
- [ ] Teste: token expirado dispara renovação

## 4. Testes unitários + CI (qualidade)
- [ ] `truncate_response`: texto curto inalterado; texto > limite cortado com aviso; edge case mensagem > limite
- [ ] Dispatch: achar/não achar tool, repasse de `run_context`
- [ ] Schema de cada tool: `get_tool_input_schema()` retorna `name`/`description`/`inputSchema` válidos e `required` coerente
- [ ] Mock de HTTP para tools que chamam APIs externas (sem rede nos testes)
- [ ] Workflow GitHub Actions rodando `pytest` em push/PR
- [ ] Todos os testes unitários rodam sem rede, sem DB, sem segredos reais

## 5. Config central + logging + sem side-effects no import (robustez)
- [ ] Módulo `settings` central validando envs obrigatórias no boot (falha cedo com mensagem clara)
- [ ] `logging.basicConfig` chamado UMA vez só no entrypoint (não em cada módulo)
- [ ] Serviços pesados (ex. embedding/vector DB) criados no `lifespan`/startup, NUNCA no topo do módulo
- [ ] Importar qualquer módulo não deve abrir conexão nem baixar modelo
- [ ] Usar `lifespan` do Starlette em vez de `@app.on_event` (deprecado)
- [ ] Teste: importar o entrypoint não dispara efeitos colaterais (não exige serviço no ar)

---

## Definição de pronto (global)
- [ ] `pytest` verde, sem rede
- [ ] Nenhum segredo hardcoded; todas as envs em `.env.example`
- [ ] Camada HTTP não executa nada sem autenticação
- [ ] stdio e HTTP compartilham a mesma lógica de dispatch
- [ ] README atualizado
