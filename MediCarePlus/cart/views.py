from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Cart, CartItem
from medicines.models import Medicine


@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.filter(saved_for_later=False).select_related('medicine')
    saved_items = cart.items.filter(saved_for_later=True).select_related('medicine')
    context = {
        'cart': cart,
        'items': items,
        'saved_items': saved_items,
    }
    return render(request, 'cart/cart.html', context)


@login_required
def add_to_cart(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk, is_active=True)
    quantity = int(request.POST.get('quantity', 1))

    if quantity > medicine.stock:
        messages.error(request, f'Only {medicine.stock} units available.')
        return redirect('medicines:detail', pk=pk)

    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        medicine=medicine,
        defaults={'quantity': quantity}
    )
    if not created:
        item.quantity = min(item.quantity + quantity, medicine.stock)
        item.saved_for_later = False
        item.save()

    messages.success(request, f'{medicine.name} added to cart!')
    return redirect('cart:cart')


@login_required
def remove_from_cart(request, pk):
    item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    item.delete()
    messages.info(request, 'Item removed from cart.')
    return redirect('cart:cart')


@login_required
def update_cart(request, pk):
    item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0 and quantity <= item.medicine.stock:
        item.quantity = quantity
        item.save()
    elif quantity <= 0:
        item.delete()
    return redirect('cart:cart')


@login_required
def save_for_later(request, pk):
    item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    item.saved_for_later = True
    item.save()
    messages.info(request, 'Item saved for later.')
    return redirect('cart:cart')


@login_required
def move_to_cart(request, pk):
    item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    item.saved_for_later = False
    item.save()
    messages.success(request, 'Item moved to cart.')
    return redirect('cart:cart')