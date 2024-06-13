from django.shortcuts import render, get_object_or_404, redirect
from .models import Products, ProductsPage, ProductSize
from cart.models import Cart

def product_list(request):
    products = Products.objects.all()
    return render(request, 'products/product_list.html', {'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    product_page, created = ProductsPage.objects.get_or_create(product=product, defaults={'title': product.title, 'shipping': 'Default shipping information'})
    return render(request, 'products/product_detail.html', {'product': product, 'product_page': product_page})

def add_to_cart(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    size_id = request.POST.get('size')
    size = get_object_or_404(ProductSize, id=size_id)
    if request.user.is_authenticated:
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product, size=size)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
    else:
        cart = request.session.get('cart', {})
        if str(product_id) not in cart:
            cart[str(product_id)] = {'quantity': 0, 'size_id': size_id}
        cart[str(product_id)]['quantity'] += 1
        request.session['cart'] = cart
    return redirect('cart:cart')

def checkout(request):
    if request.method == 'POST':
        request.session['cart'] = {}
        return redirect('products:product_list')
    return render(request, 'products/checkout.html')
