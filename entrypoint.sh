#!/bin/sh
set -eu
umask 077

# Directories for the passphrase file and data paths.
SECRET_KEY_DIR="$(dirname -- "$SECRET_KEY_PATH")"
mkdir -p -- "$SECRET_KEY_DIR"

# Normalize and ensure mountpoint (cleartext view).
DATA_MOUNTPOINT="${DATA_MOUNTPOINT%/}"
mkdir -p "$DATA_MOUNTPOINT"

# Normalize and ensure cipher dir (encrypted store).
DATA_CIPHER_DIR="${DATA_CIPHER_DIR%/}"
mkdir -p -- "$DATA_CIPHER_DIR"

# How often the watchdog checks passphrase presence / mount state.
SECRET_KEY_WATCHDOG_INTERVAL_SECONDS="${SECRET_KEY_WATCHDOG_INTERVAL_SECONDS:-2}"

# First boot: generate passphrase once if nothing exists yet
if [ ! -f "$SECRET_KEY_PATH" ] && [ ! -f "$DATA_CIPHER_DIR/gocryptfs.conf" ] && ! mountpoint -q "$DATA_MOUNTPOINT"; then
  tr -dc 'A-Za-z0-9' </dev/urandom | head -c "$SECRET_KEY_LENGTH" > "$SECRET_KEY_PATH"
  chmod 600 "$SECRET_KEY_PATH"
  echo "Secret key generated: $SECRET_KEY_PATH"
fi

# Watchdog: hot init/mount on passphrase presence, unmount on absence
(
  while :; do
    if [ -f "$SECRET_KEY_PATH" ]; then
      # Initialize cipher once when the passphrase is present (idempotent).
      if [ ! -f "$DATA_CIPHER_DIR/gocryptfs.conf" ]; then
        if gocryptfs -init -passfile "$SECRET_KEY_PATH" "$DATA_CIPHER_DIR" -nosyslog; then
          echo "[watchdog] cipher initialized"
        fi
      fi

      # Mount when not mounted and the directory is empty (ignoring .fuse_hidden* files).
      if [ -f "$DATA_CIPHER_DIR/gocryptfs.conf" ] && ! mountpoint -q "$DATA_MOUNTPOINT"; then
        if ! find "$DATA_MOUNTPOINT" -mindepth 1 -maxdepth 1 ! -name '.fuse_hidden*' -print -quit | grep -q .; then
          rm -f "$DATA_MOUNTPOINT"/.fuse_hidden* 2>/dev/null || true
          if gocryptfs -passfile "$SECRET_KEY_PATH" "$DATA_CIPHER_DIR" "$DATA_MOUNTPOINT" -nosyslog; then
            echo "[watchdog] mounted: $DATA_MOUNTPOINT"
          fi
        fi
      fi
    else
      # Passphrase missing: unmount if currently mounted (idempotent).
      if mountpoint -q "$DATA_MOUNTPOINT"; then
        if fusermount -u "$DATA_MOUNTPOINT" 2>/dev/null || \
           fusermount -uz "$DATA_MOUNTPOINT" 2>/dev/null || \
           umount "$DATA_MOUNTPOINT" 2>/dev/null || \
           gocryptfs -q -u "$DATA_MOUNTPOINT" 2>/dev/null; then
          echo "[watchdog] unmounted: $DATA_MOUNTPOINT"
        fi
      fi
    fi
    sleep "$SECRET_KEY_WATCHDOG_INTERVAL_SECONDS"
  done
) &

# Other services.
service redis-server start
/usr/local/bin/node_exporter >/dev/null 2>&1 &

# Make uvicorn PID 1 so it receives signals directly.
exec uvicorn app.app:app --host "${UVICORN_HOST}" --port "${UVICORN_PORT}" --workers "${UVICORN_WORKERS}"
