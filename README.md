# MediCarePlus

MediCarePlus is a Django-based healthcare platform that brings online pharmacy shopping and doctor appointment management together. Patients can browse medicines, upload prescriptions, manage orders, and connect with doctors through one application.

## Features

- Patient and doctor accounts, email OTP verification, profiles, and address management
- Medicine catalogue, categories, search, wishlists, and shopping cart
- Order checkout, order tracking, and Razorpay or cash-on-delivery payment options
- Doctor discovery, appointment booking, and appointment management
- Prescription upload and doctor review workflows
- Patient and doctor dashboards, notifications, and reviews
- AI-assisted health chatbot and doctor suggestions (requires a Gemini API key)

## Technology

- Python and Django
- SQLite by default, with database settings configurable through environment variables
- Bootstrap 5 forms, crispy forms, and Django templates
- Optional Razorpay and Google Gemini integrations

## Getting started

### Requirements

- Python 3.10 or later
- pip

### Install and run

From the repository root, create and activate a virtual environment, then install the dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` for your environment. The example uses Django's console email backend so email content is printed locally instead of sent through an SMTP provider.

Run the Django commands from the application directory:

```powershell
Set-Location .\MediCarePlus
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open <http://127.0.0.1:8000/> in your browser. The Django admin is available at <http://127.0.0.1:8000/admin/>.

To load the bundled sample doctors, medicines, and reviews, optionally run `python populate_data.py` from `MediCarePlus/` after migrations. Newly created sample doctor accounts have no usable password unless `SEED_DOCTOR_PASSWORD` is set in `.env`; do not use a shared seed password in production.

## Configuration

Copy `.env.example` to `.env` and set values appropriate for your environment.

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Django signing key; use a private, randomly generated value outside local development |
| `DEBUG` | Enables Django debug mode; keep disabled in production |
| `ALLOWED_HOSTS` | Comma-separated hostnames accepted by Django |
| `EMAIL_BACKEND` | Email backend; the example uses the console backend |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS` | SMTP connection settings when using an SMTP backend |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | SMTP credentials; do not commit real credentials |
| `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Optional database connection settings; defaults to SQLite |
| `USE_ORACLE_DB` | Oracle database configuration flag |
| `SEED_DOCTOR_PASSWORD` | Optional local-only password for newly seeded doctor accounts |
| `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET` | Optional Razorpay payment integration credentials |
| `GEMINI_API_KEY` | Optional Google Gemini API key for chatbot features |

Never commit `.env`, production secrets, local databases, or uploaded user files. Uploaded profile images are kept out of Git; only the default placeholder image is tracked.

## Project layout

The Django project and `manage.py` are in `MediCarePlus/`. Feature apps are split by responsibility: `accounts`, `medicines`, `cart`, `orders`, `payments`, `appointments`, `prescriptions`, `reviews`, `notifications`, `dashboard`, and `chatbot`. Templates, static assets, and media assets are stored alongside these apps.

## Development checks

From `MediCarePlus/`, run Django's configuration check and the available app tests with:

```powershell
python manage.py check
python manage.py test
```
