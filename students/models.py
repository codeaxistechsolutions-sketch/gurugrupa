from django.db import models
from django.contrib.auth.models import User
import random


class StudentAcademic(models.Model):

    # ================= APPLICATION STATUS =================

    APPLICATION_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Changes Requested', 'Changes Requested'),
        ('Rejected', 'Rejected'),
    ]

    # ================= STUDENT =================

    student = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='academic'
    )

    # ================= APPLICATION ID =================

    application_id = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        null=True
    )

    # ================= CURRENT ACADEMIC =================

    course = models.CharField(
        max_length=100
    )

    branch = models.CharField(
        max_length=150
    )

    college = models.CharField(
        max_length=200
    )

    university = models.CharField(
        max_length=200
    )

    current_year = models.CharField(
        max_length=50
    )

    semester = models.CharField(
        max_length=50
    )

    academic_year = models.CharField(
        max_length=20
    )

    # ================= APPLICATION REVIEW =================

    application_status = models.CharField(
        max_length=30,
        choices=APPLICATION_STATUS_CHOICES,
        default='Pending'
    )

    admin_remark = models.TextField(
        blank=True,
        default=''
    )

    # ================= TIMESTAMPS =================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # ================= SAVE =================

    def save(self, *args, **kwargs):

        if not self.application_id:

            while True:

                random_number = random.randint(
                    100000,
                    999999
                )

                new_application_id = (
                    f"APP-2026-{random_number}"
                )

                if not StudentAcademic.objects.filter(
                    application_id=new_application_id
                ).exists():

                    self.application_id = (
                        new_application_id
                    )

                    break

        super().save(*args, **kwargs)

    # ================= STRING =================

    def __str__(self):

        return (
            f"{self.application_id} - "
            f"{self.student.username} - "
            f"{self.course}"
        )


# ============================================================
# APPLICATION ACTION HISTORY
# ============================================================

class ApplicationActionHistory(models.Model):

    ACTION_CHOICES = [
        ('Approved', 'Approved'),
        ('Changes Requested', 'Changes Requested'),
        ('Rejected', 'Rejected'),
    ]

    application = models.ForeignKey(
        StudentAcademic,
        on_delete=models.CASCADE,
        related_name='action_history'
    )

    action = models.CharField(
        max_length=30,
        choices=ACTION_CHOICES
    )

    remark = models.TextField(
        blank=True,
        default=''
    )

    action_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='application_actions'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.application.student.username} - "
            f"{self.action}"
        )