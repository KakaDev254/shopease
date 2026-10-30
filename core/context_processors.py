from products.models import Category

def global_context(request):
    cart = request.session.get('cart', {})
    wishlist = request.session.get('wishlist', {})
    return {
        'nav_categories': Category.objects.filter(parent=None)[:15],
        'cart_count': sum(cart.values()) if cart else 0,
        'wishlist_count': len(wishlist) if wishlist else 0,
    }