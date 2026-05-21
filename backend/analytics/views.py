import csv
from io import TextIOWrapper
from django.utils.dateparse import parse_datetime
from decimal import Decimal
from pathlib import Path
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Alert, Machine, SensorData
from .services.metrics import (
    as_float,
    engineering_kpis,
    hourly_load_profiles,
    machine_reliability_summary,
    record_is_anomaly,
)


def row_to_point(row):
    return {
        'machine_code': row.machine.machine_code,
        'machine_name': row.machine.machine_name,
        'factory_zone': row.machine.factory_zone,
        'temperature': as_float(row.temperature),
        'vibration': as_float(row.vibration),
        'energy_consumption': as_float(row.energy_consumption),
        'load_percentage': as_float(row.load_percentage),
        'is_anomaly': record_is_anomaly(row),
        'recorded_at': row.recorded_at.isoformat(),
    }


@api_view(['GET'])
def health(request):
    return Response({
        'status': 'ok',
        'service': 'industrial-field-data-api',
        'version': '3.0.0',
        'purpose': 'Load profile analytics for field data from heating/cooling style assets',
        'stack': ['Django REST Framework', 'Vue.js', 'PostgreSQL-ready', 'Python ETL', 'PySpark extension path'],
    })


def machine_inventory_payload():
    data = Machine.objects.all().order_by('machine_code')
    reliability = {row['machine_code']: row for row in machine_reliability_summary()}
    return [
        {
            'machine_code': machine.machine_code,
            'machine_name': machine.machine_name,
            'factory_zone': machine.factory_zone,
            'status': machine.status,
            'records': reliability.get(machine.machine_code, {}).get('records', 0),
            'risk_level': reliability.get(machine.machine_code, {}).get('risk_level', 'Low'),
        }
        for machine in data
    ]


@api_view(['GET'])
def machines(request):
    return Response(machine_inventory_payload())


@api_view(['GET'])
def machine_load(request):
    machine = request.GET.get('machine')
    limit = int(request.GET.get('limit', 250))
    limit = min(max(limit, 1), 1000)
    qs = SensorData.objects.select_related('machine').order_by('-recorded_at')
    if machine and machine.lower() != 'all':
        qs = qs.filter(machine__machine_code=machine)
    return Response([row_to_point(row) for row in qs[:limit]])


@api_view(['GET'])
def load_profiles(request):
    machine = request.GET.get('machine')
    return Response(hourly_load_profiles(machine))


@api_view(['GET'])
def energy_consumption(request):
    machine = request.GET.get('machine')
    qs = SensorData.objects.select_related('machine').order_by('recorded_at')[:500]
    if machine and machine.lower() != 'all':
        qs = qs.filter(machine__machine_code=machine)
    return Response([
        {
            'machine_code': row.machine.machine_code,
            'machine_name': row.machine.machine_name,
            'energy_consumption': as_float(row.energy_consumption),
            'recorded_at': row.recorded_at.isoformat(),
        }
        for row in qs
    ])


@api_view(['GET'])
def kpis(request):
    return Response(engineering_kpis())


@api_view(['GET'])
def reliability_summary(request):
    return Response(machine_reliability_summary())


@api_view(['GET'])
def alerts(request):
    data = Alert.objects.select_related('machine').order_by('-created_at')[:100]
    return Response([
        {
            'machine_code': row.machine.machine_code,
            'machine_name': row.machine.machine_name,
            'alert_type': row.alert_type,
            'severity': row.severity,
            'message': row.message,
            'created_at': row.created_at.isoformat(),
        }
        for row in data
    ])


@api_view(['GET'])
def data_quality(request):
    issues = []
    for record in SensorData.objects.select_related('machine').all().order_by('-recorded_at'):
        checks = [
            ('High temperature', 'Critical', record.temperature, 90),
            ('High vibration', 'Warning', record.vibration, 5),
            ('Machine overload', 'Critical', record.load_percentage, 95),
            ('High energy consumption', 'Warning', record.energy_consumption, 200),
        ]
        for issue, severity, value, threshold in checks:
            if value > threshold:
                issues.append({
                    'machine_code': record.machine.machine_code,
                    'machine': record.machine.machine_name,
                    'zone': record.machine.factory_zone,
                    'issue': issue,
                    'severity': severity,
                    'value': as_float(value),
                    'threshold': threshold,
                    'recorded_at': record.recorded_at.isoformat(),
                })
    return Response(issues[:250])


