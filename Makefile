include .env
export

.PHONY: install develop

install:
	docker build --no-cache -t hidden .
	docker run -dit -p 80:80 --name hidden --env-file .env hidden
	$(MAKE) update_configs
	docker restart hidden
	$(MAKE) make_pause
	$(MAKE) create_database
	$(MAKE) finish_installation

develop:
	docker build --no-cache -t hidden .
	docker-compose --env-file .env up -d
	$(MAKE) update_configs
	docker-compose restart hidden
	$(MAKE) make_pause
	$(MAKE) create_database
	$(MAKE) finish_installation

update_configs:
	docker exec hidden /bin/sh -c "echo \"listen_addresses = '*'\" >> /etc/postgresql/14/main/postgresql.conf"
	docker exec hidden /bin/sh -c "sudo sed -i \"/^# IPv4 local connections:/a \host hidden hidden 0.0.0.0/0 md5\" /etc/postgresql/14/main/pg_hba.conf"
	docker exec hidden /bin/sh -c "sudo sed -i \"/^# IPv4 local connections:/a \host hidden hidden 127.0.0.1/32 trust\" /etc/postgresql/14/main/pg_hba.conf"
	docker exec hidden /bin/sh -c "echo \"bind 0.0.0.0\" >> /etc/redis/redis.conf"

make_pause:
	@sleep 10
	@echo "Press [Enter] to finish..."
	@read dummy

create_database:
	docker exec hidden sudo -u postgres psql -c "CREATE USER $(POSTGRES_USERNAME) WITH PASSWORD '$(POSTGRES_PASSWORD)';"
	docker exec hidden sudo -u postgres psql -c "CREATE DATABASE $(POSTGRES_DATABASE);"

finish_installation:
	@echo "Installation is finished."
