import paypalrestsdk
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from .models import Cart, DeliveryAddress, DeliveryStatus
from products.models import Products, ProductSize, ShippingOption
from user.models import Order
from .forms import GuestCheckoutForm, CheckoutForm, DeliveryAddressForm
from .paypal_utils import create_invoice
import logging

logger = logging.getLogger(__name__)

CustomUser = get_user_model()

def create_invoice_view(request, order, email):
    logger.debug(f"Creating invoice for order {order.id} and email {email}")
    invoice = create_invoice(order, email)
    if invoice and invoice.send():
        logger.debug(f"Invoice created and sent successfully for order {order.id}")
        return True
    logger.error(f"Failed to create and send invoice for order {order.id}")
    return False

def send_order_confirmation(orders, user_email, shipping_address, shipping_option, total_payment, shipping_cost):
    subject = 'Order Confirmation'
    context = {
        'first_name': orders[0].user.first_name if orders[0].user.first_name else '',
        'last_name': orders[0].user.last_name if orders[0].user.last_name else '',
        'orders': orders,
        'total_price': sum(order.size.price * order.quantity for order in orders),
        'shipping_address': shipping_address,
        'shipping_option': shipping_option.name,  # Add shipping option name
        'shipping_cost': shipping_cost,  # Add shipping cost
        'total_payment': total_payment,
    }
    email_content = render_to_string('emails/order_confirmation.html', context)
    plain_message = strip_tags(email_content)

    try:
        # Send email to the customer
        customer_email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            to=[user_email]
        )
        customer_email.attach_alternative(email_content, "text/html")
        customer_email.send()
        logger.info(f"Order confirmation email sent to customer: {user_email}")

        # Send email to the seller
        seller_email = EmailMultiAlternatives(
            subject='New Order',
            body=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            to=[settings.EMAIL_HOST_USER]
        )
        seller_email.attach_alternative(email_content, "text/html")
        seller_email.send()
        logger.info(f"Order confirmation email sent to seller: {settings.EMAIL_HOST_USER}")

    except Exception as e:
        logger.error(f"Error sending order confirmation email: {e}")

def cart_view(request):
    cart_items = []
    total_price = 0

    if request.user.is_authenticated:
        cart_items_queryset = Cart.objects.filter(user=request.user)
        for item in cart_items_queryset:
            size = get_object_or_404(ProductSize, id=item.size_id)
            total_price += size.price * item.quantity
            cart_items.append({
                'product': item.product,
                'size': size,
                'quantity': item.quantity,
                'total_price': size.price * item.quantity,
            })
    else:
        cart = request.session.get('cart', {})
        for product_id, details in cart.items():
            product = get_object_or_404(Products, id=product_id)
            size = get_object_or_404(ProductSize, id=details['size_id'])
            total_price += size.price * details['quantity']
            cart_items.append({
                'product': product,
                'size': size,
                'quantity': details['quantity'],
                'total_price': size.price * details['quantity'],
            })

    return render(request, 'cart/cart.html', {'cart_items': cart_items, 'total_price': total_price})

def add_to_cart(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    size_id = request.POST.get('size')
    size = get_object_or_404(ProductSize, id=size_id)
    if request.user.is_authenticated:
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product, size_id=size_id)
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

