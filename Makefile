include .env
export

configure_hidden:
	docker exec hidden /bin/sh -c "echo \"listen_addresses = '*'\" >> /etc/postgresql/14/main/postgresql.conf"
	docker exec hidden /bin/sh -c "sudo sed -i \"/^# IPv4 local connections:/a \host hidden hidden 0.0.0.0/0 md5\" /etc/postgresql/14/main/pg_hba.conf"
	docker exec hidden /bin/sh -c "sudo sed -i \"/^# IPv4 local connections:/a \host hidden hidden 127.0.0.1/32 trust\" /etc/postgresql/14/main/pg_hba.conf"
	
	docker exec hidden /bin/sh -c "echo \"bind 0.0.0.0\" >> /etc/redis/redis.conf"

install:
	docker build --no-cache -t hidden .
	docker run -dit -p 80:80 --name hidden --env-file .env hidden

	$(MAKE) configure_hidden
	docker restart hidden

develop:
	docker build --no-cache -t hidden .
	docker-compose --env-file .env up -d

	$(MAKE) configure_hidden
	docker-compose restart hidden
