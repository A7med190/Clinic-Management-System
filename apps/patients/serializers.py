from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Patient

User = get_user_model()


class PatientSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email")
    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)
    phone = serializers.CharField(source="user.phone", required=False)

    class Meta:
        model = Patient
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def create(self, validated_data):
        user_data = validated_data.pop("user", {})
        email = user_data.get("email", "")
        user = User.objects.create_user(
            username=email.split("@")[0] if email else "",
            email=email,
            first_name=user_data.get("first_name", ""),
            last_name=user_data.get("last_name", ""),
            phone=user_data.get("phone", ""),
            role=User.Role.PATIENT,
        )
        patient = Patient.objects.create(user=user, **validated_data)
        return patient

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()
        return super().update(instance, validated_data)


class PatientListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)

    class Meta:
        model = Patient
        fields = (
            "id",
            "full_name",
            "email",
            "phone",
            "date_of_birth",
            "gender",
            "blood_group",
            "city",
            "created_at",
        )
