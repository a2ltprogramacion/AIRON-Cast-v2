from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from decimal import Decimal
import datetime
import pytz
from .models import CreditCard, ExchangeRateLog, Transaction, BankAccount, BankAccountTransaction, TransactionReconciliation
from .services import ensure_exchange_rate
from .parser import (
    BanescoEmailParser, parse_banesco_txt_report,
    parse_banesco_bank_statement, extract_banesco_pdf_receipt,
    parse_banesco_transfer_text
)
from .reconciliation import ReconciliationEngine


class DashboardView(View):
    """
    Vista principal que renderiza el balance, simulador de apalancamiento,
    semáforos de alerta y listado general de transacciones, junto con
    el estado consolidado y liquidez de la Cuenta Corriente Banesco.
    """
    def get(self, request):
        today = timezone.localdate()
        
        # Actualizar dinámicamente el estado de transacciones PENDIENTES cuya fecha de corte ya pasó
        Transaction.update_statuses(today)
        
        cards = CreditCard.objects.all()
        
        # NO inyectar tarjetas placeholder — los 4 dígitos deben coincidir con los TXT reales del banco.
        # Las tarjetas se crean automáticamente al importar archivos.

        # Obtener todas las cuentas bancarias
        bank_accounts = BankAccount.objects.all()
        if not bank_accounts.exists():
            bank_account = BankAccount.objects.create(
                name="Cuenta Corriente Banesco",
                account_number="01340000000000000000",
                last_four="0000",
                initial_balance=Decimal("0.00"),
                account_type='current'
            )
            bank_accounts = BankAccount.objects.all()
            
        # Recuperar la cuenta seleccionada
        account_id = request.GET.get("account_id", "").strip()
        bank_account = None
        if account_id:
            bank_account = BankAccount.objects.filter(id=account_id).first()
        if not bank_account:
            bank_account = bank_accounts.first()

        # Asociar automáticamente tarjetas a esta cuenta bancaria si no tienen asociación
        for card in cards:
            if not card.associated_account:
                card.associated_account = bank_account
                card.save(update_fields=['associated_account'])

        card_summaries = []
        for card in cards:
            # Calcular balance pendiente (PENDIENTE y CORTADO_NO_PAGADO)
            unpaid_transactions = card.transactions.filter(status__in=['PENDIENTE', 'CORTADO_NO_PAGADO'])

            # Calcular balance pendiente (para TDC se usa previous_balance + suma neta total, para TDD consumos pendientes)
            if card.cutoff_day is not None:
                balance_ves = card.previous_balance + sum(t.amount_ves for t in card.transactions.all())
                transactions_to_sum = card.transactions.all()
            else:
                balance_ves = card.previous_balance + sum(t.amount_ves for t in unpaid_transactions)
                transactions_to_sum = unpaid_transactions
            
            # Calcular el balance indexado a dólares (BCV y Binance)
            # Siempre usar balance_ves directo / tasa_actual (no iterar transactions)
            latest_rate = ExchangeRateLog.objects.order_by('-date').first()
            bcv_r = latest_rate.bcv_rate if latest_rate else Decimal("36.50")
            bin_r = latest_rate.binance_rate if (latest_rate and latest_rate.binance_rate) else bcv_r
            if balance_ves > 0:
                balance_usd_bcv = balance_ves / bcv_r
                balance_usd_binance = balance_ves / bin_r
            else:
                balance_usd_bcv = Decimal("0.00")
                balance_usd_binance = Decimal("0.00")

            # Calcular intereses ordinarios y de mora acumulados de consumos no pagados (monto > 0)
            total_ordinary_interest = sum(t.calculate_projected_interest() for t in unpaid_transactions if t.amount_ves > 0)
            total_mora_interest = sum(t.calculate_mora_interest(today) for t in unpaid_transactions if t.amount_ves > 0)
            total_financial_cost = total_ordinary_interest + total_mora_interest

            # Calcular Pago Mínimo: % del saldo + intereses ordinarios del período
            min_payment_rate = card.minimum_payment_rate or Decimal("4.20")
            minimum_payment = (balance_ves * (min_payment_rate / Decimal("100.00"))) + total_ordinary_interest
            minimum_payment = minimum_payment.quantize(Decimal("0.01"))
            
            # Calcular porcentaje de uso del límite
            credit_use_percent = 0.0
            if card.credit_limit > 0:
                credit_use_percent = float(((card.credit_limit - card.available_limit) / card.credit_limit) * 100)
                credit_use_percent = max(0.0, min(100.0, credit_use_percent))
                
            # Simulación de apalancamiento para hoy
            simulation = card.get_financing_simulation(today)
            
            # Semáforo de alerta de cobro para deuda cortada
            payment_alert_color = "green"
            days_to_pay = None
            next_payment_date = None
            next_cutoff_date = None
            
            if card.cutoff_day is not None:
                # Determinar próximas fechas basadas en simulación
                next_cutoff_date = simulation["cutoff_date"]
                next_payment_date = simulation["payment_date"]
                
                # Si hay deudas por pagar, verificar la fecha límite de pago real más próxima
                due_transactions = card.transactions.filter(status='CORTADO_NO_PAGADO')
                if due_transactions.exists():
                    # Usar la fecha de pago de la transacción más antigua sin pagar
                    oldest_due = due_transactions.order_by('booking_date').first()
                    next_payment_date = oldest_due.fecha_limite_pago
                
                if next_payment_date:
                    days_to_pay = (next_payment_date - today).days
                    if days_to_pay < 2:
                        payment_alert_color = "red"
                    elif days_to_pay < 5:
                        payment_alert_color = "yellow"

            card_summaries.append({
                "card": card,
                "balance_ves": balance_ves,
                "balance_usd_bcv": balance_usd_bcv,
                "balance_usd_binance": balance_usd_binance,
                "total_projected_interest": total_mora_interest,  # Mantiene compatibilidad con la variable de mora anterior
                "total_ordinary_interest": total_ordinary_interest,
                "total_mora_interest": total_mora_interest,
                "total_financial_cost": total_financial_cost,
                "minimum_payment": minimum_payment,
                "credit_use_percent": credit_use_percent,
                "available_limit_discrepancy": card.available_limit_discrepancy if card.cutoff_day else Decimal("0.00"),
                "simulation": simulation,
                "next_cutoff_date": next_cutoff_date,
                "next_payment_date": next_payment_date,
                "days_to_pay": days_to_pay,
                "payment_alert_color": payment_alert_color,
            })
            
        # Calcular Deuda Consolidada total de todas las tarjetas de crédito (TDC)
        total_tdc_debt = Decimal("0.00")
        total_tdc_debt_usd_bcv = Decimal("0.00")
        total_tdc_debt_usd_binance = Decimal("0.00")
        
        credit_cards = cards.filter(cutoff_day__isnull=False)
        for card in credit_cards:
            card_debt = card.previous_balance + sum(t.amount_ves for t in card.transactions.all())
            total_tdc_debt += card_debt
            for t in card.transactions.all():
                if t.exchange_rate:
                    bcv_r = t.exchange_rate.bcv_rate or Decimal("1.00")
                    bin_r = t.exchange_rate.binance_rate or bcv_r or Decimal("1.00")
                    total_tdc_debt_usd_bcv += t.amount_ves / bcv_r
                    total_tdc_debt_usd_binance += t.amount_ves / bin_r
                else:
                    rate_log = ExchangeRateLog.objects.filter(date=t.booking_date.date()).first()
                    bcv_r = rate_log.bcv_rate if rate_log else Decimal("36.50")
                    bin_r = rate_log.binance_rate if (rate_log and rate_log.binance_rate) else bcv_r
                    total_tdc_debt_usd_bcv += t.amount_ves / bcv_r
                    total_tdc_debt_usd_binance += t.amount_ves / bin_r

        # Obtener tasa de cambio más reciente para la indexación de liquidez de cuenta bancaria
        latest_rate_log = ExchangeRateLog.objects.order_by('-date').first()
        bcv_rate = latest_rate_log.bcv_rate if latest_rate_log else Decimal("36.50")
        binance_rate = (latest_rate_log.binance_rate if latest_rate_log else None) or bcv_rate
        
        bank_balance_ves = bank_account.current_balance
        bank_projected_balance_ves = bank_account.projected_balance
        
        bank_balance_usd_bcv = (bank_balance_ves / bcv_rate).quantize(Decimal("0.01"))
        bank_balance_usd_binance = (bank_balance_ves / binance_rate).quantize(Decimal("0.01"))
        
        bank_projected_balance_usd_bcv = (bank_projected_balance_ves / bcv_rate).quantize(Decimal("0.01"))
        bank_projected_balance_usd_binance = (bank_projected_balance_ves / binance_rate).quantize(Decimal("0.01"))
        
        # ── FILTROS Y BÚSQUEDA DEL HISTORIAL ──────────────────────────────────
        search_query = request.GET.get('search', '').strip()
        selected_card_id = request.GET.get('card_id', '').strip()
        date_filter = request.GET.get('date', '').strip()
        active_tab = request.GET.get('active_tab', 'cards').strip()

        # Query base para Tarjetas
        card_txs = Transaction.objects.all().order_by('-booking_date')
        if search_query:
            card_txs = card_txs.filter(
                Q(description__icontains=search_query) |
                Q(reference__icontains=search_query) |
                Q(amount_ves__icontains=search_query)
            )
        if selected_card_id:
            card_txs = card_txs.filter(card_id=selected_card_id)
        if date_filter:
            try:
                card_txs = card_txs.filter(booking_date__date=date_filter)
            except Exception:
                pass

        # Query base para Banco
        bank_txs = bank_account.transactions.all().order_by('-booking_date')
        if search_query:
            bank_txs = bank_txs.filter(
                Q(description__icontains=search_query) |
                Q(reference__icontains=search_query) |
                Q(amount_ves__icontains=search_query)
            )
        if date_filter:
            try:
                bank_txs = bank_txs.filter(booking_date__date=date_filter)
            except Exception:
                pass

        # ── PAGINACIÓN ────────────────────────────────────────────────────────
        from django.core.paginator import Paginator
        
        # Paginador Tarjetas
        paginator_cards = Paginator(card_txs, 10)
        page_cards = request.GET.get('page_cards', '1')
        transactions_page = paginator_cards.get_page(page_cards)

        # Paginador Banco
        paginator_bank = Paginator(bank_txs, 10)
        page_bank = request.GET.get('page_bank', '1')
        bank_transactions_page = paginator_bank.get_page(page_bank)
        
        context = {
            "card_summaries": card_summaries,
            "transactions": transactions_page,
            "bank_account": bank_account,
            "bank_accounts": bank_accounts,
            "bank_balance_ves": bank_balance_ves,
            "bank_projected_balance_ves": bank_projected_balance_ves,
            "bank_balance_usd_bcv": bank_balance_usd_bcv,
            "bank_balance_usd_binance": bank_balance_usd_binance,
            "bank_projected_balance_usd_bcv": bank_projected_balance_usd_bcv,
            "bank_projected_balance_usd_binance": bank_projected_balance_usd_binance,
            "bank_transactions": bank_transactions_page,
            "latest_rate_log": latest_rate_log,
            "today": today,
            # Nuevos campos de Deuda Consolidada
            "total_tdc_debt": total_tdc_debt,
            "total_tdc_debt_usd_bcv": total_tdc_debt_usd_bcv,
            "total_tdc_debt_usd_binance": total_tdc_debt_usd_binance,
            # Nuevos campos de filtro y paginación
            "all_cards": cards,
            "search_query": search_query,
            "selected_card_id": selected_card_id,
            "date_filter": date_filter,
            "active_tab": active_tab,
        }
        return render(request, "banesco_tracker/dashboard.html", context)


