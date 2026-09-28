from django.urls import path
from . import views


urlpatterns = [

    path(
        'academic/',
        views.academic_view,
        name='user_academic'
    ),

]