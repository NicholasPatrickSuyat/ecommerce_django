import paypalrestsdk
from django.conf import settings

def create_invoice(order, email):
    paypalrestsdk.configure({
        "mode": "sandbox",  # or "live" if in production
        "client_id": settings.PAYPAL_CLIENT_ID,
        "client_secret": settings.PAYPAL_CLIENT_SECRET,
    })

    invoice = paypalrestsdk.Invoice({
        'merchant_info': {
            "email": "merchant@example.com",  # Replace with your merchant email
        },
        'billing_info': [{
            "email": email,
        }],
        'items': [{
            "name": order.product.title,
            "quantity": order.quantity,
            "unit_price": {
                "currency": "USD",
                "value": str(order.size.price)
            }
        }],
        'note': 'Thank you for your purchase!',
        'payment_term': {
            "term_type": "NET_45"
        }
    })

    if invoice.create():
        return invoice
    else:
        return None