class PasteBoxView(View):
    """
    Formulario Paste Box para copiar y pegar el texto del correo
    de notificaciones diarias de Banesco y procesarlo en lote.
    """
    def get(self, request):
        cards = CreditCard.objects.filter(cutoff_day__isnull=False)  # Solo TDC para pagos
        bank_accounts = BankAccount.objects.all()
        return render(request, "banesco_tracker/paste_box.html", {"cards": cards, "bank_accounts": bank_accounts})
        
    def post(self, request):
        email_text = request.POST.get("email_text", "")
        report_file = request.FILES.get("report_file")
        bank_account_id = request.POST.get("bank_account_id", "").strip()
        
        parsed_txs = []
        is_report = False
        is_pdf = False
        is_bank_statement = False
        
        # Buscar cuenta bancaria seleccionada o principal
        bank_account = None
        if bank_account_id:
            bank_account = BankAccount.objects.filter(id=bank_account_id).first()
        if not bank_account:
            bank_account = BankAccount.objects.first()
            
        if not bank_account:
            bank_account = BankAccount.objects.create(
                name="Cuenta Corriente Banesco",
                account_number="01340000000000000000",
                last_four="0000",
                initial_balance=Decimal("0.00"),
                account_type='current'
            )
            
        # 1. Determinar el origen de la ingesta (Archivo o Texto)
        if report_file:
            is_report = True
            filename = report_file.name.lower()
            
            # Caso PDF: Recibo de transferencia
            if filename.endswith('.pdf'):
                is_pdf = True
                try:
                    file_bytes = report_file.read()
                    pdf_data = extract_banesco_pdf_receipt(file_bytes)
                    if pdf_data:
                        parsed_txs = [pdf_data]
                    else:
                        messages.error(request, "No se pudo extraer información del archivo PDF subido.")
                        return redirect("paste_box")
                except Exception as e:
                    messages.error(request, f"Error al leer el PDF de recibo: {e}")
                    return redirect("paste_box")
                    
            # Caso TXT: Reporte de Tarjeta o Estado de Cuenta Bancaria
            elif filename.endswith('.txt'):
                try:
                    # Intentar decodificar como UTF-8, si falla usar Latin-1
                    try:
                        file_content = report_file.read().decode('utf-8')
                    except UnicodeDecodeError:
                        report_file.seek(0)
                        file_content = report_file.read().decode('latin-1')
                    
                    # Detectar si es un estado de cuenta bancario o un reporte de tarjeta
                    if "Saldo" in file_content and "Referencia" in file_content and "Tarjeta:" not in file_content:
                        is_bank_statement = True
                        
                        # Auto-detectar la cuenta bancaria por coincidencia del número de cuenta en el contenido del archivo
                        normalized_content = file_content.replace("-", "").replace(" ", "")
                        detected_account = None
                        for acc in BankAccount.objects.all():
                            if acc.account_number in normalized_content:
                                detected_account = acc
                                break
                        if detected_account:
                            bank_account = detected_account
                            
                        parsed_txs = parse_banesco_bank_statement(file_content)
                    else:
                        parsed_txs = parse_banesco_txt_report(file_content)
                except Exception as e:
                    messages.error(request, f"Error al procesar el archivo de reporte: {e}")
                    return redirect("paste_box")
            else:
                messages.error(request, "Formato de archivo no soportado. Suba un .txt o un .pdf.")
                return redirect("paste_box")
                
        elif email_text.strip():
            # Puede ser una transferencia o una lista de notificaciones normales
            # Primero intentamos parsear como texto de transferencia
            transfer_data = parse_banesco_transfer_text(email_text)
            if transfer_data:
                parsed_txs = [transfer_data]
                is_pdf = True # Lo tratamos como flujo de recibo/transferencia
            else:
                parsed_txs = BanescoEmailParser.parse_text(email_text)
        else:
            messages.error(request, "Debe pegar texto o subir un archivo (.txt, .pdf).")
            return redirect("paste_box")
            
        if not parsed_txs:
            messages.warning(request, "No se encontraron transacciones válidas para procesar.")
            return redirect("paste_box")
            
        created_count = 0
        duplicate_count = 0
        
        # Procesar según sea un estado de cuenta corriente bancario o transacciones de tarjeta/recibos
        if is_bank_statement:
            # Si el balance inicial es 0.00, podemos deducirlo dinámicamente del primer registro
            if bank_account.initial_balance == Decimal("0.00") and parsed_txs:
                # El reporte está ordenado de forma cronológica ascendente
                first_tx = parsed_txs[0]
                first_amount = first_tx["amount_ves"]
                first_balance = first_tx["balance_ves"]
                # saldo_anterior = saldo_actual - monto (teniendo en cuenta que amount_ves es negativo para egresos y positivo para ingresos)
                bank_account.initial_balance = first_balance - first_amount
                bank_account.save(update_fields=['initial_balance'])
                
            for tx in parsed_txs:
                # Asegurar tasa de cambio
                log = ensure_exchange_rate(tx['booking_date'].date())
                
                ref = tx['reference']
                clean_ref = ref.lstrip('0')
                if not clean_ref:
                    clean_ref = ref
                
                try:
                    # Buscar si ya existe un movimiento bancario con esa referencia (exacta o parcial)
                    existing_tx = BankAccountTransaction.objects.filter(
                        account=bank_account
                    ).filter(
                        Q(reference=ref) | Q(reference__endswith=clean_ref) | Q(reference=clean_ref)
                    ).order_by('-is_manual').first()
                    
                    if existing_tx:
                        if existing_tx.is_manual:
                            # Confirmar y actualizar el movimiento manual
                            existing_tx.is_manual = False
                            existing_tx.booking_date = tx['booking_date']
                            existing_tx.description = tx['description']  # oficial
                            existing_tx.balance_ves = tx['balance_ves']  # saldo oficial
                            existing_tx.reference = ref  # oficial largo
                            existing_tx.exchange_rate = log
                            existing_tx.save()
                            created_count += 1
                        else:
                            duplicate_count += 1
                    else:
                        # Crear uno nuevo oficial
                        BankAccountTransaction.objects.create(
                            account=bank_account,
                            reference=ref,
                            booking_date=tx['booking_date'],
                            description=tx['description'],
                            amount_ves=tx['amount_ves'],
                            balance_ves=tx['balance_ves'],
                            is_manual=False,
                            exchange_rate=log
                        )
                        created_count += 1
                except Exception as e:
                    print(f"[PasteBoxView] Error al guardar movimiento de cuenta: {e}")
                    duplicate_count += 1
            
            # Ejecutar conciliador inteligente
            reconciled = ReconciliationEngine.reconcile_account(bank_account)
            
            if created_count > 0:
                messages.success(
                    request,
                    f"Carga exitosa del Estado de Cuenta Bancario. Se agregaron {created_count} movimientos de cuenta. "
                    f"({reconciled} transacciones conciliadas dinámicamente, {duplicate_count} omitidas por duplicidad)."
                )
            else:
                messages.info(request, f"No se agregaron movimientos nuevos. ({duplicate_count} ya estaban registrados).")
                
        else:
            # Procesar recibo de transferencia (is_pdf o texto de transferencia) o transacciones normales de tarjeta
            debit_card = bank_account.cards.filter(cutoff_day__isnull=True).first()
            if not debit_card:
                debit_card = CreditCard.objects.create(
                    name="Tarjeta de Débito Banesco",
                    last_four="0000",
                    cutoff_day=None,
                    payment_day=None,
                    associated_account=bank_account
                )
                
            for tx in parsed_txs:
                # Si viene de un recibo o transferencia individual
                if is_pdf or tx.get('type') == 'TRANSFER':
                    # Es un egreso de la cuenta bancaria por transferencia (puramente bancario)
                    amount_ves = tx['amount_ves']
                    amount_ves_bank = -abs(amount_ves)
                    
                    # Asegurar tasa de cambio
                    booking_date = tx.get('booking_date') or timezone.now()
                    booking_date_only = booking_date.date() if isinstance(booking_date, datetime.datetime) else booking_date
                    log = ensure_exchange_rate(booking_date_only)
                    
                    clean_ref = tx['reference'].lstrip('0')
                    if not clean_ref:
                        clean_ref = tx['reference']
                        
                    # Validar duplicados en la cuenta
                    exists = BankAccountTransaction.objects.filter(
                        account=bank_account
                    ).filter(
                        Q(reference=tx['reference']) | Q(reference__endswith=clean_ref) | Q(reference=clean_ref)
                    ).exists()
                    
                    if not exists:
                        try:
                            BankAccountTransaction.objects.create(
                                account=bank_account,
                                booking_date=booking_date,
                                reference=tx['reference'],
                                description=tx.get('description') or f"Transferencia a {tx.get('beneficiary', 'Terceros')}",
                                amount_ves=amount_ves_bank,
                                is_manual=True,
                                exchange_rate=log
                            )
                            created_count += 1
                        except Exception as e:
                            print(f"[PasteBoxView] Error al guardar transferencia manual: {e}")
                            duplicate_count += 1
                    else:
                        duplicate_count += 1
                        
                else:
                    # Notificaciones clásicas de TDC o TDD (emails o reporte .txt de tarjeta)
                    last_four = tx['card_last_four']
                    if not last_four:
                        messages.error(request, "Una o más transacciones no están asociadas a un número de tarjeta.")
                        return redirect("paste_box")
                        
                    card = CreditCard.objects.filter(last_four=last_four).first()
                    if not card:
                        if tx.get('type') == 'DEBIT':
                            card = CreditCard.objects.create(
                                name=f"Débito Banesco *{last_four}",
                                last_four=last_four,
                                cutoff_day=None,
                                payment_day=None,
                                associated_account=bank_account
                            )
                        else:
                            card = CreditCard.objects.create(
                                name=f"Visa Crédito Banesco *{last_four}",
                                last_four=last_four,
                                cutoff_day=12,
                                payment_day=8,
                                associated_account=bank_account
                            )
                            
                    log = ensure_exchange_rate(tx['booking_date'].date())
                    
                    amount_ves = tx['amount_ves']
                    description = tx['description']
                    is_payment = tx.get('is_payment', False)
                    if is_payment:
                        amount_ves = -amount_ves
                        if not description.upper().startswith("PAGO"):
                            description = f"PAGO: {description}"
                    
                    # Evitar registrar pagos duplicados si ya existen con el mismo monto y fecha (+/- 1 día)
                    if is_payment:
                        date_min = tx['booking_date'].date() - datetime.timedelta(days=1)
                        date_max = tx['booking_date'].date() + datetime.timedelta(days=1)
                        existing_payment = Transaction.objects.filter(
                            card=card,
                            type='TDC',
                            amount_ves=amount_ves,
                            booking_date__date__range=(date_min, date_max)
                        ).first()
                        if existing_payment:
                            duplicate_count += 1
                            continue

                    
                    # BUG FIX #2: Los archivos TXT del banco no contienen referencia larga.
                    # Generamos un hash sintético único basado en tarjeta+fecha+monto+descripción
                    # para que get_or_create NO use reference=None (que nunca deduplica).
                    import hashlib
                    raw_ref = tx.get('reference')
                    if not raw_ref:
                        hash_key = f"{card.last_four}|{tx['booking_date'].strftime('%Y%m%d')}|{amount_ves}|{description[:30]}"
                        raw_ref = f"TXT-{hashlib.md5(hash_key.encode()).hexdigest()[:12]}"
                            
                    try:
                        tx_obj, created = Transaction.objects.get_or_create(
                            card=card,
                            type=tx.get('type', 'TDC'),
                            booking_date=tx['booking_date'],
                            amount_ves=amount_ves,
                            reference=raw_ref,
                            defaults={
                                'description': description,
                                'exchange_rate': log,
                                'status': 'PENDIENTE'
                            }
                        )
                        if created:
                            created_count += 1
                        else:
                            duplicate_count += 1
                    except Exception as e:
                        print(f"[PasteBoxView] Error al guardar transacción: {e}")
                        duplicate_count += 1
                        
            # Disparar conciliación en la cuenta bancaria
            reconciled = ReconciliationEngine.reconcile_account(bank_account)
            
            if created_count > 0:
                messages.success(
                    request, 
                    f"Ingesta exitosa. Se agregaron {created_count} nuevas transacciones y se conciliaron {reconciled} con la cuenta bancaria. "
                    f"({duplicate_count} omitidas por duplicidad)."
                )
            else:
                messages.info(request, f"No se agregaron transacciones nuevas. ({duplicate_count} ya estaban registradas).")
                
        return redirect("dashboard")




