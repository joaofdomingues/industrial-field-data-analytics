from django.db import models

class Machine(models.Model):
    machine_code = models.CharField(max_length=20, unique=True)
    machine_name = models.CharField(max_length=100)
    factory_zone = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default="Active")

    class Meta:
        db_table = "machines"

class SensorData(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    temperature = models.DecimalField(max_digits=5, decimal_places=2)
    vibration = models.DecimalField(max_digits=5, decimal_places=2)
    energy_consumption = models.DecimalField(max_digits=10, decimal_places=2)
    load_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    recorded_at = models.DateTimeField()

    class Meta:
        db_table = "sensor_data"

class Alert(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=50)
    severity = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alerts"
