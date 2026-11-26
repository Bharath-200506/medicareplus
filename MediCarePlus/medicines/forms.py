from django import forms
from .models import Medicine

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = [
            'name', 'category', 'description', 'price', 
            'discount', 'stock', 'manufacturer', 'expiry_date', 
            'image', 'prescription_required', 'is_featured'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Paracetamol 500mg'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the medicine benefits, usage, side effects...'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100, 'step': '0.1'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Cipla Ltd'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'prescription_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
