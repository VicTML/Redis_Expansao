# Redis API

API em FastAPI com Redis: Cache, Fila e Rate Limiting.

## 📋 Estrutura

```
redis/
├── src/
│   ├── api/
│   │   ├── main.py          # FastAPI app
│   │   ├── routes.py        # Endpoints
│   │   ├── dependencies.py  # Cache, Queue, RateLimiter
│   │   └── models.py        # Schemas Pydantic
│   └── worker/
│       └── processor.py     # Worker background
├── tests/
│   └── test_api.py          # Testes
├── config.py                # Configurações
├── requirements.txt         # Dependências
├── Dockerfile               # Imagem
├── docker-compose.yml       # Orquestração
└── README.md
```

## 🚀 Quick Start

### Pré-requisitos
- Docker & Docker Compose

### Executar

```bash
# Instale dependências
pip install -r requirements.txt

# Suba containers
docker-compose up

# Em outro terminal, inicie o worker
python -m src.worker.processor

# Acesse a API
open http://localhost:8000/docs
```

## 🔧 Funcionalidades

### 1. Cache (GET /cache/{key})

**Primeira requisição (MISS):**
```bash
curl -i http://localhost:8000/data
# X-Cache: MISS (demora ~200ms)
```

**Segunda requisição (HIT):**
```bash
curl -i http://localhost:8000/data
# X-Cache: HIT (instantâneo, TTL: 30s)
```

**Set manualmente:**
```bash
curl -X POST http://localhost:8000/cache \
  -H "Content-Type: application/json" \
  -d '{"key": "user:1", "value": {"name": "João"}}'
```

### 2. Fila (POST /job)

**Enfileirar tarefa:**
```bash
curl -X POST "http://localhost:8000/job?task_name=GerarRelatorio"
```

**Status da fila:**
```bash
curl http://localhost:8000/jobs
```

**Processar (worker):**
```bash
python -m src.worker.processor
```

### 3. Rate Limiting

Limite: **5 requisições por 60 segundos** por IP

```bash
# Primeiras 5: OK
for i in {1..5}; do curl http://localhost:8000/health; done

# 6ª em diante: 429
curl http://localhost:8000/health
# {"error": "Too many requests"}
```

**Status:**
```bash
curl http://localhost:8000/status
```

## 🧪 Testes

```bash
pytest tests/ -v
```

## 📊 Conceitos Redis

| Comando | Uso |
|---------|-----|
| `SETEX` | Cache com TTL |
| `GET` | Recuperar cache |
| `LPUSH` | Enfileirar |
| `BRPOP` | Consumir (bloqueante) |
| `INCR` | Rate limit |
| `EXPIRE` | TTL em counter |

## 🌐 Endpoints

- `GET /` - Info
- `GET /health` - Health check
- `GET /data` - Cache demo
- `GET /cache/{key}` - Get cache
- `POST /cache` - Set cache
- `POST /job?task_name=...` - Enfileirar
- `GET /jobs` - Status fila
- `GET /status` - Rate limit status
- `GET /docs` - Swagger UI

## 🐳 Docker

```bash
# Build
docker-compose build

# Up
docker-compose up

# Down
docker-compose down

# Logs
docker-compose logs -f api
```

## 📝 Variáveis de Ambiente

Crie `.env`:
```env
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
```

## 🤝 Contribuindo

1. Fork
2. Crie branch: `git checkout -b feature`
3. Commit: `git commit -m "descricao"`
4. Push: `git push origin feature`
5. PR

## 📄 Licença

MIT
