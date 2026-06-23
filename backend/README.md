# Personal Portfolio Backend (Django)

Django REST Framework API for the personal portfolio website.

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env` and configure MySQL credentials.

```bash
python manage.py migrate --fake-initial  # existing database
python manage.py create_superadmin
python manage.py runserver   # uses dev_port from .env (default: 8000)
```

## Production

```bash
python run_gunicorn.py   # uses prod_port from .env
```

See `gunicorn.service.example` for systemd configuration.

## API

Base URL: `/api/v1/`

- `GET /api/v1/health`
- `GET /api/v1/profile`
- `GET /api/v1/projects`
- `GET /api/v1/blog`
- Admin panel: `/admin`

## Legacy Flask backend

The previous Flask implementation lives in `../backend-flask/` for reference only.
