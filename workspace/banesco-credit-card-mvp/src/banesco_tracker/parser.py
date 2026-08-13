import re
import datetime
from decimal import Decimal
from django.utils import timezone
import pytz

def clean_amount(amount_str):
    """
    Limpia inconsistencias numéricas del monto de bolívares (miles y decimales).
    Convierte formatos como '1.250,50' o '1,250.50' o '1250.50' a un Decimal limpio.
    """
    amount_str = amount_str.strip()
    
    # Remover símbolos comunes si estuvieran presentes
    amount_str = amount_str.replace("Bs.", "").replace("Bs", "").strip()
    
    # Caso 1: Contiene comas y puntos
    if ',' in amount_str and '.' in amount_str:
        if amount_str.rfind(',') > amount_str.rfind('.'):
            # Coma es el separador decimal, puntos son de miles
            amount_str = amount_str.replace('.', '').replace(',', '.')
        else:
            # Punto es el separador decimal, comas son de miles
            amount_str = amount_str.replace(',', '')
    # Caso 2: Solo contiene comas
    elif ',' in amount_str:
        amount_str = amount_str.replace(',', '.')
        
    return Decimal(amount_str)


class BanescoEmailParser:
    """
    Parser robusto para extraer transacciones a partir del bloque de texto
    del correo diario de Banesco.
    """
    
    # Patrón TDC: TDC # (?P<card>\d+)\s+Bs\.\s+(?P<amount>[\d.]+)\s+el\s+(?P<date>\d{2}-\d{2}-\d{4})\s+(?P<time>\d{2}:\d{2})\s+Ref\s+(?P<ref>\d+)
    TDC_REGEX = re.compile(
        r'TDC # (?P<card>\d+)\s+Bs\.\s+(?P<amount>[\d.,]+)\s+el\s+(?P<date>\d{2}-\d{2}-\d{4})\s+(?P<time>\d{2}:\d{2})\s+Ref\s+(?P<ref>\d+)'
    )
    
    # Patrón Débito: Nro. Tr:.*?(?P<card>\d{4})\nFecha: (?P<date>\d{2}/\d{2}/\d{4})\nHora: (?P<time>\d{2}:\d{2}:\d{2})\nMonto: (?P<amount>[\d.,]+)\nNro. de aprob: (?P<ref>\d+)
    # Usamos re.DOTALL para que .*? funcione a través de múltiples líneas si es necesario
    DEBIT_REGEX = re.compile(
        r'Nro\. Tr:.*?(?P<card>\d{4})\s*\n\s*Fecha: (?P<date>\d{2}/\d{2}/\d{4})\s*\n\s*Hora: (?P<time>\d{2}:\d{2}:\d{2})\s*\n\s*Monto: (?P<amount>[\d.,]+)\s*\n\s*Nro\. de aprob: (?P<ref>\d+)',
        re.MULTILINE
    )

    # Patrón Transferencia Bancaria
    TRANSFER_REGEX = re.compile(
        r'Transferencia exitosa.*?al beneficiario (?P<beneficiary>.*?)\.*\r?\n'
        r'.*?asociado al Beneficiario\s*:\s*(?P<beneficiary_account>\d+)\r?\n'
        r'.*?debitada N°\s*:\s*(?P<source_account>[\d*-]+)\r?\n'
        r'.*?Monto\s*:\s*Bs\.\s*(?P<amount>[\d.,]+)\r?\n'
        r'.*?Banco Beneficiario\s*:\s*(?P<beneficiary_bank>.*?)\r?\n'
        r'.*?Recibo N°\s*:\s*(?P<ref>\d+)\r?\n'
        r'.*?Fecha\s*:\s*(?P<date>\d{2}/\d{2}/\d{4})\r?\n'
        r'.*?Hora\s*:\s*(?P<time>\d{2}:\d{2}:\d{2})',
        re.IGNORECASE | re.DOTALL
    )

    @classmethod
    def parse_text(cls, text):
        """
        Parsea un bloque de texto plano buscando transacciones de TDC, Débito y Transferencia.
        Retorna una lista de diccionarios con la información extraída.
        """
        transactions = []
        caracas_tz = pytz.timezone('America/Caracas')
        
        # 1. Parsear transacciones de Tarjeta de Crédito (TDC)
        for match in cls.TDC_REGEX.finditer(text):
            data = match.groupdict()
            try:
                # Combinar fecha y hora
                naive_dt = datetime.datetime.strptime(f"{data['date']} {data['time']}", "%d-%m-%Y %H:%M")
                booking_date = timezone.make_aware(naive_dt, caracas_tz)
                
                amount = clean_amount(data['amount'])
                
                transactions.append({
                    'type': 'TDC',
                    'card_last_four': data['card'][-4:],  # Nos quedamos con los últimos 4 dígitos para match de tarjeta
                    'booking_date': booking_date,
                    'description': "Consumo Tarjeta de Crédito Banesco",
                    'amount_ves': amount,
                    'reference': data['ref'],
                })
            except Exception as e:
                print(f"[Parser] Error al procesar match TDC: {e} | Data: {data}")
                
        # 2. Parsear transacciones de Débito (DEBIT)
        for match in cls.DEBIT_REGEX.finditer(text):
            data = match.groupdict()
            try:
                # Combinar fecha y hora
                naive_dt = datetime.datetime.strptime(f"{data['date']} {data['time']}", "%d/%m/%Y %H:%M:%S")
                booking_date = timezone.make_aware(naive_dt, caracas_tz)
                
                amount = clean_amount(data['amount'])
                
                transactions.append({
                    'type': 'DEBIT',
                    'card_last_four': data['card'],  # Ya son 4 dígitos en la captura de Débito
                    'booking_date': booking_date,
                    'description': "Retiro/Compra Tarjeta de Débito Banesco",
                    'amount_ves': amount,
                    'reference': data['ref'],
                })
            except Exception as e:
                print(f"[Parser] Error al procesar match Débito: {e} | Data: {data}")

        # 3. Parsear transacciones de Transferencia (TRANSFER)
        for match in cls.TRANSFER_REGEX.finditer(text):
            data = match.groupdict()
            try:
                # Combinar fecha y hora
                naive_dt = datetime.datetime.strptime(f"{data['date']} {data['time']}", "%d/%m/%Y %H:%M:%S")
                booking_date = timezone.make_aware(naive_dt, caracas_tz)
                
                amount = clean_amount(data['amount'])
                
                transactions.append({
                    'type': 'TRANSFER',
                    'card_last_four': data['source_account'][-4:] if len(data['source_account']) >= 4 else "0000",
                    'booking_date': booking_date,
                    'description': f"Transferencia a {data['beneficiary'].strip()}",
                    'amount_ves': amount,
                    'reference': data['ref'],
                    'beneficiary_bank': data['beneficiary_bank'].strip(),
                    'beneficiary_account': data['beneficiary_account'],
                })
            except Exception as e:
                print(f"[Parser] Error al procesar match Transferencia: {e} | Data: {data}")
                
        return transactions


