from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from analytics.models import Alert, Machine, SensorData


class AnalyticsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.machine = Machine.objects.create(
            machine_code="HP001",
            machine_name="Heat Pump Field Unit 01",
            factory_zone="North Field",
            status="Active",
        )
        now = timezone.now()
        for idx, load in enumerate([65, 72, 91, 97]):
            SensorData.objects.create(
                machine=self.machine,
                temperature=Decimal("70.0") + idx,
                vibration=Decimal("2.5") + idx,
                energy_consumption=Decimal("120.0") + idx * 10,
                load_percentage=Decimal(load),
                recorded_at=now.replace(minute=0, second=0, microsecond=0),
            )
        Alert.objects.create(
            machine=self.machine,
            alert_type="Overload",
            severity="Critical",
            message="Load exceeded safe threshold",
        )

    def test_health_endpoint(self):
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "ok")

    def test_kpis_are_dynamic(self):
        response = self.client.get("/kpis/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total_records"], 4)
        self.assertEqual(response.data["machines"], 1)
        self.assertGreater(response.data["average_load"], 0)

    def test_load_profiles_are_aggregated_by_hour(self):
        response = self.client.get("/load-profiles/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertIn("avg_load", response.data[0])
        self.assertIn("anomaly_events", response.data[0])

    def test_engineering_summary_endpoint(self):
        response = self.client.get("/engineering-summary/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("kpis", response.data)
        self.assertIn("load_profiles", response.data)
        self.assertIn("reliability", response.data)
