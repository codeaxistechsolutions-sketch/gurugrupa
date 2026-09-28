from django.shortcuts import render
from django.contrib.auth.decorators import login_required


# =========================================================
# STUDENT TRACK APPLICATION
# =========================================================

@login_required
def track_application(request):

    tracking = (
        request.user.project_tracking
        .select_related('project')
        .first()
    )

    profile = getattr(
        request.user,
        'profile',
        None
    )

    context = {
        'tracking': tracking,
        'profile': profile,
        'user': request.user,
    }

    return render(
        request,
        'user/tracking/track-application.html',
        context
    )