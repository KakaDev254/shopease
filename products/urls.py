from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # pages
    path('', views.catalog, name='catalog'),
    path('p/<slug:slug>/', views.product_detail, name='detail'),

    # ajax
    path('api/live-search/', views.live_search, name='live_search'),
    path('api/cart/add/', views.cart_add, name='cart_add'),
    path('api/cart/update/', views.cart_update, name='cart_update'),
    path('api/cart/drawer/', views.cart_drawer, name='cart_drawer'),
    path('api/wishlist/toggle/', views.wishlist_toggle, name='wishlist_toggle'),
    path('api/wishlist/drawer/', views.wishlist_drawer, name='wishlist_drawer'),
]