from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from decimal import Decimal
from .models import Cart, DeliveryAddress, DeliveryStatus
from products.models import Products, ProductSize
from user.models import Order
from .forms import GuestCheckoutForm, CheckoutForm, DeliveryAddressForm
from paypal.standard.forms import PayPalPaymentsForm

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
        if form.is_valid() and address_form.is_valid():
            shipping_address = address_form.save(commit=False)
            shipping_address.user = request.user
            shipping_address.save()
            
            cart_items = Cart.objects.filter(user=request.user)
            total_price = 0
            orders = []
            for item in cart_items:
                size = get_object_or_404(ProductSize, id=item.size_id)
                total_price += size.price * item.quantity
                order = Order.objects.create(
                    user=request.user,
                    product=item.product,
                    quantity=item.quantity,
                    shipping_address=shipping_address.address_line1  # Use the address line or any other field
                )
                order.size = size  # Make sure to include size in order
                orders.append(order)

            request.session['order_id'] = str(orders[0].id)  # Store the first order ID in the session as a string
            request.session['total_price'] = str(total_price)  # Store the total price in the session as a string

            # Render the email template
            context = {
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'orders': orders,
                'total_price': total_price,
                'shipping_address': shipping_address,
            }
            email_content = render_to_string('emails/order_confirmation.html', context)
            plain_message = strip_tags(email_content)

            # Send order confirmation email to the user
            email = EmailMultiAlternatives(
                subject='Order Confirmation',
                body=plain_message,
                from_email=settings.EMAIL_HOST_USER,
                to=[request.user.email]
            )
            email.attach_alternative(email_content, "text/html")
            email.send()

            # Send order notification email to the seller
            seller_email = EmailMultiAlternatives(
                subject='New Order',
                body=plain_message,
                from_email=settings.EMAIL_HOST_USER,
                to=[settings.SELLER_EMAIL]
            )
            seller_email.attach_alternative(email_content, "text/html")
            seller_email.send()

            cart_items.delete()

            return_url = request.build_absolute_uri(reverse('cart:payment_done'))
            cancel_url = request.build_absolute_uri(reverse('cart:payment_canceled'))
            paypal_dict = {
                'business': settings.PAYPAL_RECEIVER_EMAIL,
                'amount': '%.2f' % total_price,
                'item_name': 'Order {}'.format(request.user.username),
                'invoice': str(orders[0].id),
                'currency_code': 'USD',
                'notify_url': request.build_absolute_uri(reverse('paypal-ipn')),
                'return_url': return_url,
                'cancel_return': cancel_url,
            }

            form = PayPalPaymentsForm(initial=paypal_dict)
            return render(request, 'cart/process_payment.html', {'form': form, 'total_price': total_price})

    else:
        form = CheckoutForm()
        address_form = DeliveryAddressForm()
    return render(request, 'cart/checkout.html', {'form': form, 'address_form': address_form, 'user': request.user})


def guest_checkout_view(request):
    if request.method == 'POST':
        form = GuestCheckoutForm(request.POST)
        address_form = DeliveryAddressForm(request.POST)
        if form.is_valid() and address_form.is_valid():
            email = form.cleaned_data['email']
            shipping_address = address_form.save()
            cart = request.session.get('cart', {})
            total_price = 0
            orders = []
            for product_id, details in cart.items():
                product = get_object_or_404(Products, id=product_id)
                size = get_object_or_404(ProductSize, id=details['size_id'])
                total_price += size.price * details['quantity']
                order = Order.objects.create(
                    guest_email=email,
                    product=product,
                    quantity=details['quantity'],
                    shipping_address=shipping_address.address_line1  # Use the address line or any other field
                )
                order.size = size  # Make sure to include size in order
                orders.append(order)

            request.session['order_id'] = str(orders[0].id)  # Store the first order ID in the session as a string
            request.session['total_price'] = str(total_price)  # Store the total price in the session as a string

            # Render the email template
            context = {
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'orders': orders,
                'total_price': total_price,
                'shipping_address': shipping_address,
            }
            email_content = render_to_string('emails/order_confirmation.html', context)
            plain_message = strip_tags(email_content)

            # Send order confirmation email to the guest
            guest_email = EmailMultiAlternatives(
                subject='Order Confirmation',
                body=plain_message,
                from_email=settings.EMAIL_HOST_USER,
                to=[email]
            )
            guest_email.attach_alternative(email_content, "text/html")
            guest_email.send()

            # Send order notification email to the seller
            seller_email = EmailMultiAlternatives(
                subject='New Order',
                body=plain_message,
                from_email=settings.EMAIL_HOST_USER,
                to=[settings.SELLER_EMAIL]
            )
            seller_email.attach_alternative(email_content, "text/html")
            seller_email.send()

            request.session['cart'] = {}
            return redirect('cart:process_payment')

    else:
        form = GuestCheckoutForm()
        address_form = DeliveryAddressForm()
    return render(request, 'cart/guest_checkout.html', {'form': form, 'address_form': address_form})


