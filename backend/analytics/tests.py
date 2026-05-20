from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile

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
    
    def test_csv_upload_endpoint(self):
        csv_content = (
            "machine_code,machine_name,factory_zone,temperature,vibration,energy_consumption,load_percentage,recorded_at\n"
            "CSV-001,CSV Test Machine,Upload Zone,70.5,2.2,111.4,66.7,2026-05-19T14:00:00Z\n"
        )

        uploaded_file = SimpleUploadedFile(
            "test_upload.csv",
            csv_content.encode("utf-8"),
            content_type="text/csv",
        )

        response = self.client.post(
            "/upload-csv/",
            {"file": uploaded_file},
            format="multipart",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["created_records"], 1)
        self.assertTrue(Machine.objects.filter(machine_code="CSV-001").exists())