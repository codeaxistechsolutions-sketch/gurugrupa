from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings

import razorpay

from .models import Payment
from quotations.models import Quotation
from projects.models import StudentProject
from tracking.models import ProjectTracking

from notifications.services import send_student_notification


# ============================================================
# DEFAULT PROJECT REGISTRATION PAYMENT
# ============================================================
#
# IMPORTANT:
# Actual payment amount quotation.amount मधून घेतला जाईल.
#
# Default amount फक्त quotation मध्ये amount invalid/empty
# असल्यास fallback म्हणून वापरला जाईल.
# ============================================================

DEFAULT_PAYMENT_AMOUNT = Decimal("2500.00")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_student_quotation(student):
    """
    Get the latest quotation for the logged-in student.

    Admin approval is NOT required.
    """

    return (
        Quotation.objects
        .filter(student=student)
        .order_by('-id')
        .first()
    )


def get_student_project(student):
    """
    Get the latest project of the logged-in student.
    """

    return (
        StudentProject.objects
        .filter(student=student)
        .order_by('-created_at')
        .first()
    )


def get_student_profile(student):
    """
    Safely get student profile.
    """

    try:

        return student.profile

    except Exception:

        return None


# ============================================================
# GET ACTUAL QUOTATION PAYMENT AMOUNT
# ============================================================

def get_quotation_amount(quotation):
    """
    Get the actual payment amount from quotation.

    College-wise amount has already been calculated in
    projects/views.py and stored in quotation.amount.

    Therefore Razorpay should always use quotation.amount.
    """

    if quotation.amount is None:

        return DEFAULT_PAYMENT_AMOUNT

    try:

        amount = Decimal(str(quotation.amount))

    except (ValueError, TypeError):

        return DEFAULT_PAYMENT_AMOUNT

    if amount <= 0:

        return DEFAULT_PAYMENT_AMOUNT

    return amount.quantize(
        Decimal("0.01")
    )


# ============================================================
# PAYMENT PAGE
# ============================================================

@login_required
def payment_view(request):

    # --------------------------------------------------------
    # GET LATEST QUOTATION
    # --------------------------------------------------------

    quotation = get_student_quotation(request.user)

    # --------------------------------------------------------
    # NO QUOTATION
    # --------------------------------------------------------

    if quotation is None:

        messages.error(
            request,
            'Please complete your project details first.'
        )

        return redirect(
            'user_project_details'
        )

    # --------------------------------------------------------
    # GET ACTUAL QUOTATION AMOUNT
    # --------------------------------------------------------

    amount = get_quotation_amount(
        quotation
    )

    # --------------------------------------------------------
    # CHECK ALREADY PAID PAYMENT
    # --------------------------------------------------------

    payment = (
        Payment.objects
        .filter(
            student=request.user,
            quotation=quotation
        )
        .order_by('-id')
        .first()
    )

    # --------------------------------------------------------
    # GET PROJECT
    # --------------------------------------------------------

    project = get_student_project(
        request.user
    )

    # --------------------------------------------------------
    # GET PROFILE
    # --------------------------------------------------------

    profile = get_student_profile(
        request.user
    )

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context = {

        'quotation':
            quotation,

        'project':
            project,

        'profile':
            profile,

        'user':
            request.user,

        'payment':
            payment,

        # Actual quotation amount
        'amount':
            amount,

        # Keep this variable if payment.html
        # currently uses fixed_amount.
        'fixed_amount':
            amount,
    }

    return render(
        request,
        'user/payment/payment.html',
        context
    )


# ============================================================
# RAZORPAY CREATE ORDER
# ============================================================

