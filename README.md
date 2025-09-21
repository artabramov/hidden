# Designed to be hidden

![Designed to be hidden](img/hidden.png)

A small, fast, async, security-minded file-storage service built with `FastAPI`, `SQLAlchemy`, `SQLite`, and `Redis`. Internally, all data is stored in a `gocryptfs`-encrypted directory (cipher) and protected by a single secret key. It supports multi-user access with role-based permissions (RBAC) and multi-factor authentication (MFA). A clean `REST API` provides filesystem-like operations (upload, move, rename), organizes files into collections, and manages metadata and thumbnails. Supports versioning; past file states are available as revisions. For secure file erase, it uses the `shred` utility (revisions included). The encrypted directory is exposed as a `Docker` volume and can be mounted directly with `gocryptfs` when the secret key is available.

[![Release](https://img.shields.io/github/v/tag/artabramov/hidden?sort=semver&label=Release&color=2f81f7)](https://github.com/artabramov/hidden/blob/master/CHANGELOG.md)
![Tests](https://img.shields.io/badge/Tests-Passed-2f81f7)
![Coverage](https://img.shields.io/badge/Coverage-54%-2f81f7)
[![License](https://img.shields.io/badge/License-Non--Commercial-2f81f7)](https://github.com/artabramov/hidden/blob/master/LICENSE)

If you like it, star it ⭐ — it helps discoverability.  

## Quick links
- Official website: [joinhidden.com](https://joinhidden.com)
- Telegram announcements: [@hiddenupdates](https://t.me/hiddenupdates)

## Threat model

This app is designed to withstand **full compromise of the host** (filesystem and database) **without compromise of the secret key**. In that scenario, an attacker may read all on-disk files and metadata but **cannot recover original data** (assumed that the secret key is stored securely outside the app).

Without the secret encryption key, deriving any meaningful information is **computationally infeasible**: all user data is encrypted at rest, so even with complete physical control over the storage an attacker obtains only unintelligible ciphertext blobs.

Read more about gocryptfs: [github.com/rfjakob/gocryptfs](https://github.com/rfjakob/gocryptfs)

## Highlights

- **Isolated workspace** — may run fully offline, without requiring an internet connection; no implicit network traffic, no statistics collection.
- **Protected storage** — all persistent data (database and files) is encrypted by `gocryptfs` and access to the storage is controlled by a secret key, which acts as the single point of trust.
- **Extractable secret key** — stored as a file that can be extracted from the app; losing it makes the data permanently inaccessible.
- **Irreversible deletion** — file removal relies on the `shred` utility, which overwrites file data multiple times (ineffective on SSDs or CoW/journaling filesystems).
- **Head-based versioning** — the newest file revision is the head, and any previous revision can be restored.
- **Role-based access** — user permissions are managed through the predefined `Reader`, `Author`, `Editor` and `Admin` roles.
- **Multi-factor auth** — login sessions are protected with one-time passwords, adding a layer of defense against credential theft.
- **Public API** — the `REST API` is fully documented with `Swagger/OpenAPI` documentation.
- **Backend documentation** — detailed developer docs are generated with `Sphinx`, covering architecture, internals, and extension points. 
- **Add-on friendly** — the core follows a microkernel design with a hook-based extension system, making it easy to add new features without modifying the main codebase.  

## Tech stack

- **Python** — core runtime  
- **FastAPI** — web framework  
- **Pydantic** — validation  
- **Asyncio** — concurrency  
- **gocryptfs** — encryption  
- **shred** — secure file deletion  
- **SQLite** — database  
- **Redis** — cache  
- **unittest** — testing  
- **Sphinx** — documentation  
- **flake8** — linting  
- **safety** — dependency security checks 

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

## Development

Thanks for your interest in improving **Hidden**!

To set up the development environment, clone the repository and run `make install`, which will build the Docker image and install all dependencies. The container also includes a `.vscode` directory with IDE settings and launch parameters for running the app in debug mode.

Please **do not** open public issues for vulnerabilities. Use GitHub's "Report a vulnerability" (Security Advisories) or contact the maintainer privately. Include steps to reproduce and a clear impact assessment.

Please note that the project is provided as **source-available** under a **non-commercial** license. By contributing, you agree that your contributions are licensed under the same terms. The author reserves the right to change the license or relicense the project in the future.
