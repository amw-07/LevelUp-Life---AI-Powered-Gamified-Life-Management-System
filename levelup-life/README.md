# ⚔️ LevelUp Life

AI-Powered Gamified Life Management Platform

## Quick Start

```bash
cp .env.example .env
# Edit .env — add GEMINI_API_KEY and SECRET_KEY:
# openssl rand -hex 32

docker compose up --build

# Initialize database (first run only)
docker compose exec backend alembic upgrade head
```

- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

## Run Tests

```bash
docker compose exec backend pytest --cov=app tests/ -v
docker compose exec frontend npm run test
```
