from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    """Form for collecting shipping information during checkout."""
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CartAddProductForm(forms.Form):
    """Form for adding products to the cart with quantity selection."""
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'value': 1})
    )
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)