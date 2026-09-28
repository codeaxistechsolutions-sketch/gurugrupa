from django.contrib import admin
from .models import ProjectTracking


@admin.register(ProjectTracking)
class ProjectTrackingAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'project',
        'application_status',
        'progress',
        'status',
        'start_date',
        'expected_delivery',
        'current_stage',
    )

    list_filter = (
        'status',
        'application_status',
    )

    search_fields = (
        'student__username',
        'student__first_name',
        'student__last_name',
        'project__project_title',
    )