from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    order_type = forms.ChoiceField(choices=(('buy', 'buy'), ('sell', 'sell')), required=True)
    btc_amount = forms.FloatField(required=True)
    btc_unit_price = forms.FloatField(required=True)

    class Meta:
        model = Order
        fields = ('order_type', 'btc_amount','btc_unit_price')
