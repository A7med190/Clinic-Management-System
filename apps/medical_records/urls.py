from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import MedicalRecordViewSet

router = DefaultRouter()
router.register(r"", MedicalRecordViewSet, basename="medicalrecord")

urlpatterns = router.urls
