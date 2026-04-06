from django.contrib import admin
from .models import Prescription


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ("patient", "doctor", "start_date", "end_date", "status")
    list_filter = ("status", "start_date")
    search_fields = ("patient__user__first_name", "patient__user__last_name", "medications")
    readonly_fields = ("id", "created_at", "updated_at")
