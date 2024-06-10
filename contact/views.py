from django.shortcuts import render, redirect
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .forms import ContactForm
from .models import ContactMessage

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            # Render the email template
            context = {
                'name': contact_message.name,
                'email': contact_message.email,
                'phone_number': contact_message.phone_number,
                'message': contact_message.message,
            }
            email_content = render_to_string('emails/contact_email.html', context)
            plain_message = strip_tags(email_content)

            # Send email
            email = EmailMultiAlternatives(
                subject=f'Contact Form Submission from {contact_message.name}',
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.SELLER_EMAIL],  # Use the configured seller email
            )
            email.attach_alternative(email_content, "text/html")
            email.send()

            return redirect('home:home')  # Redirect to the home page
    else:
        form = ContactForm()

    return render(request, 'contact/contact.html', {'form': form})

def contact_success(request):
    return render(request, 'contact/contact_success.html')
