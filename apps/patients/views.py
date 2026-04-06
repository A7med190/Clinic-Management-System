from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Patient
from .serializers import PatientSerializer, PatientListSerializer


class PatientViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["gender", "blood_group", "city"]
    search_fields = ["user__first_name", "user__last_name", "user__email", "phone"]
    ordering_fields = ["user__first_name", "user__last_name", "created_at"]
    ordering = ["-created_at"]
    lookup_field = "pk"

    def get_queryset(self):
        return Patient.objects.select_related("user").all()

    def get_serializer_class(self):
        if self.action == "list":
            return PatientListSerializer
        return PatientSerializer

    @action(detail=True, methods=["get"])
    def medical_records(self, request, pk=None):
        patient = self.get_object()
        records = patient.medical_records.select_related("doctor").all()
        from apps.medical_records.serializers import MedicalRecordListSerializer
        serializer = MedicalRecordListSerializer(records, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def appointments(self, request, pk=None):
        patient = self.get_object()
        appointments = patient.appointments.select_related("doctor").all()
        from apps.appointments.serializers import AppointmentListSerializer
        serializer = AppointmentListSerializer(appointments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def prescriptions(self, request, pk=None):
        patient = self.get_object()
        prescriptions = patient.prescriptions.select_related("doctor").all()
        from apps.prescriptions.serializers import PrescriptionListSerializer
        serializer = PrescriptionListSerializer(prescriptions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def bills(self, request, pk=None):
        patient = self.get_object()
        bills = patient.bills.all()
        from apps.billing.serializers import BillListSerializer
        serializer = BillListSerializer(bills, many=True)
        return Response(serializer.data)
