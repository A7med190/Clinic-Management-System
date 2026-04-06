from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Doctor
from .serializers import DoctorSerializer, DoctorListSerializer


class DoctorViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["specialization", "department", "status", "is_active"]
    search_fields = ["user__first_name", "user__last_name", "user__email", "qualifications", "bio"]
    ordering_fields = ["user__first_name", "user__last_name", "experience_years", "consultation_fee", "created_at"]
    ordering = ["-created_at"]
    lookup_field = "pk"

    def get_queryset(self):
        return Doctor.objects.select_related("user", "specialization", "department").all()

    def get_serializer_class(self):
        if self.action == "list":
            return DoctorListSerializer
        return DoctorSerializer

    @action(detail=True, methods=["get"])
    def schedule(self, request, pk=None):
        doctor = self.get_object()
        schedules = doctor.schedules.all()
        from apps.schedules.serializers import ScheduleSerializer
        serializer = ScheduleSerializer(schedules, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def appointments(self, request, pk=None):
        doctor = self.get_object()
        appointments = doctor.appointments.select_related("patient__user").all()
        from apps.appointments.serializers import AppointmentListSerializer
        serializer = AppointmentListSerializer(appointments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def patients(self, request, pk=None):
        doctor = self.get_object()
        patient_ids = doctor.medical_records.values_list("patient_id", flat=True).distinct()
        from apps.patients.models import Patient
        patients = Patient.objects.filter(id__in=patient_ids).select_related("user")
        from apps.patients.serializers import PatientListSerializer
        serializer = PatientListSerializer(patients, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_specialization(self, request):
        specialization_id = request.query_params.get("specialization_id")
        if not specialization_id:
            return Response({"error": "specialization_id is required"}, status=400)
        doctors = self.get_queryset().filter(specialization_id=specialization_id, is_active=True)
        serializer = DoctorListSerializer(doctors, many=True)
        return Response(serializer.data)
