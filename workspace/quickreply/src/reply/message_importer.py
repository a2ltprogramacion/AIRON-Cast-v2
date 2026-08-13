"""
Message Importer — QuickReply
=============================
Maneja la importacion de mensajes en masa desde texto plano,
Markdown o JSON.

Formatos soportados:

1. MARKDOWN (recomendado)
   =======================
   Separador: ---
   Estructura por bloque:

   [Categoria]
   # Titulo del mensaje
   Contenido en multiples lineas.
   Aqui va el cuerpo del mensaje.
   {F012_usd} y {F012_bcv} funcionan igual.

   ---

   [Otra Categoria]
   # Otro titulo
   Otro contenido...

   El primer [CATEGORIA] antes del titulo es la categoria.
   Todo lo demas es el contenido. El # Titulo se usa como titulo.


2. JSON (para integrations)
   ==========================
   [
     {
       "titulo": "Nombre del mensaje",
       "categoria": "Ventiladores",
       "contenido": "Hola {F012_usd}...{F012_bcv}..."
     },
     {
       "titulo": "Otro mensaje",
       "categoria": "Bombas",
       "contenido": "Contenido..."
     }
   ]

3. TEXTO PLANO
   ============
   Separador: ---

   [Categoria] Titulo del mensaje
   Primera linea del contenido
   Segunda linea del contenido

   ---

   [Otra] Otro titulo
   Primer linea
   Segunda linea

   La categoria es opcional (puede omitirse el [Categoria] ).
   Si no hay [ ], todo hasta el primer salto es el titulo.
"""

import re
import json
from typing import Optional


def detectar_formato(texto: str) -> str:
    texto_stripped = texto.strip()
    if texto_stripped.startswith("[") or texto_stripped.startswith("{"):
        if texto_stripped.startswith("{"):
            try:
                json.loads(texto_stripped)
                return "json"
            except Exception:
                pass
        if "---" in texto_stripped and ("#" in texto_stripped or "[" in texto_stripped):
            return "markdown"
        if "---" in texto_stripped:
            return "plain"
    if texto_stripped.startswith("["):
        return "plain"
    if "---" in texto_stripped:
        return "markdown"
    if "[" in texto_stripped and "]" in texto_stripped:
        return "plain"
    return "markdown"


def parse_plain(texto: str) -> list[dict]:
    """
    Formato texto plano:
    [Categoria] Titulo
    Linea 1 del contenido
    Linea 2
    ---
    [Otra] Otro titulo
    Contenido
    ---
    """
    bloques = re.split(r"\n---\n", texto)
    resultados = []

    for bloque in bloques:
        if not bloque.strip():
            continue

        lineas = bloque.strip().split("\n")
        primera = lineas[0].strip()

        categoria_match = re.match(r"^\[([^\]]+)\]\s*(.+)$", primera)
        if categoria_match:
            categoria = categoria_match.group(1).strip()
            titulo = categoria_match.group(2).strip()
            contenido = "\n".join(lineas[1:]).strip()
        else:
            titulo = primera
            categoria = None
            contenido = "\n".join(lineas[1:]).strip()

        if not titulo or not contenido:
            continue

        resultados.append({
            "titulo": titulo,
            "categoria": categoria or "",
            "contenido": contenido,
        })

    return resultados


def parse_markdown(texto: str) -> list[dict]:
    """
    Formato Markdown:
    [Categoria]
    # Titulo
    Contenido multilinea

    ---
    [Otra]
    # Otro titulo
    Contenido
    """
    bloques = re.split(r"\n---\n", texto)
    resultados = []

    for bloque in bloques:
        if not bloque.strip():
            continue

        lineas = bloque.strip().split("\n")
        categoria = None
        titulo = None
        contenido_partes = []
        en_contenido = False

        for i, linea in enumerate(lineas):
            l = linea.strip()

            if not en_contenido:
                cat_match = re.match(r"^\[([^\]]+)\]$", l)
                if cat_match:
                    categoria = cat_match.group(1).strip()
                    continue

                if l.startswith("# "):
                    titulo = l[2:].strip()
                    en_contenido = True
                    continue

                if i == 0 and not l.startswith("#") and not l.startswith("["):
                    titulo = l
                    en_contenido = True
                    continue
            else:
                contenido_partes.append(l)

        if not titulo:
            continue

        contenido = "\n".join(contenido_partes).strip()
        if not contenido:
            contenido = titulo

        resultados.append({
            "titulo": titulo,
            "categoria": categoria or "",
            "contenido": contenido,
        })

    return resultados