@login_required
def create_razorpay_order(request):

    # --------------------------------------------------------
    # ONLY POST REQUEST
    # --------------------------------------------------------

    if request.method != 'POST':

        return redirect(
            'user_payment'
        )

    # --------------------------------------------------------
    # GET LATEST QUOTATION
    #
    # IMPORTANT:
    # No Accepted status required.
    # --------------------------------------------------------

    quotation = get_student_quotation(
        request.user
    )

    # --------------------------------------------------------
    # NO QUOTATION
    # --------------------------------------------------------

    if quotation is None:

        messages.error(
            request,
            'Please complete your project details first.'
        )

        return redirect(
            'user_project_details'
        )

    # --------------------------------------------------------
    # GET ACTUAL QUOTATION AMOUNT
    #
    # IMPORTANT:
    # NEVER TRUST USER-SIDE AMOUNT.
    #
    # Amount comes directly from database quotation.
    # --------------------------------------------------------

    amount = get_quotation_amount(
        quotation
    )

    # --------------------------------------------------------
    # MAKE SURE QUOTATION HAS VALID AMOUNT
    # --------------------------------------------------------

    if quotation.amount != amount:

        quotation.amount = amount

        quotation.save(
            update_fields=[
                'amount',
                'updated_at'
            ]
        )

    # --------------------------------------------------------
    # CHECK ALREADY PAID
    # --------------------------------------------------------

    existing_payment = (
        Payment.objects
        .filter(
            student=request.user,
            quotation=quotation,
            payment_status='Paid'
        )
        .order_by('-id')
        .first()
    )

    if existing_payment:

        messages.info(
            request,
            'Payment for this quotation has already been completed.'
        )

        return redirect(
            'payment_receipt',
            payment_id=existing_payment.id
        )

    # --------------------------------------------------------
    # RAZORPAY AMOUNT IN PAISE
    #
    # Example:
    #
    # ₹1,800 × 100 = 180000 paise
    #
    # ₹2,500 × 100 = 250000 paise
    # --------------------------------------------------------

    amount_in_paise = int(
        amount * Decimal('100')
    )

    # --------------------------------------------------------
    # RAZORPAY CLIENT
    # --------------------------------------------------------

    try:

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        # ----------------------------------------------------
        # CREATE RAZORPAY ORDER
        # ----------------------------------------------------

        razorpay_order = client.order.create({

            'amount':
                amount_in_paise,

            'currency':
                'INR',

            'receipt':
                f'quotation_{quotation.id}',

            'notes': {

                'student_id':
                    str(request.user.id),

                'quotation_id':
                    str(quotation.id),

                'quotation_number':
                    str(
                        quotation.quotation_id
                    ),

                'application_id':
                    str(
                        quotation.application_id
                    ),

                'project_title':
                    str(
                        quotation.project_title
                    ),

                'quotation_amount':
                    str(amount),
            }
        })

    except Exception as e:

        print(
            'Razorpay order creation error:',
            e
        )

        messages.error(
            request,
            'Unable to create Razorpay order. Please try again.'
        )

        return redirect(
            'user_payment'
        )

    # --------------------------------------------------------
    # CREATE PENDING PAYMENT RECORD
    # --------------------------------------------------------

    payment = Payment.objects.create(

        student=request.user,

        quotation=quotation,

        payment_method='Razorpay',

        upi_id='',

        transaction_reference=
            razorpay_order['id'],

        amount=amount,

        payment_status='Pending',

        payment_date=None,

        razorpay_order_id=
            razorpay_order['id']
    )

    # --------------------------------------------------------
    # GET PROJECT
    # --------------------------------------------------------

    project = get_student_project(
        request.user
    )

    # --------------------------------------------------------
    # GET PROFILE
    # --------------------------------------------------------

    profile = get_student_profile(
        request.user
    )

    # --------------------------------------------------------
    # RAZORPAY CHECKOUT CONTEXT
    # --------------------------------------------------------

    context = {

        'quotation':
            quotation,

        'payment':
            payment,

        'project':
            project,

        'razorpay_order_id':
            razorpay_order['id'],

        'razorpay_key_id':
            settings.RAZORPAY_KEY_ID,

        'razorpay_amount':
            amount_in_paise,

        'amount':
            amount,

        'currency':
            'INR',

        'user':
            request.user,

        'profile':
            profile,
    }

    return render(
        request,
        'user/payment/razorpay_checkout.html',
        context
    )


# ============================================================
# OLD / DEMO PAYMENT FLOW
#
# IMPORTANT:
# Manual card / UPI / bank details are NOT accepted anymore.
# Razorpay is the only actual payment flow.
# ============================================================

