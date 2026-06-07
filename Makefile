.PHONY: install audit passphrase

PORT ?= 80

# NOTE (ADR-02): Application runs inside a Docker container.
# 1. Packages all dependencies and runtime environment, ensuring
#    consistent behavior across different hosts.
# 2. Isolates encryption runtime and secret handling from the host,
#    reducing the risk of accidental exposure or interference.
# 3. Keeps the decrypted filesystem mountpoint internal to the container
#    by default, limiting direct host access.

# NOTE (ADR-03): Cipherdir and secrets are stored in Docker volumes.
# 1. The secrets volume allows the encrypted passphrase to be removed
#    at runtime; its absence is detected by the watchdog, which triggers
#    automatic unmount of the gocryptfs mountpoint.
# 2. The cipherdir volume keeps encrypted data portable, enabling backup,
#    migration between instances, and emergency recovery using gocryptfs
#    without the application.

install:
	docker build -t hidden .
	docker run -dit \
	--init \
	--restart unless-stopped \
	--cap-add SYS_ADMIN \
	--device /dev/fuse \
	--security-opt apparmor:unconfined \
	-p $(PORT):80 \
	-v hidden-cipherdir:/var/lib/hidden/cipherdir \
	-v hidden-secrets:/media/secrets \
	--name hidden \
	hidden

develop:
	docker exec hidden sh -c "apt-get update && apt-get install -y --no-install-recommends git openssh-client"
	docker exec hidden mkdir -p /root/.ssh
	docker cp "$$HOME/.ssh/." hidden:/root/.ssh
	docker exec hidden sh -c "\
	chmod 700 /root/.ssh && \
	find /root/.ssh -type f -exec chmod 600 {} \; && \
	find /root/.ssh -name '*.pub' -type f -exec chmod 644 {} \; \
	"

passphrase:
	docker exec -it hidden python3 -m app.runtime.passphrase

audit:
	docker exec hidden python3 -m pip install --quiet bandit pip-audit
	docker exec hidden python3 -m pip_audit -r requirements.txt
	docker exec hidden python3 -m bandit -r app -x tests -lll

	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
		aquasec/trivy image --scanners vuln --severity HIGH,CRITICAL hidden
