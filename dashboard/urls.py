
from django.urls import path

from . import views


urlpatterns = [

    # =========================================================
    # ADMIN LOGIN
    # =========================================================

    path(
        '',
        views.admin_login,
        name='admin_login'
    ),

    path(
        'login/',
        views.admin_login,
        name='admin_login_page'
    ),


    # =========================================================
    # ADMIN DASHBOARD
    # =========================================================

    path(
        'dashboard/',
        views.admin_dashboard,
        name='admin_dashboard'
    ),


    # =========================================================
    # STUDENTS
    # =========================================================

    path(
        'students/',
        views.admin_students,
        name='admin_students'
    ),

    path(
        'students/<int:student_id>/',
        views.admin_student_detail,
        name='admin_student_detail'
    ),


    # =========================================================
    # APPLICATIONS
    # =========================================================

    path(
        'applications/',
        views.admin_applications,
        name='admin_applications'
    ),

    path(
        'applications/<str:application_id>/action/',
        views.admin_application_action,
        name='admin_application_action'
    ),

    path(
        'applications/<str:application_id>/history/',
        views.admin_application_history,
        name='admin_application_history'
    ),


    # =========================================================
    # QUOTATIONS
    # =========================================================

    path(
        'quotations/',
        views.admin_quotations,
        name='admin_quotations'
    ),

    path(
        'quotations/create/',
        views.admin_quotation_create,
        name='admin_quotation_create'
    ),

    path(
        'quotations/<str:quotation_id>/update/',
        views.admin_quotation_update,
        name='admin_quotation_update'
    ),

    path(
        'quotations/<str:quotation_id>/delete/',
        views.admin_quotation_delete,
        name='admin_quotation_delete'
    ),


    # =========================================================
    # PAYMENTS
    # =========================================================

    path(
        'payments/',
        views.admin_payments,
        name='admin_payments'
    ),


    # =========================================================
    # PROJECT MANAGEMENT
    # =========================================================

    path(
        'projects/',
        views.admin_projects,
        name='admin_projects'
    ),

    path(
        'projects/<int:project_id>/update/',
        views.admin_project_update,
        name='admin_project_update'
    ),


    # =========================================================
    # PROJECT FINAL DELIVERY
    # =========================================================

    path(
        'projects/<int:project_id>/delivery/',
        views.admin_project_delivery,
        name='admin_project_delivery'
    ),

    path(
    'quotations/create/',
    views.admin_quotation_create,
    name='admin_quotation_create'
),

path(
    'quotations/<str:quotation_id>/update/',
    views.admin_quotation_update,
    name='admin_quotation_update'
),

path(
    'quotations/<str:quotation_id>/delete/',
    views.admin_quotation_delete,
    name='admin_quotation_delete'
),

    # =========================================================
    # ADMIN LOGOUT
    # =========================================================

    path(
        'logout/',
        views.admin_logout,
        name='admin_logout'
    ),

]

