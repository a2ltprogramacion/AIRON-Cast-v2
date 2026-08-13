import datetime
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.db.models import UniqueConstraint

def add_months(sourcedate, months):
    """Suma N meses a una fecha manejando fin de año y bisiestos."""
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, [
        31,
        29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
        31, 30, 31, 30, 31, 31, 30, 31, 30, 31
    ][month - 1])
    return datetime.date(year, month, day)

def get_safe_date(year, month, day):
    """Retorna una fecha válida limitando el día al máximo del mes (para febrero/30)."""
    max_day = [
        31,
        29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
        31, 30, 31, 30, 31, 31, 30, 31, 30, 31
    ][month - 1]
    return datetime.date(year, month, min(day, max_day))


class CreditCard(models.Model):
    THEME_CHOICES = [
        ('gold', 'Dorado Metálico'),
        ('platinum', 'Gris Platino Oscuro'),
        ('green', 'Verde Esmeralda'),
        ('blue', 'Azul Zafiro'),
        ('purple', 'Violeta Real'),
        ('black', 'Carbono Profundo'),
        ('silver', 'Plata Metálica'),
        ('white', 'Hielo Blanco'),
        ('red', 'Rubí Intenso'),
    ]

    name = models.CharField(max_length=50)
    last_four = models.CharField(max_length=4)
    cutoff_day = models.PositiveIntegerField(null=True, blank=True)
    payment_day = models.PositiveIntegerField(null=True, blank=True)
    card_type_display = models.CharField(max_length=50, default="VISA DORADA")
    theme_color = models.CharField(max_length=20, choices=THEME_CHOICES, default="gold")
    
    # Nuevos campos financieros según normativa Banesco
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("60.00"))
    mora_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("3.00"))
    minimum_payment_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("4.20"))
    previous_balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    associated_account = models.ForeignKey('BankAccount', on_delete=models.SET_NULL, null=True, blank=True, related_name='cards')

    def __str__(self):
        return f"{self.name} (*{self.last_four})"

    @property
    def available_limit(self):
        """
        Calcula dinámicamente el cupo disponible de la tarjeta:
        Límite de Crédito - Deuda Total (previous_balance + Consumos - Pagos).
        """
        if self.cutoff_day is None:
            return Decimal("0.00")
            
        total_debt = self.previous_balance + sum(t.amount_ves for t in self.transactions.all())
        return (self.credit_limit - total_debt).quantize(Decimal("0.01"))


    @property
    def available_limit_discrepancy(self):
        """
        No aplica discrepancia ya que el cupo disponible es 100% dinámico.
        """
        return Decimal("0.00")

    @property
    def minimum_payment_info(self):
        """
        Retorna dict con balance, interes_ordinario y pago_minimo.
        Para uso en templates que no tienen acceso a summaries pre-computadas.
        """
        if self.cutoff_day is None:
            return {"balance": Decimal("0.00"), "interes_ordinario": Decimal("0.00"), "pago_minimo": Decimal("0.00")}
        
        balance = self.previous_balance + sum(t.amount_ves for t in self.transactions.all())
        unpaid = self.transactions.filter(amount_ves__gt=0)
        interes = Decimal(str(sum(t.calculate_projected_interest() for t in unpaid)))
        min_rate = self.minimum_payment_rate or Decimal("4.20")
        pago_minimo = (balance * (min_rate / Decimal("100.00")) + interes).quantize(Decimal("0.01"))
        
        return {
            "balance": balance.quantize(Decimal("0.01")),
            "interes_ordinario": interes.quantize(Decimal("0.01")),
            "pago_minimo": pago_minimo,
        }

    @property
    def theme_css(self):
        mapping = {
            'gold': 'from-amber-600 via-yellow-600 to-yellow-500 text-slate-950',
            'platinum': 'from-slate-800 via-slate-700 to-slate-600 text-white',
            'green': 'from-emerald-700 via-teal-800 to-emerald-500 text-white',
            'blue': 'from-blue-950 via-teal-900 to-cyan-900 text-white',
            'purple': 'from-slate-900 via-purple-950 to-indigo-900 text-white',
            'black': 'from-slate-950 via-slate-900 to-zinc-900 text-white',
            'silver': 'from-slate-400 via-slate-350 to-slate-200 text-slate-950',
            'white': 'from-slate-100 via-slate-50 to-white text-slate-950 border border-slate-300/40',
            'red': 'from-rose-900 via-red-950 to-rose-800 text-white',
        }
        return mapping.get(self.theme_color, 'from-amber-600 via-yellow-600 to-yellow-500 text-slate-950')


    def get_financing_simulation(self, target_date=None, calculate_limits=True):
        """
        Calcula dinámicamente el apalancamiento si se consumiera en target_date.
        Retorna un dict con: cutoff_date, payment_date, days, semaphore_color.
        """
        if self.cutoff_day is None or self.payment_day is None:
            return None  # No aplica apalancamiento para débito

        if target_date is None:
            target_date = timezone.localdate()
        elif isinstance(target_date, datetime.datetime):
            target_date = target_date.date()

        # Determinación de Ciclo de Corte y Pago
        if self.cutoff_day == 12 and self.payment_day == 8:
            # Visa Dorada
            if target_date.day <= 12:
                cutoff_date = datetime.date(target_date.year, target_date.month, 12)
                # Paga el mes siguiente, día 8
                payment_date = get_safe_date(target_date.year, target_date.month, 8)
                payment_date = add_months(payment_date, 1)
            else:
                # Corta el mes siguiente, día 12
                cutoff_date = get_safe_date(target_date.year, target_date.month, 12)
                cutoff_date = add_months(cutoff_date, 1)
                # Paga dos meses adelante, día 8
                payment_date = get_safe_date(target_date.year, target_date.month, 8)
                payment_date = add_months(payment_date, 2)

        elif self.cutoff_day == 3 and self.payment_day == 30:
            # Mastercard Platinum
            if target_date.day <= 3:
                cutoff_date = datetime.date(target_date.year, target_date.month, 3)
                # Paga este mismo mes, día 30
                payment_date = get_safe_date(target_date.year, target_date.month, 30)
            else:
                # Corta el mes siguiente, día 3
                cutoff_date = get_safe_date(target_date.year, target_date.month, 3)
                cutoff_date = add_months(cutoff_date, 1)
                # Paga el mes siguiente, día 30
                next_month = add_months(target_date, 1)
                payment_date = get_safe_date(next_month.year, next_month.month, 30)
        else:
            # Caso genérico fallback
            if target_date.day <= self.cutoff_day:
                cutoff_date = get_safe_date(target_date.year, target_date.month, self.cutoff_day)
                payment_date = get_safe_date(target_date.year, target_date.month, self.payment_day)
                if self.payment_day < self.cutoff_day:
                    payment_date = add_months(payment_date, 1)
            else:
                cutoff_date = get_safe_date(target_date.year, target_date.month, self.cutoff_day)
                cutoff_date = add_months(cutoff_date, 1)
                payment_date = get_safe_date(target_date.year, target_date.month, self.payment_day)
                payment_date = add_months(payment_date, 2 if self.payment_day < self.cutoff_day else 1)

        # Medición del ciclo de facturación cronológico
        previous_cutoff_date = add_months(cutoff_date, -1)
        cycle_start_date = previous_cutoff_date + datetime.timedelta(days=1)
        cycle_total_days = (cutoff_date - previous_cutoff_date).days
        days_elapsed = (target_date - previous_cutoff_date).days
        days_elapsed = max(0, min(cycle_total_days, days_elapsed))
        
        cycle_elapsed_percent = 0.0
        if cycle_total_days > 0:
            cycle_elapsed_percent = float((days_elapsed / cycle_total_days) * 100)
            cycle_elapsed_percent = max(0.0, min(100.0, cycle_elapsed_percent))

        # Días totales de financiamiento libre de interés
        days = (payment_date - target_date).days

        # Semáforo alineado dinámicamente con la posición/porcentaje en el ciclo de facturación
        if cycle_elapsed_percent < 40.0:
            semaphore_color = "green"
        elif cycle_elapsed_percent < 80.0:
            semaphore_color = "yellow"
        else:
            semaphore_color = "red"

        # Límites de financiamiento calculados dinámicamente si se solicita
        max_financing_days = None
        min_financing_days = None
        if calculate_limits:
            sim_max = self.get_financing_simulation(target_date=cycle_start_date, calculate_limits=False)
            sim_min = self.get_financing_simulation(target_date=cutoff_date, calculate_limits=False)
            max_financing_days = sim_max["days"] if sim_max else None
            min_financing_days = sim_min["days"] if sim_min else None

        return {
            "days": days,
            "cutoff_date": cutoff_date,
            "payment_date": payment_date,
            "semaphore_color": semaphore_color,
            "cycle_start_date": cycle_start_date,
            "cycle_end_date": cutoff_date,
            "cycle_total_days": cycle_total_days,
            "cycle_days_elapsed": days_elapsed,
            "cycle_elapsed_percent": cycle_elapsed_percent,
            "max_financing_days": max_financing_days,
            "min_financing_days": min_financing_days,
        }


