# Designed to be hidden

![Designed to be hidden](hidden.png)


A small, security-minded file storage backend built with FastAPI. It encrypts everything at rest (DB fields + files), supports multi-user access.

**Official website**: https://joinhidden.com  

## Highlights

- **Isolated workspace** — runs without Internet; no telemetry, no implicit traffic.
- **Protected storage** — AES-256 at rest, per-file fragmentation into shards, secret-key–gated access.
- **Lock mechanism** — temporary read-only mode that blocks writes/deletes during maintenance.
- **Role-based access** — `Reader` / `Author` / `Editor` / `Admin`.
- **Multi-factor auth** — OTP protects logins.
- **Public API (Swagger/OpenAPI)** — explore endpoints at `/docs`.
- **Backend documentation (Sphinx)** — developer reference at `/sphinx/`.
- **Add-on friendly** — microkernel with hook-based extensions.

## Quick start (Docker)

Get the latest image:
```
docker pull artabramov/hidden
```

Run the app:
```
docker run -dit -p 80:80 artabramov/hidden
```

Open in a browser:
```
http://localhost
```

## API & Documentation

Public API (Swagger/OpenAPI):
```
http://localhost/docs
```

Backend docs (Sphinx):
```
http://localhost/sphinx/
```

## News and updates

Telegram:
```
t.me/hiddenupdates
```
