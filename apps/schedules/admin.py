from django.contrib import admin
from .models import Schedule


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("doctor", "day_of_week", "start_time", "end_time", "is_available", "max_appointments")
    list_filter = ("day_of_week", "is_available")
    search_fields = ("doctor__user__first_name", "doctor__user__last_name")
