# Architecture

```text
Field telemetry CSV
      |
      v
Python ETL / Data Quality / Anomaly Scoring
      |
      +--> Processed CSV outputs for BI/reporting
      |
      v
Django import command
      |
      v
PostgreSQL-ready relational model
      |
      v
Django REST API
      |
      v
Vue Engineering Dashboard
```

## Main API resources

- `/health/` service status
- `/machines/` machine inventory with risk level
- `/kpis/` executive engineering KPIs
- `/machine-load/` latest telemetry records
- `/load-profiles/` hourly aggregated load profiles
- `/reliability/summary/` MTBF, anomalies and risk classification
- `/engineering-summary/` consolidated dashboard payload
- `/data-quality/` threshold-based data-quality issues

## Scalability path

```text
Azure Blob Storage -> Azure Databricks PySpark -> PostgreSQL/Azure SQL -> Django API -> Vue/Power BI
```

The local repository focuses on a defendable portfolio implementation. The cloud path is documented so the candidate can explain how the same workflow would scale.
