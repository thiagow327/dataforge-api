# DataForge API (Componente Principal)

Componente principal da plataforma **DataForge** — uma solução distribuída de
**análise de qualidade e enriquecimento de dados com IA**.

Esta API expõe o CRUD de *datasets*, persiste os dados em PostgreSQL e funciona como
**proxy** para o `dataforge-insight-service`, que executa as regras de negócio
(estatística, detecção de anomalias, enriquecimento via API externa e interpretação por IA).

> Arquitetura no padrão **Cenário 2.1**: API principal (proxy) → API secundária
> (regras de negócio + serviço externo).

## Arquitetura

```
  dataforge-api (esta) ──REST──> dataforge-insight-service ──REST──> BrasilAPI
        │                                    │
   PostgreSQL                            Ollama (IA local)
```

> _(Fluxograma/imagem da arquitetura será adicionado na Fase 7.)_

## API externa utilizada

- **BrasilAPI** — `https://brasilapi.com.br/api/cep/v2/{cep}`
- Pública, gratuita, sem cadastro e sem API key.
- Usada pelo `insight-service` para enriquecer os CEPs dos registros (cidade/estado;
  a região é derivada da UF). Os dados são consumidos e tratados internamente — não há
  redirecionamento do usuário.

## Tecnologias

Python 3.12 · FastAPI · SQLAlchemy · PostgreSQL · httpx · Docker

## Como executar

### Pré-requisitos
- Docker e Docker Compose instalados.
- Os **dois repositórios clonados lado a lado**:
  ```
  pasta-mae/
  ├── dataforge-api/                (este repositório)
  └── dataforge-insight-service/
  ```

### Subir tudo com Docker Compose
```bash
docker compose up --build
```

Depois, baixe o modelo de IA uma única vez:
```bash
docker exec -it $(docker compose ps -q ollama) ollama pull llama3.2:3b
```

Serviços disponíveis:
- API principal → http://localhost:8000/docs
- Insight service → http://localhost:8001/docs

### Subir só a infraestrutura (Postgres + Ollama)
```bash
docker compose up -d postgres ollama
```

## Configuração

Variáveis de ambiente (ver `.env.example`):

| Variável | Descrição |
|---|---|
| `DATABASE_URL` | String de conexão do PostgreSQL |
| `INSIGHT_URL` | URL base do `dataforge-insight-service` |

## Status

🚧 Em construção — Fase 0 (setup) concluída. Rotas de CRUD e proxy nas próximas fases.
