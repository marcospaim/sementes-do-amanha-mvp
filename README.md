# Sementes do Amanhã — MVP

Sistema web (PWA) para controle de doações, famílias e entregas de cestas do
**Instituto Sementes do Amanhã**, ONG fictícia da Restinga, em Porto Alegre (RS).

O projeto nasce de um problema real de gestão: cadastros de famílias, doações e
entregas vivem em cadernos e planilhas isoladas, o que gera duplicidade, perda de
histórico, retrabalho e dificuldade de prestar contas. O MVP prioriza um cadastro
único de famílias e o registro de entregas **offline**, com integridade embutida.

## Objetivos e ODS

- **ODS 2 — Fome Zero e Agricultura Sustentável** (meta 2.1), com conexão ao ODS 1.
- Contribuição delimitada: tornar a distribuição de cestas mais confiável e
  equitativa, sem resolver a fome no território nem controlar doações ou renda.

## Escopo do MVP

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF01 | Cadastrar família com código único | Obrigatório |
| RF02 | Registrar entrega mesmo sem internet | Obrigatório |
| RF03 | Bloquear entrega duplicada no mesmo ciclo | Obrigatório |
| RF04 | Gerar relatório mensal em PDF | Desejável |

Requisitos não funcionais: RNF01 (autenticação/perfis), RNF02 (OWASP e proteção de
dados), RNF03 (hospedagem, portabilidade e desempenho) e RNF04 (acessibilidade).

## Arquitetura

Monólito em camadas com MVC na apresentação e Repository na persistência:

1. **Apresentação** — Django Templates + HTMX.
2. **Serviços** — regras de negócio (duplicidade, estoque, entrega).
3. **Domínio** — modelos Família, Item, Doador, Doação, Entrega e Usuário.
4. **Persistência** — repositórios (IndexedDB local e API remota).
5. **Infraestrutura** — *service worker* (Workbox) e fila de sincronização.

## Tecnologias

- Python 3.12+ e Django 5.2 LTS
- Django REST Framework (endpoint de sincronização)
- PostgreSQL 16 (produção) / SQLite (desenvolvimento e testes)
- HTMX, Workbox e IndexedDB (PWA offline)
- pytest, pytest-django e Ruff
- GitHub Actions (CI)

## Como executar localmente

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env        # ajuste as variáveis
python manage.py migrate
python manage.py runserver
```

Acesse http://127.0.0.1:8000/ — a rota `/health/` responde `{"status": "ok"}`.

## Testes e qualidade

```bash
ruff check .
ruff format --check .
python manage.py check
pytest
```

O CI executa os mesmos passos em cada push e Pull Request.

## Fluxo de versionamento

- `main` protegida; mudanças entram por Pull Request.
- Branches: `feat/...`, `fix/...`, `docs/...`, `test/...`.
- Commits no padrão Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`).
- PR com descrição, checklist e CI verde antes do merge.

## Protótipo

As três telas do protótipo e as capturas estão em
[`docs/prototipo/`](docs/prototipo/). Para visualizar:

```bash
xdg-open docs/prototipo/prototipo-sementes.html   # ou abra no navegador
```

Modos de captura: `?only=tela1`, `?only=tela2`, `?only=tela3`.

## Estrutura

```
config/            configuração do projeto Django
core/              app base (health check)
docs/prototipo/    protótipo navegável e capturas
tests/             testes automatizados
.github/workflows/ pipeline de CI
```

## Licença

Projeto acadêmico, sem fins comerciais.
