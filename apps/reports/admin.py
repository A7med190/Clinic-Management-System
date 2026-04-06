from django.contrib import admin
from .models import Report, ReportType


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'report_type', 'generated_by', 'start_date', 'end_date', 'created_at']
    list_filter = ['report_type', 'created_at']
    search_fields = ['title', 'generated_by__email']
    readonly_fields = ['generated_by', 'data', 'file', 'created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Report Information', {
            'fields': ('report_type', 'title', 'generated_by')
        }),
        ('Date Range', {
            'fields': ('start_date', 'end_date')
        }),
        ('Parameters', {
            'fields': ('parameters',)
        }),
        ('Data', {
            'fields': ('data', 'file'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
