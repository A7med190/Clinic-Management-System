from rest_framework import serializers
from .models import Prescription


class PrescriptionSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.user.get_full_name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.user.get_full_name", read_only=True)

    class Meta:
        model = Prescription
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class PrescriptionListSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.user.get_full_name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.user.get_full_name", read_only=True)
    medication_names = serializers.SerializerMethodField()

    class Meta:
        model = Prescription
        fields = (
            "id",
            "patient_name",
            "doctor_name",
            "medication_names",
            "start_date",
            "end_date",
            "status",
            "created_at",
        )

    def get_medication_names(self, obj):
        return [med.get("name", "") for med in obj.medications]