class ExchangeRateAdjustView(View):
    """
    Vista de lista y actualización rápida de tasas de cambio (BCV y Binance).
    """
    def get(self, request):
        logs = ExchangeRateLog.objects.all().order_by('-date')[:30]
        return render(request, "banesco_tracker/rates.html", {"logs": logs})
        
    def post(self, request):
        rate_id = request.POST.get("rate_id")
        bcv_val = request.POST.get("bcv_rate")
        binance_val = request.POST.get("binance_rate")
        
        try:
            log = ExchangeRateLog.objects.get(id=rate_id)
            log.bcv_rate = Decimal(bcv_val)
            if binance_val.strip():
                log.binance_rate = Decimal(binance_val)
            else:
                log.binance_rate = None
            log.save()
            messages.success(request, f"Tasa de cambio para el {log.date.strftime('%d/%m/%Y')} actualizada con éxito.")
        except Exception as e:
            messages.error(request, f"Error al actualizar la tasa: {e}")
            
        return redirect("rates")


class CreditCardListView(View):
    """
    Vista para listar todas las tarjetas y cuentas bancarias,
    permitiendo registrar nuevos elementos de forma manual.
    """
    def get(self, request):
        cards = CreditCard.objects.all()
        bank_accounts = BankAccount.objects.all()
        return render(request, "banesco_tracker/cards.html", {
            "cards": cards,
            "bank_accounts": bank_accounts
        })
        
    def post(self, request):
        name = request.POST.get("name", "").strip()
        last_four = request.POST.get("last_four", "").strip()
        cutoff_day_str = request.POST.get("cutoff_day", "").strip()
        payment_day_str = request.POST.get("payment_day", "").strip()
        card_type_display = request.POST.get("card_type_display", "").strip() or "VISA DORADA"
        theme_color = request.POST.get("theme_color", "").strip() or "gold"
        associated_account_id = request.POST.get("associated_account", "").strip()
        
        # Nuevos campos financieros
        credit_limit_str = request.POST.get("credit_limit", "").strip()
        interest_rate_str = request.POST.get("interest_rate", "").strip()
        mora_rate_str = request.POST.get("mora_rate", "").strip()
        
        if not name or not last_four:
            messages.error(request, "El nombre de la tarjeta y los últimos 4 dígitos son campos obligatorios.")
            return redirect("card_list")
            
        if len(last_four) != 4 or not last_four.isdigit():
            messages.error(request, "El número de terminación debe tener exactamente 4 dígitos numéricos.")
            return redirect("card_list")
            
        cutoff_day = int(cutoff_day_str) if cutoff_day_str else None
        payment_day = int(payment_day_str) if payment_day_str else None
        
        if cutoff_day is None or payment_day is None:
            cutoff_day = None
            payment_day = None
            credit_limit = Decimal("0.00")
            interest_rate = Decimal("0.00")
            mora_rate = Decimal("0.00")
        else:
            credit_limit = Decimal(credit_limit_str) if credit_limit_str else Decimal("0.00")
            interest_rate = Decimal(interest_rate_str) if interest_rate_str else Decimal("60.00")
            mora_rate = Decimal(mora_rate_str) if mora_rate_str else Decimal("3.00")
            
        associated_account = BankAccount.objects.filter(id=associated_account_id).first() if associated_account_id else None
        
        try:
            CreditCard.objects.create(
                name=name,
                last_four=last_four,
                cutoff_day=cutoff_day,
                payment_day=payment_day,
                card_type_display=card_type_display,
                theme_color=theme_color,
                credit_limit=credit_limit,
                interest_rate=interest_rate,
                mora_rate=mora_rate,
                associated_account=associated_account
            )
            messages.success(request, f"Tarjeta '{name}' (*{last_four}) registrada con éxito.")
        except Exception as e:
            messages.error(request, f"Error al registrar la tarjeta: {e}")
            
        return redirect("card_list")


