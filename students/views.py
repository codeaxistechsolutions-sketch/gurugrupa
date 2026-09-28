
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

from .models import StudentAcademic


@login_required
def academic_view(request):

    # Get existing academic record or create new one
    academic, created = StudentAcademic.objects.get_or_create(
        student=request.user
    )

    if request.method == 'POST':

        # ==========================================
        # CURRENT ACADEMIC DETAILS
        # ==========================================

        academic.course = request.POST.get(
            'course', ''
        ).strip()

        academic.branch = request.POST.get(
            'branch', ''
        ).strip()

        academic.college = request.POST.get(
            'college', ''
        ).strip()

        academic.university = request.POST.get(
            'university', ''
        ).strip()

        academic.current_year = request.POST.get(
            'current_year', ''
        ).strip()

        academic.semester = request.POST.get(
            'semester', ''
        ).strip()

        academic.academic_year = request.POST.get(
            'academic_year', ''
        ).strip()


        # ==========================================
        # SAVE
        # ==========================================

        academic.save()


        messages.success(
            request,
            'Academic details saved successfully.'
        )


        # ==========================================
        # SAVE & CONTINUE
        # Project Details page
        # ==========================================

        return redirect('user_project_details')


    # ==========================================
    # PAGE LOAD
    # ==========================================

    try:
        profile = request.user.profile
    except Exception:
        profile = None


    context = {
        'academic': academic,
        'profile': profile,
        'user': request.user,
    }


    return render(
        request,
        'user/academic/academic.html',
        context
    )