def process_payment(request):
    total_price = Decimal(request.session.get('total_price'))  # Retrieve the total price from the session and convert to Decimal
    order_id = request.session.get('order_id')
    if not order_id:
        return redirect('cart:cart')  # or handle this case as needed

    order = get_object_or_404(Order, id=order_id)
    host = request.get_host()

    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': '%.2f' % total_price,
        'item_name': 'Order {}'.format(order.id),
        'invoice': str(order.id),
        'currency_code': 'USD',
        'notify_url': 'http://{}{}'.format(host, reverse('paypal-ipn')),
        'return_url': 'http://{}{}'.format(host, reverse('cart:payment_done')),
        'cancel_return': 'http://{}{}'.format(host, reverse('cart:payment_canceled')),
    }

    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, 'cart/process_payment.html', {'order': order, 'form': form, 'total_price': total_price})

def payment_done(request):
    return render(request, 'cart/payment_success.html')

def payment_canceled(request):
    return render(request, 'cart/payment_cancel.html')

def guest_checkout_success_view(request):
    return render(request, 'cart/guest_checkout_success.html')



"""EMAIL AFTER PAYMENT ONLY(USE THIS CODE AFTER DEPLOYMENT)"""
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.core.mail import EmailMultiAlternatives
# from django.urls import reverse
# from django.conf import settings
# from django.template.loader import render_to_string
# from django.utils.html import strip_tags
# from decimal import Decimal
# from .models import Cart, DeliveryAddress, DeliveryStatus
# from products.models import Products, ProductSize
# from user.models import Order
# from .forms import GuestCheckoutForm, CheckoutForm, DeliveryAddressForm
# from paypal.standard.forms import PayPalPaymentsForm

# def cart_view(request):
#     cart_items = []
#     total_price = 0

#     if request.user.is_authenticated:
#         cart_items_query = Cart.objects.filter(user=request.user)
#         for item in cart_items_query:
#             size = get_object_or_404(ProductSize, id=item.size_id)
#             total_price += size.price * item.quantity
#             cart_items.append({
#                 'product': item.product,
#                 'size': size,
#                 'quantity': item.quantity,
#                 'total_price': size.price * item.quantity,
#             })
#     else:
#         cart = request.session.get('cart', {})
#         for product_id, details in cart.items():
#             product = get_object_or_404(Products, id=product_id)
#             size = get_object_or_404(ProductSize, id=details['size_id'])
#             total_price += size.price * details['quantity']
#             cart_items.append({
#                 'product': product,
#                 'size': size,
#                 'quantity': details['quantity'],
#                 'total_price': size.price * details['quantity'],
#             })

#     return render(request, 'cart/cart.html', {'cart_items': cart_items, 'total_price': total_price})


# def add_to_cart(request, product_id):
#     product = get_object_or_404(Products, id=product_id)
#     size_id = request.POST.get('size')
#     size = get_object_or_404(ProductSize, id=size_id)
#     if request.user.is_authenticated:
#         cart_item, created = Cart.objects.get_or_create(user=request.user, product=product, size_id=size_id)
#         if not created:
#             cart_item.quantity += 1
#             cart_item.save()
#     else:
#         cart = request.session.get('cart', {})
#         if str(product_id) not in cart:
#             cart[str(product_id)] = {'quantity': 0, 'size_id': size_id}
#         cart[str(product_id)]['quantity'] += 1
#         request.session['cart'] = cart
#     return redirect('cart:cart')

# def remove_from_cart(request, product_id):
#     product = get_object_or_404(Products, id=product_id)
#     size_id = request.POST.get('size')
#     if size_id is None:
#         return redirect('cart:cart')  # Redirect if size_id is missing

