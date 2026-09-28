from django.contrib import admin
from .models import StudentDocument


@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'document_type',
        'file',
        'status',
        'uploaded_at',
        'updated_at',
    )

    list_filter = (
        'document_type',
        'status',
        'uploaded_at',
    )

    search_fields = (
        'student__username',
        'student__first_name',
        'student__last_name',
        'student__email',
    )

    list_editable = (
        'status',
    )

    readonly_fields = (
        'uploaded_at',
        'updated_at',
    )

    ordering = (
        '-uploaded_at',
    )