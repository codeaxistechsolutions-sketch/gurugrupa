from django.db import models
from django.contrib.auth.models import User


class StudentDocument(models.Model):

    DOCUMENT_TYPES = [
        ('college_id', 'College ID Card'),
        ('bonafide', 'Bonafide Certificate'),
        ('marksheet', 'Academic Marksheet'),
        ('project_proposal', 'Project Proposal / Synopsis'),
        ('other', 'Other Supporting Document'),
    ]

    STATUS_CHOICES = [
        ('Pending Review', 'Pending Review'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    document_id = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        null=True
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='documents'
    )

    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPES
    )

    file = models.FileField(
        upload_to='students/documents/'
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='Pending Review'
    )

    admin_remark = models.TextField(
        blank=True,
        default=''
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    reviewed_at = models.DateTimeField(
        blank=True,
        null=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'document_type'],
                name='unique_student_document_type'
            )
        ]

        ordering = ['-uploaded_at']

    def save(self, *args, **kwargs):

        if not self.document_id:

            last_document = StudentDocument.objects.order_by('-id').first()

            if last_document:
                next_number = last_document.id + 1
            else:
                next_number = 1

            self.document_id = f"DOC-2026-{next_number:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.document_id} - {self.student.username}"