class CreditCardUpdateView(View):
    """
    Vista para editar una tarjeta de crédito o débito existente.
    """
    def get(self, request, pk):
        card = get_object_or_404(CreditCard, pk=pk)
        bank_accounts = BankAccount.objects.all()
        return render(request, "banesco_tracker/card_form.html", {
            "card": card,
            "bank_accounts": bank_accounts
        })
        
    def post(self, request, pk):
        card = get_object_or_404(CreditCard, pk=pk)
        name = request.POST.get("name", "").strip()
        last_four = request.POST.get("last_four", "").strip()
        cutoff_day_str = request.POST.get("cutoff_day", "").strip()
        payment_day_str = request.POST.get("payment_day", "").strip()
        card_type_display = request.POST.get("card_type_display", "").strip() or "VISA DORADA"
        theme_color = request.POST.get("theme_color", "").strip() or "gold"
        associated_account_id = request.POST.get("associated_account", "").strip()
        
        # Nuevos campos financieros
        credit_limit_str = request.POST.get("credit_limit", "").strip()
        interest_rate_str = request.POST.get("interest_rate", "").strip()
        mora_rate_str = request.POST.get("mora_rate", "").strip()
        
        if not name or not last_four:
            messages.error(request, "El nombre de la tarjeta y los últimos 4 dígitos son campos obligatorios.")
            return redirect("card_edit", pk=pk)
            
        if len(last_four) != 4 or not last_four.isdigit():
            messages.error(request, "El número de terminación debe tener exactamente 4 dígitos numéricos.")
            return redirect("card_edit", pk=pk)
            
        cutoff_day = int(cutoff_day_str) if cutoff_day_str else None
        payment_day = int(payment_day_str) if payment_day_str else None
        
        if cutoff_day is None or payment_day is None:
            cutoff_day = None
            payment_day = None
            credit_limit = Decimal("0.00")
            interest_rate = Decimal("0.00")
            mora_rate = Decimal("0.00")
        else:
            credit_limit = Decimal(credit_limit_str) if credit_limit_str else Decimal("0.00")
            interest_rate = Decimal(interest_rate_str) if interest_rate_str else Decimal("60.00")
            mora_rate = Decimal(mora_rate_str) if mora_rate_str else Decimal("3.00")
            
        associated_account = BankAccount.objects.filter(id=associated_account_id).first() if associated_account_id else None
        
        try:
            card.name = name
            card.last_four = last_four
            card.cutoff_day = cutoff_day
            card.payment_day = payment_day
            card.card_type_display = card_type_display
            card.theme_color = theme_color
            card.credit_limit = credit_limit
            card.interest_rate = interest_rate
            card.mora_rate = mora_rate
            card.associated_account = associated_account
            card.save()
            messages.success(request, f"Tarjeta '{name}' (*{last_four}) actualizada con éxito.")
            return redirect("card_list")
        except Exception as e:
            messages.error(request, f"Error al guardar los cambios de la tarjeta: {e}")
            return redirect("card_edit", pk=pk)


