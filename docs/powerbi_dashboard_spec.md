# Power BI Dashboard Specification

## Pages

### 1. Executive Overview
- Total records
- Number of machines
- Average load
- Total energy
- Critical/warning issues
- Risk level distribution

### 2. Load Profile Analysis
- Line chart: load percentage over time
- Machine selector
- Zone selector
- Peak load by machine

### 3. Reliability & Anomalies
- Estimated MTBF by machine
- Anomaly events by machine
- High temperature/vibration events
- Risk level table

### 4. Data Quality
- Invalid/critical records
- Threshold breaches
- Data-quality issue trend

## Suggested data sources

- `data/processed/load_profiles_by_machine_hour.csv`
- `data/processed/reliability_summary.csv`
- `data/processed/data_quality_report.csv`
- PostgreSQL reporting views in `sql/02_reporting_views.sql`
