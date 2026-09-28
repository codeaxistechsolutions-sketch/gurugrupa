from django.db import models
from django.contrib.auth.models import User
from quotations.models import Quotation


class Payment(models.Model):

    # =====================================================
    # PAYMENT METHOD
    # =====================================================

    PAYMENT_METHOD_CHOICES = [
        ('Razorpay', 'Razorpay'),
        ('UPI', 'UPI'),
        ('Card', 'Debit / Credit Card'),
        ('Net Banking', 'Net Banking'),
        ('Wallet', 'Wallet'),
        ('EMI', 'EMI'),
    ]

    # =====================================================
    # PAYMENT STATUS
    # =====================================================

    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
    ]

    # =====================================================
    # BASIC PAYMENT DETAILS
    # =====================================================

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    payment_method = models.CharField(
        max_length=30,
        choices=PAYMENT_METHOD_CHOICES,
        default='Razorpay'
    )

    upi_id = models.CharField(
        max_length=100,
        blank=True
    )

    transaction_reference = models.CharField(
        max_length=100
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='Pending'
    )

    payment_date = models.DateTimeField(
        null=True,
        blank=True
    )

    # =====================================================
    # RAZORPAY DETAILS
    # =====================================================

    razorpay_order_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    razorpay_payment_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    razorpay_signature = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    # =====================================================
    # TIMESTAMPS
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
        return f"{self.student.username} - {self.transaction_reference}"