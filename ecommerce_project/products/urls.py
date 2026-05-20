from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),

    path('about/', views.about, name='about'),

    path('products/', views.product_list, name='products'),

    path('category/', views.category, name='category'),

    path('contact/', views.contact, name='contact'),
]