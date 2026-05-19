# Technical Defense Notes

## 30-second pitch

I built a full-stack, data-driven platform for industrial field telemetry. The application processes raw machine data, converts it into hourly load profiles, detects anomalies, calculates reliability indicators such as estimated MTBF, exposes the data through a Django REST API and visualizes it in a Vue.js dashboard. The architecture mirrors how engineering teams could access heating/cooling system field data faster during product development.

## Why this matches the role

- **Vue.js:** dashboard with filters, KPIs, charts and reliability tables.
- **Python Django:** REST API exposing engineering-ready endpoints.
- **Field data:** raw sensor telemetry is cleaned, validated and modeled.
- **Load profiles:** hourly machine load aggregation with peak/average load.
- **PostgreSQL:** schema, views, Docker service and database-ready model.
- **Azure Databricks/PySpark:** local PySpark-style extension included and documented as a cloud path.
- **Statistics/Reliability:** anomaly flags, z-score, rolling averages, MTBF and risk classification.

## Data flow

1. Raw CSV simulates field telemetry from industrial assets.
2. Python ETL validates missing values, ranges and duplicates.
3. The processing layer creates clean data, load profiles, anomaly flags and quality reports.
4. Django imports the telemetry and exposes API endpoints.
5. Vue consumes the API and presents engineering dashboards.
6. The documented cloud extension moves the ETL to Azure Blob + Databricks + PostgreSQL/Azure SQL.

## Key technical decisions

### Django REST Framework
Chosen because the role asks for Django and because DRF is fast for building stable JSON APIs. The API separates the data layer from the dashboard, making the frontend replaceable.

### Vue.js
Chosen because the role asks for Vue. The dashboard is component-oriented and supports filters and chart updates from API data.

### PostgreSQL-ready design
The local demo can run with SQLite for simplicity, but Docker Compose includes PostgreSQL and the SQL folder includes schema/reporting views.

### Reliability metrics
MTBF is estimated as operating hours divided by anomaly events. It is not a perfect production reliability model, but it is a defendable engineering indicator for a portfolio demo.

### PySpark/Databricks path
The project does not pretend to be a real Azure production deployment. It includes a PySpark job and documents how it would move to Azure Databricks.

## Weaknesses to admit honestly

- The dataset is simulated, not real production telemetry.
- Azure/Databricks is an extension path, not a live deployment.
- Authentication and role-based access are not implemented yet.
- Automated tests cover the API smoke path, not full frontend behavior.

## Best answer if asked “what would you improve next?”

I would first deploy the stack with Docker to Azure Container Apps or App Service, then move raw-data ingestion to Azure Blob Storage and schedule PySpark jobs in Azure Databricks. After that, I would add authentication, CI/CD, monitoring and more rigorous reliability models.
