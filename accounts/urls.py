
from django.urls import path
from . import views


urlpatterns = [

    # =====================================================
    # REGISTER
    # =====================================================

    path(
        'register/',
        views.register_view,
        name='user_register'
    ),


    # =====================================================
    # MSG91 OTP - SEND
    # =====================================================

    path(
        'send-registration-otp/',
        views.send_registration_otp,
        name='send_registration_otp'
    ),


    # =====================================================
    # MSG91 OTP - VERIFY
    # =====================================================

    path(
        'verify-registration-otp/',
        views.verify_registration_otp,
        name='verify_registration_otp'
    ),


    # =====================================================
    # FORGOT PASSWORD
    # =====================================================

    path(
        'forgot-password/',
        views.user_forgot_password,
        name='user_forgot_password'
    ),


    # =====================================================
    # RESET PASSWORD
    # =====================================================

    path(
        'reset-password/<uidb64>/<token>/',
        views.user_reset_password,
        name='user_reset_password'
    ),


    # =====================================================
    # LOGIN
    # =====================================================

    path(
        'login/',
        views.login_view,
        name='user_login'
    ),


    # =====================================================
    # LOGOUT
    # =====================================================

    path(
        'logout/',
        views.logout_view,
        name='user_logout'
    ),


    # =====================================================
    # STUDENT DASHBOARD
    # =====================================================

    path(
        'dashboard/',
        views.dashboard_view,
        name='user_dashboard'
    ),


    # =====================================================
    # STUDENT PROFILE
    # =====================================================

    path(
        'profile/',
        views.profile_view,
        name='user_profile'
    ),


    # =====================================================
    # STUDENT QUOTATION
    # =====================================================

    path(
        'quotation/',
        views.user_quotation,
        name='user_quotation'
    ),


    # =====================================================
    # ACCEPT / REJECT QUOTATION
    # =====================================================

    path(
        'quotation/<str:quotation_id>/<str:action>/',
        views.quotation_action,
        name='quotation_action'
    ),

]
