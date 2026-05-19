# Azure / Databricks Extension Path

This project runs locally with pandas + Django + Vue, but the architecture can scale to Azure.

## Proposed cloud architecture

```text
Field telemetry files / device exports
        ↓
Azure Blob Storage / Data Lake
        ↓
Azure Databricks PySpark job
        ↓
Curated Delta/Parquet load-profile tables
        ↓
PostgreSQL / Azure SQL serving database
        ↓
Django REST API
        ↓
Vue dashboard / Power BI
```

## What Databricks would do

- Read large volumes of field telemetry
- Validate schema and remove invalid records
- Aggregate load profiles by machine and time bucket
- Flag anomaly events
- Write curated datasets for API and reporting consumption

A lightweight PySpark example is included in:

```text
databricks/load_profile_pyspark_job.py
```

This is not required to run the local demo. It exists to show how the same transformation logic would move from pandas to PySpark in a cloud environment.
