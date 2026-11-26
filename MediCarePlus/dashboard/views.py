from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from accounts.decorators import admin_required, doctor_required
from medicines.models import Medicine
from orders.models import Order
from appointments.models import Appointment
from prescriptions.models import Prescription
from payments.models import Payment
from django.db.models import Sum, Count
from django.utils import timezone

User = get_user_model()


@login_required
def home(request):
    user = request.user
    if user.role == 'ADMIN':
        return admin_dashboard(request)
    elif user.role == 'DOCTOR':
        return doctor_dashboard(request)
    else:
        return patient_dashboard(request)


@admin_required
def admin_dashboard(request):
    today = timezone.now().date()
    context = {
        'total_users': User.objects.filter(role='PATIENT').count(),
        'total_doctors': User.objects.filter(role='DOCTOR').count(),
        'total_medicines': Medicine.objects.filter(is_active=True).count(),
        'total_orders': Order.objects.count(),
        'total_revenue': Payment.objects.filter(status='SUCCESS').aggregate(Sum('amount'))['amount__sum'] or 0,
        'total_appointments': Appointment.objects.count(),
        'recent_orders': Order.objects.order_by('-created_at')[:5],
        'pending_prescriptions': Prescription.objects.filter(status='PENDING').count(),
        'low_stock_medicines': Medicine.objects.filter(stock__lt=10, is_active=True)[:5],
        'recent_appointments': Appointment.objects.order_by('-created_at')[:5],
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@doctor_required
def doctor_dashboard(request):
    user = request.user
    context = {
        'pending_appointments': Appointment.objects.filter(doctor=user, status='PENDING').count(),
        'today_appointments': Appointment.objects.filter(
            doctor=user,
            appointment_date=timezone.now().date()
        ),
        'total_patients': Appointment.objects.filter(doctor=user).values('patient').distinct().count(),
        'recent_appointments': Appointment.objects.filter(doctor=user).order_by('-created_at')[:10],
        'pending_prescriptions': Prescription.objects.filter(status='PENDING').count(),
    }
    return render(request, 'dashboard/doctor_dashboard.html', context)


@login_required
def patient_dashboard(request):
    user = request.user
    context = {
        'recent_orders': Order.objects.filter(user=user).order_by('-created_at')[:3],
        'appointments': Appointment.objects.filter(patient=user).order_by('-created_at')[:3],
        'prescriptions': user.prescriptions.all().order_by('-uploaded_at')[:3],
        'total_orders': Order.objects.filter(user=user).count(),
    }
    return render(request, 'dashboard/patient_dashboard.html', context)