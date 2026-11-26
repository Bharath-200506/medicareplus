from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Prescription
from accounts.decorators import patient_required, role_required
from notifications.utils import create_notification
from django.conf import settings
import os


@patient_required
def upload_prescription(request):
    if request.method == 'POST':
        file = request.FILES.get('prescription_file')
        if not file:
            messages.error(request, 'Please select a file.')
            return redirect('prescriptions:upload')

        # Validate file
        allowed_types = ['image/jpeg', 'image/png', 'application/pdf']
        if file.content_type not in allowed_types:
            messages.error(request, 'Only JPG, PNG, or PDF files are allowed.')
            return redirect('prescriptions:upload')

        if file.size > settings.MAX_UPLOAD_SIZE:
            messages.error(request, 'File size must be under 5MB.')
            return redirect('prescriptions:upload')

        prescription = Prescription.objects.create(
            patient=request.user,
            file=file,
        )
        create_notification(request.user, 'Your prescription has been uploaded and is under review.', 'PRESCRIPTION')
        messages.success(request, 'Prescription uploaded successfully! We will review it shortly.')
        return redirect('prescriptions:list')

    return render(request, 'prescriptions/upload.html')


@patient_required
def prescription_list(request):
    prescriptions = Prescription.objects.filter(patient=request.user)
    return render(request, 'prescriptions/list.html', {'prescriptions': prescriptions})


@role_required('DOCTOR', 'ADMIN')
def review_prescriptions(request):
    prescriptions = Prescription.objects.filter(status='PENDING')
    return render(request, 'prescriptions/review.html', {'prescriptions': prescriptions})


@role_required('DOCTOR', 'ADMIN')
def approve_prescription(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    prescription.status = 'APPROVED'
    prescription.reviewed_by = request.user
    prescription.reviewed_at = timezone.now()
    prescription.notes = request.POST.get('notes', '')
    prescription.save()
    create_notification(prescription.patient, 'Your prescription has been approved.', 'PRESCRIPTION')
    messages.success(request, 'Prescription approved.')
    return redirect('prescriptions:review')


@role_required('DOCTOR', 'ADMIN')
def reject_prescription(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    prescription.status = 'REJECTED'
    prescription.reviewed_by = request.user
    prescription.reviewed_at = timezone.now()
    prescription.rejection_reason = request.POST.get('rejection_reason', '')
    prescription.save()
    create_notification(prescription.patient, 'Your prescription was rejected. Please re-upload.', 'PRESCRIPTION')
    messages.info(request, 'Prescription rejected.')
    return redirect('prescriptions:review')