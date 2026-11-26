"""
OTP utility functions for MediCarePlus.
Handles OTP generation, session storage, and email dispatch for both
registration verification and login 2FA.
"""
import random
import time
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def generate_otp(length=6):
    """Generate a random numeric OTP of the given length."""
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


def store_otp_in_session(request, otp, purpose='registration'):
    """
    Store OTP and metadata in the session.
    purpose: 'registration' | 'login'
    """
    request.session[f'otp_{purpose}'] = otp
    request.session[f'otp_{purpose}_created'] = time.time()
    request.session[f'otp_{purpose}_attempts'] = 0


def verify_otp_from_session(request, submitted_otp, purpose='registration', max_age=300, max_attempts=5):
    """
    Verify submitted OTP against session-stored OTP.
    Returns (success: bool, error_message: str|None).
    max_age: OTP validity in seconds (default 5 minutes).
    max_attempts: max wrong attempts before lockout.
    """
    stored_otp = request.session.get(f'otp_{purpose}')
    created_at = request.session.get(f'otp_{purpose}_created', 0)
    attempts = request.session.get(f'otp_{purpose}_attempts', 0)

    if not stored_otp:
        return False, 'No OTP found. Please request a new one.'

    if attempts >= max_attempts:
        clear_otp_from_session(request, purpose)
        return False, 'Too many failed attempts. Please request a new OTP.'

    if time.time() - created_at > max_age:
        clear_otp_from_session(request, purpose)
        return False, 'OTP has expired. Please request a new one.'

    if str(submitted_otp).strip() != str(stored_otp).strip():
        request.session[f'otp_{purpose}_attempts'] = attempts + 1
        remaining = max_attempts - attempts - 1
        return False, f'Invalid OTP. {remaining} attempt(s) remaining.'

    # Success — clear OTP data
    clear_otp_from_session(request, purpose)
    return True, None


def clear_otp_from_session(request, purpose='registration'):
    """Remove OTP data from session."""
    for key in [f'otp_{purpose}', f'otp_{purpose}_created', f'otp_{purpose}_attempts']:
        request.session.pop(key, None)


def send_otp_email(email, otp, purpose='registration', user_name=''):
    """Send OTP email with a professional HTML template."""
    if purpose == 'registration':
        subject = 'MediCarePlus — Verify Your Email Address'
        heading = 'Email Verification'
        intro = f'Hi {user_name or "there"},\n\nThank you for registering with MediCarePlus! Please use the following OTP to verify your email address:'
    else:
        subject = 'MediCarePlus — Login Verification Code'
        heading = 'Login Verification'
        intro = f'Hi {user_name or "there"},\n\nA login attempt was detected on your MediCarePlus account. Please use the following OTP to complete your sign-in:'

    context = {
        'otp': otp,
        'heading': heading,
        'intro': intro,
        'purpose': purpose,
    }

    html_message = render_to_string('accounts/emails/otp_email.html', context)
    plain_message = strip_tags(html_message)

    try:
        print(f"\n{'='*55}")
        print(f"[OTP DISPATCH] To: {email} | OTP: {otp} | Purpose: {purpose}")
        print(f"{'='*55}\n")
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"[OTP WARNING] SMTP delivery failed: {e}. OTP remains valid: {otp}")

