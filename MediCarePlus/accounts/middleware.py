from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages


class RoleBasedAccessMiddleware:
    """Middleware to protect routes based on user roles."""

    DOCTOR_PATHS = ['/appointments/doctor/', '/dashboard/doctor/']
    ADMIN_PATHS = ['/dashboard/admin/']
    PATIENT_PATHS = ['/cart/', '/orders/', '/prescriptions/upload/']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            path = request.path

            for p in self.DOCTOR_PATHS:
                if path.startswith(p) and request.user.role != 'DOCTOR':
                    messages.error(request, 'Doctor access only.')
                    return redirect('/')

            for p in self.ADMIN_PATHS:
                if path.startswith(p) and request.user.role != 'ADMIN':
                    messages.error(request, 'Admin access only.')
                    return redirect('/')

        response = self.get_response(request)
        return response