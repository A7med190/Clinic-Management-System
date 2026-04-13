from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import SpecializationViewSet

router = DefaultRouter()
router.register(r"", SpecializationViewSet, basename="specialization")

urlpatterns = []