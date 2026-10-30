from django.contrib import admin
from .models import HeroSlide, PromoBanner

@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    # 1. Fields to show in the table columns
    list_display = ('image_alt_text', 'order', 'is_active', 'link_url')
    
    # 2. Fields that can be edited directly in the table rows
    list_editable = ('order', 'is_active')
    
    # 3. The field that acts as the clickable link to edit the slide
    list_display_links = ('image_alt_text',)
    
    # 4. Sidebar filters
    list_filter = ('is_active',)
    
    # 5. Search bar functionality
    search_fields = ('image_alt_text', 'link_url')
    
@admin.register(PromoBanner)
class PromoBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_display_links = ('title',)
    list_filter = ('is_active',)    