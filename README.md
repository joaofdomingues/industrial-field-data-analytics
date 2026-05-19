# Industrial Field Data Analytics Platform

A full-stack, data-driven portfolio project built for a **Full-Stack Developer (Data-Driven)** role focused on Vue.js, Python Django, PostgreSQL, field-data processing and engineering load profiles.

The project simulates how field telemetry from heating/cooling-style industrial assets can be cleaned, modeled, exposed through an API and visualized by product engineering teams.

## Executive summary

This is not a generic CRUD. It demonstrates an end-to-end engineering analytics workflow:

```text
Raw field telemetry -> Python ETL -> anomaly/reliability metrics -> Django REST API -> Vue dashboard -> BI/cloud extension path
```

## Role alignment

| Job requirement | Project evidence |
|---|---|
| Vue.js web development | Interactive dashboard with machine filters, KPIs, charts, reliability and alert tables |
| Python Django backend | Django REST API with multiple dashboard and engineering analytics endpoints |
| Field-data processing | Python ETL validates raw sensor data and produces clean/processed datasets |
| Load-profile display | Hourly load-profile API and chart using average/peak load |
| Backend/frontend optimization | Consolidated `/engineering-summary/` endpoint and dynamic KPIs |
| PostgreSQL concepts | SQL schema, reporting views, indexes, Docker PostgreSQL service and DB-ready models |
| Azure / Databricks awareness | PySpark job and documented Azure Databricks extension path |
| Python/PySpark data modeling | Pandas ETL plus PySpark-style processing job |
| Statistics and Reliability | z-score, rolling averages, anomaly flags, MTBF estimate and risk classification |
| GitHub collaboration | Clean repository structure, `.gitignore`, `.env.example`, Makefile, tests and docs |

## Main features

- Raw machine telemetry ingestion from CSV
- Data validation and quality report generation
- Load-profile aggregation by machine and hour
- Dynamic engineering KPIs
- Anomaly detection using thresholds and statistical indicators
- Reliability summary with estimated MTBF
- Django REST API
- Vue dashboard with charts and machine filtering
- Docker Compose with PostgreSQL
- Local SQLite fallback for easy demo
- PySpark/Databricks extension path
- API tests and interview defense notes

## Repository structure

```text
backend/       Django REST API
frontend/      Vue.js dashboard
etl/           Python data-processing scripts
data/          Raw and processed sample telemetry
sql/           PostgreSQL schema and reporting views
databricks/    PySpark-style transformation job
docs/          Architecture, runbook, Power BI and interview notes
```

## API endpoints

| Endpoint | Purpose |
|---|---|
| `GET /health/` | Service metadata and health status |
| `GET /machines/` | Machine inventory with record count and risk level |
| `GET /kpis/` | Engineering dashboard KPIs |
| `GET /machine-load/` | Latest telemetry records, optional `?machine=M001` |
| `GET /load-profiles/` | Hourly load profiles, optional `?machine=M001` |
| `GET /energy-consumption/` | Energy telemetry |
| `GET /reliability/summary/` | MTBF, anomaly events and risk classification |
| `GET /alerts/` | Alert feed |
| `GET /data-quality/` | Data-quality issues based on threshold rules |
| `GET /engineering-summary/` | Consolidated endpoint for dashboards |

## Quick start

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py import_machine_data --reset
python manage.py runserver
```

Backend: `http://127.0.0.1:8000`

Test it:

```text
http://127.0.0.1:8000/health/
http://127.0.0.1:8000/kpis/
http://127.0.0.1:8000/load-profiles/
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://127.0.0.1:5173`

### 3. ETL

From the project root:

```bash
python etl/process_data.py
python etl/anomaly_detection.py
```

Generated outputs:

- `data/processed/clean_machine_data.csv`
- `data/processed/load_profiles_by_machine_hour.csv`
- `data/processed/data_quality_report.csv`
- `data/processed/alerts.csv`
- `data/processed/reliability_summary.csv`

### 4. Tests

```bash
cd backend
python manage.py test
```

## Docker option

```bash
docker compose up --build
```

Services:

- PostgreSQL: `5432`
- Django API: `8000`
- Vue dashboard: `5173`

## Demo pitch

> I built a full-stack data-driven application that simulates how field telemetry from industrial heating/cooling-style assets can be transformed into engineering insights. The backend is Django REST Framework, the frontend is Vue.js, and the data workflow includes Python ETL, data-quality validation, anomaly detection, hourly load-profile aggregation and reliability metrics such as estimated MTBF. The project is designed to show both web-development capability and data-processing thinking, matching the role’s focus on field data, load profiles and engineering process improvement.

## Honest limitations

- The dataset is simulated.
- Azure/Databricks is documented and represented through a PySpark job, not deployed live.
- Authentication, CI/CD and production monitoring are future work.

## Next improvements

- Deploy API/frontend to Azure
- Store raw telemetry in Azure Blob Storage
- Schedule PySpark transformations in Azure Databricks
- Add JWT authentication and role-based access
- Add frontend component tests and GitHub Actions
- Add more advanced reliability models


## Azure / GitHub Deployment

This repository includes an interview-grade deployment setup:

- `.github/workflows/ci.yml` — backend tests and frontend build.
- `.github/workflows/azure-backend-container.yml` — builds and deploys the Django backend Docker image to Azure App Service.
- `.github/workflows/azure-static-web-app.yml` — deploys the Vue frontend to Azure Static Web Apps.
- `docs/deployment.md` — exact GitHub and Azure commands/secrets.

The project is Azure-ready. A real live URL requires running the deployment commands inside your own Azure subscription and adding the GitHub secrets.
