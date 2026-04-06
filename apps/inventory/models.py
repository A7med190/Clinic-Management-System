import uuid
from django.db import models
from django.utils import timezone


class Medicine(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True, default="")
    manufacturer = models.CharField(max_length=200, blank=True, default="")
    category = models.CharField(max_length=100, blank=True, default="")
    unit = models.CharField(max_length=20, default="tablet", help_text="tablet, capsule, ml, etc.")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=10, help_text="Alert when stock falls below this")
    batch_number = models.CharField(max_length=100, blank=True, default="")
    expiry_date = models.DateField(null=True, blank=True)
    requires_prescription = models.BooleanField(default=False)
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "medicines"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["expiry_date"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.stock_quantity} {self.unit}s)"

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.reorder_level

    @property
    def is_expired(self):
        return self.expiry_date and self.expiry_date < timezone.now().date()


class InventoryTransaction(models.Model):
    TYPE_CHOICES = (
        ("in", "Stock In"),
        ("out", "Stock Out"),
        ("adjustment", "Adjustment"),
        ("return", "Return"),
        ("expired", "Expired"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name="transactions")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    quantity = models.IntegerField()
    reference = models.CharField(max_length=200, blank=True, default="", help_text="PO number, prescription ID, etc.")
    notes = models.TextField(blank=True, default="")
    created_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inventory_transactions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.medicine} - {self.type} ({self.quantity})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.type == "in":
            self.medicine.stock_quantity += self.quantity
        elif self.type in ("out", "expired"):
            self.medicine.stock_quantity = max(0, self.medicine.stock_quantity - self.quantity)
        elif self.type == "adjustment":
            self.medicine.stock_quantity = self.quantity
        elif self.type == "return":
            self.medicine.stock_quantity += self.quantity
        self.medicine.save(update_fields=["stock_quantity", "updated_at"])
