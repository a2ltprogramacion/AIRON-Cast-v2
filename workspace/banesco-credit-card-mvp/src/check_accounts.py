import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banesco_project.settings')
django.setup()

from banesco_tracker.models import BankAccount, CreditCard

print("=== BANK ACCOUNTS IN DB ===")
for acc in BankAccount.objects.all():
    print(f"ID: {acc.id} | Name: {acc.name} | Number: {acc.account_number} | Last Four: {acc.last_four} | Initial: {acc.initial_balance} | Balance: {acc.current_balance}")
    for card in acc.cards.all():
        print(f"  Associated Card: {card.name} (*{card.last_four})")
