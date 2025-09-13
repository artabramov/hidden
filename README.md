![Designed to be hidden](hidden.png)

A small, asynchronous, security-minded file storage backend built with FastAPI. It encrypts all data at rest (DB fields and files), supports multi-user access, and secures everything with a secret key; it keeps all data local unless explicit consent is given and provides secure, irreversible deletion.

[![License](https://img.shields.io/badge/License-Non--Commercial-c0392b)](https://github.com/artabramov/hidden/blob/master/LICENSE)
[![Website](https://img.shields.io/badge/Website-joinhidden.com-2ea44f)](https://joinhidden.com)
[![Telegram](https://img.shields.io/badge/Telegram-@hiddenupdates-2CA5E0?logoColor=white)](https://t.me/hiddenupdates)

If you like it, star it ⭐ — it helps discoverability.  

## Threat model

The primary threat this app is designed to mitigate is the **loss of the device** running the application. In such a scenario, an attacker may gain full access to the filesystem and the database, including all encrypted files and metadata — but **not the secret key**.

Without the secret encryption key, recovering any meaningful information is computationally infeasible. All user data is encrypted and fragmented, and cannot be extracted from a disk dump. Even with complete physical control over the storage, the attacker only obtains meaningless encrypted blobs.

## Highlights

- **Isolated workspace** — may run fully offline, without requiring an internet connection; no implicit network traffic, no statistics collection.
- **Protected storage** — all persistent data (database fields and files) is encrypted with `AES-256`; each file is fragmented into shards, and access to the storage is controlled by a secret key, which acts as the single point of trust.
- **Extractable secret key** — stored as a file that can be exported and backed up; losing it makes the data permanently inaccessible.
- **Irreversible deletion** — file removal relies on the `shred` utility, which overwrites file data multiple times. It is recommended to avoid using SSDs and copy-on-write filesystems (e.g. btrfs, ZFS).
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
- **Cryptography** — encryption  
- **shred** — secure file deletion  
- **PostgreSQL** — database  
- **Redis** — cache  
- **unittest** — testing  
- **Sphinx** — documentation  
- **flake8** — linting  
- **safety** — dependency security checks 


## Quick start (Docker)

Pull the latest image:
```bash
docker pull artabramov/hidden
```

Run the app:
```bash
docker run -dit -p 80:80 artabramov/hidden
```

On first start, the container will generate a random **secret key** and a **serial number**. These files will be created in the `/hidden` directory inside the container. By default, the secret key is stored at `/hidden/secret.key`. You can override this path by setting the `SECRET_KEY_PATH` environment variable and restart the container.

## UI & documentation
The web client is a **single-page application** built with **React** and **Bootstrap**. Its sources are **not** included in this repository. A pre-built JavaScript bundle is shipped with the backend container, already compiled and ready to use.


Web client (UI):
```bash
http://localhost
```

Public API (Swagger/OpenAPI):
```bash
http://localhost/docs
```

Backend documentation (Sphinx):
```bash
http://localhost/sphinx/
```

## Development

Thanks for your interest in improving **Hidden**!

To set up the development environment, clone the repository and run `make install`, which will build the Docker image and install all dependencies. The container also includes a `.vscode` directory with IDE settings and launch parameters for running the app in debug mode.

Please **do not** open public issues for vulnerabilities. Use GitHub's "Report a vulnerability" (Security Advisories) or contact the maintainer privately. Include steps to reproduce and a clear impact assessment.

Please note that the project is provided as **source-available** under a **non-commercial** license. By contributing, you agree that your contributions are licensed under the same terms. The author reserves the right to change the license or relicense the project in the future.
