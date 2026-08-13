import datetime
from decimal import Decimal
import re
from django.utils import timezone
from django.db.models import Sum
from .models import BankAccount, BankAccountTransaction, CreditCard, Transaction, ExchangeRateLog, TransactionReconciliation
from .services import ensure_exchange_rate

class ReconciliationEngine:
    """
    Motor inteligente de reconciliación financiera para Banesco.
    Cruza los movimientos del estado de cuenta de la cuenta bancaria con
    los consumos de tarjetas y transferencias registrados por correo o manualmente.
    Usa la tabla intermedia TransactionReconciliation (Muchos a Muchos).
    """

    @classmethod
    def reconcile_account(cls, account):
        """
        Ejecuta las reglas de conciliación inteligente sobre todas las transacciones
        no conciliadas de una cuenta bancaria específica.
        """
        # Obtener todas las transacciones de cuenta bancaria que no están conciliadas
        unreconciled = []
        for tx in account.transactions.all():
            reconciled_sum = tx.reconciliations.aggregate(total=Sum('reconciled_amount'))['total'] or Decimal("0.00")
            if reconciled_sum < abs(tx.amount_ves):
                tx.remaining_to_reconcile = abs(tx.amount_ves) - reconciled_sum
                unreconciled.append(tx)

        reconciled_count = 0

        # Obtener las tarjetas de crédito y débito asociadas a la cuenta
        associated_cards = account.cards.all()
        debit_card = associated_cards.filter(cutoff_day__isnull=True).first()
        credit_cards = associated_cards.filter(cutoff_day__isnull=False)

        for bank_tx in unreconciled:
            # 1. Detectar si es una compra por Punto de Venta (Consumo de Tarjeta de Débito - TDD)
            # En Banesco se muestra como "COMPRA POS CTA/CTE" o similar
            if "COMPRA POS" in bank_tx.description or "COMPRA POS CTA/CTE" in bank_tx.description:
                if debit_card:
                    # Heurística TDD:
                    # - Monto en bolívares debe ser idéntico (en valor absoluto)
                    # - Fecha de compra muy cercana (+/- 1 día) o igual
                    # - La referencia del banco debe terminar en el Trace del correo
                    abs_amount = abs(bank_tx.amount_ves)
                    date_min = bank_tx.booking_date.date() - datetime.timedelta(days=1)
                    date_max = bank_tx.booking_date.date() + datetime.timedelta(days=1)

                    # Buscar transacción de débito huérfana o parcialmente conciliada en el sistema
                    matching_debit_txs = Transaction.objects.filter(
                        card=debit_card,
                        type='DEBIT',
                        amount_ves=abs_amount,
                        booking_date__date__range=(date_min, date_max)
                    )
                    
                    matching_debit_tx = None
                    for tx in matching_debit_txs:
                        rec_sum = tx.reconciliations.aggregate(total=Sum('reconciled_amount'))['total'] or Decimal("0.00")
                        if rec_sum < abs_amount:
                            matching_debit_tx = tx
                            break

                    # Si hay un match pero queremos confirmar por referencia corta (Trace)
                    # El reference del banco (ej. 40001341428) termina en el Trace del correo (341428)
                    if matching_debit_tx:
                        ref_bank = bank_tx.reference or ""
                        ref_email = matching_debit_tx.reference or ""
                        is_ref_match = False
                        if ref_bank and ref_email:
                            if ref_bank.endswith(ref_email) or ref_email.endswith(ref_bank):
                                is_ref_match = True
                            elif len(ref_bank) >= 5 and len(ref_email) >= 5 and ref_bank[-5:] == ref_email[-5:]:
                                is_ref_match = True
                                
                        if is_ref_match:
                            # Enlazar transacción vía tabla pivot (con get_or_create para seguridad)
                            TransactionReconciliation.objects.get_or_create(
                                bank_transaction=bank_tx,
                                card_transaction=matching_debit_tx,
                                defaults={'reconciled_amount': abs_amount}
                            )
                            reconciled_count += 1
                            continue

                    # Si no existe la transacción de débito en el sistema, la creamos automáticamente
                    # para que el usuario no tenga que registrarla manualmente.
                    # Extraer el comercio/tienda si viene en la descripción del banco
                    # ej: "COMPRA POS CTA/CTE DIST MEGA MARKET JONA" -> "Mega Market Jona"
                    clean_desc = bank_tx.description.replace("COMPRA POS CTA/CTE", "").replace("COMPRA POS", "").strip()
                    if not clean_desc:
                        clean_desc = "Consumo Tarjeta de Débito Banesco"
                    else:
                        clean_desc = f"Consumo Débito: {clean_desc.title()}"

                    # Buscar la tasa de cambio de esa fecha para indexar en USD
                    rate_log = ExchangeRateLog.objects.filter(date=bank_tx.booking_date.date()).first()
                    if not rate_log:
                        # Fallback al día actual o tasa segura
                        rate_log = ensure_exchange_rate(bank_tx.booking_date.date())

                    new_debit_tx = Transaction.objects.create(
                        card=debit_card,
                        type='DEBIT',
                        booking_date=bank_tx.booking_date,
                        description=clean_desc,
                        amount_ves=abs_amount,
                        reference=bank_tx.reference[-6:] if bank_tx.reference else None,
                        status='PAGADO',
                        exchange_rate=rate_log
                    )
                    
                    TransactionReconciliation.objects.get_or_create(
                        bank_transaction=bank_tx,
                        card_transaction=new_debit_tx,
                        defaults={'reconciled_amount': abs_amount}
                    )
                    reconciled_count += 1
                    continue

            # 2. Detectar si es un Pago a una Tarjeta de Crédito (Egreso TDC)
            # En Banesco se muestra como: "PAGO TDC C/C EN CUENTA5467040014854567" o "PAGO HOMEBANKIN"
            elif "PAGO TDC" in bank_tx.description or "PAGO HOMEBANKIN" in bank_tx.description:
                # Intentar mapear la tarjeta usando el prefijo de 8 dígitos de Banesco en la descripción
                target_card = None
                PREFIX_TO_LAST_FOUR = {
                    '54670400': '4567',
                    '49663816': '2048',
                }
                last_four = None
                prefix_found = None
                for pref, lf in PREFIX_TO_LAST_FOUR.items():
                    if pref in bank_tx.description:
                        last_four = lf
                        prefix_found = pref
                        break

                if last_four:
                    target_card = credit_cards.filter(last_four=last_four).first()
                    if not target_card:
                        # Crear la tarjeta automáticamente si no existe para evitar fallbacks incorrectos
                        name = "Visa Crédito Banesco" if prefix_found.startswith('4') else "MasterCard Crédito Banesco"
                        target_card = CreditCard.objects.create(
                            name=f"{name} *{last_four}",
                            last_four=last_four,
                            cutoff_day=12 if prefix_found.startswith('4') else 3,
                            payment_day=8 if prefix_found.startswith('4') else 30,
                            associated_account=account
                        )
                        # Actualizar la lista local de credit_cards
                        credit_cards = account.cards.filter(cutoff_day__isnull=False)

                # Fallback tradicional si no hubo coincidencia por prefijo
                if not target_card:
                    card_last_four = None
                    last_four_match = re.search(r'(\d{4})$', bank_tx.description)
                    if last_four_match:
                        card_last_four = last_four_match.group(1)
                    if card_last_four:
                        target_card = credit_cards.filter(last_four=card_last_four).first()
                        
                # Fallback definitivo a la primera tarjeta si todo lo anterior falla
                if not target_card and credit_cards.exists():
                    target_card = credit_cards.first()


                if target_card:
                    # Monto del abono debe ser negativo en la tarjeta (abono)
                    abono_amount = -abs(bank_tx.amount_ves)
                    
                    date_min = bank_tx.booking_date.date() - datetime.timedelta(days=1)
                    date_max = bank_tx.booking_date.date() + datetime.timedelta(days=1)

                    # Buscar abono existente para evitar duplicados
                    matching_tdc_payments = Transaction.objects.filter(
                        card=target_card,
                        type='TDC',
                        amount_ves=abono_amount,
                        booking_date__date__range=(date_min, date_max)
                    )
                    
                    matching_tdc_payment = None
                    for tx in matching_tdc_payments:
                        rec_sum = tx.reconciliations.aggregate(total=Sum('reconciled_amount'))['total'] or Decimal("0.00")
                        if rec_sum < abs(abono_amount):
                            matching_tdc_payment = tx
                            break

                    if matching_tdc_payment:
                        TransactionReconciliation.objects.create(
                            bank_transaction=bank_tx,
                            card_transaction=matching_tdc_payment,
                            reconciled_amount=abs(abono_amount)
                        )
                        reconciled_count += 1
                    else:
                        # Si no existe, creamos automáticamente el abono (transacción con monto negativo en TDC)
                        rate_log = ExchangeRateLog.objects.filter(date=bank_tx.booking_date.date()).first()
                        if not rate_log:
                            rate_log = ensure_exchange_rate(bank_tx.booking_date.date())

                        new_abono = Transaction.objects.create(
                            card=target_card,
                            type='TDC',
                            booking_date=bank_tx.booking_date,
                            description=f"Abono Pago desde Cuenta Banesco (*{account.last_four})",
                            amount_ves=abono_amount,
                            reference=bank_tx.reference[-6:] if bank_tx.reference else None,
                            status='PAGADO',
                            exchange_rate=rate_log
                        )
                        
                        TransactionReconciliation.objects.create(
                            bank_transaction=bank_tx,
                            card_transaction=new_abono,
                            reconciled_amount=abs(abono_amount)
                        )
                        reconciled_count += 1
                    continue

            # 3. Conciliar Transferencias / Pagos Móviles registrados previamente mediante PDF o Correo
            # Estos movimientos se identifican directamente por su número de referencia único
            else:
                # Buscar si existe una transacción de tipo 'DEBIT' o 'TDC' (o una general en el futuro)
                # con el mismo número de referencia único
                matching_txs = Transaction.objects.filter(
                    reference=bank_tx.reference
                )
                matching_tx = None
                for tx in matching_txs:
                    rec_sum = tx.reconciliations.aggregate(total=Sum('reconciled_amount'))['total'] or Decimal("0.00")
                    if rec_sum < abs(tx.amount_ves):
                        matching_tx = tx
                        break

                if matching_tx:
                    TransactionReconciliation.objects.create(
                        bank_transaction=bank_tx,
                        card_transaction=matching_tx,
                        reconciled_amount=abs(matching_tx.amount_ves)
                    )
                    # Enriquecer descripción
                    if matching_tx.description and matching_tx.description != "Consumo Tarjeta de Débito Banesco":
                        bank_tx.description = f"{bank_tx.description} ({matching_tx.description})"
                    bank_tx.save()
                    reconciled_count += 1
                    continue

        # Al finalizar la conciliación de movimientos de banco, forzar la re-evaluación
        # de cupos y apalancamientos en todas las tarjetas de crédito
        Transaction.update_statuses(timezone.localdate())

        return reconciled_count
