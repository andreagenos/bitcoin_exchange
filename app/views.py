from django.shortcuts import render, redirect
from .models import Wallet_Balance, Order, Transaction
from .forms import OrderForm
from django.utils import timezone
from django.db.models import Q
from django.http import HttpResponse


def show_balance(request):
    if request.user.is_authenticated:
        balance = Wallet_Balance.objects.get(user=request.user)
        context = {'balance': balance}
    else:
        context = {}
    return render(request, 'app/home.html', context)
   

def create_order(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid:
            order = form.save(commit=False)
            order.author = request.user
            order.datetime = timezone.now()
            order.total_price = order.btc_unit_price * order.btc_amount
            if order.order_type == 'buy' and order.total_price > order.author.userbalance.usd_balance:
                return HttpResponse("You don't have enough USD for a buy order")
                
            elif order.order_type == 'sell' and order.btc_amount > order.author.userbalance.btc_balance:
                return HttpResponse("You don't have enough BTC for a sell order")
                
            else:
                order.save()
                match_orders(order)
                return redirect('order_list')
    else:
        form = OrderForm()
    return render(request, 'app/create_order.html', {'form': form})


def order_list(request):
    orders = Order.objects.filter(status='open').order_by("-datetime")
    return render(request, 'app/order_list.html', {"orders": orders})


def match_orders(order):
    match = False
    open_orders = Order.objects.filter(status='open').order_by('btc_unit_price').exclude(author=order.author)
    for open_order in open_orders:
        if order.order_type == 'sell' and order.order_type != open_order.order_type and open_order.btc_unit_price >= order.btc_unit_price:
            o = []
            o.append(open_order.btc_unit_price)
            if len(o) == 1: 
                transaction_amount = min(order.btc_amount, open_order.btc_amount)
                profit_loss = (transaction_amount * open_order.btc_unit_price) - (transaction_amount * order.btc_unit_price)
                transaction = Transaction.objects.create(
                    buyer=open_order.author,
                    seller=order.author,
                    btc_amount=transaction_amount,
                    btc_unit_price=order.btc_unit_price,
                    total_price = order.total_price,
                    profit_loss = profit_loss
                ) 

                #update wallet
                order.author.userbalance.btc_balance -= transaction.btc_amount
                order.author.userbalance.usd_balance += transaction.total_price
                order.author.userbalance.save()
                open_order.author.userbalance.btc_balance += transaction.btc_amount
                open_order.author.userbalance.usd_balance -= transaction.total_price
                open_order.author.userbalance.save()

                #update status
                order.btc_amount -= transaction_amount
                open_order.btc_amount -= transaction_amount
                if open_order.btc_amount <= 0:
                    open_order.status = 'closed'
                open_order.save()
                if order.btc_amount <= 0:
                    order.status = 'closed'
                    order.save()
                    match = True
                    break
                else:
                    match_orders(order)
                    break
        
        elif order.order_type == 'buy' and order.order_type != open_order.order_type and order.btc_unit_price >= open_order.btc_unit_price:
            a = []
            a.append(open_order.btc_unit_price)
            if len(a) == 1: 
                transaction_amount = min(order.btc_amount, open_order.btc_amount)
                profit_loss = (transaction_amount * order.btc_unit_price) - (transaction_amount * open_order.btc_unit_price)
                transaction = Transaction.objects.create(
                    buyer=order.author,
                    seller=open_order.author,
                    btc_amount=transaction_amount,
                    btc_unit_price=open_order.btc_unit_price,
                    total_price = open_order.total_price,
                    profit_loss = profit_loss
                )

                #update wallet
                order.author.userbalance.btc_balance += transaction.btc_amount
                order.author.userbalance.usd_balance -= transaction.total_price
                order.author.userbalance.save()
                open_order.author.userbalance.btc_balance -= transaction.btc_amount
                open_order.author.userbalance.usd_balance += transaction.total_price
                open_order.author.userbalance.save()

                #update status
                order.btc_amount -= transaction_amount
                open_order.btc_amount -= transaction_amount
                if open_order.btc_amount <= 0:
                    open_order.status = 'closed' 
                open_order.save()
                if order.btc_amount <= 0:
                    order.status = 'closed'
                    order.save()
                    match = True
                    break
                else:
                    match_orders(order)
                    break
    return match

def transaction_list(request):
    t_list = Transaction.objects.filter(Q(buyer=request.user) | Q(seller=request.user)).order_by('-datetime')
    return render(request, 'app/transaction_list.html', {'t_list': t_list})


    
                