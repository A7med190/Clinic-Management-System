from django.contrib import admin
from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("user", "date_of_birth", "gender", "blood_group", "city", "created_at")
    list_filter = ("gender", "blood_group", "city")
    search_fields = ("user__first_name", "user__last_name", "user__email")
    readonly_fields = ("id", "created_at", "updated_at")
