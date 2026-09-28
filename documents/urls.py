from django.urls import path
from . import views


urlpatterns = [

    # ==============================
    # USER / STUDENT DOCUMENTS
    # ==============================

    path(
        '',
        views.documents_view,
        name='user_documents'
    ),


    # ==============================
    # ADMIN DOCUMENTS
    # ==============================

    # Admin Documents List
    path(
        'admin/',
        views.admin_documents,
        name='admin_documents'
    ),

    # Approve / Reject Document
    path(
        'admin/<str:document_id>/action/',
        views.admin_document_action,
        name='admin_document_action'
    ),

    # Download Document
    path(
        'admin/<str:document_id>/download/',
        views.admin_document_download,
        name='admin_document_download'
    ),
]