from rest_framework import serializers
from .models import Specialization


class SpecializationSerializer(serializers.ModelSerializer):
    doctor_count = serializers.SerializerMethodField()

    class Meta:
        model = Specialization
        fields = "__all__"
        read_only_fields = ("created_at",)

    def get_doctor_count(self, obj):
        return obj.doctors.filter(is_active=True).count()
