from django.contrib import admin
from .models import Medicine, InventoryTransaction


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ("name", "generic_name", "category", "price", "stock_quantity", "reorder_level", "expiry_date", "is_active")
    list_filter = ("is_active", "category", "requires_prescription")
    search_fields = ("name", "generic_name", "manufacturer")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ("medicine", "type", "quantity", "reference", "created_by", "created_at")
    list_filter = ("type", "created_at")
    search_fields = ("medicine__name", "reference", "notes")
    readonly_fields = ("id", "created_at")
