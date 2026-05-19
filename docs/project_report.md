# Project Report — Industrial Field Data Analytics Platform

## Context

The project simulates a web application used by engineering teams to explore field data from industrial machines. The goal is to make load profiles, anomalies and reliability indicators easier to access through a full-stack application.

## Technical scope

- **Frontend:** Vue.js dashboard with KPIs, charts, machine filter, alerts and reliability tables.
- **Backend:** Django REST API exposing processed telemetry and operational indicators.
- **Data:** Python ETL for cleaning, validation, load-profile aggregation and anomaly detection.
- **Database:** PostgreSQL-ready schema, SQL views and SQLite fallback for demo simplicity.

## Business value

The application improves access to field data for product engineering and operations teams. Instead of manually opening CSV files, users can inspect load behavior, identify abnormal machines and compare reliability indicators through a single web interface.

## Engineering workflow

1. Raw telemetry is stored as CSV.
2. ETL validates and enriches the data.
3. Processed outputs are generated for analytics and reporting.
4. Data is imported into the Django database.
5. API endpoints expose operational metrics.
6. Vue dashboard consumes the API and presents user-centric insights.

## Key metrics

- Average load percentage
- Total energy consumption
- Critical/warning issue count
- Data-quality issue count
- Anomaly events per machine
- Estimated MTBF hours
- Machine risk level

## Limitations

This is a portfolio simulation, not a production system. Authentication, real device ingestion, CI/CD, cloud deployment and automated test coverage would be the next steps.

## Why it fits the target role

The project combines the exact technical areas requested by the role: Vue.js, Django, field-data processing, load-profile visualization, database modelling, statistics/reliability concepts and a clear path to Azure Databricks/PySpark.
