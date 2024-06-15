# forms.py

from django import forms
from .models import DeliveryAddress
from user.models import Order

class CheckoutForm(forms.Form):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    use_default_shipping = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    use_default_billing = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    same_billing_address = forms.BooleanField(required=False, widget=forms.CheckboxInput())

class GuestCheckoutForm(forms.Form):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    use_default_shipping = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    use_default_billing = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    same_billing_address = forms.BooleanField(required=False, widget=forms.CheckboxInput())

class DeliveryAddressForm(forms.ModelForm):
    class Meta:
        model = DeliveryAddress
        fields = ['address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country', 'phone_number']
        widgets = {
            'address_line1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street address, P.O. box, company name, c/o'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apartment, suite, unit, building, floor, etc.'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State / Province / Region'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ZIP / Postal Code'}),
            'country': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('US', 'United States'),
                ('GB', 'United Kingdom'),
                # Add other countries as needed
            ]),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
        }

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