class CreditCardDeleteView(View):
    """
    Vista para eliminar una tarjeta (incluyendo cascada de transacciones asociadas).
    """
    def post(self, request, pk):
        card = get_object_or_404(CreditCard, pk=pk)
        card_name = card.name
        card_last_four = card.last_four
        try:
            card.delete()
            messages.success(request, f"Tarjeta '{card_name}' (*{card_last_four}) eliminada con éxito junto con sus transacciones.")
        except Exception as e:
            messages.error(request, f"Error al eliminar la tarjeta: {e}")
            
        return redirect("card_list")


class BankAccountCreateView(View):
    """
    Vista para crear nuevas cuentas bancarias.
    """
    def post(self, request):
        name = request.POST.get("name", "").strip() or "Cuenta Corriente Banesco"
        account_number = request.POST.get("account_number", "").strip()
        initial_balance_str = request.POST.get("initial_balance", "").strip() or "0.00"
        
        if not account_number:
            messages.error(request, "El número de cuenta es obligatorio.")
            return redirect("card_list")
            
        if len(account_number) != 20 or not account_number.isdigit():
            messages.error(request, "El número de cuenta debe tener exactamente 20 dígitos numéricos.")
            return redirect("card_list")
            
        try:
            initial_balance = Decimal(initial_balance_str.replace(",", "."))
        except Exception:
            messages.error(request, "El saldo inicial no es válido.")
            return redirect("card_list")
            
        last_four = account_number[-4:]
        
        try:
            BankAccount.objects.create(
                name=name,
                account_number=account_number,
                last_four=last_four,
                initial_balance=initial_balance
            )
            messages.success(request, f"Cuenta bancaria '{name}' (*{last_four}) registrada con éxito.")
        except Exception as e:
            messages.error(request, f"Error al registrar la cuenta bancaria: {e}")
            
        return redirect("card_list")


