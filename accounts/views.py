
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.http import (
    urlsafe_base64_encode,
    urlsafe_base64_decode
)
from django.utils.encoding import (
    force_bytes,
    force_str
)
from django.views.decorators.http import require_POST


import json
import random

# =========================================================
# MODELS
# =========================================================

from .models import UserProfile
from students.models import StudentAcademic
from quotations.models import Quotation


# =========================================================
# GENERATE APPLICATION ID
# =========================================================

def generate_application_id():

    while True:

        year = timezone.now().year

        number = random.randint(
            100000,
            999999
        )

        application_id = f"APP-{year}-{number}"

        if not UserProfile.objects.filter(
            application_id=application_id
        ).exists():

            return application_id


# =========================================================
# REGISTER
# EMAIL OTP VERIFICATION
# =========================================================

@transaction.atomic
def register_view(request):

    if request.method == 'POST':

        # =================================================
        # PERSONAL DETAILS
        # =================================================

        full_name = request.POST.get(
            'full_name',
            ''
        ).strip()

        mobile = request.POST.get(
            'mobile',
            ''
        ).strip()

        email = request.POST.get(
            'email',
            ''
        ).strip()

        gender = request.POST.get(
            'gender',
            ''
        ).strip()

        address = request.POST.get(
            'address',
            ''
        ).strip()

        district = request.POST.get(
            'district',
            ''
        ).strip()

        state = request.POST.get(
            'state',
            ''
        ).strip()

        # =================================================
        # ACADEMIC DETAILS
        # =================================================

        course = request.POST.get(
            'course',
            ''
        ).strip()

        branch = request.POST.get(
            'branch',
            ''
        ).strip()

        college = request.POST.get(
            'college',
            ''
        ).strip()

        university = request.POST.get(
            'university',
            ''
        ).strip()

        current_year = request.POST.get(
            'current_year',
            ''
        ).strip()

        semester = request.POST.get(
            'semester',
            ''
        ).strip()

        academic_year = request.POST.get(
            'academic_year',
            ''
        ).strip()

        # =================================================
        # ACCOUNT DETAILS
        # =================================================

        username = request.POST.get(
            'username',
            ''
        ).strip()

        password = request.POST.get(
            'password',
            ''
        )

        confirm_password = request.POST.get(
            'confirm_password',
            ''
        )

        # =================================================
        # FULL NAME VALIDATION
        # =================================================

        if not full_name:

            messages.error(
                request,
                'Please enter your full name.'
            )

            return redirect(
                'user_register'
            )

        # =================================================
        # MOBILE VALIDATION
        # =================================================

        if not mobile.isdigit() or len(mobile) != 10:

            messages.error(
                request,
                'Please enter a valid 10 digit mobile number.'
            )

            return redirect(
                'user_register'
            )

        # =================================================
        # EMAIL VALIDATION
        # =================================================

        if not email:

            messages.error(
                request,
                'Please enter your email address.'
            )

            return redirect(
                'user_register'
            )

        # =================================================
        # EMAIL OTP VERIFICATION
        # =================================================

        verified_email = request.session.get(
            'registration_verified_email'
        )

        verified_mobile = request.session.get(
            'registration_verified_mobile'
        )

        otp_verified = request.session.get(
            'registration_otp_verified',
            False
        )

        # =================================================
        # OTP VERIFIED CHECK
        # =================================================

        if not otp_verified:

            messages.error(
                request,
                'Please verify your email address with OTP first.'
            )

            return redirect(
                'user_register'
            )

        # =================================================
        # EMAIL MATCH CHECK
        # =================================================

        if not verified_email:

            messages.error(
                request,
                'Email verification not found. Please verify OTP again.'
            )

            return redirect(
                'user_register'
            )

        if verified_email.lower() != email.lower():

            messages.error(
                request,
                'Verified email address does not match the entered email address.'
            )

            return redirect(
                'user_register'
            )

        # =================================================
        # MOBILE MATCH CHECK
        # =================================================

        if verified_mobile != mobile:

            messages.error(
                request,
                'Verified mobile number does not match the entered mobile number.'
            )

            return redirect(
                'user_register'
            )

        # =================================================
        # USERNAME VALIDATION
        # =================================================

        if not username:

            messages.error(
                request,
                'Please enter a username.'
            )

            return redirect(
                'user_register'
            )

        # =================================================
        # PASSWORD VALIDATION
        # =================================================

        if not password:

            messages.error(
                request,
                'Please enter a password.'
            )

            return redirect(
                'user_register'
            )

        if password != confirm_password:

            messages.error(
                request,
                'Password and Confirm Password do not match.'
            )

            return redirect(
                'user_register'
            )

        if len(password) < 8:

            messages.error(
                request,
                'Password must contain at least 8 characters.'
            )

            return redirect(
                'user_register'
            )

        # =================================================
        # USERNAME CHECK
        # =================================================

        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                'Username already exists. Please choose another username.'
            )

            return redirect(
                'user_register'
            )

        # =================================================
        # EMAIL CHECK
        # =================================================

        if User.objects.filter(
            email__iexact=email
        ).exists():

            messages.error(
                request,
                'Email already registered.'
            )

            return redirect(
                'user_register'
            )

        # =================================================
        # MOBILE CHECK
        # =================================================

        if UserProfile.objects.filter(
            mobile=mobile
        ).exists():

            messages.error(
                request,
                'This mobile number is already registered.'
            )

            return redirect(
                'user_register'
            )

        # =================================================
        # CREATE USER
        # =================================================

        user = User.objects.create_user(

            username=username,

            email=email,

            password=password
        )

        # =================================================
        # GENERATE APPLICATION ID
        # =================================================

        application_id = generate_application_id()

        # =================================================
        # CREATE USER PROFILE
        # =================================================

        UserProfile.objects.create(

            user=user,

            full_name=full_name,

            mobile=mobile,

            gender=gender,

            address=address,

            district=district,

            state=state,

            application_id=application_id
        )

        # =================================================
        # CREATE ACADEMIC PROFILE
        # =================================================

        StudentAcademic.objects.create(

            student=user,

            course=course,

            branch=branch,

            college=college,

            university=university,

            current_year=current_year,

            semester=semester,

            academic_year=academic_year
        )

        # =================================================
        # CLEAR OTP SESSION
        # =================================================

        request.session.pop(
            'registration_otp',
            None
        )

        request.session.pop(
            'registration_otp_mobile',
            None
        )

        request.session.pop(
            'registration_otp_email',
            None
        )

        request.session.pop(
            'registration_otp_verified',
            None
        )

        request.session.pop(
            'registration_verified_mobile',
            None
        )

        request.session.pop(
            'registration_verified_email',
            None
        )

        request.session.modified = True

        # =================================================
        # SUCCESS
        # =================================================

        messages.success(
            request,
            f'Registration successful! Your Application ID is {application_id}.'
        )

        # =================================================
        # REDIRECT LOGIN
        # =================================================

        return redirect(
            'user_login'
        )

    # =====================================================
    # GET
    # =====================================================

    return render(
        request,
        'user/auth/register.html'
    )


