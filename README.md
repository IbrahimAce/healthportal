# 🏥 HealthPortal Kenya

A production-ready, cloud-native healthcare patient portal built with Django. Patients can book appointments, doctors manage medical records and prescriptions, and staff handle scheduling—all protected by role-based access control and brute-force security.

---

## 🏗️ System Architecture

This project has been architected for a modern cloud environment with continuous deployment:

*   Hosting: Andasy.io (Containerized Django + Gunicorn + WhiteNoise)
*   Database: Neon (Serverless PostgreSQL)
*   Cache & Queue: Upstash (Serverless Redis)
*   CI/CD: GitHub Actions (Automated deployments on push to main)
*   Frontend: Tailwind CSS + HTMX (Dynamic UI without a heavy JS framework)

### App Structure
healthportal/
├── .github/workflows/ # GitHub Actions CI/CD configuration
├── config/          # Settings (base/dev/prod), URLs, Celery, WSGI
├── accounts/        # Custom User model, JWT auth, RBAC permissions
├── patients/        # Patient profiles (SHA/NHIF, emergency contacts)
├── doctors/         # Doctor profiles, weekly schedules, specializations
├── appointments/    # Booking engine, HTMX slot picker, M-Pesa mock
├── records/         # Medical records, prescriptions (HTMX), lab results
├── notifications/   # Celery tasks — email, SMS (Africa's Talking mock)
└── dashboard/       # Role-specific HTMX dashboards

---

## ✨ Key Features & Design Decisions

*   Custom User Model & RBAC: Single authentication table with role enums (PATIENT, DOCTOR, RECEPTIONIST, ADMIN) ensuring strict data isolation across dashboards.
*   HTMX over SPA: Zero custom JavaScript. Features like the real-time appointment slot picker and live prescription additions are handled via server-rendered HTMX partials.
*   Dual Authentication: Session auth for the web frontend and JWT (JSON Web Tokens) for the DRF API.
*   Asynchronous Processing: Celery + Redis ensures that email and SMS notifications never block the main HTTP response thread.
*   Enterprise Security: Protected by django-axes (brute-force lockout), strict CSRF trusted origins, and secure proxy headers.

### 🌍 Kenya-Specific Implementation
*   SHA/NHIF Number: Integrated into the patient profile schema representing Kenya's national health insurance.
*   Africa's Talking SMS: Mocked Celery task architecture ready for the Africa's Talking Python SDK (higher reach than email).
*   M-Pesa Integration: Mocked Daraja API STK push flow for consultation fee payments.
*   Timezone & i18n: Configured for Africa/Nairobi (EAT) and prepared for Swahili localization.

---

## 🚀 Setup (Local Development)

### Prerequisites
*   Python 3.10+
*   Local PostgreSQL & Redis (or use your cloud Neon/Upstash URLs)

[ 1. Clone the repository ]
git clone https://github.com/IbrahimAce/healthportal.git
cd healthportal

[ 2. Create and activate virtual environment ]
python3 -m venv venv
source venv/bin/activate

[ 3. Install dependencies ]
pip install -r requirements.txt

[ 4. Environment Variables ]
cp .env.example .env
(Edit .env to add your local DB credentials or cloud URLs)

[ 5. Database Setup ]
python manage.py migrate
python manage.py createsuperuser

[ 6. Run Server ]
python manage.py runserver

### Run Celery Worker (Separate Terminal)
source venv/bin/activate
celery -A config worker --loglevel=info

---

## ☁️ Deployment (Continuous Integration)

This project utilizes GitHub Actions for CI/CD. 

1. Push code to the main branch.
2. GitHub Actions intercepts the push and connects to Andasy.io.
3. The Dockerfile executes, running python manage.py migrate on the Neon database.
4. The init_admin.py script ensures a superuser is seeded.
5. Gunicorn binds to [::]:8000 (IPv6 ready for internal proxies) and serves the app.

---

## 📖 API Documentation

Base URL: /api/v1/
(All endpoints require Authorization: Bearer <token> except registration.)

POST   | /auth/register/              | Patient self-registration
POST   | /auth/login/                 | Get JWT tokens
POST   | /auth/refresh/               | Refresh access token
GET    | /auth/me/                    | Current user profile
GET    | /patients/                   | List patients (staff only)
GET/PT | /patients/me/                | Patient own profile
GET    | /doctors/                    | List available doctors
GET    | /doctors/<id>/               | Doctor detail + schedule
GET/PT | /appointments/               | List / create appointments
GET/PT | /appointments/<id>/          | Detail / update status
POST   | /appointments/<id>/cancel/   | Cancel appointment
GET    | /records/                    | Medical records
GET    | /records/<id>/               | Record detail + prescriptions

---

## 🛡️ Security
*   Brute-Force Protection: django-axes locks out users/IPs after 3 failed login attempts.
*   Environment Isolation: Secrets are injected at runtime via Andasy environment variables.
*   Secure Headers: SECURE_PROXY_SSL_HEADER and CSRF_TRUSTED_ORIGINS enforced for proxy environments.
