from rest_framework import serializers
from .models import Bill, BillItem


class BillItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillItem
        fields = "__all__"


class BillSerializer(serializers.ModelSerializer):
    items = BillItemSerializer(many=True, required=False)
    patient_name = serializers.CharField(source="patient.user.get_full_name", read_only=True)
    balance = serializers.ReadOnlyField()

    class Meta:
        model = Bill
        fields = "__all__"
        read_only_fields = ("id", "bill_number", "total", "created_at", "updated_at")

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        bill = Bill.objects.create(**validated_data)
        for item_data in items_data:
            BillItem.objects.create(bill=bill, **item_data)
        bill.subtotal = sum(item.total for item in bill.items.all())
        bill.save()
        return bill

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                BillItem.objects.create(bill=instance, **item_data)
            instance.subtotal = sum(item.total for item in instance.items.all())
        return super().update(instance, validated_data)


class BillListSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.user.get_full_name", read_only=True)
    balance = serializers.ReadOnlyField()

    class Meta:
        model = Bill
        fields = (
            "id",
            "bill_number",
            "patient_name",
            "subtotal",
            "tax",
            "discount",
            "total",
            "paid_amount",
            "balance",
            "status",
            "payment_method",
            "created_at",
        )
