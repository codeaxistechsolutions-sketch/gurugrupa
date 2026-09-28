from django.urls import path
from . import views


urlpatterns = [
    path(
        'details/',
        views.project_details_view,
        name='user_project_details'
    ),

    
    path(
        'download-excel/',
        views.download_project_excel,
        name='download_project_excel'
    ),
]