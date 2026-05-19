# Runbook

## Local backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py import_machine_data --reset
python manage.py runserver
```

## Local frontend

```bash
cd frontend
npm install
npm run dev
```

## ETL

```bash
python etl/process_data.py
python etl/anomaly_detection.py
```

## Tests

```bash
cd backend
python manage.py test
```

## Common problems

### API offline in frontend
Check that Django is running at `http://127.0.0.1:8000` or set `VITE_API_URL`.

### PostgreSQL connection fails
Use the default SQLite mode for a quick demo, or start Docker Compose.

### Frontend install fails
Delete `node_modules` and `package-lock.json`, then run `npm install` again.
