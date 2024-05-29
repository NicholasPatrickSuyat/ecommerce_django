from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from .models import Cart
from products.models import Products
from user.models import Order
from .forms import GuestCheckoutForm, CheckoutForm
from paypal.standard.forms import PayPalPaymentsForm
import os
from decimal import Decimal

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
            cart_items = Cart.objects.filter(user=request.user)
            total_price = sum(item.product.price * item.quantity for item in cart_items)

            # Create an order for each cart item and store the order ID in the session
            for item in cart_items:
                order = Order.objects.create(
                    user=request.user,
                    product=item.product,
                    quantity=item.quantity,
                    shipping_address=shipping_address
                )
                request.session['order_id'] = order.id

                # Send order confirmation email to the user
                send_mail(
                    f'Order Confirmation for {item.product.title}',
                    f'Thank you for your purchase of {item.product.title}.\n\nShipping Address: {shipping_address}',
                    settings.EMAIL_HOST_USER,
                    [request.user.email]
                )

                # Send order notification email to the seller
                send_mail(
                    f'New Order for {item.product.title}',
                    f'A new order has been placed for {item.product.title}.\n\nQuantity: {item.quantity}\n\nShipping Address: {shipping_address}\n\nUser: {request.user.username} ({request.user.email})',
                    settings.EMAIL_HOST_USER,
                    [settings.SELLER_EMAIL]
                )
            cart_items.delete()

            # Redirect to PayPal for payment
            return_url = request.build_absolute_uri(reverse('cart:payment_done'))
            cancel_url = request.build_absolute_uri(reverse('cart:payment_canceled'))
            paypal_dict = {
                'business': settings.PAYPAL_RECEIVER_EMAIL,
                'amount': '%.2f' % total_price,
                'item_name': 'Order {}'.format(request.user.username),
                'invoice': str(order.id),
                'currency_code': 'USD',
                'notify_url': request.build_absolute_uri(reverse('paypal-ipn')),
                'return_url': return_url,
                'cancel_return': cancel_url,
            }

            form = PayPalPaymentsForm(initial=paypal_dict)
            return render(request, 'cart/process_payment.html', {'form': form, 'total_price': total_price})

    else:
        form = CheckoutForm()
    return render(request, 'cart/checkout.html', {'form': form, 'user': request.user})

def guest_checkout_view(request):
    if request.method == 'POST':
        form = GuestCheckoutForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            shipping_address = form.cleaned_data['address']
            cart = request.session.get('cart', {})
            total_price = sum(get_object_or_404(Products, id=product_id).price * quantity for product_id, quantity in cart.items())
            
            # Create an order for each cart item and store the order ID in the session
            for product_id, quantity in cart.items():
                product = get_object_or_404(Products, id=product_id)
                order = Order.objects.create(
                    guest_email=email,
                    product=product,
                    quantity=quantity,
                    shipping_address=shipping_address
                )
                request.session['order_id'] = order.id

                # Send order confirmation email to the guest
                send_mail(
                    f'Order Confirmation for {product.title}',
                    f'Thank you for your purchase of {product.title}.\n\nShipping Address: {shipping_address}',
                    settings.EMAIL_HOST_USER,
                    [email]
                )

                # Send order notification email to the seller
                send_mail(
                    f'New Order for {product.title}',
                    f'A new order has been placed for {product.title}.\n\nQuantity: {quantity}\n\nShipping Address: {shipping_address}\n\nGuest Email: {email}',
                    settings.EMAIL_HOST_USER,
                    [settings.EMAIL_HOST_USER]
                )

            # Redirect to PayPal for payment
            request.session['cart'] = {}
            return redirect('cart:process_payment')

    else:
        form = GuestCheckoutForm()
    return render(request, 'cart/guest_checkout.html', {'form': form})

def process_payment(request):
    order_id = request.session.get('order_id')
    if not order_id:
        return redirect('cart:cart')  # or handle this case as needed

    order = get_object_or_404(Order, id=order_id)
    host = request.get_host()

    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': '%.2f' % (order.product.price * order.quantity),
        'item_name': 'Order {}'.format(order.id),
        'invoice': str(order.id),
        'currency_code': 'USD',
        'notify_url': 'http://{}{}'.format(host, reverse('paypal-ipn')),
        'return_url': 'http://{}{}'.format(host, reverse('cart:payment_done')),
        'cancel_return': 'http://{}{}'.format(host, reverse('cart:payment_canceled')),
    }

    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, 'cart/process_payment.html', {'order': order, 'form': form, 'total_price': order.product.price * order.quantity})

def payment_done(request):
    return render(request, 'cart/payment_success.html')

def payment_canceled(request):
    return render(request, 'cart/payment_cancel.html')

def guest_checkout_success_view(request):
    return render(request, 'cart/guest_checkout_success.html')