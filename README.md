# Sementes do Amanhã — MVP

Sistema web (PWA) para controle de famílias, doações e entregas de cestas do
**Instituto Sementes do Amanhã**, ONG fictícia da Restinga, em Porto Alegre (RS).

O projeto nasce de um problema de gestão: cadastros de famílias, doações e
entregas vivem em cadernos e planilhas isoladas, o que gera duplicidade, perda de
histórico, retrabalho e dificuldade de prestar contas. O MVP prioriza um cadastro
único de famílias e o registro de entregas **offline**, com integridade embutida.

## Objetivos e ODS

- **ODS 2 — Fome Zero e Agricultura Sustentável** (meta 2.1), com conexão ao ODS 1.
- Contribuição delimitada: tornar a distribuição de cestas mais confiável e
  equitativa, sem resolver a fome no território nem controlar doações ou renda.

## Funcionalidades

| ID | Requisito | Situação |
|----|-----------|----------|
| RF01 | Cadastro único de família com código único e alerta de duplicidade | Implementado |
| RF02 | Registro de entrega offline com fila local (IndexedDB) | Implementado |
| RF03 | Bloqueio de entrega duplicada no mesmo ciclo | Implementado |
| RF04 | Painel do ciclo, relatório em PDF e exportação CSV | Implementado |
| RF06 | Sincronização idempotente por `origem_uuid` | Implementado |
| RNF01–RNF04 | Perfis, OWASP, desempenho e acessibilidade | Implementado |

## Rotas principais

| Rota | Acesso | Função |
|------|--------|--------|
| `/contas/login/` | Público | Login com bloqueio após 5 tentativas |
| `/` | Autenticado | Menu inicial |
| `/familias/` | Autenticado | Busca e listagem (telefone só para coordenação) |
| `/familias/nova/` | Autenticado | Cadastro único de família |
| `/entregas/nova/` | Autenticado | Registro de entrega (offline) |
| `/entregas/pendentes/` | Autenticado | Fila local do aparelho |
| `/estoque/` | Autenticado | Saldo dos itens |
| `/estoque/doacoes/nova/` | Coordenação | Entrada de doação |
| `/painel/` | Coordenação | Totais do ciclo |
| `/painel/relatorio.pdf` | Coordenação | Relatório em PDF |
| `/painel/relatorio.csv` | Coordenação | Exportação CSV |
| `/api/entregas/sincronizar/` | Autenticado | Sincronização offline (JSON) |
| `/sw.js` | Público | Service worker (escopo raiz) |
| `/health/` | Público | Verificação de disponibilidade |

## Arquitetura

Monólito em camadas com MVC na apresentação e Repository na persistência:

1. **Apresentação** — Django Templates + HTMX (previsto) + JS do PWA.
2. **Serviços** — `estoque/services.py` e `entregas/services.py` (duplicidade,
   estoque, entrega) executados em transações.
3. **Domínio** — Família, Item, Doador, Doação, Entrega e Perfil de usuário.
4. **Persistência** — PostgreSQL em produção; IndexedDB no cliente para a fila
   offline; SQLite em desenvolvimento e testes.
5. **Infraestrutura** — service worker (cache do PWA) e fila de sincronização.

## Tecnologias

- Python 3.12+ e Django 5.2 LTS
- Django REST Framework (endpoint de sincronização)
- PostgreSQL 16 (produção) / SQLite (desenvolvimento e testes)
- HTMX (previsto), Workbox-style service worker e IndexedDB
- ReportLab (relatório PDF)
- pytest, pytest-django e Ruff
- GitHub Actions (CI)

## Como executar localmente

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_demo        # dados fictícios de demonstração
python manage.py runserver
```

Acesse http://127.0.0.1:8000/ e entre com um dos usuários de demonstração:

- **Coordenação:** `coordenacao` / `demo-sementes-123`
- **Voluntário:** `voluntario` / `demo-sementes-123`

> As credenciais acima são fictícias e servem apenas para demonstração local.
> Em produção, crie usuários próprios e não versione segredos.

## Funcionamento offline

1. Ao abrir a tela de entrega sem internet (ou desligando a rede), o formulário
   grava o registro no IndexedDB com um `origem_uuid`.
2. A tela de pendentes lista os registros salvos no aparelho.
3. Ao voltar a conexão, a fila é enviada para `/api/entregas/sincronizar/`.
4. O servidor é idempotente pelo `origem_uuid`: reenvios não duplicam a entrega.
5. Conflitos (duplicidade no ciclo ou saldo insuficiente) retornam 409 e o
   registro aparece como "Rejeitado" na fila local.

## Segurança

- Senhas com PBKDF2 (`pbkdf2_sha256`) do Django; nunca em texto limpo.
- Sessão com cookie `HttpOnly`, `SameSite=Lax`, `Secure` em produção e expiração
  deslizante de 8 horas (`SESSION_SAVE_EVERY_REQUEST`).
- HTTPS, HSTS e `DEBUG=False` obrigatórios em produção (`config/settings.py`).
- Autorização por operação: `coordenacao_required` nega por padrão.
- Bloqueio temporário de login após 5 tentativas inválidas.
- CSP (`script-src 'self'`), `Permissions-Policy`, `COOP` e `X-Frame-Options`,
  aplicados por `core/middleware.py` (o admin fica fora da CSP estrita).
- ORM parametrizado, validação no servidor e escape de saída dos templates.
- Segredos em variáveis de ambiente (`.env` fora do versionamento).
- Proxy reverso: `USE_X_FORWARDED_PROTO` e `CSRF_TRUSTED_ORIGINS` documentados
  em `.env.example`.

## Testes e qualidade

```bash
ruff format --check .
ruff check .
python manage.py check
pytest
```

Cobertura atual: **65 testes** (modelos, validações, serviços, views, API,
segurança, painel/relatório, PWA e acessibilidade). O CI executa os mesmos
passos em cada push e Pull Request.

## Fluxo de versionamento

- `main` protegida; mudanças entram por Pull Request.
- Branches: `feat/...`, `fix/...`, `docs/...`, `test/...`.
- Commits no padrão Conventional Commits.
- PR com descrição, checklist e CI verde antes do merge.

## Protótipo

As três telas e as capturas estão em [`docs/prototipo/`](docs/prototipo/):

- `tela1.png` — entrada principal / menu
- `tela2.png` — registro de entrega (offline)
- `tela3.png` — alertas, pendentes e resultados

Modos de captura no HTML: `?only=tela1`, `?only=tela2`, `?only=tela3`.

## Estrutura

```
config/            configuração do projeto Django
core/              menu, painel, PDF/CSV, service worker e seed_demo
contas/            perfis, login com bloqueio e autorização
familias/          cadastro único de famílias (RF01)
estoque/           itens, doadores e doações
entregas/          entregas, regras de duplicidade e API de sincronização
static/            CSS, manifest, service worker e JS offline
docs/prototipo/    protótipo navegável e capturas
tests/             testes automatizados
```

## Limitações conhecidas

- A fila offline usa IndexedDB do navegador: limpar os dados do site apaga os
  registros pendentes. A sincronização automática depende de a aba ser reaberta.
- O bloqueio de tentativas de login usa o cache local do processo; em múltiplas
  instâncias, é necessário um cache compartilhado (Redis).
- Não há módulo de cursos/capacitação, controle financeiro nem aplicativo nativo.
- A validação em campo com duas rodadas de usabilidade ainda será registrada na
  documentação da disciplina.

## Licença

Projeto acadêmico, sem fins comerciais.
