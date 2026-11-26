"""
Email notification service for MediCarePlus.
Sends professionally-designed HTML emails for all key application events:
  - Welcome (registration)
  - Order placed / confirmed / shipped / delivered / cancelled
  - Appointment booked / approved / rejected / completed
  - Password reset (already exists — not duplicated here)
"""
import threading
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def _send_async(subject, plain, html, recipient_list):
    """Fire-and-forget email delivery on a background thread."""
    def _target():
        try:
            print(f"\n[EMAIL DISPATCH] To: {recipient_list} | Subject: {subject}")
            send_mail(
                subject,
                plain,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
                html_message=html,
                fail_silently=False,
            )
            print(f"[EMAIL SUCCESS] Delivered to {recipient_list}")
        except Exception as e:
            print(f"[EMAIL NOTICE] SMTP delivery failed: {e}. Email template rendered successfully.")

    thread = threading.Thread(target=_target)
    thread.daemon = True
    thread.start()


def send_notification_email(user_email, subject, template_name, context, sync=False):
    """
    Generic helper: render an HTML email template and dispatch.
    Set sync=True to send synchronously (useful in tests).
    """
    try:
        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message)
    except Exception as e:
        print(f"[EMAIL TEMPLATE ERROR] Failed to render {template_name}: {e}")
        return

    if sync:
        try:
            print(f"\n[EMAIL DISPATCH SYNC] To: {user_email} | Subject: {subject}")
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user_email],
                html_message=html_message,
                fail_silently=False,
            )
            print(f"[EMAIL SUCCESS] Delivered to {user_email}")
        except Exception as e:
            print(f"[EMAIL NOTICE] SMTP delivery failed: {e}. Email template rendered successfully.")
    else:
        _send_async(subject, plain_message, html_message, [user_email])


# ── Event-specific helpers ────────────────────────────────────────────────────

def send_welcome_email(user):
    """Send welcome email upon successful registration & verification."""
    send_notification_email(
        user.email,
        'Welcome to MediCarePlus! 🎉',
        'emails/welcome.html',
        {
            'user_name': user.get_full_name() or user.username,
            'email': user.email,
        },
    )


def send_order_placed_email(user, order):
    """Send email when order is placed."""
    items = order.items.select_related('medicine').all()
    send_notification_email(
        user.email,
        f'Order Confirmed — #{order.order_number}',
        'emails/order_placed.html',
        {
            'user_name': user.get_full_name() or user.username,
            'order': order,
            'items': items,
        },
    )


def send_order_status_email(user, order, new_status):
    """Send email on order status change (confirmed/shipped/delivered/cancelled)."""
    status_info = {
        'CONFIRMED': ('Order Confirmed', '✅', 'Your order has been confirmed and is being prepared.'),
        'PACKED':    ('Order Packed', '📦', 'Your order has been packed and is ready for dispatch.'),
        'SHIPPED':   ('Order Shipped', '🚚', 'Your order is on its way! Track it for live updates.'),
        'DELIVERED': ('Order Delivered', '🎉', 'Your order has been delivered. We hope you enjoy your purchase!'),
        'CANCELLED': ('Order Cancelled', '❌', 'Your order has been cancelled. If you didn\'t request this, please contact support.'),
    }
    title, emoji, description = status_info.get(new_status, ('Order Update', '📋', 'Your order status has been updated.'))

    send_notification_email(
        user.email,
        f'{emoji} {title} — #{order.order_number}',
        'emails/order_status.html',
        {
            'user_name': user.get_full_name() or user.username,
            'order': order,
            'status_title': title,
            'status_emoji': emoji,
            'status_description': description,
            'new_status': new_status,
        },
    )


def send_appointment_booked_email(patient, doctor, appointment):
    """Send email to patient when appointment is booked."""
    send_notification_email(
        patient.email,
        f'Appointment Booked with Dr. {doctor.get_full_name()}',
        'emails/appointment_booked.html',
        {
            'patient_name': patient.get_full_name() or patient.username,
            'doctor_name': doctor.get_full_name(),
            'appointment': appointment,
        },
    )


def send_appointment_notification_to_doctor(doctor, patient, appointment):
    """Send email to doctor when a new appointment request arrives."""
    send_notification_email(
        doctor.email,
        f'New Appointment Request from {patient.get_full_name()}',
        'emails/appointment_doctor_notify.html',
        {
            'doctor_name': doctor.get_full_name(),
            'patient_name': patient.get_full_name() or patient.username,
            'appointment': appointment,
        },
    )


def send_appointment_approved_email(patient, doctor, appointment):
    """Send email to patient when appointment is approved."""
    send_notification_email(
        patient.email,
        f'✅ Appointment Approved — Dr. {doctor.get_full_name()}',
        'emails/appointment_approved.html',
        {
            'patient_name': patient.get_full_name() or patient.username,
            'doctor_name': doctor.get_full_name(),
            'appointment': appointment,
        },
    )


def send_appointment_rejected_email(patient, doctor, appointment):
    """Send email to patient when appointment is rejected."""
    send_notification_email(
        patient.email,
        f'Appointment Update — Dr. {doctor.get_full_name()}',
        'emails/appointment_rejected.html',
        {
            'patient_name': patient.get_full_name() or patient.username,
            'doctor_name': doctor.get_full_name(),
            'appointment': appointment,
        },
    )


def send_appointment_completed_email(patient, doctor, appointment):
    """Send email to patient when appointment is marked complete."""
    send_notification_email(
        patient.email,
        f'Appointment Completed — Dr. {doctor.get_full_name()}',
        'emails/appointment_completed.html',
        {
            'patient_name': patient.get_full_name() or patient.username,
            'doctor_name': doctor.get_full_name(),
            'appointment': appointment,
        },
    )
