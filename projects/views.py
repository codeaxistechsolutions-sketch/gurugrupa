from decimal import Decimal

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse

from notifications.services import send_student_notification

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

from .models import StudentProject
from quotations.models import Quotation
from students.models import StudentAcademic


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
    # DEBUG NORMALIZED VALUE
    # -----------------------------------------------------

    print("College checking:", repr(college))

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
    # PARIKRAMA + ALL OTHER COLLEGES → ₹2500
    # -----------------------------------------------------

    return DEFAULT_QUOTATION_AMOUNT


# =========================================================
# STUDENT PROJECT DETAILS
# =========================================================

@login_required
def project_details_view(request):

    # =====================================================
    # GET EXISTING PROJECT FOR LOGGED-IN STUDENT
    # =====================================================

    project = (
        StudentProject.objects
        .filter(
            student=request.user
        )
        .order_by('-id')
        .first()
    )

    # =====================================================
    # SAVE / UPDATE PROJECT
    # =====================================================

    if request.method == 'POST':

        # -------------------------------------------------
        # Check whether project already exists
        # -------------------------------------------------

        is_new_project = project is None

        # -------------------------------------------------
        # Existing project → UPDATE
        # New project → CREATE
        # -------------------------------------------------

        if is_new_project:

            project = StudentProject(
                student=request.user
            )

        # -------------------------------------------------
        # Always connect project with logged-in student
        # -------------------------------------------------

        project.student = request.user

        # =================================================
        # BASIC PROJECT DETAILS
        # =================================================

        project.project_title = request.POST.get(
            'project_title',
            ''
        ).strip()

        project.project_type = request.POST.get(
            'project_type',
            ''
        ).strip()

        project.domain = request.POST.get(
            'domain',
            ''
        ).strip()

        project.technology = request.POST.get(
            'technology',
            ''
        ).strip()

        project.guide = request.POST.get(
            'guide',
            ''
        ).strip()

        # =================================================
        # TEAM SIZE
        # =================================================

        team_size = request.POST.get(
            'team_size',
            '1'
        ).strip()

        try:

            team_size = int(team_size)

            if team_size < 1:
                team_size = 1

        except (ValueError, TypeError):

            team_size = 1

        project.team_size = team_size

        # =================================================
        # DURATION
        # =================================================

        project.duration = request.POST.get(
            'duration',
            ''
        ).strip()

        # =================================================
        # DESCRIPTION
        # =================================================

        project.description = request.POST.get(
            'description',
            ''
        ).strip()

        # =================================================
        # REQUIREMENTS
        # =================================================

        project.requirements = request.POST.get(
            'requirements',
            ''
        ).strip()

        # =================================================
        # ADDITIONAL INFORMATION
        # =================================================

        project.additional = request.POST.get(
            'additional',
            ''
        ).strip()

        # =================================================
        # DELIVERABLES
        # =================================================

        project.source_code = (
            'source_code' in request.POST
        )

        project.documentation = (
            'documentation' in request.POST
        )

        project.ppt = (
            'ppt' in request.POST
        )

        # =================================================
        # GUIDELINE FILE
        # =================================================

        guideline_file = request.FILES.get(
            'guideline_file'
        )

        if guideline_file:

            project.guideline_file = guideline_file

        project.file_description = request.POST.get(
            'file_description',
            ''
        ).strip()

        # =================================================
        # ADDITIONAL FILE
        # =================================================

        additional_file = request.FILES.get(
            'additional_file'
        )

        if additional_file:

            project.additional_file = additional_file

        project.additional_file_description = request.POST.get(
            'additional_file_description',
            ''
        ).strip()

        # =================================================
        # VALIDATION
        # =================================================

        if not project.project_title:

            messages.error(
                request,
                'Project Title is required.'
            )

            return redirect(
                'user_project_details'
            )

        if not project.project_type:

            messages.error(
                request,
                'Project Type is required.'
            )

            return redirect(
                'user_project_details'
            )

        if not project.domain:

            messages.error(
                request,
                'Project Domain is required.'
            )

            return redirect(
                'user_project_details'
            )

        if not project.technology:

            messages.error(
                request,
                'Technology / Tech Stack is required.'
            )

            return redirect(
                'user_project_details'
            )

        if not project.description:

            messages.error(
                request,
                'Project Description is required.'
            )

            return redirect(
                'user_project_details'
            )

        if not project.requirements:

            messages.error(
                request,
                'Project Requirements are required.'
            )

            return redirect(
                'user_project_details'
            )

        # =================================================
        # DEFAULT ADMIN PROJECT MANAGEMENT VALUES
        # =================================================

        if not project.status:

            project.status = 'Pending'

        if not project.project_status:

            project.project_status = 'Pending'

        if not project.current_stage:

            project.current_stage = 'Project Assigned'

        # =================================================
        # SAVE PROJECT
        # =================================================

        project.save()

        # =================================================
        # GET APPLICATION ID + COLLEGE
        # =================================================

        application_id = ''

        college_name = ''

        quotation_amount = DEFAULT_QUOTATION_AMOUNT

        try:

            academic = StudentAcademic.objects.get(
                student=request.user
            )

            # -------------------------------------------------
            # APPLICATION ID
            # -------------------------------------------------

            application_id = getattr(
                academic,
                'application_id',
                ''
            )

            # -------------------------------------------------
            # If application_id is stored in Profile
            # -------------------------------------------------

            if not application_id:

                profile = getattr(
                    request.user,
                    'profile',
                    None
                )

                if profile:

                    application_id = getattr(
                        profile,
                        'application_id',
                        ''
                    )

            # -------------------------------------------------
            # GET COLLEGE NAME
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
            # COLLEGE-WISE QUOTATION AMOUNT
            # -------------------------------------------------

            quotation_amount = (
                get_college_quotation_amount(
                    college_name
                )
            )

            # =================================================
            # DEBUG COLLEGE + QUOTATION
            # =================================================

            print("====================================")
            print(
                "COLLEGE FROM DATABASE:",
                repr(college_name)
            )
            print(
                "COLLEGE NORMALIZED:",
                " ".join(
                    str(college_name)
                    .strip()
                    .lower()
                    .split()
                )
            )
            print(
                "QUOTATION AMOUNT:",
                quotation_amount
            )
            print("====================================")

        except StudentAcademic.DoesNotExist:

            # -------------------------------------------------
            # Academic record नसल्यास profile मधून
            # application_id घेण्याचा प्रयत्न
            # -------------------------------------------------

            profile = getattr(
                request.user,
                'profile',
                None
            )

            if profile:

                application_id = getattr(
                    profile,
                    'application_id',
                    ''
                )

            # -------------------------------------------------
            # No academic record → ₹2500
            # -------------------------------------------------

            quotation_amount = (
                DEFAULT_QUOTATION_AMOUNT
            )

            # =================================================
            # DEBUG - ACADEMIC RECORD NOT FOUND
            # =================================================

            print("====================================")
            print(
                "STUDENT ACADEMIC RECORD NOT FOUND"
            )
            print(
                "COLLEGE FROM DATABASE:",
                repr(college_name)
            )
            print(
                "QUOTATION AMOUNT:",
                quotation_amount
            )
            print("====================================")

        # =====================================================
        # AUTOMATIC QUOTATION
        # =====================================================

        quotation = (
            Quotation.objects
            .filter(
                student=request.user,
                project_title=project.project_title
            )
            .order_by('-created_at')
            .first()
        )

        # =====================================================
        # CREATE QUOTATION IF NOT EXISTS
        # =====================================================

        if not quotation:

            quotation = Quotation.objects.create(

                application_id=application_id,

                student=request.user,

                project_title=project.project_title,

                project_domain=project.domain,

                description=project.description,

                amount=quotation_amount,

                status='Accepted',

                admin_remark=(
                    f'Project registration charge for '
                    f'{college_name or "selected college"}: '
                    f'₹{quotation_amount:.2f}.'
                ),

                student_remark=''
            )

            # =================================================
            # QUOTATION NOTIFICATION
            # =================================================

            student_name = (
                request.user.get_full_name()
                or request.user.username
            )

            notification_message = (

                f'Hello {student_name},\n\n'

                'Your project quotation has been generated '
                'successfully.\n\n'

                f'Application ID: '
                f'{application_id or "N/A"}\n'

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

                    student=request.user,

                    subject=(
                        'Quotation Generated | '
                        'Code Axis TechSolutions LLP'
                    ),

                    message=notification_message
                )
            )

            print(
                'Quotation notification result:',
                notification_result
            )

        else:

            # =================================================
            # EXISTING QUOTATION UPDATE
            # =================================================
            #
            # College बदलल्यास amount देखील update होईल.
            # =================================================

            quotation.amount = quotation_amount

            quotation.project_title = (
                project.project_title
            )

            quotation.project_domain = (
                project.domain
            )

            quotation.description = (
                project.description
            )

            if application_id:

                quotation.application_id = (
                    application_id
                )

            quotation.status = 'Accepted'

            quotation.admin_remark = (
                f'Project registration charge for '
                f'{college_name or "selected college"}: '
                f'₹{quotation_amount:.2f}.'
            )

            quotation.save()

        # =====================================================
        # SEND PROJECT NOTIFICATION ONLY FOR NEW PROJECT
        # =====================================================

        if is_new_project:

            student_name = (
                request.user.get_full_name()
                or request.user.username
            )

            notification_message = (

                f'Hello {student_name},\n\n'

                'Your project details have been submitted '
                'successfully.\n\n'

                f'Application ID: '
                f'{application_id or "N/A"}\n'

                f'Project Title: '
                f'{project.project_title}\n'

                f'Project Type: '
                f'{project.project_type}\n'

                f'Domain: '
                f'{project.domain}\n'

                f'Technology: '
                f'{project.technology}\n'

                f'College: '
                f'{college_name or "N/A"}\n\n'

                'Your application has now moved to the '
                'quotation stage.\n\n'

                f'A quotation of '
                f'₹{quotation_amount:.2f} has been '
                'generated for your project.\n\n'

                'Please login to the Student Project Portal '
                'to proceed with payment.\n\n'

                'Regards,\n'
                'Code Axis TechSolutions LLP'
            )

            notification_result = (
                send_student_notification(

                    student=request.user,

                    subject=(
                        'Project Details Submitted | '
                        'Code Axis TechSolutions LLP'
                    ),

                    message=notification_message
                )
            )

            print(
                'Project notification result:',
                notification_result
            )

        # =====================================================
        # SUCCESS MESSAGE
        # =====================================================

        messages.success(

            request,

            f'Project details saved successfully. '

            f'Quotation of ₹{quotation_amount:.2f} '

            f'is ready for payment.'
        )

        # =====================================================
        # SAVE & CONTINUE → QUOTATION
        # =====================================================

        return redirect(
            'user_quotation'
        )

    # =====================================================
    # GET REQUEST
    # =====================================================

    context = {

        'project': project,

        'profile': getattr(
            request.user,
            'profile',
            None
        ),

        'user': request.user,
    }

    return render(
        request,
        'user/project/project.html',
        context
    )


