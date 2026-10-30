from django.shortcuts import render
from products.models import Product, Category, Brand
from .models import HeroSlide, PromoBanner

def home(request):
    # Fetch the 10 most recent in-stock products
    trending = Product.objects.filter(in_stock=True).order_by('-created_at')[:10]
    
    return render(request, 'core/home.html', {
        'trending_products': trending,
        'brands': Brand.objects.all()[:10],
        'hero_slides': HeroSlide.objects.filter(is_active=True),
        'promo_banners': PromoBanner.objects.filter(is_active=True),
    })