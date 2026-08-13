# Banesco Credit Card Tracker & Indexer MVP 💳📈
**Control de Gastos Indexados y Simulador de Apalancamiento para Tarjetas de Crédito Banesco**

Bienvenido al MVP de **Banesco Credit Card Tracker**, una solución local robusta, modular y premium desarrollada en **Python 3.10+ / Django 5.x** con **Tailwind CSS** en el frontend. Este sistema permite indexar consumos de bolívares (VES) a dólares (USD) a tasas BCV y Binance P2P, parsear notificaciones de correo en lote y simular el apalancamiento financiero exacto de sus tarjetas de crédito.

---

## 🚀 Características Clave

1. **Simulador de Apalancamiento en Tiempo Real**:
   * Calcula de forma interactiva y dinámica los días libres de interés si se realiza un consumo el día de hoy.
   * Renderiza el texto exacto:
     > *"Si compras hoy con **[Nombre de Tarjeta]**, tienes **XX días** de financiamiento libre de interés. Tu fecha límite de pago será el **DD/MM/AAAA**."*
   * Cuenta con **coloración de semáforo** basada en la salud del financiamiento:
     * 🟢 **Verde** (> 35 días libres): Máximo apalancamiento disponible.
     * 🟡 **Amarillo** (20 a 35 días libres): Apalancamiento medio.
     * 🔴 **Rojo** (< 20 días libres): Advertencia, corte próximo o ya superado.

2. **Tracking Dinámico de Ciclos de Facturación**:
   * **Visa Dorada**: Día de Corte = `12` de cada mes | Día Límite de Pago = `08` del mes siguiente.
   * **Mastercard Platinum**: Día de Corte = `03` de cada mes | Día Límite de Pago = `30` del mismo mes.
   * **Tarjetas de Débito Banesco**: Registradas de forma segura con corte y pago nulos (`None`), permitiendo registrar y asociar consumos sin interferir en el simulador de apalancamiento de las TDC.
   * **Control Dinámico de Febrero (Mastercard)**: Desplazamiento automático al último día de febrero (28 o 29 en años bisiestos) cuando la fecha límite calculada excede los límites calendarios del mes.

3. **Motor de Extracción Regex ("Paste Box")**:
   * Procesamiento masivo y en un solo clic mediante pegado de texto.
   * Parsea de manera impecable y simultánea correos de notificaciones de consumo de Banesco Débito y Banesco Crédito.
   * Resuelve y limpia inconsistencias numéricas y de separadores en los montos de bolívares (ej. `Bs. 1.250,50` o `450,75`).
   * Asocia de manera inteligente la tasa de cambio de la fecha de transacción.

4. **Integración e Indexación a USD en Tiempo Real**:
   * Obtiene la tasa del **BCV en vivo** utilizando el endpoint público de `DolarAPI`.
   * Obtiene la tasa de **Binance P2P** promediando las 3 primeras ofertas `SELL` (comerciantes vendiendo USDT para obtener el precio de compra real del usuario) de manera segura simulando cabeceras de navegador.
   * **Caché diario robusto** y políticas de fallback históricos (con edición manual en línea desde la interfaz de usuario).

5. **Base de Datos 100% Independiente**:
   * Cumple con la directriz estricta del operador: la base de datos de usuario de la aplicación es `src/db.sqlite3` de manera totalmente aislada, sin interactuar ni interferir con la base de datos central de tareas del framework `core/airon.sqlite`.

---

## 🛠️ Reglas de Negocio Implementadas

### Lógica de Facturación
* Si la fecha del consumo es **MENOR o IGUAL** al día de corte del mes en curso, el consumo pertenece al ciclo del mes actual.
* Si la fecha del consumo es **MAYOR** al día de corte, el consumo pertenece al ciclo del mes siguiente.
* **Restricción Única de Cuatro Vías**: Para evitar duplicidad de registros en la Paste Box al pegar el mismo correo múltiples veces, se implementó una restricción única a nivel base de datos sobre la combinación: `(tarjeta, fecha_hora_transaccion, monto_ves, referencia)`. Esto evita colisiones involuntarias del mismo día o referencias idénticas legítimas.

---

## 📁 Estructura del Proyecto

El código fuente del MVP se encuentra organizado bajo la siguiente estructura modular:

