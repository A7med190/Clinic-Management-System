from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import F
from django.db import models
from .models import Medicine, InventoryTransaction
from .serializers import MedicineSerializer, InventoryTransactionSerializer


class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["is_active", "category", "requires_prescription"]
    search_fields = ["name", "generic_name", "manufacturer", "category"]
    ordering_fields = ["name", "price", "stock_quantity", "expiry_date", "created_at"]
    ordering = ["name"]
    lookup_field = "pk"

    @action(detail=False, methods=["get"])
    def low_stock(self, request):
        medicines = Medicine.objects.filter(stock_quantity__lte=models.F("reorder_level"), is_active=True)
        serializer = MedicineSerializer(medicines, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def expiring_soon(self, request):
        days = int(request.query_params.get("days", 30))
        threshold = timezone.now().date() + timezone.timedelta(days=days)
        medicines = Medicine.objects.filter(expiry_date__lte=threshold, expiry_date__gte=timezone.now().date(), is_active=True)
        serializer = MedicineSerializer(medicines, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def adjust(self, request, pk=None):
        medicine = self.get_object()
        quantity = int(request.data.get("quantity", 0))
        transaction_type = request.data.get("type", "adjustment")
        notes = request.data.get("notes", "")
        reference = request.data.get("reference", "")
        InventoryTransaction.objects.create(
            medicine=medicine,
            type=transaction_type,
            quantity=quantity,
            notes=notes,
            reference=reference,
            created_by=request.user,
        )
        return Response(MedicineSerializer(medicine).data)


class InventoryTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InventoryTransaction.objects.select_related("medicine", "created_by").all()
    serializer_class = InventoryTransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["medicine", "type", "created_by"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
