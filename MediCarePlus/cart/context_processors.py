from .models import Cart


def cart_count(request):
    count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            count = cart.items.filter(saved_for_later=False).count()
        except Cart.DoesNotExist:
            pass
    return {'cart_count': count}