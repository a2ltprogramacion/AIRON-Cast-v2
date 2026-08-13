import datetime
from decimal import Decimal
from unittest.mock import patch
from django.test import TestCase
from django.utils import timezone
from .models import CreditCard, ExchangeRateLog, Transaction, TransactionReconciliation
from .parser import BanescoEmailParser, clean_amount
from .services import ensure_exchange_rate

class CleanAmountTestCase(TestCase):
    """Pruebas unitarias para la limpieza de montos en bolívares."""
    def test_clean_amount_tdc_format(self):
        self.assertEqual(clean_amount("1.250,50"), Decimal("1250.50"))
        self.assertEqual(clean_amount("Bs. 1.250,50"), Decimal("1250.50"))
        self.assertEqual(clean_amount("Bs. 500"), Decimal("500.00"))

    def test_clean_amount_debit_format(self):
        self.assertEqual(clean_amount("4.800,00"), Decimal("4800.00"))
        self.assertEqual(clean_amount("450,75"), Decimal("450.75"))
        self.assertEqual(clean_amount("12,5"), Decimal("12.50"))
        self.assertEqual(clean_amount("1,250.50"), Decimal("1250.50"))


class BanescoCreditCardCyclesTestCase(TestCase):
    """Pruebas unitarias de la lógica de ciclos de facturación y apalancamiento."""
    
    def setUp(self):
        self.visa = CreditCard.objects.create(
            name="Visa Dorada",
            last_four="1234",
            cutoff_day=12,
            payment_day=8
        )
        self.mastercard = CreditCard.objects.create(
            name="Mastercard Platinum",
            last_four="5678",
            cutoff_day=3,
            payment_day=30
        )
        self.debit_card = CreditCard.objects.create(
            name="Tarjeta de Débito",
            last_four="0000",
            cutoff_day=None,
            payment_day=None
        )

    def test_visa_dorada_cycle_assignment_before_cutoff(self):
        # Consumo el 10 de Mayo (antes o igual al día de corte: 12)
        tx = Transaction.objects.create(
            card=self.visa,
            type='TDC',
            booking_date=timezone.make_aware(datetime.datetime(2026, 5, 10, 10, 0)),
            description="Consumo Test",
            amount_ves=Decimal("100.00"),
            reference="111"
        )
        self.assertEqual(tx.fecha_corte_asignada, datetime.date(2026, 5, 12))
        self.assertEqual(tx.fecha_limite_pago, datetime.date(2026, 6, 8))

    def test_visa_dorada_cycle_assignment_after_cutoff(self):
        # Consumo el 15 de Mayo (después del día de corte: 12)
        tx = Transaction.objects.create(
            card=self.visa,
            type='TDC',
            booking_date=timezone.make_aware(datetime.datetime(2026, 5, 15, 10, 0)),
            description="Consumo Test",
            amount_ves=Decimal("100.00"),
            reference="222"
        )
        self.assertEqual(tx.fecha_corte_asignada, datetime.date(2026, 6, 12))
        self.assertEqual(tx.fecha_limite_pago, datetime.date(2026, 7, 8))

    def test_mastercard_platinum_cycle_assignment_before_cutoff(self):
        # Consumo el 2 de Mayo (antes o igual al día de corte: 3)
        tx = Transaction.objects.create(
            card=self.mastercard,
            type='TDC',
            booking_date=timezone.make_aware(datetime.datetime(2026, 5, 2, 10, 0)),
            description="Consumo Test",
            amount_ves=Decimal("100.00"),
            reference="333"
        )
        self.assertEqual(tx.fecha_corte_asignada, datetime.date(2026, 5, 3))
        self.assertEqual(tx.fecha_limite_pago, datetime.date(2026, 5, 30))

    def test_mastercard_platinum_cycle_assignment_after_cutoff(self):
        # Consumo el 5 de Mayo (después del día de corte: 3)
        tx = Transaction.objects.create(
            card=self.mastercard,
            type='TDC',
            booking_date=timezone.make_aware(datetime.datetime(2026, 5, 5, 10, 0)),
            description="Consumo Test",
            amount_ves=Decimal("100.00"),
            reference="444"
        )
        self.assertEqual(tx.fecha_corte_asignada, datetime.date(2026, 6, 3))
        self.assertEqual(tx.fecha_limite_pago, datetime.date(2026, 6, 30))

    def test_mastercard_platinum_february_handling_non_leap(self):
        # Año 2026 (No bisiesto): Consumo > 3 de Enero. El corte cae el 3 de Febrero.
        # La fecha de pago debe caer el 30 de febrero, pero al corregirse dinámicamente
        # debe resultar en el 28 de Febrero de 2026.
        tx = Transaction.objects.create(
            card=self.mastercard,
            type='TDC',
            booking_date=timezone.make_aware(datetime.datetime(2026, 1, 10, 10, 0)),
            description="Consumo Enero",
            amount_ves=Decimal("100.00"),
            reference="555"
        )
        self.assertEqual(tx.fecha_corte_asignada, datetime.date(2026, 2, 3))
        self.assertEqual(tx.fecha_limite_pago, datetime.date(2026, 2, 28))

    def test_mastercard_platinum_february_handling_leap_year(self):
        # Año 2028 (Bisiesto): Corte cae el 3 de Febrero. Pago ajustado al 29 de Febrero.
        tx = Transaction.objects.create(
            card=self.mastercard,
            type='TDC',
            booking_date=timezone.make_aware(datetime.datetime(2028, 1, 15, 10, 0)),
            description="Consumo Enero Bisiesto",
            amount_ves=Decimal("100.00"),
            reference="666"
        )
        self.assertEqual(tx.fecha_corte_asignada, datetime.date(2028, 2, 3))
        self.assertEqual(tx.fecha_limite_pago, datetime.date(2028, 2, 29))

    def test_debit_card_has_no_billing_cycle(self):
        tx = Transaction.objects.create(
            card=self.debit_card,
            type='DEBIT',
            booking_date=timezone.make_aware(datetime.datetime(2026, 5, 21, 10, 0)),
            description="Retiro Débito",
            amount_ves=Decimal("500.00"),
            reference="777"
        )
        self.assertIsNone(tx.fecha_corte_asignada)
        self.assertIsNone(tx.fecha_limite_pago)

    def test_visa_dorada_financing_simulation(self):
        # Consumo el 13 de Mayo de 2026 (un día después del corte).
        # Próximo corte: 12 de Junio. Pago: 8 de Julio.
        # Días totales: 8 de Julio - 13 de Mayo = 56 días. Semáforo: Green.
        date_today = datetime.date(2026, 5, 13)
        sim = self.visa.get_financing_simulation(date_today)
        self.assertEqual(sim['days'], 56)
        self.assertEqual(sim['cutoff_date'], datetime.date(2026, 6, 12))
        self.assertEqual(sim['payment_date'], datetime.date(2026, 7, 8))
        self.assertEqual(sim['semaphore_color'], 'green')

        # Consumo el 12 de Mayo de 2026 (el mismo día del corte).
        # Corte: 12 de Mayo. Pago: 8 de Junio.
        # Días: 8 de Junio - 12 de Mayo = 27 días. Semáforo: Red (100% del ciclo transcurrido).
        sim_low = self.visa.get_financing_simulation(datetime.date(2026, 5, 12))
        self.assertEqual(sim_low['days'], 27)
        self.assertEqual(sim_low['semaphore_color'], 'red')

    def test_debit_card_financing_simulation(self):
        sim = self.debit_card.get_financing_simulation(datetime.date(2026, 5, 21))
        self.assertIsNone(sim)


