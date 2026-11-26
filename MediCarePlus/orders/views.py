from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import random
from .models import Order, OrderItem, OrderTracking
from cart.models import Cart, CartItem
from accounts.models import Address
from notifications.utils import create_notification
from notifications.email_service import send_order_placed_email, send_order_status_email
from payments.models import Payment


@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    items = cart.items.filter(saved_for_later=False).select_related('medicine')

    if not items.exists():
        messages.error(request, 'Your cart is empty.')
        return redirect('cart:cart')

    addresses = Address.objects.filter(user=request.user)
    total = sum(i.subtotal for i in items)

    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        payment_method = request.POST.get('payment_method', 'COD')
        address = get_object_or_404(Address, id=address_id, user=request.user)

        # Create order
        order = Order.objects.create(
            user=request.user,
            order_number=f"MCP{request.user.id}{random.randint(10000, 99999)}",
            address=address,
            total_amount=total,
            status='PENDING',
        )

        # Create order items & reduce stock
        for item in items:
            OrderItem.objects.create(
                order=order,
                medicine=item.medicine,
                quantity=item.quantity,
                price=item.medicine.discounted_price,
            )
            item.medicine.stock -= item.quantity
            item.medicine.save()

        # Clear cart
        items.delete()

        # Create tracking
        OrderTracking.objects.create(
            order=order,
            status='PENDING',
            message='Your order has been placed successfully.'
        )

        # Notification
        create_notification(request.user, f'Order #{order.order_number} placed successfully!', 'ORDER')

        # Redirect to payment or confirmation
        if payment_method == 'RAZORPAY':
            return redirect('payments:initiate', order_id=order.id)
        else:
            # Cash on Delivery
            Payment.objects.update_or_create(
                order=order,
                defaults={
                    'user': request.user,
                    'payment_method': 'COD',
                    'amount': order.grand_total,
                    'status': 'PENDING',
                }
            )
            # Dispatch order confirmation email
            send_order_placed_email(request.user, order)
            messages.success(request, f'Order #{order.order_number} placed successfully! A confirmation email has been sent to {request.user.email}.')
            return redirect('orders:confirmation', order_id=order.id)

    context = {
        'items': items,
        'total': total,
        'addresses': addresses,
        'delivery_charge': 50,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/confirmation.html', {'order': order})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    tracking = order.tracking.all()
    return render(request, 'orders/order_detail.html', {'order': order, 'tracking': tracking})


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status in ['PENDING', 'CONFIRMED']:
        order.status = 'CANCELLED'
        order.save()
        OrderTracking.objects.create(
            order=order,
            status='CANCELLED',
            message='Order cancelled by customer.'
        )
        send_order_status_email(order.user, order, 'CANCELLED')
        messages.success(request, 'Order cancelled successfully.')
    else:
        messages.error(request, 'This order cannot be cancelled.')
    return redirect('orders:detail', order_id=order.id)