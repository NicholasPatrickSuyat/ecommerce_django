from django.shortcuts import render, redirect, get_object_or_404
from .models import Products
from django.contrib.auth.decorators import login_required

# View to list products
def product_list(request):
    products = Products.objects.all()
    return render(request, 'products/product_list.html', {'products': products})


# View to add product to cart
@login_required
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart[product_id] = cart.get(product_id, 0) + 1
    request.session['cart'] = cart
    return redirect('products:product_list')

# View to checkout
@login_required
def checkout(request):
    if request.method == 'POST':
        # Implement your checkout logic here
        request.session['cart'] = {}  # Clear the cart after checkout
        return redirect('products:product_list')
    return render(request, 'products/checkout.html')