#     if request.user.is_authenticated:
#         cart_item = get_object_or_404(Cart, user=request.user, product=product, size_id=size_id)
#         cart_item.delete()
#     else:
#         cart = request.session.get('cart', {})
#         if str(product_id) in cart:
#             del cart[str(product_id)]
#             request.session['cart'] = cart
#     return redirect('cart:cart')

# def update_cart(request, product_id):
#     product = get_object_or_404(Products, id=product_id)
#     size_id = request.POST.get('size')
#     if size_id is None:
#         return redirect('cart:cart')  # Redirect if size_id is missing

#     quantity = int(request.POST.get('quantity'))
#     if request.user.is_authenticated:
#         cart_item = get_object_or_404(Cart, user=request.user, product=product, size_id=size_id)
#         cart_item.quantity = quantity
#         cart_item.save()
#     else:
#         cart = request.session.get('cart', {})
#         if str(product_id) in cart:
#             cart[str(product_id)]['quantity'] = quantity
#             request.session['cart'] = cart
#     return redirect('cart:cart')

# def checkout_view(request):
#     if request.user.is_authenticated:
#         return logged_in_checkout_view(request)
#     else:
#         return guest_checkout_view(request)

# @login_required
# def logged_in_checkout_view(request):
#     if request.method == 'POST':
#         form = CheckoutForm(request.POST)
#         address_form = DeliveryAddressForm(request.POST)
#         if form.is_valid() and address_form.is_valid():
#             shipping_address = address_form.save(commit=False)
#             shipping_address.user = request.user
#             shipping_address.save()
            
#             cart_items = Cart.objects.filter(user=request.user)
#             total_price = 0
#             orders = []
#             for item in cart_items:
#                 size = get_object_or_404(ProductSize, id=item.size_id)
#                 total_price += size.price * item.quantity
#                 order = Order.objects.create(
#                     user=request.user,
#                     product=item.product,
#                     quantity=item.quantity,
#                     shipping_address=shipping_address.address_line1  # Use the address line or any other field
#                 )
#                 orders.append(order)

#             request.session['order_id'] = str(orders[0].id)  # Store the first order ID in the session as a string
#             request.session['total_price'] = str(total_price)  # Store the total price in the session as a string
#             request.session['first_name'] = form.cleaned_data['first_name']
#             request.session['last_name'] = form.cleaned_data['last_name']
#             request.session['shipping_address'] = shipping_address.id

#             return_url = request.build_absolute_uri(reverse('cart:payment_done'))
#             cancel_url = request.build_absolute_uri(reverse('cart:payment_canceled'))
#             paypal_dict = {
#                 'business': settings.PAYPAL_RECEIVER_EMAIL,
#                 'amount': '%.2f' % total_price,
#                 'item_name': 'Order {}'.format(request.user.username),
#                 'invoice': str(orders[0].id),
#                 'currency_code': 'USD',
#                 'notify_url': request.build_absolute_uri(reverse('paypal-ipn')),
#                 'return_url': return_url,
#                 'cancel_return': cancel_url,
#             }

#             form = PayPalPaymentsForm(initial=paypal_dict)
#             return render(request, 'cart/process_payment.html', {'form': form, 'total_price': total_price})

#     else:
#         form = CheckoutForm()
#         address_form = DeliveryAddressForm()
#     return render(request, 'cart/checkout.html', {'form': form, 'address_form': address_form, 'user': request.user})

# def guest_checkout_view(request):
#     if request.method == 'POST':
#         form = GuestCheckoutForm(request.POST)
#         address_form = DeliveryAddressForm(request.POST)
#         if form.is_valid() and address_form.is_valid():
#             email = form.cleaned_data['email']
#             shipping_address = address_form.save()
#             cart = request.session.get('cart', {})
#             total_price = 0
#             orders = []
#             for product_id, details in cart.items():
#                 product = get_object_or_404(Products, id=product_id)
#                 size = get_object_or_404(ProductSize, id=details['size_id'])
#                 total_price += size.price * details['quantity']
#                 order = Order.objects.create(
#                     guest_email=email,
#                     product=product,
#                     quantity=details['quantity'],
#                     shipping_address=shipping_address.address_line1  # Use the address line or any other field
#                 )
#                 orders.append(order)

