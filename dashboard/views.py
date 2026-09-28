from decimal import Decimal, InvalidOperation
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.shortcuts import render, redirect

from django.core.mail import send_mail
from django.conf import settings

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.contrib.auth import (
    authenticate,
    login,
    logout,
    get_user_model,
)

from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse

from accounts.models import UserProfile

from students.models import (
    StudentAcademic,
    ApplicationActionHistory,
)

from projects.models import StudentProject

from quotations.models import Quotation

from payments.models import Payment

# ============================================================
# STUDENT NOTIFICATION SERVICE
# ============================================================

from notifications.services import (
    send_student_notification
)


# ============================================================
# ADMIN LOGIN
# ============================================================

def admin_login(request):

    if (
        request.user.is_authenticated
        and request.user.is_staff
    ):
        return redirect('admin_dashboard')

    if request.method == 'POST':

        login_value = request.POST.get(
            'login_value',
            ''
        ).strip()

        password = request.POST.get(
            'password',
            ''
        )

        User = get_user_model()

        user = None

        try:

            user_obj = User.objects.get(
                email__iexact=login_value
            )

            user = authenticate(
                request,
                username=user_obj.get_username(),
                password=password
            )

        except User.DoesNotExist:

            user = None

        if user is not None:

            if user.is_staff:

                login(
                    request,
                    user
                )

                return redirect(
                    'admin_dashboard'
                )

            return render(
                request,
                'admin/auth/login.html',
                {
                    'error':
                        'You are not authorized to access Admin Panel.'
                }
            )

        return render(
            request,
            'admin/auth/login.html',
            {
                'error':
                    'Invalid admin email or password.'
            }
        )

    return render(
        request,
        'admin/auth/login.html'
    )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

def admin_dashboard(request):

    if not request.user.is_authenticated:
        return redirect('admin_login')

    if not request.user.is_staff:
        return redirect('admin_login')

    # ========================================================
    # STUDENT STATISTICS
    # ========================================================

    total_students = (
        UserProfile.objects.count()
    )

    # ========================================================
    # APPLICATION STATISTICS
    # ========================================================

    total_applications = (
        StudentAcademic.objects.count()
    )

    pending_applications = (
        StudentAcademic.objects.filter(
            application_status='Pending'
        ).count()
    )

    approved_applications = (
        StudentAcademic.objects.filter(
            application_status='Approved'
        ).count()
    )

    changes_requested_applications = (
        StudentAcademic.objects.filter(
            application_status='Changes Requested'
        ).count()
    )

    rejected_applications = (
        StudentAcademic.objects.filter(
            application_status='Rejected'
        ).count()
    )

    # ========================================================
    # PROJECT STATISTICS
    # ========================================================

    total_projects = (
        StudentProject.objects.count()
    )

    pending_projects = (
        StudentProject.objects.filter(
            status='Pending'
        ).count()
    )

    active_projects = (
        StudentProject.objects.filter(
            status='In Progress'
        ).count()
    )

    completed_projects = (
        StudentProject.objects.filter(
            status='Completed'
        ).count()
    )

    on_hold_projects = (
        StudentProject.objects.filter(
            status='On Hold'
        ).count()
    )

    # ========================================================
    # QUOTATION STATISTICS
    # ========================================================

    total_quotations = (
        Quotation.objects.count()
    )

    pending_quotations = (
        Quotation.objects.filter(
            status='Pending'
        ).count()
    )

    accepted_quotations = (
        Quotation.objects.filter(
            status='Accepted'
        ).count()
    )

    rejected_quotations = (
        Quotation.objects.filter(
            status='Rejected'
        ).count()
    )

    # ========================================================
    # PAYMENT STATISTICS
    # ========================================================

    total_payments = (
        Payment.objects.count()
    )

    pending_payments = (
        Payment.objects.filter(
            payment_status='Pending'
        ).count()
    )

    paid_payments = (
        Payment.objects.filter(
            payment_status='Paid'
        ).count()
    )

    failed_payments = (
        Payment.objects.filter(
            payment_status='Failed'
        ).count()
    )

    # ========================================================
    # RECENT STUDENTS
    # ========================================================

    recent_students = (
        UserProfile.objects
        .select_related('user')
        .order_by('-created_at')[:10]
    )

    # ========================================================
    # RECENT PROJECTS
    # ========================================================

    recent_projects = (
        StudentProject.objects
        .select_related('student')
        .order_by('-created_at')[:10]
    )

    # ========================================================
    # RECENT QUOTATIONS
    # ========================================================

    recent_quotations = (
        Quotation.objects
        .select_related('student')
        .order_by('-created_at')[:10]
    )

    # ========================================================
    # RECENT PAYMENTS
    # ========================================================

    recent_payments = (
        Payment.objects
        .select_related(
            'student',
            'quotation'
        )
        .order_by('-created_at')[:10]
    )

    context = {

        'total_students':
            total_students,

        'total_applications':
            total_applications,

        'pending_applications':
            pending_applications,

        'approved_applications':
            approved_applications,

        'changes_requested_applications':
            changes_requested_applications,

        'rejected_applications':
            rejected_applications,

        'total_projects':
            total_projects,

        'pending_projects':
            pending_projects,

        'active_projects':
            active_projects,

        'completed_projects':
            completed_projects,

        'on_hold_projects':
            on_hold_projects,

        'total_quotations':
            total_quotations,

        'pending_quotations':
            pending_quotations,

        'accepted_quotations':
            accepted_quotations,

        'rejected_quotations':
            rejected_quotations,

        'total_payments':
            total_payments,

        'pending_payments':
            pending_payments,

        'paid_payments':
            paid_payments,

        'failed_payments':
            failed_payments,

        'recent_students':
            recent_students,

        'recent_projects':
            recent_projects,

        'recent_quotations':
            recent_quotations,

        'recent_payments':
            recent_payments,
    }

    return render(
        request,
        'admin/dashboard/dashboard.html',
        context
    )


# ============================================================
# ADMIN STUDENTS
# ============================================================

