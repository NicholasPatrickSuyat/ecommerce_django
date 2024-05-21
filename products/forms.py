from django import forms
from .models import Products

class ProductsForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ['title', 'image', 'description', 'price']