from django.contrib import admin
from .models import Category, Brand, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('parent',)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'price', 'in_stock')
    list_filter = ('category', 'brand', 'in_stock')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)