# =========================================================
# LOGIN
# =========================================================

def login_view(request):

    if request.method == 'POST':

        login_by = request.POST.get(
            'login_by',
            ''
        ).strip()

        login_value = request.POST.get(
            'login_value',
            ''
        ).strip()

        password = request.POST.get(
            'password',
            ''
        )

        # =================================================
        # LOGIN BY EMAIL
        # =================================================

        if login_by == 'email':

            try:

                user_obj = User.objects.get(
                    email__iexact=login_value
                )

                username = user_obj.username

            except User.DoesNotExist:

                messages.error(
                    request,
                    'Invalid email or password.'
                )

                return redirect(
                    'user_login'
                )

        # =================================================
        # LOGIN BY USERNAME
        # =================================================

        elif login_by == 'username':

            username = login_value

        else:

            messages.error(
                request,
                'Please select Login By.'
            )

            return redirect(
                'user_login'
            )

        # =================================================
        # AUTHENTICATE
        # =================================================

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            return redirect(
                'user_dashboard'
            )

        messages.error(
            request,
            'Invalid username/email or password.'
        )

        return redirect(
            'user_login'
        )

    # =====================================================
    # LOGIN PAGE
    # =====================================================

    return render(
        request,
        'user/auth/login.html'
    )


# =========================================================
# LOGOUT
# =========================================================

def logout_view(request):

    logout(request)

    messages.success(
        request,
        'You have been logged out successfully.'
    )

    return redirect(
        'user_login'
    )