@api_view(['GET'])
def engineering_summary(request):
    """Single endpoint intended for dashboards and interview demos."""

    machine = request.GET.get('machine')

    latest_data = [
        row_to_point(row)
        for row in SensorData.objects.select_related('machine')
        .order_by('-recorded_at')[:20]
    ]

    latest_alerts = [
        {
            'machine_code': row.machine.machine_code,
            'machine_name': row.machine.machine_name,
            'alert_type': row.alert_type,
            'severity': row.severity,
            'message': row.message,
            'created_at': row.created_at.isoformat(),
        }
        for row in Alert.objects.select_related('machine')
        .order_by('-created_at')[:20]
    ]

    quality_issues = []

    for record in SensorData.objects.select_related('machine').all().order_by('-recorded_at')[:200]:
        checks = [
            ('High temperature', 'Critical', record.temperature, 90),
            ('High vibration', 'Warning', record.vibration, 5),
            ('Machine overload', 'Critical', record.load_percentage, 95),
            ('High energy consumption', 'Warning', record.energy_consumption, 200),
        ]

        for issue, severity, value, threshold in checks:
            if value > threshold:
                quality_issues.append({
                    'machine_code': record.machine.machine_code,
                    'machine': record.machine.machine_name,
                    'zone': record.machine.factory_zone,
                    'issue': issue,
                    'severity': severity,
                    'value': as_float(value),
                    'threshold': threshold,
                    'recorded_at': record.recorded_at.isoformat(),
                })

    return Response({
        'health': {
            'status': 'ok',
            'service': 'industrial-field-data-api',
            'version': '4.0.0'
        },
        'kpis': engineering_kpis(),
        'machines': machine_inventory_payload(),
        'load_profiles': hourly_load_profiles(machine),
        'reliability': machine_reliability_summary(),
        'latest_field_data': latest_data,
        'alerts': latest_alerts,
        'data_quality': quality_issues[:50],
    })

@api_view(['GET'])
def machine_detail(request, machine_code):
    """Detailed analytics for a single machine."""

    try:
        machine = Machine.objects.get(machine_code=machine_code)
    except Machine.DoesNotExist:
        return Response({'error': 'Machine not found'}, status=404)

    records = SensorData.objects.select_related('machine').filter(
        machine=machine
    ).order_by('-recorded_at')

    latest_records = [row_to_point(row) for row in records[:50]]

    reliability = next(
        (
            row for row in machine_reliability_summary()
            if row['machine_code'] == machine_code
        ),
        None
    )

    return Response({
        'machine': {
            'machine_code': machine.machine_code,
            'machine_name': machine.machine_name,
            'factory_zone': machine.factory_zone,
            'status': machine.status,
        },
        'records_count': records.count(),
        'latest_records': latest_records,
        'load_profiles': hourly_load_profiles(machine_code),
        'reliability': reliability,
    })

@api_view(['POST'])

