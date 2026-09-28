from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from students.models import StudentAcademic
from projects.models import StudentProject
from quotations.models import Quotation
from payments.models import Payment

from notifications.services import send_student_notification


User = get_user_model()


# =========================================================
# DEFAULT QUOTATION AMOUNT
# =========================================================

DEFAULT_QUOTATION_AMOUNT = Decimal("2500.00")


# =========================================================
# COLLEGE-WISE QUOTATION AMOUNT
# =========================================================

def get_college_quotation_amount(college_name):
    """
    Return quotation amount according to college name.

    ₹1800:
    - Adsul's Technical Campus
    - Vishwabharati Academy's College of Engineering

    ₹2500:
    - Parikrama Faculty of Engineering, Kashti
    - Other colleges
    """

    # -----------------------------------------------------
    # Empty college → default ₹2500
    # -----------------------------------------------------

    if not college_name:
        return DEFAULT_QUOTATION_AMOUNT

    # -----------------------------------------------------
    # Normalize college name
    # -----------------------------------------------------

    college = " ".join(
        str(college_name)
        .strip()
        .lower()
        .split()
    )

    # -----------------------------------------------------
    # DEBUG
    # -----------------------------------------------------

    print(
        "Quotation college checking:",
        repr(college)
    )

    # -----------------------------------------------------
    # ADSUL'S TECHNICAL CAMPUS → ₹1800
    # -----------------------------------------------------

    if "adsul" in college:

        return Decimal("1800.00")

    # -----------------------------------------------------
    # VISHWABHARATI ACADEMY'S COLLEGE OF ENGINEERING
    # → ₹1800
    # -----------------------------------------------------

    if "vishwabharati" in college:

        return Decimal("1800.00")

    # -----------------------------------------------------
    # PARIKRAMA + OTHER COLLEGES → ₹2500
    # -----------------------------------------------------

    return DEFAULT_QUOTATION_AMOUNT


# =========================================================
# GET COLLEGE FROM STUDENT ACADEMIC
# =========================================================

def get_student_college(student):

    """
    Get college name from StudentAcademic.

    Returns:
        college_name
    """

    try:

        academic = (
            StudentAcademic.objects
            .filter(
                student=student
            )
            .first()
        )

        if academic:

            college_name = getattr(
                academic,
                'college',
                ''
            )

            if college_name:

                return str(
                    college_name
                ).strip()

    except Exception as e:

        print(
            "Error while getting college:",
            e
        )

    return ""


# =========================================================
# ADMIN QUOTATIONS LIST
# =========================================================

