#!/bin/sh
# Dijalankan sekali saat volume Postgres pertama kali dibuat.
# app_user dipakai FastAPI. Dia BUKAN superuser dan BUKAN pemilik tabel,
# jadi Row-Level Security berlaku penuh untuk dia (lihat ADR 0001).
# Role migrator (POSTGRES_USER) dipakai Alembic dan script seed.
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<EOSQL
CREATE ROLE app_user LOGIN PASSWORD '${APP_DB_PASSWORD}'
  NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
EOSQL
