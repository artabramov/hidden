#!/bin/sh
service postgresql start
service redis-server start
/usr/local/bin/node_exporter >/dev/null 2>&1 &
/usr/local/bin/redis_exporter >/dev/null 2>&1 &
/usr/local/bin/postgres_exporter >/dev/null 2>&1 &
uvicorn app.app:app --host 0.0.0.0 --port 80 --workers 4