def admin_quotations(request):

    # -----------------------------------------------------
    # ADMIN AUTHENTICATION
    # -----------------------------------------------------

    if (
        not request.user.is_authenticated
        or not request.user.is_staff
    ):

        return redirect(
            'admin_login'
        )

    # -----------------------------------------------------
    # GET QUOTATIONS
    # -----------------------------------------------------

    quotations = (
        Quotation.objects
        .select_related('student')
        .prefetch_related('payments')
        .order_by('-created_at')
    )

    search = request.GET.get(
        'search',
        ''
    ).strip()

    selected_status = request.GET.get(
        'status',
        ''
    ).strip()

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    if search:

        quotations = quotations.filter(

            Q(
                quotation_id__icontains=search
            )

            |

            Q(
                application_id__icontains=search
            )

            |

            Q(
                project_title__icontains=search
            )

            |

            Q(
                project_domain__icontains=search
            )

            |

            Q(
                student__username__icontains=search
            )

            |

            Q(
                student__email__icontains=search
            )

            |

            Q(
                student__first_name__icontains=search
            )

            |

            Q(
                student__last_name__icontains=search
            )
        )

    # -----------------------------------------------------
    # CONVERT QUERYSET TO LIST
    # -----------------------------------------------------

    quotation_list = list(
        quotations
    )

    # -----------------------------------------------------
    # PAYMENT STATUS
    # -----------------------------------------------------

    for quotation in quotation_list:

        # -------------------------------------------------
        # GET COLLEGE
        # -------------------------------------------------

        college_name = get_student_college(
            quotation.student
        )

        quotation.admin_college = (
            college_name
        )

        # -------------------------------------------------
        # CALCULATE COLLEGE-WISE AMOUNT
        # -------------------------------------------------

        college_amount = (
            get_college_quotation_amount(
                college_name
            )
        )

        # -------------------------------------------------
        # Keep quotation amount correct
        # -------------------------------------------------

        if quotation.amount != college_amount:

            quotation.amount = (
                college_amount
            )

            quotation.save(
                update_fields=[
                    'amount'
                ]
            )

        # -------------------------------------------------
        # CHECK PAID PAYMENT
        # -------------------------------------------------

        paid_payment = (
            quotation.payments
            .filter(
                payment_status='Paid'
            )
            .order_by(
                '-payment_date',
                '-created_at'
            )
            .first()
        )

        quotation.admin_latest_payment = (
            paid_payment
        )

        # -------------------------------------------------
        # DISPLAY STATUS
        # -------------------------------------------------

        if paid_payment:

            quotation.admin_payment_status = (
                'Paid'
            )

            quotation.admin_display_status = (
                'Paid'
            )

        elif quotation.status == 'Rejected':

            quotation.admin_payment_status = (
                'Unpaid'
            )

            quotation.admin_display_status = (
                'Rejected'
            )

        else:

            quotation.admin_payment_status = (
                'Unpaid'
            )

            quotation.admin_display_status = (
                'Ready for Payment'
            )

    # -----------------------------------------------------
    # STATUS FILTER
    # -----------------------------------------------------

    if selected_status == 'Paid':

        quotation_list = [

            quotation

            for quotation in quotation_list

            if (
                quotation.admin_display_status
                == 'Paid'
            )
        ]

    elif selected_status in [
        'Pending',
        'Unpaid',
        'Ready for Payment'
    ]:

        quotation_list = [

            quotation

            for quotation in quotation_list

            if (
                quotation.admin_display_status
                == 'Ready for Payment'
            )

            or

            (
                quotation.admin_payment_status
                == 'Unpaid'
            )
        ]

    elif selected_status == 'Rejected':

        quotation_list = [

            quotation

            for quotation in quotation_list

            if (
                quotation.admin_display_status
                == 'Rejected'
            )
        ]

    # -----------------------------------------------------
    # STATISTICS
    # -----------------------------------------------------

    all_quotations = (
        Quotation.objects
        .prefetch_related('payments')
        .all()
    )

    total = all_quotations.count()

    paid = 0
    ready_for_payment = 0
    unpaid = 0
    rejected = 0

    for quotation in all_quotations:

        has_paid_payment = (
            quotation.payments
            .filter(
                payment_status='Paid'
            )
            .exists()
        )

        if has_paid_payment:

            paid += 1

        elif quotation.status == 'Rejected':

            rejected += 1

        else:

            ready_for_payment += 1

            unpaid += 1

    # -----------------------------------------------------
    # CONTEXT
    # -----------------------------------------------------

    context = {

        'quotations': quotation_list,

        # Main stats
        'total': total,

        'ready_for_payment': (
            ready_for_payment
        ),

        'paid': paid,

        'unpaid': unpaid,

        'rejected': rejected,

        # Old variable compatibility
        'pending': ready_for_payment,

        'accepted': paid,

        'search': search,

        'selected_status': selected_status,
    }

    return render(
        request,
        'admin/quotations/list.html',
        context
    )


# =========================================================
# ADMIN CREATE QUOTATION
# =========================================================
#
# Admin quotation creation is disabled.
# Quotation is automatically generated for the student.
#
# Amount is calculated according to college.
# =========================================================

def admin_quotation_create(request):

    if (
        not request.user.is_authenticated
        or not request.user.is_staff
    ):

        return redirect(
            'admin_login'
        )

    return redirect(
        'admin_quotations'
    )


# =========================================================
# USER QUOTATION
# =========================================================

