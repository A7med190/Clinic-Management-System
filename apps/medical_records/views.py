from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import MedicalRecord
from .serializers import MedicalRecordSerializer, MedicalRecordListSerializer


class MedicalRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["patient", "doctor", "visit_date"]
    search_fields = ["diagnosis", "chief_complaint", "icd_codes"]
    ordering_fields = ["visit_date", "created_at"]
    ordering = ["-visit_date"]
    lookup_field = "pk"

    def get_queryset(self):
        user = self.request.user
        qs = MedicalRecord.objects.select_related("patient__user", "doctor__user", "appointment")
        if hasattr(user, "doctor_profile"):
            return qs.filter(doctor=user.doctor_profile)
        if hasattr(user, "patient_profile"):
            return qs.filter(patient=user.patient_profile)
        return qs.all()

    def get_serializer_class(self):
        if self.action == "list":
            return MedicalRecordListSerializer
        return MedicalRecordSerializer

    @action(detail=True, methods=["post"])
    def lab_results(self, request, pk=None):
        record = self.get_object()
        record.lab_results = request.data.get("lab_results", "")
        record.save(update_fields=["lab_results", "updated_at"])
        return Response(MedicalRecordSerializer(record).data)
