from django.db.models import Sum
from .models import Announcement, Cart, Wishlist


def announcements_context(request):
    announcements = Announcement.objects.filter(is_active=True)
    return {
        'announcements': announcements
    }


def cart_wishlist_context(request):
    cart_count = 0
    wishlist_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.filter(user=request.user).first()
            if cart:
                cart_count = cart.items.aggregate(Sum('quantity'))['quantity__sum'] or 0
        except Exception:
            pass
            
        try:
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
        except Exception:
            pass
            
    return {
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
    }