class BankAccountUpdateView(View):
    """
    Vista para editar una cuenta bancaria existente.
    """
    def get(self, request, pk):
        account = get_object_or_404(BankAccount, pk=pk)
        return render(request, "banesco_tracker/account_form.html", {"account": account})
        
    def post(self, request, pk):
        account = get_object_or_404(BankAccount, pk=pk)
        name = request.POST.get("name", "").strip() or "Cuenta Corriente Banesco"
        account_number = request.POST.get("account_number", "").strip()
        initial_balance_str = request.POST.get("initial_balance", "").strip() or "0.00"
        
        if not account_number:
            messages.error(request, "El número de cuenta es obligatorio.")
            return render(request, "banesco_tracker/account_form.html", {"account": account})
            
        if len(account_number) != 20 or not account_number.isdigit():
            messages.error(request, "El número de cuenta debe tener exactamente 20 dígitos numéricos.")
            return render(request, "banesco_tracker/account_form.html", {"account": account})
            
        try:
            initial_balance = Decimal(initial_balance_str.replace(",", "."))
        except Exception:
            messages.error(request, "El saldo inicial no es válido.")
            return render(request, "banesco_tracker/account_form.html", {"account": account})
            
        try:
            account.name = name
            account.account_number = account_number
            account.last_four = account_number[-4:]
            account.initial_balance = initial_balance
            account.save()
            messages.success(request, f"Cuenta bancaria '{name}' (*{account.last_four}) actualizada con éxito.")
            return redirect("card_list")
        except Exception as e:
            messages.error(request, f"Error al actualizar la cuenta bancaria: {e}")
            return render(request, "banesco_tracker/account_form.html", {"account": account})


class BankAccountDeleteView(View):
    """
    Vista para eliminar una cuenta bancaria de forma segura.
    """
    def post(self, request, pk):
        account = get_object_or_404(BankAccount, pk=pk)
        name = account.name
        last_four = account.last_four
        try:
            account.delete()
            messages.success(request, f"Cuenta bancaria '{name}' (*{last_four}) eliminada con éxito.")
        except Exception as e:
            messages.error(request, f"Error al eliminar la cuenta bancaria: {e}")
            
        return redirect("card_list")


class ManualPaymentView(View):
    """
    Registra un pago manual para una tarjeta de crédito,
    almacenándolo como una transacción con monto negativo y
    ejecutando la conciliación FIFO de forma inmediata.
    """
    def post(self, request):
        card_id = request.POST.get("card_id")
        booking_date_str = request.POST.get("booking_date")
        amount_ves_str = request.POST.get("amount_ves")
        reference = request.POST.get("reference", "").strip()
        description = request.POST.get("description", "").strip()

        if not card_id or not amount_ves_str:
            messages.error(request, "La tarjeta y el monto son campos obligatorios.")
            return redirect("paste_box")

        card = get_object_or_404(CreditCard, id=card_id)

        try:
            # Parsear monto como positivo, pero guardarlo como negativo (pago)
            amount_ves = Decimal(amount_ves_str)
            if amount_ves <= 0:
                messages.error(request, "El monto del pago debe ser mayor a cero.")
                return redirect("paste_box")
            amount_ves = -amount_ves

            # Parsear fecha
            if booking_date_str:
                booking_date = timezone.make_aware(datetime.datetime.strptime(booking_date_str, "%Y-%m-%dT%H:%M"))
            else:
                booking_date = timezone.now()

            if not description:
                description = f"Pago Manual - Reconciliado FIFO"

            # Asegurar tasa de cambio para la fecha de pago
            log = ensure_exchange_rate(booking_date.date())

            # Crear la transacción de pago (evitando duplicados mediante get_or_create)
            tx, created = Transaction.objects.get_or_create(
                card=card,
                type='TDC',
                booking_date=booking_date,
                amount_ves=amount_ves,
                reference=reference or None,
                defaults={
                    'description': description,
                    'exchange_rate': log,
                    'status': 'PAGADO'  # Los pagos nacen PAGADO
                }
            )

            if created:
                # Disparar la reconciliación FIFO inmediatamente para aplicar el pago a consumos
                Transaction.update_statuses(timezone.localdate())
                messages.success(request, f"Pago manual de Bs. {abs(amount_ves):,.2f} registrado y conciliado con éxito para {card.name}.")
            else:
                messages.info(request, "Este pago manual ya se encuentra registrado.")

        except Exception as e:
            messages.error(request, f"Error al registrar el pago manual: {e}")

        return redirect("dashboard")