# =========================================================
# STUDENT DASHBOARD
# =========================================================

@login_required
def dashboard_view(request):

    # =====================================================
    # ADMIN USER
    # =====================================================

    if request.user.is_staff:

        return redirect(
            'admin_dashboard'
        )

    # =====================================================
    # STUDENT PROFILE
    # =====================================================

    try:

        profile = request.user.profile

    except UserProfile.DoesNotExist:

        messages.error(
            request,
            'Student profile not found. Please contact administrator.'
        )

        logout(request)

        return redirect(
            'user_login'
        )

    # =====================================================
    # STUDENT ACADEMIC PROFILE
    # =====================================================

    try:

        academic = request.user.academic

    except StudentAcademic.DoesNotExist:

        academic = None

    # =====================================================
    # CONTEXT
    # =====================================================

    context = {

        'profile':
            profile,

        'academic':
            academic,

        'user':
            request.user,

    }

    # =====================================================
    # DASHBOARD
    # =====================================================

    return render(
        request,
        'user/dashboard/dashboard.html',
        context
    )


# =========================================================
# STUDENT PROFILE
# =========================================================

@login_required
def profile_view(request):

    # =====================================================
    # ADMIN USER
    # =====================================================

    if request.user.is_staff:

        return redirect(
            'admin_dashboard'
        )

    # =====================================================
    # STUDENT PROFILE
    # =====================================================

    try:

        profile = request.user.profile

    except UserProfile.DoesNotExist:

        messages.error(
            request,
            'Student profile not found. Please contact administrator.'
        )

        logout(request)

        return redirect(
            'user_login'
        )

    # =====================================================
    # STUDENT ACADEMIC PROFILE
    # =====================================================

    try:

        academic = request.user.academic

    except StudentAcademic.DoesNotExist:

        academic = None

    # =====================================================
    # UPDATE PROFILE
    # =====================================================

    if request.method == 'POST':

        full_name = request.POST.get(
            'full_name',
            ''
        ).strip()

        mobile = request.POST.get(
            'mobile',
            ''
        ).strip()

        gender = request.POST.get(
            'gender',
            ''
        ).strip()

        address = request.POST.get(
            'address',
            ''
        ).strip()

        district = request.POST.get(
            'district',
            ''
        ).strip()

        state = request.POST.get(
            'state',
            ''
        ).strip()

        # -------------------------------------------------
        # FULL NAME
        # -------------------------------------------------

        if not full_name:

            messages.error(
                request,
                'Full name is required.'
            )

            return redirect(
                'user_profile'
            )

        # -------------------------------------------------
        # MOBILE
        # -------------------------------------------------

        if not mobile.isdigit() or len(mobile) != 10:

            messages.error(
                request,
                'Please enter a valid 10 digit mobile number.'
            )

            return redirect(
                'user_profile'
            )

        # -------------------------------------------------
        # UPDATE
        # -------------------------------------------------

        profile.full_name = full_name

        profile.mobile = mobile

        profile.gender = gender

        profile.address = address

        profile.district = district

        profile.state = state

        profile.save()

        messages.success(
            request,
            'Profile updated successfully.'
        )

        return redirect(
            'user_profile'
        )

    # =====================================================
    # DISPLAY PROFILE
    # =====================================================

    context = {

        'profile':
            profile,

        'academic':
            academic,

        'user':
            request.user,

    }

    return render(
        request,
        'user/profile/profile.html',
        context
    )


# =========================================================
# STUDENT QUOTATION
# =========================================================

@login_required
def user_quotation(request):

    if request.user.is_staff:

        return redirect(
            'admin_dashboard'
        )

    # =====================================================
    # PROFILE
    # =====================================================

    try:

        profile = request.user.profile

    except UserProfile.DoesNotExist:

        messages.error(
            request,
            'Student profile not found. Please contact administrator.'
        )

        logout(request)

        return redirect(
            'user_login'
        )

    # =====================================================
    # LATEST QUOTATION
    # =====================================================

    quotation = (
        Quotation.objects
        .filter(
            student=request.user
        )
        .order_by(
            '-created_at'
        )
        .first()
    )

    # =====================================================
    # CONTEXT
    # =====================================================

    context = {

        'profile':
            profile,

        'user':
            request.user,

        'quotation':
            quotation,

    }

    return render(
        request,
        'user/quotation/quotation.html',
        context
    )