class BanescoEmailParserTestCase(TestCase):
    """Pruebas unitarias de la extracción de transacciones con Regex."""

    def test_parse_tdc_email(self):
        email_text = (
            "Estimado cliente: Banesco informa que se realizo un consumo "
            "en su TDC # 4321 Bs. 1.250,50 el 21-05-2026 13:45 Ref 987654321 en COMERCIO."
        )
        txs = BanescoEmailParser.parse_text(email_text)
        self.assertEqual(len(txs), 1)
        
        tx = txs[0]
        self.assertEqual(tx['type'], 'TDC')
        self.assertEqual(tx['card_last_four'], '4321')
        self.assertEqual(tx['amount_ves'], Decimal('1250.50'))
        self.assertEqual(tx['reference'], '987654321')
        self.assertEqual(tx['booking_date'].strftime('%d-%m-%Y %H:%M'), '21-05-2026 13:45')

    def test_parse_debit_email(self):
        email_text = (
            "Notificacion de Operacion de Debito Banesco.\n"
            "Detalles de la operacion:\n"
            "Nro. Tr: 1234567895678\n"
            "Fecha: 21/05/2026\n"
            "Hora: 13:45:00\n"
            "Monto: 4.800,00\n"
            "Nro. de aprob: 112233\n"
            "Gracias por preferirnos."
        )
        txs = BanescoEmailParser.parse_text(email_text)
        self.assertEqual(len(txs), 1)
        
        tx = txs[0]
        self.assertEqual(tx['type'], 'DEBIT')
        self.assertEqual(tx['card_last_four'], '5678')
        self.assertEqual(tx['amount_ves'], Decimal('4800.00'))
        self.assertEqual(tx['reference'], '112233')
        self.assertEqual(tx['booking_date'].strftime('%d/%m/%Y %H:%M:%S'), '21/05/2026 13:45:00')

    def test_parse_mixed_emails(self):
        email_text = (
            "TDC # 1234 Bs. 500,75 el 10-05-2026 09:12 Ref 999888\n"
            "Texto basura intermedio...\n"
            "Nro. Tr: 9999999990000\n"
            "Fecha: 15/05/2026\n"
            "Hora: 18:30:15\n"
            "Monto: 12.350,25\n"
            "Nro. de aprob: 777666\n"
        )
        txs = BanescoEmailParser.parse_text(email_text)
        self.assertEqual(len(txs), 2)
        
        tdc = [t for t in txs if t['type'] == 'TDC'][0]
        debit = [t for t in txs if t['type'] == 'DEBIT'][0]
        
        self.assertEqual(tdc['amount_ves'], Decimal('500.75'))
        self.assertEqual(tdc['reference'], '999888')
        
        self.assertEqual(debit['amount_ves'], Decimal('12350.25'))
        self.assertEqual(debit['reference'], '777666')


class ExchangeRateServicesTestCase(TestCase):
    """Pruebas unitarias para la integración y cacheo de tasas de cambio."""

    @patch('banesco_tracker.services.fetch_binance_rate')
    @patch('banesco_tracker.services.fetch_bcv_rate')
    def test_ensure_exchange_rate_today_fetches_and_saves(self, mock_bcv, mock_binance):
        mock_bcv.return_value = Decimal('36.8000')
        mock_binance.return_value = Decimal('38.2000')
        
        today = timezone.localdate()
        
        # Eliminar si existiera
        ExchangeRateLog.objects.filter(date=today).delete()
        
        # Llamar a ensure_exchange_rate
        log = ensure_exchange_rate(today)
        
        self.assertEqual(log.date, today)
        self.assertEqual(log.bcv_rate, Decimal('36.8000'))
        self.assertEqual(log.binance_rate, Decimal('38.2000'))
        
        # Comprobar persistencia
        db_log = ExchangeRateLog.objects.get(date=today)
        self.assertEqual(db_log.bcv_rate, Decimal('36.8000'))

    @patch('banesco_tracker.services.fetch_bcv_rate')
    def test_ensure_exchange_rate_past_date_leaves_binance_none(self, mock_bcv):
        mock_bcv.return_value = Decimal('36.1000')
        
        past_date = timezone.localdate() - datetime.timedelta(days=5)
        ExchangeRateLog.objects.filter(date=past_date).delete()
        
        log = ensure_exchange_rate(past_date)
        
        self.assertEqual(log.date, past_date)
        self.assertEqual(log.bcv_rate, Decimal('36.1000'))
        self.assertIsNone(log.binance_rate)


from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from .parser import parse_banesco_txt_report

class BanescoTxtReportParserTestCase(TestCase):
    """Batería de pruebas unitarias para la ingesta de reportes planos (.txt) de Banesco."""

    def setUp(self):
        self.visa = CreditCard.objects.create(
            name="Visa Dorada",
            last_four="2048",
            cutoff_day=12,
            payment_day=8
        )
        # Asegurar tasa de cambio de prueba
        self.log_date = datetime.date(2026, 5, 21)
        self.rate_log = ExchangeRateLog.objects.create(
            date=self.log_date,
            bcv_rate=Decimal("36.5000"),
            binance_rate=Decimal("38.0000")
        )

    def test_parse_banesco_txt_report_success(self):
        report_content = (
            "Banesco Banco Universal\n"
            "Reporte de Movimientos de Tarjeta\n"
            "Tarjeta: 4000123456782048 - Visa Dorada\n"
            "Fecha Proc   Descripción                  Monto\n"
            "21/05/2026   SUPERMERCADO CENTRAL         +1.500,50\n"
            "             Monto desbordado en línea siguiente\n"
            "21/05/2026   TIENDA TECNOLOGIA\n"
            "                                          +2.500,00\n"
            "21/05/2026   ABONO PAGO MINIMO            -1.000,00\n"
        )
        
        txs = parse_banesco_txt_report(report_content)
        self.assertEqual(len(txs), 3)
        
        # 1. Transacción Normal
        self.assertEqual(txs[0]["card_last_four"], "2048")
        self.assertEqual(txs[0]["description"], "SUPERMERCADO CENTRAL")
        self.assertEqual(txs[0]["amount_ves"], Decimal("1500.50"))
        self.assertFalse(txs[0]["is_payment"])
        
        # 2. Line-wrapped Monto
        self.assertEqual(txs[1]["description"], "TIENDA TECNOLOGIA")
        self.assertEqual(txs[1]["amount_ves"], Decimal("2500.00"))
        self.assertFalse(txs[1]["is_payment"])
        
        # 3. Pago
        self.assertEqual(txs[2]["description"], "ABONO PAGO MINIMO")
        self.assertEqual(txs[2]["amount_ves"], Decimal("1000.00"))
        self.assertTrue(txs[2]["is_payment"])

    def test_paste_box_view_upload_txt_file(self):
        report_content = (
            "Tarjeta: 4000123456782048\n"
            "21/05/2026   CONSUMO EXCLUSIVO            +350,00\n"
            "21/05/2026   ABONO EN TAQUILLA            -350,00\n"
        )
        
        uploaded_file = SimpleUploadedFile(
            "reporte_banesco.txt",
            report_content.encode("latin-1"),
            content_type="text/plain"
        )
        
        # Realizar POST con el archivo subido
        response = self.client.post(
            reverse("paste_box"),
            {"report_file": uploaded_file}
        )
        
        self.assertRedirects(response, reverse("dashboard"))
        
        # Verificar creación de transacciones
        tx_consumo = Transaction.objects.get(description="CONSUMO EXCLUSIVO")
        self.assertEqual(tx_consumo.amount_ves, Decimal("350.00"))
        self.assertEqual(tx_consumo.card, self.visa)
        
        tx_pago = Transaction.objects.get(description="PAGO: ABONO EN TAQUILLA")
        self.assertEqual(tx_pago.amount_ves, Decimal("-350.00"))  # Debe ser negativo por ser pago
        
        # Verificar prevención de duplicados (ingesta doble)
        uploaded_file.seek(0)
        response_dup = self.client.post(
            reverse("paste_box"),
            {"report_file": uploaded_file}
        )
        self.assertRedirects(response_dup, reverse("dashboard"))
        
        # El número total de transacciones debe seguir siendo 2
        self.assertEqual(Transaction.objects.filter(card=self.visa).count(), 2)


