from django.db import models
from django.contrib.auth.models import User


class Quotation(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]

    quotation_id = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        null=True
    )

    application_id = models.CharField(
        max_length=50,
        blank=True,
        default=''
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='quotations'
    )

    project_title = models.CharField(
        max_length=255,
        blank=True,
        default=''
    )

    project_domain = models.CharField(
        max_length=150,
        blank=True,
        default=''
    )

    description = models.TextField(
        blank=True,
        default=''
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    admin_remark = models.TextField(
        blank=True,
        default=''
    )

    student_remark = models.TextField(
        blank=True,
        default=''
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):

        if not self.quotation_id:

            last_quotation = (
                Quotation.objects
                .order_by('-id')
                .first()
            )

            if last_quotation:
                next_number = last_quotation.id + 1
            else:
                next_number = 1

            self.quotation_id = (
                f"QT-2026-{next_number:04d}"
            )

        super().save(*args, **kwargs)

    def __str__(self):

        return (
            f"{self.quotation_id} - "
            f"{self.student.username}"
        )