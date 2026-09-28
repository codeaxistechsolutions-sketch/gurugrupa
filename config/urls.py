from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.html import escape
from dashboard import views



# ==========================================
# HOME PAGE
# ==========================================

def home_view(request):

    return render(
        request,
        'public/index.html'
    )


# ==========================================
# ABOUT US PAGE
# ==========================================

def about_view(request):

    return render(
        request,
        'public/about.html'
    )


# ==========================================
# PROJECT SERVICES PAGE
# ==========================================

def services_view(request):

    return render(
        request,
        'public/services.html'
    )


# ==========================================
# CONTACT US PAGE
# ==========================================

def contact_view(request):

    return render(
        request,
        'public/contact.html'
    )


# ==========================================
# HOW IT WORKS PAGE
# ==========================================

def how_it_works_view(request):

    return render(
        request,
        'public/how-it-works.html'
    )


# ==========================================
# DOWNLOADS PAGE
# ==========================================

def downloads_view(request):

    return render(
        request,
        'public/downloads.html'
    )


# ==========================================
# DOCUMENT VIEW / PREVIEW
# ==========================================

def document_view(request, filename):

    # --------------------------------------
    # FILE NAME
    # --------------------------------------

    safe_filename = escape(filename)

    document_title = filename.rsplit(
        '.',
        1
    )[0]

    document_title = (
        document_title
        .replace('-', ' ')
        .replace('_', ' ')
        .title()
    )

    # --------------------------------------
    # PDF PREVIEW
    # --------------------------------------

    if filename.lower().endswith('.pdf'):

        context = {
            'filename': filename,
            'title': document_title,
        }

        return render(
            request,
            'public/document-preview.html',
            context
        )

    # --------------------------------------
    # DOCX PREVIEW
    # --------------------------------------

    if filename.lower().endswith('.docx'):

        context = {

            'filename': filename,

            'title': document_title,

            'paragraphs': [

                'Student Project Portal',

                document_title,

                'This document is provided for student project development and submission.',

                'Please follow the project guidelines and complete all required sections.',

                'Maintain proper documentation and verify your project before final submission.',

                'Keep a backup copy of the completed project.',

            ],

        }

        return render(
            request,
            'public/document-preview.html',
            context
        )

    # --------------------------------------
    # PPTX PREVIEW
    # --------------------------------------

    if filename.lower().endswith('.pptx'):

        context = {

            'filename': filename,

            'title': document_title,

            'slides': [

                {
                    'number': 1,

                    'texts': [
                        'Student Project Portal',
                        document_title,
                        'Student Name: ____________________',
                        'Project Guide: ____________________',
                    ]
                },

                {
                    'number': 2,

                    'texts': [
                        'Project Overview',
                        'Problem Statement',
                        'Project Objectives',
                        'Project Scope',
                    ]
                },

                {
                    'number': 3,

                    'texts': [
                        'Technology Stack',
                        'Frontend',
                        'Backend',
                        'Database',
                    ]
                },

                {
                    'number': 4,

                    'texts': [
                        'Project Modules',
                        'Implementation Details',
                        'Testing',
                        'Results',
                    ]
                },

                {
                    'number': 5,

                    'texts': [
                        'Conclusion',
                        'Future Scope',
                        'References',
                    ]
                },

            ],

        }

        return render(
            request,
            'public/presentation-preview.html',
            context
        )

    # --------------------------------------
    # OTHER FILE TYPES
    # --------------------------------------

    return render(
        request,
        'public/document-preview.html',
        {
            'filename': filename,

            'title': document_title,

            'paragraphs': [
                'Student Project Portal',
                'Document Preview',
                f'This document is available for viewing: {safe_filename}',
            ],
        }
    )


# ==========================================
# DOWNLOAD FILE
# ==========================================

def download_file_view(request, filename):

    # --------------------------------------
    # FILE NAME
    # --------------------------------------

    safe_filename = escape(filename)

    document_title = filename.rsplit(
        '.',
        1
    )[0]

    document_title = (
        document_title
        .replace('-', ' ')
        .replace('_', ' ')
        .title()
    )

    # ======================================
    # PDF DOWNLOAD
    # ======================================

    if filename.lower().endswith('.pdf'):

        pdf_content = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] >>
