#!/bin/sh
service postgresql start
service redis-server start
/usr/local/bin/node_exporter >/dev/null 2>&1 &
/usr/local/bin/redis_exporter >/dev/null 2>&1 &
/usr/local/bin/postgres_exporter >/dev/null 2>&1 &

# Check if the PostgreSQL user exists, if not, create it
USER_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='${POSTGRES_USERNAME}'")
if [ "$USER_EXISTS" != "1" ]; then
  sudo -u postgres psql -c "CREATE USER ${POSTGRES_USERNAME} WITH PASSWORD '${POSTGRES_PASSWORD}';"
fi

# Check if the PostgreSQL database exists, if not, create it
DB_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='${POSTGRES_DATABASE}'")
if [ "$DB_EXISTS" != "1" ]; then
  sudo -u postgres psql -c "CREATE DATABASE ${POSTGRES_DATABASE};"
fi

uvicorn app.app:app --host ${UVICORN_HOST} --port ${UVICORN_PORT} --workers ${UVICORN_WORKERS}
