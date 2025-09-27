# Hidden — REST over gocryptfs

![Designed to be hidden](img/hidden.png)

A small, fast, async, self-hosted, security-minded file-storage service built with `FastAPI`, `SQLAlchemy`, `SQLite`, and `Redis`. Internally, all data is stored in a `gocryptfs`-encrypted directory (cipher) and protected by a detachable secret key (gocryptfs passphrase). Externally, a clean `REST API` provides filesystem-like operations (upload, move, rename) and organizes files into collections. Supports file metadata, tags, and thumbnails. Versioning is built in — past file states are available as revisions. Deletion uses `shred` to securely erase files and all their revisions. A microkernel design allows hook-based `add-ons` to extend functionality without modifying the core.

Source data can be imported through the API using a console utility. The encrypted data isn’t bound to the application — it’s exposed as a `Docker` volume and can be mounted directly with `gocryptfs` when the secret key is available.

Supports multi-user access with role-based permissions (RBAC) and multi-factor authentication (MFA).

[![release](https://img.shields.io/github/v/tag/artabramov/hidden?sort=semver&label=release&color=2f81f7)](https://github.com/artabramov/hidden/blob/master/CHANGELOG.md)
![vulnerability scan](https://img.shields.io/badge/vulnerability%20scan-2025--09--21-2f81f7)
![test coverage](https://img.shields.io/badge/test%20coverage-81%25-2f81f7)
[![license](https://img.shields.io/badge/license-Non--Commercial-2f81f7)](https://github.com/artabramov/hidden/blob/master/LICENSE)

If you like it, star it ⭐ — it helps discoverability. Thank you!

## Quick links

- Official website: [joinhidden.com](https://joinhidden.com)
- Telegram announcements: [t.me/hiddenupdates](https://t.me/hiddenupdates)

## Threat model

The app is designed for data protection in local workflows: **all data stays within the environment** — suitable for personal use and co-located teams.

It is engineered to withstand **full compromise of the host** (filesystem and database) **without compromise of the secret key**. In that scenario, an attacker may read all on-disk files and metadata but **cannot recover original data** (assumed that the secret key is stored securely outside the app).

Without the secret key, deriving any meaningful information is **computationally infeasible**: all user data is encrypted at rest, so even with complete physical control over the storage an attacker obtains only unintelligible ciphertext blobs.

When deleted, files are securely wiped with shred (with all revisions and thumbnails). **After deletion, recovery is impossible, even if the secret key is later compromised**.

- Read more about gocryptfs: [github.com/rfjakob/gocryptfs](https://github.com/rfjakob/gocryptfs)
- Read more about shred: [en.wikipedia.org/wiki/Shred_(Unix)](https://en.wikipedia.org/wiki/Shred_(Unix))

## Caution

- **Losing the secret key permanently locks all encrypted data without the possibility of recovery**. Store the key in a secure, reliable location. Do not keep it in the same place as the application. Do not share the key with anyone.
- **On SSDs and copy-on-write/journaling filesystems, shred is ineffective** (wear-leveling and CoW defeat multi-pass overwrites). Use non-CoW filesystems and avoid snapshots.

## Highlights

- **Self-hosted mode** — containerized with Docker, so it works on any hardware and operating system where a container runtime is available.
- **Isolated workspace** — fully offline; no internet required. No external services, no background network traffic, no analytics, no AI.
- **Protected storage** — everything is encrypted, and access is controlled by a secret key that serves as the single point of trust.
- **Detachable secret key** — an external key file (gocryptfs passphrase) that can be extracted and stored separately.
- **App-agnostic volume** — the encrypted store is exposed as a Docker volume; with the secret key, it can be mounted directly via gocryptfs or migrated to another instance of the application.
- **Irreversible deletion** — securely erases files by overwriting data multiple times to prevent recovery.
- **Head-based versioning** — the newest file revision is the head, any previous revision can be listed and restored.
- **Rich file features** — supports file metadata, tags, description, and automatic thumbnail generation.
- **Role-based access** — user permissions are managed through the predefined `Reader`, `Author`, `Editor` and `Admin` roles.
- **Multi-factor auth** — login sessions are protected with one-time passwords, adding a layer of defense against credential theft.
- **Public API** — the `REST API` is fully documented with `Swagger/OpenAPI` documentation.
- **Backend documentation** — detailed developer docs are generated with `Sphinx`, covering architecture, internals, and extension points. 
- **Add-on friendly** — the core follows a microkernel design with a hook-based extension system, making it easy to add new features without modifying the main codebase.
- **Import CLI** — source data can be ingested through a console utility for bulk or scripted imports.

## Main stack

- **Python** `3.13` — core runtime
- **FastAPI** `0.115.12` — framework
- **Pydantic** `2.11.7` — validation
- **SQLite** `3.45.1` — database
- **Redis** `7.0.15` — cache
- **gocryptfs** `2.4.0` — encrypted FS layer
- **shred** `9.4` — secure file erasure

## Security

- **pip-audit** —
- **semgrep** —
- **bandit** —
- **gitleaks** —
- **trivy** —

## Quick start

Build and run with Docker:
```bash
make install
```

On first launch, a random secret key is generated and stored in a file in the `hidden-secret` Docker volume, from which it can be extracted. Encrypted data is stored in the `hidden-data` Docker volume; logs are in `hidden-logs`.

Public API:
```bash
http://localhost/docs
```

Documentation:
```bash
http://localhost/sphinx/
```

## Import data

## Development

Thanks for your interest in improving **Hidden**!

To set up the development environment, clone the repository and run `make install`, which will build the Docker image and install all dependencies. The container also includes a `.vscode` directory with IDE settings and launch parameters for running the app in debug mode.

Please **do not** open public issues for vulnerabilities. Use GitHub's "Report a vulnerability" (Security Advisories) or contact the maintainer privately. Include steps to reproduce and a clear impact assessment.

Please note that the project is provided as **source-available** under a **non-commercial** license. By contributing, you agree that your contributions are licensed under the same terms. The author reserves the right to change the license or relicense the project in the future.
