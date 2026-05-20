from django.shortcuts import render
from .models import Product


def home(request):

    products = Product.objects.all()

    return render(request, 'products/home.html', {
        'products': products
    })


def about(request):

    return render(request, 'products/about.html')


def product_list(request):

    products = Product.objects.all()

    return render(request, 'products/product_list.html', {
        'products': products
    })


def category(request):

    return render(request, 'products/category.html')


def contact(request):

    return render(request, 'products/contact.html')