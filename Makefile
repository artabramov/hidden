include .env
export

install:
	docker build --no-cache -t hidden .
	docker run -dit --cap-add SYS_ADMIN --device /dev/fuse --security-opt apparmor:unconfined -p 80:80 -p 9100:9100 -v hidden-data:/encrypted/data -v hidden-secret:/hidden/secret -v hidden-logs:/var/log/hidden --name hidden --env-file .env hidden
	docker restart hidden
