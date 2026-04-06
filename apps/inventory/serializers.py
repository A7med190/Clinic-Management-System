from rest_framework import serializers
from .models import Medicine, InventoryTransaction


class MedicineSerializer(serializers.ModelSerializer):
    is_low_stock = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()

    class Meta:
        model = Medicine
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class InventoryTransactionSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source="medicine.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)

    class Meta:
        model = InventoryTransaction
        fields = "__all__"
        read_only_fields = ("id", "created_at")
