from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from .models import Medicine, MedicineCategory, Wishlist
from .forms import MedicineForm
from accounts.decorators import role_required


def home(request):
    featured_medicines = Medicine.objects.filter(is_featured=True, is_active=True)[:8]
    categories = MedicineCategory.objects.all()[:6]
    context = {
        'featured_medicines': featured_medicines,
        'categories': categories,
    }
    return render(request, 'home.html', context)


def medicine_list(request):
    medicines = Medicine.objects.filter(is_active=True)
    categories = MedicineCategory.objects.all()

    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort = request.GET.get('sort', '')
    prescription = request.GET.get('prescription', '')

    if query:
        medicines = medicines.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(manufacturer__icontains=query)
        )

    if category_id:
        medicines = medicines.filter(category_id=category_id)

    if min_price:
        medicines = medicines.filter(price__gte=min_price)

    if max_price:
        medicines = medicines.filter(price__lte=max_price)

    if prescription == 'yes':
        medicines = medicines.filter(prescription_required=True)
    elif prescription == 'no':
        medicines = medicines.filter(prescription_required=False)

    if sort == 'price_asc':
        medicines = medicines.order_by('price')
    elif sort == 'price_desc':
        medicines = medicines.order_by('-price')
    elif sort == 'name':
        medicines = medicines.order_by('name')
    elif sort == 'newest':
        medicines = medicines.order_by('-created_at')
    else:
        medicines = medicines.order_by('-created_at')

    paginator = Paginator(medicines, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = Wishlist.objects.filter(user=request.user).values_list('medicine_id', flat=True)

    context = {
        'medicines': page_obj,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'wishlist_ids': list(wishlist_ids),
    }
    return render(request, 'medicines/list.html', context)


def medicine_detail(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk, is_active=True)
    similar = Medicine.objects.filter(
        category=medicine.category, is_active=True
    ).exclude(pk=pk)[:4]
    reviews = medicine.reviews.all().order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, medicine=medicine).exists()

    context = {
        'medicine': medicine,
        'similar': similar,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'in_wishlist': in_wishlist,
    }
    return render(request, 'medicines/detail.html', context)


@login_required
def toggle_wishlist(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    obj, created = Wishlist.objects.get_or_create(user=request.user, medicine=medicine)
    if not created:
        obj.delete()
        messages.info(request, f'{medicine.name} removed from wishlist.')
    else:
        messages.success(request, f'{medicine.name} added to wishlist.')
    return redirect(request.META.get('HTTP_REFERER', 'medicines:list'))


@login_required
def wishlist_view(request):
    wishlist = Wishlist.objects.filter(user=request.user).select_related('medicine')
    return render(request, 'medicines/wishlist.html', {'wishlist': wishlist})


@login_required
@role_required('DOCTOR', 'ADMIN')
def add_medicine(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES)
        if form.is_valid():
            medicine = form.save()
            messages.success(request, f'Medicine "{medicine.name}" has been added successfully.')
            return redirect('medicines:detail', pk=medicine.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = MedicineForm()
    return render(request, 'medicines/add_medicine.html', {'form': form})