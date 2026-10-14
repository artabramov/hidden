FROM python:3.12-slim
WORKDIR /opt/hidden

# NOTE (ADR-03): gocryptfs is used for filesystem-level encryption.
# The choice is driven by the storage architecture and deployment goals:
# 1. Encryption must cover all persistent S3 data and IAM state without
#    depending on encryption provided by the S3 layer or application.
#    Filesystem-level encryption provides a single protection boundary
#    below VersityGW and keeps encryption independent of S3 semantics.
# 2. Block-level encryption (LUKS, dm-crypt) was rejected because it
#    requires host-level setup or a privileged container, which breaks
#    the goal of running the application as a self-contained container.
# 3. A userspace FUSE filesystem allows encryption to remain inside the
#    container while exposing a regular POSIX filesystem to VersityGW.
#    gocryptfs is chosen over EncFS due to known security concerns and
#    over CryFS due to its higher complexity and performance overhead.
# 4. Accepted trade-off: gocryptfs does not hide all filesystem metadata
#    from access to the cipherdir. Approximate file sizes, timestamps,
#    file counts, and aspects of the directory structure may remain
#    observable, while file contents and plaintext names are encrypted.

RUN apt-get update \
 && apt-get install -y --no-install-recommends gocryptfs fuse3 \
 && rm -rf /var/lib/apt/lists/*

RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl \
 && curl -fsSL \
      https://github.com/versity/versitygw/releases/download/v1.8.0/versitygw_1.8.0_linux_amd64.deb \
      -o /tmp/versitygw.deb \
 && apt-get install -y --no-install-recommends /tmp/versitygw.deb \
 && rm -f /tmp/versitygw.deb \
 && rm -rf /var/lib/apt/lists/*

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["./entrypoint.sh"]