def admin_students(request):

    if (
        not request.user.is_authenticated
        or not request.user.is_staff
    ):
        return redirect('admin_login')

    students = (
        UserProfile.objects
        .select_related(
            'user',
            'user__academic'
        )
        .order_by('-created_at')
    )

    search = request.GET.get(
        'search',
        ''
    ).strip()

    if search:

        students = students.filter(

            Q(
                full_name__icontains=search
            )
            |
            Q(
                user__academic__application_id__icontains=search
            )
            |
            Q(
                mobile__icontains=search
            )
            |
            Q(
                user__email__icontains=search
            )
            |
            Q(
                user__username__icontains=search
            )

        )

    course = request.GET.get(
        'course',
        ''
    ).strip()

    if course:

        students = students.filter(
            user__academic__course__icontains=course
        )

    status = request.GET.get(
        'status',
        ''
    ).strip()

    if status == 'Active':

        students = students.filter(
            user__is_active=True
        )

    elif status == 'Inactive':

        students = students.filter(
            user__is_active=False
        )

    elif status == 'New':

        today = timezone.localdate()

        students = students.filter(
            created_at__date=today
        )

    total_students = (
        UserProfile.objects.count()
    )

    active_students = (
        UserProfile.objects.filter(
            user__is_active=True
        ).count()
    )

    today = timezone.localdate()

    new_registrations = (
        UserProfile.objects.filter(
            created_at__date=today
        ).count()
    )

    final_year_students = (
        StudentAcademic.objects.filter(
            current_year__icontains='final'
        ).count()
    )

    courses = (
        StudentAcademic.objects
        .values_list(
            'course',
            flat=True
        )
        .distinct()
        .order_by('course')
    )

    context = {

        'students':
            students,

        'search':
            search,

        'course':
            course,

        'status':
            status,

        'total_students':
            total_students,

        'active_students':
            active_students,

        'new_registrations':
            new_registrations,

        'final_year_students':
            final_year_students,

        'courses':
            courses,
    }

    return render(
        request,
        'admin/students/list.html',
        context
    )


# ============================================================
# ADMIN STUDENT DETAIL
# ============================================================

def admin_student_detail(
    request,
    student_id
):

    if (
        not request.user.is_authenticated
        or not request.user.is_staff
    ):
        return redirect('admin_login')

    student = get_object_or_404(

        UserProfile.objects.select_related(
            'user',
            'user__academic'
        ),

        id=student_id
    )

    academic = None

    try:

        academic = student.user.academic

    except StudentAcademic.DoesNotExist:

        academic = None

    projects = (
        StudentProject.objects
        .filter(
            student=student.user
        )
        .order_by('-created_at')
    )

    quotations = (
        Quotation.objects
        .filter(
            student=student.user
        )
        .order_by('-created_at')
    )

    payments = (
        Payment.objects
        .filter(
            student=student.user
        )
        .order_by('-created_at')
    )

    context = {

        'student':
            student,

        'academic':
            academic,

        'projects':
            projects,

        'quotations':
            quotations,

        'payments':
            payments,
    }

    return render(
        request,
        'admin/students/detail.html',
        context
    )


# ============================================================
# ADMIN APPLICATIONS
# ============================================================

def admin_applications(request):

    if (
        not request.user.is_authenticated
        or not request.user.is_staff
    ):
        return redirect('admin_login')

    academic_qs = (
        StudentAcademic.objects
        .select_related(
            'student',
            'student__profile'
        )
        .order_by('-created_at')
    )

    search = request.GET.get(
        'search',
        ''
    ).strip()

    college = request.GET.get(
        'college',
        ''
    ).strip()

    university = request.GET.get(
        'university',
        ''
    ).strip()

    course = request.GET.get(
        'course',
        ''
    ).strip()

    branch = request.GET.get(
        'branch',
        ''
    ).strip()

    domain = request.GET.get(
        'domain',
        ''
    ).strip()

    payment_status = request.GET.get(
        'payment_status',
        ''
    ).strip()

    project_status = request.GET.get(
        'project_status',
        ''
    ).strip()

    if search:

        academic_qs = academic_qs.filter(

            Q(
                application_id__icontains=search
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
                student__profile__full_name__icontains=search
            )

        )

    if college:

        academic_qs = academic_qs.filter(
            college__icontains=college
        )

    if university:

        academic_qs = academic_qs.filter(
            university__icontains=university
        )

    if course:

        academic_qs = academic_qs.filter(
            course__icontains=course
        )

    if branch:

        academic_qs = academic_qs.filter(
            branch__icontains=branch
        )

    applications = []

    for academic in academic_qs:

        student = academic.student

        try:

            profile = student.profile

        except UserProfile.DoesNotExist:

            profile = None

        project = (
            StudentProject.objects
            .filter(
                student=student
            )
            .order_by('-created_at')
            .first()
        )

        payment = (
            Payment.objects
            .filter(
                student=student
            )
            .order_by('-created_at')
            .first()
        )

        if academic.application_id:

            application_id = (
                academic.application_id
            )

        else:

            application_id = "-"

        if student.username:

            student_id = student.username

        else:

            student_id = str(
                student.id
            )

        if (
            profile
            and profile.full_name
        ):

            student_name = (
                profile.full_name
            )

        elif student.get_full_name():

            student_name = (
                student.get_full_name()
            )

        else:

            student_name = (
                student.username
            )

        email = (
            student.email
            or "-"
        )

        if (
            project
            and project.domain
        ):

            project_domain = (
                project.domain
            )

        else:

            project_domain = "-"

        if payment:

            current_payment_status = (
                payment.payment_status
            )

        else:

            current_payment_status = "Unpaid"

        if project:

            current_project_status = (
                project.status
            )

        else:

            current_project_status = "Pending"

        current_application_status = (
            academic.application_status
            or "Pending"
        )

        current_admin_remark = (
            academic.admin_remark
            or ""
        )

        if domain:

            if (
                project_domain.lower()
                != domain.lower()
            ):
                continue

        if payment_status:

            if payment_status == "Unpaid":

                if (
                    current_payment_status
                    != "Unpaid"
                ):
                    continue

            elif (
                current_payment_status
                != payment_status
            ):

                continue

        if project_status:

            if (
                current_project_status
                != project_status
            ):
                continue

        applications.append({

            "application_id":
                application_id,

            "student_id":
                student_id,

            "student_name":
                student_name,

            "email":
                email,

            "college":
                academic.college or "-",

            "university":
                academic.university or "-",

            "course":
                academic.course or "-",

            "branch":
                academic.branch or "-",

            "domain":
                project_domain,

            "payment_status":
                current_payment_status,

            "project_status":
                current_project_status,

            "application_status":
                current_application_status,

            "admin_remark":
                current_admin_remark,
        })

    total_applications = (
        StudentAcademic.objects.count()
    )

    pending_applications = (
        StudentAcademic.objects.filter(
            application_status="Pending"
        ).count()
    )

    approved_applications = (
        StudentAcademic.objects.filter(
            application_status="Approved"
        ).count()
    )

    changes_requested_applications = (
        StudentAcademic.objects.filter(
            application_status="Changes Requested"
        ).count()
    )

    rejected_applications = (
        StudentAcademic.objects.filter(
            application_status="Rejected"
        ).count()
    )

    colleges = (
        StudentAcademic.objects
        .values_list(
            "college",
            flat=True
        )
        .distinct()
        .order_by("college")
    )

    universities = (
        StudentAcademic.objects
        .values_list(
            "university",
            flat=True
        )
        .distinct()
        .order_by("university")
    )

    courses = (
        StudentAcademic.objects
        .values_list(
            "course",
            flat=True
        )
        .distinct()
        .order_by("course")
    )

    branches = (
        StudentAcademic.objects
        .values_list(
            "branch",
            flat=True
        )
        .distinct()
        .order_by("branch")
    )

    domains = (
        StudentProject.objects
        .values_list(
            "domain",
            flat=True
        )
        .exclude(
            domain__isnull=True
        )
        .exclude(
            domain=""
        )
        .distinct()
        .order_by("domain")
    )

    context = {

        "applications":
            applications,

        "total_applications":
            total_applications,

        "pending_applications":
            pending_applications,

        "approved_applications":
            approved_applications,

        "changes_requested_applications":
            changes_requested_applications,

        "rejected_applications":
            rejected_applications,

        "search":
            search,

        "college":
            college,

        "university":
            university,

        "course":
            course,

        "branch":
            branch,

        "domain":
            domain,

        "payment_status":
            payment_status,

        "project_status":
            project_status,

        "colleges":
            colleges,

        "universities":
            universities,

        "courses":
            courses,

        "branches":
            branches,

        "domains":
            domains,
    }

    return render(
        request,
        "admin/applications/list.html",
        context
    )