class ExchangeRateLog(models.Model):
    date = models.DateField(unique=True)
    bcv_rate = models.DecimalField(max_digits=12, decimal_places=4)
    binance_rate = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)

    def __str__(self):
        return f"{self.date} | BCV: {self.bcv_rate} | Binance: {self.binance_rate or 'N/A'}"


class Transaction(models.Model):
    TYPE_CHOICES = [
        ('TDC', 'Tarjeta de Crédito'),
        ('DEBIT', 'Débito'),
    ]

    STATUS_CHOICES = [
        ('PENDIENTE', 'Pendiente por Cortar'),
        ('CORTADO_NO_PAGADO', 'Cortado No Pagado'),
        ('PAGADO', 'Pagado'),
    ]

    card = models.ForeignKey(CreditCard, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    booking_date = models.DateTimeField()
    description = models.CharField(max_length=255)
    amount_ves = models.DecimalField(max_digits=15, decimal_places=2)
    reference = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDIENTE')
    exchange_rate = models.ForeignKey(ExchangeRateLog, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')

    class Meta:
        constraints = [
            UniqueConstraint(fields=['card', 'booking_date', 'amount_ves', 'reference'], name='unique_banesco_transaction')
        ]
        ordering = ['-booking_date']

    def __str__(self):
        return f"{self.booking_date.strftime('%d/%m/%Y')} | {self.card.name} | {self.description} | Bs.{self.amount_ves}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        
        if self.type == 'DEBIT':
            self.status = 'PAGADO'
            
        super().save(*args, **kwargs)
        
        # Si es un consumo de tarjeta de débito nuevo, crear y reconciliar automáticamente
        if is_new and self.type == 'DEBIT':
            account = self.card.associated_account
            if account:
                from django.db.models import Q
                
                # Búsqueda difusa para evitar duplicación
                ref = (self.reference or '').strip()
                bank_tx = None
                if ref:
                    # Normalizar referencia quitando ceros a la izquierda
                    clean_ref = ref.lstrip('0')
                    if clean_ref:
                        # Buscar por coincidencia difusa en la cuenta corriente correspondiente
                        # y priorizar los movimientos bancarios que aún tengan saldo disponible para conciliar
                        candidates = BankAccountTransaction.objects.filter(
                            account=account
                        ).filter(
                            Q(reference=ref) | Q(reference__endswith=clean_ref) | Q(reference=clean_ref)
                        )
                        for candidate in candidates:
                            existing_bank_sum = sum(r.reconciled_amount for r in candidate.reconciliations.all())
                            bank_total = abs(candidate.amount_ves)
                            if bank_total - existing_bank_sum > 0:
                                bank_tx = candidate
                                break
                
                if not bank_tx:
                    # Si no existe, crear el movimiento manual con monto negativo (egreso de banco)
                    # Si reference está vacío, generar una referencia única basada en el ID
                    unique_ref = ref or f"DEBIT-TX-{self.id}"
                    
                    # Asegurar que no choque con otra referencia única si hay colisiones
                    counter = 1
                    while BankAccountTransaction.objects.filter(account=account, reference=unique_ref).exists():
                        unique_ref = f"{ref or 'DEBIT-TX'}-{self.id}-{counter}"
                        counter += 1
                        
                    bank_tx = BankAccountTransaction.objects.create(
                        account=account,
                        booking_date=self.booking_date,
                        reference=unique_ref,
                        description=self.description,
                        amount_ves=-self.amount_ves, # egreso de banco
                        is_manual=True,
                        exchange_rate=self.exchange_rate
                    )
                
                # Crear la reconciliación automática si no existe
                TransactionReconciliation.objects.get_or_create(
                    bank_transaction=bank_tx,
                    card_transaction=self,
                    defaults={'reconciled_amount': self.amount_ves}
                )

    @property
    def fecha_corte_asignada(self):
        """Deriva la fecha de corte asignada para este consumo."""
        if self.card.cutoff_day is None:
            return None

        consumption_date = self.booking_date.date()

        if consumption_date.day <= self.card.cutoff_day:
            return get_safe_date(consumption_date.year, consumption_date.month, self.card.cutoff_day)
        else:
            next_month = add_months(consumption_date, 1)
            return get_safe_date(next_month.year, next_month.month, self.card.cutoff_day)

    @property
    def fecha_limite_pago(self):
        """Deriva la fecha límite de pago para este consumo basado en su fecha de corte asignada."""
        corte = self.fecha_corte_asignada
        if corte is None or self.card.payment_day is None:
            return None

        # Reglas por tarjeta
        if self.card.cutoff_day == 12 and self.card.payment_day == 8:
            # Visa Dorada: Paga el 8 del mes siguiente a la fecha de corte
            payment_base = get_safe_date(corte.year, corte.month, 8)
            return add_months(payment_base, 1)
        elif self.card.cutoff_day == 3 and self.card.payment_day == 30:
            # Mastercard Platinum: Paga el 30 del mismo mes de la fecha de corte
            return get_safe_date(corte.year, corte.month, 30)
        else:
            # Fallback genérico
            payment_base = get_safe_date(corte.year, corte.month, self.card.payment_day)
            if self.card.payment_day < self.card.cutoff_day:
                return add_months(payment_base, 1)
            return payment_base

    @property
    def amount_usd(self):
        """Calcula el monto equivalente en dólares usando la tasa registrada (Binance por defecto, BCV fallback)."""
        if not self.exchange_rate:
            return None
        rate = self.exchange_rate.binance_rate or self.exchange_rate.bcv_rate
        if rate:
            return self.amount_ves / rate
        return None

    @property
    def amount_usd_bcv(self):
        """Calcula el monto equivalente en dólares usando la tasa oficial BCV."""
        if not self.exchange_rate or not self.exchange_rate.bcv_rate:
            return None
        return self.amount_ves / self.exchange_rate.bcv_rate

    @property
    def amount_usd_binance(self):
        """Calcula el monto equivalente en dólares usando la tasa Binance P2P."""
        if not self.exchange_rate or not self.exchange_rate.binance_rate:
            return None
        return self.amount_ves / self.exchange_rate.binance_rate

    def calculate_projected_interest(self):
        """
        Calcula el interés ordinario de financiamiento para consumos de TDC.
        Fórmula: Interés = Monto_VES * (Tasa_Interés_Tarjeta / 100) * (t / 360)
        Donde t = fecha_corte_asignada - booking_date.date()
        """
        if self.type != 'TDC' or self.amount_ves <= 0:
            return Decimal("0.00")
            
        corte = self.fecha_corte_asignada
        if not corte:
            return Decimal("0.00")
            
        t_days = (corte - self.booking_date.date()).days
        if t_days <= 0:
            return Decimal("0.00")
            
        rate = self.card.interest_rate or Decimal("60.00")
        interest = self.amount_ves * (rate / Decimal("100.00")) * (Decimal(t_days) / Decimal("360.00"))
        return interest.quantize(Decimal("0.01"))

    def calculate_mora_interest(self, today=None):
        """
        Calcula el recargo por mora si la transacción de crédito pasó de su fecha límite sin ser pagada.
        Fórmula: Mora = Monto_VES * (Tasa_Mora_Tarjeta / 100) * (días_retraso / 360)
        """
        if self.type != 'TDC' or self.status != 'CORTADO_NO_PAGADO' or self.amount_ves <= 0:
            return Decimal("0.00")
            
        limit_date = self.fecha_limite_pago
        if not limit_date:
            return Decimal("0.00")
            
        if today is None:
            today = timezone.localdate()
        elif isinstance(today, datetime.datetime):
            today = today.date()
            
        if today <= limit_date:
            return Decimal("0.00")
            
        overdue_days = (today - limit_date).days
        mora_rate = self.card.mora_rate or Decimal("3.00")
        mora = self.amount_ves * (mora_rate / Decimal("100.00")) * (Decimal(overdue_days) / Decimal("360.00"))
        return mora.quantize(Decimal("0.01"))

    @property
    def projected_interest(self):
        """
        Calcula el interés financiero por mora acumulado tras pasar la fecha límite de pago.
        Para compatibilidad con el resto del sistema, invoca calculate_mora_interest.
        """
        return self.calculate_mora_interest()

    @classmethod
    def update_statuses(cls, today=None):
        """
        Reconcilia dinámicamente los consumos de cada tarjeta con sus pagos registrados (FIFO),
        y actualiza los consumos restantes a CORTADO_NO_PAGADO si ya pasó su fecha de corte.
        """
        if today is None:
            today = timezone.localdate()
        elif isinstance(today, datetime.datetime):
            today = today.date()

        from .models import CreditCard
        cards = CreditCard.objects.all()
        updated_count = 0

        for card in cards:
            # Si la tarjeta no tiene corte (débito), todas sus transacciones son marcadas como PAGADO
            if card.cutoff_day is None:
                debit_txs = cls.objects.filter(card=card).exclude(status='PAGADO')
                for tx in debit_txs:
                    tx.status = 'PAGADO'
                    tx.save(update_fields=['status'])
                    updated_count += 1
                continue

            # Obtener consumos (monto > 0) y pagos (monto < 0) por separado, ambos en orden cronológico
            consumos = list(cls.objects.filter(card=card, amount_ves__gt=0).order_by('booking_date'))
            pagos = list(cls.objects.filter(card=card, amount_ves__lt=0).order_by('booking_date'))

            # Marcar todos los pagos como PAGADO en la base de datos por consistencia
            for p in pagos:
                if p.status != 'PAGADO':
                    p.status = 'PAGADO'
                    p.save(update_fields=['status'])
                    updated_count += 1

            # Motor FIFO: pool global de todos los pagos de la tarjeta.
            # Cada pago cancela los consumos más antiguos primero (FIFO cronológico).
            # La eliminación previa de pagos duplicados garantiza que el pool no esté inflado.
            payment_pool = sum(abs(p.amount_ves) for p in pagos)

            for tx in consumos:
                if payment_pool >= tx.amount_ves:
                    payment_pool -= tx.amount_ves
                    target_status = 'PAGADO'
                elif payment_pool > 0:
                    payment_pool = Decimal("0.00")
                    corte = tx.fecha_corte_asignada
                    target_status = 'CORTADO_NO_PAGADO' if (corte and corte < today) else 'PENDIENTE'
                else:
                    corte = tx.fecha_corte_asignada
                    target_status = 'CORTADO_NO_PAGADO' if (corte and corte < today) else 'PENDIENTE'
                
                if tx.status != target_status:
                    tx.status = target_status
                    tx.save(update_fields=['status'])
                    updated_count += 1

        return updated_count


class BankAccount(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ('current', 'Cuenta Corriente'),
        ('savings', 'Cuenta de Ahorros'),
    ]

    name = models.CharField(max_length=50, default="Cuenta Corriente Banesco")
    account_number = models.CharField(max_length=20, unique=True)
    last_four = models.CharField(max_length=4)
    initial_balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES, default='current')

    def __str__(self):
        return f"{self.name} (*{self.last_four})"

    @property
    def current_balance(self):
        """Retorna el saldo de la última transacción registrada (balance oficial del banco).
        
        Si no hay transacciones, retorna initial_balance.
        El saldo de la última transacción es la cifra oficial del banco y no depende de
        tener todos los movimientos intermedios en la base de datos.
        Se usa -id como tiebreaker porque todas las transacciones del mismo día tienen
        el mismo datetime, y el ID más alto corresponde a la última línea del archivo.
        """
        last_tx = self.transactions.order_by('-booking_date', '-id').first()
        if last_tx and last_tx.balance_ves is not None:
            return last_tx.balance_ves
        return (self.initial_balance + sum(t.amount_ves for t in self.transactions.all())).quantize(Decimal("0.01"))

    @property
    def unreconciled_debits(self):
        """Consumos de débito no conciliados vinculados a esta cuenta."""
        return sum(
            t.amount_ves for t in Transaction.objects.filter(
                card__associated_account=self,
                type='DEBIT',
                amount_ves__gt=0,
                reconciliations__isnull=True
            )
        ) or Decimal("0.00")

    @property
    def unreconciled_tdc_payments(self):
        """Pagos de TDC no conciliados realizados desde esta cuenta."""
        return sum(
            abs(t.amount_ves) for t in Transaction.objects.filter(
                card__associated_account=self,
                type='TDC',
                amount_ves__lt=0,
                reconciliations__isnull=True
            )
        ) or Decimal("0.00")

    @property
    def projected_balance(self):
        """Calcula el saldo líquido proyectado (Disponible), deduciendo egresos y pagos no conciliados."""
        return (self.current_balance - self.unreconciled_debits - self.unreconciled_tdc_payments).quantize(Decimal("0.01"))


class BankAccountTransaction(models.Model):
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='transactions')
    booking_date = models.DateTimeField()
    reference = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255)
    amount_ves = models.DecimalField(max_digits=15, decimal_places=2)  # Positivo = Ingreso, Negativo = Egreso
    balance_ves = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    exchange_rate = models.ForeignKey(
        ExchangeRateLog,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bank_transactions'
    )
    is_manual = models.BooleanField(default=False)

    class Meta:
        ordering = ['-booking_date']

    def __str__(self):
        sign = "+" if self.amount_ves >= 0 else ""
        return f"{self.booking_date.strftime('%d/%m/%Y')} | {self.account.name} | {self.description} | {sign}Bs.{self.amount_ves}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        
        # Ingesta inteligente y de-duplicación al insertar un movimiento oficial nuevo
        if is_new and not self.is_manual:
            ref = (self.reference or '').strip()
            if ref:
                clean_ref = ref.lstrip('0')
                if clean_ref:
                    from django.db.models import Q
                    # Buscar movimientos manuales previos con coincidencia difusa de referencia
                    manual_candidates = BankAccountTransaction.objects.filter(
                        account=self.account,
                        is_manual=True
                    ).filter(
                        Q(reference=ref) | Q(reference__endswith=clean_ref) | Q(reference=clean_ref)
                    )
                    
                    duplicate_tx = manual_candidates.first()
                    if duplicate_tx:
                        # Guardar el registro oficial primero para obtener un PK
                        super().save(*args, **kwargs)
                        
                        # Re-asociar reconciliaciones existentes de la transacción manual a la oficial
                        for recon in duplicate_tx.reconciliations.all():
                            # Usar update para re-vincular de forma directa y limpia
                            TransactionReconciliation.objects.filter(pk=recon.pk).update(bank_transaction=self)
                            
                        # Eliminar el movimiento manual duplicado
                        duplicate_tx.delete()
                        return
                        
        super().save(*args, **kwargs)

    @property
    def amount_usd(self):
        if not self.exchange_rate:
            return None
        rate = self.exchange_rate.binance_rate or self.exchange_rate.bcv_rate
        if rate:
            return self.amount_ves / rate
        return None

    @property
    def amount_usd_bcv(self):
        if not self.exchange_rate or not self.exchange_rate.bcv_rate:
            return None
        return self.amount_ves / self.exchange_rate.bcv_rate

    @property
    def amount_usd_binance(self):
        if not self.exchange_rate or not self.exchange_rate.binance_rate:
            return None
        return self.amount_ves / self.exchange_rate.binance_rate


