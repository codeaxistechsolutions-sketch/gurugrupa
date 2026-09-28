from django.db import models


class ContactMessage(models.Model):

    SUBJECT_CHOICES = [
        ('Registration Related Query', 'Registration Related Query'),
        ('Project Related Query', 'Project Related Query'),
        ('Document Upload Issue', 'Document Upload Issue'),
        ('Quotation Query', 'Quotation Query'),
        ('Payment Issue', 'Payment Issue'),
        ('Project Tracking', 'Project Tracking'),
        ('Technical Support', 'Technical Support'),
        ('Other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('New', 'New'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    ]

    full_name = models.CharField(
        max_length=150
    )

    email = models.EmailField()

    mobile = models.CharField(
        max_length=10
    )

    subject = models.CharField(
        max_length=100,
        choices=SUBJECT_CHOICES
    )

    message = models.TextField()

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='New'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.full_name} - {self.subject}"