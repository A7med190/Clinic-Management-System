from rest_framework import serializers
from .models import MedicalRecord


class MedicalRecordSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.user.get_full_name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.user.get_full_name", read_only=True)

    class Meta:
        model = MedicalRecord
        fields = "__all__"
        read_only_fields = ("id", "visit_date", "created_at", "updated_at")


class MedicalRecordListSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.user.get_full_name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.user.get_full_name", read_only=True)

    class Meta:
        model = MedicalRecord
        fields = (
            "id",
            "patient_name",
            "doctor_name",
            "visit_date",
            "diagnosis",
            "icd_codes",
            "follow_up_date",
            "created_at",
        )