def remove_from_cart(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    size_id = request.POST.get('size')
    if not size_id:
        return redirect('cart:cart')  # Ensure size_id is provided

    if request.user.is_authenticated:
        cart_item = get_object_or_404(Cart, user=request.user, product=product, size_id=size_id)
        cart_item.delete()
    else:
        cart = request.session.get('cart', {})
        if str(product_id) in cart and cart[str(product_id)]['size_id'] == size_id:
            del cart[str(product_id)]
            request.session['cart'] = cart
    return redirect('cart:cart')

def update_cart(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    size_id = request.POST.get('size')
    quantity = int(request.POST.get('quantity'))
    if not size_id:
        return redirect('cart:cart')  # Ensure size_id is provided

    if request.user.is_authenticated:
        cart_item = get_object_or_404(Cart, user=request.user, product=product, size_id=size_id)
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart = request.session.get('cart', {})
        if str(product_id) in cart and cart[str(product_id)]['size_id'] == size_id:
            cart[str(product_id)]['quantity'] = quantity
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
        address_form = DeliveryAddressForm(request.POST)
        shipping_option_id = request.POST.get('shipping_method')
        shipping_option = get_object_or_404(ShippingOption, id=shipping_option_id)

        if form.is_valid() and address_form.is_valid():
            shipping_address = address_form.save(commit=False)
            shipping_address.user = request.user
            shipping_address.save()

            cart_items = Cart.objects.filter(user=request.user)
            if not cart_items.exists():
                return redirect('cart:cart')

            total_price = Decimal(shipping_option.cost)
            orders = []
            for item in cart_items:
                size = get_object_or_404(ProductSize, id=item.size_id)
                total_price += size.price * item.quantity
                order = Order.objects.create(
                    user=request.user,
                    product=item.product,
                    size=size,
                    quantity=item.quantity,
                    shipping_address=shipping_address.address_line1,
                    shipping_option=shipping_option
                )
                orders.append(order)

            # Check if orders are created
            if orders:
                print("Orders created successfully.")

            request.session['order_id'] = str(orders[0].id)
            request.session['total_price'] = str(total_price)

            if create_invoice_view(request, orders[0], request.user.email):
                cart_items.delete()

                # Send order confirmation email
                send_order_confirmation(orders, request.user.email, shipping_address, shipping_option, total_price, shipping_option.cost)

                return redirect('cart:payment_done')
            else:
                return render(request, 'cart/payment_cancel.html', {'error': 'Failed to create and send invoice'})

    else:
        form = CheckoutForm()
        address_form = DeliveryAddressForm()
        shipping_options = ShippingOption.objects.all()
        cart_items = Cart.objects.filter(user=request.user)
        total_price = sum(item.size.price * item.quantity for item in cart_items)

    return render(request, 'cart/checkout.html', {
        'form': form,
        'address_form': address_form,
        'shipping_options': shipping_options,
        'total_price': total_price,
        'PAYPAL_CLIENT_ID': settings.PAYPAL_CLIENT_ID,
        'user': request.user
    })


def guest_checkout_view(request):
    if request.method == 'POST':
        form = GuestCheckoutForm(request.POST)
        address_form = DeliveryAddressForm(request.POST)
        shipping_option_id = request.POST.get('shipping_method')
        shipping_option = get_object_or_404(ShippingOption, id=shipping_option_id)

        if form.is_valid() and address_form.is_valid():
            email = form.cleaned_data['email']
            shipping_address = address_form.save(commit=False)
            guest_username = f"guest_{get_random_string(10)}"
            user = CustomUser.objects.create_user(username=guest_username, email=email)
            shipping_address.user = user
            shipping_address.save()

            cart = request.session.get('cart', {})
            if not cart:
                return redirect('cart:cart')  # Redirect to cart if there are no items

            total_price = Decimal(shipping_option.cost)
            orders = []
            for product_id, details in cart.items():
                product = get_object_or_404(Products, id=product_id)
                size = get_object_or_404(ProductSize, id=details['size_id'])
                item_total_price = size.price * details['quantity']
                total_price += item_total_price
                order = Order.objects.create(
                    user=user,
                    product=product,
                    size=size,
                    quantity=details['quantity'],
                    shipping_address=shipping_address.address_line1,
                    shipping_option=shipping_option
                )
                orders.append(order)

            request.session['order_id'] = str(orders[0].id)
            request.session['total_price'] = str(total_price)

            if create_invoice_view(request, orders[0], email):
                request.session['cart'] = {}

                # Send order confirmation email
                send_order_confirmation(orders, email, shipping_address, shipping_option, total_price, shipping_option.cost)

                return redirect('cart:payment_done')
            else:
                return render(request, 'cart/payment_cancel.html', {'error': 'Failed to create and send invoice'})

    else:
        form = GuestCheckoutForm()
        address_form = DeliveryAddressForm()
        shipping_options = ShippingOption.objects.all()
        cart = request.session.get('cart', {})
        total_price = sum(get_object_or_404(ProductSize, id=details['size_id']).price * details['quantity'] for product_id, details in cart.items())

    return render(request, 'cart/guest_checkout.html', {
        'form': form,
        'address_form': address_form,
        'shipping_options': shipping_options,
        'total_price': total_price,
        'PAYPAL_CLIENT_ID': settings.PAYPAL_CLIENT_ID
    })

def payment_done(request):
    if request.user.is_authenticated:
        return render(request, 'cart/payment_success.html')
    else:
        return render(request, 'cart/guest_checkout_success.html')

def payment_canceled(request):
    return render(request, 'cart/payment_cancel.html')

def guest_checkout_success_view(request):
    return render(request, 'cart/guest_checkout_success.html')

def payment_error(request):
    return render(request, 'cart/payment_error.html')
