# Clinic Management System

A comprehensive clinic management system built with Django REST Framework.

## Features

- User Management & Role-Based Access Control
- Patient Management
- Doctor Management & Specializations
- Appointment Scheduling & Calendar
- Electronic Medical Records (EMR)
- Prescription Management
- Billing & Invoicing
- Inventory & Pharmacy Management
- Department & Service Management
- Staff Scheduling
- Notifications (Email/SMS)
- Reporting & Analytics Dashboard
- Audit Logging

## Tech Stack

- **Backend:** Django 4.2 + Django REST Framework
- **Database:** PostgreSQL 16
- **Authentication:** JWT (SimpleJWT)
- **Async Tasks:** Celery + Redis
- **API Docs:** drf-spectacular (OpenAPI 3.0 / Swagger)
- **Containerization:** Docker + Docker Compose

## Quick Start (Docker)

```bash
# Clone and enter project
git clone <repository-url>
cd clinic-management

# Start all services
docker-compose -f docker-compose.local.yml up -d

# Run migrations
docker-compose -f docker-compose.local.yml exec django python manage.py migrate

# Create superuser
docker-compose -f docker-compose.local.yml exec django python manage.py createsuperuser
```

## Quick Start (Local)

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/local.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

## API Documentation

| Endpoint | Description |
|----------|-------------|
| `/api/v1/docs/` | Swagger UI (interactive) |
| `/api/v1/redoc/` | ReDoc (clean documentation) |
| `/api/v1/schema/` | OpenAPI 3.0 JSON schema |

## Project Structure

```
clinic_management/
├── config/              # Django project settings
│   ├── settings/        # Split settings (base, local, production)
│   ├── urls.py          # Root URL configuration
│   ├── celery.py        # Celery app configuration
│   └── wsgi.py / asgi.py
├── apps/                # Django applications (one per domain)
├── core/                # Shared utilities (pagination, permissions, etc.)
├── compose/             # Docker configurations
├── requirements/        # Python dependencies (split by environment)
├── .envs/               # Environment variables per environment
├── templates/           # HTML templates (emails, PDFs)
├── static/              # Static assets
└── media/               # User-uploaded files
```

## Environment Variables

See `.env.example` for all required variables. Key variables:

| Variable | Description |
|----------|-------------|
| `DJANGO_SECRET_KEY` | Django cryptographic signing key |
| `POSTGRES_*` | PostgreSQL connection settings |
| `CELERY_*` | Redis broker/backend URLs |
| `EMAIL_*` | SMTP configuration |
| `SENTRY_DSN` | Sentry error tracking (production) |

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov=core --cov-report=html

# Run specific test file
pytest apps/users/tests/
```

## Code Quality

```bash
# Format code
black .
isort .

# Check formatting (CI)
black --check .
isort --check .
```

## License

MIT
