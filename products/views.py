from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Min, Max
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.template.loader import render_to_string

from .models import Product, Category, Brand
from decimal import Decimal


# ------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------
def _filtered_products(request):
    """
    Build a queryset based on sidebar filters + sorting + search.
    Returns (queryset, filter_context).
    """
    qs = Product.objects.select_related('category', 'brand').filter(in_stock=True)

    # ---------- Search ----------
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(brand__name__icontains=q) |
            Q(category__name__icontains=q)
        )

    # ---------- Category filter ----------
    category_slug = request.GET.get('category')
    active_category = None
    if category_slug:
        active_category = Category.objects.filter(slug=category_slug).first()
        if active_category:
            # include products in subcategories too
            sub_ids = active_category.subcategories.values_list('id', flat=True)
            qs = qs.filter(Q(category=active_category) | Q(category_id__in=sub_ids))

    # ---------- Brand filter (multiple) ----------
    brand_slugs = request.GET.getlist('brand')
    if brand_slugs:
        qs = qs.filter(brand__slug__in=brand_slugs)

    # ---------- Price filter ----------
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        qs = qs.filter(price__gte=Decimal(min_price))
    if max_price:
        qs = qs.filter(price__lte=Decimal(max_price))

    # ---------- In-stock ----------
    if request.GET.get('in_stock') == '1':
        qs = qs.filter(in_stock=True)

    # ---------- Sorting ----------
    sort = request.GET.get('sort', 'popular')
    if sort == 'price_asc':
        qs = qs.order_by('price')
    elif sort == 'price_desc':
        qs = qs.order_by('-price')
    elif sort == 'newest':
        qs = qs.order_by('-created_at')
    else:  # popular
        qs = qs.order_by('-created_at')

    ctx = {
        'q': q,
        'active_category': active_category,
        'selected_brands': brand_slugs,
        'min_price': min_price or '',
        'max_price': max_price or '',
        'in_stock_only': request.GET.get('in_stock') == '1',
        'sort': sort,
    }
    return qs, ctx


# ------------------------------------------------------------------
# CATALOG
# ------------------------------------------------------------------
def catalog(request):
    qs, ctx = _filtered_products(request)

    price_range = Product.objects.aggregate(
        lo=Min('price'), hi=Max('price')
    )
    ctx.update({
        'products': qs,
        'product_count': qs.count(),
        'brands': Brand.objects.all(),
        'categories': Category.objects.filter(parent=None),
        'price_lo': int(price_range['lo'] or 0),
        'price_hi': int(price_range['hi'] or 200000),
    })
    return render(request, 'products/catalog.html', ctx)


# ------------------------------------------------------------------
# PRODUCT DETAIL
# ------------------------------------------------------------------
def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('category', 'brand'),
        slug=slug
    )
    related = (
        Product.objects
        .filter(category=product.category, in_stock=True)
        .exclude(pk=product.pk)[:8]
    )
    return render(request, 'products/product_detail.html', {
        'product': product,
        'related': related,
    })


# ------------------------------------------------------------------
# LIVE SEARCH (AJAX)
# ------------------------------------------------------------------
@require_GET
def live_search(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})

    results = (
        Product.objects
        .filter(in_stock=True)
        .filter(Q(name__icontains=q) | Q(brand__name__icontains=q))
        .select_related('brand')[:8]
    )
    data = [{
        'name': p.name,
        'slug': p.slug,
        'price': f'{p.price:,.0f}',
        'image': p.image.url if p.image else '',
        'brand': p.brand.name if p.brand else '',
    } for p in results]
    return JsonResponse({'results': data})


# ------------------------------------------------------------------
# CART ACTIONS (session-based, no login needed)
# ------------------------------------------------------------------
@require_POST
def cart_add(request):
    from django.conf import settings
    slug = request.POST.get('slug')
    qty = int(request.POST.get('qty', 1))
    product = get_object_or_404(Product, slug=slug)

    cart = request.session.get(settings.CART_SESSION_ID, {})
    key = str(product.id)
    cart[key] = cart.get(key, 0) + qty
    request.session[settings.CART_SESSION_ID] = cart

    return JsonResponse({
        'ok': True,
        'cart_count': sum(cart.values()),
        'item': {'name': product.name, 'qty': cart[key]},
    })


@require_POST
def cart_update(request):
    from django.conf import settings
    slug = request.POST.get('slug')
    qty = int(request.POST.get('qty', 1))
    product = get_object_or_404(Product, slug=slug)

    cart = request.session.get(settings.CART_SESSION_ID, {})
    key = str(product.id)
    if qty <= 0:
        cart.pop(key, None)
    else:
        cart[key] = qty
    request.session[settings.CART_SESSION_ID] = cart

    # return updated subtotal for drawer
    products = Product.objects.filter(id__in=cart.keys())
    subtotal = sum(p.price * cart[str(p.id)] for p in products)

    return JsonResponse({
        'ok': True,
        'cart_count': sum(cart.values()),
        'subtotal': f'{subtotal:,.0f}',
        'removed': qty <= 0,
    })


@require_GET
def cart_drawer(request):
    """Renders the HTML of the cart drawer (fetched by JS)."""
    from django.conf import settings
    cart = request.session.get(settings.CART_SESSION_ID, {})
    items = []
    subtotal = Decimal('0')
    for pid, qty in cart.items():
        p = Product.objects.filter(id=pid).first()
        if not p:
            continue
        line = p.price * qty
        subtotal += line
        items.append({'product': p, 'qty': qty, 'line_total': line})

    return render(request, 'partials/cart_drawer_items.html', {
        'items': items,
        'subtotal': subtotal,
        'cart_count': sum(cart.values()),
    })


# ------------------------------------------------------------------
# WISHLIST ACTIONS
# ------------------------------------------------------------------
@require_POST
def wishlist_toggle(request):
    from django.conf import settings
    slug = request.POST.get('slug')
    product = get_object_or_404(Product, slug=slug)

    wishlist = request.session.get(settings.WISHLIST_SESSION_ID, {})
    key = str(product.id)
    if key in wishlist:
        del wishlist[key]
        active = False
    else:
        wishlist[key] = True
        active = True
    request.session[settings.WISHLIST_SESSION_ID] = wishlist

    return JsonResponse({
        'ok': True,
        'active': active,
        'wishlist_count': len(wishlist),
    })


@require_GET
def wishlist_drawer(request):
    from django.conf import settings
    wishlist = request.session.get(settings.WISHLIST_SESSION_ID, {})
    products = Product.objects.filter(id__in=wishlist.keys())
    return render(request, 'partials/wishlist_drawer_items.html', {
        'items': products,
        'wishlist_count': len(wishlist),
    })