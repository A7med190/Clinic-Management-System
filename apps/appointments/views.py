from datetime import datetime, timedelta, time
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q
from .models import Appointment
from .serializers import AppointmentSerializer, AppointmentListSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["doctor", "patient", "status", "type", "date"]
    search_fields = ["patient__user__first_name", "patient__user__last_name", "doctor__user__first_name", "doctor__user__last_name"]
    ordering_fields = ["date", "start_time", "created_at"]
    ordering = ["-date", "-start_time"]
    lookup_field = "pk"

    def get_queryset(self):
        user = self.request.user
        qs = Appointment.objects.select_related("patient__user", "doctor__user", "department")
        if hasattr(user, "doctor_profile"):
            return qs.filter(doctor=user.doctor_profile)
        if hasattr(user, "patient_profile"):
            return qs.filter(patient=user.patient_profile)
        return qs.all()

    def get_serializer_class(self):
        if self.action == "list":
            return AppointmentListSerializer
        return AppointmentSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["patch"])
    def status(self, request, pk=None):
        appointment = self.get_object()
        new_status = request.data.get("status")
        if new_status not in dict(Appointment.STATUS_CHOICES):
            return Response({"error": "Invalid status"}, status=400)
        appointment.status = new_status
        appointment.save(update_fields=["status", "updated_at"])
        return Response(AppointmentSerializer(appointment).data)

    @action(detail=True, methods=["post"])
    def check_in(self, request, pk=None):
        appointment = self.get_object()
        appointment.status = "in_progress"
        appointment.save(update_fields=["status", "updated_at"])
        return Response({"message": "Patient checked in", "appointment": AppointmentSerializer(appointment).data})

    @action(detail=True, methods=["post"])
    def check_out(self, request, pk=None):
        appointment = self.get_object()
        appointment.status = "completed"
        appointment.save(update_fields=["status", "updated_at"])
        return Response({"message": "Patient checked out", "appointment": AppointmentSerializer(appointment).data})

    @action(detail=False, methods=["get"])
    def available_slots(self, request):
        doctor_id = request.query_params.get("doctor_id")
        date_str = request.query_params.get("date")
        if not doctor_id or not date_str:
            return Response({"error": "doctor_id and date are required"}, status=400)
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)
        from apps.schedules.models import Schedule
        day_num = (date.weekday() + 1) % 7
        schedules = Schedule.objects.filter(doctor_id=doctor_id, day_of_week=day_num, is_available=True)
        if not schedules.exists():
            return Response({"available_slots": [], "message": "No schedule found for this day"})
        booked = Appointment.objects.filter(doctor_id=doctor_id, date=date).exclude(status__in=["cancelled", "no_show"])
        booked_times = set((a.start_time, a.end_time) for a in booked)
        available_slots = []
        for schedule in schedules:
            current = datetime.combine(date, schedule.start_time)
            end = datetime.combine(date, schedule.end_time)
            duration = timedelta(minutes=schedule.appointment_duration)
            while current + duration <= end:
                slot_start = current.time()
                slot_end = (current + duration).time()
                if (slot_start, slot_end) not in booked_times:
                    available_slots.append({"start_time": slot_start, "end_time": slot_end})
                current += duration
        return Response({"available_slots": available_slots, "date": date_str, "doctor_id": doctor_id})

    @action(detail=False, methods=["get"])
    def today(self, request):
        today = datetime.now().date()
        appointments = self.get_queryset().filter(date=today)
        serializer = AppointmentListSerializer(appointments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        today = datetime.now().date()
        appointments = self.get_queryset().filter(date__gte=today, status__in=["scheduled", "confirmed"])
        serializer = AppointmentListSerializer(appointments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def calendar(self, request):
        start = request.query_params.get("start")
        end = request.query_params.get("end")
        if not start or not end:
            return Response({"error": "start and end dates are required"}, status=400)
        appointments = self.get_queryset().filter(date__gte=start, date__lte=end)
        serializer = AppointmentListSerializer(appointments, many=True)
        return Response(serializer.data)
