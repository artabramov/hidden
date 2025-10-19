include .env
export

install:
	docker build --no-cache -t hidden .
	docker run -dit --restart unless-stopped --cap-add SYS_ADMIN --device /dev/fuse --security-opt apparmor:unconfined -p 80:80 -p 9100:9100 -v hidden-data:/encrypted/data -v hidden-secrets:/mnt/secrets -v hidden-logs:/var/log/hidden --name hidden --env-file .env hidden

scan:
	@docker exec hidden sh -c 'pip3 install -U pip-audit bandit'
	@echo "Scanning..."
	@docker exec hidden sh -c 'date -u "+_Last updated: %Y-%m-%d %H:%M:%S UTC_" > /hidden/SECURITY_SCAN.md'
	@docker exec hidden sh -c 'printf "\n\n## pip-audit\n\n" >> /hidden/SECURITY_SCAN.md'
	@docker exec hidden sh -c 'pip-audit -r /hidden/requirements.txt >> /hidden/SECURITY_SCAN.md || true'
	@docker exec hidden sh -c 'printf "\n\n## bandit\n\n" >> /hidden/SECURITY_SCAN.md'
	@docker exec hidden sh -c 'bandit -r /hidden --exclude /hidden/tests >> /hidden/SECURITY_SCAN.md || true'
	@echo "SECURITY_SCAN.md is updated"

documentation:
	@docker exec hidden sh -c 'pip3 install -U --no-cache-dir sphinx sphinx-markdown-builder'
	@echo "Generating API stubs..."
	@docker exec hidden sh -c 'mkdir -p /hidden/docs/api && sphinx-apidoc -o /hidden/docs/api /hidden/app /hidden/app/tests'
	@echo "Building Markdown..."
	@docker exec hidden sh -c 'rm -rf /hidden/docs/_build/md && mkdir -p /hidden/docs/_build/md'
	@docker exec hidden sh -c 'sphinx-build -b markdown /hidden/docs /hidden/docs/_build/md'
	@echo "Copying to app/docs/md..."
	@docker exec hidden sh -c 'rm -rf /hidden/docs/md && mkdir -p /hidden/docs/md'
	@docker exec hidden sh -c 'cp -r /hidden/docs/_build/md/* /hidden/docs/md/'
	@echo "Docs ready at /hidden/docs/md"
