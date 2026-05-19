import csv
from decimal import Decimal
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from analytics.models import Alert, Machine, SensorData


class Command(BaseCommand):
    help = 'Import raw or processed machine field data CSV into the Django database.'

    def add_arguments(self, parser):
        parser.add_argument('--file', default='data/raw/machine_data.csv')
        parser.add_argument('--reset', action='store_true')

    def handle(self, *args, **options):
        project_root = Path(__file__).resolve().parents[4]
        csv_path = (project_root / options['file']).resolve()
        if options['reset']:
            Alert.objects.all().delete()
            SensorData.objects.all().delete()
            Machine.objects.all().delete()

        created_records = 0
        with csv_path.open(newline='', encoding='utf-8') as handle:
            for row in csv.DictReader(handle):
                machine, _ = Machine.objects.get_or_create(
                    machine_code=row['machine_code'],
                    defaults={
                        'machine_name': row['machine_name'],
                        'factory_zone': row['factory_zone'],
                        'status': 'Active',
                    },
                )
                SensorData.objects.create(
                    machine=machine,
                    temperature=Decimal(str(row['temperature'])),
                    vibration=Decimal(str(row['vibration'])),
                    energy_consumption=Decimal(str(row['energy_consumption'])),
                    load_percentage=Decimal(str(row['load_percentage'])),
                    recorded_at=timezone.make_aware(parse_datetime(row['recorded_at'])) if timezone.is_naive(parse_datetime(row['recorded_at'])) else parse_datetime(row['recorded_at']),
                )
                created_records += 1

        # Create business-readable alerts from imported telemetry.
        for record in SensorData.objects.select_related('machine').all():
            if record.temperature > 90:
                Alert.objects.get_or_create(
                    machine=record.machine,
                    alert_type='High Temperature',
                    severity='Critical',
                    message=f'{record.machine.machine_name} exceeded safe temperature threshold.',
                )
            if record.vibration > 8:
                Alert.objects.get_or_create(
                    machine=record.machine,
                    alert_type='High Vibration',
                    severity='Warning',
                    message=f'{record.machine.machine_name} requires vibration inspection.',
                )

        self.stdout.write(self.style.SUCCESS(f'Imported {created_records} sensor records from {csv_path}'))
