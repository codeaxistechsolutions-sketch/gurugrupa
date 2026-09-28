from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.utils import timezone

from django.db.models import Q

from django.http import (
    FileResponse,
    Http404
)

from .models import StudentDocument


# ============================================================
# FILE VALIDATION SETTINGS
# ============================================================

ALLOWED_EXTENSIONS = [
    '.pdf',
    '.doc',
    '.docx',
    '.jpg',
    '.jpeg',
    '.png',
]

# Maximum file size = 5 MB
MAX_FILE_SIZE = 5 * 1024 * 1024


# ============================================================
# STUDENT DOCUMENTS
# ============================================================

@login_required
def documents_view(request):

    # --------------------------------------------------------
    # POST - Upload Documents
    # --------------------------------------------------------

    if request.method == 'POST':

        document_fields = {
            'college_id': 'college_id',
            'bonafide': 'bonafide',
            'marksheet': 'marksheet',
            'project_proposal': 'project_proposal',
        }

        uploaded_any = False

        for field_name, document_type in document_fields.items():

            uploaded_file = request.FILES.get(field_name)

            # No file selected
            if not uploaded_file:
                continue

            uploaded_any = True

            # ------------------------------------------------
            # File Name Validation
            # ------------------------------------------------

            file_name = uploaded_file.name.lower()

            if '.' not in file_name:

                messages.error(
                    request,
                    f'Invalid file selected for {document_type}.'
                )

                continue

            # Get extension
            extension = '.' + file_name.rsplit(
                '.',
                1
            )[-1]

            # ------------------------------------------------
            # Extension Validation
            # ------------------------------------------------

            if extension not in ALLOWED_EXTENSIONS:

                messages.error(
                    request,
                    f'{uploaded_file.name} is not a supported file type.'
                )

                continue

            # ------------------------------------------------
            # File Size Validation
            # ------------------------------------------------

            if uploaded_file.size > MAX_FILE_SIZE:

                messages.error(
                    request,
                    f'{uploaded_file.name} is larger than 5 MB.'
                )

                continue

            # ------------------------------------------------
            # Check Existing Document
            # ------------------------------------------------

            existing_document = StudentDocument.objects.filter(
                student=request.user,
                document_type=document_type
            ).first()

            # ------------------------------------------------
            # Update Existing Document
            # ------------------------------------------------

            if existing_document:

                # Delete old physical file
                if existing_document.file:

                    try:

                        existing_document.file.delete(
                            save=False
                        )

                    except Exception:

                        pass

                existing_document.file = uploaded_file

                # New upload requires fresh admin review
                existing_document.status = 'Pending Review'

                # Clear previous admin review data
                existing_document.admin_remark = ''
                existing_document.reviewed_at = None

                existing_document.save()

            # ------------------------------------------------
            # Create New Document
            # ------------------------------------------------

            else:

                StudentDocument.objects.create(
                    student=request.user,
                    document_type=document_type,
                    file=uploaded_file,
                    status='Pending Review'
                )

        # ----------------------------------------------------
        # Success Message
        # ----------------------------------------------------

        if uploaded_any:

            messages.success(
                request,
                'Documents uploaded successfully and sent for review.'
            )

        else:

            messages.warning(
                request,
                'Please select at least one document to upload.'
            )

        return redirect('user_documents')

    # ========================================================
    # GET - Display Student Documents
    # ========================================================

    documents = StudentDocument.objects.filter(
        student=request.user
    ).order_by('-uploaded_at')

    context = {
        'documents': documents,
    }

    return render(
        request,
        'user/documents/documents.html',
        context
    )


# ============================================================
# ADMIN DOCUMENT LIST
# ============================================================

