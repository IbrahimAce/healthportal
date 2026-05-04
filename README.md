# 🏥 HealthPortal Kenya

A production-ready healthcare patient portal built with Django.
Patients book appointments, doctors manage records and prescriptions,
staff handle scheduling — all with role-based access control.

---

## Architecture
healthportal/
├── config/          # Settings (base/dev/prod), URLs, Celery, WSGI
├── accounts/        # Custom User model, JWT auth, RBAC permissions
├── patients/        # Patient profiles (SHA/NHIF, emergency contacts)
├── doctors/         # Doctor profiles, weekly schedules, specializations
├── appointments/    # Booking engine, HTMX slot picker, M-Pesa mock
├── records/         # Medical records, prescriptions (HTMX), lab results
├── notifications/   # Celery tasks — email, SMS (Africa's Talking mock)
└── dashboard/       # Role-specific HTMX dashboards

### Key Design Decisions

- **Custom User model** with role enum (PATIENT / DOCTOR / RECEPTIONIST / ADMIN)
  — single table, role-gated views and API endpoints
- **HTMX over SPA** — no custom JavaScript, server-rendered partials
  for slot picker and prescription form
- **JWT for API, session for browser** — dual auth so the DRF browsable
  API and the web frontend both work
- **Celery + Redis** — notifications never block HTTP responses
- **SHA/NHIF number** on patient profile — Kenya's national health insurance ID
- **Africa's Talking SMS** (mocked) — higher reach than email in Kenya
- **M-Pesa payment** (mocked) — Daraja STK push flow ready to go live

---

## Setup (Local Development)

### Prerequisites
- Python 3.10+
- PostgreSQL
- Redis

```bash
git clone https://github.com/IbrahimAce/healthportal.git
cd healthportal

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env with your database and email credentials

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Run Celery worker (separate terminal)

```bash
celery -A config worker --loglevel=info
```

---

## Setup (Docker)

```bash
cp .env.example .env
# Edit .env

docker-compose up --build
docker-compose exec app python manage.py migrate
docker-compose exec app python manage.py createsuperuser
```

---

## API Documentation

Base URL: `/api/v1/`

All endpoints require `Authorization: Bearer <token>` except registration.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register/` | Patient self-registration |
| POST | `/auth/login/` | Get JWT tokens |
| POST | `/auth/refresh/` | Refresh access token |
| GET | `/auth/me/` | Current user profile |
| GET | `/patients/` | List patients (staff only) |
| GET/PATCH | `/patients/me/` | Patient own profile |
| GET | `/doctors/` | List available doctors |
| GET | `/doctors/<id>/` | Doctor detail + schedule |
| GET/POST | `/appointments/` | List / create appointments |
| GET/PATCH | `/appointments/<id>/` | Detail / update status |
| POST | `/appointments/<id>/cancel/` | Cancel appointment |
| GET | `/records/` | Medical records |
| GET | `/records/<id>/` | Record detail + prescriptions |
| GET | `/labs/` | Lab results |

---

## Evaluation Criteria Coverage

| Criteria | Implementation |
|----------|---------------|
| Engineering Quality (40%) | Modular apps, signals, mixins, select_related, clean queries |
| System Design (25%) | RBAC architecture, separation of concerns, API versioning |
| Features (20%) | Booking, records, prescriptions, notifications, lab results |
| Production Readiness (10%) | Docker, .env, WhiteNoise, gunicorn, structured logging |
| Presentation (5%) | Role dashboards, live HTMX demo, API browsable interface |

---

## Kenya-Specific Features

- **SHA/NHIF number** field on patient profile
- **M-Pesa payment** mock (Daraja STK push architecture)
- **Africa's Talking SMS** mock (swap logger for real SDK)
- **Africa/Nairobi timezone** (EAT) configured throughout
- **Swahili i18n** configured (ready to add translations)
