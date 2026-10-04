# Higiene Ocupacional MVP

Aplicação web para cálculo e avaliação de agentes ambientais com foco em:
- ruído
- vibração
- calor
- substâncias químicas
- comparação com referências normativas (ACGIH, NR-15 e Linarch)

## Visão geral

Este repositório contém um MVP funcional com:
- backend em FastAPI
- frontend em React + TypeScript
- banco SQLite para uso local em desenvolvimento
- cálculos iniciais de ruído, vibração, calor e químicos
- relatórios em tela com comparação de limites

## Estrutura

- `backend/` — API FastAPI
- `frontend/` — aplicação web em React
- `README.md` — documentação

## Tecnologias

- Python 3.11+
- FastAPI
- React
- TypeScript
- Vite
- SQLite (MVP)

## Como executar

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

A aplicação web fica disponível em:
- http://localhost:5173

A API fica disponível em:
- http://localhost:8000

## Endpoints principais

- `GET /health`
- `GET /api/norms`
- `POST /api/noise/calculate`
- `POST /api/chemicals/calculate`
- `POST /api/vibration/calculate`
- `POST /api/heat/calculate`

## Observação

Este projeto é um suporte para cálculo e análise técnica. A interpretação final e a decisão técnica devem ser conduzidas por profissional habilitado, conforme as normas vigentes e a legislação aplicável.

## Próximos passos recomendados

- cadastro de empresas/locais/funcionários
- persistência com PostgreSQL
- autenticação
- geração de laudos PDF/Excel
- módulos específicos de NR-15 e anexos
- gestão de substâncias com base normativa configurável
