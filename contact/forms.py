from django import forms
from .models import ContactMessage

class ContactMessageForm(forms.ModelForm):
    class meta:
        model = ContactMessage
        fields = ['name', 'email', 'message', 'phone']

    phone = forms.CharField(max_length=15, required=False)
    