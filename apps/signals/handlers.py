import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


def connect_signals():
    from apps.appointments.models import Appointment
    from apps.billing.models import Invoice
    from apps.medical_records.models import MedicalRecord
    from apps.notifications.models import Notification
    from apps.patients.models import Patient
    from apps.prescriptions.models import Prescription

    for model in [Patient, Appointment, MedicalRecord, Prescription, Invoice, Notification]:
        post_save.connect(_handle_save, sender=model)
        post_delete.connect(_handle_delete, sender=model)


def _handle_save(sender, instance, created, **kwargs):
    action = "created" if created else "updated"
    logger.info(f"{sender.__name__} {action}: {instance.pk}")


def _handle_delete(sender, instance, **kwargs):
    logger.info(f"{sender.__name__} deleted: {instance.pk}")
