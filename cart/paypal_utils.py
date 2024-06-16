import paypalrestsdk
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def create_invoice(order, email):
    print("create_invoice function called")  # Add this line
    logger.debug("create_invoice function called")  # Log to ensure function is called
    
    # Configure PayPal SDK
    paypalrestsdk.configure({
        "mode": settings.PAYPAL_MODE,  # 'sandbox' or 'live'
        "client_id": settings.PAYPAL_CLIENT_ID,
        "client_secret": settings.PAYPAL_CLIENT_SECRET,
    })

    # Create the invoice
    invoice = paypalrestsdk.Invoice({
        'merchant_info': {
            "email": settings.PAYPAL_RECEIVER_EMAIL,
        },
        'billing_info': [{
            "email": email,
        }],
        'items': [{
            "name": item.product.title,
            "quantity": item.quantity,
            "unit_price": {
                "currency": "USD",
                "value": str(item.size.price)
            }
        } for item in order.items.all()],
        'note': f"Order ID: {order.id}",
        'payment_term': {
            'term_type': 'NET_30'
        }
    })

    try:
        if invoice.create():
            print(f"Invoice created successfully for order {order.id}, Invoice ID: {invoice.id}")  # Add this line
            logger.info(f"Invoice created successfully for order {order.id}")
            logger.debug(f"Invoice ID: {invoice.id}")
            return invoice.id  # Return the invoice ID to be stored in the order
        else:
            print(f"Error creating invoice for order {order.id}: {invoice.error}")  # Add this line
            logger.error(f"Error creating invoice for order {order.id}: {invoice.error}")
            return None
    except Exception as e:
        print(f"Exception occurred while creating invoice for order {order.id}: {str(e)}")  # Add this line
        logger.error(f"Exception occurred while creating invoice for order {order.id}: {str(e)}")
        return None
