from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import CheckoutForm
from products.models import Products
import json
import requests

@login_required
def cart_view(request):
    cart = request.session.get('cart', {})
    products = Products.objects.filter(id__in=cart.keys())
    total_price = sum(product.price * cart[str(product.id)] for product in products)
    return render(request, 'cart/cart.html', {'products': products, 'cart': cart, 'total_price': total_price})

@login_required
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1
    request.session['cart'] = cart
    return redirect('cart:cart')

@login_required
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
    return redirect('cart:cart')

@login_required
def update_cart(request, product_id):
    cart = request.session.get('cart', {})
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        cart[str(product_id)] = quantity
    else:
        if str(product_id) in cart:
            del cart[str(product_id)]
    request.session['cart'] = cart
    return redirect('cart:cart')

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    products = Products.objects.filter(id__in=cart.keys())
    total_price = sum(product.price * cart[str(product.id)] for product in products)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Process payment with PayPal
            order_data = {
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {
                        "currency_code": "USD",
                        "value": str(total_price)
                    }
                }],
                "application_context": {
                    "return_url": request.build_absolute_uri('/cart/payment-success/'),
                    "cancel_url": request.build_absolute_uri('/cart/payment-cancel/')
                }
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {get_paypal_access_token()}"
            }

            response = requests.post('https://api-m.sandbox.paypal.com/v2/checkout/orders', 
                                     headers=headers, 
                                     data=json.dumps(order_data))

            if response.status_code == 201:
                order = response.json()
                for link in order['links']:
                    if link['rel'] == 'approve':
                        return redirect(link['href'])
            else:
                return render(request, 'cart/checkout.html', {'form': form, 'error': 'Error creating PayPal order.'})

    else:
        form = CheckoutForm()

    return render(request, 'cart/checkout.html', {'form': form, 'products': products, 'total_price': total_price})

def get_paypal_access_token():
    client_id = 'YOUR_PAYPAL_CLIENT_ID'
    secret = 'YOUR_PAYPAL_SECRET'
    auth = (client_id, secret)
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }
    response = requests.post('https://api-m.sandbox.paypal.com/v1/oauth2/token', 
                             headers=headers, 
                             data=data, 
                             auth=auth)
    if response.status_code == 200:
        return response.json()['access_token']
    return None

@login_required
def payment_success(request):
    request.session['cart'] = {}
    return render(request, 'cart/payment_success.html')

@login_required
def payment_cancel(request):
    return render(request, 'cart/payment_cancel.html')
