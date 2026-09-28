from django.core.mail import send_mail
from django.conf import settings


# =========================================================
# GET STUDENT EMAIL
# =========================================================

def get_student_email(student):

    if not student:
        return None

    email = getattr(
        student,
        'email',
        ''
    )

    if email:
        return email.strip()

    return None


# =========================================================
# GET STUDENT MOBILE
# =========================================================

def get_student_mobile(student):

    if not student:
        return None

    try:

        profile = student.profile

        mobile = getattr(
            profile,
            'mobile',
            ''
        )

        if mobile:
            return mobile.strip()

    except Exception:

        pass

    return None


# =========================================================
# SEND EMAIL
# =========================================================

def send_student_email(
    student,
    subject,
    message
):

    email = get_student_email(student)

    if not email:

        print(
            'Student email not found.'
        )

        return False

    try:

        send_mail(

            subject=subject,

            message=message,

            from_email=settings.DEFAULT_FROM_EMAIL,

            recipient_list=[
                email
            ],

            fail_silently=False,
        )

        print(
            f'Email sent successfully to {email}'
        )

        return True

    except Exception as e:

        print(
            f'Email notification error: {e}'
        )

        return False


# =========================================================
# SEND SMS
# =========================================================

def send_student_sms(
    student,
    message
):

    mobile = get_student_mobile(student)

    if not mobile:

        print(
            'Student mobile number not found.'
        )

        return False

    # -----------------------------------------------------
    # SMS API will be connected here
    # -----------------------------------------------------

    print(
        f'SMS notification prepared for {mobile}'
    )

    print(
        f'Message: {message}'
    )

    return True


# =========================================================
# SEND BOTH EMAIL + SMS
# =========================================================

def send_student_notification(
    student,
    subject,
    message
):

    email_status = send_student_email(
        student=student,
        subject=subject,
        message=message
    )

    sms_status = send_student_sms(
        student=student,
        message=message
    )

    return {
        'email': email_status,
        'sms': sms_status
    }