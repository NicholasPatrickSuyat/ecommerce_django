from django.shortcuts import render, redirect
from django.core.mail import send_mail
from .forms import ContactForm
from .models import ContactMessage

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            # Send email (this is an example, you'll need to configure your email settings)
            send_mail(
                f'Contact Form Submission from {contact_message.name}',
                f"Message: {contact_message.message}\nPhone Number: {contact_message.phone_number}",
                contact_message.email,
                ['your-email@example.com'],  # Replace with your email or a list of recipients
            )
            return redirect('contact:contact_success')
    else:
        form = ContactForm()

    return render(request, 'contact/contact.html', {'form': form})

def contact_success(request):
    return render(request, 'contact/contact_success.html')
