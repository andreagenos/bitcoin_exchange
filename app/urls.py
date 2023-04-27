from django.urls import path
from . import views

urlpatterns = [
    path('', views.show_balance, name= 'show_balance'),
    path('create_order/', views.create_order, name= 'create_order'),
    path('order_list/', views.order_list, name = 'order_list'),
    path('transaction_list/', views.transaction_list, name= 'transaction_list')
]