```text
output/banesco-credit-card-mvp/
├── README.md                  <- Esta guía técnica detallada.
├── spec.md                    <- Especificación técnica inicial del proyecto.
├── state.json                 <- Estado del ciclo de vida del MVP.
└── src/
    ├── db.sqlite3             <- Base de datos SQLite local e independiente.
    ├── manage.py              <- CLI de Django.
    ├── banesco_project/       <- Configuración global del servidor.
    │   ├── __init__.py
    │   ├── asgi.py
    │   ├── settings.py        <- Configuración de base de datos, huso horario y templates.
    │   ├── urls.py
    │   └── wsgi.py
    ├── templates/             <- Plantillas frontend en modo oscuro premium.
    │   ├── base.html          <- Layout maestro responsivo con efectos blur y mensajes.
    │   └── banesco_tracker/
    │       ├── dashboard.html <- Tableros con widgets semafóricos y listado indexado.
    │       ├── paste_box.html <- Área de pegado masivo de notificaciones.
    │       └── rates.html     <- Control interactivo en línea de tasas de cambio.
    └── banesco_tracker/       <- Módulo de lógica de la aplicación.
        ├── migrations/
        ├── models.py          <- Clases CreditCard, ExchangeRateLog y Transaction.
        ├── parser.py          <- Limpieza e inyección regex de notificaciones.
        ├── services.py        <- Consultas de API (BCV & Binance P2P) con caché y fallback.
        ├── tests.py           <- Batería de 16 tests automatizados.
        ├── urls.py
        └── views.py           <- Controladores de vistas y persistencia.
```

---

## 🚀 Guía de Instalación y Despliegue Local

Siga estos sencillos pasos para iniciar y levantar el servidor local en su entorno de desarrollo:

### 1. Preparar el Entorno y Dependencias
Abra su terminal (PowerShell o CMD) y sitúese en la raíz del proyecto en `y:\Proyectos\AIRON-Cast-v1\output\banesco-credit-card-mvp\src`.

* **Instalar librerías necesarias** (Django, Requests y Pytz):
  ```powershell
  pip install django requests pytz
  ```

### 2. Ejecutar Migraciones
Cree la base de datos independiente local `db.sqlite3` y aplique el esquema:
```powershell
python manage.py migrate
```

### 3. Ejecutar la Batería de Tests Automatizados
Valide el 100% de la lógica de negocio (bisiestos, ciclos, limpieza regex, etc.) mediante la suite de QA:
```powershell
python manage.py test banesco_tracker
```
Debería obtener un resultado exitoso similar a:
```text
Ran 16 tests in 3.282s
OK
```

### 4. Levantar el Servidor de Desarrollo
Inicie el servidor local:
```powershell
python manage.py runserver
```
Abra su navegador e ingrese a [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

*Nota: La primera vez que ingrese al Dashboard, el sistema sembrará automáticamente las tarjetas iniciales de muestra (Visa Dorada Banesco, Mastercard Platinum Banesco y Tarjeta de Débito Banesco) en la base de datos local para que comience de inmediato.*

---

## 📧 Formato de Notificaciones Banesco Soportadas

Pegue uno o varios bloques de notificaciones de correo en el **Paste Box** para procesarlos en lote. El parser soporta múltiples formatos de Banesco:

### A. Formato de Notificación de Tarjeta de Crédito (TDC)
```text
Banesco Banco Universal informa que se realizo un consumo con su TDC # 1234 por Bs. 1.500,75 el 21-05-2026 14:30 Ref 987654321 en COMERCIO TEST.
```

### B. Formato de Notificación de Cuenta / Tarjeta de Débito (TDD)
```text
Banesco Banco Universal
Notificacion de Transaccion

Nro. Tr: 000023456789
Cuenta de origen: *******1234
Operacion: Compra Puntos de Venta
Fecha: 21/05/2026
Hora: 14:30:15
Monto: 850,00
Nro. de aprob: 123456
Comercio: SUPERMERCADO TEST
```

---

## 🎨 Arquitectura de Frontend Premium

El diseño frontend se concibió bajo los lineamientos visuales y de UX más exigentes:
* **Diseño UI en Modo Oscuro**: Paleta de colores armoniosos en Slate, Emerald (para estados seguros) y Rose (para estados de alerta).
* **Widgets de Apalancamiento Animados**: Cada tarjeta cuenta con efectos blur, bordes Platinum y badges dinámicos con el color del semáforo.
* **Alertas y Mensajería Dinámica**: Utiliza el framework de mensajes de Django integrados en componentes tipo "Toast" arriba a la derecha con micro-desvanecimientos en CSS.
* **Ajuste Inline de Tasas de Cambio**: Desde la pestaña de Tasas, podrá ver un listado histórico y corregir a mano cualquier tasa Binance o BCV si la conexión a internet fallara.
