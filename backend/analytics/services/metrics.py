from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from statistics import mean, pstdev
from typing import Iterable

from django.db.models import Avg, Count, Max, Min, Sum

from analytics.models import Machine, SensorData


def as_float(value):
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    return value


def classify_risk(anomalies: int, avg_load: float | None, max_vibration: float | None) -> str:
    avg_load = avg_load or 0
    max_vibration = max_vibration or 0
    if anomalies >= 5 or avg_load >= 92 or max_vibration >= 9:
        return "High"
    if anomalies >= 1 or avg_load >= 82 or max_vibration >= 5:
        return "Medium"
    return "Low"


def record_is_anomaly(record: SensorData) -> bool:
    return (
        record.temperature > 90
        or record.vibration > 8
        or record.load_percentage > 95
        or record.energy_consumption > 200
    )


def machine_reliability_summary():
    rows = []
    for machine in Machine.objects.all().order_by("machine_code"):
        records = list(SensorData.objects.filter(machine=machine).order_by("recorded_at"))
        total = len(records)
        anomalies = sum(1 for row in records if record_is_anomaly(row))
        if total:
            avg_load = mean(float(row.load_percentage) for row in records)
            avg_temperature = mean(float(row.temperature) for row in records)
            max_vibration = max(float(row.vibration) for row in records)
            peak_load = max(float(row.load_percentage) for row in records)
        else:
            avg_load = avg_temperature = max_vibration = peak_load = 0

        if total > 1 and anomalies:
            operating_hours = (records[-1].recorded_at - records[0].recorded_at).total_seconds() / 3600
            mtbf = round(max(operating_hours, 1) / anomalies, 2)
        else:
            mtbf = None

        rows.append({
            "machine_code": machine.machine_code,
            "machine_name": machine.machine_name,
            "factory_zone": machine.factory_zone,
            "status": machine.status,
            "records": total,
            "anomaly_events": anomalies,
            "estimated_mtbf_hours": mtbf,
            "avg_load": round(avg_load, 2),
            "peak_load": round(peak_load, 2),
            "avg_temperature": round(avg_temperature, 2),
            "max_vibration": round(max_vibration, 2),
            "risk_level": classify_risk(anomalies, avg_load, max_vibration),
        })
    return rows


def engineering_kpis():
    aggregates = SensorData.objects.aggregate(
        total_records=Count("id"),
        avg_load=Avg("load_percentage"),
        peak_load=Max("load_percentage"),
        total_energy=Sum("energy_consumption"),
        avg_temperature=Avg("temperature"),
        max_temperature=Max("temperature"),
        max_vibration=Max("vibration"),
    )
    reliability = machine_reliability_summary()
    critical = sum(1 for row in reliability if row["risk_level"] == "High")
    warnings = sum(1 for row in reliability if row["risk_level"] == "Medium")
    low_risk = sum(1 for row in reliability if row["risk_level"] == "Low")

    return {
        "total_records": aggregates["total_records"] or 0,
        "machines": Machine.objects.count(),
        "critical_machines": critical,
        "warning_machines": warnings,
        "stable_machines": low_risk,
        "average_load": round(as_float(aggregates["avg_load"]) or 0, 2),
        "peak_load": round(as_float(aggregates["peak_load"]) or 0, 2),
        "total_energy": round(as_float(aggregates["total_energy"]) or 0, 2),
        "average_temperature": round(as_float(aggregates["avg_temperature"]) or 0, 2),
        "max_temperature": round(as_float(aggregates["max_temperature"]) or 0, 2),
        "max_vibration": round(as_float(aggregates["max_vibration"]) or 0, 2),
    }


def hourly_load_profiles(machine_code: str | None = None):
    qs = SensorData.objects.select_related("machine").order_by("recorded_at")
    if machine_code and machine_code.lower() != "all":
        qs = qs.filter(machine__machine_code=machine_code)

    buckets = defaultdict(list)
    for row in qs:
        hour = row.recorded_at.replace(minute=0, second=0, microsecond=0)
        key = (row.machine.machine_code, row.machine.machine_name, row.machine.factory_zone, hour)
        buckets[key].append(row)

    points = []
    for (code, name, zone, hour), rows in sorted(buckets.items(), key=lambda item: item[0][3]):
        loads = [float(row.load_percentage) for row in rows]
        temperatures = [float(row.temperature) for row in rows]
        vibrations = [float(row.vibration) for row in rows]
        energy = [float(row.energy_consumption) for row in rows]
        anomalies = sum(1 for row in rows if record_is_anomaly(row))
        points.append({
            "machine_code": code,
            "machine_name": name,
            "factory_zone": zone,
            "recorded_hour": hour.isoformat(),
            "avg_load": round(mean(loads), 2),
            "peak_load": round(max(loads), 2),
            "load_stddev": round(pstdev(loads), 2) if len(loads) > 1 else 0,
            "avg_temperature": round(mean(temperatures), 2),
            "avg_vibration": round(mean(vibrations), 2),
            "total_energy": round(sum(energy), 2),
            "anomaly_events": anomalies,
        })
    return points
