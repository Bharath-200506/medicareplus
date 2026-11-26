from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Appointment, DoctorAvailability
from accounts.decorators import patient_required, doctor_required
from notifications.utils import create_notification
from notifications.email_service import (
    send_appointment_booked_email,
    send_appointment_notification_to_doctor,
    send_appointment_approved_email,
    send_appointment_rejected_email,
    send_appointment_completed_email,
)

User = get_user_model()


def doctor_list(request):
    doctors = User.objects.filter(role='DOCTOR').select_related('doctor_profile')
    specialization = request.GET.get('specialization', '')
    if specialization:
        doctors = doctors.filter(doctor_profile__specialization__icontains=specialization)
    
    specializations = [
        "Cardiologist", "Dermatologist", "Pediatrician", 
        "Neurologist", "Orthopedist", "Gynecologist", 
        "ENT", "General Physician"
    ]
    return render(request, 'appointments/doctor_list.html', {
        'doctors': doctors,
        'specializations': specializations
    })


@patient_required
def book_appointment(request, doctor_id):
    doctor = get_object_or_404(User, id=doctor_id, role='DOCTOR')
    availability = DoctorAvailability.objects.filter(doctor=doctor, is_available=True)

    if request.method == 'POST':
        appt_date = request.POST.get('appointment_date')
        appt_time = request.POST.get('appointment_time')
        reason = request.POST.get('reason')
        payment_method = request.POST.get('payment_method', 'ONLINE')

        payment_status = 'PENDING' if payment_method == 'ONLINE' else 'PAY_AT_CLINIC'

        appointment = Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            appointment_date=appt_date,
            appointment_time=appt_time,
            reason=reason,
            consultation_fee=doctor.doctor_profile.consultation_fee,
            payment_method=payment_method,
            payment_status=payment_status,
        )
        create_notification(request.user, f'Appointment booked with Dr. {doctor.get_full_name()}.', 'APPOINTMENT')
        create_notification(doctor, f'New appointment request from {request.user.get_full_name()}.', 'APPOINTMENT')

        if payment_method == 'ONLINE':
            return redirect('payments:initiate_appointment', appointment_id=appointment.id)
        else:
            send_appointment_booked_email(request.user, doctor, appointment)
            send_appointment_notification_to_doctor(doctor, request.user, appointment)
            messages.success(request, f'Appointment booked successfully with Dr. {doctor.get_full_name()}! Fee to be paid at clinic.')
            return redirect('appointments:list')

    context = {'doctor': doctor, 'availability': availability}
    return render(request, 'appointments/book.html', context)


@patient_required
def appointment_list(request):
    appointments = Appointment.objects.filter(patient=request.user)
    return render(request, 'appointments/list.html', {'appointments': appointments})


@doctor_required
def doctor_appointments(request):
    appointments = Appointment.objects.filter(doctor=request.user)
    return render(request, 'appointments/doctor_appointments.html', {'appointments': appointments})


@doctor_required
def approve_appointment(request, pk):
    appt = get_object_or_404(Appointment, pk=pk, doctor=request.user)
    appt.status = 'APPROVED'
    appt.notes = request.POST.get('notes', '')
    appt.save()
    create_notification(appt.patient, f'Your appointment with Dr. {request.user.get_full_name()} has been approved.', 'APPOINTMENT')
    send_appointment_approved_email(appt.patient, appt.doctor, appt)
    messages.success(request, 'Appointment approved and confirmation email sent to patient.')
    return redirect('appointments:doctor_appointments')


@doctor_required
def reject_appointment(request, pk):
    appt = get_object_or_404(Appointment, pk=pk, doctor=request.user)
    appt.status = 'REJECTED'
    appt.rejection_reason = request.POST.get('rejection_reason', '')
    appt.save()
    create_notification(appt.patient, f'Your appointment with Dr. {request.user.get_full_name()} was rejected.', 'APPOINTMENT')
    send_appointment_rejected_email(appt.patient, appt.doctor, appt)
    messages.info(request, 'Appointment rejected.')
    return redirect('appointments:doctor_appointments')


@doctor_required
def complete_appointment(request, pk):
    appt = get_object_or_404(Appointment, pk=pk, doctor=request.user)
    if appt.status == 'APPROVED':
        appt.status = 'COMPLETED'
        notes = request.POST.get('notes', '')
        if notes:
            appt.notes = notes
        appt.save()
        create_notification(appt.patient, f'Your appointment with Dr. {request.user.get_full_name()} has been marked as Completed.', 'APPOINTMENT')
        send_appointment_completed_email(appt.patient, appt.doctor, appt)
        messages.success(request, 'Appointment marked as Completed.')
    else:
        messages.error(request, 'Only approved appointments can be marked as Completed.')
    return redirect('appointments:doctor_appointments')


@login_required
@doctor_required
def send_patient_message(request, pk):
    appt = get_object_or_404(Appointment, pk=pk, doctor=request.user)
    if request.method == 'POST':
        message_content = request.POST.get('message_content')
        if message_content:
            create_notification(
                appt.patient,
                f"Message from Dr. {request.user.get_full_name()}: {message_content}",
                'APPOINTMENT'
            )
            messages.success(request, 'Message sent to patient successfully!')
    return redirect('appointments:doctor_appointments')