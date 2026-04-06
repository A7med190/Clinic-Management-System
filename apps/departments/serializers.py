from rest_framework import serializers
from .models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    head_doctor_name = serializers.CharField(source="head_doctor", read_only=True)
    doctor_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")

    def get_doctor_count(self, obj):
        return obj.doctors.filter(is_active=True).count()
