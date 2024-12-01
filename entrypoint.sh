#!/bin/sh
service postgresql start
service redis-server start
sleep 5

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

psql -U postgres -c "
  DO \$\$
  BEGIN
      IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole') THEN
          CREATE TYPE userrole AS ENUM ('reader', 'writer', 'editor', 'admin');
      END IF;
  END \$\$;
"

/usr/local/bin/node_exporter >/dev/null 2>&1 &
/usr/local/bin/redis_exporter >/dev/null 2>&1 &
/usr/local/bin/postgres_exporter >/dev/null 2>&1 &

uvicorn app.app:app --host ${UVICORN_HOST} --port ${UVICORN_PORT} --workers ${UVICORN_WORKERS}