# ============================================================
# ADMIN APPLICATION ACTION
# ============================================================

def admin_application_action(
    request,
    application_id
):

    if (
        not request.user.is_authenticated
        or not request.user.is_staff
    ):
        return redirect('admin_login')

    if request.method != 'POST':

        return redirect(
            'admin_applications'
        )

    try:

        academic = (
            StudentAcademic.objects
            .select_related(
                'student',
                'student__profile'
            )
            .get(
                application_id=application_id
            )
        )

    except StudentAcademic.DoesNotExist:

        messages.error(
            request,
            'Application not found.'
        )

        return redirect(
            'admin_applications'
        )

    action = request.POST.get(
        'admin_action',
        ''
    ).strip()

    remark = request.POST.get(
        'admin_remark',
        ''
    ).strip()

    allowed_actions = [
        'Approved',
        'Changes Requested',
        'Rejected',
    ]

    if action not in allowed_actions:

        messages.error(
            request,
            'Invalid application action.'
        )

        return redirect(
            'admin_applications'
        )

    if (
        action in [
            'Changes Requested',
            'Rejected'
        ]
        and not remark
    ):

        messages.error(
            request,
            'Admin remark is required.'
        )

        return redirect(
            'admin_applications'
        )

    academic.application_status = action

    academic.admin_remark = remark

    academic.save(
        update_fields=[
            'application_status',
            'admin_remark',
            'updated_at'
        ]
    )

    ApplicationActionHistory.objects.create(

        application=academic,

        action=action,

        remark=remark,

        action_by=request.user
    )

    messages.success(
        request,
        f'Application {application_id} updated successfully.'
    )

    return redirect(
        'admin_applications'
    )


# ============================================================
# ADMIN APPLICATION HISTORY
# ============================================================

def admin_application_history(
    request,
    application_id
):

    if (
        not request.user.is_authenticated
        or not request.user.is_staff
    ):

        return JsonResponse(
            {
                "error":
                    "Unauthorized"
            },
            status=403
        )

    try:

        academic = (
            StudentAcademic.objects
            .get(
                application_id=application_id
            )
        )

    except StudentAcademic.DoesNotExist:

        return JsonResponse(
            {
                "error":
                    "Application not found"
            },
            status=404
        )

    history = (
        ApplicationActionHistory.objects
        .filter(
            application=academic
        )
        .select_related(
            'action_by'
        )
        .order_by(
            '-created_at'
        )
    )

    history_data = []

    for item in history:

        if item.action_by:

            action_by = (
                item.action_by.get_full_name()
                or item.action_by.email
                or item.action_by.username
            )

        else:

            action_by = "Admin"

        history_data.append({

            "action":
                item.action,

            "remark":
                item.remark or "",

            "action_by":
                action_by,

            "created_at":
                item.created_at.strftime(
                    "%d %b %Y, %I:%M %p"
                )

        })

    return JsonResponse(
        {
            "history":
                history_data
        }
    )


# ============================================================
# ADMIN QUOTATIONS
# ============================================================

# ============================================================
# ADMIN QUOTATIONS
# FIXED ₹2,500 + PAYMENT STATUS
# ============================================================