# =========================================================
# QUOTATION ACTION
# =========================================================

@login_required
def quotation_action(
    request,
    quotation_id,
    action
):

    if request.user.is_staff:

        return redirect(
            'admin_dashboard'
        )

    # =====================================================
    # POST ONLY
    # =====================================================

    if request.method != 'POST':

        return redirect(
            'user_quotation'
        )

    # =====================================================
    # GET QUOTATION
    # =====================================================

    try:

        quotation = Quotation.objects.get(

            quotation_id=quotation_id,

            student=request.user

        )

    except Quotation.DoesNotExist:

        messages.error(
            request,
            'Quotation not found.'
        )

        return redirect(
            'user_quotation'
        )

    # =====================================================
    # ONLY PENDING
    # =====================================================

    if quotation.status != 'Pending':

        messages.warning(
            request,
            f'Quotation is already {quotation.status}.'
        )

        return redirect(
            'user_quotation'
        )

    # =====================================================
    # ACCEPT
    # =====================================================

    if action == 'accept':

        quotation.status = 'Accepted'

        quotation.student_remark = (
            'Quotation accepted by student.'
        )

        quotation.save(
            update_fields=[
                'status',
                'student_remark',
                'updated_at'
            ]
        )

        messages.success(
            request,
            'Quotation accepted successfully. You can proceed to payment.'
        )

        return redirect(
            'user_payment'
        )

    # =====================================================
    # REJECT
    # =====================================================

    elif action == 'reject':

        quotation.status = 'Rejected'

        quotation.student_remark = (
            'Quotation rejected by student.'
        )

        quotation.save(
            update_fields=[
                'status',
                'student_remark',
                'updated_at'
            ]
        )

        messages.success(
            request,
            'Quotation rejected successfully.'
        )

        return redirect(
            'user_quotation'
        )

    # =====================================================
    # INVALID ACTION
    # =====================================================

    messages.error(
        request,
        'Invalid quotation action.'
    )

    return redirect(
        'user_quotation'
    )


# =========================================================
# STUDENT FORGOT PASSWORD
# =========================================================

def user_forgot_password(request):

    if request.method == "POST":

        email = request.POST.get(
            "email",
            ""
        ).strip()

        success_message = (
            "If a student account exists with this email, "
            "a password reset link has been sent."
        )

        try:

            user = User.objects.get(
                email__iexact=email,
                is_staff=False
            )

            # =================================================
            # GENERATE UID
            # =================================================

            uid = urlsafe_base64_encode(
                force_bytes(user.pk)
            )

            # =================================================
            # GENERATE SECURE TOKEN
            # =================================================

            token = default_token_generator.make_token(
                user
            )

            # =================================================
            # CREATE RESET URL
            # =================================================

            reset_url = request.build_absolute_uri(
                reverse(
                    "user_reset_password",
                    kwargs={
                        "uidb64": uid,
                        "token": token
                    }
                )
            )

            # =================================================
            # EMAIL
            # =================================================

            subject = (
                "Student Password Reset | "
                "Student Project Portal"
            )

            message = f"""
Hello,

We received a request to reset your Student Portal password.

Click the link below to create a new password:

{reset_url}

This link is valid only for this password reset request.

If you did not request a password reset, please ignore this email.

Regards,
Code Axis TechSolutions LLP
Student Project Portal
"""

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

        except User.DoesNotExist:

            # =================================================
            # DO NOT REVEAL WHETHER EMAIL EXISTS
            # =================================================

            pass

        return render(
            request,
            "user/auth/forgot_password.html",
            {
                "success":
                    success_message
            }
        )

    return render(
        request,
        "user/auth/forgot_password.html"
    )


# =========================================================
# STUDENT RESET PASSWORD
# =========================================================