class PagoMovilAsistidoView(View):
    """
    Ingesta asistida 'Smart Fast Input' para Pagos Móviles.
    Permite asociar una captura de pantalla (backup) e ingresar Referencia + Monto
    para buscar coincidencias inmediatas en los movimientos bancarios ya cargados,
    o dejarlo registrado a la espera de la carga del estado de cuenta futuro.
    Soporta flujos de Consumos (Egresos) e Ingresos (Cobros recibidos).
    """
    def get(self, request):
        bank_accounts = BankAccount.objects.all()
        return render(request, "banesco_tracker/pago_movil_asistido.html", {"bank_accounts": bank_accounts})
        
    def post(self, request):
        amount_str = request.POST.get("amount_ves", "").strip()
        reference = request.POST.get("reference", "").strip()
        description = request.POST.get("description", "").strip()
        flow_type = request.POST.get("flow_type", "egress").strip()
        bank_account_id = request.POST.get("bank_account_id", "").strip()
        
        if not amount_str or not reference:
            messages.error(request, "Monto y Referencia son campos obligatorios.")
            return redirect("pago_movil")
            
        try:
            amount_ves = Decimal(amount_str.replace(",", "."))
            if amount_ves <= 0:
                messages.error(request, "El monto debe ser mayor a cero.")
                return redirect("pago_movil")
        except Exception:
            messages.error(request, "El monto ingresado no es válido.")
            return redirect("pago_movil")
            
        bank_account = None
        if bank_account_id:
            bank_account = BankAccount.objects.filter(id=bank_account_id).first()
        if not bank_account:
            bank_account = BankAccount.objects.first()
            
        if not bank_account:
            bank_account = BankAccount.objects.create(
                name="Cuenta Corriente Banesco",
                account_number="01340000000000000000",
                last_four="0000",
                initial_balance=Decimal("0.00"),
                account_type='current'
            )
            
        debit_card = bank_account.cards.filter(cutoff_day__isnull=True).first()
        if not debit_card:
            debit_card = CreditCard.objects.create(
                name="Tarjeta de Débito Banesco",
                last_four="0000",
                cutoff_day=None,
                payment_day=None,
                associated_account=bank_account
            )
            
        clean_ref = reference.lstrip('0')
        if not clean_ref:
            clean_ref = reference

        # Validar duplicados en la cuenta bancaria antes de crear nuevos registros
        exists = BankAccountTransaction.objects.filter(
            account=bank_account
        ).filter(
            Q(reference=reference) | Q(reference__endswith=clean_ref) | Q(reference=clean_ref)
        ).exists()

        if exists:
            messages.warning(
                request,
                f"El Pago Móvil con referencia {reference} ya se encuentra registrado."
            )
            return redirect("dashboard")

        # Configurar tasa y fecha
        booking_date = timezone.now()
        log = ensure_exchange_rate(booking_date.date())

        final_desc = description or ("Pago Móvil Enviado" if flow_type == "egress" else "Pago Móvil Recibido")
        amount = -amount_ves if flow_type == "egress" else amount_ves

        try:
            BankAccountTransaction.objects.create(
                account=bank_account,
                booking_date=booking_date,
                reference=reference,
                description=final_desc,
                amount_ves=amount,
                is_manual=True,
                exchange_rate=log
            )
            
            messages.success(
                request,
                f"¡Pago Móvil registrado con éxito! Se creó el movimiento en cuenta de Bs. {amount_ves:,.2f} (Ref: {reference}). "
                f"Pendiente de verificación bancaria."
            )
            
            # Forzar actualización de estados
            Transaction.update_statuses(timezone.localdate())

        except Exception as e:
            messages.error(request, f"Error al procesar el Pago Móvil: {e}")

        return redirect("dashboard")


class TransactionDeleteView(View):
    """
    Vista para eliminar una transacción de tarjeta de crédito/débito manualmente.
    """
    def post(self, request, pk):
        tx = get_object_or_404(Transaction, pk=pk)
        desc = tx.description
        amount = tx.amount_ves
        try:
            tx.delete()
            messages.success(request, f"Transacción '{desc}' por Bs. {amount:,.2f} eliminada con éxito.")
        except Exception as e:
            messages.error(request, f"Error al eliminar la transacción: {e}")
        return redirect("dashboard")


class BankAccountTransactionDeleteView(View):
    """
    Vista para eliminar un movimiento de cuenta bancaria manualmente.
    """
    def post(self, request, pk):
        tx = get_object_or_404(BankAccountTransaction, pk=pk)
        desc = tx.description
        amount = tx.amount_ves
        try:
            tx.delete()
            messages.success(request, f"Movimiento bancario '{desc}' por Bs. {amount:,.2f} eliminado con éxito.")
        except Exception as e:
            messages.error(request, f"Error al eliminar el movimiento bancario: {e}")
        return redirect("dashboard")


