# 🏥 HealthPortal Kenya

A production-ready healthcare patient portal built with Django.
Patients book appointments, doctors manage records and prescriptions,
staff handle scheduling — all secured with role-based access control.

Live Demo: https://healthportal.andasy.dev

---

## 🏗️ Architecture

| Layer | Technology |
|---|---|
| Backend | Django 5.2 + Django REST Framework |
| Frontend | Tailwind CSS (CDN) + HTMX (no custom JS) |
| Auth | JWT (API) + Session (web) + django-axes (brute-force) |
| Database | PostgreSQL via Neon (serverless) |
| Cache / Queue | Redis via Upstash (serverless) |
| Background Tasks | Celery (email, SMS, M-Pesa notifications) |
| Hosting | Andasy.io (Docker + Gunicorn + WhiteNoise) |
| CI/CD | GitHub → Andasy auto-deploy on push to main |

### App Structure

    healthportal/
    ├── config/          # Settings (base/dev/prod), URLs, Celery, WSGI
    ├── accounts/        # Custom User model, JWT auth, RBAC permissions
    ├── patients/        # Patient profiles (SHA/NHIF, emergency contacts)
    ├── doctors/         # Doctor profiles, schedules, specializations
    ├── appointments/    # Booking engine, HTMX slot picker, M-Pesa mock
    ├── records/         # Medical records, prescriptions (HTMX), lab results
    ├── notifications/   # Celery tasks: email, SMS, M-Pesa
    └── dashboard/       # Role-specific dashboards (Patient/Doctor/Admin)

---

## ✨ Key Features

### Core
- Role-Based Access Control: PATIENT, DOCTOR, RECEPTIONIST, ADMIN roles with separate dashboards and data isolation
- Appointment Booking: HTMX-powered real-time slot picker (no page reload), double-booking prevention
- Medical Records: Doctors write diagnosis, treatment, prescriptions inline via HTMX
- Lab Results: File upload (PDF/image), patient read-only access
- DRF API: Full REST API with JWT auth, pagination, filtering, and role-gated endpoints

### Security
- Brute-Force Protection: django-axes locks out after 3 failed login attempts
- JWT + Session Dual Auth: API uses Bearer tokens, web frontend uses sessions
- CSRF Trusted Origins: Enforced for Andasy proxy environment
- Secrets Management: All credentials injected at runtime, never in code

### Background Processing
- Email Notifications: Booking confirmations and cancellations via Celery
- SMS Reminders: Africa's Talking integration (mocked, swap SDK to go live)
- M-Pesa Payments: Daraja STK push flow (mocked, architecture production-ready)
- Redis Caching: Doctor availability slots cached (5 min) to reduce DB hits

### Kenya-Specific
- SHA/NHIF Number: National health insurance field on patient profile
- Africa's Talking SMS: Higher reach than email in Kenya
- M-Pesa Integration: Dominant payment method in Kenya
- EAT Timezone: Africa/Nairobi configured throughout
- Swahili i18n: Django i18n configured, ready for translations

---

## 🚀 Local Development

Prerequisites
- Python 3.10+
- PostgreSQL
- Redis

Setup

    git clone https://github.com/IbrahimAce/healthportal.git
    cd healthportal
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver

Run Celery (second terminal)

    source venv/bin/activate
    celery -A config worker --loglevel=info

---

## ☁️ Deployment

Deployment is fully automated via GitHub Actions + Andasy.io.

    git push origin main

On every push to main:
1. Andasy builds the Docker image
2. python manage.py migrate runs on the Neon database
3. init_admin.py seeds the superuser if not present
4. Gunicorn starts and serves the application

Environment Variables (set in Andasy dashboard)

    SECRET_KEY
    DJANGO_SETTINGS_MODULE=config.settings.prod
    ALLOWED_HOSTS
    DEBUG=False
    DATABASE_URL
    REDIS_URL
    EMAIL_HOST / EMAIL_HOST_USER / EMAIL_HOST_PASSWORD
    SITE_NAME=HealthPortal Kenya

---

## 📖 API Reference

Base URL: /api/v1/
Authentication: Authorization: Bearer <access_token>

| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | /auth/register/ | Public | Patient registration |
| POST | /auth/login/ | Public | Get JWT tokens |
| POST | /auth/refresh/ | Public | Refresh access token |
| GET | /auth/me/ | Auth | Current user profile |
| GET | /patients/ | Staff | List all patients |
| GET/PATCH | /patients/me/ | Patient | Own profile |
| GET | /doctors/ | Auth | List available doctors |
| GET | /doctors/<id>/ | Auth | Doctor detail + schedule |
| GET/POST | /appointments/ | Auth | List / book appointments |
| GET/PATCH | /appointments/<id>/ | Auth | Detail / update status |
| POST | /appointments/<id>/cancel/ | Auth | Cancel appointment |
| GET | /records/ | Auth | Medical records |
| GET | /records/<id>/ | Auth | Record + prescriptions |
| GET | /labs/ | Auth | Lab results |

---

## 🧪 Evaluation Criteria (Bootcamp)

| Criteria | Weight | How We Meet It |
|---|---|---|
| Engineering Quality | 40% | Modular apps, signals, select_related, clean separation of concerns |
| System Design | 25% | RBAC architecture, dual auth, async processing, API versioning |
| Features | 20% | Booking engine, records, prescriptions, notifications, lab results |
| Production Readiness | 10% | Docker, .env, WhiteNoise, Gunicorn, structured logging, CI/CD |
| Presentation | 5% | Live demo URL, role dashboards, browsable API |

---

## 👨‍💻 Author

Ibrahim Karanja
Final-year BSc Computer Science — Dedan Kimathi University of Technology
GitHub: @IbrahimAce — https://github.com/IbrahimAce
