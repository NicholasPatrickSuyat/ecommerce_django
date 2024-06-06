from django.shortcuts import render, get_object_or_404,redirect
from .models import Products, ProductsPage

def product_list(request):
    products = Products.objects.all()
    return render(request, 'products/product_list.html', {'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    product_page, created = ProductsPage.objects.get_or_create(product=product, defaults={'title': product.title, 'shipping': 'Default shipping information'})
    return render(request, 'products/product_detail.html', {'product': product, 'product_page': product_page})

def add_to_cart(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    cart = request.session.get('cart', {})
    cart[product_id] = cart.get(product_id, 0) + 1
    request.session['cart'] = cart
    return redirect('products:product_list')

def checkout(request):
    if request.method == 'POST':
        request.session['cart'] = {}  # Clear the cart after checkout
        return redirect('products:product_list')
    return render(request, 'products/checkout.html')
