# DataForge API (Componente Principal)

Componente principal da plataforma **DataForge** — uma solução distribuída de
**análise de qualidade e enriquecimento de dados com IA**.

O usuário envia um conjunto de registros (ex.: vendas com data, produto, CEP e valor).
A plataforma valida a qualidade dos dados, detecta anomalias, enriquece os CEPs com uma
API externa e usa IA para gerar um **resumo executivo em português** — transformando um
arquivo bruto em que ninguém confia num diagnóstico legível em segundos.

Esta API expõe o CRUD de *datasets*, persiste os dados em PostgreSQL e funciona como
**proxy** para o `dataforge-insight-service`, que executa as regras de negócio.

> Arquitetura no padrão **Cenário 2.1**: a API principal (proxy) comunica-se com a API
> secundária, que concentra as regras de negócio e consome o serviço externo.

## Arquitetura

![Arquitetura do DataForge](docs/arquitetura.svg)

```
Cliente → dataforge-api ──REST──> dataforge-insight-service ──REST──> BrasilAPI
              │                              │
         PostgreSQL                     Ollama (IA local)
```

- **dataforge-api** (este repo) — CRUD + proxy + persistência.
- **dataforge-insight-service** ([repo separado](https://github.com/SEU_USUARIO/dataforge-insight-service)) — análise, enriquecimento e IA.
- **BrasilAPI** — serviço externo de CEP.
- **Ollama** — IA local (self-hosted), gratuita.

## Tecnologias

Python 3.12 · FastAPI · SQLAlchemy 2 · PostgreSQL · psycopg 3 · httpx · Docker

## Rotas

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/datasets` | Cria um dataset com seus registros |
| `GET` | `/datasets` | Lista datasets (paginação `skip`/`limit` + filtro `name`) |
| `GET` | `/datasets/{id}` | Detalha um dataset e seus registros |
| `PUT` | `/datasets/{id}` | Atualiza nome/descrição |
| `DELETE` | `/datasets/{id}` | Remove o dataset (e registros em cascata) |
| `GET` | `/datasets/{id}/records` | Lista os registros (paginado) |
| `POST` | `/datasets/{id}/analyze` | Proxy → insight-service; persiste o resultado |
| `GET` | `/datasets/{id}/insights` | Retorna a análise mais recente persistida |

> Os quatro métodos exigidos (POST, PUT, DELETE, GET) estão implementados. Paginação,
> filtro e as rotas de análise/insights são funcionalidades **além do CRUD**.

### Exemplo de uso

```bash
# 1. Criar um dataset (usa o exemplo versionado no repo)
curl -X POST http://localhost:8000/datasets \
  -H "Content-Type: application/json" \
  -d @examples/dataset_exemplo.json

# 2. Analisar (chama o insight-service, roda IA e persiste)
curl -X POST http://localhost:8000/datasets/1/analyze

# 3. Consultar os insights persistidos
curl http://localhost:8000/datasets/1/insights
```

Resposta (resumida) de `/analyze` e `/insights`:

```json
{
  "dataset_id": 1,
  "analysis_id": 1,
  "created_at": "2026-03-10T12:00:00Z",
  "result": {
    "quality": {"total": 5, "ausentes": {"cep": 1}, "invalidos": {"valor": 1},
                "duplicatas": 1, "linhas_limpas": 2},
    "statistics": {"valor": {"media": 1959.2, "mediana": 3299.0},
                   "por_regiao": {"Sudeste": 3, "Sul": 1}},
    "anomalies": [{"linha": 4, "campo": "valor", "motivo": "valor negativo (-150.0)"}],
    "data_quality_score": 0.4,
    "summary": "O conjunto tem 5 registros, dos quais 2 estão totalmente limpos..."
  }
}
```

## API externa utilizada

- **Nome:** BrasilAPI — módulo de CEP
- **Endpoint:** `https://brasilapi.com.br/api/cep/v2/{cep}`
- **Licença:** projeto open source (MIT), uso público e **gratuito**.
- **Cadastro / API key:** não é necessário.
- **Rotas consumidas:** `GET /api/cep/v2/{cep}` (retorna cidade e estado do CEP).
- **Como é usada:** o `insight-service` consulta cada CEP dos registros, deriva a região a
  partir da UF e agrega a distribuição regional. Os dados são **consumidos e tratados
  internamente** — não há redirecionamento do usuário.

## Como executar (Docker Compose)

### Pré-requisitos
- Docker e Docker Compose.
- Os **dois repositórios clonados lado a lado**:
  ```
  pasta-mae/
  ├── dataforge-api/                (este repositório)
  └── dataforge-insight-service/
  ```

### Passos
```bash
# 1. Subir toda a stack (api, insight-service, postgres, ollama)
docker compose up --build

# 2. Baixar o modelo de IA (uma única vez)
docker exec -it $(docker compose ps -q ollama) ollama pull llama3.2:3b
```

Serviços:
- API principal → http://localhost:8000/docs
- Insight service → http://localhost:8001/docs

## Configuração

| Variável | Descrição | Padrão |
|---|---|---|
| `DATABASE_URL` | Conexão do PostgreSQL | `postgresql+psycopg://postgres:dataforge@postgres:5432/dataforge` |
| `INSIGHT_URL` | URL base do insight-service | `http://insight-service:8000` |

## Testes

```bash
pip install -r requirements.txt pytest
pytest
```

## Estrutura

```
dataforge-api/
├── Dockerfile
├── docker-compose.yml          # orquestra os 4 serviços
├── examples/dataset_exemplo.json
├── docs/arquitetura.svg
├── app/
│   ├── main.py
│   ├── config.py · database.py · models.py · schemas.py
│   ├── routers/datasets.py
│   └── services/insight_client.py
└── tests/
```
