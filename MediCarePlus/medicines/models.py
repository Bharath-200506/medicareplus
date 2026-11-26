from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class MedicineCategory(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'medicines_category'
        verbose_name_plural = 'Medicine Categories'

    def __str__(self):
        return self.name


class Medicine(models.Model):
    name = models.CharField(max_length=300)
    category = models.ForeignKey(
        MedicineCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='medicines'
    )
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    stock = models.PositiveIntegerField(default=0)
    manufacturer = models.CharField(max_length=300)
    expiry_date = models.DateField()
    image = models.ImageField(upload_to='medicines/', blank=True, null=True)
    prescription_required = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'medicines_medicine'

    def __str__(self):
        return self.name

    @property
    def discounted_price(self):
        if self.discount > 0:
            return self.price - (self.price * self.discount / 100)
        return self.price

    @property
    def is_in_stock(self):
        return self.stock > 0

    def get_image_url(self):
        if self.image:
            return self.image.url
        if self.category:
            cat_name = self.category.name.lower()
            if 'pain' in cat_name or 'analgesic' in cat_name:
                return '/static/images/analgesics.jpg'
            elif 'antibiotic' in cat_name:
                return '/static/images/antibiotics.jpg'
            elif 'cardio' in cat_name:
                return '/static/images/cardiovascular.jpg'
            elif 'diabet' in cat_name:
                return '/static/images/antidiabetics.jpg'
            elif 'respir' in cat_name or 'allerg' in cat_name:
                return '/static/images/respiratory.jpg'
            elif 'vitamin' in cat_name or 'supple' in cat_name:
                return '/static/images/vitamins.jpg'
            elif 'gastro' in cat_name or 'digest' in cat_name:
                return '/static/images/gastrointestinal.jpg'
            elif 'derm' in cat_name or 'skin' in cat_name:
                return '/static/images/dermatology.jpg'
        return '/static/images/medicine1.jpg'


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'medicines_wishlist'
        unique_together = ('user', 'medicine')

    def __str__(self):
        return f"{self.user.email} - {self.medicine.name}"