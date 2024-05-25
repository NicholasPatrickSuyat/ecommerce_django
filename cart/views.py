from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .models import Cart
from products.models import Products
from user.models import Order
from .forms import GuestCheckoutForm, CheckoutForm
import os

def cart_view(request):
    cart_items = []
    total_price = 0

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        total_price = sum(item.product.price * item.quantity for item in cart_items)
    else:
        cart = request.session.get('cart', {})
        for product_id, quantity in cart.items():
            product = get_object_or_404(Products, id=product_id)
            total_price += product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total_price': product.price * quantity,
            })

    return render(request, 'cart/cart.html', {'cart_items': cart_items, 'total_price': total_price})

def add_to_cart(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    if request.user.is_authenticated:
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
    else:
        cart = request.session.get('cart', {})
        cart[str(product_id)] = cart.get(str(product_id), 0) + 1
        request.session['cart'] = cart
    return redirect('cart:cart')

def remove_from_cart(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    if request.user.is_authenticated:
        cart_item = get_object_or_404(Cart, user=request.user, product=product)
        cart_item.delete()
    else:
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            del cart[str(product_id)]
            request.session['cart'] = cart
    return redirect('cart:cart')

def update_cart(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    quantity = int(request.POST.get('quantity'))
    if request.user.is_authenticated:
        cart_item = get_object_or_404(Cart, user=request.user, product=product)
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart = request.session.get('cart', {})
        cart[str(product_id)] = quantity
        request.session['cart'] = cart
    return redirect('cart:cart')

def checkout_view(request):
    if request.user.is_authenticated:
        return logged_in_checkout_view(request)
    else:
        return guest_checkout_view(request)

@login_required
def logged_in_checkout_view(request):
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            shipping_address = form.cleaned_data['address']
            orders = Order.objects.filter(user=request.user, shipping_address='')
            for order in orders:
                order.shipping_address = shipping_address
                order.save()
            return redirect('user:order_history')
    else:
        form = CheckoutForm()
    return render(request, 'cart/checkout.html', {'form': form, 'user': request.user})

def guest_checkout_view(request):
    if request.method == 'POST':
        form = GuestCheckoutForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            shipping_address = form.cleaned_data['shipping_address']
            cart = request.session.get('cart', {})
            for product_id, quantity in cart.items():
                product = get_object_or_404(Products, id=product_id)
                order = Order.objects.create(
                    guest_email=email,
                    product=product,
                    quantity=quantity,
                    shipping_address=shipping_address
                )
                send_mail(
                    f'Order Confirmation for {product.title}',
                    f'Thank you for your purchase of {product.title}.\n\nShipping Address: {shipping_address}',
                    os.environ.get('EMAIL_HOST_USER'),  # This should match EMAIL_HOST_USER
                    [email]
                )
            request.session['cart'] = {}
            return redirect('cart:guest_checkout_success')
    else:
        form = GuestCheckoutForm()
    return render(request, 'cart/guest_checkout.html', {'form': form})

def guest_checkout_success_view(request):
    return render(request, 'cart/guest_checkout_success.html')

def payment_success(request):
    return render(request, 'cart/payment_success.html')

def payment_cancel(request):
    return render(request, 'cart/payment_cancel.html')
