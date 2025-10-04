#!/bin/sh
set -eu
umask 077

# Directories for the passphrase file and data paths.
GOCRYPTFS_PASSPHRASE_DIR="$(dirname -- "$GOCRYPTFS_PASSPHRASE_PATH")"
mkdir -p -- "$GOCRYPTFS_PASSPHRASE_DIR"

# Normalize and ensure mountpoint (cleartext view).
GOCRYPTFS_DATA_MOUNTPOINT="${GOCRYPTFS_DATA_MOUNTPOINT%/}"
mkdir -p "$GOCRYPTFS_DATA_MOUNTPOINT"

# Normalize and ensure cipher dir (encrypted store).
GOCRYPTFS_DATA_CIPHER_DIR="${GOCRYPTFS_DATA_CIPHER_DIR%/}"
mkdir -p -- "$GOCRYPTFS_DATA_CIPHER_DIR"

# How often the watchdog checks passphrase presence / mount state.
GOCRYPTFS_WATCHDOG_INTERVAL_SECONDS="${GOCRYPTFS_WATCHDOG_INTERVAL_SECONDS:-2}"

# First boot: generate passphrase once if nothing exists yet
if [ ! -f "$GOCRYPTFS_PASSPHRASE_PATH" ] && [ ! -f "$GOCRYPTFS_DATA_CIPHER_DIR/gocryptfs.conf" ] && ! mountpoint -q "$GOCRYPTFS_DATA_MOUNTPOINT"; then
  tr -dc 'A-Za-z0-9' </dev/urandom | head -c "$GOCRYPTFS_PASSPHRASE_LENGTH" > "$GOCRYPTFS_PASSPHRASE_PATH"
  chmod 600 "$GOCRYPTFS_PASSPHRASE_PATH"
  echo "gocryptfs key generated: $GOCRYPTFS_PASSPHRASE_PATH"
fi

# Watchdog: hot init/mount on passphrase presence, unmount on absence
(
  while :; do
    if [ -f "$GOCRYPTFS_PASSPHRASE_PATH" ]; then
      # Initialize cipher once when the passphrase is present (idempotent).
      if ! find "$GOCRYPTFS_DATA_CIPHER_DIR" -mindepth 1 -maxdepth 1 -print -quit | grep -q .; then
        if gocryptfs -init -passfile "$GOCRYPTFS_PASSPHRASE_PATH" "$GOCRYPTFS_DATA_CIPHER_DIR" -nosyslog; then
          echo "[watchdog] cipher initialized"
        else
          echo "[watchdog] cipher init FAILED"
        fi
      fi

      # Mount when not mounted and the directory is empty (ignoring .fuse_hidden* files).
      if [ -f "$GOCRYPTFS_DATA_CIPHER_DIR/gocryptfs.conf" ] && ! mountpoint -q "$GOCRYPTFS_DATA_MOUNTPOINT"; then
        if ! find "$GOCRYPTFS_DATA_MOUNTPOINT" -mindepth 1 -maxdepth 1 ! -name '.fuse_hidden*' -print -quit | grep -q .; then
          rm -f "$GOCRYPTFS_DATA_MOUNTPOINT"/.fuse_hidden* 2>/dev/null || true
          if gocryptfs -passfile "$GOCRYPTFS_PASSPHRASE_PATH" "$GOCRYPTFS_DATA_CIPHER_DIR" "$GOCRYPTFS_DATA_MOUNTPOINT" -nosyslog; then
            echo "[watchdog] mounted: $GOCRYPTFS_DATA_MOUNTPOINT"
          fi
        fi
      fi
    else
      # Passphrase missing: unmount if currently mounted (idempotent).
      if mountpoint -q "$GOCRYPTFS_DATA_MOUNTPOINT"; then
        if fusermount -u "$GOCRYPTFS_DATA_MOUNTPOINT" 2>/dev/null || \
           fusermount -uz "$GOCRYPTFS_DATA_MOUNTPOINT" 2>/dev/null || \
           umount "$GOCRYPTFS_DATA_MOUNTPOINT" 2>/dev/null || \
           gocryptfs -q -u "$GOCRYPTFS_DATA_MOUNTPOINT" 2>/dev/null; then
          echo "[watchdog] unmounted: $GOCRYPTFS_DATA_MOUNTPOINT"
        fi
      fi
    fi
    sleep "$GOCRYPTFS_WATCHDOG_INTERVAL_SECONDS"
  done
) &

# Other services.
service redis-server start
/usr/local/bin/node_exporter >/dev/null 2>&1 &

# Make uvicorn PID 1 so it receives signals directly.
exec uvicorn app.app:app --host "${UVICORN_HOST}" --port "${UVICORN_PORT}" --workers "${UVICORN_WORKERS}"