class CardCrudAndStatusTransitionTestCase(TestCase):
    """Pruebas unitarias para el CRUD de tarjetas y la transición de estados de facturación."""

    def setUp(self):
        self.card = CreditCard.objects.create(
            name="Tarjeta de Prueba",
            last_four="9999",
            cutoff_day=15,
            payment_day=5
        )

    def test_dynamic_status_transition_past_due(self):
        # Transacción con corte el 15 de Febrero de 2026.
        # Hoy es 21 de Mayo de 2026.
        # Por lo tanto, la fecha de corte asignada (15-Feb-2026) ya transcurrió.
        tx = Transaction.objects.create(
            card=self.card,
            type='TDC',
            booking_date=timezone.make_aware(datetime.datetime(2026, 2, 10, 12, 0)),
            description="Consumo Febrero",
            amount_ves=Decimal("1500.00"),
            reference="999901",
            status='PENDIENTE'
        )
        
        # Al crearse, el estado por defecto es PENDIENTE
        self.assertEqual(tx.status, 'PENDIENTE')
        self.assertEqual(tx.fecha_corte_asignada, datetime.date(2026, 2, 15))
        
        # Ejecutar update_statuses simulando que hoy es 21 de Mayo de 2026
        today = datetime.date(2026, 5, 21)
        updated = Transaction.update_statuses(today=today)
        
        # Debe haber actualizado 1 transacción
        self.assertEqual(updated, 1)
        
        # Refrescar y comprobar que el estado cambió a CORTADO_NO_PAGADO
        tx.refresh_from_db()
        self.assertEqual(tx.status, 'CORTADO_NO_PAGADO')

    def test_card_crud_operations(self):
        # 1. Crear una tarjeta adicional por POST
        response_create = self.client.post(
            reverse("card_list"),
            {
                "name": "Visa Nueva",
                "last_four": "8888",
                "cutoff_day": "10",
                "payment_day": "5"
            }
        )
        self.assertRedirects(response_create, reverse("card_list"))
        self.assertTrue(CreditCard.objects.filter(last_four="8888").exists())
        
        new_card = CreditCard.objects.get(last_four="8888")
        
        # 2. Editar la tarjeta por POST
        response_edit = self.client.post(
            reverse("card_edit", kwargs={"pk": new_card.pk}),
            {
                "name": "Visa Nueva Editada",
                "last_four": "8888",
                "cutoff_day": "12",
                "payment_day": "8"
            }
        )
        self.assertRedirects(response_edit, reverse("card_list"))
        
        new_card.refresh_from_db()
        self.assertEqual(new_card.name, "Visa Nueva Editada")
        self.assertEqual(new_card.cutoff_day, 12)
        self.assertEqual(new_card.payment_day, 8)
        
        # 3. Eliminar la tarjeta y sus transacciones asociadas por POST
        # Primero le creamos una transacción
        Transaction.objects.create(
            card=new_card,
            type='TDC',
            booking_date=timezone.now(),
            description="Consumo Temporal",
            amount_ves=Decimal("10.00"),
            reference="temp-ref"
        )
        
        self.assertEqual(Transaction.objects.filter(card=new_card).count(), 1)
        
        # Eliminar
        response_delete = self.client.post(
            reverse("card_delete", kwargs={"pk": new_card.pk})
        )
        self.assertRedirects(response_delete, reverse("card_list"))
        
        # Comprobar eliminación en cascada
        self.assertFalse(CreditCard.objects.filter(last_four="8888").exists())
        self.assertEqual(Transaction.objects.filter(card=new_card).count(), 0)

    def test_fifo_payment_reconciliation(self):
        """
        Valida que un conjunto de consumos en febrero sea cubierto
        por un pago posterior en el mismo ciclo, cambiando su estado
        correctamente a PAGADO mediante el algoritmo FIFO.
        """
        # Crear tarjeta Visa Dorada Banesco de prueba para el escenario
        visa_feb = CreditCard.objects.create(
            name="Visa Banesco Feb Test",
            last_four="2049",
            cutoff_day=12,
            payment_day=8
        )
        
        # 1. Crear los 3 consumos descritos por el usuario
        c1 = Transaction.objects.create(
            card=visa_feb,
            type='TDC',
            booking_date=timezone.make_aware(datetime.datetime(2026, 2, 14, 10, 0)),
            description="Consumo Feb 1",
            amount_ves=Decimal("4140.00"),
            reference="ref-c1"
        )
        c2 = Transaction.objects.create(
            card=visa_feb,
            type='TDC',
            booking_date=timezone.make_aware(datetime.datetime(2026, 2, 14, 11, 0)),
            description="Consumo Feb 2",
            amount_ves=Decimal("1812.74"),
            reference="ref-c2"
        )
        c3 = Transaction.objects.create(
            card=visa_feb,
            type='TDC',
            booking_date=timezone.make_aware(datetime.datetime(2026, 2, 17, 10, 0)),
            description="Consumo Feb 3",
            amount_ves=Decimal("12875.21"),
            reference="ref-c3"
        )
        
        # Total consumos febrero = 4140.00 + 1812.74 + 12875.21 = 18827.95
        
        # 2. Crear el pago de Bs. -36077.08
        pago = Transaction.objects.create(
            card=visa_feb,
            type='TDC',
            booking_date=timezone.make_aware(datetime.datetime(2026, 2, 26, 12, 0)),
            description="PAGO HOMEBANKIN",
            amount_ves=Decimal("-36077.08"),
            reference="ref-p1"
        )
        
        # 3. Crear un consumo en marzo para verificar amortización del remanente (36077.08 - 18827.95 = 17249.13)
        # Este consumo es de 5000.00, por lo que debe ser cubierto enteramente por el remanente.
        c4 = Transaction.objects.create(
            card=visa_feb,
            type='TDC',
            booking_date=timezone.make_aware(datetime.datetime(2026, 3, 10, 10, 0)),
            description="Consumo Mar 4 (Cubierto por remanente)",
            amount_ves=Decimal("5000.00"),
            reference="ref-c4"
        )
        
        # Este consumo es de 20000.00, supera el remanente restante (17249.13 - 5000.00 = 12249.13).
        # Por lo tanto, no se cubre completamente y debe pasar a CORTADO_NO_PAGADO si ya pasó su corte.
        c5 = Transaction.objects.create(
            card=visa_feb,
            type='TDC',
            booking_date=timezone.make_aware(datetime.datetime(2026, 3, 11, 10, 0)),
            description="Consumo Mar 5 (Excede remanente)",
            amount_ves=Decimal("20000.00"),
            reference="ref-c5"
        )
        
        # Ejecutar la reconciliación simulando hoy como 21 de Mayo de 2026 (todos los cortes transcurridos)
        today = datetime.date(2026, 5, 21)
        Transaction.update_statuses(today=today)
        
        # Refrescar desde la base de datos
        c1.refresh_from_db()
        c2.refresh_from_db()
        c3.refresh_from_db()
        c4.refresh_from_db()
        c5.refresh_from_db()
        pago.refresh_from_db()
        
        # Aserciones
        self.assertEqual(c1.status, 'PAGADO')
        self.assertEqual(c2.status, 'PAGADO')
        self.assertEqual(c3.status, 'PAGADO')
        self.assertEqual(pago.status, 'PAGADO')
        self.assertEqual(c4.status, 'PAGADO')
        self.assertEqual(c5.status, 'CORTADO_NO_PAGADO')