def user_reset_password(
    request,
    uidb64,
    token
):

    # =====================================================
    # GET USER
    # =====================================================

    try:

        uid = force_str(
            urlsafe_base64_decode(
                uidb64
            )
        )

        user = User.objects.get(
            pk=uid,
            is_staff=False
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
        User.DoesNotExist
    ):

        user = None

    # =====================================================
    # INVALID / EXPIRED TOKEN
    # =====================================================

    if (
        user is None
        or not default_token_generator.check_token(
            user,
            token
        )
    ):

        return render(
            request,
            "user/auth/reset_password.html",
            {
                "error":
                    "This password reset link is invalid or has expired."
            }
        )

    # =====================================================
    # RESET PASSWORD
    # =====================================================

    if request.method == "POST":

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        # =================================================
        # EMPTY PASSWORD
        # =================================================

        if not password or not confirm_password:

            return render(
                request,
                "user/auth/reset_password.html",
                {
                    "error":
                        "Please enter both passwords."
                }
            )

        # =================================================
        # PASSWORD MATCH
        # =================================================

        if password != confirm_password:

            return render(
                request,
                "user/auth/reset_password.html",
                {
                    "error":
                        "Passwords do not match."
                }
            )

        # =================================================
        # PASSWORD LENGTH
        # =================================================

        if len(password) < 8:

            return render(
                request,
                "user/auth/reset_password.html",
                {
                    "error":
                        "Password must contain at least 8 characters."
                }
            )

        # =================================================
        # SAVE PASSWORD
        # =================================================

        user.set_password(
            password
        )

        user.save()

        # =================================================
        # REDIRECT LOGIN
        # =================================================

        return redirect(
            "user_login"
        )

    # =====================================================
    # RESET PASSWORD PAGE
    # =====================================================

    return render(
        request,
        "user/auth/reset_password.html"
    )


# =========================================================
# SEND REGISTRATION OTP TO EMAIL
# =========================================================

@require_POST
def send_registration_otp(request):

    try:

        data = json.loads(
            request.body
        )

        mobile = data.get(
            'mobile',
            ''
        ).strip()

        email = data.get(
            'email',
            ''
        ).strip()

    except json.JSONDecodeError:

        return JsonResponse({
            'success': False,
            'message': 'Invalid request.'
        }, status=400)

    # =====================================================
    # MOBILE VALIDATION
    # =====================================================

    if not mobile.isdigit() or len(mobile) != 10:

        return JsonResponse({
            'success': False,
            'message': (
                'Please enter a valid 10 digit mobile number.'
            )
        }, status=400)

    # =====================================================
    # EMAIL VALIDATION
    # =====================================================

    if not email:

        return JsonResponse({
            'success': False,
            'message': (
                'Please enter your email address.'
            )
        }, status=400)

    # =====================================================
    # CHECK EXISTING MOBILE
    # =====================================================

    if UserProfile.objects.filter(
        mobile=mobile
    ).exists():

        return JsonResponse({
            'success': False,
            'message': (
                'This mobile number is already registered.'
            )
        }, status=400)

    # =====================================================
    # CHECK EXISTING EMAIL
    # =====================================================

    if User.objects.filter(
        email__iexact=email
    ).exists():

        return JsonResponse({
            'success': False,
            'message': (
                'This email address is already registered.'
            )
        }, status=400)

    # =====================================================
    # GENERATE 6 DIGIT OTP
    # =====================================================

    otp = str(
        random.randint(
            100000,
            999999
        )
    )

    # =====================================================
    # STORE OTP IN SESSION
    # =====================================================

    request.session[
        'registration_otp'
    ] = otp

    request.session[
        'registration_otp_mobile'
    ] = mobile

    request.session[
        'registration_otp_email'
    ] = email

    request.session[
        'registration_otp_verified'
    ] = False

    # =====================================================
    # CLEAR OLD VERIFIED DATA
    # =====================================================

    request.session.pop(
        'registration_verified_mobile',
        None
    )

    request.session.pop(
        'registration_verified_email',
        None
    )

    request.session.modified = True

    # =====================================================
    # EMAIL SUBJECT
    # =====================================================

    subject = (
        'Student Registration OTP | '
        'Code Axis TechSolutions LLP'
    )

    # =====================================================
    # EMAIL MESSAGE
    # =====================================================

    message = f"""
Hello,

Thank you for registering with Code Axis TechSolutions LLP
Student Project Portal.

Your One-Time Password (OTP) for registration verification is:

{otp}

This OTP is valid for the current registration session.

Please do not share this OTP with anyone.

Regards,
Code Axis TechSolutions LLP
Student Project Portal
"""

    # =====================================================
    # SEND OTP EMAIL
    # =====================================================

    try:

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

    except Exception as e:

        print(
            "REGISTRATION OTP EMAIL ERROR:",
            e
        )

        # =================================================
        # REMOVE OTP SESSION IF EMAIL FAILED
        # =================================================

        request.session.pop(
            'registration_otp',
            None
        )

        request.session.pop(
            'registration_otp_mobile',
            None
        )

        request.session.pop(
            'registration_otp_email',
            None
        )

        request.session.pop(
            'registration_otp_verified',
            None
        )

        request.session.modified = True

        return JsonResponse({
            'success': False,
            'message': (
                'Unable to send OTP email. '
                'Please check email configuration.'
            )
        }, status=500)

    # =====================================================
    # SUCCESS
    # =====================================================

    return JsonResponse({
        'success': True,
        'message': (
            'OTP sent successfully to your email address.'
        )
    })