endobj
trailer
<< /Root 1 0 R >>
%%EOF
"""

        response = HttpResponse(
            pdf_content,
            content_type='application/pdf'
        )

        response['Content-Disposition'] = (
            f'attachment; filename="{filename}"'
        )

        return response

    # ======================================
    # DOCX / PPTX DEMO DOWNLOAD
    # ======================================

    response = HttpResponse(

        f"""
        <!DOCTYPE html>

        <html>

        <head>

            <meta charset="UTF-8">

            <title>
                Download - {safe_filename}
            </title>

            <style>

                body {{
                    font-family: Arial, sans-serif;
                    background: #F5F7FB;
                    text-align: center;
                    padding: 80px 20px;
                }}

                .box {{
                    max-width: 650px;
                    margin: auto;
                    background: white;
                    padding: 40px;
                    border-radius: 12px;
                    box-shadow:
                        0 10px 30px
                        rgba(0,0,0,0.08);
                }}

                h1 {{
                    color: #172554;
                }}

                p {{
                    color: #64748B;
                    line-height: 1.7;
                }}

                .btn {{
                    display: inline-block;
                    margin-top: 20px;
                    padding: 12px 22px;
                    background: #2563EB;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                }}

            </style>

        </head>

        <body>

            <div class="box">

                <h1>
                    {document_title}
                </h1>

                <p>
                    Your requested document action
                    has been performed successfully.
                </p>

                <p>
                    This is a temporary demo document
                    generated by Student Project Portal.
                </p>

                <a
                    href="/downloads/"
                    class="btn"
                >
                    Back to Downloads
                </a>

            </div>

        </body>

        </html>
        """,

        content_type='text/html'
    )

    response['Content-Disposition'] = (
        f'attachment; filename="{filename}.html"'
    )

    return response


# ==========================================
# URL PATTERNS
# ==========================================

urlpatterns = [

    # ======================================
    # HOME
    # ======================================

    path(
        '',
        home_view,
        name='home'
    ),


    # ======================================
    # ABOUT US
    # ======================================

    path(
        'about/',
        about_view,
        name='about'
    ),


    # ======================================
    # PROJECT SERVICES
    # ======================================

    path(
        'services/',
        services_view,
        name='project_services'
    ),


    # ======================================
    # CONTACT US
    # ======================================

    path(
        'contact/',
        contact_view,
        name='contact'
    ),


    # ======================================
    # HOW IT WORKS
    # ======================================

    path(
        'how-it-works/',
        how_it_works_view,
        name='how_it_works'
    ),


    # ======================================
    # DOWNLOADS PAGE
    # ======================================

    path(
        'downloads/',
        downloads_view,
        name='downloads'
    ),


    # ======================================
    # DOCUMENT VIEW
    # ======================================

    path(
        'downloads/view/<str:filename>/',
        document_view,
        name='document_view'
    ),


    # ======================================
    # DOCUMENT DOWNLOAD
    # ======================================

    path(
        'downloads/download/<str:filename>/',
        download_file_view,
        name='download_file'
    ),


    # ======================================
    # CUSTOM ADMIN
    #
    # All admin URLs are handled by
    # dashboard/urls.py
    #
    # Example:
    # /admin/
    # /admin/login/
    # /admin/dashboard/
    # /admin/applications/
    # /admin/quotations/
    # /admin/payments/
    #
    # ======================================

    path(
        'admin/',
        include('dashboard.urls')
    ),


    # ======================================
    # USER ACCOUNT
    # ======================================

    path(
        'account/',
        include('accounts.urls')
    ),


    # ======================================
    # STUDENT ACADEMIC
    # ======================================

    path(
        'student/',
        include('students.urls')
    ),


    # ======================================
    # PROJECT
    # ======================================

    path(
        'project/',
        include('projects.urls')
    ),

    path(
    'admin/projects/<int:project_id>/update/',
    views.admin_project_update,
    name='admin_project_update'
    ),



    # ======================================
    # DOCUMENTS
    # ======================================

    path(
        'documents/',
        include('documents.urls')
    ),


    # ======================================
    # QUOTATION
    # ======================================

    path(
        'quotation/',
        include('quotations.urls')
    ),


    # ======================================
    # PAYMENT
    # ======================================

    path(
        'payment/',
        include('payments.urls')
    ),


    # ======================================
    # TRACKING
    # ======================================

    path(
        'tracking/',
        include('tracking.urls')
    ),

    path(
    'admin/forgot-password/',
    views.admin_forgot_password,
    name='admin_forgot_password'
),

path(
    'admin/reset-password/<uidb64>/<token>/',
    views.admin_reset_password,
    name='admin_reset_password'
),

]


# ==========================================
# MEDIA FILES
# ==========================================

if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )