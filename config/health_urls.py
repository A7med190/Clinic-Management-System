from django.urls import path, include
from health_check.views import MainView

urlpatterns = [
    path("health/", MainView.as_view(), name="health_check"),
]
