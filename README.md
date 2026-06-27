<p align="center">
  <img src="docs/logman_logo.png" alt="LogMan" width="420" />
</p>

<h1 align="center">LogMan — Backend</h1>

<p align="center">Real-time log streaming with Django, Channels and Daphne.</p>

<p align="center">
  <img src="https://img.shields.io/badge/license-BSD-green" alt="License" />
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python" />
  <img src="https://img.shields.io/badge/django-5.x-darkgreen" alt="Django" />
  <img src="https://img.shields.io/badge/nginx-1.28-red" alt="Nginx" />
</p>

---

## Overview

**LogMan** tails log files on remote servers over SSH and streams them to the
browser in real time. This repository is the **Django + Channels (ASGI)**
backend: it exposes the REST API and the live-log WebSocket. The companion
single-page app lives in the [`logman-ui`](https://github.com/devngugi/logman-ui)
repository.

---

## Features

* ✅ **Real-time log streaming** via WebSockets (no polling)
* ✅ **Django + Channels backend** on the Daphne ASGI server
* ✅ Remote log tailing over SSH using a **password or an SSH private key**
* ✅ SSH secrets **encrypted at rest** (Fernet)
* ✅ JWT authentication; **only superusers** can create/edit/delete sources & connections
* ✅ **Scalable** — handles multiple concurrent log streams
* ✅ **Docker-ready**

---

## Architecture

```
   ┌───────────────┐  SSH   ┌─────────────┐        ┌───────────────┐
   │  Remote log   │ <----- │ Django App  │  -->   │ WebSocket API │
   │     file      │  tail  │ + Channels  │        │  via Daphne   │
   └───────────────┘        └─────────────┘        └───────────────┘
                                   │
                             Real-time logs
                                   │
                          ┌─────────────────┐
                          │  Vue.js (logman-ui)
                          └─────────────────┘
```

---

## Tech stack

* **Backend:** Django 5.x, Django REST Framework, Django Channels, Daphne
* **Channel layer / realtime:** Redis (`channels_redis`), ASGI
* **Database:** PostgreSQL
* **Auth:** SimpleJWT / Djoser
* **SSH:** paramiko · **Secret storage:** `cryptography` (Fernet)
* **Containerization:** Docker

---

## Installation

### Prerequisites

* Python **3.10+**
* Redis (WebSocket channel layer)
* PostgreSQL
* Nginx (production)

### Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/devngugi/logman_backend
   cd logman_backend
   ```

2. **Create a virtual environment and install dependencies**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Populate your env file**

   ```bash
   cp .env.example .env
   ```

   | Variable | Description |
   | --- | --- |
   | `SECRET_KEY` | Django secret key |
   | `DEBUG` | `True` in development, `False` in production |
   | `ALLOWED_HOSTS` | Comma-separated hostnames |
   | `TIMEZONE` | e.g. `Africa/Nairobi` |
   | `CRYPT` | Fernet key used to encrypt SSH secrets (step 4) |
   | `DB_NAME` / `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` | PostgreSQL connection |
   | `REDIS_HOST` / `REDIS_PORT` | Redis channel layer |
   | `CORS_ALLOWED_ORIGINS` / `CSRF_TRUSTED_ORIGINS` | Comma-separated frontend origins |

4. **Generate the `CRYPT` key** (32 url-safe base64 bytes) and set it in `.env`.
   ⚠️ Changing this later makes existing stored SSH secrets undecryptable.

   ```bash
   python3 scripts/generaye_key.py
   ```

5. **Apply migrations, create default groups and a superuser**

   ```bash
   python manage.py migrate
   python manage.py create_groups
   python manage.py createsuperuser
   ```

6. **Create the default Organization** via the admin panel

   ```bash
   # navigate to http://your-domain/admin/
   ```

7. **Run the ASGI server**

   For development:

   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

   For production (Daphne):

   ```bash
   daphne -b 0.0.0.0 -p 8000 core.asgi:application
   ```

   Redis must be running, or WebSocket log streaming will fail.

---

## API overview

Base path: `/api/v1/` — interactive Swagger docs are served at `/`.

| Method(s) | Path | Notes |
| --- | --- | --- |
| `POST` | `accounts/token/` | Obtain JWT (`{ access, refresh, user }`) |
| `POST` | `accounts/token/refresh/` | Refresh JWT |
| `GET` | `accounts/users/` | List users |
| `GET` / `POST` | `sources/` | List / create sources (create = superuser) |
| `GET` `PUT` `PATCH` `DELETE` | `sources/<id>/` | Manage a source (writes = superuser) |
| `GET` / `POST` | `connections/` | List / create connections (create = superuser) |
| `GET` `PUT` `PATCH` `DELETE` | `connections/<id>/` | Manage a connection (writes = superuser) |

WebSocket: `ws(s)://<host>/ws/log/<room>/` — send `{ "source": "<id>", "lines": <n> }`
to begin tailing.

A connection authenticates over SSH with either a password or a private key
(`auth_method = password | key`); both are stored Fernet-encrypted.

---

## Roles

* `superuser`: sees all orgs; can manage sources & connections.
* `Org Admin`: can add users, sources and connections; sees their org's users and the sources/connections they own or are assigned.
* `normal user`: can only view sources.

---

## Docker

```bash
docker build -t logman-backend .
docker run --env-file .env -p 8000:8000 logman-backend
```

You still need reachable PostgreSQL and Redis instances (point `DB_HOST` /
`REDIS_HOST` at them).

---

## Deployment

> First deploy the frontend by following the instructions in [`logman-ui`](https://github.com/devngugi/logman-ui).

1. **Copy the systemd unit file**

   ```bash
   sudo cp deployment_configs/logman_backend.service /etc/systemd/system/logman_backend.service
   ```

2. **Enable and start the service**

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now logman_backend.service
   ```

3. **Copy the nginx configuration**

   ```bash
   sudo cp deployment_configs/logman_backend.conf /etc/nginx/conf.d/logman.conf
   ```

4. **Restart nginx**

   ```bash
   sudo systemctl restart nginx.service
   ```

---

## License

BSD License.