class AmpliacionTresTestCase(TestCase):
    """Pruebas unitarias para la ampliación 3: pagos manuales, intereses y tasas duales."""

    def setUp(self):
        self.card = CreditCard.objects.create(
            name="Visa Platinum Test",
            last_four="4444",
            cutoff_day=12,
            payment_day=8,
            mora_rate=Decimal("40.00"),
            card_type_display="VISA PLATINUM",
            theme_color="platinum"
        )
        self.rate_log = ExchangeRateLog.objects.create(
            date=datetime.date(2026, 5, 10),
            bcv_rate=Decimal("36.5000"),
            binance_rate=Decimal("38.0000")
        )

    def test_dual_usd_indexed_exchange_rates(self):
        tx = Transaction.objects.create(
            card=self.card,
            type='TDC',
            booking_date=timezone.make_aware(datetime.datetime(2026, 5, 10, 10, 0)),
            description="Consumo Dual Tasa",
            amount_ves=Decimal("365.00"),
            reference="ref-dual",
            exchange_rate=self.rate_log
        )
        # Tasa BCV = 36.5000 -> amount_usd_bcv = 365.00 / 36.5000 = 10.00
        # Tasa Binance = 38.0000 -> amount_usd_binance = 365.00 / 38.0000 = 9.605...
        self.assertEqual(tx.amount_usd_bcv, Decimal("10.00"))
        self.assertAlmostEqual(tx.amount_usd_binance, Decimal("9.61"), places=2)

    def test_dynamic_interest_accrual_past_due(self):
        # Consumo con fecha de corte el 12 de Abril. Límite de pago: 8 de Mayo.
        # Simulamos que hoy es 18 de Mayo (10 días de mora después del 8 de Mayo).
        # Tasa de interés anual = 40%.
        # Interés diario = 40% / 100 / 360 = 0.001111...
        # Monto = Bs. 9000.00
        # Interés acumulado en 10 días = 9000 * (40 / 100 / 360) * 10 = 9000 * 0.001111 * 10 = 100.00 Bs.
        tx = Transaction.objects.create(
            card=self.card,
            type='TDC',
            booking_date=timezone.make_aware(datetime.datetime(2026, 4, 10, 12, 0)),
            description="Consumo Abril",
            amount_ves=Decimal("9000.00"),
            reference="ref-int-1",
            status='CORTADO_NO_PAGADO'  # Ya cortada
        )
        
        # Simulamos que la fecha límite es 8 de Mayo
        self.assertEqual(tx.fecha_limite_pago, datetime.date(2026, 5, 8))
        
        # Con fecha simulada 18 de Mayo (10 días de mora)
        with patch('django.utils.timezone.localdate') as mock_localdate:
            mock_localdate.return_value = datetime.date(2026, 5, 18)
            interest = tx.projected_interest
            self.assertEqual(interest, Decimal("100.00"))
            
        # Si hoy es <= 8 de Mayo, el interés debe ser cero
        with patch('django.utils.timezone.localdate') as mock_localdate:
            mock_localdate.return_value = datetime.date(2026, 5, 8)
            interest = tx.projected_interest
            self.assertEqual(interest, Decimal("0.00"))

    def test_manual_payment_reconciliation_fifo(self):
        # 1. Crear un consumo pendiente por corte
        tx_consumo = Transaction.objects.create(
            card=self.card,
            type='TDC',
            booking_date=timezone.make_aware(datetime.datetime(2026, 5, 10, 12, 0)),
            description="Consumo Pendiente",
            amount_ves=Decimal("1500.00"),
            reference="ref-cons-1",
            status='PENDIENTE'
        )

        # 2. Hacer POST a ManualPaymentView para registrar un pago de Bs. 1500
        response = self.client.post(
            reverse("manual_payment"),
            {
                "card_id": self.card.id,
                "booking_date": "2026-05-11T15:30",
                "amount_ves": "1500.00",
                "reference": "ref-pay-1",
                "description": "Pago Manual de Prueba"
            }
        )
        self.assertRedirects(response, reverse("dashboard"))

        # Refrescar transacción
        tx_consumo.refresh_from_db()
        
        # Comprobar que el consumo pasó a PAGADO
        self.assertEqual(tx_consumo.status, 'PAGADO')
        
        # Comprobar que se creó el registro de pago negativo en la base de datos
        pago = Transaction.objects.get(reference="ref-pay-1")
        self.assertEqual(pago.amount_ves, Decimal("-1500.00"))
        self.assertEqual(pago.status, 'PAGADO')


class BanescoNormativeFinanceTestCase(TestCase):
    """Pruebas unitarias para validar las tasas de interés nominales/moratorias de Banesco."""

    def setUp(self):
        self.visa_dorada = CreditCard.objects.create(
            name="Visa Dorada Banesco",
            last_four="1111",
            cutoff_day=12,
            payment_day=8,
            credit_limit=Decimal("100000.00"),
            interest_rate=Decimal("60.00"),
            mora_rate=Decimal("3.00"),
            card_type_display="VISA DORADA",
            theme_color="gold"
        )

    def test_ordinary_projected_interest_calculation(self):
        # Gasto el 14/02/2026. Corte el 12/03/2026.
        # Diferencia de días: 14/02/2026 al 28/02/2026 (14 días) + 12 días de marzo = 26 días.
        # Monto: Bs. 10,000.00. Tasa: 60.00%.
        # Interés ordinario = 10000 * 0.60 * (26 / 360) = 433.333... Bs. -> quantize a 433.33.
        tx = Transaction.objects.create(
            card=self.visa_dorada,
            type='TDC',
            booking_date=timezone.make_aware(datetime.datetime(2026, 2, 14, 10, 0)),
            description="Gasto Visa Dorada",
            amount_ves=Decimal("10000.00"),
            reference="ref-dorada-1",
            status='PENDIENTE'
        )

        self.assertEqual(tx.fecha_corte_asignada, datetime.date(2026, 3, 12))
        self.assertEqual(tx.fecha_limite_pago, datetime.date(2026, 4, 8))

        projected_interest = tx.calculate_projected_interest()
        self.assertEqual(projected_interest, Decimal("433.33"))

    def test_mora_interest_calculation(self):
        # Gasto el 14/02/2026. Corte el 12/03/2026. Límite de pago: 08/04/2026.
        # Simulamos que hoy es 18/04/2026 (10 días de mora tras la fecha límite del 08/04/2026).
        # Monto: Bs. 10,000.00. Tasa de mora: 3.00%.
        # Interés de mora = 10000 * 0.03 * (10 / 360) = 8.333... Bs. -> quantize a 8.33.
        tx = Transaction.objects.create(
            card=self.visa_dorada,
            type='TDC',
            booking_date=timezone.make_aware(datetime.datetime(2026, 2, 14, 10, 0)),
            description="Gasto Visa Dorada",
            amount_ves=Decimal("10000.00"),
            reference="ref-dorada-2",
            status='CORTADO_NO_PAGADO'
        )

        # Con fecha simulada 18 de Abril de 2026 (10 días de mora)
        today = datetime.date(2026, 4, 18)
        mora_interest = tx.calculate_mora_interest(today=today)
        self.assertEqual(mora_interest, Decimal("8.33"))

        # Si hoy es <= 8 de Abril, el interés de mora debe ser cero
        today_on_time = datetime.date(2026, 4, 8)
        mora_interest_zero = tx.calculate_mora_interest(today=today_on_time)
        self.assertEqual(mora_interest_zero, Decimal("0.00"))


