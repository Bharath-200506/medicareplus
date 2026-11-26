from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
from orders.models import Order

User = get_user_model()


class Payment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    )

    METHOD_CHOICES = (
        ('RAZORPAY', 'Razorpay'),
        ('COD', 'Cash on Delivery'),
        ('PAY_AT_CLINIC', 'Pay at Clinic'),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment', null=True, blank=True)
    appointment = models.OneToOneField('appointments.Appointment', on_delete=models.CASCADE, related_name='payment', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    razorpay_order_id = models.CharField(max_length=200, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=200, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=500, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments_payment'

    def __str__(self):
        ref = f"Order #{self.order.order_number}" if self.order else (f"Appointment #{self.appointment.id}" if self.appointment else f"Payment #{self.id}")
        return f"Payment for {ref} - {self.status}"