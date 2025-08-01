from django.urls import path
from . import views

urlpatterns = [
    path('', views.create_wallet, name='create_wallet'),      
    path('transfer/', views.transfer_money, name='transfer'),       
    path('deposit/', views.deposit_money, name='deposit'),           
    path('withdraw/', views.withdraw_money, name='withdraw'),        
    path('transactions/', views.transactions_history, name='transactions_history'),
]
