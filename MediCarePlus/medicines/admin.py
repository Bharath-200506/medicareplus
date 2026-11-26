from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Medicine, MedicineCategory, Wishlist


@admin.register(MedicineCategory)
class MedicineCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_featured', 'is_active', 'expiry_date')
    list_filter = ('category', 'is_featured', 'is_active', 'prescription_required')
    search_fields = ('name', 'manufacturer')
    list_editable = ('is_featured', 'is_active', 'stock')