@login_required
def confirm_payment(request):

    quotation = get_student_quotation(
        request.user
    )

    if quotation:

        amount = get_quotation_amount(
            quotation
        )

        messages.info(
            request,
            f'Please use Razorpay to complete the '
            f'₹{amount:.2f} payment.'
        )

    else:

        messages.info(
            request,
            'Please complete your project details first.'
        )

    return redirect(
        'user_payment'
    )


# ============================================================
# PAYMENT RECEIPT
# ============================================================

@login_required
def payment_receipt(
    request,
    payment_id
):

    payment = get_object_or_404(

        Payment,

        id=payment_id,

        student=request.user
    )

    # --------------------------------------------------------
    # PROJECT
    # --------------------------------------------------------

    project = get_student_project(
        request.user
    )

    # --------------------------------------------------------
    # PROFILE
    # --------------------------------------------------------

    profile = get_student_profile(
        request.user
    )

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context = {

        'payment':
            payment,

        'quotation':
            payment.quotation,

        'project':
            project,

        'profile':
            profile,

        'user':
            request.user,
    }

    return render(

        request,

        'user/payment/payment_receipt.html',

        context
    )


# ============================================================
# RAZORPAY PAYMENT VERIFICATION
# ============================================================

@login_required
def verify_razorpay_payment(request):

    # --------------------------------------------------------
    # ONLY POST REQUEST
    # --------------------------------------------------------

    if request.method != 'POST':

        return redirect(
            'user_payment'
        )

    # --------------------------------------------------------
    # GET RAZORPAY DATA
    # --------------------------------------------------------

    razorpay_payment_id = request.POST.get(
        'razorpay_payment_id',
        ''
    ).strip()

    razorpay_order_id = request.POST.get(
        'razorpay_order_id',
        ''
    ).strip()

    razorpay_signature = request.POST.get(
        'razorpay_signature',
        ''
    ).strip()

    # --------------------------------------------------------
    # BASIC VALIDATION
    # --------------------------------------------------------

    if not razorpay_payment_id:

        messages.error(
            request,
            'Razorpay payment ID is missing.'
        )

        return redirect(
            'user_payment'
        )

    if not razorpay_order_id:

        messages.error(
            request,
            'Razorpay order ID is missing.'
        )

        return redirect(
            'user_payment'
        )

    if not razorpay_signature:

        messages.error(
            request,
            'Razorpay payment signature is missing.'
        )

        return redirect(
            'user_payment'
        )

    # --------------------------------------------------------
    # FIND PAYMENT
    #
    # IMPORTANT:
    # Payment must belong to logged-in student.
    # --------------------------------------------------------

    payment = get_object_or_404(

        Payment,

        student=request.user,

        razorpay_order_id=
            razorpay_order_id
    )

    # --------------------------------------------------------
    # CHECK QUOTATION
    # --------------------------------------------------------

    quotation = payment.quotation

    if quotation is None:

        messages.error(
            request,
            'Quotation associated with this payment was not found.'
        )

        return redirect(
            'user_payment'
        )

    # --------------------------------------------------------
    # GET EXPECTED AMOUNT FROM QUOTATION
    # --------------------------------------------------------

    expected_amount = get_quotation_amount(
        quotation
    )

    # --------------------------------------------------------
    # ALREADY PAID
    # --------------------------------------------------------

    if payment.payment_status == 'Paid':

        messages.info(
            request,
            'This payment has already been completed.'
        )

        return redirect(
            'payment_receipt',
            payment_id=payment.id
        )

    # --------------------------------------------------------
    # RAZORPAY CLIENT
    # --------------------------------------------------------

    try:

        client = razorpay.Client(

            auth=(

                settings.RAZORPAY_KEY_ID,

                settings.RAZORPAY_KEY_SECRET

            )
        )

        # ----------------------------------------------------
        # VERIFY SIGNATURE
        # ----------------------------------------------------

        client.utility.verify_payment_signature({

            'razorpay_order_id':
                razorpay_order_id,

            'razorpay_payment_id':
                razorpay_payment_id,

            'razorpay_signature':
                razorpay_signature

        })

        # ----------------------------------------------------
        # FETCH ACTUAL PAYMENT DETAILS
        # ----------------------------------------------------

        razorpay_payment = (
            client.payment.fetch(
                razorpay_payment_id
            )
        )

    except razorpay.errors.SignatureVerificationError:

        messages.error(
            request,
            'Payment verification failed. Invalid Razorpay signature.'
        )

        return redirect(
            'user_payment'
        )

    except Exception as e:

        print(
            'Razorpay verification error:',
            e
        )

        messages.error(
            request,
            'Unable to verify payment. Please contact support.'
        )

        return redirect(
            'user_payment'
        )

    # ========================================================
    # VERIFY PAYMENT AMOUNT
    #
    # IMPORTANT:
    # Expected amount comes from quotation.amount.
    #
    # Example:
    #
    # Adsul's       → ₹1,800 → 180000 paise
    # Vishwabharati  → ₹1,800 → 180000 paise
    # Parikrama      → ₹2,500 → 250000 paise
    # Other College  → ₹2,500 → 250000 paise
    # ========================================================

    expected_amount_in_paise = int(
        expected_amount * Decimal('100')
    )

    actual_amount_in_paise = int(
        razorpay_payment.get(
            'amount',
            0
        )
    )

    if actual_amount_in_paise != expected_amount_in_paise:

        print(
            'Razorpay amount mismatch:',
            actual_amount_in_paise,
            'Expected:',
            expected_amount_in_paise
        )

        payment.payment_status = 'Failed'

        payment.save(
            update_fields=[
                'payment_status',
                'updated_at'
            ]
        )

        messages.error(
            request,
            'Payment amount verification failed.'
        )

        return redirect(
            'user_payment'
        )

    # ========================================================
    # VERIFY CURRENCY
    # ========================================================

    actual_currency = (
        razorpay_payment.get(
            'currency',
            ''
        )
    )

    if actual_currency != 'INR':

        payment.payment_status = 'Failed'

        payment.save(
            update_fields=[
                'payment_status',
                'updated_at'
            ]
        )

        messages.error(
            request,
            'Payment currency verification failed.'
        )

        return redirect(
            'user_payment'
        )

    # ========================================================
    # VERIFY PAYMENT STATUS
    # ========================================================

    razorpay_status = (
        razorpay_payment.get(
            'status',
            ''
        )
    )

    if razorpay_status != 'captured':

        print(
            'Razorpay payment status:',
            razorpay_status
        )

        messages.error(
            request,
            'Payment has not been captured by Razorpay.'
        )

        return redirect(
            'user_payment'
        )

    # ========================================================
    # ACTUAL PAYMENT METHOD
    # ========================================================

    razorpay_method = (
        razorpay_payment.get(
            'method',
            ''
        )
    )

    # ========================================================
    # CONVERT RAZORPAY METHOD
    # ========================================================

    if razorpay_method == 'upi':

        actual_payment_method = 'UPI'

    elif razorpay_method == 'card':

        actual_payment_method = 'Card'

    elif razorpay_method == 'netbanking':

        actual_payment_method = 'Net Banking'

    elif razorpay_method == 'wallet':

        actual_payment_method = 'Wallet'

    elif razorpay_method == 'emi':

        actual_payment_method = 'EMI'

    else:

        actual_payment_method = 'Razorpay'

    # ========================================================
    # UPDATE PAYMENT
    # ========================================================

    payment.razorpay_payment_id = (
        razorpay_payment_id
    )

    payment.razorpay_order_id = (
        razorpay_order_id
    )

    payment.razorpay_signature = (
        razorpay_signature
    )

    payment.transaction_reference = (
        razorpay_payment_id
    )

    payment.payment_method = (
        actual_payment_method
    )

    # IMPORTANT:
    # Save actual quotation amount.
    payment.amount = expected_amount

    payment.payment_status = (
        'Paid'
    )

    payment.payment_date = (
        timezone.now()
    )

    payment.save()

    # --------------------------------------------------------
    # LOG
    # --------------------------------------------------------

    print(
        '=============================================='
    )

    print(
        'Razorpay Payment Successful'
    )

    print(
        'Student:',
        request.user.username
    )

    print(
        'Quotation:',
        quotation.quotation_id
    )

    print(
        'Razorpay Order ID:',
        razorpay_order_id
    )

    print(
        'Razorpay Payment ID:',
        razorpay_payment_id
    )

    print(
        'Payment Method:',
        actual_payment_method
    )

    print(
        'Amount:',
        expected_amount
    )

    print(
        '=============================================='
    )

    # ========================================================
    # GET STUDENT PROJECT
    # ========================================================

    project = get_student_project(
        request.user
    )

    if project is None:

        messages.warning(
            request,
            'Payment was successful, but student project was not found.'
        )

        return redirect(
            'payment_receipt',
            payment_id=payment.id
        )

    # ========================================================
    # UPDATE PROJECT TRACKING
    # ========================================================

    tracking, created = (
        ProjectTracking.objects.get_or_create(

            project=project,

            defaults={

                'student':
                    request.user,

                'application_status':
                    'Project Development',

                'progress':
                    65,

                'status':
                    'In Progress',

                'start_date':
                    timezone.localdate(),

                'current_stage':
                    'Project Development',

                'current_stage_description':
                    (
                        'Your project has been assigned to the '
                        'development team. Development work is '
                        'currently in progress.'
                    ),
            }
        )
    )

    # ========================================================
    # UPDATE EXISTING TRACKING
    # ========================================================

    if not created:

        tracking.student = request.user

        tracking.application_status = (
            'Project Development'
        )

        tracking.progress = 65

        tracking.status = (
            'In Progress'
        )

        if not tracking.start_date:

            tracking.start_date = (
                timezone.localdate()
            )

        tracking.current_stage = (
            'Project Development'
        )

        tracking.current_stage_description = (
            'Your project has been assigned to the '
            'development team. Development work is '
            'currently in progress.'
        )

        tracking.save()

    # ========================================================
    # STUDENT NOTIFICATION
    # ========================================================

    student = request.user

    student_name = (
        student.get_full_name()
        or student.username
    )

    payment_date_text = (
        payment.payment_date.strftime(
            "%d-%m-%Y %I:%M %p"
        )
        if payment.payment_date
        else timezone.now().strftime(
            "%d-%m-%Y %I:%M %p"
        )
    )

    notification_message = (

        f'Hello {student_name},\n\n'

        'Your Razorpay payment has been completed '
        'successfully.\n\n'

        f'Application ID: '
        f'{quotation.application_id}\n'

        f'Quotation ID: '
        f'{quotation.quotation_id}\n'

        f'Project Title: '
        f'{quotation.project_title}\n'

        f'Payment ID: '
        f'{payment.id}\n'

        f'Razorpay Payment ID: '
        f'{payment.razorpay_payment_id}\n'

        f'Payment Amount: '
        f'₹{payment.amount:.2f}\n'

        f'Payment Method: '
        f'{payment.payment_method}\n'

        f'Transaction Reference: '
        f'{payment.transaction_reference or "N/A"}\n'

        f'Payment Date: '
        f'{payment_date_text}\n\n'

        'Your project has now moved to the '
        'Project Development stage.\n\n'

        'Current Progress: 65%\n'

        'Current Stage: Project Development\n\n'

        'Please login to the Student Project Portal '
        'for further updates.\n\n'

        'Regards,\n'

        'Code Axis TechSolutions LLP'
    )

    # ========================================================
    # SEND NOTIFICATION
    # ========================================================

    try:

        notification_result = (
            send_student_notification(

                student=student,

                subject=(
                    'Payment Successful | '
                    'Code Axis TechSolutions LLP'
                ),

                message=notification_message

            )
        )

        print(
            'Payment notification result:',
            notification_result
        )

    except Exception as e:

        print(
            'Payment notification error:',
            e
        )

    # ========================================================
    # SUCCESS MESSAGE
    # ========================================================

    messages.success(

        request,

        f'₹{expected_amount:.2f} payment completed '
        f'and verified successfully.'
    )

    # ========================================================
    # RECEIPT
    # ========================================================

    return redirect(
        'payment_receipt',
        payment_id=payment.id
    )