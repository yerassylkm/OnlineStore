"""
Forms for checkout (order creation).
"""
from django import forms


class CheckoutForm(forms.Form):
    full_name = forms.CharField(
        max_length=200,
        label="ФИО",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    address = forms.CharField(
        label="Адрес доставки",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    )
    delivery_time = forms.CharField(
        max_length=100,
        required=False,
        label="Желаемое время доставки",
        help_text="Например: 14:00–18:00",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