#             request.session['order_id'] = str(orders[0].id)  # Store the first order ID in the session as a string
#             request.session['total_price'] = str(total_price)  # Store the total price in the session as a string
#             request.session['first_name'] = form.cleaned_data['first_name']
#             request.session['last_name'] = form.cleaned_data['last_name']
#             request.session['shipping_address'] = shipping_address.id

#             return_url = request.build_absolute_uri(reverse('cart:payment_done'))
#             cancel_url = request.build_absolute_uri(reverse('cart:payment_canceled'))
#             paypal_dict = {
#                 'business': settings.PAYPAL_RECEIVER_EMAIL,
#                 'amount': '%.2f' % total_price,
#                 'item_name': 'Order {}'.format(orders[0].id),
#                 'invoice': str(orders[0].id),
#                 'currency_code': 'USD',
#                 'notify_url': request.build_absolute_uri(reverse('paypal-ipn')),
#                 'return_url': return_url,
#                 'cancel_return': cancel_url,
#             }

#             form = PayPalPaymentsForm(initial=paypal_dict)
#             return render(request, 'cart/process_payment.html', {'form': form, 'total_price': total_price})

#     else:
#         form = GuestCheckoutForm()
#         address_form = DeliveryAddressForm()
#     return render(request, 'cart/guest_checkout.html', {'form': form, 'address_form': address_form})

# def process_payment(request):
#     total_price = Decimal(request.session.get('total_price'))  # Retrieve the total price from the session and convert to Decimal
#     order_id = request.session.get('order_id')
#     if not order_id:
#         return redirect('cart:cart')  # or handle this case as needed

#     order = get_object_or_404(Order, id=order_id)
#     host = request.get_host()

#     paypal_dict = {
#         'business': settings.PAYPAL_RECEIVER_EMAIL,
#         'amount': '%.2f' % total_price,
#         'item_name': 'Order {}'.format(order.id),
#         'invoice': str(order.id),
#         'currency_code': 'USD',
#         'notify_url': 'http://{}{}'.format(host, reverse('paypal-ipn')),
#         'return_url': 'http://{}{}'.format(host, reverse('cart:payment_done')),
#         'cancel_return': 'http://{}{}'.format(host, reverse('cart:payment_canceled')),
#     }

#     form = PayPalPaymentsForm(initial=paypal_dict)
#     return render(request, 'cart/process_payment.html', {'order': order, 'form': form, 'total_price': total_price})

# def payment_done(request):
#     order_id = request.session.get('order_id')
#     total_price = request.session.get('total_price')
#     first_name = request.session.get('first_name')
#     last_name = request.session.get('last_name')
#     shipping_address_id = request.session.get('shipping_address')

#     if not order_id or not total_price or not first_name or not last_name or not shipping_address_id:
#         return redirect('cart:cart')  # or handle this case as needed

#     order = get_object_or_404(Order, id=order_id)
#     shipping_address = get_object_or_404(DeliveryAddress, id=shipping_address_id)
    
#     context = {
#         'first_name': first_name,
#         'last_name': last_name,
#         'orders': [order],
#         'total_price': total_price,
#         'shipping_address': shipping_address,
#     }
#     email_content = render_to_string('emails/order_confirmation.html', context)
#     plain_message = strip_tags(email_content)

#     # Send order confirmation email to the user
#     email = EmailMultiAlternatives(
#         subject='Order Confirmation',
#         body=plain_message,
#         from_email=settings.EMAIL_HOST_USER,
#         to=[order.user.email if order.user else order.guest_email]
#     )
#     email.attach_alternative(email_content, "text/html")
#     email.send()

#     # Send order notification email to the seller
#     seller_email = EmailMultiAlternatives(
#         subject='New Order',
#         body=plain_message,
#         from_email=settings.EMAIL_HOST_USER,
#         to=[settings.SELLER_EMAIL]
#     )
#     seller_email.attach_alternative(email_content, "text/html")
#     seller_email.send()

#     # Clear the cart
#     if request.user.is_authenticated:
#         Cart.objects.filter(user=request.user).delete()
#     else:
#         request.session['cart'] = {}

#     return render(request, 'cart/payment_success.html')

# def payment_canceled(request):
#     return render(request, 'cart/payment_cancel.html')

# def guest_checkout_success_view(request):
#     return render(request, 'cart/guest_checkout_success.html')