class TransactionReconciliation(models.Model):
    bank_transaction = models.ForeignKey(
        BankAccountTransaction,
        on_delete=models.CASCADE,
        related_name="reconciliations"
    )
    card_transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name="reconciliations"
    )
    reconciled_amount = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['bank_transaction', 'card_transaction'], name='unique_reconciliation_pair')
        ]

    def __str__(self):
        return f"Reconciliación: {self.bank_transaction.reference} <-> {self.card_transaction.id} (Bs. {self.reconciled_amount})"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.reconciled_amount <= 0:
            raise ValidationError("El monto conciliado debe ser mayor a cero.")

        # Calcular saldo disponible del BankAccountTransaction
        existing_bank_sum = sum(
            r.reconciled_amount for r in self.bank_transaction.reconciliations.all()
            if r.pk != self.pk
        )
        bank_total = abs(self.bank_transaction.amount_ves)
        if existing_bank_sum + self.reconciled_amount > bank_total:
            raise ValidationError(
                f"El monto conciliado (Bs. {self.reconciled_amount}) excede el monto disponible "
                f"del movimiento bancario (disponible: Bs. {bank_total - existing_bank_sum})."
            )

        # Calcular saldo por conciliar de la Transaction de tarjeta
        existing_card_sum = sum(
            r.reconciled_amount for r in self.card_transaction.reconciliations.all()
            if r.pk != self.pk
        )
        card_total = abs(self.card_transaction.amount_ves)
        if existing_card_sum + self.reconciled_amount > card_total:
            raise ValidationError(
                f"El monto conciliado (Bs. {self.reconciled_amount}) excede el monto pendiente "
                f"de la transacción de tarjeta (pendiente: Bs. {card_total - existing_card_sum})."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