@login_required
def admin_documents(request):

    # --------------------------------------------------------
    # Admin Permission Check
    # --------------------------------------------------------

    if not request.user.is_staff:

        messages.error(
            request,
            "You are not authorized to access Admin Panel."
        )

        return redirect('admin_login')

    # --------------------------------------------------------
    # Get All Documents
    # --------------------------------------------------------

    documents = StudentDocument.objects.select_related(
        'student'
    ).order_by('-uploaded_at')

    # --------------------------------------------------------
    # GET Filters
    # --------------------------------------------------------

    search = request.GET.get(
        'search',
        ''
    ).strip()

    document_type = request.GET.get(
        'document_type',
        ''
    ).strip()

    status = request.GET.get(
        'status',
        ''
    ).strip()

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    if search:

        documents = documents.filter(

            Q(document_id__icontains=search) |

            Q(file__icontains=search) |

            Q(student__username__icontains=search) |

            Q(student__first_name__icontains=search) |

            Q(student__last_name__icontains=search) |

            Q(student__email__icontains=search)

        )

    # --------------------------------------------------------
    # Document Type Filter
    # --------------------------------------------------------

    if document_type:

        documents = documents.filter(
            document_type=document_type
        )

    # --------------------------------------------------------
    # Status Filter
    # --------------------------------------------------------

    if status:

        documents = documents.filter(
            status=status
        )

    # ========================================================
    # ADMIN STATISTICS
    # ========================================================

    total_documents = StudentDocument.objects.count()

    pending_documents = StudentDocument.objects.filter(
        status='Pending Review'
    ).count()

    approved_documents = StudentDocument.objects.filter(
        status='Approved'
    ).count()

    rejected_documents = StudentDocument.objects.filter(
        status='Rejected'
    ).count()

    # ========================================================
    # CONTEXT
    # ========================================================

    context = {

        'documents': documents,

        'total_documents': total_documents,

        'pending_documents': pending_documents,

        'approved_documents': approved_documents,

        'rejected_documents': rejected_documents,

        'search': search,

        'document_type': document_type,

        'status': status,

        'document_types': StudentDocument.DOCUMENT_TYPES,

        'status_choices': StudentDocument.STATUS_CHOICES,

    }

    return render(
        request,
        'admin/documents/list.html',
        context
    )


# ============================================================
# ADMIN APPROVE / REJECT DOCUMENT
# ============================================================

@login_required
def admin_document_action(request, document_id):

    # --------------------------------------------------------
    # Admin Permission Check
    # --------------------------------------------------------

    if not request.user.is_staff:

        messages.error(
            request,
            "You are not authorized to access Admin Panel."
        )

        return redirect('admin_login')

    # --------------------------------------------------------
    # Only POST Allowed
    # --------------------------------------------------------

    if request.method != 'POST':

        return redirect('admin_documents')

    # --------------------------------------------------------
    # Get Document
    # --------------------------------------------------------

    document = get_object_or_404(
        StudentDocument,
        document_id=document_id
    )

    # --------------------------------------------------------
    # Get Action
    # --------------------------------------------------------

    action = request.POST.get(
        'action',
        ''
    ).strip()

    # --------------------------------------------------------
    # Get Admin Remark
    # --------------------------------------------------------

    remark = request.POST.get(
        'admin_remark',
        ''
    ).strip()

    # --------------------------------------------------------
    # Validate Action
    # --------------------------------------------------------

    if action not in [
        'Approved',
        'Rejected'
    ]:

        messages.error(
            request,
            "Invalid document action."
        )

        return redirect('admin_documents')

    # --------------------------------------------------------
    # Rejection Requires Remark
    # --------------------------------------------------------

    if action == 'Rejected' and not remark:

        messages.error(
            request,
            "Admin remark is required when rejecting a document."
        )

        return redirect('admin_documents')

    # --------------------------------------------------------
    # Update Document
    # --------------------------------------------------------

    document.status = action

    document.admin_remark = remark

    document.reviewed_at = timezone.now()

    document.save(
        update_fields=[
            'status',
            'admin_remark',
            'reviewed_at',
            'updated_at'
        ]
    )

    # --------------------------------------------------------
    # Success Message
    # --------------------------------------------------------

    if action == 'Approved':

        messages.success(
            request,
            f"Document {document.document_id} approved successfully."
        )

    else:

        messages.warning(
            request,
            f"Document {document.document_id} rejected successfully."
        )

    return redirect('admin_documents')


# ============================================================
# ADMIN DOCUMENT DOWNLOAD
# ============================================================

@login_required
def admin_document_download(request, document_id):

    # --------------------------------------------------------
    # Admin Permission Check
    # --------------------------------------------------------

    if not request.user.is_staff:

        raise Http404()

    # --------------------------------------------------------
    # Get Document
    # --------------------------------------------------------

    document = get_object_or_404(
        StudentDocument,
        document_id=document_id
    )

    # --------------------------------------------------------
    # Check File
    # --------------------------------------------------------

    if not document.file:

        raise Http404(
            "Document file not found."
        )

    # --------------------------------------------------------
    # Open File
    # --------------------------------------------------------

    try:

        return FileResponse(
            document.file.open('rb'),
            as_attachment=True,
            filename=document.file.name.split('/')[-1]
        )

    except Exception:

        raise Http404(
            "Unable to open document."
        )