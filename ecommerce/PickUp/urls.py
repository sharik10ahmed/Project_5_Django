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
    path('profile/', profile, name='profile'),
    path('orders/', orders, name='orders'),
    path('privacy-policy/', privacy_policy, name='privacy_policy'),
    path('refund-policy/', refund_policy, name='refund_policy'),
    path('shipping-policy/', shipping_policy, name='shipping_policy'),
    path('terms-and-conditions/', terms_and_conditions, name='terms_and_conditions'),
    path('our-mission/', our_mission, name='our_mission'),
    path('our-vision/', our_vision, name='our_vision'),

]