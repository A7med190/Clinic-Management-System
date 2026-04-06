from django.contrib import admin
from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("user", "specialization", "department", "experience_years", "consultation_fee", "status", "is_active")
    list_filter = ("specialization", "department", "status", "is_active")
    search_fields = ("user__first_name", "user__last_name", "user__email", "qualifications")
    readonly_fields = ("id", "created_at", "updated_at")