def refresh_pyspark_outputs():
    """Generate PySpark-compatible processed analytics outputs from database records."""

    import csv
    from collections import defaultdict

    output_base = Path(__file__).resolve().parent / "pyspark_outputs"
    load_dir = output_base / "load_summary"
    anomalies_dir = output_base / "anomalies"
    metrics_dir = output_base / "global_metrics"

    for folder in [load_dir, anomalies_dir, metrics_dir]:
        folder.mkdir(parents=True, exist_ok=True)

    records = SensorData.objects.select_related("machine").all()

    grouped = defaultdict(list)
    anomalies = []

    total_load = 0
    total_temperature = 0
    total_energy = 0
    total_reliability = 0
    total_records = 0

    for record in records:
        machine = record.machine

        temperature = float(record.temperature)
        vibration = float(record.vibration)
        energy = float(record.energy_consumption)
        load = float(record.load_percentage)

        if temperature >= 90:
            risk_level = "Critical"
            reliability_score = 35
        elif vibration >= 5:
            risk_level = "Warning"
            reliability_score = 55
        elif load >= 95:
            risk_level = "Warning"
            reliability_score = 65
        else:
            risk_level = "Healthy"
            reliability_score = 90

        item = {
            "machine_code": machine.machine_code,
            "machine_name": machine.machine_name,
            "factory_zone": machine.factory_zone,
            "temperature": temperature,
            "vibration": vibration,
            "energy_consumption": energy,
            "load_percentage": load,
            "recorded_at": record.recorded_at.isoformat(),
            "risk_level": risk_level,
            "reliability_score": reliability_score,
        }

        grouped[machine.machine_code].append(item)

        if risk_level in ["Critical", "Warning"]:
            anomalies.append(item)

        total_load += load
        total_temperature += temperature
        total_energy += energy
        total_reliability += reliability_score
        total_records += 1

    load_summary_path = load_dir / "part-00000-generated.csv"

    with open(load_summary_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "machine_code",
            "machine_name",
            "factory_zone",
            "records",
            "avg_load",
            "max_load",
            "avg_temperature",
            "max_temperature",
            "total_energy",
            "avg_reliability_score",
        ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for machine_code, rows in grouped.items():
            writer.writerow({
                "machine_code": machine_code,
                "machine_name": rows[0]["machine_name"],
                "factory_zone": rows[0]["factory_zone"],
                "records": len(rows),
                "avg_load": sum(row["load_percentage"] for row in rows) / len(rows),
                "max_load": max(row["load_percentage"] for row in rows),
                "avg_temperature": sum(row["temperature"] for row in rows) / len(rows),
                "max_temperature": max(row["temperature"] for row in rows),
                "total_energy": sum(row["energy_consumption"] for row in rows),
                "avg_reliability_score": sum(row["reliability_score"] for row in rows) / len(rows),
            })

    anomalies_path = anomalies_dir / "part-00000-generated.csv"

    with open(anomalies_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "machine_code",
            "machine_name",
            "factory_zone",
            "temperature",
            "vibration",
            "energy_consumption",
            "load_percentage",
            "recorded_at",
            "risk_level",
            "reliability_score",
        ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(anomalies)

    metrics_path = metrics_dir / "part-00000-generated.csv"

    with open(metrics_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "total_records",
            "global_avg_load",
            "global_avg_temperature",
            "global_total_energy",
            "global_reliability_score",
        ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        writer.writerow({
            "total_records": total_records,
            "global_avg_load": total_load / total_records if total_records else 0,
            "global_avg_temperature": total_temperature / total_records if total_records else 0,
            "global_total_energy": total_energy,
            "global_reliability_score": total_reliability / total_records if total_records else 0,
        }) 

def upload_telemetry_csv(request):
    """Upload a telemetry CSV file and import records into the database."""

    uploaded_file = request.FILES.get('file')

    if not uploaded_file:
        return Response({'error': 'No CSV file uploaded. Use field name "file".'}, status=400)

    try:
        decoded_file = TextIOWrapper(uploaded_file.file, encoding='utf-8')
        reader = csv.DictReader(decoded_file)

        created_records = 0
        created_machines = 0
        errors = []

        for index, row in enumerate(reader, start=2):
            try:
                machine_code = row.get('machine_code') or row.get('MachineCode') or row.get('machine')
                machine_name = row.get('machine_name') or row.get('MachineName') or machine_code
                factory_zone = row.get('factory_zone') or row.get('FactoryZone') or 'Unknown'

                if not machine_code:
                    errors.append({'row': index, 'error': 'Missing machine_code'})
                    continue

                machine, created = Machine.objects.get_or_create(
                    machine_code=machine_code,
                    defaults={
                        'machine_name': machine_name,
                        'factory_zone': factory_zone,
                        'status': 'Active',
                    }
                )

                if created:
                    created_machines += 1

                recorded_at = (
                    parse_datetime(row.get('recorded_at') or row.get('timestamp') or '')
                )

                SensorData.objects.create(
                    machine=machine,
                    temperature=row.get('temperature') or row.get('temp') or 0,
                    vibration=row.get('vibration') or 0,
                    energy_consumption=row.get('energy_consumption') or row.get('energy') or 0,
                    load_percentage=row.get('load_percentage') or row.get('load') or 0,
                    recorded_at=recorded_at,
                )

                created_records += 1

            except Exception as exc:
                errors.append({'row': index, 'error': str(exc)})
        refresh_pyspark_outputs()    
        return Response({
            'status': 'success',
            'created_records': created_records,
            'created_machines': created_machines,
            'errors': errors[:20],
        })

    except Exception as exc:
        return Response({'error': str(exc)}, status=500)


@api_view(['GET'])
def pyspark_load_summary(request):

    import csv

    file_path = (
        Path(__file__).resolve().parent
        / 'pyspark_outputs'
        / 'load_summary'
    )

    csv_files = list(file_path.glob('part-*.csv'))

    if not csv_files:
        return Response({'error': 'No PySpark load summary found'}, status=404)

    results = []

    with open(csv_files[0], newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            results.append(row)

    return Response(results)


@api_view(['GET'])
def pyspark_anomalies(request):
    """Return processed PySpark anomalies."""

    import csv

    file_path = (
        Path(__file__).resolve().parent
        / 'pyspark_outputs'
        / 'anomalies'
    )

    csv_files = list(file_path.glob('part-*.csv'))

    if not csv_files:
        return Response({'error': 'No PySpark anomalies found'}, status=404)

    results = []

    with open(csv_files[0], newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            results.append(row)

    return Response(results)


@api_view(['GET'])
def pyspark_global_metrics(request):
    """Return processed PySpark global metrics."""

    import csv

    file_path = (
        Path(__file__).resolve().parent
        / 'pyspark_outputs'
        / 'global_metrics'
    )

    csv_files = list(file_path.glob('part-*.csv'))

    if not csv_files:
        return Response({'error': 'No PySpark metrics found'}, status=404)

    results = []

    with open(csv_files[0], newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            results.append(row)

    return Response(results)
