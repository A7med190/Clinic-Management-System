from datetime import datetime
from decimal import Decimal
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Sum, Count, Q
from django.utils import timezone
from .models import Bill
from .serializers import BillSerializer, BillListSerializer


class BillViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["patient", "status", "payment_method"]
    search_fields = ["bill_number", "patient__user__first_name", "patient__user__last_name"]
    ordering_fields = ["created_at", "total", "paid_amount"]
    ordering = ["-created_at"]
    lookup_field = "pk"

    def get_queryset(self):
        user = self.request.user
        qs = Bill.objects.select_related("patient__user", "appointment")
        if hasattr(user, "patient_profile"):
            return qs.filter(patient=user.patient_profile)
        return qs.all()

    def get_serializer_class(self):
        if self.action == "list":
            return BillListSerializer
        return BillSerializer

    @action(detail=True, methods=["patch"])
    def payment(self, request, pk=None):
        bill = self.get_object()
        amount = Decimal(request.data.get("amount", 0))
        payment_method = request.data.get("payment_method", bill.payment_method)
        if amount <= 0:
            return Response({"error": "Invalid amount"}, status=400)
        bill.paid_amount += amount
        bill.payment_method = payment_method
        bill.payment_date = timezone.now()
        if bill.paid_amount >= bill.total:
            bill.status = "paid"
        elif bill.paid_amount > 0:
            bill.status = "partial"
        bill.save()
        return Response(BillSerializer(bill).data)

    @action(detail=False, methods=["get"])
    def overdue(self, request):
        overdue_bills = self.get_queryset().filter(status="pending", created_at__lt=timezone.now() - timezone.timedelta(days=30))
        serializer = BillListSerializer(overdue_bills, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def revenue(self, request):
        start = request.query_params.get("start")
        end = request.query_params.get("end")
        qs = self.get_queryset().filter(status__in=["paid", "partial"])
        if start and end:
            qs = qs.filter(created_at__date__range=[start, end])
        total_revenue = qs.aggregate(total=Sum("paid_amount"))["total"] or 0
        by_method = qs.values("payment_method").annotate(count=Count("id"), total=Sum("paid_amount"))
        return Response({
            "total_revenue": total_revenue,
            "by_payment_method": list(by_method),
            "period": {"start": start, "end": end},
        })