# =========================================================
# VERIFY REGISTRATION OTP
# =========================================================

@require_POST
def verify_registration_otp(request):

    try:

        data = json.loads(
            request.body
        )

        mobile = data.get(
            'mobile',
            ''
        ).strip()

        email = data.get(
            'email',
            ''
        ).strip()

        otp = data.get(
            'otp',
            ''
        ).strip()

    except json.JSONDecodeError:

        return JsonResponse({
            'success': False,
            'message': 'Invalid request.'
        }, status=400)

    # =====================================================
    # MOBILE VALIDATION
    # =====================================================

    if not mobile.isdigit() or len(mobile) != 10:

        return JsonResponse({
            'success': False,
            'message': 'Invalid mobile number.'
        }, status=400)

    # =====================================================
    # EMAIL VALIDATION
    # =====================================================

    if not email:

        return JsonResponse({
            'success': False,
            'message': (
                'Email address is required.'
            )
        }, status=400)

    # =====================================================
    # OTP VALIDATION
    # =====================================================

    if not otp.isdigit() or len(otp) != 6:

        return JsonResponse({
            'success': False,
            'message': (
                'Please enter a valid 6 digit OTP.'
            )
        }, status=400)

    # =====================================================
    # GET SESSION DATA
    # =====================================================

    session_mobile = request.session.get(
        'registration_otp_mobile'
    )

    session_email = request.session.get(
        'registration_otp_email'
    )

    session_otp = request.session.get(
        'registration_otp'
    )

    # =====================================================
    # OTP NOT FOUND
    # =====================================================

    if (
        not session_mobile
        or not session_email
        or not session_otp
    ):

        return JsonResponse({
            'success': False,
            'message': (
                'OTP session expired. '
                'Please send OTP again.'
            )
        }, status=400)

    # =====================================================
    # MOBILE MATCH
    # =====================================================

    if session_mobile != mobile:

        return JsonResponse({
            'success': False,
            'message': (
                'Mobile number does not match '
                'the OTP request.'
            )
        }, status=400)

    # =====================================================
    # EMAIL MATCH
    # =====================================================

    if session_email.lower() != email.lower():

        return JsonResponse({
            'success': False,
            'message': (
                'Email address does not match '
                'the OTP request.'
            )
        }, status=400)

    # =====================================================
    # CHECK EXISTING MOBILE
    # =====================================================

    if UserProfile.objects.filter(
        mobile=mobile
    ).exists():

        return JsonResponse({
            'success': False,
            'message': (
                'This mobile number is already registered.'
            )
        }, status=400)

    # =====================================================
    # CHECK EXISTING EMAIL
    # =====================================================

    if User.objects.filter(
        email__iexact=email
    ).exists():

        return JsonResponse({
            'success': False,
            'message': (
                'This email address is already registered.'
            )
        }, status=400)

    # =====================================================
    # VERIFY OTP
    # =====================================================

    if session_otp != otp:

        return JsonResponse({
            'success': False,
            'message': 'Invalid OTP.'
        }, status=400)

    # =====================================================
    # OTP VERIFIED
    # =====================================================

    request.session[
        'registration_otp_verified'
    ] = True

    request.session[
        'registration_verified_mobile'
    ] = mobile

    request.session[
        'registration_verified_email'
    ] = email

    # =====================================================
    # REMOVE ACTUAL OTP
    # =====================================================

    request.session.pop(
        'registration_otp',
        None
    )

    request.session.modified = True

    # =====================================================
    # SUCCESS
    # =====================================================

    return JsonResponse({
        'success': True,
        'message': (
            'Email OTP verified successfully.'
        )
    })

