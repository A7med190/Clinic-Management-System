import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


class MedicalRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="medical_records",
    )
    doctor = models.ForeignKey(
        "doctors.Doctor",
        on_delete=models.CASCADE,
        related_name="medical_records",
    )
    appointment = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medical_record",
    )
    visit_date = models.DateField(auto_now_add=True)
    chief_complaint = models.TextField(blank=True, default="")
    diagnosis = models.TextField(blank=True, default="")
    icd_codes = models.TextField(blank=True, default="", help_text="ICD-10 codes, comma-separated")
    examination_notes = models.TextField(blank=True, default="")
    treatment_plan = models.TextField(blank=True, default="")
    vital_signs = models.JSONField(default=dict, blank=True, help_text='{"bp": "120/80", "temperature": 98.6, "pulse": 72, "weight": 70, "height": 170}')
    lab_orders = models.TextField(blank=True, default="")
    lab_results = models.TextField(blank=True, default="")
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_notes = models.TextField(blank=True, default="")
    attachments = models.FileField(upload_to="medical_records/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "medical_records"
        ordering = ["-visit_date"]
        indexes = [
            models.Index(fields=["patient", "visit_date"]),
            models.Index(fields=["doctor", "visit_date"]),
        ]

    def __str__(self):
        return f"{self.patient} - {self.visit_date}"
