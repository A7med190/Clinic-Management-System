import uuid
from django.db import models
from django.conf import settings


class Doctor(models.Model):
    STATUS_CHOICES = (
        ("available", "Available"),
        ("busy", "Busy"),
        ("off", "Off"),
        ("on_leave", "On Leave"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_profile",
    )
    specialization = models.ForeignKey(
        "specializations.Specialization",
        on_delete=models.SET_NULL,
        null=True,
        related_name="doctors",
    )
    department = models.ForeignKey(
        "departments.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="doctors",
    )
    qualifications = models.TextField(blank=True, default="", help_text="Comma-separated qualifications")
    experience_years = models.PositiveIntegerField(default=0)
    bio = models.TextField(blank=True, default="")
    photo = models.ImageField(upload_to="doctors/", blank=True, null=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "doctors"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"

    @property
    def full_name(self):
        return f"Dr. {self.user.get_full_name()}"

    @property
    def email(self):
        return self.user.email

    @property
    def phone(self):
        return self.user.phone
