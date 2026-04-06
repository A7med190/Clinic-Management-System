from django.urls import include, path

urlpatterns = [
    path("auth/", include("apps.users.urls")),
    path("patients/", include("apps.patients.urls")),
    path("doctors/", include("apps.doctors.urls")),
    path("appointments/", include("apps.appointments.urls")),
    path("medical-records/", include("apps.medical_records.urls")),
    path("prescriptions/", include("apps.prescriptions.urls")),
    path("billing/", include("apps.billing.urls")),
    path("inventory/", include("apps.inventory.urls")),
    path("departments/", include("apps.departments.urls")),
    path("services/", include("apps.services.urls")),
    path("schedules/", include("apps.schedules.urls")),
    path("notifications/", include("apps.notifications.urls")),
    path("reports/", include("apps.reports.urls")),
]