def parse_json(texto: str) -> list[dict]:
    """
    Formato JSON: array de objetos con titulo, categoria y contenido.
    """
    datos = json.loads(texto.strip())
    if isinstance(datos, dict):
        datos = [datos]
    if not isinstance(datos, list):
        raise ValueError("JSON debe ser un array de mensajes o un objeto unico")

    resultados = []
    for item in datos:
        if not isinstance(item, dict):
            continue
        titulo = str(item.get("titulo", item.get("title", ""))).strip()
        categoria = str(item.get("categoria", item.get("category", ""))).strip()
        contenido = str(item.get("contenido", item.get("content", ""))).strip()

        if not titulo:
            continue

        resultados.append({
            "titulo": titulo,
            "categoria": categoria,
            "contenido": contenido,
        })

    return resultados


def importar_mensajes(texto: str, formato: Optional[str] = None) -> dict:
    """
    Importa mensajes desde texto plano.

    Args:
        texto: Contenido con los mensajes en el formato elegido
        formato: 'json', 'markdown' o 'plain'. Si es None, se detecta automaticamente.

    Returns:
        dict con:
            - total: int
            - creados: int
            - actualizados: int
            - errores: list[str]
            - mensajes: list[dict] con datos de cada mensaje (para preview)
    """
    from reply.models import MessageTemplate

    stats = {
        "total": 0,
        "creados": 0,
        "actualizados": 0,
        "errores": [],
        "mensajes": [],
    }

    if not texto or not texto.strip():
        stats["errores"].append("El texto esta vacio.")
        return stats

    fmt = formato or detectar_formato(texto)
    fmt = fmt.lower().strip()

    try:
        if fmt == "json":
            parsed = parse_json(texto)
        elif fmt == "plain":
            parsed = parse_plain(texto)
        else:
            parsed = parse_markdown(texto)
    except json.JSONDecodeError as e:
        stats["errores"].append(f"JSON invalido: {e}")
        return stats
    except Exception as e:
        stats["errores"].append(f"Error al parsear: {e}")
        return stats

    stats["total"] = len(parsed)

    for item in parsed:
        try:
            if not item["titulo"] or not item["contenido"]:
                continue

            obj, created = MessageTemplate.objects.update_or_create(
                titulo=item["titulo"],
                defaults={
                    "categoria": item["categoria"] or None,
                    "contenido": item["contenido"],
                },
            )

            if created:
                stats["creados"] += 1
            else:
                stats["actualizados"] += 1

            stats["mensajes"].append({
                "id": obj.id,
                "titulo": obj.titulo,
                "categoria": obj.categoria or "",
                "creado": created,
            })

        except Exception as e:
            stats["errores"].append(f"Error con '{item['titulo'][:30]}...': {e}")

    return stats


def crear_mensaje_individual(titulo: str, categoria: str, contenido: str) -> dict:
    """
    Crea un solo mensaje individual.

    Returns:
        dict con id, titulo, categoria, creado (bool), error
    """
    from reply.models import MessageTemplate

    if not titulo or not titulo.strip():
        return {"error": "El titulo es obligatorio."}
    if not contenido or not contenido.strip():
        return {"error": "El contenido es obligatorio."}

    try:
        obj, created = MessageTemplate.objects.update_or_create(
            titulo=titulo.strip(),
            defaults={
                "categoria": categoria.strip() or None,
                "contenido": contenido,
            },
        )
        return {
            "id": obj.id,
            "titulo": obj.titulo,
            "categoria": obj.categoria or "",
            "creado": created,
        }
    except Exception as e:
        return {"error": str(e)}