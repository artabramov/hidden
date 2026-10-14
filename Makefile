.PHONY: install develop

-include .env

FORCE ?= 0
VOLUME_SECRETS ?= /mnt/hidden-secrets

# NOTE (ADR-02): Application runs inside a Docker container.
# 1. Packages all dependencies and runtime environment, ensuring
#    consistent behavior across different hosts.
# 2. Isolates encryption runtime and secret handling from the host,
#    reducing the risk of accidental exposure or interference.
# 3. Keeps the decrypted filesystem mountpoint internal to the container
#    by default, limiting direct host access.

# NOTE (ADR-07): Cipherdir and secrets are stored in Docker volumes.
# 1. The secrets volume allows the encrypted passphrase to be removed
#    at runtime; its absence is detected by the watchdog, which triggers
#    automatic unmount of the gocryptfs mountpoint.
# 2. The cipherdir volume keeps encrypted data portable, enabling backup,
#    migration between instances, and emergency recovery using gocryptfs
#    without the application.

install:
	@if [ "$(FORCE)" != "1" ]; then \
		if ! mountpoint -q "$(VOLUME_SECRETS)" 2>/dev/null; then \
			echo "error: VOLUME_SECRETS is missing or not a mountpoint." >&2; \
			echo "Connect removable media at that path, then retry." >&2; \
			echo "To skip this check: make install FORCE=1" >&2; \
			exit 1; \
		fi; \
	fi
	docker build -t hidden .
	docker run -dit \
	--init \
	--restart unless-stopped \
	--cap-add SYS_ADMIN \
	--device /dev/fuse \
	--security-opt apparmor:unconfined \
	-p $(UVICORN_PORT):$(UVICORN_PORT) \
	-p $(VERSITY_PORT):$(VERSITY_PORT) \
	-p $(VERSITY_WEBGUI_PORT):$(VERSITY_WEBGUI_PORT) \
	-v hidden-cipherdir:$(INSTALL_CIPHERDIR) \
	-v $(VOLUME_SECRETS):$(INSTALL_SECRETS) \
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