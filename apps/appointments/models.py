import uuid
from django.db import models
from django.core.exceptions import ValidationError


class Appointment(models.Model):
    STATUS_CHOICES = (
        ("scheduled", "Scheduled"),
        ("confirmed", "Confirmed"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("no_show", "No Show"),
    )

    TYPE_CHOICES = (
        ("consultation", "Consultation"),
        ("follow_up", "Follow Up"),
        ("emergency", "Emergency"),
        ("routine", "Routine Checkup"),
        ("procedure", "Procedure"),
        ("other", "Other"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    doctor = models.ForeignKey(
        "doctors.Doctor",
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    department = models.ForeignKey(
        "departments.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="consultation")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="scheduled")
    reason = models.TextField(blank=True, default="")
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "appointments"
        ordering = ["-date", "-start_time"]
        indexes = [
            models.Index(fields=["date", "doctor"]),
            models.Index(fields=["date", "patient"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.patient} - {self.doctor} on {self.date} at {self.start_time}"

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")
