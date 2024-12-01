#!/bin/sh

until pg_isready -h localhost -U ${POSTGRES_USERNAME}; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

service postgresql start
service redis-server start

/usr/local/bin/node_exporter >/dev/null 2>&1 &
/usr/local/bin/redis_exporter >/dev/null 2>&1 &
/usr/local/bin/postgres_exporter >/dev/null 2>&1 &

USER_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='${POSTGRES_USERNAME}'")
if [ "$USER_EXISTS" != "1" ]; then
  sudo -u postgres psql -c "CREATE USER ${POSTGRES_USERNAME} WITH PASSWORD '${POSTGRES_PASSWORD}';"
fi

DB_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='${POSTGRES_DATABASE}'")
if [ "$DB_EXISTS" != "1" ]; then
  sudo -u postgres psql -c "CREATE DATABASE ${POSTGRES_DATABASE};"
fi

sudo -u postgres psql -c "
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole') THEN
        CREATE TYPE userrole AS ENUM ('reader', 'writer', 'editor', 'admin');
    END IF;
END \$\$;
"

uvicorn app.app:app --host ${UVICORN_HOST} --port ${UVICORN_PORT} --workers ${UVICORN_WORKERS}
tail -f /dev/null
