from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import MedicineViewSet, InventoryTransactionViewSet

router = DefaultRouter()
router.register(r"", MedicineViewSet, basename="medicine")
router.register(r"transactions", InventoryTransactionViewSet, basename="inventory-transaction")

urlpatterns = []