class ChronologicalCycleSimulationTestCase(TestCase):
    """Pruebas unitarias para la medición cronológica del ciclo de facturación y apalancamiento."""

    def setUp(self):
        self.visa_dorada = CreditCard.objects.create(
            name="Visa Dorada Test",
            last_four="1122",
            cutoff_day=12,
            payment_day=8,
            credit_limit=Decimal("50000.00"),
            interest_rate=Decimal("60.00"),
            mora_rate=Decimal("3.00")
        )

    def test_chronological_simulation_fields(self):
        # 1. Simular consumo justo el día de corte (12 de Mayo de 2026) -> 100% transcurrido
        today_cutoff = datetime.date(2026, 5, 12)
        sim = self.visa_dorada.get_financing_simulation(target_date=today_cutoff)
        
        self.assertEqual(sim["cycle_end_date"], datetime.date(2026, 5, 12))
        self.assertEqual(sim["cycle_start_date"], datetime.date(2026, 4, 13))
        self.assertEqual(sim["cycle_total_days"], 30) # Del 12 de Abril al 12 de Mayo hay 30 días
        self.assertEqual(sim["cycle_days_elapsed"], 30)
        self.assertEqual(sim["cycle_elapsed_percent"], 100.0)

        # 2. Simular consumo el día siguiente al corte (13 de Mayo de 2026) -> 0% de transcurso (0 días desde corte anterior)
        # Nota: el anterior corte es 12 de Mayo, el corte activo es 12 de Junio.
        today_start = datetime.date(2026, 5, 13)
        sim_start = self.visa_dorada.get_financing_simulation(target_date=today_start)
        
        self.assertEqual(sim_start["cycle_end_date"], datetime.date(2026, 6, 12))
        self.assertEqual(sim_start["cycle_start_date"], datetime.date(2026, 5, 13))
        self.assertEqual(sim_start["cycle_total_days"], 31) # Del 12 de Mayo al 12 de Junio hay 31 días
        self.assertEqual(sim_start["cycle_days_elapsed"], 1) # 13 de Mayo es 1 día transcurrido desde anterior corte (12 de Mayo)
        self.assertAlmostEqual(sim_start["cycle_elapsed_percent"], (1 / 31) * 100, places=2)


