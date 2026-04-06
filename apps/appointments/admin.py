from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "doctor", "date", "start_time", "end_time", "type", "status")
    list_filter = ("status", "type", "date")
    search_fields = ("patient__user__first_name", "patient__user__last_name", "doctor__user__first_name", "doctor__user__last_name")
    readonly_fields = ("id", "created_at", "updated_at")
    date_hierarchy = "date"