# =========================================================
# DOWNLOAD PROJECT LIST EXCEL
# =========================================================

@login_required
def download_project_excel(request):

    project_list = {

        "Major Project": [
            "Hospital Management System",
            "Student Management System",
            "College Management System",
            "E-Commerce Website",
            "Online Examination System",
            "Library Management System",
            "Inventory Management System",
            "Employee Management System",
            "Project Management System",
            "CRM Management System"
        ],

        "Mini Project": [
            "Calculator Application",
            "Expense Tracker",
            "Student Management System",
            "To-Do Application",
            "Weather Application",
            "Blog Website",
            "Portfolio Website",
            "Online Quiz Application",
            "Library Management System",
            "Attendance Management System"
        ],

        "Final Year Project": [
            "Hospital Management System",
            "College Management System",
            "E-Commerce Management System",
            "Student Project Management Portal",
            "ERP Management System",
            "Online Learning Management System",
            "Job Portal",
            "Employee Management System",
            "Inventory Management System",
            "Hotel Management System"
        ],

        "Internship Project": [
            "Web Development Project",
            "Full Stack Development Project",
            "React Web Application",
            "Django Web Application",
            "MERN Stack Application",
            "CRM Application",
            "ERP Application",
            "E-Commerce Website",
            "Portfolio Website",
            "Business Website"
        ],

        "Academic Project": [
            "Student Management System",
            "Library Management System",
            "Attendance Management System",
            "College Management System",
            "Employee Management System",
            "Inventory Management System",
            "Online Examination System",
            "Course Management System",
            "Result Management System",
            "Fee Management System"
        ],

        "Research Project": [
            "Market Research",
            "Consumer Behaviour Study",
            "Customer Satisfaction Analysis",
            "Employee Satisfaction Analysis",
            "Business Performance Analysis",
            "Digital Marketing Research",
            "Financial Market Analysis",
            "Sales Performance Analysis",
            "Low Code Research",
            "Business Data Analysis"
        ],

        "MBA Project": [
            "Marketing Management Project",
            "Financial Management Project",
            "Human Resource Management Project",
            "Operations Management Project",
            "Supply Chain Management Project",
            "International Business Project",
            "Business Analytics Project",
            "Strategic Management Project",
            "Customer Relationship Management Project",
            "Digital Marketing Project",
            "Consumer Behaviour Analysis",
            "Market Research Project",
            "Sales Management Project",
            "Retail Management Project",
            "Banking & Finance Project",
            "Investment Management Project",
            "Performance Management Project",
            "Recruitment & Selection Project",
            "Employee Satisfaction Survey",
            "Training & Development Project"
        ],

        "Other Project": [
            "Custom Project"
        ]
    }

    # =====================================================
    # CREATE EXCEL WORKBOOK
    # =====================================================

    workbook = Workbook()

    worksheet = workbook.active

    worksheet.title = "Project List"

    # =====================================================
    # HEADER
    # =====================================================

    worksheet["A1"] = "Project Type"

    worksheet["B1"] = "Related Project Title"

    worksheet["A1"].font = Font(
        bold=True
    )

    worksheet["B1"].font = Font(
        bold=True
    )

    worksheet["A1"].alignment = Alignment(
        horizontal="center"
    )

    worksheet["B1"].alignment = Alignment(
        horizontal="center"
    )

    # =====================================================
    # ADD PROJECT DATA
    # =====================================================

    row_number = 2

    for project_type, titles in project_list.items():

        for title in titles:

            worksheet.cell(
                row=row_number,
                column=1,
                value=project_type
            )

            worksheet.cell(
                row=row_number,
                column=2,
                value=title
            )

            row_number += 1

    # =====================================================
    # COLUMN WIDTH
    # =====================================================

    worksheet.column_dimensions["A"].width = 25

    worksheet.column_dimensions["B"].width = 45

    # =====================================================
    # FREEZE HEADER
    # =====================================================

    worksheet.freeze_panes = "A2"

    # =====================================================
    # DOWNLOAD RESPONSE
    # =====================================================

    response = HttpResponse(
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

    response["Content-Disposition"] = (
        'attachment; filename="Project_List.xlsx"'
    )

    workbook.save(response)

    return response