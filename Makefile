include .env
export

install:
	docker build --no-cache -t hidden .
	docker-compose --env-file .env up -d

	docker exec hidden /bin/sh -c "echo \"listen_addresses = '*'\" >> /etc/postgresql/14/main/postgresql.conf"
	docker exec hidden /bin/sh -c "sudo sed -i \"/^# IPv4 local connections:/a \host hidden hidden 0.0.0.0/0 md5\" /etc/postgresql/14/main/pg_hba.conf"
	docker exec hidden /bin/sh -c "sudo sed -i \"/^# IPv4 local connections:/a \host hidden hidden 127.0.0.1/32 trust\" /etc/postgresql/14/main/pg_hba.conf"
	docker exec hidden /bin/sh -c "echo \"bind 0.0.0.0\" >> /etc/redis/redis.conf"
	docker-compose restart hidden

	docker exec hidden sudo -u postgres psql -c "CREATE USER $(POSTGRES_USERNAME) WITH PASSWORD '$(POSTGRES_PASSWORD)';"
	docker exec hidden sudo -u postgres psql -c "CREATE DATABASE $(POSTGRES_DATABASE);"
	docker-compose restart hidden
