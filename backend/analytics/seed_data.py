from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from analytics.models import Machine, SensorData, Alert


def run():
    Alert.objects.all().delete()
    SensorData.objects.all().delete()
    Machine.objects.all().delete()

    machines = [
        Machine.objects.create(machine_code="M001", machine_name="Press Machine 01", factory_zone="Zone A", status="Active"),
        Machine.objects.create(machine_code="M002", machine_name="Assembly Line 02", factory_zone="Zone B", status="Active"),
        Machine.objects.create(machine_code="M003", machine_name="CNC Machine 03", factory_zone="Zone A", status="Active"),
        Machine.objects.create(machine_code="M004", machine_name="Welding Robot 04", factory_zone="Zone C", status="Active"),
        Machine.objects.create(machine_code="M005", machine_name="Packaging Line 05", factory_zone="Zone B", status="Maintenance"),
    ]

    now = timezone.now()

    base_values = [
        ("72.5", "3.2", "145.20", "82.5"),
        ("68.1", "2.8", "120.75", "76.0"),
        ("95.4", "8.9", "188.60", "91.3"),
        ("80.0", "5.5", "160.40", "87.0"),
        ("60.2", "2.1", "98.30", "55.0"),
    ]

    for machine, values in zip(machines, base_values):
        temp, vib, energy, load = values

        for i in range(10):
            SensorData.objects.create(
                machine=machine,
                temperature=Decimal(temp) + Decimal(i),
                vibration=Decimal(vib),
                energy_consumption=Decimal(energy) + Decimal(i * 3),
                load_percentage=Decimal(load) + Decimal(i) / Decimal("2"),
                recorded_at=now - timedelta(hours=i)
            )

    Alert.objects.create(machine=machines[2], alert_type="High Temperature", severity="Critical", message="Temperature above safe threshold")
    Alert.objects.create(machine=machines[2], alert_type="High Vibration", severity="Warning", message="Vibration level requires inspection")
    Alert.objects.create(machine=machines[4], alert_type="Machine Status", severity="Warning", message="Machine currently under maintenance")

    print("Industrial seed data created successfully.")