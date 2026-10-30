from django.db import models
from cloudinary.models import CloudinaryField

class HeroSlide(models.Model):
    image = CloudinaryField(
        'hero_image', 
        help_text="Upload the full poster image."
    )
    image_alt_text = models.CharField(
        max_length=200, 
        help_text="Describe the image for SEO and Accessibility."
    )
    link_url = models.CharField(
        max_length=200, 
        help_text="Where should clicking the poster take the user?"
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="0 comes first.")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Slide {self.order} - {self.image_alt_text}"
    
class PromoBanner(models.Model):
    title = models.CharField(max_length=100, help_text="For internal reference only (e.g., 'Oppo Special Offer')")
    image = CloudinaryField('promo_image', help_text="Upload the poster image (Portrait/Square ratio is best)")
    link_url = models.CharField(max_length=200, help_text="Where should this banner go? (e.g., /products/?category=phones)")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Order of appearance")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title    