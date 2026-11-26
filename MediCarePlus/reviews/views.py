from django.shortcuts import render

# Create your views here.
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import MedicineReview, DoctorReview
from medicines.models import Medicine

User = get_user_model()


@login_required
def add_medicine_review(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        MedicineReview.objects.update_or_create(
            medicine=medicine,
            user=request.user,
            defaults={'rating': rating, 'comment': comment}
        )
        messages.success(request, 'Review submitted successfully!')
    return redirect('medicines:detail', pk=pk)


@login_required
def add_doctor_review(request, doctor_id):
    doctor = get_object_or_404(User, id=doctor_id, role='DOCTOR')
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        DoctorReview.objects.update_or_create(
            doctor=doctor,
            patient=request.user,
            defaults={'rating': rating, 'comment': comment}
        )
        messages.success(request, 'Doctor review submitted!')
    return redirect('appointments:doctor_list')