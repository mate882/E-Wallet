from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Wallet, Transaction

from django.db import transaction
from Users.models import CustomUser

from django.db import models

from decimal import Decimal, InvalidOperation



@login_required
def create_wallet(request):
    if hasattr(request.user, 'wallet'):
        messages.info(request, "You already have a wallet.")
        return redirect("home")  

    if request.method == "POST":
        Wallet.objects.create(user=request.user)
        messages.success(request, "Your wallet has been created!")
        return redirect("home")

    return render(request, "wallet/create_wallet.html")


@login_required
@transaction.atomic
def transfer_money(request):
    if not hasattr(request.user, 'wallet'):
        return redirect('create_wallet')

    if request.method == "POST":
        recipient_username = request.POST.get("recipient")
        amount_str = request.POST.get("amount")

        try:
            amount = Decimal(amount_str)
        except (InvalidOperation, TypeError):
            messages.error(request, "Invalid amount")
            return redirect('transfer')

        recipient = CustomUser.objects.filter(email=recipient_username).first()
        if not recipient:
            messages.error(request, "Recipient not found")
            return redirect('transfer')

        if not hasattr(recipient, 'wallet'):
            messages.error(request, "Recipient does not have a wallet")
            return redirect('transfer')

        sender_wallet = request.user.wallet
        recipient_wallet = recipient.wallet

        if sender_wallet.balance < amount:
            messages.error(request, "Insufficient funds")
            return redirect('transfer')
        if amount <= 0:
            messages.error(request, "Transfer amount must be greater than 0.")
            return redirect('transfer')

        if not sender_wallet or not recipient_wallet:
            messages.error(request, "Wallet not found.")
            return redirect('transfer')

        sender_wallet.balance -= amount
        recipient_wallet.balance += amount
        sender_wallet.save()
        recipient_wallet.save()

        Transaction.objects.create(
            sender=request.user, receiver=recipient,
            amount=amount, transaction_type="transfer"
        )

        messages.success(request, "Transfer successful!")

    return render(request, 'wallet/transfer.html')


@login_required
def deposit_money(request):
    if not hasattr(request.user, 'wallet'):
        return redirect('create_wallet')

    if request.method == "POST":
        amount_str = request.POST.get("amount")

        try:
            amount = Decimal(amount_str)
        except:
            messages.error(request, "Invalid amount")
            return redirect('deposit')
        
        if amount <= 0:
            messages.error(request, "Deposit amount must be greater than 0.")
            return redirect('deposit')

        wallet = request.user.wallet
        wallet.balance += amount
        wallet.save()

        Transaction.objects.create(
            receiver=request.user, amount=amount, transaction_type="deposit"
        )
        messages.success(request, f"${amount} deposited successfully!")

    return render(request, 'wallet/deposit.html')


@login_required
def withdraw_money(request):
    if not hasattr(request.user, 'wallet'):
        return redirect('create_wallet')

    if request.method == "POST":
        amount_str = request.POST.get("amount")

        try:
            amount = Decimal(amount_str)
        except (InvalidOperation, TypeError):
            messages.error(request, "Invalid amount")
            return redirect('withdraw')

        wallet = request.user.wallet
        if wallet.balance < amount:
            messages.error(request, "Insufficient balance")
            return redirect('withdraw')


        wallet.balance -= amount
        wallet.save()

        Transaction.objects.create(
            sender=request.user, amount=amount, transaction_type="withdraw"
        )
        messages.success(request, f"${amount} withdrawn successfully!")

    return render(request, 'wallet/withdraw.html')

@login_required
def transactions_history(request):
    if not hasattr(request.user, 'wallet'):
        return redirect('create_wallet')

    transactions = Transaction.objects.filter(
        models.Q(sender=request.user) | models.Q(receiver=request.user)
    ).order_by('-timestamp')

    return render(request, 'wallet/transactions_history.html', {"transactions": transactions})
