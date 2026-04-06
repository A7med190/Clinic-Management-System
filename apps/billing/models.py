import uuid
from django.db import models


class Bill(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("partial", "Partially Paid"),
        ("paid", "Paid"),
        ("overdue", "Overdue"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    )

    PAYMENT_METHOD_CHOICES = (
        ("cash", "Cash"),
        ("card", "Credit/Debit Card"),
        ("insurance", "Insurance"),
        ("bank_transfer", "Bank Transfer"),
        ("mobile_payment", "Mobile Payment"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bill_number = models.CharField(max_length=50, unique=True, editable=False)
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="bills",
    )
    appointment = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bills",
    )
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, default="")
    payment_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    insurance_claim_number = models.CharField(max_length=100, blank=True, default="")
    insurance_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bills"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Bill #{self.bill_number} - {self.patient}"

    def save(self, *args, **kwargs):
        if not self.bill_number:
            prefix = "BILL"
            last = Bill.objects.order_by("-id").first()
            if last and last.bill_number:
                num = int(last.bill_number.split("-")[-1]) + 1
            else:
                num = 1
            self.bill_number = f"{prefix}-{num:06d}"
        self.total = self.subtotal + self.tax - self.discount
        super().save(*args, **kwargs)

    @property
    def balance(self):
        return self.total - self.paid_amount


class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name="items")
    description = models.CharField(max_length=300)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "bill_items"

    def __str__(self):
        return f"{self.description} x{self.quantity}"

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
