from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
from medicines.models import Medicine

User = get_user_model()


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cart_cart'

    def __str__(self):
        return f"Cart of {self.user.email}"

    @property
    def total_items(self):
        return self.items.count()

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    saved_for_later = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cart_cart_item'
        unique_together = ('cart', 'medicine')

    def __str__(self):
        return f"{self.quantity} x {self.medicine.name}"

    @property
    def subtotal(self):
        return self.medicine.discounted_price * self.quantity