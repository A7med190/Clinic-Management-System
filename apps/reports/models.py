from django.db import models
from django.utils import timezone


class ReportType(models.TextChoices):
    PATIENT_SUMMARY = "patient_summary", "Patient Summary"
    REVENUE_REPORT = "revenue_report", "Revenue Report"
    APPOINTMENT_STATS = "appointment_stats", "Appointment Statistics"
    DOCTOR_PERFORMANCE = "doctor_performance", "Doctor Performance"
    INVENTORY_STATUS = "inventory_status", "Inventory Status"
    BILLING_SUMMARY = "billing_summary", "Billing Summary"


class Report(models.Model):
    report_type = models.CharField(
        max_length=50,
        choices=ReportType.choices,
        default=ReportType.PATIENT_SUMMARY,
    )
    title = models.CharField(max_length=200)
    generated_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="generated_reports",
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    parameters = models.JSONField(default=dict, blank=True)
    data = models.JSONField(default=dict, blank=True)
    file = models.FileField(upload_to="reports/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reports"
        ordering = ["-created_at"]
        verbose_name = "Report"
        verbose_name_plural = "Reports"

    def __str__(self):
        return f"{self.title} ({self.report_type})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    @classmethod
    def generate_patient_summary(cls, start_date=None, end_date=None):
        from apps.patients.models import Patient
        from apps.appointments.models import Appointment

        queryset = Patient.objects.all()
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        total_patients = queryset.count()
        male_count = queryset.filter(gender="male").count()
        female_count = queryset.filter(gender="female").count()
        other_count = queryset.filter(gender="other").count()

        blood_group_stats = {}
        for bg, _ in Patient.BLOOD_GROUP_CHOICES:
            blood_group_stats[bg] = queryset.filter(blood_group=bg).count()

        return {
            "total_patients": total_patients,
            "gender_breakdown": {
                "male": male_count,
                "female": female_count,
                "other": other_count,
            },
            "blood_group_stats": blood_group_stats,
        }

    @classmethod
    def generate_revenue_report(cls, start_date=None, end_date=None):
        from apps.billing.models import Bill

        queryset = Bill.objects.all()
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        total_bills = queryset.count()
        total_revenue = queryset.aggregate(models.Sum("total"))["total__sum"] or 0
        total_paid = queryset.aggregate(models.Sum("paid_amount"))["paid_amount__sum"] or 0
        total_pending = total_revenue - total_paid

        status_breakdown = {}
        for status, _ in Bill.STATUS_CHOICES:
            status_breakdown[status] = {
                "count": queryset.filter(status=status).count(),
                "amount": queryset.filter(status=status).aggregate(models.Sum("total"))["total__sum"] or 0,
            }

        payment_method_stats = {}
        for method, _ in Bill.PAYMENT_METHOD_CHOICES:
            payment_method_stats[method] = queryset.filter(payment_method=method).count()

        return {
            "total_bills": total_bills,
            "total_revenue": float(total_revenue),
            "total_paid": float(total_paid),
            "total_pending": float(total_pending),
            "status_breakdown": status_breakdown,
            "payment_method_stats": payment_method_stats,
        }

    @classmethod
    def generate_appointment_stats(cls, start_date=None, end_date=None):
        from apps.appointments.models import Appointment

        queryset = Appointment.objects.all()
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        total_appointments = queryset.count()
        status_breakdown = {}
        for status, _ in Appointment.STATUS_CHOICES:
            status_breakdown[status] = queryset.filter(status=status).count()

        by_doctor = {}
        doctors = queryset.values_list("doctor_id", flat=True).distinct()
        for doctor_id in doctors:
            if doctor_id:
                doctor_appointments = queryset.filter(doctor_id=doctor_id)
                by_doctor[str(doctor_id)] = {
                    "total": doctor_appointments.count(),
                    "completed": doctor_appointments.filter(status="completed").count(),
                    "cancelled": doctor_appointments.filter(status="cancelled").count(),
                }

        return {
            "total_appointments": total_appointments,
            "status_breakdown": status_breakdown,
            "appointments_by_doctor": by_doctor,
        }

    @classmethod
    def generate_doctor_performance(cls, start_date=None, end_date=None):
        from apps.doctors.models import Doctor
        from apps.appointments.models import Appointment

        doctors = Doctor.objects.all()
        performance_data = []

        for doctor in doctors:
            appointments = appointments_qs = Appointment.objects.filter(doctor=doctor)
            if start_date:
                appointments_qs = appointments_qs.filter(date__gte=start_date)
            if end_date:
                appointments_qs = appointments_qs.filter(date__lte=end_date)

            completed = appointments_qs.filter(status="completed").count()
            cancelled = appointments_qs.filter(status="cancelled").count()
            total = appointments_qs.count()

            performance_data.append({
                "doctor_id": str(doctor.id),
                "doctor_name": str(doctor),
                "specialization": doctor.specialization.name if doctor.specialization else None,
                "total_appointments": total,
                "completed": completed,
                "cancelled": cancelled,
                "completion_rate": (completed / total * 100) if total > 0 else 0,
            })

        return {"doctors": performance_data}

    @classmethod
    def generate_inventory_status(cls, start_date=None, end_date=None):
        from apps.inventory.models import Medicine, InventoryTransaction

        queryset = Medicine.objects.all()

        low_stock = queryset.filter(stock_quantity__lte=models.F("reorder_level")).count()
        out_of_stock = queryset.filter(stock_quantity=0).count()
        total_items = queryset.count()
        total_value = queryset.aggregate(
            total=models.Sum(models.F("stock_quantity") * models.F("unit_price"))
        )["total"] or 0

        expiring_soon = queryset.filter(
            expiry_date__lte=timezone.now() + timezone.timedelta(days=30),
            expiry_date__gte=timezone.now(),
        ).count()

        transactions = InventoryTransaction.objects.all()
        if start_date:
            transactions = transactions.filter(created_at__gte=start_date)
        if end_date:
            transactions = transactions.filter(created_at__lte=end_date)

        transaction_stats = {
            "total_transactions": transactions.count(),
            "adjustments": transactions.filter(transaction_type="adjustment").count(),
            "purchases": transactions.filter(transaction_type="purchase").count(),
            "dispensed": transactions.filter(transaction_type="dispensed").count(),
        }

        return {
            "total_items": total_items,
            "low_stock": low_stock,
            "out_of_stock": out_of_stock,
            "expiring_soon": expiring_soon,
            "total_value": float(total_value),
            "transaction_stats": transaction_stats,
        }
