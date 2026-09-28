from django.shortcuts import render
from django.contrib import messages

from .models import ContactMessage


def contact_view(request):

    if request.method == 'POST':

        full_name = request.POST.get(
            'full_name',
            ''
        ).strip()

        email = request.POST.get(
            'email',
            ''
        ).strip()

        mobile = request.POST.get(
            'mobile',
            ''
        ).strip()

        subject = request.POST.get(
            'subject',
            ''
        ).strip()

        message = request.POST.get(
            'message',
            ''
        ).strip()


        # -----------------------------
        # VALIDATION
        # -----------------------------

        if not full_name:

            messages.error(
                request,
                'Please enter your full name.'
            )

            return render(
                request,
                'public/contact.html'
            )


        if not email:

            messages.error(
                request,
                'Please enter your email address.'
            )

            return render(
                request,
                'public/contact.html'
            )


        if not mobile.isdigit() or len(mobile) != 10:

            messages.error(
                request,
                'Please enter a valid 10-digit mobile number.'
            )

            return render(
                request,
                'public/contact.html'
            )


        if not subject:

            messages.error(
                request,
                'Please select a subject.'
            )

            return render(
                request,
                'public/contact.html'
            )


        if len(message) < 10:

            messages.error(
                request,
                'Message should contain at least 10 characters.'
            )

            return render(
                request,
                'public/contact.html'
            )


        # -----------------------------
        # SAVE CONTACT MESSAGE
        # -----------------------------

        ContactMessage.objects.create(

            full_name=full_name,

            email=email,

            mobile=mobile,

            subject=subject,

            message=message,

            status='New'
        )


        # -----------------------------
        # SUCCESS MESSAGE
        # -----------------------------

        messages.success(
            request,
            'Message sent successfully! '
            'Our support team will contact you soon.'
        )

        return render(
            request,
            'public/contact.html'
        )


    return render(
        request,
        'public/contact.html'
    )