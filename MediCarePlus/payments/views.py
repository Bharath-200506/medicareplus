from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
import razorpay
import hmac
import hashlib
import json
import random
from .models import Payment
from orders.models import Order, OrderTracking
from appointments.models import Appointment
from notifications.utils import create_notification
from notifications.email_service import (
    send_order_placed_email,
    send_appointment_booked_email,
    send_appointment_notification_to_doctor,
)


@login_required
def initiate_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Check if keys are placeholder values or missing
    key_id = getattr(settings, 'RAZORPAY_KEY_ID', '')
    key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '')
    is_mock = not key_id or not key_secret or key_id.startswith('your_') or key_secret.startswith('your_')

    amount_paise = int(order.grand_total * 100)
    razorpay_order_id = None
    fallback_to_mock = False

    if not is_mock:
        try:
            client = razorpay.Client(auth=(key_id, key_secret))
            razorpay_order = client.order.create({
                'amount': amount_paise,
                'currency': 'INR',
                'receipt': order.order_number,
                'payment_capture': 1,
            })
            razorpay_order_id = razorpay_order['id']
        except Exception:
            # Fall back to mock mode if actual API fails
            fallback_to_mock = True
            is_mock = True

    if is_mock:
        razorpay_order_id = f"pay_mock_ord_{order.order_number}"

    Payment.objects.update_or_create(
        order=order,
        defaults={
            'user': request.user,
            'payment_method': 'RAZORPAY',
            'razorpay_order_id': razorpay_order_id,
            'amount': order.grand_total,
            'status': 'PENDING',
        }
    )

    context = {
        'order': order,
        'razorpay_order_id': razorpay_order_id,
        'razorpay_key': key_id if not is_mock else "mock_key_id",
        'amount': amount_paise,
        'is_mock': is_mock,
        'fallback_to_mock': fallback_to_mock,
    }
    return render(request, 'payments/payment.html', context)


@login_required
def initiate_appointment_payment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)

    key_id = getattr(settings, 'RAZORPAY_KEY_ID', '')
    key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '')
    is_mock = not key_id or not key_secret or key_id.startswith('your_') or key_secret.startswith('your_')

    amount_paise = int(appointment.consultation_fee * 100)
    razorpay_order_id = None
    fallback_to_mock = False

    if not is_mock:
        try:
            client = razorpay.Client(auth=(key_id, key_secret))
            razorpay_order = client.order.create({
                'amount': amount_paise,
                'currency': 'INR',
                'receipt': f"APPT{appointment.id}",
                'payment_capture': 1,
            })
            razorpay_order_id = razorpay_order['id']
        except Exception:
            fallback_to_mock = True
            is_mock = True

    if is_mock:
        razorpay_order_id = f"pay_mock_appt_{appointment.id}_{random.randint(1000, 9999)}"

    Payment.objects.update_or_create(
        appointment=appointment,
        defaults={
            'user': request.user,
            'payment_method': 'RAZORPAY',
            'razorpay_order_id': razorpay_order_id,
            'amount': appointment.consultation_fee,
            'status': 'PENDING',
        }
    )

    context = {
        'appointment': appointment,
        'doctor': appointment.doctor,
        'razorpay_order_id': razorpay_order_id,
        'razorpay_key': key_id if not is_mock else "mock_key_id",
        'amount': amount_paise,
        'is_mock': is_mock,
        'fallback_to_mock': fallback_to_mock,
    }
    return render(request, 'payments/appointment_payment.html', context)


@csrf_exempt
def payment_callback(request):
    if request.method == 'POST':
        data = request.POST
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')

        try:
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
            
            # Check if this is a mock payment
            is_mock_payment = razorpay_order_id.startswith('pay_mock_') if razorpay_order_id else False

            signature_verified = False
            if is_mock_payment:
                signature_verified = True
            else:
                try:
                    # Verify signature
                    msg = f"{razorpay_order_id}|{razorpay_payment_id}"
                    secret = settings.RAZORPAY_KEY_SECRET.encode()
                    generated_signature = hmac.new(secret, msg.encode(), hashlib.sha256).hexdigest()
                    if generated_signature == razorpay_signature:
                        signature_verified = True
                except Exception:
                    signature_verified = False

            if signature_verified:
                payment.status = 'SUCCESS'
                payment.razorpay_payment_id = razorpay_payment_id or f"pay_mock_tx_{random.randint(100000, 999999)}"
                payment.razorpay_signature = razorpay_signature or "mock_signature"
                payment.save()

                if payment.appointment:
                    appointment = payment.appointment
                    appointment.payment_status = 'PAID'
                    appointment.payment_method = 'ONLINE'
                    appointment.status = 'APPROVED'
                    appointment.save()

                    create_notification(
                        payment.user,
                        f'Payment of ₹{appointment.consultation_fee} confirmed for Dr. {appointment.doctor.get_full_name()}!',
                        'PAYMENT'
                    )
                    create_notification(
                        appointment.doctor,
                        f'Consultation fee of ₹{appointment.consultation_fee} paid by {payment.user.get_full_name()} (Appointment #{appointment.id}).',
                        'PAYMENT'
                    )

                    # Send confirmation emails
                    send_appointment_booked_email(payment.user, appointment.doctor, appointment)
                    send_appointment_notification_to_doctor(appointment.doctor, payment.user, appointment)

                    messages.success(request, f'Payment of ₹{appointment.consultation_fee} successful! Your appointment with Dr. {appointment.doctor.get_full_name()} is confirmed.')
                    return redirect('appointments:list')

                elif payment.order:
                    order = payment.order
                    order.status = 'CONFIRMED'
                    order.save()

                    if not OrderTracking.objects.filter(order=order, status='CONFIRMED').exists():
                        OrderTracking.objects.create(
                            order=order,
                            status='CONFIRMED',
                            message='Payment confirmed. Order is being processed.'
                        )
                    create_notification(payment.user, f'Payment successful for Order #{order.order_number}', 'PAYMENT')

                    # Send order confirmation email
                    send_order_placed_email(payment.user, order)

                    return redirect('orders:confirmation', order_id=order.id)
            else:
                payment.status = 'FAILED'
                payment.save()
                messages.error(request, 'Payment failed. Please try again.')
                if payment.appointment:
                    return redirect('appointments:list')
                elif payment.order:
                    return redirect('orders:list')
        except Payment.DoesNotExist:
            pass

    return redirect('dashboard:home')