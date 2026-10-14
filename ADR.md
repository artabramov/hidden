# ADR Registry

This file indexes architecture decisions referenced in code through
`NOTE (ADR-XX)` comments. The source of truth is the code. Use global
search across the project for details.

- ADR-01: Naming and code style conventions follow PEP 8.
- ADR-02: Application runs inside a Docker container.
- ADR-03: gocryptfs is used for filesystem-level encryption.
- ADR-04: gocryptfs passphrase is protected by master password.
- ADR-05: gocryptfs passphrase is provided through tmpfs.
- ADR-06: Cipherdir initialization is a one-time operation.
- ADR-07: Cipherdir and secrets are stored in Docker volumes.