def user_quotation(request):

    # -----------------------------------------------------
    # USER AUTHENTICATION
    # -----------------------------------------------------

    if not request.user.is_authenticated:

        return redirect(
            'user_login'
        )

    student = request.user

    # -----------------------------------------------------
    # GET LATEST PROJECT
    # -----------------------------------------------------

    project = (
        StudentProject.objects
        .filter(
            student=student
        )
        .order_by('-created_at')
        .first()
    )

    # -----------------------------------------------------
    # IF PROJECT DOES NOT EXIST
    # -----------------------------------------------------

    if not project:

        return render(

            request,

            'user/quotation.html',

            {
                'quotation': None,

                'project': None,

                'fixed_amount': (
                    DEFAULT_QUOTATION_AMOUNT
                ),
            }
        )

    # -----------------------------------------------------
    # GET APPLICATION ID + COLLEGE
    # -----------------------------------------------------

    application_id = ''

    college_name = ''

    try:

        academic = (
            StudentAcademic.objects
            .filter(
                student=student
            )
            .first()
        )

        if academic:

            # -------------------------------------------------
            # COLLEGE
            # -------------------------------------------------

            college_name = getattr(
                academic,
                'college',
                ''
            )

            if college_name:

                college_name = str(
                    college_name
                ).strip()

            # -------------------------------------------------
            # APPLICATION ID
            # -------------------------------------------------

            application_id = getattr(
                academic,
                'application_id',
                ''
            )

            # -------------------------------------------------
            # PROFILE APPLICATION ID FALLBACK
            # -------------------------------------------------

            if not application_id:

                profile = getattr(
                    student,
                    'profile',
                    None
                )

                if profile:

                    application_id = getattr(
                        profile,
                        'application_id',
                        ''
                    )

    except Exception as e:

        print(
            "Academic details error:",
            e
        )

    # -----------------------------------------------------
    # FALLBACK APPLICATION ID
    # -----------------------------------------------------

    if not application_id:

        application_id = (
            f"APP-{student.id:04d}"
        )

    # -----------------------------------------------------
    # GET COLLEGE-WISE QUOTATION AMOUNT
    # -----------------------------------------------------

    quotation_amount = (
        get_college_quotation_amount(
            college_name
        )
    )

    # =====================================================
    # DEBUG
    # =====================================================

    print("====================================")
    print(
        "USER QUOTATION COLLEGE:",
        repr(college_name)
    )
    print(
        "USER QUOTATION AMOUNT:",
        quotation_amount
    )
    print("====================================")

    # -----------------------------------------------------
    # GET EXISTING QUOTATION
    # -----------------------------------------------------

    quotation = (
        Quotation.objects
        .filter(
            student=student,
            project_title=project.project_title
        )
        .order_by('-created_at')
        .first()
    )

    # -----------------------------------------------------
    # CREATE AUTOMATIC QUOTATION
    # -----------------------------------------------------

    if not quotation:

        quotation = Quotation.objects.create(

            application_id=application_id,

            student=student,

            project_title=project.project_title,

            project_domain=project.domain,

            description=project.description,

            amount=quotation_amount,

            admin_remark=(
                f'Project registration charge for '
                f'{college_name or "selected college"}: '
                f'₹{quotation_amount:.2f}.'
            ),

            student_remark='',

            status='Accepted'
        )

        # -------------------------------------------------
        # SEND NOTIFICATION
        # -------------------------------------------------

        student_name = (
            student.get_full_name()
            or student.username
        )

        notification_message = (

            f'Hello {student_name},\n\n'

            'Your project quotation has been generated '
            'automatically.\n\n'

            f'Application ID: '
            f'{application_id}\n'

            f'Quotation ID: '
            f'{quotation.quotation_id}\n'

            f'Project Title: '
            f'{quotation.project_title}\n'

            f'Project Domain: '
            f'{quotation.project_domain}\n'

            f'College: '
            f'{college_name or "N/A"}\n'

            f'Quotation Amount: '
            f'₹{quotation_amount:.2f}\n\n'

            'This is the applicable project registration '
            'charge for your selected college. '

            'You can now proceed to the payment stage.\n\n'

            'Please login to the Student Project Portal '
            'to complete your payment.\n\n'

            'Regards,\n'
            'Code Axis TechSolutions LLP'
        )

        notification_result = (
            send_student_notification(

                student=student,

                subject=(
                    'Quotation Generated | '
                    'Code Axis TechSolutions LLP'
                ),

                message=notification_message
            )
        )

        print(
            'Automatic quotation notification result:',
            notification_result
        )

    # -----------------------------------------------------
    # UPDATE QUOTATION DETAILS
    # -----------------------------------------------------

    quotation.application_id = (
        application_id
    )

    quotation.project_title = (
        project.project_title
    )

    quotation.project_domain = (
        project.domain
    )

    quotation.description = (
        project.description
    )

    # -----------------------------------------------------
    # IMPORTANT:
    # College-wise amount
    # -----------------------------------------------------

    quotation.amount = (
        quotation_amount
    )

    quotation.admin_remark = (
        f'Project registration charge for '
        f'{college_name or "selected college"}: '
        f'₹{quotation_amount:.2f}.'
    )

    quotation.save(
        update_fields=[
            'application_id',
            'project_title',
            'project_domain',
            'description',
            'amount',
            'admin_remark',
            'updated_at'
        ]
    )

    # -----------------------------------------------------
    # CONTEXT
    # -----------------------------------------------------

    context = {

        'quotation': quotation,

        'project': project,

        # Keep this variable for template compatibility
        'fixed_amount': quotation_amount,

        # Additional useful values
        'quotation_amount': quotation_amount,

        'college_name': college_name,
    }

    return render(
        request,
        'user/quotation.html',
        context
    )


