# Chatbot RAG UMKM

Platform multi-tenant untuk memasang chatbot RAG di website UMKM, dengan dashboard Lead. Arah project dan istilah ada di [Claude.md](Claude.md) dan [GLOSSARY.md](GLOSSARY.md), rencana kerja di [docs/PHASES.md](docs/PHASES.md).

## Menjalankan

```powershell
Copy-Item .env.example .env   # lalu ganti semua nilai "change-me"
docker compose up -d --build
```

| Service | Alamat |
|---|---|
| Dashboard (Next.js) | http://localhost:3000 |
| API (FastAPI) | http://localhost:8000/docs |
| Postgres + pgvector | localhost:5433 |

`docker compose up` menjalankan migrasi Alembic dan seed (Super Admin dan Business "Toko Demo", kredensialnya dari `.env`). Seed idempotent, aman dijalankan berulang.

## Test backend

Butuh database dari compose sedang berjalan (`docker compose up -d db`).

```powershell
cd backend
uv run pytest
```

Test membuat database `chatbot_test` sendiri. Semua assertion isolasi dijalankan sebagai role `app_user` (non-superuser), bukan role owner.
