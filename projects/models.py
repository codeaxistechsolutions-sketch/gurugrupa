from django.db import models
from django.contrib.auth.models import User


# =========================================================
# STUDENT PROJECT MODEL
# =========================================================

class StudentProject(models.Model):

    # =====================================================
    # PROJECT STATUS
    # =====================================================

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('On Hold', 'On Hold'),
    ]

    # =====================================================
    # ADMIN PROJECT STATUS
    # =====================================================

    ADMIN_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Assigned', 'Assigned'),
        ('In Progress', 'In Progress'),
        ('On Hold', 'On Hold'),
        ('Completed', 'Completed'),
        ('Rejected', 'Rejected'),
    ]

    # =====================================================
    # PROJECT STAGE
    # =====================================================

    STAGE_CHOICES = [
        ('Project Submitted', 'Project Submitted'),
        ('Quotation Generated', 'Quotation Generated'),
        ('Payment Pending', 'Payment Pending'),
        ('Payment Completed', 'Payment Completed'),
        ('Project Assigned', 'Project Assigned'),
        ('Development Started', 'Development Started'),
        ('Development In Progress', 'Development In Progress'),
        ('Testing', 'Testing'),
        ('Final Review', 'Final Review'),
        ('Final Delivery', 'Final Delivery'),
    ]

    # =====================================================
    # STUDENT
    # =====================================================

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='student_projects'
    )

    # =====================================================
    # PROJECT DETAILS
    # =====================================================

    project_title = models.CharField(
        max_length=255
    )

    domain = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    # =====================================================
    # PROJECT TYPE
    # =====================================================

    project_type = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    technology = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    # =====================================================
    # ADMIN / DEVELOPMENT DETAILS
    # =====================================================

    project_manager = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    developer = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    current_stage = models.CharField(
        max_length=100,
        choices=STAGE_CHOICES,
        default='Project Submitted'
    )

    project_status = models.CharField(
        max_length=50,
        choices=ADMIN_STATUS_CHOICES,
        default='Pending'
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    # =====================================================
    # DEADLINE
    # =====================================================

    deadline = models.DateField(
        blank=True,
        null=True
    )

    # =====================================================
    # ADMIN REMARK
    # =====================================================

    admin_remark = models.TextField(
        blank=True,
        null=True
    )

    # =====================================================
    # FINAL PROJECT FILES
    # =====================================================

    final_source_code = models.FileField(
        upload_to='projects/source_code/',
        blank=True,
        null=True
    )

    final_documentation = models.FileField(
        upload_to='projects/documentation/',
        blank=True,
        null=True
    )

    final_ppt = models.FileField(
        upload_to='projects/ppt/',
        blank=True,
        null=True
    )

    final_database_file = models.FileField(
        upload_to='projects/database/',
        blank=True,
        null=True
    )

    # =====================================================
    # SEND TO STUDENT
    # =====================================================

    send_to_student = models.BooleanField(
        default=False
    )

    # =====================================================
    # CREATED / UPDATED
    # =====================================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # =====================================================
    # STRING REPRESENTATION
    # =====================================================

    def __str__(self):

        return (
            f"{self.project_title} - "
            f"{self.student.username}"
        )

    # =====================================================
    # META
    # =====================================================

    class Meta:

        ordering = [
            '-created_at'
        ]

        verbose_name = 'Student Project'

        verbose_name_plural = 'Student Projects'