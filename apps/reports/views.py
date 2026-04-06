from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Sum, Count, Avg
from django.utils import timezone

from .models import Report, ReportType
from .serializers import ReportSerializer, ReportGenerateSerializer, ReportListSerializer


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filterset_fields = ['report_type']
    search_fields = ['title']
    ordering_fields = ['created_at', 'report_type']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ReportListSerializer
        if self.action == 'generate':
            return ReportGenerateSerializer
        return ReportSerializer

    @action(detail=False, methods=['post'])
    def generate(self, request):
        serializer = ReportGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        report_type = serializer.validated_data['report_type']
        start_date = serializer.validated_data.get('start_date')
        end_date = serializer.validated_data.get('end_date')
        title = serializer.validated_data.get('title', f"{ReportType(report_type).label} Report")
        
        report = Report.objects.create(
            report_type=report_type,
            title=title,
            generated_by=request.user,
            start_date=start_date,
            end_date=end_date,
            parameters={
                'start_date': str(start_date) if start_date else None,
                'end_date': str(end_date) if end_date else None,
            }
        )
        
        if report_type == ReportType.PATIENT_SUMMARY:
            data = Report.generate_patient_summary(start_date, end_date)
        elif report_type == ReportType.REVENUE_REPORT:
            data = Report.generate_revenue_report(start_date, end_date)
        elif report_type == ReportType.APPOINTMENT_STATS:
            data = Report.generate_appointment_stats(start_date, end_date)
        elif report_type == ReportType.DOCTOR_PERFORMANCE:
            data = Report.generate_doctor_performance(start_date, end_date)
        elif report_type == ReportType.INVENTORY_STATUS:
            data = Report.generate_inventory_status(start_date, end_date)
        elif report_type == ReportType.BILLING_SUMMARY:
            data = Report.generate_revenue_report(start_date, end_date)
        else:
            data = {}
        
        report.data = data
        report.save()
        
        return Response(
            ReportSerializer(report).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get'])
    def quick_stats(self, request):
        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        from apps.patients.models import Patient
        from apps.billing.models import Bill
        from apps.appointments.models import Appointment
        from apps.inventory.models import Medicine
        
        stats = {
            'total_patients': Patient.objects.count(),
            'new_patients_this_month': Patient.objects.filter(created_at__gte=month_start).count(),
            'total_revenue': Bill.objects.filter(status='paid').aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0,
            'monthly_revenue': Bill.objects.filter(
                status='paid',
                payment_date__gte=month_start
            ).aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0,
            'pending_bills': Bill.objects.filter(status__in=['pending', 'partial']).count(),
            'today_appointments': Appointment.objects.filter(date=today).count(),
            'completed_appointments_today': Appointment.objects.filter(
                date=today,
                status='completed'
            ).count(),
            'low_stock_items': Medicine.objects.filter(
                stock_quantity__lte=models.F('reorder_level')
            ).count(),
        }
        
        return Response(stats)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        report = self.get_object()
        if report.file:
            return Response({
                'file_url': report.file.url,
                'filename': report.file.name,
            })
        return Response(
            {'error': 'No file attached to this report'},
            status=status.HTTP_404_NOT_FOUND
        )