class BanescoJunctionReconciliationTestCase(TestCase):
    """Pruebas unitarias para el Módulo de Conciliación Bancaria y Expansión de Ingesta."""

    def setUp(self):
        from .models import CreditCard, BankAccount, ExchangeRateLog
        self.bank_account = BankAccount.objects.create(
            name="Cuenta Corriente Banesco",
            account_number="01340000000000000000",
            last_four="0000",
            initial_balance=Decimal("5000.00")
        )
        self.debit_card = CreditCard.objects.create(
            name="Tarjeta de Débito",
            last_four="0000",
            cutoff_day=None,
            payment_day=None,
            associated_account=self.bank_account
        )
        self.credit_card = CreditCard.objects.create(
            name="Visa Dorada Banesco",
            last_four="1111",
            cutoff_day=12,
            payment_day=8,
            associated_account=self.bank_account
        )
        self.rate_log = ExchangeRateLog.objects.create(
            date=datetime.date(2026, 5, 22),
            bcv_rate=Decimal("36.50"),
            binance_rate=Decimal("37.00")
        )

    def test_parse_banesco_bank_statement_success(self):
        from .parser import parse_banesco_bank_statement
        
        # Simular el contenido del reporte TXT exportado de Banesco Online
        statement_content = (
            "Fecha      Referencia       Descripción                         Monto                  Saldo\n"
            "22/05/2026 123456789        COMPRA POS CTA/CTE DIST EL MERCADO   -1.000,00              4.000,00\n"
            "22/05/2026 987654321        TRANSFERENCIA RECIBIDA              +2.000,00              6.000,00\n"
        )
        
        parsed = parse_banesco_bank_statement(statement_content)
        self.assertEqual(len(parsed), 2)
        
        # Primera fila (Compra POS)
        self.assertEqual(parsed[0]["reference"], "123456789")
        self.assertEqual(parsed[0]["description"], "COMPRA POS CTA/CTE DIST EL MERCADO")
        self.assertEqual(parsed[0]["amount_ves"], Decimal("-1000.00"))
        self.assertEqual(parsed[0]["balance_ves"], Decimal("4000.00"))
        
        # Segunda fila (Abono)
        self.assertEqual(parsed[1]["reference"], "987654321")
        self.assertEqual(parsed[1]["description"], "TRANSFERENCIA RECIBIDA")
        self.assertEqual(parsed[1]["amount_ves"], Decimal("2000.00"))
        self.assertEqual(parsed[1]["balance_ves"], Decimal("6000.00"))

    def test_bank_account_initial_and_current_balance(self):
        from .models import BankAccountTransaction
        
        # Validar saldo inicial
        self.assertEqual(self.bank_account.current_balance, Decimal("5000.00"))
        
        # Agregar transacción
        BankAccountTransaction.objects.create(
            account=self.bank_account,
            booking_date=timezone.now(),
            reference="10001",
            description="Compra Harina PAN",
            amount_ves=Decimal("-200.00"),
            balance_ves=Decimal("4800.00"),
            exchange_rate=self.rate_log
        )
        
        # Saldo debe disminuir
        self.assertEqual(self.bank_account.current_balance, Decimal("4800.00"))
        
        # Agregar abono
        BankAccountTransaction.objects.create(
            account=self.bank_account,
            booking_date=timezone.now(),
            reference="10002",
            description="Pago Nomina",
            amount_ves=Decimal("1500.00"),
            balance_ves=Decimal("6300.00"),
            exchange_rate=self.rate_log
        )
        
        # Saldo actual debe aumentar
        self.assertEqual(self.bank_account.current_balance, Decimal("6300.00"))

    def test_tdd_trace_reconciliation_and_auto_creation(self):
        from .models import Transaction, BankAccountTransaction, TransactionReconciliation
        from .reconciliation import ReconciliationEngine
        
        # Caso A: Reconciliación con compra de débito (TDD) existente por correo
        # El correo tiene Trace de 6 dígitos. El banco tiene referencia de 11 dígitos.
        debit_email_tx = Transaction.objects.create(
            card=self.debit_card,
            type='DEBIT',
            booking_date=timezone.make_aware(datetime.datetime(2026, 5, 22, 12, 11, 49)),
            description="Retiro/Compra Tarjeta de Débito Banesco",
            amount_ves=Decimal("932.33"),
            reference="341428",  # Trace de correo
            status='PENDIENTE',
        )
        
        # Limpiar la reconciliación y movimiento de cuenta manual creados automáticamente en el save()
        # del modelo para poder probar la conciliación del ReconciliationEngine de forma aislada
        TransactionReconciliation.objects.all().delete()
        BankAccountTransaction.objects.filter(is_manual=True).delete()
        
        bank_tx = BankAccountTransaction.objects.create(
            account=self.bank_account,
            booking_date=timezone.make_aware(datetime.datetime(2026, 5, 22, 12, 11, 49)),
            reference="00041428",  # Referencia del banco
            description="COMPRA POS CTA/CTE DIST MERCADITO",
            amount_ves=Decimal("-932.33"),
            balance_ves=Decimal("4067.67"),
            exchange_rate=self.rate_log
        )
        
        reconciled_count = ReconciliationEngine.reconcile_account(self.bank_account)
        self.assertEqual(reconciled_count, 1)
        
        # Recargar de BD
        bank_tx.refresh_from_db()
        debit_email_tx.refresh_from_db()
        
        # Verificar la reconciliación vía tabla pivot
        reconciliation_exists = TransactionReconciliation.objects.filter(
            bank_transaction=bank_tx,
            card_transaction=debit_email_tx
        ).exists()
        self.assertTrue(reconciliation_exists)
        self.assertEqual(bank_tx.reconciliations.count(), 1)
        
        # Caso B: Autocreación de transacciones de débito si no existen en BD
        bank_tx_new = BankAccountTransaction.objects.create(
            account=self.bank_account,
            booking_date=timezone.make_aware(datetime.datetime(2026, 5, 22, 12, 31, 52)),
            reference="00079533",
            description="COMPRA POS CTA/CTE FARMACIA SAAS",
            amount_ves=Decimal("-2056.32"),
            balance_ves=Decimal("2011.35"),
            exchange_rate=self.rate_log
        )
        
        # Corremos la conciliación
        reconciled_count_2 = ReconciliationEngine.reconcile_account(self.bank_account)
        self.assertEqual(reconciled_count_2, 1)
        
        bank_tx_new.refresh_from_db()
        self.assertEqual(bank_tx_new.reconciliations.count(), 1)
        
        auto_debit_tx = bank_tx_new.reconciliations.first().card_transaction
        self.assertEqual(auto_debit_tx.card, self.debit_card)
        self.assertEqual(auto_debit_tx.type, 'DEBIT')
        self.assertEqual(auto_debit_tx.amount_ves, Decimal("2056.32"))
        self.assertEqual(auto_debit_tx.reference, "079533")  # Trace de 6 dígitos

    def test_credit_card_auto_payment_creation(self):
        from .models import Transaction, BankAccountTransaction
        from .reconciliation import ReconciliationEngine
        
        # Registrar deuda de TDC
        Transaction.objects.create(
            card=self.credit_card,
            type='TDC',
            booking_date=timezone.make_aware(datetime.datetime(2026, 5, 10, 10, 0)),
            description="Consumo de prueba",
            amount_ves=Decimal("3000.00"),
            reference="555555",
            status='PENDIENTE',
            exchange_rate=self.rate_log
        )
        
        # Simular egreso de banco que representa el pago a la TDC
        bank_payment_tx = BankAccountTransaction.objects.create(
            account=self.bank_account,
            booking_date=timezone.make_aware(datetime.datetime(2026, 5, 22, 15, 0)),
            reference="888888",
            description="PAGO TDC C/C EN CUENTA1111",  # Termina en los 4 dígitos de la tarjeta
            amount_ves=Decimal("-3000.00"),
            balance_ves=Decimal("1000.00"),
            exchange_rate=self.rate_log
        )
        
        # Ejecutar reconciliación
        reconciled_count = ReconciliationEngine.reconcile_account(self.bank_account)
        self.assertEqual(reconciled_count, 1)
        
        bank_payment_tx.refresh_from_db()
        self.assertEqual(bank_payment_tx.reconciliations.count(), 1)
        
        auto_payment_tx = bank_payment_tx.reconciliations.first().card_transaction
        self.assertEqual(auto_payment_tx.card, self.credit_card)
        self.assertEqual(auto_payment_tx.type, 'TDC')
        self.assertEqual(auto_payment_tx.amount_ves, Decimal("-3000.00")) # Abono en negativo!
        
        # Verificar que el estado de consumos de la tarjeta de crédito se haya liquidado a PAGADO
        unpaid_consumptions = Transaction.objects.filter(card=self.credit_card, amount_ves__gt=0, status='PENDIENTE')
        self.assertFalse(unpaid_consumptions.exists())

    def test_bank_transaction_consolidation_matching(self):
        """
        Valida que bajo la Opción C (Muchos a Muchos), un único movimiento consolidado de banco (Bs. 3000)
        puede conciliarse con múltiples abonos de TDC (dos de Bs. 1500 cada uno), creando exactamente
        dos registros en la tabla intermedia TransactionReconciliation.
        """
        from django.db.models import Sum
        from .models import Transaction, BankAccountTransaction, TransactionReconciliation
        
        # Simular dos abonos/pagos de TDC independientes en el sistema
        pay1 = Transaction.objects.create(
            card=self.credit_card,
            type='TDC',
            booking_date=timezone.make_aware(datetime.datetime(2026, 5, 22, 10, 0)),
            description="Pago A",
            amount_ves=Decimal("-1500.00"),
            reference="111222",
            status='PAGADO',
            exchange_rate=self.rate_log
        )
        pay2 = Transaction.objects.create(
            card=self.credit_card,
            type='TDC',
            booking_date=timezone.make_aware(datetime.datetime(2026, 5, 22, 11, 0)),
            description="Pago B",
            amount_ves=Decimal("-1500.00"),
            reference="333444",
            status='PAGADO',
            exchange_rate=self.rate_log
        )
        
        # Crear un único movimiento de banco consolidado por el total (Bs. 3000)
        bank_tx = BankAccountTransaction.objects.create(
            account=self.bank_account,
            booking_date=timezone.make_aware(datetime.datetime(2026, 5, 22, 15, 0)),
            reference="999999",
            description="PAGO TDC CONSOLIDADO",
            amount_ves=Decimal("-3000.00"),
            balance_ves=Decimal("1000.00"),
            exchange_rate=self.rate_log
        )
        
        # Conciliar de forma cruzada usando la tabla pivot
        rec1 = TransactionReconciliation.objects.create(
            bank_transaction=bank_tx,
            card_transaction=pay1,
            reconciled_amount=Decimal("1500.00")
        )
        rec2 = TransactionReconciliation.objects.create(
            bank_transaction=bank_tx,
            card_transaction=pay2,
            reconciled_amount=Decimal("1500.00")
        )
        
        # Verificar la relación cruzada y el saldo total conciliado en la base de datos
        self.assertEqual(bank_tx.reconciliations.count(), 2)
        self.assertEqual(pay1.reconciliations.count(), 1)
        self.assertEqual(pay2.reconciliations.count(), 1)
        
        # Validar la suma de montos conciliados del movimiento de banco
        total_reconciled = bank_tx.reconciliations.aggregate(total=Sum('reconciled_amount'))['total']
        self.assertEqual(total_reconciled, Decimal("3000.00"))

    def test_assisted_pago_movil_ingress_flow(self):
        """Valida el registro exitoso de un Pago Móvil de tipo Ingreso en el banco."""
        from django.urls import reverse
        from .models import BankAccountTransaction
        
        # Simular POST al Pago Móvil con flow_type='ingress'
        url = reverse('pago_movil')
        data = {
            'amount_ves': '4500.50',
            'reference': '99887766',
            'description': 'Cobro de prueba por servicio prestado',
            'flow_type': 'ingress'
        }
        
        # Ejecutar la petición
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Debe redireccionar al dashboard
        
        # Verificar que el movimiento se haya creado en BankAccountTransaction con monto positivo
        ingress_tx = BankAccountTransaction.objects.filter(reference='99887766').first()
        self.assertIsNotNone(ingress_tx)
        self.assertEqual(ingress_tx.amount_ves, Decimal("4500.50"))
        self.assertEqual(ingress_tx.description, 'Cobro de prueba por servicio prestado')

    def test_bank_account_crud_operations(self):
        """Valida las operaciones de creación, edición y eliminación de cuentas bancarias."""
        from django.urls import reverse
        from .models import BankAccount
        
        # 1. Crear una cuenta bancaria por POST
        response_create = self.client.post(
            reverse("account_create"),
            {
                "name": "Cuenta Banesco Adicional",
                "account_number": "01349999999999999999",
                "initial_balance": "2500.50"
            }
        )
        self.assertRedirects(response_create, reverse("card_list"))
        self.assertTrue(BankAccount.objects.filter(last_four="9999").exists())
        
        account = BankAccount.objects.get(last_four="9999")
        self.assertEqual(account.name, "Cuenta Banesco Adicional")
        self.assertEqual(account.initial_balance, Decimal("2500.50"))
        
        # 2. Editar la cuenta por POST
        response_edit = self.client.post(
            reverse("account_edit", kwargs={"pk": account.pk}),
            {
                "name": "Cuenta Banesco Editada",
                "account_number": "01349999999999998888",
                "initial_balance": "3000.00"
            }
        )
        self.assertRedirects(response_edit, reverse("card_list"))
        
        account.refresh_from_db()
        self.assertEqual(account.name, "Cuenta Banesco Editada")
        self.assertEqual(account.last_four, "8888")
        self.assertEqual(account.initial_balance, Decimal("3000.00"))
        
        # 3. Eliminar la cuenta por POST
        response_delete = self.client.post(
            reverse("account_delete", kwargs={"pk": account.pk})
        )
        self.assertRedirects(response_delete, reverse("card_list"))
        self.assertFalse(BankAccount.objects.filter(pk=account.pk).exists())

    def test_card_edit_associates_bank_account(self):
        """Valida que al editar una tarjeta se pueda vincular o cambiar la cuenta bancaria asociada."""
        from django.urls import reverse
        from .models import CreditCard, BankAccount
        
        # Crear otra cuenta bancaria para cambiar la asociación
        other_account = BankAccount.objects.create(
            name="Otra Cuenta Banesco",
            account_number="01347777777777777777",
            last_four="7777",
            initial_balance=Decimal("1000.00")
        )
        
        # Editar tarjeta existente (self.debit_card) para apuntar a other_account
        response = self.client.post(
            reverse("card_edit", kwargs={"pk": self.debit_card.pk}),
            {
                "name": self.debit_card.name,
                "last_four": self.debit_card.last_four,
                "cutoff_day": "",
                "payment_day": "",
                "card_type_display": "DÉBITO BANESCO",
                "theme_color": "green",
                "associated_account": other_account.id,
                "credit_limit": "0.00",
                "interest_rate": "0.00",
                "mora_rate": "0.00"
            }
        )
        self.assertRedirects(response, reverse("card_list"))
        
        self.debit_card.refresh_from_db()
        self.assertEqual(self.debit_card.associated_account, other_account)

    def test_debit_card_transaction_creates_bank_transaction_and_reconciles(self):
        """
        Verifica que al guardar una Transaction de tipo DEBIT (Tarjeta de Débito)
        se crea automáticamente un movimiento bancario manual negativo y se reconcilian.
        """
        from .models import Transaction, BankAccountTransaction, TransactionReconciliation
        
        # Crear transacción de TDD
        tx = Transaction.objects.create(
            card=self.debit_card,
            type='DEBIT',
            booking_date=timezone.now(),
            description="Compra Supermercado TDD",
            amount_ves=Decimal("1500.00"),
            reference="987654",
            exchange_rate=self.rate_log
        )
        
        # Verificar que el status se marca automáticamente como PAGADO
        self.assertEqual(tx.status, 'PAGADO')
        
        # Verificar que se creó el BankAccountTransaction manual correspondiente (egreso, negativo)
        bank_tx = BankAccountTransaction.objects.filter(
            account=self.bank_account,
            is_manual=True,
            amount_ves=Decimal("-1500.00")
        ).first()
        self.assertIsNotNone(bank_tx)
        self.assertEqual(bank_tx.reference, "987654")
        self.assertEqual(bank_tx.description, "Compra Supermercado TDD")
        
        # Verificar que están enlazados mediante TransactionReconciliation
        recon = TransactionReconciliation.objects.filter(
            bank_transaction=bank_tx,
            card_transaction=tx
        ).first()
        self.assertIsNotNone(recon)
        self.assertEqual(recon.reconciled_amount, Decimal("1500.00"))

    def test_official_statement_import_confirms_manual_transaction(self):
        """
        Verifica que la importación de un estado de cuenta oficial (is_manual=False)
        que coincide con un movimiento manual (is_manual=True) lo confirma, reasocia
        la reconciliación y elimina el duplicado manual.
        """
        from .models import Transaction, BankAccountTransaction, TransactionReconciliation
        
        # 1. Crear transacción de débito que genera automáticamente el movimiento manual
        tx = Transaction.objects.create(
            card=self.debit_card,
            type='DEBIT',
            booking_date=timezone.now(),
            description="Compra Tienda TDD",
            amount_ves=Decimal("2500.00"),
            reference="123456",
            exchange_rate=self.rate_log
        )
        
        # Comprobar estado inicial
        manual_tx = BankAccountTransaction.objects.filter(reference="123456", is_manual=True).first()
        self.assertIsNotNone(manual_tx)
        
        # 2. Simular importación de estado de cuenta oficial (is_manual=False) con la misma referencia (o difusa)
        official_tx = BankAccountTransaction.objects.create(
            account=self.bank_account,
            booking_date=timezone.now(),
            reference="000123456",  # Referencia difusa con ceros a la izquierda
            description="COMPRA POS CTA/CTE TIENDA",
            amount_ves=Decimal("-2500.00"),
            balance_ves=Decimal("5000.00"),
            is_manual=False,
            exchange_rate=self.rate_log
        )
        
        # 3. Comprobar que el movimiento manual fue eliminado
        self.assertFalse(BankAccountTransaction.objects.filter(pk=manual_tx.pk).exists())
        
        # 4. Comprobar que el movimiento oficial existe en la base de datos
        self.assertTrue(BankAccountTransaction.objects.filter(pk=official_tx.pk).exists())
        
        # 5. Comprobar que la reconciliación se re-asoció correctamente al movimiento oficial
        recon = TransactionReconciliation.objects.filter(card_transaction=tx).first()
        self.assertIsNotNone(recon)
        self.assertEqual(recon.bank_transaction, official_tx)
        self.assertEqual(recon.reconciled_amount, Decimal("2500.00"))

    def test_multi_account_support_and_selection(self):
        """
        Valida que el sistema soporte múltiples cuentas bancarias de diferentes tipos,
        se filtren y seleccionen correctamente en las vistas y se ingeste Pago Móvil en la cuenta indicada.
        """
        from django.urls import reverse
        from .models import BankAccount, BankAccountTransaction
        
        # 1. Crear una segunda cuenta del tipo Ahorros (savings)
        savings_account = BankAccount.objects.create(
            name="Mi Cuenta Ahorro Banesco",
            account_number="01348888888888888888",
            last_four="8888",
            initial_balance=Decimal("12000.00"),
            account_type="savings"
        )
        
        # Validar tipo de cuenta y clasificación
        self.assertEqual(savings_account.account_type, "savings")
        self.assertEqual(savings_account.get_account_type_display(), "Cuenta de Ahorros")
        
        # 2. Consultar el Dashboard con query params para cada cuenta y validar filtrado
        url_dashboard = reverse('dashboard')
        
        # A. Sin parámetros (debe usar fallback de primera cuenta)
        response_default = self.client.get(url_dashboard)
        self.assertEqual(response_default.status_code, 200)
        self.assertEqual(response_default.context['bank_account'], self.bank_account)
        self.assertEqual(response_default.context['bank_balance_ves'], Decimal("5000.00"))
        
        # B. Pasando account_id de la cuenta de ahorros
        response_savings = self.client.get(f"{url_dashboard}?account_id={savings_account.id}")
        self.assertEqual(response_savings.status_code, 200)
        self.assertEqual(response_savings.context['bank_account'], savings_account)
        self.assertEqual(response_savings.context['bank_balance_ves'], Decimal("12000.00"))
        
        # 3. Procesar un Pago Móvil apuntando explícitamente a la cuenta de ahorros
        url_pago_movil = reverse('pago_movil')
        pago_data = {
            'amount_ves': '1500.00',
            'reference': '77665544',
            'description': 'Pago Móvil de Ahorros',
            'flow_type': 'egress',
            'bank_account_id': savings_account.id
        }
        
        response_pm = self.client.post(url_pago_movil, pago_data)
        self.assertEqual(response_pm.status_code, 302)
        
        # El movimiento debió impactar estrictamente la cuenta de ahorros
        self.assertTrue(BankAccountTransaction.objects.filter(account=savings_account, reference='77665544').exists())
        self.assertFalse(BankAccountTransaction.objects.filter(account=self.bank_account, reference='77665544').exists())
        
        # El balance de la cuenta de ahorros debe actualizarse de forma dinamica
        self.assertEqual(savings_account.current_balance, Decimal("10500.00"))