def admin_quotations(request):

    if (
        not request.user.is_authenticated
        or not request.user.is_staff
    ):
        return redirect('admin_login')

    # ========================================================
    # ALL QUOTATIONS
    # ========================================================

    quotation_qs = (
        Quotation.objects
        .select_related(
            'student',
            'student__profile'
        )
        .prefetch_related(
            'payments'
        )
        .order_by('-created_at')
    )

    # ========================================================
    # SEARCH
    # ========================================================

    search = request.GET.get(
        'search',
        ''
    ).strip()

    if search:

        quotation_qs = quotation_qs.filter(

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

    # ========================================================
    # BUILD QUOTATION LIST
    # ========================================================

    quotations = []

    for quotation in quotation_qs:

        # ----------------------------------------------------
        # STUDENT NAME
        # ----------------------------------------------------

        profile = getattr(
            quotation.student,
            'profile',
            None
        )

        if (
            profile
            and profile.full_name
        ):

            student_name = (
                profile.full_name
            )

        elif quotation.student.get_full_name():

            student_name = (
                quotation.student.get_full_name()
            )

        else:

            student_name = (
                quotation.student.username
            )

        # ----------------------------------------------------
        # PAYMENT STATUS
        # ----------------------------------------------------

        paid_payment = (
            quotation.payments
            .filter(
                payment_status='Paid'
            )
            .order_by('-created_at')
            .first()
        )

        latest_payment = (
            quotation.payments
            .order_by('-created_at')
            .first()
        )

        if paid_payment:

            payment_status = 'Paid'

        else:

            payment_status = 'Unpaid'

        # ----------------------------------------------------
        # FIXED AMOUNT
        # ----------------------------------------------------

        quotation.amount = Decimal(
            '2500.00'
        )

        # ----------------------------------------------------
        # ATTACH EXTRA DATA TO OBJECT
        # ----------------------------------------------------

        quotation.admin_student_name = (
            student_name
        )

        quotation.admin_payment_status = (
            payment_status
        )

        quotation.admin_latest_payment = (
            latest_payment
        )

        quotation.admin_display_status = (
            'Paid'
            if payment_status == 'Paid'
            else 'Ready for Payment'
        )

        quotations.append(
            quotation
        )

    # ========================================================
    # PAYMENT STATUS FILTER
    # ========================================================

    selected_status = request.GET.get(
        'status',
        ''
    ).strip()

    if selected_status:

        filtered_quotations = []

        for quotation in quotations:

            payment_status = (
                quotation.admin_payment_status
            )

            if selected_status == 'Paid':

                if payment_status == 'Paid':

                    filtered_quotations.append(
                        quotation
                    )

            elif selected_status in [
                'Pending',
                'Unpaid',
                'Ready for Payment'
            ]:

                if payment_status == 'Unpaid':

                    filtered_quotations.append(
                        quotation
                    )

            elif selected_status == 'Rejected':

                if quotation.status == 'Rejected':

                    filtered_quotations.append(
                        quotation
                    )

        quotations = filtered_quotations

    # ========================================================
    # STATISTICS
    # ========================================================

    total = (
        Quotation.objects.count()
    )

    paid = 0

    for quotation in (
        Quotation.objects
        .prefetch_related('payments')
    ):

        if quotation.payments.filter(
            payment_status='Paid'
        ).exists():

            paid += 1

    # --------------------------------------------------------
    # READY FOR PAYMENT
    # --------------------------------------------------------

    ready_for_payment = (
        total - paid
    )

    # --------------------------------------------------------
    # UNPAID
    # --------------------------------------------------------

    unpaid = (
        ready_for_payment
    )

    # ========================================================
    # APPLICATION OPTIONS
    # ========================================================

    application_options = []

    academics = (
        StudentAcademic.objects
        .select_related(
            'student',
            'student__profile'
        )
        .exclude(
            application_id__isnull=True
        )
        .exclude(
            application_id=''
        )
        .order_by(
            '-created_at'
        )
    )

    for academic in academics:

        student = academic.student

        profile = getattr(
            student,
            'profile',
            None
        )

        # ----------------------------------------------------
        # STUDENT NAME
        # ----------------------------------------------------

        if profile and profile.full_name:

            student_name = (
                profile.full_name
            )

        elif student.get_full_name():

            student_name = (
                student.get_full_name()
            )

        else:

            student_name = (
                student.username
            )

        # ----------------------------------------------------
        # PROJECT
        # ----------------------------------------------------

        project = (
            StudentProject.objects
            .filter(
                student=student
            )
            .order_by(
                '-created_at'
            )
            .first()
        )

        if project:

            project_title = (
                project.project_title
                or ''
            )

            project_domain = (
                project.domain
                or ''
            )

            project_description = (
                project.description
                or ''
            )

        else:

            project_title = ''
            project_domain = ''
            project_description = ''

        # ----------------------------------------------------
        # EXISTING QUOTATION
        # ----------------------------------------------------

        existing_quotation = (
            Quotation.objects
            .filter(
                application_id=
                    academic.application_id
            )
            .order_by(
                '-created_at'
            )
            .first()
        )

        application_options.append({

            'application_id':
                academic.application_id,

            'student_name':
                student_name,

            'project_title':
                project_title,

            'project_domain':
                project_domain,

            'project_description':
                project_description,

            'student_id':
                student.id,

            'username':
                student.username,

            'has_quotation':
                bool(
                    existing_quotation
                ),

            'quotation_id':
                (
                    existing_quotation.quotation_id
                    if existing_quotation
                    else ''
                ),
        })

    # ========================================================
    # CONTEXT
    # ========================================================

    context = {

        'quotations':
            quotations,

        # Main quotation statistics
        'total':
            total,

        'ready_for_payment':
            ready_for_payment,

        'paid':
            paid,

        'unpaid':
            unpaid,

        # Compatibility with old template
        'pending':
            ready_for_payment,

        'accepted':
            paid,

        'rejected':
            (
                Quotation.objects
                .filter(
                    status='Rejected'
                )
                .count()
            ),

        'search':
            search,

        'selected_status':
            selected_status,

        'application_options':
            application_options,
    }

    return render(
        request,
        'admin/quotations/list.html',
        context
    )

# ============================================================
# ADMIN QUOTATION CREATE
# SEPARATE CREATE PAGE
# ============================================================

def admin_quotation_create(request):

    # ========================================================
    # ADMIN ACCESS
    # ========================================================

    if (
        not request.user.is_authenticated
        or not request.user.is_staff
    ):
        return redirect('admin_login')

    # ========================================================
    # GET
    # SHOW CREATE QUOTATION PAGE
    # ========================================================

    if request.method == 'GET':

        application_options = []

        academics = (
            StudentAcademic.objects
            .select_related(
                'student',
                'student__profile'
            )
            .exclude(
                application_id__isnull=True
            )
            .exclude(
                application_id=''
            )
            .order_by(
                '-created_at'
            )
        )

        for academic in academics:

            student = academic.student

            profile = getattr(
                student,
                'profile',
                None
            )

            if profile and profile.full_name:

                student_name = (
                    profile.full_name
                )

            elif student.get_full_name():

                student_name = (
                    student.get_full_name()
                )

            else:

                student_name = (
                    student.username
                )

            project = (
                StudentProject.objects
                .filter(
                    student=student
                )
                .order_by(
                    '-created_at'
                )
                .first()
            )

            if project:

                project_title = (
                    project.project_title
                    or ''
                )

                project_domain = (
                    project.domain
                    or ''
                )

                project_description = (
                    project.description
                    or ''
                )

            else:

                project_title = ''
                project_domain = ''
                project_description = ''

            existing_quotation = (
                Quotation.objects
                .filter(
                    application_id=academic.application_id
                )
                .order_by(
                    '-created_at'
                )
                .first()
            )

            application_options.append({

                'application_id':
                    academic.application_id,

                'student_name':
                    student_name,

                'project_title':
                    project_title,

                'project_domain':
                    project_domain,

                'project_description':
                    project_description,

                'has_quotation':
                    bool(existing_quotation),

                'quotation_id':
                    (
                        existing_quotation.quotation_id
                        if existing_quotation
                        else ''
                    ),
            })

        context = {

            'application_options':
                application_options,
        }

        return render(
            request,
            'admin/quotations/create.html',
            context
        )

    # ========================================================
    # POST
    # CREATE QUOTATION
    # ========================================================

    application_id = request.POST.get(
        'application_id',
        ''
    ).strip()

    project_title = request.POST.get(
        'project_title',
        ''
    ).strip()

    project_domain = request.POST.get(
        'project_domain',
        ''
    ).strip()

    description = request.POST.get(
        'description',
        ''
    ).strip()

    amount_raw = request.POST.get(
        'amount',
        ''
    ).strip()

    admin_remark = request.POST.get(
        'admin_remark',
        ''
    ).strip()

    if not application_id:

        messages.error(
            request,
            'Please select Application ID.'
        )

        return redirect(
            'admin_quotation_create'
        )

    try:

        academic = (
            StudentAcademic.objects
            .select_related(
                'student',
                'student__profile'
            )
            .get(
                application_id=application_id
            )
        )

    except StudentAcademic.DoesNotExist:

        messages.error(
            request,
            'Selected Application ID was not found.'
        )

        return redirect(
            'admin_quotation_create'
        )

    student = academic.student

    existing_quotation = (
        Quotation.objects
        .filter(
            application_id=application_id
        )
        .order_by(
            '-created_at'
        )
        .first()
    )

    if existing_quotation:

        messages.warning(
            request,
            f'Quotation already exists for '
            f'{application_id} '
            f'({existing_quotation.quotation_id}).'
        )

        return redirect(
            'admin_quotations'
        )

    project = (
        StudentProject.objects
        .filter(
            student=student
        )
        .order_by(
            '-created_at'
        )
        .first()
    )

    if project:

        if not project_title:

            project_title = (
                project.project_title
                or ''
            )

        if not project_domain:

            project_domain = (
                project.domain
                or ''
            )

        if not description:

            description = (
                project.description
                or ''
            )

    if not project_title:

        messages.error(
            request,
            'Project Title is required.'
        )

        return redirect(
            'admin_quotation_create'
        )

    if not amount_raw:

        messages.error(
            request,
            'Total Amount is required.'
        )

        return redirect(
            'admin_quotation_create'
        )

    try:

        amount = Decimal(
            amount_raw
        )

        if amount < 0:

            messages.error(
                request,
                'Amount cannot be negative.'
            )

            return redirect(
                'admin_quotation_create'
            )

    except (
        InvalidOperation,
        ValueError
    ):

        messages.error(
            request,
            'Please enter a valid amount.'
        )

        return redirect(
            'admin_quotation_create'
        )

    quotation = Quotation.objects.create(

        application_id=
            application_id,

        student=
            student,

        project_title=
            project_title,

        project_domain=
            project_domain,

        description=
            description,

        amount=
            amount,

        status=
            'Pending',

        admin_remark=
            admin_remark,

        student_remark=
            ''
    )

    if not quotation.quotation_id:

        quotation.quotation_id = (
            f"QT-2026-{quotation.id:04d}"
        )

        quotation.save(
            update_fields=[
                'quotation_id'
            ]
        )

    # ========================================================
    # QUOTATION NOTIFICATION
    # SEND TO SAME STUDENT
    # ========================================================

    student_name = (
        student.get_full_name()
        or student.username
    )

    notification_message = (
        f'Hello {student_name},\n\n'
        'A quotation has been generated for your project '
        'by Code Axis TechSolutions LLP.\n\n'
        f'Application ID: {quotation.application_id}\n'
        f'Quotation ID: {quotation.quotation_id}\n'
        f'Project Title: {quotation.project_title}\n'
        f'Project Domain: {quotation.project_domain}\n'
        f'Quotation Amount: ₹{quotation.amount}\n\n'
        f'Admin Remark: '
        f'{quotation.admin_remark or "No additional remark"}\n\n'
        'Please login to the Student Project Portal '
        'to view the complete quotation and take the '
        'required action.\n\n'
        'Regards,\n'
        'Code Axis TechSolutions LLP'
    )

    notification_result = send_student_notification(
        student=student,
        subject=(
            'Quotation Generated | '
            'Code Axis TechSolutions LLP'
        ),
        message=notification_message
    )

    print(
        'Quotation notification result:',
        notification_result
    )

    messages.success(
        request,
        f'Quotation {quotation.quotation_id} '
        f'created successfully.'
    )

    return redirect(
        'admin_quotations'
    )


# ============================================================
# ADMIN QUOTATION UPDATE
# ============================================================

def admin_quotation_update(
    request,
    quotation_id
):

    if (
        not request.user.is_authenticated
        or not request.user.is_staff
    ):
        return redirect('admin_login')

    if request.method != 'POST':

        return redirect(
            'admin_quotations'
        )

    quotation = get_object_or_404(
        Quotation,
        quotation_id=quotation_id
    )

    old_status = quotation.status

    project_title = request.POST.get(
        'project_title',
        ''
    ).strip()

    project_domain = request.POST.get(
        'project_domain',
        ''
    ).strip()

    amount_raw = request.POST.get(
        'amount',
        ''
    ).strip()

    status = request.POST.get(
        'status',
        'Pending'
    ).strip()

    description = request.POST.get(
        'description',
        ''
    ).strip()

    admin_remark = request.POST.get(
        'admin_remark',
        ''
    ).strip()

    allowed_statuses = [
        'Pending',
        'Accepted',
        'Rejected'
    ]

    if status not in allowed_statuses:

        status = 'Pending'

    if not project_title:

        messages.error(
            request,
            'Project Title is required.'
        )

        return redirect(
            'admin_quotations'
        )

    if not amount_raw:

        messages.error(
            request,
            'Amount is required.'
        )

        return redirect(
            'admin_quotations'
        )

    try:

        amount = Decimal(
            amount_raw
        )

        if amount < 0:

            messages.error(
                request,
                'Amount cannot be negative.'
            )

            return redirect(
                'admin_quotations'
            )

    except (
        InvalidOperation,
        ValueError
    ):

        messages.error(
            request,
            'Please enter a valid amount.'
        )

        return redirect(
            'admin_quotations'
        )

    quotation.project_title = (
        project_title
    )

    quotation.project_domain = (
        project_domain
    )

    quotation.amount = (
        amount
    )

    quotation.status = (
        status
    )

    quotation.description = (
        description
    )

    quotation.admin_remark = (
        admin_remark
    )

    quotation.save()

    # ========================================================
    # QUOTATION STATUS NOTIFICATION
    # ========================================================

    if old_status != status:

        student = quotation.student

        student_name = (
            student.get_full_name()
            or student.username
        )

        if status == 'Accepted':

            notification_subject = (
                'Quotation Accepted | '
                'Code Axis TechSolutions LLP'
            )

            notification_message = (
                f'Hello {student_name},\n\n'
                'Your quotation has been accepted successfully.\n\n'
                f'Application ID: {quotation.application_id}\n'
                f'Quotation ID: {quotation.quotation_id}\n'
                f'Project Title: {quotation.project_title}\n'
                f'Quotation Amount: ₹{quotation.amount}\n\n'
                'You can now proceed to the payment stage.\n\n'
                'Please login to the Student Project Portal '
                'for further details.\n\n'
                'Regards,\n'
                'Code Axis TechSolutions LLP'
            )

        elif status == 'Rejected':

            notification_subject = (
                'Quotation Rejected | '
                'Code Axis TechSolutions LLP'
            )

            notification_message = (
                f'Hello {student_name},\n\n'
                'Your quotation has been rejected.\n\n'
                f'Application ID: {quotation.application_id}\n'
                f'Quotation ID: {quotation.quotation_id}\n'
                f'Project Title: {quotation.project_title}\n\n'
                f'Admin Remark: '
                f'{quotation.admin_remark or "No additional remark"}\n\n'
                'Please login to the Student Project Portal '
                'to view the quotation details.\n\n'
                'Regards,\n'
                'Code Axis TechSolutions LLP'
            )

        else:

            notification_subject = (
                'Quotation Updated | '
                'Code Axis TechSolutions LLP'
            )

            notification_message = (
                f'Hello {student_name},\n\n'
                'Your quotation has been updated.\n\n'
                f'Application ID: {quotation.application_id}\n'
                f'Quotation ID: {quotation.quotation_id}\n'
                f'Project Title: {quotation.project_title}\n'
                f'Quotation Amount: ₹{quotation.amount}\n\n'
                'Please login to the Student Project Portal '
                'to view the latest quotation details.\n\n'
                'Regards,\n'
                'Code Axis TechSolutions LLP'
            )

        notification_result = send_student_notification(
            student=student,
            subject=notification_subject,
            message=notification_message
        )

        print(
            'Quotation status notification result:',
            notification_result
        )

    messages.success(
        request,
        f'Quotation {quotation.quotation_id} updated successfully.'
    )

    return redirect(
        'admin_quotations'
    )


# ============================================================
# ADMIN QUOTATION DELETE
# ============================================================

def admin_quotation_delete(
    request,
    quotation_id
):

    if (
        not request.user.is_authenticated
        or not request.user.is_staff
    ):
        return redirect('admin_login')

    quotation = get_object_or_404(
        Quotation,
        quotation_id=quotation_id
    )

    if request.method == 'POST':

        quotation.delete()

        messages.success(
            request,
            'Quotation deleted successfully.'
        )

    return redirect(
        'admin_quotations'
    )


# ============================================================
# ADMIN PAYMENTS
# ============================================================

def admin_payments(request):

    if (
        not request.user.is_authenticated
        or not request.user.is_staff
    ):
        return redirect('admin_login')

    payments = (
        Payment.objects
        .select_related(
            'student',
            'student__profile',
            'quotation'
        )
        .order_by('-id')
    )

    search = request.GET.get(
        'search',
        ''
    ).strip()

    selected_status = request.GET.get(
        'status',
        ''
    ).strip()

    selected_method = request.GET.get(
        'method',
        ''
    ).strip()

    if search:

        payments = payments.filter(

            Q(
                transaction_reference__icontains=search
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
            |
            Q(
                quotation__quotation_id__icontains=search
            )
            |
            Q(
                quotation__application_id__icontains=search
            )

        )

    if selected_status:

        payments = payments.filter(
            payment_status=selected_status
        )

    if selected_method:

        payments = payments.filter(
            payment_method=selected_method
        )

    total_payments = (
        Payment.objects.count()
    )

    paid_payments = (
        Payment.objects
        .filter(
            payment_status='Paid'
        )
        .count()
    )

    pending_payments = (
        Payment.objects
        .filter(
            payment_status='Pending'
        )
        .count()
    )

    failed_payments = (
        Payment.objects
        .filter(
            payment_status='Failed'
        )
        .count()
    )

    context = {

        'payments':
            payments,

        'total_payments':
            total_payments,

        'paid_payments':
            paid_payments,

        'pending_payments':
            pending_payments,

        'failed_payments':
            failed_payments,

        'search':
            search,

        'selected_status':
            selected_status,

        'selected_method':
            selected_method,
    }

    return render(
        request,
        'admin/payments/list.html',
        context
    )


# ============================================================
# ADMIN PROJECTS
# ============================================================

def admin_projects(request):

    projects = StudentProject.objects.all().order_by('-pk')

    return render(
    request,
    'admin/projects/list.html',
    {
        'projects': projects,
    }
)
# ============================================================
# ADMIN PROJECT UPDATE
# ============================================================



# ============================================================
# ADMIN PROJECT UPDATE
# ============================================================

@login_required
def admin_project_update(request, project_id):

    # --------------------------------------------------------
    # ADMIN ACCESS CHECK
    # --------------------------------------------------------

    if not request.user.is_staff:

        messages.error(
            request,
            "You are not authorized to access admin."
        )

        return redirect(
            'admin_login'
        )

    # --------------------------------------------------------
    # GET PROJECT
    # --------------------------------------------------------

    project = get_object_or_404(
        StudentProject,
        id=project_id
    )

    # --------------------------------------------------------
    # POST ONLY
    # --------------------------------------------------------

    if request.method != 'POST':

        return redirect(
            'admin_projects'
        )

    # --------------------------------------------------------
    # OLD STATUS
    # Used to detect first-time completion
    # --------------------------------------------------------

    old_project_status = project.project_status
    old_status = project.status

    # --------------------------------------------------------
    # FORM DATA
    # --------------------------------------------------------

    manager = request.POST.get(
        'project_manager',
        ''
    ).strip()

    developer = request.POST.get(
        'developer',
        ''
    ).strip()

    current_stage = request.POST.get(
        'current_stage',
        'Project Assigned'
    ).strip()

    project_status = request.POST.get(
        'project_status',
        'Pending'
    ).strip()

    deadline = request.POST.get(
        'deadline',
        ''
    ).strip()

    admin_remark = request.POST.get(
        'admin_remark',
        ''
    ).strip()

    # --------------------------------------------------------
    # VALID PROJECT STAGES
    # --------------------------------------------------------

    valid_stages = [
        'Project Assigned',
        'Requirement Analysis',
        'UI Development',
        'Backend Development',
        'Database Integration',
        'Testing',
        'Documentation',
        'Final Delivery',
    ]

    # --------------------------------------------------------
    # VALID PROJECT STATUS
    # --------------------------------------------------------

    valid_statuses = [
        'Pending',
        'Active',
        'Testing',
        'Completed',
        'Delayed',
    ]

    # --------------------------------------------------------
    # STATUS VALIDATION
    # --------------------------------------------------------

    if project_status not in valid_statuses:

        messages.error(
            request,
            'Invalid project status.'
        )

        return redirect(
            'admin_projects'
        )

    # --------------------------------------------------------
    # COMPLETED = FINAL DELIVERY + 100%
    # --------------------------------------------------------

    if project_status == 'Completed':

        current_stage = 'Final Delivery'

    # --------------------------------------------------------
    # STAGE VALIDATION
    # --------------------------------------------------------

    if current_stage not in valid_stages:

        messages.error(
            request,
            'Invalid project stage.'
        )

        return redirect(
            'admin_projects'
        )

    # --------------------------------------------------------
    # MANAGER VALIDATION
    # --------------------------------------------------------

    if not manager:

        messages.error(
            request,
            'Please enter Project Manager.'
        )

        return redirect(
            'admin_projects'
        )

    # --------------------------------------------------------
    # DEVELOPER VALIDATION
    # --------------------------------------------------------

    if not developer:

        messages.error(
            request,
            'Please enter Developer.'
        )

        return redirect(
            'admin_projects'
        )

    # --------------------------------------------------------
    # DEADLINE
    # --------------------------------------------------------

    if deadline:

        try:

            parsed_deadline = datetime.strptime(
                deadline,
                '%Y-%m-%d'
            ).date()

        except ValueError:

            messages.error(
                request,
                'Invalid deadline date.'
            )

            return redirect(
                'admin_projects'
            )

    else:

        parsed_deadline = None

    # --------------------------------------------------------
    # PROGRESS MAP
    # --------------------------------------------------------

    progress_map = {

        'Project Assigned': 10,

        'Requirement Analysis': 20,

        'UI Development': 40,

        'Backend Development': 60,

        'Database Integration': 70,

        'Testing': 85,

        'Documentation': 95,

        'Final Delivery': 100,
    }

    # --------------------------------------------------------
    # PROJECT BASIC DETAILS
    # --------------------------------------------------------

    project.project_manager = manager

    project.developer = developer

    project.current_stage = current_stage

    project.project_status = project_status

    project.deadline = parsed_deadline

    project.admin_remark = admin_remark

    # --------------------------------------------------------
    # PROGRESS
    # --------------------------------------------------------

    if project_status == 'Completed':

        project.progress = 100

    else:

        project.progress = progress_map.get(
            current_stage,
            0
        )

    # --------------------------------------------------------
    # OLD STATUS FIELD
    # --------------------------------------------------------

    if project_status == 'Pending':

        project.status = 'Pending'

    elif project_status == 'Active':

        project.status = 'In Progress'

    elif project_status == 'Testing':

        project.status = 'In Progress'

    elif project_status == 'Completed':

        project.status = 'Completed'

    elif project_status == 'Delayed':

        project.status = 'On Hold'

    # --------------------------------------------------------
    # FINAL PROJECT FILES
    # IMPORTANT:
    # These names match the HTML and model
    # --------------------------------------------------------

    final_source_code = request.FILES.get(
        'final_source_code'
    )

    if final_source_code:

        project.final_source_code = (
            final_source_code
        )

    final_documentation = request.FILES.get(
        'final_documentation'
    )

    if final_documentation:

        project.final_documentation = (
            final_documentation
        )

    final_ppt = request.FILES.get(
        'final_ppt'
    )

    if final_ppt:

        project.final_ppt = (
            final_ppt
        )

    final_database_file = request.FILES.get(
        'final_database_file'
    )

    if final_database_file:

        project.final_database_file = (
            final_database_file
        )

    # --------------------------------------------------------
    # SEND FINAL PROJECT TO STUDENT
    # --------------------------------------------------------

    send_to_student = request.POST.get(
        'send_to_student',
        '0'
    )

    if send_to_student == '1':

        # Must be completed

        if project_status != 'Completed':

            messages.error(
                request,
                'Project must be Completed before sending to student.'
            )

            return redirect(
                'admin_projects'
            )

        # Must be Final Delivery

        if current_stage != 'Final Delivery':

            messages.error(
                request,
                'Project must be in Final Delivery stage.'
            )

            return redirect(
                'admin_projects'
            )

        # At least one final file

        has_final_file = any([

            bool(
                project.final_source_code
            ),

            bool(
                project.final_documentation
            ),

            bool(
                project.final_ppt
            ),

            bool(
                project.final_database_file
            ),

        ])

        if not has_final_file:

            messages.error(
                request,
                'Please upload at least one final project file before sending.'
            )

            return redirect(
                'admin_projects'
            )

        project.sent_to_student = True

        project.sent_at = timezone.now()

    # --------------------------------------------------------
    # SAVE PROJECT
    # --------------------------------------------------------

    project.save()

    # ========================================================
    # PROJECT COMPLETION DETECTION
    # ========================================================

    project_just_completed = (

        project_status == 'Completed'

        and (

            old_project_status != 'Completed'

            or old_status != 'Completed'

        )

    )

    # ========================================================
    # SEND COMPLETION NOTIFICATION
    # ========================================================

    if project_just_completed:

        student = project.student

        student_name = (
            student.get_full_name()
            or student.username
        )

        # ----------------------------------------------------
        # APPLICATION ID
        # ----------------------------------------------------

        application_id = 'N/A'

        try:

            academic = student.academic

            if academic.application_id:

                application_id = (
                    academic.application_id
                )

        except StudentAcademic.DoesNotExist:

            pass

        # ----------------------------------------------------
        # MOBILE
        # ----------------------------------------------------

        mobile = 'N/A'

        try:

            profile = student.profile

            if profile.mobile:

                mobile = profile.mobile

        except UserProfile.DoesNotExist:

            pass

        # ----------------------------------------------------
        # NOTIFICATION MESSAGE
        # ----------------------------------------------------

        notification_message = (

            f'Hello {student_name},\n\n'

            'Congratulations!\n\n'

            'Your project has been completed successfully '
            'by Code Axis TechSolutions LLP.\n\n'

            f'Application ID: {application_id}\n'

            f'Project Title: '
            f'{project.project_title}\n'

            f'Project Type: '
            f'{project.project_type}\n'

            f'Domain: '
            f'{project.domain}\n'

            f'Technology: '
            f'{project.technology}\n\n'

            'Project Status: Completed\n'

            'Project Progress: 100%\n'

            'Current Stage: Final Delivery\n\n'

            f'Project Manager: '
            f'{project.project_manager or "N/A"}\n'

            f'Developer: '
            f'{project.developer or "N/A"}\n\n'

            f'Deadline: '
            f'{project.deadline.strftime("%d-%m-%Y") if project.deadline else "N/A"}\n\n'

            f'Admin Remark: '
            f'{project.admin_remark or "No additional remark"}\n\n'

            f'Registered Mobile: '
            f'{mobile}\n\n'

            'Your project is now completed.\n'

            'Please login to the Student Project Portal '
            'for further details and final project delivery.\n\n'

            'Regards,\n'

            'Code Axis TechSolutions LLP'
        )

        # ----------------------------------------------------
        # SEND EMAIL + SMS
        # ----------------------------------------------------

        notification_result = (
            send_student_notification(

                student=student,

                subject=(
                    'Project Completed | '
                    'Code Axis TechSolutions LLP'
                ),

                message=notification_message
            )
        )

        print(
            'Project completion notification result:',
            notification_result
        )

    # ========================================================
    # SUCCESS MESSAGE
    # ========================================================

    if send_to_student == '1':

        messages.success(
            request,
            'Project updated and final project sent to student successfully.'
        )

    elif project_just_completed:

        messages.success(
            request,
            'Project marked as Completed and student notification sent successfully.'
        )

    else:

        messages.success(
            request,
            'Project details updated successfully.'
        )

    return redirect(
        'admin_projects'
    )

# ============================================================
# SEND FINAL PROJECT TO STUDENT
# ============================================================

@login_required
def admin_project_delivery(
    request,
    project_id
):

    if not request.user.is_staff:

        return redirect(
            'admin_login'
        )

    if request.method != 'POST':

        return redirect(
            'admin_projects'
        )

    project = get_object_or_404(
        StudentProject,
        id=project_id
    )

    if project.current_stage != 'Final Delivery':

        messages.error(
            request,
            'Project is not in Final Delivery stage.'
        )

        return redirect(
            'admin_projects'
        )

    if project.project_status != 'Completed':

        messages.error(
            request,
            'Project must be Completed before delivery.'
        )

        return redirect(
            'admin_projects'
        )

    has_final_file = any([

        bool(
            project.final_source_code
        ),

        bool(
            project.final_documentation
        ),

        bool(
            project.final_ppt
        ),

        bool(
            project.final_database_file
        ),

    ])

    if not has_final_file:

        messages.error(
            request,
            'Please upload at least one final project file before delivery.'
        )

        return redirect(
            'admin_projects'
        )

    project.sent_to_student = True

    project.sent_at = (
        timezone.now()
    )

    project.save(
        update_fields=[
            'sent_to_student',
            'sent_at',
            'updated_at'
        ]
    )

    # ========================================================
    # FINAL DELIVERY NOTIFICATION
    # ========================================================

    student = project.student

    student_name = (
        student.get_full_name()
        or student.username
    )

    application_id = 'N/A'

    try:

        academic = student.academic

        if academic.application_id:

            application_id = (
                academic.application_id
            )

    except StudentAcademic.DoesNotExist:

        pass

    notification_message = (
        f'Hello {student_name},\n\n'
        'Your completed project has been delivered '
        'successfully.\n\n'
        f'Application ID: {application_id}\n'
        f'Project Title: {project.project_title}\n'
        f'Project Status: {project.project_status}\n'
        f'Project Progress: {project.progress}%\n\n'
        'Your final project files are now available '
        'in the Student Project Portal.\n\n'
        'Please login to download your final project files.\n\n'
        'Thank you for choosing Code Axis TechSolutions LLP.\n\n'
        'Regards,\n'
        'Code Axis TechSolutions LLP'
    )

    notification_result = send_student_notification(
        student=student,
        subject=(
            'Final Project Delivered | '
            'Code Axis TechSolutions LLP'
        ),
        message=notification_message
    )

    print(
        'Final delivery notification result:',
        notification_result
    )

    messages.success(
        request,
        'Final project sent to student successfully.'
    )

    return redirect(
        'admin_projects'
    )

# ==========================================================
# ADMIN FORGOT PASSWORD
# ==========================================================

def admin_forgot_password(request):

    if request.method == "POST":

        email = request.POST.get("email", "").strip()

        # Always show generic message for security
        success_message = (
            "If an admin account exists with this email, "
            "a password reset link has been sent."
        )

        try:
            user = User.objects.get(
                email__iexact=email,
                is_staff=True
            )

            # Generate secure reset token
            uid = urlsafe_base64_encode(
                force_bytes(user.pk)
            )

            token = default_token_generator.make_token(user)

            reset_url = request.build_absolute_uri(
                reverse(
                    "admin_reset_password",
                    kwargs={
                        "uidb64": uid,
                        "token": token
                    }
                )
            )

            subject = "Admin Password Reset | Code Axis TechSolutions LLP"

            message = f"""
Hello,

We received a request to reset your Admin Portal password.

Click the link below to create a new password:

{reset_url}

This link is valid only for this password reset request.

If you did not request a password reset, please ignore this email.

Regards,
Code Axis TechSolutions LLP
"""

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

        except User.DoesNotExist:
            pass

        return render(
            request,
            "admin/forgot_password.html",
            {
                "success": success_message
            }
        )

    return render(
        request,
        "admin/forgot_password.html"
    )


# ==========================================================
# ADMIN RESET PASSWORD
# ==========================================================

def admin_reset_password(request, uidb64, token):

    try:
        uid = force_str(
            urlsafe_base64_decode(uidb64)
        )

        user = User.objects.get(
            pk=uid,
            is_staff=True
        )

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        return render(
            request,
            "admin/reset_password.html",
            {
                "error": "This password reset link is invalid or has expired."
            }
        )

    if request.method == "POST":

        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if not password or not confirm_password:
            return render(
                request,
                "admin/reset_password.html",
                {
                    "error": "Please enter both passwords."
                }
            )

        if password != confirm_password:
            return render(
                request,
                "admin/reset_password.html",
                {
                    "error": "Passwords do not match."
                }
            )

        if len(password) < 8:
            return render(
                request,
                "admin/reset_password.html",
                {
                    "error": "Password must contain at least 8 characters."
                }
            )

        # Update password
        user.set_password(password)
        user.save()

        return redirect("admin_login")

    return render(
        request,
        "admin/reset_password.html"
    )


# ============================================================
# ADMIN LOGOUT
# ============================================================

def admin_logout(request):

    logout(request)

    return redirect(
        'admin_login'
    )