#!/bin/sh

service postgresql start
service redis-server start

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

/usr/local/bin/node_exporter >/dev/null 2>&1 &
/usr/local/bin/redis_exporter >/dev/null 2>&1 &
/usr/local/bin/postgres_exporter >/dev/null 2>&1 &

sphinx-apidoc --remove-old --output-dir /hidden/docs/autodoc /hidden/app
make -C /hidden/docs html

uvicorn app.app:app --host ${UVICORN_HOST} --port ${UVICORN_PORT} --workers ${UVICORN_WORKERS}
