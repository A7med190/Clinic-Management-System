from rest_framework import serializers
from .models import Report, ReportType


class ReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.SerializerMethodField()
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)

    class Meta:
        model = Report
        fields = [
            'id',
            'report_type',
            'report_type_display',
            'title',
            'generated_by',
            'generated_by_name',
            'start_date',
            'end_date',
            'parameters',
            'data',
            'file',
            'created_at',
        ]
        read_only_fields = ['id', 'generated_by', 'data', 'file', 'created_at']

    def get_generated_by_name(self, obj):
        if obj.generated_by:
            return obj.generated_by.get_full_name()
        return None


class ReportGenerateSerializer(serializers.Serializer):
    report_type = serializers.ChoiceField(choices=ReportType.choices)
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    title = serializers.CharField(max_length=200, required=False)

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("End date must be after start date")
        return data


class ReportListSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.SerializerMethodField()
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)

    class Meta:
        model = Report
        fields = [
            'id',
            'report_type',
            'report_type_display',
            'title',
            'generated_by_name',
            'start_date',
            'end_date',
            'created_at',
        ]

    def get_generated_by_name(self, obj):
        if obj.generated_by:
            return obj.generated_by.get_full_name()
        return None
