from django.db import models
from cloudinary.models import CloudinaryField

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    image = CloudinaryField('category_image', blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=100)
    logo = CloudinaryField('brand_logo', blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = CloudinaryField('product_image')
    in_stock = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name