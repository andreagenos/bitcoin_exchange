from django.contrib import admin
from .models import Wallet_Balance, Order, Transaction

# Register your models here.
admin.site.register(Wallet_Balance)
admin.site.register(Order)
admin.site.register(Transaction)