from django.contrib import admin
from .models import Bill, BillItem


class BillItemInline(admin.TabularInline):
    model = BillItem
    extra = 0


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ("bill_number", "patient", "total", "paid_amount", "status", "payment_method", "created_at")
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("bill_number", "patient__user__first_name", "patient__user__last_name")
    readonly_fields = ("id", "bill_number", "total", "created_at", "updated_at")
    inlines = [BillItemInline]
    date_hierarchy = "created_at"
