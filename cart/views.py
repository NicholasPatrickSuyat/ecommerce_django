import paypalrestsdk
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import Cart, DeliveryAddress
from products.models import Products, ProductSize
from user.models import Order, OrderItem
from .forms import GuestCheckoutForm, CheckoutForm, DeliveryAddressForm, OrderStatusForm
from .paypal_utils import create_invoice
from .decorators import user_is_admin
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import json
from django.utils import timezone
import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

CustomUser = get_user_model()

def create_order(user, shipping_address, cart_items):
    logger.debug("Creating order")
    order = Order.objects.create(
        user=user,
        shipping_address=shipping_address,
        order_date=timezone.now(),
        status='PENDING'
    )
    total_cost = 0
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            size=item['size'],
            sheen=item.get('sheen'),
            quantity=item['quantity']
        )
        total_cost += item['size'].price * item['quantity']
    
    order.total_cost = total_cost
    order.save()
    logger.debug(f"Order created with ID: {order.id}")

    # Generate the PayPal invoice
    invoice_id = create_invoice(order, user.email)
    if invoice_id:
        order.paypal_invoice_id = invoice_id
        order.save()
        logger.debug(f"PayPal invoice ID {invoice_id} saved for order {order.id}")
    else:
        logger.warning(f"Failed to create PayPal invoice for order {order.id}")
    
    return order


def create_invoice_view(request, order, email):
    invoice_id = create_invoice(order, email)
    return invoice_id

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
        return redirect('cart:cart')

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
        return redirect('cart:cart')

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

        if form.is_valid() and address_form.is_valid():
            shipping_address = address_form.save(commit=False)
            shipping_address.user = request.user
            shipping_address.save()

            cart_items = Cart.objects.filter(user=request.user)
            if not cart_items.exists():
                return redirect('cart:cart')

            # Create order without the paypal_invoice_id initially
            order = create_order(request.user, shipping_address, cart_items)

            # Generate the invoice and update the order with the paypal_invoice_id
            invoice_id = create_invoice_view(request, order, request.user.email)
            if invoice_id:
                order.paypal_invoice_id = invoice_id
                order.save()

            # Clear the cart
            cart_items.delete()
            request.session['order_id'] = str(order.id)
            request.session['total_price'] = str(order.total_cost())
            return redirect('cart:payment_done')
    else:
        form = CheckoutForm()
        address_form = DeliveryAddressForm()
        cart_items = Cart.objects.filter(user=request.user)
        total_price = sum(item.size.price * item.quantity for item in cart_items)

    return render(request, 'cart/checkout.html', {
        'form': form,
        'address_form': address_form,
        'total_price': total_price,
        'PAYPAL_CLIENT_ID': settings.PAYPAL_CLIENT_ID,
        'user': request.user
    })


def guest_checkout_view(request):
    if request.method == 'POST':
        form = GuestCheckoutForm(request.POST)
        address_form = DeliveryAddressForm(request.POST)

        if form.is_valid() and address_form.is_valid():
            email = form.cleaned_data['email']
            shipping_address = address_form.save(commit=False)
            guest_username = f"guest_{get_random_string(10)}"
            user = CustomUser.objects.create_user(username=guest_username, email=email)
            shipping_address.user = user
            shipping_address.save()

            cart = request.session.get('cart', {})
            if not cart:
                return redirect('cart:cart')

            cart_items = []
            for product_id, details in cart.items():
                product = get_object_or_404(Products, id=product_id)
                size = get_object_or_404(ProductSize, id=details['size_id'])
                cart_items.append({
                    'product': product,
                    'size': size,
                    'quantity': details['quantity']
                })

            # Create order without the paypal_invoice_id initially
            order = create_order(user, shipping_address, cart_items)

            # Generate the invoice and update the order with the paypal_invoice_id
            invoice_id = create_invoice_view(request, order, email)
            if invoice_id:
                order.paypal_invoice_id = invoice_id
                order.save()

            # Clear the cart
            request.session['cart'] = {}
            request.session['order_id'] = str(order.id)
            request.session['total_price'] = str(order.total_cost())
            return redirect('cart:payment_done')
    else:
        form = GuestCheckoutForm()
        address_form = DeliveryAddressForm()
        cart = request.session.get('cart', {})
        total_price = sum(get_object_or_404(ProductSize, id=details['size_id']).price * details['quantity'] for details in cart.values())

    return render(request, 'cart/guest_checkout.html', {
        'form': form,
        'address_form': address_form,
        'total_price': total_price,
        'PAYPAL_CLIENT_ID': settings.PAYPAL_CLIENT_ID
    })

def send_order_confirmation_email(order):
    subject = 'Order Confirmation'
    html_message = render_to_string('emails/order_confirmation.html', {
        'order': order,
        'order_items': order.items.all(),
        'total_cost': order.total_cost
    })
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [order.user.email if order.user else order.guest_email, from_email]

    send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)


