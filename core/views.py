from django.shortcuts import render
from products.models import Product, Category, Brand
from .models import HeroSlide, PromoBanner

def home(request):
    # Get the Phones & Tablets category
    phones_category = Category.objects.filter(slug='phones-tablets').first()
    
    # Get 10 products from that category
    phones_products = []
    if phones_category:
        phones_products = Product.objects.filter(
            category=phones_category, 
            in_stock=True
        ).order_by('-created_at')[:10]

    return render(request, 'core/home.html', {
        'trending_products': Product.objects.filter(in_stock=True).order_by('-created_at')[:10],
        'phones_products': phones_products,
        'phones_category': phones_category,
        'brands': Brand.objects.all()[:10],
        'hero_slides': HeroSlide.objects.filter(is_active=True),
        'promo_banners': PromoBanner.objects.filter(is_active=True),
    })