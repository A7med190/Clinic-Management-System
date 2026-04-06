from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Prescription
from .serializers import PrescriptionSerializer, PrescriptionListSerializer


class PrescriptionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["patient", "doctor", "status"]
    search_fields = ["medications"]
    ordering_fields = ["start_date", "end_date", "created_at"]
    ordering = ["-created_at"]
    lookup_field = "pk"

    def get_queryset(self):
        user = self.request.user
        qs = Prescription.objects.select_related("patient__user", "doctor__user", "medical_record")
        if hasattr(user, "doctor_profile"):
            return qs.filter(doctor=user.doctor_profile)
        if hasattr(user, "patient_profile"):
            return qs.filter(patient=user.patient_profile)
        return qs.all()

    def get_serializer_class(self):
        if self.action == "list":
            return PrescriptionListSerializer
        return PrescriptionSerializer

    @action(detail=True, methods=["post"])
    def refill(self, request, pk=None):
        prescription = self.get_object()
        if prescription.status != "active":
            return Response({"error": "Only active prescriptions can be refilled"}, status=400)
        prescription.status = "completed"
        prescription.save(update_fields=["status", "updated_at"])
        return Response({"message": "Prescription refilled", "prescription": PrescriptionSerializer(prescription).data})
