from django.contrib import admin
from .models import MedicalRecord


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ("patient", "doctor", "visit_date", "diagnosis", "follow_up_date")
    list_filter = ("visit_date",)
    search_fields = ("patient__user__first_name", "patient__user__last_name", "diagnosis", "icd_codes")
    readonly_fields = ("id", "visit_date", "created_at", "updated_at")
    date_hierarchy = "visit_date"