class ProxyPoolTestCase(TestCase):
    """Tests para el ProxyPool con health checking."""

    def test_round_robin_selection(self):
        """Verifica que los proxies se seleccionen en round-robin."""
        from .services import ProxyPool
        pool = ProxyPool(["proxy1", "proxy2", "proxy3"])
        
        self.assertEqual(pool.get_next(), "proxy1")
        self.assertEqual(pool.get_next(), "proxy2")
        self.assertEqual(pool.get_next(), "proxy3")
        self.assertEqual(pool.get_next(), "proxy1")

    def test_failed_proxy_excluded(self):
        """Verifica que un proxy con 3 fallos sea excluido, pero los demas sigan disponibles."""
        from .services import ProxyPool
        pool = ProxyPool(["proxy1", "proxy2"])
        
        pool.mark_failed("proxy1")
        pool.mark_failed("proxy1")
        self.assertEqual(pool.get_next(), "proxy1")  # 2 fallos, aun disponible
        
        pool.mark_failed("proxy1")  # 3er fallo -> proxy1 excluido
        # proxy2 sigue disponible
        self.assertEqual(pool.get_next(), "proxy2")
        # Solo si ambos fallan retorna None
        pool.mark_failed("proxy2")
        pool.mark_failed("proxy2")
        pool.mark_failed("proxy2")
        self.assertIsNone(pool.get_next())

    def test_empty_pool_returns_none(self):
        """Verifica que un pool vacio retorne None."""
        from .services import ProxyPool
        pool = ProxyPool([])
        self.assertIsNone(pool.get_next())

    def test_reset_all_clears_failures(self):
        """Verifica que reset_all() reacondicione todos los proxies."""
        from .services import ProxyPool
        pool = ProxyPool(["proxy1", "proxy2"])
        
        pool.mark_failed("proxy1")
        pool.mark_failed("proxy1")
        pool.mark_failed("proxy1")
        
        pool.reset_all()
        
        self.assertEqual(pool.get_next(), "proxy1")