def parse_banesco_txt_report(file_content):
    """
    Parses the raw text report exported from Banesco Online Banking.
    Handles multi-line wrapping and state retention for credit card numbers.
    """
    transactions = []
    current_card = None
    caracas_tz = pytz.timezone('America/Caracas')
    
    # Dividir el contenido por saltos de línea crudos
    lines = file_content.split('\n')
    
    # Patrones de extracción específicos
    card_pattern = re.compile(r'(\d{16})')
    date_pattern = re.compile(r'(\d{2}/\d{2}/\d{4})')
    amount_pattern = re.compile(r'([+-]\s*[\d.]+,\d{2})')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # 1. Detectar y actualizar la tarjeta activa si aparece en la línea
        card_match = card_pattern.search(line)
        if card_match:
            current_card = card_match.group(1)[-4:]  # Extrae los últimos 4 dígitos (ej: 2048)
            
        # Ignorar líneas vacías o encabezados del reporte bancario
        if not line or "Tarjeta" in line or "Fecha Proc" in line:
            i += 1
            continue
            
        # 2. Detectar si la línea contiene una fecha de procesamiento válida
        date_match = date_pattern.search(line)
        if date_match:
            date_str = date_match.group(1)
            
            # Limpiar la línea para aislar la descripción intermedia
            clean_line = line
            if card_match:
                clean_line = clean_line.replace(card_match.group(1), "")
            clean_line = clean_line.replace(date_str, "").strip()
            
            # Verificar si el monto está en la misma línea (Caso normal)
            amount_match = amount_pattern.search(clean_line)
            
            if amount_match:
                amount_str = amount_match.group(1)
                description = clean_line.replace(amount_str, "").strip()
            else:
                # Caso de borde: El monto se desbordó a la línea siguiente
                description = clean_line
                amount_str = None
                
                j = i + 1
                while j < len(lines):
                    next_line = lines[j].strip()
                    next_amount_match = amount_pattern.search(next_line)
                    
                    if next_amount_match:
                        amount_str = next_amount_match.group(1)
                        i = j  # Adelantar el puntero principal del bucle
                        break
                    # Break de seguridad: si encuentra otra fecha antes del monto, el archivo está corrupto
                    if date_pattern.search(next_line) or not next_line:
                        break
                    j += 1
            
            # Si logramos consolidar el monto, procesamos la transacción
            if amount_str:
                # Determinar si es un pago (crédito a la tarjeta) o un consumo (débito)
                is_payment = "-" in amount_str
                
                # Normalización del formato numérico de Banesco (+4.140,00 -> 4140.00)
                clean_amount_str = amount_str.replace("+", "").replace("-", "").replace(".", "").replace(",", ".").strip()
                amount_dec = Decimal(clean_amount_str)
                
                # Convertir la fecha a aware timezone
                naive_dt = datetime.datetime.strptime(date_str, "%d/%m/%Y")
                booking_date = timezone.make_aware(naive_dt, caracas_tz)
                
                transactions.append({
                    "type": "TDC",
                    "card_last_four": current_card,
                    "booking_date": booking_date,
                    "description": description,
                    "amount_ves": amount_dec,
                    "is_payment": is_payment,
                    "reference": None  # Este reporte plano omite el número de referencia largo
                })
                
        i += 1
        
    return transactions