# =========================================================
# ADMIN UPDATE QUOTATION
# =========================================================
#
# Admin can update project-related quotation information.
#
# Admin cannot manually change the amount.
# Amount is automatically calculated according to
# student's selected college.
# =========================================================

def admin_quotation_update(
    request,
    quotation_id
):

    if (
        not request.user.is_authenticated
        or not request.user.is_staff
    ):

        return redirect(
            'admin_login'
        )

    quotation = get_object_or_404(
        Quotation,
        quotation_id=quotation_id
    )

    if request.method != 'POST':

        return redirect(
            'admin_quotations'
        )

    # -----------------------------------------------------
    # PROJECT DETAILS
    # -----------------------------------------------------

    project_title = request.POST.get(
        'project_title',
        quotation.project_title
    ).strip()

    project_domain = request.POST.get(
        'project_domain',
        quotation.project_domain
    ).strip()

    description = request.POST.get(
        'description',
        quotation.description
    ).strip()

    admin_remark = request.POST.get(
        'admin_remark',
        quotation.admin_remark
    ).strip()

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not project_title:

        return redirect(
            'admin_quotations'
        )

    # -----------------------------------------------------
    # GET STUDENT COLLEGE
    # -----------------------------------------------------

    student = quotation.student

    college_name = get_student_college(
        student
    )

    # -----------------------------------------------------
    # CALCULATE COLLEGE-WISE AMOUNT
    # -----------------------------------------------------

    quotation_amount = (
        get_college_quotation_amount(
            college_name
        )
    )

    # -----------------------------------------------------
    # UPDATE DETAILS
    # -----------------------------------------------------

    quotation.project_title = (
        project_title
    )

    quotation.project_domain = (
        project_domain
    )

    quotation.description = (
        description
    )

    # -----------------------------------------------------
    # COLLEGE-WISE AMOUNT
    # -----------------------------------------------------

    quotation.amount = (
        quotation_amount
    )

    # -----------------------------------------------------
    # ADMIN REMARK
    # -----------------------------------------------------

    if admin_remark:

        quotation.admin_remark = (
            admin_remark
        )

    else:

        quotation.admin_remark = (
            f'Project registration charge for '
            f'{college_name or "selected college"}: '
            f'₹{quotation_amount:.2f}.'
        )

    # -----------------------------------------------------
    # DO NOT ALLOW ADMIN TO CHANGE PAYMENT STATUS
    # -----------------------------------------------------

    if quotation.status != 'Rejected':

        quotation.status = 'Accepted'

    quotation.save()

    # -----------------------------------------------------
    # SEND UPDATE NOTIFICATION
    # -----------------------------------------------------

    student_name = (
        student.get_full_name()
        or student.username
    )

    notification_subject = (
        'Quotation Updated | '
        'Code Axis TechSolutions LLP'
    )

    notification_message = (

        f'Hello {student_name},\n\n'

        'Your quotation details have been updated.\n\n'

        f'Application ID: '
        f'{quotation.application_id}\n'

        f'Quotation ID: '
        f'{quotation.quotation_id}\n'

        f'Project Title: '
        f'{quotation.project_title}\n'

        f'Project Domain: '
        f'{quotation.project_domain}\n'

        f'College: '
        f'{college_name or "N/A"}\n'

        f'Quotation Amount: '
        f'₹{quotation_amount:.2f}\n\n'

        'Please login to the Student Project Portal '
        'to view the latest quotation details and '
        'proceed with payment.\n\n'

        'Regards,\n'
        'Code Axis TechSolutions LLP'
    )

    notification_result = (
        send_student_notification(

            student=student,

            subject=notification_subject,

            message=notification_message
        )
    )

    print(
        'Quotation update notification result:',
        notification_result
    )

    return redirect(
        'admin_quotations'
    )


# =========================================================
# ADMIN DELETE QUOTATION
# =========================================================

def admin_quotation_delete(
    request,
    quotation_id
):

    if (
        not request.user.is_authenticated
        or not request.user.is_staff
    ):

        return redirect(
            'admin_login'
        )

    quotation = get_object_or_404(
        Quotation,
        quotation_id=quotation_id
    )

    # -----------------------------------------------------
    # DELETE ONLY THROUGH POST
    # -----------------------------------------------------

    if request.method == 'POST':

        quotation.delete()

    return redirect(
        'admin_quotations'
    )