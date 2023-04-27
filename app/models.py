from djongo import models
from django.contrib.auth.models import User
import random
from django.db.models.signals import post_save
from django.dispatch import receiver
from djongo.models.fields import ObjectIdField
from bson.objectid import ObjectId
from django.utils import timezone

class Wallet_Balance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name= 'userbalance', primary_key=True)
    btc_balance = models.FloatField()
    usd_balance = models.FloatField()

    def save(self, *args, **kwargs):
        if self.btc_balance is None:
            self.btc_balance = round(random.uniform(1, 10), 3)
        if self.usd_balance is None:
            self.usd_balance = round(10000, 2)
        super(Wallet_Balance, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.user)

@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet_Balance.objects.create(user=instance)

class Order(models.Model):
    _id = models.ObjectIdField(primary_key=True, default= ObjectId)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField(blank=True, null=True)
    order_type = models.CharField(max_length=4, choices=(("buy", "buy"), ("sell", "sell")), default='')
    status = models.CharField(max_length=10, choices=(("open", "open"), ("closed", "closed")), default='open')
    btc_amount = models.FloatField()
    btc_unit_price = models.FloatField()
    total_price = models.FloatField()
    
    def save(self, *args, **kwargs):
        self.btc_amount = round(self.btc_amount, 2)
        self.btc_unit_price = round(self.btc_unit_price, 2)
        self.total_price = round(self.total_price, 2)
        super(Order, self).save(*args, **kwargs)
    

class Transaction(models.Model):
    _id = ObjectIdField()
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller')
    btc_amount = models.FloatField()
    btc_unit_price = models.FloatField()
    total_price = models.FloatField()
    profit_loss = models.FloatField()
    datetime = models.DateTimeField(default=timezone.now)

    
    def save(self, *args, **kwargs):
        self.total_price = self.btc_amount * self.btc_unit_price
        self.btc_amount = round(self.btc_amount, 2)
        self.btc_unit_price = round(self.btc_unit_price, 2)
        self.total_price = round(self.total_price, 2)
        super(Transaction, self).save(*args, **kwargs)