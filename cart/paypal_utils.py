import paypalrestsdk
from django.conf import settings

def create_invoice(order, email):
    paypalrestsdk.configure({
        "mode": "sandbox",  # or "live" if in production
        "client_id": settings.PAYPAL_CLIENT_ID,
        "client_secret": settings.PAYPAL_CLIENT_SECRET,
    })

    items = [{
        "name": order.product.title,
        "quantity": order.quantity,
        "unit_price": {
            "currency": "USD",
            "value": str(order.size.price)
        }
    }]

    total_product_cost = order.size.price * order.quantity
    shipping_cost = order.shipping_option.cost

    invoice = paypalrestsdk.Invoice({
        'merchant_info': {
            "email": settings.PAYPAL_RECEIVER_EMAIL,  # Replace with your merchant email
        },
        'billing_info': [{
            "email": email,
        }],
        'items': items,
        'shipping_info': {
            'first_name': order.user.first_name,
            'last_name': order.user.last_name,
            'address': {
                'line1': order.shipping_address,
                'city': '',  # Add city if available
                'state': '',  # Add state if available
                'postal_code': '',  # Add postal code if available
                'country_code': 'US'  # Replace with appropriate country code
            }
        },
        'shipping_cost': {
            'amount': {
                'currency': 'USD',
                'value': str(shipping_cost)
            }
        },
        'total_amount': {
            'currency': 'USD',
            'value': str(total_product_cost + shipping_cost)
        },
        'note': 'Thank you for your purchase!',
        'payment_term': {
            "term_type": "NET_45"
        }
    })

    if invoice.create():
        return invoice
    else:
        return None
