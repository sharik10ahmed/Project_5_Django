from django.urls import path
from .views import *


urlpatterns =[
    path('',home, name='home'),
    path('register/',register,name='register'),
    path('verify-otp/',verify_otp,name='verify_otp'),
    path('login/',login_view,name='login'),
    path('logout/',logout_view,name='logout'),
    path('product/', product, name='product'),
    path('category/', category, name='category'),
    path('gallery/', gallery, name='gallery'),
    path('about/', about, name='about'),
    path('wishlist/', wishlist, name='wishlist'),
    path('cart/', cart, name='cart'),
    path('checkout/', checkout, name='checkout'),
    path('profile/', profile, name='profile'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('orders/', orders, name='orders'),
    path('orders/cancel/<int:order_id>/', cancel_order, name='cancel_order'),
    path('privacy-policy/', privacy_policy, name='privacy_policy'),
    path('refund-policy/', refund_policy, name='refund_policy'),
    path('shipping-policy/', shipping_policy, name='shipping_policy'),
    path('terms-and-conditions/', terms_and_conditions, name='terms_and_conditions'),
    path('our-mission/', our_mission, name='our_mission'),
    path('our-vision/', our_vision, name='our_vision'),
    path('contact/', contact, name='contact'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', update_cart_quantity, name='update_cart_quantity'),
    path('wishlist/add/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:wishlist_id>/', remove_from_wishlist, name='remove_from_wishlist'),

]