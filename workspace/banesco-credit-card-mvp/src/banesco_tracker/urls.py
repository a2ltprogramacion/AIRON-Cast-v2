from django.urls import path
from .views import (
    DashboardView, PasteBoxView, ExchangeRateAdjustView,
    CreditCardListView, CreditCardUpdateView, CreditCardDeleteView,
    ManualPaymentView, PagoMovilAsistidoView,
    BankAccountCreateView, BankAccountUpdateView, BankAccountDeleteView,
    TransactionDeleteView, BankAccountTransactionDeleteView,
    ManualEntryView,
)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('paste-box/', PasteBoxView.as_view(), name='paste_box'),
    path('rates/', ExchangeRateAdjustView.as_view(), name='rates'),
    path('cards/', CreditCardListView.as_view(), name='card_list'),
    path('cards/<int:pk>/edit/', CreditCardUpdateView.as_view(), name='card_edit'),
    path('cards/<int:pk>/delete/', CreditCardDeleteView.as_view(), name='card_delete'),
    path('accounts/create/', BankAccountCreateView.as_view(), name='account_create'),
    path('accounts/<int:pk>/edit/', BankAccountUpdateView.as_view(), name='account_edit'),
    path('accounts/<int:pk>/delete/', BankAccountDeleteView.as_view(), name='account_delete'),
    path('manual-payment/', ManualPaymentView.as_view(), name='manual_payment'),
    path('pago-movil/', PagoMovilAsistidoView.as_view(), name='pago_movil'),
    path('manual-entry/', ManualEntryView.as_view(), name='manual_entry'),
    path('transactions/<int:pk>/delete/', TransactionDeleteView.as_view(), name='transaction_delete'),
    path('bank-transactions/<int:pk>/delete/', BankAccountTransactionDeleteView.as_view(), name='bank_transaction_delete'),
]


