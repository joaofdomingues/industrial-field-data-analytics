from decimal import Decimal
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