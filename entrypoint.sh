#!/bin/sh

service postgresql start
service redis-server start

/usr/local/bin/node_exporter >/dev/null 2>&1 &
/usr/local/bin/redis_exporter >/dev/null 2>&1 &
/usr/local/bin/postgres_exporter >/dev/null 2>&1 &

DB_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='${POSTGRES_DATABASE}'")
if [ "$DB_EXISTS" != "1" ]; then
  sudo -u postgres psql -c "CREATE DATABASE ${POSTGRES_DATABASE};"
fi

USER_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='${POSTGRES_USERNAME}'")
if [ "$USER_EXISTS" != "1" ]; then
  sudo -u postgres psql -c "CREATE USER ${POSTGRES_USERNAME} WITH PASSWORD '${POSTGRES_PASSWORD}';"
  sudo -u postgres psql -c "GRANT ALL ON DATABASE ${POSTGRES_DATABASE} TO ${POSTGRES_USERNAME};"
  sudo -u postgres psql -c "ALTER DATABASE ${POSTGRES_DATABASE} OWNER TO ${POSTGRES_USERNAME};"
fi

if [ ! -f /hidden/secret.key ]; then
  tr -dc "A-Za-z0-9" < /dev/urandom | head -c 80 > /hidden/secret.key
fi

if [ ! -f /hidden/serial.py ]; then
  echo "__serial__ = \"$(tr -dc 'A-Z0-9' < /dev/urandom | head -c 20)\"" > /hidden/serial.py
fi

uvicorn app.app:app --host ${UVICORN_HOST} --port ${UVICORN_PORT} --workers ${UVICORN_WORKERS}