def parse_banesco_bank_statement(file_content):
    """
    Parsea el reporte de movimientos de cuenta bancaria (.txt) exportado de Banesco Online.
    """
    transactions = []
    caracas_tz = pytz.timezone('America/Caracas')
    lines = file_content.split('\n')
    
    # Expresión regular robusta para matchear cada fila del estado de cuenta corriente Banesco
    line_pattern = re.compile(
        r'^(?P<date>\d{2}/\d{2}/\d{4})\s+'
        r'(?P<ref>\d{5,15})\s+'
        r'(?P<desc>.+?)\s+'
        r'(?P<amount>[+-]\s*[\d.]+,\d{2})\s+'
        r'(?P<balance>[+-]?\s*[\d.]+,\d{2})\s*$'
    )
    
    for line in lines:
        line = line.strip()
        if not line or "Fecha" in line or "Referencia" in line:
            continue
            
        match = line_pattern.match(line)
        if match:
            data = match.groupdict()
            try:
                date_str = data['date']
                ref_str = data['ref']
                desc_str = data['desc'].strip()
                amount_str = data['amount']
                balance_str = data['balance']
                
                # Conversión de montos con manejo de formato numérico de Banesco (+1.500,00)
                clean_amount_str = amount_str.replace("+", "").replace("-", "").replace(".", "").replace(",", ".").strip()
                amount_dec = Decimal(clean_amount_str)
                # Mantener el signo: egresos en negativo, ingresos en positivo
                if "-" in amount_str:
                    amount_dec = -amount_dec
                
                clean_balance_str = balance_str.replace("+", "").replace("-", "").replace(".", "").replace(",", ".").strip()
                balance_dec = Decimal(clean_balance_str)
                if "-" in balance_str:
                    balance_dec = -balance_dec
                
                naive_dt = datetime.datetime.strptime(date_str, "%d/%m/%Y")
                booking_date = timezone.make_aware(naive_dt, caracas_tz)
                
                transactions.append({
                    "booking_date": booking_date,
                    "reference": ref_str,
                    "description": desc_str,
                    "amount_ves": amount_dec,
                    "balance_ves": balance_dec,
                })
            except Exception as e:
                print(f"[Parser Banco] Error al procesar línea: {line} | Error: {e}")
                
    return transactions


def parse_banesco_transfer_text(text):
    """
    Parsea el bloque de texto extraído de un PDF o pegado de una transferencia Banesco
    y retorna los datos limpios en un diccionario.
    """
    data = {}
    
    # 1. Nro de Recibo
    receipt_match = re.search(r'(?:N° DE RECIBO|Recibo N°)\s*:\s*(\d+)', text, re.IGNORECASE)
    if receipt_match:
        data['reference'] = receipt_match.group(1)
        
    # 2. Fecha
    date_match = re.search(r'Fecha\s*:\s*(\d{2}/\d{2}/\d{4})', text, re.IGNORECASE)
    if date_match:
        data['date'] = date_match.group(1)
        
    # 3. Monto
    monto_match = re.search(r'Monto\s*:\s*([\d.,]+)', text, re.IGNORECASE)
    if not monto_match:
        # Intento multilínea si hay saltos de línea después de la etiqueta
        monto_match = re.search(r'Monto\s*:\s*\n\s*([\d.,]+)', text, re.IGNORECASE)
    if monto_match:
        monto_str = monto_match.group(1).replace(".", "").replace(",", ".").strip()
        data['amount_ves'] = Decimal(monto_str)
        
    # 4. Beneficiario
    benef_match = re.search(r'Beneficiario\s*:\s*([^\n]+)', text, re.IGNORECASE)
    if benef_match:
        data['beneficiary'] = benef_match.group(1).strip()
        
    # 5. Concepto / Descripción
    concept_match = re.search(r'Concepto\s*:\s*([^\n]+)', text, re.IGNORECASE)
    if concept_match:
        data['description'] = concept_match.group(1).strip()
        
    # 6. Cuenta Debitada
    debit_match = re.search(r'debitada\s*(?:N°)?\s*:\s*([\d*-]+)', text, re.IGNORECASE)
    if debit_match:
        data['source_account'] = debit_match.group(1).strip()
        
    return data if 'reference' in data and 'amount_ves' in data else None


def extract_banesco_pdf_receipt(file_bytes):
    """
    Extrae la información de un recibo de transferencia en PDF utilizando pypdf.
    """
    try:
        import pypdf
    except ImportError:
        return None
        
    import io
    try:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
            
        return parse_banesco_transfer_text(text)
    except Exception as e:
        print(f"[PDF Extractor] Error al leer PDF de recibo: {e}")
        return None


