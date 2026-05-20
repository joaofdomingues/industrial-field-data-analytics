from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from .models import Machine, SensorData


class AnalyticsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.machine = Machine.objects.create(
            machine_code="TST-001",
            machine_name="Test Machine",
            factory_zone="Test Zone",
            status="Active",
        )

        SensorData.objects.create(
            machine=self.machine,
            temperature=72.5,
            vibration=2.1,
            energy_consumption=120.5,
            load_percentage=65.0,
            recorded_at=timezone.now(),
        )

    def test_health_endpoint(self):
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "ok")

    def test_machines_endpoint(self):
        response = self.client.get("/machines/")
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["machine_code"], "TST-001")

    def test_kpis_endpoint(self):
        response = self.client.get("/kpis/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("total_records", response.data)
        self.assertEqual(response.data["total_records"], 1)

    def test_engineering_summary_endpoint(self):
        response = self.client.get("/engineering-summary/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("kpis", response.data)
        self.assertIn("machines", response.data)
        self.assertIn("load_profiles", response.data)
        self.assertIn("reliability", response.data)

    def test_machine_detail_endpoint(self):
        response = self.client.get("/machines/TST-001/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["machine"]["machine_code"], "TST-001")

    def test_machine_detail_not_found(self):
        response = self.client.get("/machines/UNKNOWN/")
        self.assertEqual(response.status_code, 404)