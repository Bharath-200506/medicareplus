from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
from medicines.models import Medicine

User = get_user_model()

RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]


class MedicineReview(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medicine_reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reviews_medicine_review'
        unique_together = ('medicine', 'user')

    def __str__(self):
        return f"{self.user.email} - {self.medicine.name} ({self.rating}★)"


class DoctorReview(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_reviews')
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_doctor_reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reviews_doctor_review'
        unique_together = ('doctor', 'patient')

    def __str__(self):
        return f"{self.patient.email} reviewed Dr. {self.doctor.get_full_name()} ({self.rating}★)"