def payment_done(request):
    try:
        if request.method == "POST":
            form = CheckoutForm(request.POST)
            address_form = DeliveryAddressForm(request.POST)

            if form.is_valid() and address_form.is_valid():
                user = request.user if request.user.is_authenticated else None
                guest_email = form.cleaned_data.get('email') if not user else None

                shipping_address = address_form.save()

                # Create order
                order = Order.objects.create(
                    user=user,
                    guest_email=guest_email,
                    shipping_address=str(shipping_address),
                    status='PENDING'
                )

                # Move items from cart to order
                if user:
                    cart_items = Cart.objects.filter(user=user)
                else:
                    cart_items = []
                    cart = request.session.get('cart', {})
                    for product_id, details in cart.items():
                        product = get_object_or_404(Products, id=product_id)
                        size = get_object_or_404(ProductSize, id=details['size_id'])
                        cart_items.append(Cart(product=product, size=size, quantity=details['quantity']))

                total_cost = 0
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        size=item.size,
                        quantity=item.quantity
                    )
                    total_cost += item.size.price * item.quantity
                
                # Update total cost and save the order
                order.total_cost = total_cost
                order.save()

                # Clear cart
                if user:
                    cart_items.delete()
                else:
                    request.session['cart'] = {}

                # Send order confirmation email
                send_order_confirmation_email(order)

                return render(request, 'cart/payment_success.html', {'order': order})
            else:
                return redirect('cart:checkout')
        else:
            return redirect('cart:checkout')
    except Exception as e:
        return redirect('cart:payment_error')

def payment_cancelled(request):
    return render(request, 'cart/payment_cancel.html', {'error': 'Payment was cancelled'})

def payment_error(request):
    return render(request, 'cart/payment_error.html')

@user_is_admin
def order_list_view(request):
    orders = Order.objects.all().order_by('-order_date')
    return render(request, 'order_management/order_list.html', {'orders': orders})

@user_is_admin
def order_detail_view(request, id):
    order = get_object_or_404(Order, id=id)
    order_items = OrderItem.objects.filter(order=order)
    total_cost = sum(item.size.price * item.quantity for item in order_items)
    return render(request, 'order_management/order_detail.html', {
        'order': order,
        'order_items': order_items,
        'total_cost': total_cost
    })

@user_is_admin
def order_update_view(request, id):
    order = get_object_or_404(Order, id=id)
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('cart:order_detail', id=order.id)
    else:
        form = OrderStatusForm(instance=order)
    return render(request, 'order_management/order_update.html', {'form': form, 'order': order})

@user_is_admin
def order_delete_view(request, id):
    order = get_object_or_404(Order, id=id)
    if request.method == 'POST':
        order.delete()
        return redirect('cart:order_list')
    return render(request, 'order_management/order_delete.html', {'order': order})

def custom_permission_denied_view(request, exception=None):
    return render(request, 'errors/permission_denied.html', status=403)

@csrf_exempt
def paypal_webhook(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.debug(f"Webhook received: {json.dumps(data, indent=2)}")

            event_type = data.get('event_type')
            resource = data.get('resource')

            # Check for order_id in multiple places
            order_id = resource.get('supplementary_data', {}).get('related_ids', {}).get('order_id')
            if not order_id:
                order_id = resource.get('invoice_id')
            if not order_id:
                for purchase_unit in resource.get('purchase_units', []):
                    order_id = purchase_unit.get('reference_id')
                    if order_id:
                        break

            logger.debug(f"Processed event type: {event_type}, Order ID: {order_id}")

            if not order_id:
                logger.warning("Order ID not found in the resource.")
                return JsonResponse({'status': 'invalid data', 'message': 'Order ID not found'}, status=400)

            if event_type == 'PAYMENT.CAPTURE.COMPLETED':
                try:
                    order = get_object_or_404(Order, paypal_invoice_id=order_id)
                    order.status = 'COMPLETED'
                    order.save()
                    logger.info(f"Order {order_id} marked as completed.")
                    return JsonResponse({'status': 'success'}, status=200)
                except Order.DoesNotExist:
                    logger.error(f"No Order matches the given query for order_id: {order_id}")
                    return JsonResponse({'status': 'error', 'message': 'Order not found'}, status=400)

            elif event_type == 'CHECKOUT.ORDER.APPROVED':
                try:
                    order = get_object_or_404(Order, paypal_invoice_id=order_id)
                    order.status = 'APPROVED'
                    order.save()
                    logger.info(f"Order {order_id} marked as approved.")
                    return JsonResponse({'status': 'success'}, status=200)
                except Order.DoesNotExist:
                    logger.error(f"No Order matches the given query for order_id: {order_id}")
                    return JsonResponse({'status': 'error', 'message': 'Order not found'}, status=400)

            elif event_type == 'CHECKOUT.ORDER.COMPLETED':
                try:
                    order = get_object_or_404(Order, paypal_invoice_id=order_id)
                    order.status = 'COMPLETED'
                    order.save()
                    logger.info(f"Order {order_id} marked as completed.")
                    return JsonResponse({'status': 'success'}, status=200)
                except Order.DoesNotExist:
                    logger.error(f"No Order matches the given query for order_id: {order_id}")
                    return JsonResponse({'status': 'error', 'message': 'Order not found'}, status=400)

            else:
                logger.warning(f"Unhandled event type: {event_type}")
                return JsonResponse({'status': 'invalid event type'}, status=400)

        except json.JSONDecodeError as e:
            logger.exception(f"JSON decode error: {e}")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.exception(f"Exception processing webhook: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        logger.warning("Invalid request method")
        return JsonResponse({'status': 'invalid request'}, status=400)


def test_logging_view(request):
    logger = logging.getLogger(__name__)
    logger.debug("Test logging debug message")
    logger.info("Test logging info message")
    return HttpResponse("Logging test complete. Check your logs.")


def test_invoice_creation(request):
    user = request.user
    order = Order.objects.filter(user=user).last()  # Use the most recent order for testing
    if not order:
        return HttpResponse("No orders found for this user.")
    
    invoice_id = create_invoice(order, user.email)
    if invoice_id:
        order.paypal_invoice_id = invoice_id
        order.save()
        return HttpResponse(f"Invoice created successfully: {invoice_id}")
    else:
        return HttpResponse("Failed to create invoice.")
