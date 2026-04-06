from rest_framework import serializers
from .models import Doctor


class DoctorSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)
    specialization_name = serializers.CharField(source="specialization.name", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = Doctor
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class DoctorListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    specialization_name = serializers.CharField(source="specialization.name", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = Doctor
        fields = (
            "id",
            "full_name",
            "email",
            "phone",
            "specialization_name",
            "department_name",
            "experience_years",
            "consultation_fee",
            "status",
            "is_active",
            "photo",
        )
