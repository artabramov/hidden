FROM python:3.12-slim
WORKDIR /opt/hidden

# NOTE (ADR-04): gocryptfs is used for filesystem-level encryption.
# The choice is driven by a constrained design space:
# 1. Encryption must cover all sensitive data including the metadata DB;
#    doing it at the application or DB layer was rejected because:
#    A. Search, sort, LIKE, and ORDER BY over encrypted columns become
#       impossible without leaking properties (deterministic encryption
#       reveals frequency; order-preserving encryption has known crypto
#       weaknesses; blind indexes need ad-hoc per-query design).
#    B. Filenames, keys, and partial-encryption edge cases require
#       ad-hoc handling with a high probability of subtle leaks.
# 2. Block-level encryption (LUKS, dm-crypt) was rejected because it
#    requires host-level setup or a privileged container, which breaks
#    the "single docker run on any host" deployment goal.
# 3. Within userspace FUSE options, gocryptfs is chosen over EncFS
#    (known weaknesses since the 2014 audit) and over CryFS (slower,
#    less mature, weaker recovery story); CryFS would hide more
#    cipherdir-level metadata but that trade-off does not pay off in
#    the operator-trusted host threat model.
# 4. Accepted trade-off: gocryptfs leaks structural metadata of the
#    cipherdir to anyone with host filesystem access (file count per
#    directory, approximate per-file size, tree shape, FS timestamps).

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    gocryptfs fuse3 libmagic1 \
 && rm -rf /var/lib/apt/lists/*

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["./entrypoint.sh"]
