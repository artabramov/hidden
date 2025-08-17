include .env
export

install:
	docker build --no-cache -t hidden .
	docker run -dit -p 80:80 -p 5432:5432 -p 6379:6379 -p 9100:9100 -p 9187:9187 -p 9121:9121 -v hidden-appdata:/hidden/data -v hidden-pgdata:/var/lib/postgresql -v hidden-logs:/var/log/hidden --name hidden --env-file .env hidden

	docker exec hidden /bin/sh -c "echo \"listen_addresses = '*'\" >> /etc/postgresql/16/main/postgresql.conf"
	docker exec hidden /bin/sh -c "sudo sed -i \"/^# IPv4 local connections:/a \host hidden hidden 0.0.0.0/0 md5\" /etc/postgresql/16/main/pg_hba.conf"
	docker exec hidden /bin/sh -c "sudo sed -i \"/^# IPv4 local connections:/a \host hidden hidden 127.0.0.1/32 trust\" /etc/postgresql/16/main/pg_hba.conf"
	docker exec hidden /bin/sh -c "echo \"bind 0.0.0.0\" >> /etc/redis/redis.conf"

	docker restart hidden
	@sleep 20


