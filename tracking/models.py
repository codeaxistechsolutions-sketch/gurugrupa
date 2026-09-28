from django.db import models
from django.contrib.auth.models import User
from projects.models import StudentProject


class ProjectTracking(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('On Hold', 'On Hold'),
    ]

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='project_tracking'
    )

    project = models.OneToOneField(
        StudentProject,
        on_delete=models.CASCADE,
        related_name='tracking'
    )

    application_status = models.CharField(
        max_length=50,
        default='Project Development'
    )

    progress = models.PositiveIntegerField(
        default=0
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='In Progress'
    )

    start_date = models.DateField(
        null=True,
        blank=True
    )

    expected_delivery = models.DateField(
        null=True,
        blank=True
    )

    current_stage = models.CharField(
        max_length=150,
        default='Project Development'
    )

    current_stage_description = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.student.username} - {self.project.project_title}"