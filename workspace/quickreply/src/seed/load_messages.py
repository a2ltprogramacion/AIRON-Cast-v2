"""
Script de seeds para QuickReply.
Carga los mensajes del archivo Mensjaes de Respuesta.txt a la base de datos.

Uso:
    cd src
    python -m seed.load_messages

Requiere que Django este configurado (primero ejecuta migrations).
"""
import os
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quickreply.settings")

import django
django.setup()

from reply.models import MessageTemplate


MENSAJES = [
    {
        "titulo": "Agradecimiento post-compra",
        "categoria": "General",
        "contenido": """Antes que nada, gracias por tu compra y confianza en nosotros. 🙏

Si Facebook te da la opcion de calificarnos, te agradeceriamos enormemente que nos regales esos ⭐⭐⭐⭐⭐. Es un gesto pequeno que nos ayuda enormemente a llegar a mas personas y seguir creciendo.

📍 C.C. San Diego / Fin De Siglo - Gran Bazar, Local M9-5, Municipio San Diego.
📞 0412.186.92.11 | 📱 Instagram: @g3multistore

¡Gracias por apoyar lo nuestro! 💙"""
    },
    {
        "titulo": "Articulo agotado",
        "categoria": "General",
        "contenido": """Hola 👋 Este articulo esta agotado por ahora. 📦 Estamos gestionando nuevo despacho.

✅ ¿Te interesa ver opciones similares de la misma categoria?
📍 C.C. San Diego / Fin De Siglo - Gran Bazar, Local M9-5, Municipio San Diego.
📞 0412.186.92.11 | 📱 Instagram: @g3multistore
🛵 Delivery GRATIS 👉 Consulta tu zona

💡 Activa las notificaciones de nuestro perfil para enterarte de nuevos productos. 👋"""
    },
    {
        "titulo": "Ventiladores recargables",
        "categoria": "Ventiladores",
        "contenido": """Hola 👋

✅ Sí, disponibles todos los ventiladores recargables. Ideales para llevar frescura a cualquier lugar sin depender de enchufes.

📍 C.C. San Diego / Fin De Siglo - Gran Bazar, Local M9-5, Municipio San Diego.
📞 0412.186.92.11 | 📱 Instagram: @g3multistore
🛵 Delivery GRATIS 👉 Consulta tu zona

💨 Recargable 8" Multifuncional (F012) ➡️ {F012_usd} (Divisas) | {F012_bcv} (BCV)
✔️ Bateria 10.000mAh. Autonomia hasta 20h. Perfecto para hogar, oficina o viajes.

💨 Recargable con Rociador 6" (F018/F019) ➡️ {F018_usd} (Divisas) | {F018_bcv} (BCV)
✔️ Nebulizador refrescante + bateria 10.000mAh. Ideal para escritorio, auto o dias de calor intenso.

💨 Recargable 8" de Lujo 2 en 1 (F020) ➡️ {F020_usd} (Divisas) | {F020_bcv} (BCV)
✔️ Motor sin escobillas + 5 velocidades + luz LED nocturna. Silencioso y con salida USB para cargar tu celular.

💨 Tripode 10" con Rociador (F023) ➡️ {F023_usd} (Divisas) | {F023_bcv} (BCV)
✔️ Altura regulable hasta 1,37m + control remoto + nebulizador. Maximo alcance para espacios amplios.

✅ Rotacion rapida 👉 ¡Reserva el tuyo!
📲 Escribenos o visitanos hoy. @g3multistore

💱 Precios en Bs sujetos a cambio segun tasa BCV

💡 ¿Buscas mas opciones? Consulta por nuestros ventiladores de mesa y pared para hogar y oficina."""
    },
    {
        "titulo": "Ventiladores industriales",
        "categoria": "Ventiladores",
        "contenido": """Hola 👋

✅ Sí, disponibles todos los ventiladores industriales.

📍 C.C. San Diego / Fin De Siglo - Gran Bazar, Local M9-5, Municipio San Diego.
📞 0412.186.92.11 | 📱 Instagram: @g3multistore
🛵 Delivery GRATIS 👉 Consulta tu zona

💨 26" Industrial Pedestal/Aereo (F007/F007A) ➡️ {F007_usd} (Divisas) | {F007_bcv} (BCV)
✔️ Aspas y rejillas metalicas + armazon aluminio reforzado. Ideal para galpones y talleres.

💨 30" Industrial Pedestal/Aereo (F008/F008A) ➡️ {F008_usd} (Divisas) | {F008_bcv} (BCV)
✔️ Motor 175W + montaje pared/techo. Potencia sin ocupar espacio en piso.

💨 26" Pedestal de Lujo (F010) ➡️ {F010_usd} (Divisas) | {F010_bcv} (BCV)
✔️ Motor 100% cobre embobinado + altura ajustable 157-184cm. Durabilidad premium para uso intensivo.

💨 26" Aereo con Rociador (F022) ➡️ {F022_usd} (Divisas) | {F022_bcv} (BCV)
✔️ Tanque 6L integrado + nebulizador refrescante. Confort termico maximo para ambientes calurosos.

✅ Rotacion rapida 👉 ¡Reserva el tuyo!
📲 Escribenos o visitanos hoy. @g3multistore

💱 Precios en Bs sujetos a cambio segun tasa BCV

💡 ¿Equipamiento completo? Consulta por nuestros compresores de aire y herramientas industriales."""
    },
    {
        "titulo": "Press Control + Bombas",
        "categoria": "Bombas",
        "contenido": """Hola 👋

✅ Sí, disponible nuestro ⚙️ Press Control Inteligente (B005) ➡️ {B005_usd} (Divisas) | {B005_bcv} (BCV)
✔️ Automatiza encendido/apagado + proteccion IP65 + ahorro de energia. Instalacion rapida, ideal para proteger tu bomba contra sobrecarga y funcionamiento en seco.

📍 C.C. San Diego / Fin De Siglo - Gran Bazar, Local M9-5, Municipio San Diego.
📞 0412.186.92.11 | 📱 Instagram: @g3multistore
🛵 Delivery GRATIS 👉 Consulta tu zona

💡 Tambien podria interesarte (armamos tu combo):
💦 Periferica 1/2HP 110V (B001) ➡️ {B001_usd} (Divisas) | {B001_bcv} (BCV)
✔️ Caudal 35L/min + succion 9m. Ideal para tanques domesticos o riego basico.

💦 Periferica 1/2HP 100% Cobre (B001C) ➡️ {B001C_usd} (Divisas) | {B001C_bcv} (BCV)
✔️ Motor de cobre + cuerpo hierro fundido. Mayor durabilidad y eficiencia para uso continuo.

💦 Centrifuga 1HP 110V (B012C) ➡️ {B012C_usd} (Divisas) | {B012C_bcv} (BCV)
✔️ Caudal 100L/min + altura 30m. Motor 100% cobre. Ideal para riego extenso o presion constante.

✅ Rotacion rapida 👉 ¡Reserva el tuyo!
📲 Escribenos o visitanos hoy. @g3multistore

💱 Precios en Bs sujetos a cambio segun tasa BCV"""
    },
    {
        "titulo": "Bombas para piscina",
        "categoria": "Bombas",
        "contenido": """Hola 👋

✅ Sí, disponibles todas las bombas para piscina. Prestamos asesoria personalizada para que selecciones la que realmente necesita segun el tamano de tu piscina y uso.

📍 C.C. San Diego / Fin De Siglo - Gran Bazar, Local M9-5, Municipio San Diego.
📞 0412.186.92.11 | 📱 Instagram: @g3multistore
🛵 Delivery GRATIS 👉 Consulta tu zona

💦 Bomba Piscina 3/4HP HFC-552 (B017P) ➡️ {B017P_usd} (Divisas) | {B017P_bcv} (BCV)
✔️ Motor 100% cobre + eje S.S304 + cuerpo PPO resistente. Ideal para piscinas familiares de uso regular.

💦 Bomba Piscina 1.5HP HFC-1101 (B020P) ➡️ {B020P_usd} (Divisas) | {B020P_bcv} (BCV)
✔️ Caudal 360L/min + altura 16m + conexiones 2". Perfecta para piscinas de uso frecuente y mayor volumen.

💦 Bomba Piscina 2HP HFC-1501 (B021P) ➡️ {B021P_usd} (Divisas) | {B021P_bcv} (BCV)
✔️ Caudal 480L/min + altura 17m + motor reforzado. Alto rendimiento para piscinas grandes o comerciales.

💦 Bomba Piscina 3HP HFC-2201 (B022P) ➡️ {B022P_usd} (Divisas) | {B022P_bcv} (BCV)
✔️ Caudal 500L/min + altura 20m + potencia profesional. Para clubes, hoteles o instalaciones exigentes.

✅ Rotacion rapida 👉 ¡Reserva la tuya!
📲 Escribenos o visitanos hoy. @g3multistore

💱 Precios en Bs sujetos a cambio segun tasa BCV

💡 ¿Arma tu combo completo? Consulta por nuestros filtros de arena y lamparas LED para piscina."""
    },
    {
        "titulo": "Filtros de piscina",
        "categoria": "Piscina",
        "contenido": """Hola 👋

✅ Sí, disponibles todos los filtros de piscina.

📍 C.C. San Diego / Fin De Siglo - Gran Bazar, Local M9-5, Municipio San Diego.
📞 0412.186.92.11 | 📱 Instagram: @g3multistore
🛵 Delivery GRATIS 👉 Consulta tu zona

🌀 Filtro Piscina 16" (B030F) ➡️ {B030F_usd} (Divisas) | {B030F_bcv} (BCV)
✔️ Caudal 8m³/h + valvula 6 funciones. Ideal para piscinas pequenas y mantenimiento basico.

🌀 Filtro Piscina 21" (B031F) ➡️ {B031F_usd} (Divisas) | {B031F_bcv} (BCV)
✔️ Caudal 12m³/h + fibra de vidrio resistente a UV. Perfecto para piscinas residenciales medianas.

🌀 Filtro Piscina 24" (B025F) ➡️ {B025F_usd} (Divisas) | {B025F_bcv} (BCV)
✔️ Caudal 14m³/h + valvula superior incluida. Maxima eficiencia para piscinas de uso frecuente.

✅ Rotacion rapida 👉 ¡Reserva el tuyo!
📲 Escribenos o visitanos hoy. @g3multistore

💱 Precios en Bs sujetos a cambio segun tasa BCV

💡 ¿Arma tu combo completo? Consulta por nuestras bombas para piscina y lamparas LED."""
    },
    {
        "titulo": "Bombas sumergibles",
        "categoria": "Bombas",
        "contenido": """Hola 👋

✅ Sí, disponibles todas las bombas sumergibles. Prestamos asesoria personalizada para que selecciones la que realmente necesita segun la profundidad de tu pozo, caudal requerido y voltaje disponible.

📍 C.C. San Diego / Fin De Siglo - Gran Bazar, Local M9-5, Municipio San Diego.
📞 0412.186.92.11 | 📱 Instagram: @g3multistore
🛵 Delivery GRATIS 👉 Consulta tu zona

💦 Sumergible 1/2HP 110V/220V (B006S/B007S) ➡️ {B006S_usd} (Divisas) | {B006S_bcv} (BCV)
✔️ Caudal hasta 55L/min + profundidad hasta 56m + bobina de cobre. Ideal para pozos domesticos poco profundos y tanques elevados.

💦 Sumergible 3/4HP 220V (B008S) ➡️ {B008S_usd} (Divisas) | {B008S_bcv} (BCV)
✔️ Bobinas de cobre + profundidad hasta 81m + caudal 55L/min. Ideal para pozos de mayor altura y sistemas de presion continua.

💦 Sumergible 1HP 220V (B009S) ➡️ {B009S_usd} (Divisas) | {B009S_bcv} (BCV)
✔️ Caudal hasta 55L/min + profundidad hasta 106m + bobina de cobre. La mas versatil para casas de varios pisos y riego por goteo.

💦 Sumergible 2HP 220V (B011S) ➡️ {B011S_usd} (Divisas) | {B011S_bcv} (BCV)
✔️ Caudal hasta 80L/min + profundidad hasta 174m + bobina de cobre. Maximo caudal para fincas, granjas o sistemas de alta demanda.

💦 Sumergible 5.5HP Trifasica (B012S) ➡️ {B012S_usd} (Divisas) | {B012S_bcv} (BCV)
✔️ Caudal hasta 270L/min + profundidad hasta 80m + motor trifasico. Potencia industrial para proyectos agricolas o comerciales de gran escala.

✅ Rotacion rapida 👉 ¡Reserva la tuya!
📲 Escribenos o visitanos hoy. @g3multistore

💱 Precios en Bs sujetos a cambio segun tasa BCV

💡 ¿Arma tu sistema de bombeo completo? Consulta por nuestros press controls inteligentes, bombas centrifugas y accesorios para pozos."""
    },
    {
        "titulo": "Bombas sumergibles Tipo Lapiz",
        "categoria": "Bombas",
        "contenido": """Hola 👋

✅ Sí, disponibles todas las bombas sumergibles tipo lapiz. Prestamos asesoria personalizada para que selecciones la que realmente necesita segun la profundidad de tu pozo, caudal requerido y voltaje disponible.

📍 C.C. San Diego / Fin De Siglo - Gran Bazar, Local M9-5, Municipio San Diego.
📞 0412.186.92.11 | 📱 Instagram: @g3multistore
🛵 Delivery GRATIS 👉 Consulta tu zona

💦 Sumergible Tipo Lapiz 1/2HP 110V (B014L) ➡️ {B014L_usd} (Divisas) | {B014L_bcv} (BCV)
✔️ Diseno delgado 2" + bobinas de cobre + profundidad hasta 36m. Perfecta para pozos tubulares de diametro reducido.

💦 Sumergible Tipo Lapiz 1/2HP 220V (B015L) ➡️ {B015L_usd} (Divisas) | {B015L_bcv} (BCV)
✔️ Mismas especificaciones que la 110V pero para redes de 220V. Ideal para instalaciones con mayor voltaje disponible.

💦 Sumergible Tipo Lapiz 3/4HP 220V (B016L) ➡️ {B016L_usd} (Divisas) | {B016L_bcv} (BCV)
✔️ Diseno delgado 2" + profundidad hasta 41m + bobinas de cobre. Potencia intermedia para pozos estrechos que requieren mayor caudal.

✅ Rotacion rapida 👉 ¡Reserva la tuya!
📲 Escribenos o visitanos hoy. @g3multistore

💱 Precios en Bs sujetos a cambio segun tasa BCV"""
    },
    {
        "titulo": "Motores fuera de borda",
        "categoria": "Marina",
        "contenido": """Hola 👋

✅ Sí, disponibles todos los motores fuera de borda.

📍 C.C. San Diego / Fin De Siglo - Gran Bazar, Local M9-5, Municipio San Diego.
📞 0412.186.92.11 | 📱 Instagram: @g3multistore
🛵 Delivery GRATIS 👉 Consulta tu zona

🚤 Fuera de Borda 15HP SEAPRO Eje Corto (E003) ➡️ {E003_usd} (Divisas) | {E003_bcv} (BCV)
✔️ 246cc + 2 tiempos + encendido CDI. Ligero (41kg) y confiable para lanchas pequenas, pesca o recreacion.

🚤 Fuera de Borda 15HP SEAPRO Eje Largo (E004) ➡️ {E004_usd} (Divisas) | {E004_bcv} (BCV)
✔️ Misma potencia con eje extendido. Ideal para embarcaciones con mayor distancia al agua o cascos altos.

🚤 Fuera de Borda 40HP SEAPRO Eje Corto (E005) ➡️ {E005_usd} (Divisas) | {E005_bcv} (BCV)
✔️ 703cc + helice aluminio + tanque 24L. Potencia versatil para trabajo, transporte o embarcaciones medianas.

🚤 Fuera de Borda 40HP SEAPRO Eje Largo (E006) ➡️ {E006_usd} (Divisas) | {E006_bcv} (BCV)
✔️ Maxima potencia con configuracion extendida. Perfecto para lanchas de mayor calado o uso profesional.

🚤 Fuera de Borda 40HP ENDURANCE Eje Corto (E001) ➡️ {E001_usd} (Divisas) | {E001_bcv} (BCV)
✔️ 669cc + sistema reforzado + bajo consumo. Alta gama para uso profesional, continuo o condiciones exigentes.

🚤 Fuera de Borda 40HP ENDURANCE Eje Largo (E002) ➡️ {E002_usd} (Divisas) | {E002_bcv} (BCV)
✔️ Version extendida de la linea Endurance. Maxima durabilidad para navegacion intensiva y aguas profundas.

✅ Rotacion rapida 👉 ¡Reserva el tuyo!
📲 Escribenos o visitanos hoy. @g3multistore

💱 Precios en Bs sujetos a cambio segun tasa BCV"""
    },
    {
        "titulo": "Compresores de aire",
        "categoria": "Herramientas",
        "contenido": """Hola 👋

✅ Sí, disponibles todos los compresores de aire.

📍 C.C. San Diego / Fin De Siglo - Gran Bazar, Local M9-5, Municipio San Diego.
📞 0412.186.92.11 | 📱 Instagram: @g3multistore
🛵 Delivery GRATIS 👉 Consulta tu zona

🔧 Compresor 24L 2HP 100% Cobre FL-24 (H082) ➡️ {H082_usd} (Divisas) | {H082_bcv} (BCV)
✔️ Motor 100% cobre + doble valvula de salida + 115 PSI. Ideal para talleres pequenos y uso domestico.

🔧 Compresor 50L 3HP 100% Cobre FL-50 (H083) ➡️ {H083_usd} (Divisas) | {H083_bcv} (BCV)
✔️ Mayor capacidad + motor reforzado + manometros internos. Perfecto para uso continuo en talleres.

🔧 Compresor Libre de Aceite 30L Ultra Silent (H114) ➡️ {H114_usd} (Divisas) | {H114_bcv} (BCV)
✔️ Tecnologia libre de aceite + reduccion de ruido + 8 Bar. Ideal para trabajos que requieren aire limpio y bajo nivel sonoro.

🔧 Compresor Libre de Aceite 50L 3.2HP DAC-50 (H087) ➡️ {H087_usd} (Divisas) | {H087_bcv} (BCV)
✔️ 4 mufflers anti-ruido + libre de aceite + alta presion. Maximo rendimiento profesional sin contaminacion de aceite.

🔧 Compresor Libre de Aceite 60L Ultra Silent (H115) ➡️ {H115_usd} (Divisas) | {H115_bcv} (BCV)
✔️ 290L/min de flujo + 2HP + operacion silenciosa. Potencia maxima para industrias que exigen aire limpio y bajo ruido.

✅ Rotacion rapida 👉 ¡Reserva el tuyo!
📲 Escribenos o visitanos hoy. @g3multistore

💱 Precios en Bs sujetos a cambio segun tasa BCV

💡 ¿Equipamiento completo? Consulta por nuestras herramientas para taller."""
    },
    {
        "titulo": "Rebanadoras",
        "categoria": "Alimentos",
        "contenido": """Hola 👋

✅ Sí, disponibles las rebanadoras industriales.

📍 C.C. San Diego / Fin De Siglo - Gran Bazar, Local M9-5, Municipio San Diego.
📞 0412.186.92.11 | 📱 Instagram: @g3multistore
🛵 Delivery GRATIS 👉 Consulta tu zona

🔪 Rebanadora 250 mm (I001) ➡️ {I001_usd} (Divisas) | {I001_bcv} (BCV)
✔️ Disco acero inoxidable + motor 320W + corte milimetrico. Ideal para delicatessen, embutidos y cortes precisos en negocios medianos.

🔪 Rebanadora 300 mm (I002) ➡️ {I002_usd} (Divisas) | {I002_bcv} (BCV)
✔️ Disco acero inoxidable + motor 420W + mayor capacidad de corte. Perfecta para alto volumen en carnicerias, restaurantes o industrias alimentarias.

✅ Rotacion rapida 👉 ¡Reserva la tuya!
📲 Escribenos o visitanos hoy. @g3multistore

💱 Precios en Bs sujetos a cambio segun tasa BCV

💡 ¿Equipamiento completo? Consulta por nuestros molinos de carne y embutidoras para procesadora."""
    },
    {
        "titulo": "Powerbanks",
        "categoria": "Electronica",
        "contenido": """Hola 👋

✅ Sí, disponibles los Powerbanks 30000mAh. Ideales para mantener tus dispositivos cargados todo el dia sin depender de enchufes.

📍 C.C. San Diego / Fin De Siglo - Gran Bazar, Local M9-5, Municipio San Diego.
📞 0412.186.92.11 | 📱 Instagram: @g3multistore
🛵 Delivery GRATIS 👉 Consulta tu zona

🔋 Powerbank 30000mAh Carga Rapida Blanco/Negro (M025/M025N) ➡️ {M025_usd} (Divisas) | {M025_bcv} (BCV)
✔️ Capacidad real 30000mAh + carga rapida bidireccional + 3 puertos USB. Ideal para viajes, trabajo o emergencias. Compatible con celulares, tablets y dispositivos USB.

✅ Rotacion rapida 👉 ¡Reserva el tuyo!
📲 Escribenos o visitanos hoy. @g3multistore

💱 Precios en Bs sujetos a cambio segun tasa BCV

💡 ¿Buscas mas opciones? Consulta por nuestros ventiladores recargables y lamparas solares portatiles."""
    },
    {
        "titulo": "Licuadoras",
        "categoria": "Electrodomesticos",
        "contenido": """Hola 👋

✅ Sí, disponibles todas las licuadoras comerciales.

📍 C.C. San Diego / Fin De Siglo - Gran Bazar, Local M9-5, Municipio San Diego.
📞 0412.186.92.11 | 📱 Instagram: @g3multistore
🛵 Delivery GRATIS 👉 Consulta tu zona

🥤 Licuadora Comercial 2L Alta Potencia (I042) ➡️ {I042_usd} (Divisas) | {I042_bcv} (BCV)
✔️ 1500W + 25.000 RPM + vaso policarbonato resistente. Ideal para jugos, smoothies y uso continuo en cafeterias.

🥤 Licuadora Comercial 6L Alta Potencia (I043) ➡️ {I043_usd} (Divisas) | {I043_bcv} (BCV)
✔️ 3000W + motor 100% cobre + capacidad industrial. Perfecta para restaurantes, comedores o produccion masiva.

🥤 Licuadora Inteligente 2 en 1 Roja/Negra (I048/I048N) ➡️ {I048_usd} (Divisas) | {I048_bcv} (BCV)
✔️ 1200W + 10 funciones (sopas, cremas, granizados) + panel tactil. Versatilidad profesional para emprendimientos gastronomicos.

🥤 Licuadora Silenciosa 2L Comercial RS-305 (I053) ➡️ {I053_usd} (Divisas) | {I053_bcv} (BCV)
✔️ 800W + motor cobre + operacion silenciosa + 9 velocidades. Ideal para oficinas, consultorios o espacios que requieren bajo ruido.

🥤 Licuadora Multifuncional 1.8L RS-06 (I054) ➡️ {I054_usd} (Divisas) | {I054_bcv} (BCV)
✔️ 600W + 3 velocidades + funcion multiusos (moler, mezclar, licuar, triturar). Compacta y duradera para uso domestico o pequenos negocios.

✅ Rotacion rapida 👉 ¡Reserva la tuya!
📲 Escribenos o visitanos hoy. @g3multistore

💱 Precios en Bs sujetos a cambio segun tasa BCV

💡 ¿Buscas mas opciones? Consulta por nuestras licuadoras inteligentes y accesorios para procesamiento de alimentos."""
    },
    {
        "titulo": "Hidrojets",
        "categoria": "Limpieza",
        "contenido": """Hola 👋

✅ Sí, disponibles todos los hidrojets. Te asesoramos para que selecciones el que realmente necesita segun tu tipo de limpieza: hogar, negocio o uso industrial.

📍 C.C. San Diego / Fin De Siglo - Gran Bazar, Local M9-5, Municipio San Diego.
📞 0412.186.92.11 | 📱 Instagram: @g3multistore
🛵 Delivery GRATIS 👉 Consulta tu zona

💦 Hidrojet Induccion 2100W SY11X (B020H) ➡️ {B020H_usd} (Divisas) | {B020H_bcv} (BCV)
✔️ 2350 PSI + 6L/min + manguera 8m. Ideal para limpieza profunda de vehiculos, paredes y patios.

💦 Hidrojet Induccion 2200W SP11Z (B023H) ➡️ {B023H_usd} (Divisas) | {B023H_bcv} (BCV)
✔️ 2400 PSI + 7.5L/min + tanque para jabon. Potencia versatil para mantenimiento residencial y comercial.

💦 Hidrojet Gasolina 2800PSI RH-2900A (B026H) ➡️ {B026H_usd} (Divisas) | {B026H_bcv} (BCV)
✔️ Motor 6.5HP + 11.3L/min + boquillas multiples. Maxima potencia para uso industrial y areas extensas sin dependencia electrica.

🔋 Hidrojet Inalambrico Portatil Crescent (B034H) ➡️ {B034H_usd} (Divisas) | {B034H_bcv} (BCV)
✔️ Bateria 2000mAh + 435 PSI + boquillas 6 en 1. Perfecto para limpiezas rapidas en auto, bicicleta o exteriores.

✅ Rotacion rapida 👉 ¡Reserva el tuyo!
📲 Escribenos o visitanos hoy. @g3multistore

💱 Precios en Bs sujetos a cambio segun tasa BCV

💡 ¿Necesitas otra potencia? Tenemos hidrojets desde 1400W hasta 3000PSI, con y sin cable. ¡Pregunta por el modelo ideal para tu proyecto! 🎯"""
    },
    {
        "titulo": "Maquinas de soldar",
        "categoria": "Herramientas",
        "contenido": """Hola 👋

✅ Sí, disponibles todas las maquinas de soldar inverter.

📍 C.C. San Diego / Fin De Siglo - Gran Bazar, Local M9-5, Municipio San Diego.
📞 0412.186.92.11 | 📱 Instagram: @g3multistore
🛵 Delivery GRATIS 👉 Consulta tu zona

🔧 Soldadora Inverter MIG/MMA 120AH (H146) ➡️ {H146_usd} (Divisas) | {H146_bcv} (BCV)
✔️ Doble funcion MIG/MMA + 120Ah + doble voltaje 110V/220V. Ideal para talleres pequenos y proyectos de herrajeria con maxima versatilidad.

🔧 Soldadora Inverter MMA 160Ah (H134) ➡️ {H134_usd} (Divisas) | {H134_bcv} (BCV)
✔️ 160Ah + doble voltaje + arco estable. Perfecta para soldadura de electrodo en acero y hierro.

🔧 Soldadora Inverter MMA 200Ah (H135) ➡️ {H135_usd} (Divisas) | {H135_bcv} (BCV)
✔️ 200Ah + mayor potencia + proteccion termica. Para trabajos continuos en estructuras y herrajeria pesada.

🔧 Soldadora Profesional Inverter MMA 250Ah (H136) ➡️ {H136_usd} (Divisas) | {H136_bcv} (BCV)
✔️ 250Ah + uso industrial + ciclo de trabajo 50%. Maxima potencia para soldadura profesional exigente.

🔧 Soldadora Inverter MIG/MMA 120/160Ah (H145) ➡️ {H145_usd} (Divisas) | {H145_bcv} (BCV)
✔️ Doble funcion + 160Ah + alambre incluido. Versatilidad MIG y electrodo para multiples aplicaciones.

🔧 Soldadora MMA-120DV 120Ah (H153) ➡️ {H153_usd} (Divisas) | {H153_bcv} (BCV)
✔️ Compacta + doble voltaje + facil transporte. Ideal para reparaciones rapidas y trabajos livianos.

🔧 Soldadora TIG-200P AC/DC 120/200Ah (H154) ➡️ {H154_usd} (Divisas) | {H154_bcv} (BCV)
✔️ TIG AC/DC + 200Ah + soldadura de aluminio. Alta precision para trabajos en acero inoxidable y aluminio.

🔧 Soldadora MMA/MIG/CUT/TIG MMCT-200 (H155) ➡️ {H155_usd} (Divisas) | {H155_bcv} (BCV)
✔️ 4 en 1 + corte por plasma + 200Ah. Estacion completa de soldadura y corte para talleres profesionales.

✅ Rotacion rapida 👉 ¡Reserva la tuya!
📲 Escribenos o visitanos hoy. @g3multistore

💱 Precios en Bs sujetos a cambio segun tasa BCV

💡 ¿Necesitas accesorios? Consulta por nuestros electrodos, alambres para soldar y caretas de proteccion."""
    },
    {
        "titulo": "Gatos tipo botella",
        "categoria": "Automotriz",
        "contenido": """Hola 👋

✅ Sí, disponibles los gatos tipo botella.

📍 C.C. San Diego / Fin De Siglo - Gran Bazar, Local M9-5, Municipio San Diego.
📞 0412.186.92.11 | 📱 Instagram: @g3multistore
🛵 Delivery GRATIS 👉 Consulta tu zona

🔧 Gato Botella 20 Ton Good Quality (H094) ➡️ {H094_usd} (Divisas) | {H094_bcv} (BCV)
✔️ Acero reforzado + valvula de seguridad + base antideslizante. Ideal para camionetas, trailers y levantamiento pesado en talleres.

🔧 Gato Botella 30 Ton Good Quality (H095) ➡️ {H095_usd} (Divisas) | {H095_bcv} (BCV)
✔️ Mayor capacidad + bomba de alta presion + construccion industrial. Perfecto para maquinaria pesada, buses o transporte de carga.

🔧 Gato Botella Neumatico 30 Ton ST3007Q (H108) ➡️ {H108_usd} (Divisas) | {H108_bcv} (BCV)
✔️ Accionamiento por aire + doble sistema (neumatico/manual) + altura ajustable. Maxima rapidez y seguridad para flotas y talleres profesionales.

✅ Rotacion rapida 👉 ¡Reserva el tuyo!
📲 Escribenos o visitanos hoy. @g3multistore

💱 Precios en Bs sujetos a cambio segun tasa BCV

💡 ¿Buscas mas opciones? Consulta por nuestros gatos tipoaiman de bajo perfil, ideales para vehiculos deportivos y trabajos en espacios reducidos."""
    },
    {
        "titulo": "Cortadoras de grama",
        "categoria": "Jardin",
        "contenido": """Hola 👋

✅ Sí, disponibles las cortadoras de grama 4 ruedas.

📍 C.C. San Diego / Fin De Siglo - Gran Bazar, Local M9-5, Municipio San Diego.
📞 0412.186.92.11 | 📱 Instagram: @g3multistore
🛵 Delivery GRATIS 👉 Consulta tu zona

🌿 Cortadora de Grama 4 Ruedas 16" 4HP (J006) ➡️ {J006_usd} (Divisas) | {J006_bcv} (BCV)
✔️ Ancho de corte 400mm + motor 4HP + altura ajustable 25-75mm. Ideal para jardines residenciales y terrenos planos.

🌿 Cortadora de Grama 4 Ruedas 22" 6.5HP (J007) ➡️ {J007_usd} (Divisas) | {J007_bcv} (BCV)
✔️ Ancho de corte 560mm + motor 6.5HP + traccion a ruedas + recogedor 70L. Perfecta para areas extensas y uso profesional.

✅ Rotacion rapida 👉 ¡Reserva la tuya!
📲 Escribenos o visitanos hoy. @g3multistore

💱 Precios en Bs sujetos a cambio segun tasa BCV

💡 ¿Buscas mas opciones? Consulta por nuestras desmalezadoras, motosierras y nylon de corte para jardin."""
    },
    {
        "titulo": "Desmalezadora",
        "categoria": "Jardin",
        "contenido": """Hola 👋

✅ Sí, disponible la Desmalezadora 51.7CC.

📍 C.C. San Diego / Fin De Siglo - Gran Bazar, Local M9-5, Municipio San Diego.
📞 0412.186.92.11 | 📱 Instagram: @g3multistore
🛵 Delivery GRATIS 👉 Consulta tu zona

🌿 Desmalezadora 51.7CC (J001) ➡️ {J001_usd} (Divisas) | {J001_bcv} (BCV)
✔️ Motor 1.6kW + tanque 1L + compatible con hoja de corte y nylon. Ideal para maleza densa, bordes de cercas y areas de dificil acceso.

✅ Rotacion rapida 👉 ¡Reserva la tuya!
📲 Escribenos o visitanos hoy. @g3multistore

💱 Precios en Bs sujetos a cambio segun tasa BCV

💡 ¿Buscas mas opciones? Consulta por nuestras cortadoras de grama y equipos de riego para tu jardin."""
    },
    {
        "titulo": "Bombas centrifugas",
        "categoria": "Bombas",
        "contenido": """Hola 👋

✅ Sí, disponibles todas las bombas centrifugas. Te asesoramos para que selections la que realmente necesita segun tu proyecto: hogar, agricultura o industria.

📍 C.C. San Diego / Fin De Siglo - Gran Bazar, Local M9-5, Municipio San Diego.
📞 0412.186.92.11 | 📱 Instagram: @g3multistore
🛵 Delivery GRATIS 👉 Consulta tu zona

💦 Centrifuga 1HP 110V HCM158 (B012C) ➡️ {B012C_usd} (Divisas) | {B012C_bcv} (BCV)
✔️ Motor 100% cobre + caudal 100L/min + altura 30m. Ideal para sistemas de presion domesticos y riego basico.

💦 Centrifuga 2HP 220V HCM190 (B014C) ➡️ {B014C_usd} (Divisas) | {B014C_bcv} (BCV)
✔️ Motor 100% cobre + caudal hasta 140L/min + altura 41m. Perfecta para tanques elevados y presion constante en casas de 2-3 pisos.

💦 Centrifuga Acero Inoxidable 1HP HCT-26S (B019AI) ➡️ {B019AI_usd} (Divisas) | {B019AI_bcv} (BCV)
✔️ Impulsor y cuerpo en acero inoxidable + motor 100% cobre. Resistente a corrosion, ideal para agua salobre o quimicos ligeros.

💦 Centrifuga Trifasica 5.5HP HST40-160/40 (B016C) ➡️ {B016C_usd} (Divisas) | {B016C_bcv} (BCV)
✔️ Motor 100% cobre + caudal 583L/min + impulsor hierro fundido. Potencia industrial para riego extensivo o procesos productivos.

💦 Centrifuga Doble Impulsor 7.5HP HST32-250/55D (B020C) ➡️ {B020C_usd} (Divisas) | {B020C_bcv} (BCV)
✔️ Doble impulsor + motor 100% cobre + altura hasta 88m. Maxima presion para pozos profundos o sistemas de alta demanda.

✅ Rotacion rapida 👉 ¡Reserva la tuya!
📲 Escribenos o visitanos hoy. @g3multistore

💱 Precios en Bs sujetos a cambio segun tasa BCV"""
    },
    {
        "titulo": "Mini UPS + Powerbank",
        "categoria": "Electronica",
        "contenido": """Hola 👋

✅ Sí, disponible el Mini UPS 13.500mAh. Ideal para que tu internet, modem o camaras de seguridad no se apaguen cuando se va la luz.

📍 C.C. San Diego / Fin De Siglo - Gran Bazar, Local M9-5, Municipio San Diego.
📞 0412.186.92.11 | 📱 Instagram: @g3multistore
🛵 Delivery GRATIS 👉 Consulta tu zona

🔋 Mini UPS 13.500mAh Litio (M013) ➡️ {M013_usd} (Divisas) | {M013_bcv} (BCV)
✔️ Bateria de litio de alta duracion + salidas 5V/9V/12V. Mantiene tu router y equipos esenciales encendidos durante los cortes de luz. Carga completa en solo 2.5 horas.

💡 Tambien podria interesarte (armamos tu combo de respaldo electrico):
🔋 Powerbank 30000mAh Carga Rapida Blanco/Negro ➡️ {M025_usd} (Divisas) | {M025_bcv} (BCV)
✔️ Capacidad real 30000mAh + carga rapida 30W + 3 puertos USB. Perfecto para mantener tu celular y tablets cargados todo el dia sin depender de enchufes.

✅ Rotacion rapida 👉 ¡Reserva el tuyo!
📲 Escribenos o visitanos hoy. @g3multistore

💱 Precios en Bs sujetos a cambio segun tasa BCV"""
    },
    {
        "titulo": "Lamparas solares",
        "categoria": "Iluminacion",
        "contenido": """Hola 👋

✅ Sí, disponibles todas las lamparas solares.

📍 C.C. San Diego / Fin De Siglo - Gran Bazar, Local M9-5, Municipio San Diego.
📞 0412.186.92.11 | 📱 Instagram: @g3multistore
🛵 Delivery GRATIS 👉 Consulta tu zona

💡 Lámpara Solar 1400LM 80W/10Ah (LS001) ➡️ {LS001_usd} (Divisas) | {LS001_bcv} (BCV)
✔️ Bateria LifePo4 + panel 10W + autonomia 16h. Ideal para patios pequenos, entradas y caminos. Carga en 4-6h.

💡 Lámpara Solar 1100LM 80W/10Ah (LS005) ➡️ {LS005_usd} (Divisas) | {LS005_bcv} (BCV)
✔️ Deteccion de movimiento 12m + angulo 120° + panel 8W. Perfecta para seguridad en entradas y jardines.

💡 Lámpara Solar 1680LM 120W/12Ah (LS006) ➡️ {LS006_usd} (Divisas) | {LS006_bcv} (BCV)
✔️ Deteccion de movimiento 12m + angulo 120° + autonomia 12-14h. Ideal para estacionamientos o areas medianas.

💡 Lámpara Solar 2100LM 160W/15Ah (LS002) ➡️ {LS002_usd} (Divisas) | {LS002_bcv} (BCV)
✔️ Bateria LifePo4 15Ah + encendido automatico al anochecer + carga rapida. Perfecta para espacios amplos.

💡 Lámpara Solar 2100LM 150W/15Ah (LS007) ➡️ {LS007_usd} (Divisas) | {LS007_bcv} (BCV)
✔️ Mayor cobertura lumínica + autonomia 12-14h + deteccion de movimiento. Ideal para areas de transito.

💡 Lámpara Solar 2800LM 240W/20Ah (LS003) ➡️ {LS003_usd} (Divisas) | {LS003_bcv} (BCV)
✔️ Panel 20W + bateria 20Ah + potencia extra. Carga eficiente incluso en dias nublados.

💡 Lámpara Solar 4200LM 320W/30Ah (LS004) ➡️ {LS004_usd} (Divisas) | {LS004_bcv} (BCV)
✔️ Maxima autonomia + bateria 30Ah + carga eficiente sin red electrica. Perfecta para zonas remotas o alto consumo.

💡 Lámpara Solar de Poste 6000LM 450W/45Ah (LS008) ➡️ {LS008_usd} (Divisas) | {LS008_bcv} (BCV)
✔️ Potencia industrial + bateria 45Ah + mas de 1200 ciclos de carga. Para calles, canchas o negocios.

✅ Rotacion rapida 👉 ¡Reserva la tuya!
📲 Escribenos o visitanos hoy. @g3multistore

💱 Precios en Bs sujetos a cambio segun tasa BCV

💡 ¿Buscas mas opciones? Consulta por nuestros bombillos recargables, powerbanks y soportes para lamparas solares."""
    },
    {
        "titulo": "Romanas",
        "categoria": "Pesaje",
        "contenido": """Hola 👋

✅ Sí, disponibles todas las romanas industriales.

📍 C.C. San Diego / Fin De Siglo - Gran Bazar, Local M9-5, Municipio San Diego.
📞 0412.186.92.11 | 📱 Instagram: @g3multistore
🛵 Delivery GRATIS 👉 Consulta tu zona

⚖️ Romana 200 KG (P011) ➡️ {P011_usd} (Divisas) | {P011_bcv} (BCV)
✔️ Precision 20g + plataforma 30x40cm + calculo de precios. Ideal para bodegas, abastos y negocios pequenos.

⚖️ Romana 350 KG (P012) ➡️ {P012_usd} (Divisas) | {P012_bcv} (BCV)
✔️ Precision 50g + plataforma 40x50cm + bateria 20h. La mas vendida para carnicerias, fruterias y mercados.

⚖️ Romana 200KG Alta Precision 616D (P023) ➡️ {P023_usd} (Divisas) | {P023_bcv} (BCV)
✔️ Precision 50g + acero inoxidable + paral 55cm. Para negocios que exigen exactitud y durabilidad.

⚖️ Romana 300KG Alta Precision 617D (P024) ➡️ {P024_usd} (Divisas) | {P024_bcv} (BCV)
✔️ Precision 50g + plataforma 52x42cm + calculo automatico de precios. Gama alta para comercios de alto volumen.

⚖️ Romana Acero Inoxidable 400KG RS-811 (P028) ➡️ {P028_usd} (Divisas) | {P028_bcv} (BCV)
✔️ 100% acero inoxidable + precision 50g + plataforma 60x50cm. Maxima higiene y resistencia para pescaderias o industrias alimentarias.

✅ Rotacion rapida 👉 ¡Reserva la tuya!
📲 Escribenos o visitanos hoy. @g3multistore

💱 Precios en Bs sujetos a cambio segun tasa BCV

💡 ¿Arma tu sistema completo de pesaje? Consulta por nuestras balanzas de mostrador, balanzas de gancho y balanzas de cocina para tu negocio."""
    },
    {
        "titulo": "Fumigadoras",
        "categoria": "Jardin",
        "contenido": """Hola 👋

✅ Sí, disponibles las fumigadoras de canon. Ideales para tratamientos fitosanitarios, desinfeccion o control de plagas en areas extensas.

📍 C.C. San Diego / Fin De Siglo - Gran Bazar, Local M9-5, Municipio San Diego.
📞 0412.186.92.11 | 📱 Instagram: @g3multistore
🛵 Delivery GRATIS 👉 Consulta tu zona

🌿 Fumigadora de Canon 20L (J003) ➡️ {J003_usd} (Divisas) | {J003_bcv} (BCV)
✔️ Motor 2.13kW + tanque 20L + alcance 11m. Perfecta para huertos, invernaderos y aplicaciones agricolas de mediana escala.

🌿 Fumigadora de Canon 14L (J004) ➡️ {J004_usd} (Divisas) | {J004_bcv} (BCV)
✔️ Motor 2.6kW + tanque 14L + alcance 14m. Mayor potencia y distancia para tratamientos intensivos en areas extensas.

✅ Rotacion rapida 👉 ¡Reserva la tuya!
📲 Escribenos o visitanos hoy. @g3multistore

💱 Precios en Bs sujetos a cambio segun tasa BCV

💡 ¿Buscas mas opciones? Consulta por nuestras desmalezadoras, cortadoras de grama y nylon de corte para jardin."""
    },
    {
        "titulo": "Contadoras y detectoras de billetes",
        "categoria": "Dinero",
        "contenido": """Hola 👋

✅ Sí, disponibles todas las contadoras y detectoras de billetes. Equipos profesionales para que tu negocio maneje efectivo con total seguridad y rapidez.

📍 C.C. San Diego / Fin De Siglo - Gran Bazar, Local M9-5, Municipio San Diego.
📞 0412.186.92.11 | 📱 Instagram: @g3multistore
🛵 Delivery GRATIS 👉 Consulta tu zona

💵 Detectora de Billetes Falsos AL-130A Pantalla Azul (M001) ➡️ {M001_usd} (Divisas) | {M001_bcv} (BCV)
✔️ Deteccion UV e IR + pantalla TFT a color + bateria recargable. Portatil y confiable para verificar autenticidad en cualquier punto de venta.

💵 Contadora Inteligente Smart Pantalla Tactil (M010) ➡️ {M010_usd} (Divisas) | {M010_bcv} (BCV)
✔️ Pantalla tactil 4.5" + deteccion magnetica/UV/IR + velocidad 1200 billetes/min + bolsillo extra. Identifica automaticamente USD, EUR y mas monedas.

💵 Contadora Inteligente Pantalla Tactil (M011) ➡️ {M011_usd} (Divisas) | {M011_bcv} (BCV)
✔️ Pantalla tactil + deteccion magnetica/UV/IR + velocidad 1200 billetes/min. Ideal para comercios de alto volumen que exigen precision y rapidez.

💵 Contadora y Detectora con Visor R-06 (M012) ➡️ {M012_usd} (Divisas) | {M012_bcv} (BCV)
✔️ Visor externo + deteccion UV e IR + funcion de lote y adicion + capacidad 200 billetes. Excelente relacion calidad-precio para negocios en crecimiento.

✅ Rotacion rapida 👉 ¡Reserva la tuya!
📲 Escribenos o visitanos hoy. @g3multistore

💱 Precios en Bs sujetos a cambio segun tasa BCV

💡 ¿Arma tu sistema completo de cobro? Consulta por nuestras impresoras termicas, lectores de codigo de barras y balanzas de mostrador."""
    },
    {
        "titulo": "Lamparas solares y soportes",
        "categoria": "Iluminacion",
        "contenido": """Hola 👋

✅ Sí, disponibles todas las lamparas solares y soportes. Ilumina tus espacios sin gastar un centavo en electricidad.

📍 C.C. San Diego / Fin De Siglo - Gran Bazar, Local M9-5, Municipio San Diego.
📞 0412.186.92.11 | 📱 Instagram: @g3multistore
🛵 Delivery GRATIS 👉 Consulta tu zona

💡 Lámpara Solar 1100LM 80W/10Ah (LS005) ➡️ {LS005_usd} (Divisas) | {LS005_bcv} (BCV)
✔️ Deteccion de movimiento 12m + angulo 120° + panel 8W. Perfecta para seguridad en entradas y jardines.

💡 Lámpara Solar 1400LM 80W/10Ah (LS001) ➡️ {LS001_usd} (Divisas) | {LS001_bcv} (BCV)
✔️ Bateria LifePo4 + panel 10W + autonomia 16h. Ideal para patios pequenos, entradas y caminos. Carga en 4-6h.

💡 Lámpara Solar 1680LM 120W/12Ah (LS006) ➡️ {LS006_usd} (Divisas) | {LS006_bcv} (BCV)
✔️ Deteccion de movimiento 12m + angulo 120° + autonomia 12-14h. Ideal para estacionamientos o areas medianas.

💡 Lámpara Portatil 2100LM 150W/15Ah (LS009) ➡️ {LS009_usd} (Divisas) | {LS009_bcv} (BCV)
✔️ Instalacion en pared o poste + 3 modos de brillo + autonomia hasta 16h. Versatil y resistente para cualquier espacio.

💡 Lámpara Solar 2100LM 160W/15Ah (LS002) ➡️ {LS002_usd} (Divisas) | {LS002_bcv} (BCV)
✔️ Bateria LifePo4 15Ah + encendido automatico al anochecer + carga rapida. Perfecta para espacios amplos.

💡 Lámpara Solar 2100LM 150W/15Ah (LS007) ➡️ {LS007_usd} (Divisas) | {LS007_bcv} (BCV)
✔️ Mayor cobertura lumínica + autonomia 12-14h + deteccion de movimiento. Ideal para areas de transito.

💡 Lámpara Solar 2800LM 240W/20Ah (LS003) ➡️ {LS003_usd} (Divisas) | {LS003_bcv} (BCV)
✔️ Panel 20W + bateria 20Ah + potencia extra. Carga eficiente incluso en dias nublados.

💡 Lámpara Solar 4200LM 320W/30Ah (LS004) ➡️ {LS004_usd} (Divisas) | {LS004_bcv} (BCV)
✔️ Maxima autonomia + bateria 30Ah + carga eficiente sin red electrica. Perfecta para zonas remotas o alto consumo.

💡 Lámpara Solar de Poste 6000LM 450W/45Ah (LS008) ➡️ {LS008_usd} (Divisas) | {LS008_bcv} (BCV)
✔️ Potencia industrial + bateria 45Ah + mas de 1200 ciclos de carga. Para calles, canchas o negocios.

🔧 Soporte para Lámpara Solar 450mm (LS010) ➡️ {LS010_usd} (Divisas) | {LS010_bcv} (BCV)
✔️ Brazo metalico resistente + instalacion facil. Complemento ideal para fijar tus lamparas en postes o paredes.

✅ Rotacion rapida 👉 ¡Reserva la tuya!
📲 Escribenos o visitanos hoy. @g3multistore

💱 Precios en Bs sujetos a cambio segun tasa BCV

💡 ¿Buscas mas opciones? Consulta por nuestros bombillos recargables, powerbanks y paneles solares para tu sistema de energia."""
    },
]


def load_messages():
    """Carga todos los mensajes definidos en MENSAJES a la base de datos."""
    creados = 0
    actualizados = 0
    saltados = 0

    for datos in MENSAJES:
        obj, created = MessageTemplate.objects.update_or_create(
            titulo=datos["titulo"],
            defaults={
                "categoria": datos.get("categoria", ""),
                "contenido": datos["contenido"],
            }
        )
        if created:
            creados += 1
            print(f"  [CREADO] {obj.titulo}")
        else:
            actualizados += 1
            print(f"  [ACTUALIZADO] {obj.titulo}")

    print(f"[OK] Resumen: {creados} nuevos, {actualizados} actualizados")


if __name__ == "__main__":
    print("-> Cargando mensajes de seed en QuickReply...")
    print(f"   Total de mensajes a procesar: {len(MENSAJES)}")
    load_messages()
    print("\n-> Seed completado.")