class BinanceP2PServiceTestCase(TestCase):
    """Tests para el motor resiliente de scraping Binance P2P."""

    def test_parse_response_success(self):
        """Verifica el parseo correcto del promedio de 3 ofertas."""
        from .services import BinanceP2PService
        from decimal import Decimal
        
        service = BinanceP2PService(proxy_pool=None)
        
        mock_data = {
            "data": [
                {"adv": {"price": "38.50"}},
                {"adv": {"price": "38.60"}},
                {"adv": {"price": "38.40"}},
            ]
        }
        
        rate = service._parse_response(mock_data)
        self.assertEqual(rate, Decimal("38.50"))

    def test_parse_response_empty_data(self):
        """Verifica que retorne None si no hay ofertas."""
        from .services import BinanceP2PService
        
        service = BinanceP2PService(proxy_pool=None)
        
        self.assertIsNone(service._parse_response({"data": []}))
        self.assertIsNone(service._parse_response({}))

    def test_parse_response_missing_prices(self):
        """Verifica manejo de ofertas sin precio."""
        from .services import BinanceP2PService
        from decimal import Decimal
        
        service = BinanceP2PService(proxy_pool=None)
        
        mock_data = {
            "data": [
                {"adv": {"price": "38.50"}},
                {"adv": {}},
                {"adv": {"price": "38.40"}},
            ]
        }
        
        rate = service._parse_response(mock_data)
        self.assertEqual(rate, Decimal("38.45"))

    def test_fetch_with_stdlib_executes(self):
        """Verifica que el flujo stdlib se ejecute (puede retornar tasa real o None)."""
        from .services import BinanceP2PService
        from decimal import Decimal
        
        service = BinanceP2PService(proxy_pool=None)
        
        # El flujo stdlib se ejecuta (puede retornar Decimal real si hay conexion
        # o None si falla). Ambas son respuestas validas.
        rate = service._fetch_with_stdlib()
        # Verificar que返回值 es None o un Decimal valido
        self.assertTrue(rate is None or isinstance(rate, Decimal))

    def test_fetch_rate_fallback_chain(self):
        """Verifica que fetch_rate intente todos los metodos en cadena."""
        from .services import BinanceP2PService
        
        service = BinanceP2PService(proxy_pool=None)
        
        with patch.object(service, '_fetch_with_curl_cffi', return_value=None), \
             patch.object(service, '_fetch_with_httpx', return_value=None), \
             patch.object(service, '_fetch_with_requests', return_value=None), \
             patch.object(service, '_fetch_with_stdlib', return_value=None):
            
            rate = service.fetch_rate()
            self.assertIsNone(rate)

    def test_fetch_rate_uses_first_successful(self):
        """Verifica que curl_cffi sea el primer intento y retorne si tiene exito."""
        from .services import BinanceP2PService
        from decimal import Decimal
        
        service = BinanceP2PService(proxy_pool=None)
        
        with patch.object(service, '_fetch_with_curl_cffi', return_value=Decimal("38.75")):
            rate = service.fetch_rate()
            self.assertEqual(rate, Decimal("38.75"))

    def test_service_singleton(self):
        """Verifica que get_binance_service retorne siempre la misma instancia."""
        from .services import get_binance_service, BinanceP2PService
        
        service1 = get_binance_service()
        service2 = get_binance_service()
        
        self.assertIs(service1, service2)
        self.assertIsInstance(service1, BinanceP2PService)






