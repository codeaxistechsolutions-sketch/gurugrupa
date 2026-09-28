from django.urls import path

from . import views

from dashboard.views import (
    admin_quotations,
    admin_quotation_create,
    admin_quotation_update,
    admin_quotation_delete,
)


urlpatterns = [

    # ========================================================
    # ADMIN QUOTATIONS
    # ========================================================

    path(
        '',
        admin_quotations,
        name='admin_quotations'
    ),

    path(
        'create/',
        admin_quotation_create,
        name='admin_quotation_create'
    ),

    path(
        '<str:quotation_id>/update/',
        admin_quotation_update,
        name='admin_quotation_update'
    ),

    path(
        '<str:quotation_id>/delete/',
        admin_quotation_delete,
        name='admin_quotation_delete'
    ),

]