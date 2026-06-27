# **LogMan**

Real-time Log Streaming with Django and Daphne

![License](https://img.shields.io/badge/license-BSD-green)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Django](https://img.shields.io/badge/django-5.x-darkgreen)
![Nginx](https://img.shields.io/badge/nginx-1.28-red)


---

## **Overview**

**LogMan** is a real-time log streaming solution that leverages **Django Channels**, **Daphne**, and **WebSockets** for efficient log delivery, combined with a **Vue.js** frontend for a dynamic and responsive user experience.

---

## **Features**

* ✅ **Real-time log streaming** via WebSockets (no polling required)
* ✅ **Django + Channels backend** with Daphne ASGI server
* ✅ **Vue.js single-page application (SPA)** for an interactive UI
* ✅ **Scalable architecture** for handling multiple log streams concurrently
* ✅ **Lightweight and extensible** for custom log sources
* ✅ **Authentication support** (token-based)
* ✅ **Docker-ready** for production deployments

---

## **Architecture**

```
   ┌───────────────┐        ┌─────────────┐        ┌───────────────┐
   │    Log File   │  -->   │ Django App  │  -->   │ WebSocket API │
   └───────────────┘        │ Channels    │        │   via Daphne  │
                            └─────────────┘        └───────────────┘
                                   │
                             Real-time Logs
                                   │
                          ┌─────────────────┐
                          │ Vue.js Frontend │
                          └─────────────────┘
```

---

## **Tech Stack**

* **Backend:** Django 5.x, Django Channels, Daphne, Redis (for channel layers)
* **WebSocket Protocol:** ASGI
* **Database:** PostgreSQL
* **Containerization:** Docker

---

## **Installation**

### **Prerequisites**

* Python **3.10+**
* Redis (for WebSocket channel layer)
* PostgreSQL
* Nginx

---

### **Setup**

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

3. **Populate your env file with the required values**

   ```bash
   cp .env.example .env
   ```

4. **Run script to generate a 32 url-safe base64-encoded bytes for the CRYPT env variable**

   ```bash
   python3 scripts/generaye_key.py
   ```

5. **Apply migrations, create default groups and a superuser**

   ```bash
   python manage.py migrate
   python manage.py create_groups
   python manage.py createsuperuser
   ```
   
6. **Create the default Organization using on the admin panel**

   ```bash
   # navigate to http://your-domain/admin/
   ```

7. **Run the ASGI server with Daphne**

   ```bash
   daphne -b 0.0.0.0 -p 8000 core.asgi:application
   ```

---

### **Roles**
ROLES:
* `superuser`: can see all orgs.

* `Org Admin`: can add users, add sources and connections, can see their users in the org, can only see sources and connections they have added, or being assigned

* `normal user`: can only view sources

---

## **Deployment**
* Note: First deploy the frontend by following the instructions [here](https://github.com/devngugi/logman-ui)
1. **Populate and copy the system unit service file**

   ```bash
   sudo cp deployment_configs/logman_backend.service /etc/systemd/system/logman_backend.service
   ```

2. **Enable and start the service**

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now logman_backend.service
   ```

3. **Populate and copy the nginx configuration file to your nginx conf.d directory.**

    ```bash
   # this removes the hassle of symlinks in the sites-enabled directory
   sudo cp deployment_configs/logman_backend.conf /etc/nginx/conf.d/logman.conf
   ```
   
4. **Restart the nginx service**

   ```bash
   sudo systemctl restart nginx.service
   ```

---

## **License**

BSD License.