class ManualEntryView(View):
    """
    Registro Manual Universal.
    Soporta 4 modos via el campo `entry_mode`:
      - tdc_charge   : Consumo en tarjeta de crédito (TDC)
      - tdc_payment  : Pago/abono a tarjeta de crédito (TDC)
      - account_debit: Egreso de cuenta bancaria (débito, pago móvil, transferencia)
      - account_credit: Ingreso a cuenta bancaria (cobro recibido, depósito)
    """
    def get(self, request):
        cards_tdc = CreditCard.objects.filter(cutoff_day__isnull=False).order_by('name')
        bank_accounts = BankAccount.objects.all()
        return render(request, 'banesco_tracker/manual_entry.html', {
            'cards_tdc': cards_tdc,
            'bank_accounts': bank_accounts,
        })

    def post(self, request):
        import hashlib
        entry_mode = request.POST.get('entry_mode', '').strip()
        amount_str = request.POST.get('amount_ves', '').strip()
        date_str = request.POST.get('booking_date', '').strip()
        reference = request.POST.get('reference', '').strip() or None
        description = request.POST.get('description', '').strip()

        if not entry_mode or not amount_str:
            messages.error(request, "Modo de entrada y monto son obligatorios.")
            return redirect('manual_entry')

        try:
            amount_ves = Decimal(amount_str.replace(',', '.'))
            if amount_ves <= 0:
                messages.error(request, "El monto debe ser mayor a cero.")
                return redirect('manual_entry')
        except Exception:
            messages.error(request, "El monto ingresado no es válido.")
            return redirect('manual_entry')

        try:
            if date_str:
                booking_date = timezone.make_aware(
                    datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M")
                )
            else:
                booking_date = timezone.now()
        except Exception:
            booking_date = timezone.now()

        log = ensure_exchange_rate(booking_date.date())

        # ── MODO: Consumo en TDC ──────────────────────────────────────────────
        if entry_mode == 'tdc_charge':
            card_id = request.POST.get('card_id', '').strip()
            card = get_object_or_404(CreditCard, id=card_id)
            desc = description or f"Consumo manual {card.card_type_display}"
            hash_key = f"MANUAL|{card.last_four}|{booking_date.strftime('%Y%m%d%H%M')}|{amount_ves}|{desc[:30]}"
            ref = reference or f"MAN-{hashlib.md5(hash_key.encode()).hexdigest()[:10]}"

            tx, created = Transaction.objects.get_or_create(
                card=card, type='TDC', booking_date=booking_date,
                amount_ves=amount_ves, reference=ref,
                defaults={'description': desc, 'exchange_rate': log, 'status': 'PENDIENTE'}
            )
            if created:
                Transaction.update_statuses(timezone.localdate())
                messages.success(request, f"Consumo de Bs. {amount_ves:,.2f} registrado en {card.name} (*{card.last_four}).")
            else:
                messages.warning(request, "Este consumo ya estaba registrado (duplicado omitido).")

        # ── MODO: Pago/Abono a TDC ───────────────────────────────────────────
        elif entry_mode == 'tdc_payment':
            card_id = request.POST.get('card_id', '').strip()
            card = get_object_or_404(CreditCard, id=card_id)
            desc = description or f"Pago manual a {card.card_type_display}"
            amount_neg = -abs(amount_ves)
            hash_key = f"PAGO|{card.last_four}|{booking_date.strftime('%Y%m%d%H%M')}|{amount_neg}|{desc[:30]}"
            ref = reference or f"PAG-{hashlib.md5(hash_key.encode()).hexdigest()[:10]}"

            tx, created = Transaction.objects.get_or_create(
                card=card, type='TDC', booking_date=booking_date,
                amount_ves=amount_neg, reference=ref,
                defaults={'description': desc, 'exchange_rate': log, 'status': 'PAGADO'}
            )
            if created:
                Transaction.update_statuses(timezone.localdate())
                messages.success(request, f"Pago de Bs. {amount_ves:,.2f} aplicado a {card.name} (*{card.last_four}).")
            else:
                messages.warning(request, "Este pago ya estaba registrado (duplicado omitido).")

        # ── MODO: Egreso de cuenta (débito/pago móvil/transferencia saliente) ─
        elif entry_mode == 'account_debit':
            account_id = request.POST.get('account_id', '').strip()
            bank_account = get_object_or_404(BankAccount, id=account_id) if account_id else BankAccount.objects.first()
            desc = description or "Egreso manual de cuenta"
            amount_neg = -abs(amount_ves)
            ref = reference or f"MAN-DEB-{booking_date.strftime('%Y%m%d%H%M%S')}"
            try:
                _, created = BankAccountTransaction.objects.get_or_create(
                    reference=ref,
                    defaults={
                        'account': bank_account, 'booking_date': booking_date,
                        'description': desc, 'amount_ves': amount_neg,
                        'is_manual': True, 'exchange_rate': log,
                    }
                )
                if created:
                    messages.success(request, f"Egreso de Bs. {amount_ves:,.2f} registrado. Saldo: Bs. {bank_account.current_balance:,.2f}")
                else:
                    messages.warning(request, "Este egreso ya estaba registrado (referencia duplicada).")
            except Exception as e:
                messages.error(request, f"Error al registrar el egreso: {e}")

        # ── MODO: Ingreso a cuenta (cobro, depósito, transferencia recibida) ──
        elif entry_mode == 'account_credit':
            account_id = request.POST.get('account_id', '').strip()
            bank_account = get_object_or_404(BankAccount, id=account_id) if account_id else BankAccount.objects.first()
            desc = description or "Ingreso manual a cuenta"
            amount_pos = abs(amount_ves)
            ref = reference or f"MAN-CRE-{booking_date.strftime('%Y%m%d%H%M%S')}"
            try:
                _, created = BankAccountTransaction.objects.get_or_create(
                    reference=ref,
                    defaults={
                        'account': bank_account, 'booking_date': booking_date,
                        'description': desc, 'amount_ves': amount_pos,
                        'is_manual': True, 'exchange_rate': log,
                    }
                )
                if created:
                    messages.success(request, f"Ingreso de Bs. {amount_ves:,.2f} registrado. Saldo: Bs. {bank_account.current_balance:,.2f}")
                else:
                    messages.warning(request, "Este ingreso ya estaba registrado (referencia duplicada).")
            except Exception as e:
                messages.error(request, f"Error al registrar el ingreso: {e}")

        else:
            messages.error(request, f"Modo de entrada no reconocido: {entry_mode}")

        return redirect('manual_entry')
