from django.urls import path
from . import views


urlpatterns = [

    # Payment Page
    path(
        '',
        views.payment_view,
        name='user_payment'
    ),

    # Create Razorpay Order
    path(
        'razorpay/create-order/',
        views.create_razorpay_order,
        name='create_razorpay_order'
    ),

    # Verify Razorpay Payment
    path(
        'razorpay/verify/',
        views.verify_razorpay_payment,
        name='verify_razorpay_payment'
    ),

    # OLD / DEMO FLOW
    path(
        'confirm/',
        views.confirm_payment,
        name='confirm_payment'
    ),

    # Payment Receipt
    path(
        'receipt/<int:payment_id>/',
        views.payment_receipt,
        name='payment_receipt'
    ),
]