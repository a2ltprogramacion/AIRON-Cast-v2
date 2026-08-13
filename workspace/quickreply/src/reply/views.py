"""
Views para QuickReply: dashboard, upload Excel, busqueda de templates.
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from reply.models import Product, MessageTemplate
from reply.utils import cargar_excel, render_template
from reply.message_importer import importar_mensajes, crear_mensaje_individual


def dashboard(request):
    """Renderiza la vista principal de QuickReply."""
    total_productos = Product.objects.count()
    total_templates = MessageTemplate.objects.count()
    ult_actualizacion = (
        Product.objects.order_by("-actualizado_el").first()
    )
    return render(
        request,
        "reply/index.html",
        {
            "total_productos": total_productos,
            "total_templates": total_templates,
            "ult_actualizacion": ult_actualizacion.actualizado_el if ult_actualizacion else None,
        },
    )


@require_http_methods(["POST"])
def upload_excel(request):
    """
    Procesa la carga de un archivo Excel (.xlsx) con la lista de precios.

    Espera el archivo en el campo 'archivo_excel' del formulario multipart.
    Utiliza Django Messages para notificar el resultado.
    """
    if "archivo_excel" not in request.FILES:
        messages.error(request, "No se recibio ningun archivo.")
        return render(request, "reply/index.html")

    archivo = request.FILES["archivo_excel"]

    if not archivo.name.endswith((".xlsx", ".xls")):
        messages.error(request, "Formato no soportado. Solo se aceptan archivos .xlsx o .xls")
        return render(request, "reply/index.html")

    stats = cargar_excel(archivo)

    if stats["debug"]:
        debug = stats["debug"]
        if "hojas_encontradas" in debug:
            msgs = []
            msgs.append(f"Hojas detectadas: {debug['hojas_encontradas']}")
            if "hoja_usada" in debug:
                msgs.append(f"Hoja usada: '{debug['hoja_usada']}'")
            if "columnas_detectadas" in debug:
                cols = debug["columnas_detectadas"]
                msgs.append(f"Columnas ({len(cols)}): {cols[:8]}{'...' if len(cols) > 8 else ''}")
            if "col_usd" in debug:
                msgs.append(f"Columna USD: '{debug['col_usd']}' | BCV: '{debug['col_bcv']}'")
            if "filas_en_hoja" in debug:
                msgs.append(f"Filas en hoja: {debug['filas_en_hoja']}")
            for m in msgs:
                messages.info(request, m)

    if stats["errores"]:
        for err in stats["errores"][:5]:
            messages.warning(request, err)

    if stats["total"] == 0:
        messages.error(
            request,
            "No se cargaron productos. Revisa los mensajes de diagnostico arriba."
        )
    else:
        msg = f"Productos cargados: {stats['total']} | Nuevos: {stats['creados']} | Actualizados: {stats['actualizados']}"
        messages.success(request, msg)

    return render(request, "reply/index.html")


@require_http_methods(["GET"])
def search_templates(request):
    """
    Endpoint de busqueda de plantillas.

    Parametros:
        q (str): consulta de busqueda (opcional).
                 Busca en titulo y categoria.

    Retorna:
        JSON array de objetos con:
            - id: int
            - titulo: str
            - categoria: str
            - contenido: str (renderizado con precios actuales)
    """
    query = request.GET.get("q", "").strip()

    if query:
        templates = MessageTemplate.objects.filter(
            titulo__icontains=query
        ) | MessageTemplate.objects.filter(categoria__icontains=query)
    else:
        templates = MessageTemplate.objects.all()

    templates = templates.order_by("categoria", "titulo")[:50]

    resultados = []
    for t in templates:
        contenido_renderizado = render_template(t.contenido)

        resultados.append({
            "id": t.id,
            "titulo": _sanitizar_para_json(t.titulo),
            "categoria": _sanitizar_para_json(t.categoria or ""),
            "contenido": contenido_renderizado,
        })

    return JsonResponse({"resultados": resultados, "total": len(resultados)})


def _sanitizar_para_json(texto):
    """Escapa caracteres especiales para JSON responses."""
    if texto is None:
        return ""
    return (
        str(texto)
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )


@require_http_methods(["POST"])
def import_individual(request):
    """
    Crea un solo mensaje individual.

    Parametros POST:
        titulo: str (requerido)
        categoria: str (opcional)
        contenido: str (requerido) — puede ser contenido directo o formato plano completo
    """
    titulo = request.POST.get("titulo", "").strip()
    categoria = request.POST.get("categoria", "").strip()
    contenido = request.POST.get("contenido", "").strip()

    # Si el contenido parece formato plano (Titulo:/Categoria:/Contenido:), parsearlo
    if contenido.startswith("Titulo:") or contenido.startswith("Titulo\n"):
        parsed = _parsear_formato_plano_individual(contenido)
        if parsed:
            titulo = parsed.get("titulo", titulo)
            categoria = parsed.get("categoria", categoria)
            contenido = parsed.get("contenido", contenido)

    if not titulo:
        messages.error(request, "El titulo es obligatorio.")
        return render(request, "reply/index.html")
    if not contenido:
        messages.error(request, "El contenido es obligatorio.")
        return render(request, "reply/index.html")

    resultado = crear_mensaje_individual(titulo, categoria, contenido)

    if "error" in resultado:
        messages.error(request, resultado["error"])
    else:
        accion = "creado" if resultado["creado"] else "actualizado"
        messages.success(request, f"Mensaje '{resultado['titulo']}' {accion} exitosamente.")

    return render(request, "reply/index.html")


def _parsear_formato_plano_individual(texto: str) -> dict | None:
    """
    Parsea el formato plano individual:
    Titulo: Nombre del mensaje
    Categoria: Nombre categoria
    Contenido: Cuerpo del mensaje (puede tener multiples lineas)

    Retorna dict con titulo, categoria, contenido o None si no coincide.
    """
    import re

    lineas = texto.split("\n")
    resultado = {"titulo": "", "categoria": "", "contenido": ""}

    i = 0
    while i < len(lineas):
        linea = lineas[i].strip()
        if linea.startswith("Titulo:") or linea.startswith("Titulo"):
            # Extraer todo despues de "Titulo:" o en la siguiente linea
            if ":" in linea:
                resultado["titulo"] = linea.split(":", 1)[1].strip()
            elif i + 1 < len(lineas):
                resultado["titulo"] = lineas[i + 1].strip()
                i += 1
        elif linea.startswith("Categoria:") or linea.startswith("Categoria"):
            if ":" in linea:
                resultado["categoria"] = linea.split(":", 1)[1].strip()
            elif i + 1 < len(lineas):
                resultado["categoria"] = lineas[i + 1].strip()
                i += 1
        elif linea.startswith("Contenido:") or linea.startswith("Contenido"):
            # El contenido es todo lo que sigue
            if ":" in linea:
                resultado["contenido"] = linea.split(":", 1)[1].strip()
            else:
                resultado["contenido"] = ""
            # Agregar las lineas restantes
            resto = "\n".join(lineas[i + 1:]).strip()
            if resto:
                resultado["contenido"] = (resultado["contenido"] + "\n" + resto).strip() if resultado["contenido"] else resto
            break
        i += 1

    if resultado["titulo"] and resultado["contenido"]:
        return resultado
    return None


@require_http_methods(["POST"])
def import_bulk(request):
    """
    Importa mensajes en masa desde texto.

    Parametros POST:
        texto: str (contenido del mensaje en formato JSON, Markdown o texto plano)
        formato: 'json' | 'markdown' | 'plain' (opcional, se detecta automaticamente)

    Soporta tanto submission normal como AJAX (application/json).
    """
    import json as json_lib

    if request.content_type and "application/json" in request.content_type:
        try:
            body = json_lib.loads(request.body)
            texto = body.get("texto", "")
            formato = body.get("formato")
        except Exception:
            return JsonResponse({"error": "JSON invalido"}, status=400)
    else:
        texto = request.POST.get("texto", "").strip()
        formato = request.POST.get("formato", "").strip() or None

    if not texto:
        return JsonResponse({"error": "El texto esta vacio."}, status=400)

    stats = importar_mensajes(texto, formato)

    if request.content_type and "application/json" in request.content_type:
        return JsonResponse(stats)

    for err in stats["errores"][:5]:
        messages.warning(request, err)

    if stats["total"] == 0:
        messages.error(request, "No se encontraron mensajes validos en el texto.")
    else:
        accion = "importados" if stats["creados"] > 0 else "actualizados"
        messages.success(
            request,
            f"{stats['total']} mensaje{'' if stats['total'] == 1 else 's'} procesados: "
            f"{stats['creados']} nuevos, {stats['actualizados']} actualizados."
        )

    return render(request, "reply/index.html")


@require_http_methods(["GET"])
def api_templates_list(request):
    """
    Lista todos los mensajes (para el panel de importacion).
    No renderiza tokens, retorna el contenido original.

    Parametros GET:
        q: busqueda por titulo o categoria (opcional)
    """
    query = request.GET.get("q", "").strip()
    if query:
        templates = MessageTemplate.objects.filter(
            titulo__icontains=query
        ) | MessageTemplate.objects.filter(categoria__icontains=query)
    else:
        templates = MessageTemplate.objects.all()

    templates = templates.order_by("categoria", "titulo")

    resultados = []
    for t in templates:
        resultados.append({
            "id": t.id,
            "titulo": t.titulo,
            "categoria": t.categoria or "",
            "contenido": t.contenido,
            "copy_count": t.copy_count,
        })

    return JsonResponse({
        "resultados": resultados,
        "total": len(resultados),
    })


@require_http_methods(["POST"])
def delete_template(request, template_id):
    """Elimina un mensaje por ID. Solo acepta POST."""
    try:
        obj = MessageTemplate.objects.get(id=template_id)
        titulo = obj.titulo
        obj.delete()
        messages.success(request, f"Mensaje '{titulo}' eliminado.")
    except MessageTemplate.DoesNotExist:
        messages.error(request, "Mensaje no encontrado.")
    except Exception as e:
        messages.error(request, f"Error al eliminar: {e}")

    return render(request, "reply/index.html")


def edit_template(request, template_id):
    """Edita un mensaje por ID. Solo acepta POST."""
    if request.method == "POST":
        try:
            obj = MessageTemplate.objects.get(id=template_id)
            obj.titulo = request.POST.get("titulo", "").strip()
            obj.categoria = request.POST.get("categoria", "").strip()
            obj.contenido = request.POST.get("contenido", "").strip()
            if not obj.titulo or not obj.contenido:
                messages.error(request, "Titulo y contenido son obligatorios.")
            else:
                obj.save()
                messages.success(request, f"Mensaje '{obj.titulo}' actualizado.")
        except MessageTemplate.DoesNotExist:
            messages.error(request, "Mensaje no encontrado.")
        except Exception as e:
            messages.error(request, f"Error al actualizar: {e}")

    return render(request, "reply/index.html")