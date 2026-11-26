from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .forms import (
    PatientRegistrationForm, CustomLoginForm,
    UserProfileForm, PatientProfileForm, DoctorProfileForm, AddressForm
)
from .models import DoctorProfile, PatientProfile, Address
from .decorators import patient_required, doctor_required
from .otp_utils import generate_otp, store_otp_in_session, verify_otp_from_session, send_otp_email
from notifications.email_service import send_welcome_email

User = get_user_model()


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_verified = False
            user.save()
            PatientProfile.objects.get_or_create(user=user)

            # Generate OTP & store in session
            otp = generate_otp(6)
            store_otp_in_session(request, otp, purpose='registration')
            request.session['otp_user_id'] = user.id
            request.session['otp_email'] = user.email

            # Dispatch OTP email
            send_otp_email(user.email, otp, purpose='registration', user_name=user.first_name)

            if getattr(settings, 'DEBUG', True):
                messages.info(request, f"A 6-digit verification code has been sent to {user.email}. (Dev Hint: {otp})")
            else:
                messages.info(request, f"A 6-digit verification code has been sent to {user.email}.")

            return redirect('accounts:verify_otp')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PatientRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def verify_otp_view(request):
    if request.user.is_authenticated and getattr(request.user, 'is_verified', False):
        return redirect('dashboard:home')

    email = request.session.get('otp_email')
    user_id = request.session.get('otp_user_id')

    # If already logged in but unverified
    if not email and request.user.is_authenticated and not request.user.is_verified:
        email = request.user.email
        user_id = request.user.id
        request.session['otp_email'] = email
        request.session['otp_user_id'] = user_id

    if not email:
        messages.warning(request, 'No pending verification found. Please register or sign in.')
        return redirect('accounts:register')

    if request.method == 'POST':
        submitted_otp = request.POST.get('otp', '').strip()
        purpose = request.POST.get('purpose', 'registration')
        success, error_message = verify_otp_from_session(request, submitted_otp, purpose=purpose)

        if success:
            try:
                user = User.objects.get(id=user_id) if user_id else User.objects.get(email=email)
                user.is_verified = True
                user.save()

                request.session.pop('otp_user_id', None)
                request.session.pop('otp_email', None)

                login(request, user)
                send_welcome_email(user)
                messages.success(request, f'Email verified successfully! Welcome to MediCarePlus, {user.first_name or user.email}!')
                return redirect('dashboard:home')
            except User.DoesNotExist:
                messages.error(request, 'User account not found. Please register again.')
                return redirect('accounts:register')
        else:
            messages.error(request, error_message or 'Invalid or expired OTP code.')

    context = {
        'email': email,
        'purpose': 'registration',
    }
    return render(request, 'accounts/verify_otp.html', context)


def resend_otp_view(request):
    if request.method == 'POST':
        purpose = request.POST.get('purpose', 'registration')
        email = request.session.get('otp_email')
        user_id = request.session.get('otp_user_id')

        if not email and request.user.is_authenticated:
            email = request.user.email
            user_id = request.user.id

        if email:
            user = None
            if user_id:
                user = User.objects.filter(id=user_id).first()
            if not user:
                user = User.objects.filter(email=email).first()

            user_name = user.first_name if user else ''
            new_otp = generate_otp(6)
            store_otp_in_session(request, new_otp, purpose=purpose)
            send_otp_email(email, new_otp, purpose=purpose, user_name=user_name)

            if getattr(settings, 'DEBUG', True):
                messages.success(request, f"New OTP sent to {email}. (Dev Hint: {new_otp})")
            else:
                messages.success(request, f"A new 6-digit OTP has been sent to {email}.")
        else:
            messages.error(request, 'Verification session expired. Please register again.')
            return redirect('accounts:register')

    return redirect('accounts:verify_otp')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                if user.role == 'PATIENT' and not user.is_verified:
                    otp = generate_otp(6)
                    store_otp_in_session(request, otp, purpose='registration')
                    request.session['otp_user_id'] = user.id
                    request.session['otp_email'] = user.email
                    send_otp_email(user.email, otp, purpose='registration', user_name=user.first_name)
                    if getattr(settings, 'DEBUG', True):
                        messages.info(request, f"Please verify your email to log in. OTP sent. (Dev Hint: {otp})")
                    else:
                        messages.info(request, f"Please verify your email to log in. A verification code has been sent to {user.email}.")
                    return redirect('accounts:verify_otp')

                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.email}!')
                next_url = request.GET.get('next', 'dashboard:home')
                return redirect(next_url)
        messages.error(request, 'Invalid email or password.')
    else:
        form = CustomLoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def doctor_login_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'DOCTOR':
            return redirect('appointments:doctor_appointments')
        else:
            return redirect('dashboard:home')
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                if user.role != 'DOCTOR':
                    messages.error(request, 'Access denied. This login portal is reserved for Doctor accounts only.')
                    return render(request, 'accounts/doctor_login.html', {'form': form})
                login(request, user)
                messages.success(request, f'Welcome back, Dr. {user.last_name or user.first_name or user.email}!')
                next_url = request.GET.get('next', 'appointments:doctor_appointments')
                return redirect(next_url)
        messages.error(request, 'Invalid email or password.')
    else:
        form = CustomLoginForm()
    return render(request, 'accounts/doctor_login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    user = request.user
    user_form = UserProfileForm(instance=user)
    profile_form = None

    if user.is_patient:
        profile, _ = PatientProfile.objects.get_or_create(user=user)
        profile_form = PatientProfileForm(instance=profile)
    elif user.is_doctor:
        profile, _ = DoctorProfile.objects.get_or_create(user=user)
        profile_form = DoctorProfileForm(instance=profile)

    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=user)
        if user.is_patient:
            profile, _ = PatientProfile.objects.get_or_create(user=user)
            profile_form = PatientProfileForm(request.POST, instance=profile)
        elif user.is_doctor:
            profile, _ = DoctorProfile.objects.get_or_create(user=user)
            profile_form = DoctorProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and (profile_form is None or profile_form.is_valid()):
            user_form.save()
            if profile_form:
                profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')

    addresses = Address.objects.filter(user=user)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'addresses': addresses,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            if address.is_default:
                Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
            address.save()
            messages.success(request, 'Address added successfully!')
            return redirect('accounts:profile')
    else:
        form = AddressForm()
    return render(request, 'accounts/add_address.html', {'form': form})


@login_required
def delete_address(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    messages.success(request, 'Address deleted.')
    return redirect('accounts:profile')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = f"{request.scheme}://{request.get_host()}/accounts/reset-password/{uid}/{token}/"
            subject = 'MediCarePlus - Password Reset'
            message = render_to_string('accounts/password_reset_email.html', {
                'user': user,
                'reset_link': reset_link,
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
            messages.success(request, 'Password reset link sent to your email.')
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email.')
    return render(request, 'accounts/forgot_password.html')


def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Password reset successfully. Please login.')
                return redirect('accounts:login')
        else:
            form = SetPasswordForm(user)
        return render(request, 'accounts/reset_password.html', {'form': form})
    else:
        messages.error(request, 'Invalid or expired reset link.')
        return redirect('accounts:forgot_password')