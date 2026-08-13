# Quickreply - Guia de Uso

> Para el operador de g3multistore: como usar Quickreply en el dia a dia.

---

## Primeros Pasos

1. Abre Quickreply en tu navegador (`http://localhost:4321` en dev, o el dominio configurado en produccion)
2. Veras la pantalla principal con la lista de mensajes

---

## 1. Buscar un Mensaje

**Opcion A: Escribir en la barra de busqueda**

1. Click en la barra de busqueda (o presiona `Ctrl+K`)
2. Escribe lo que queres responder. Ejemplos:
   - "precio bomba"
   - "horario"
   - "disponible envio"
   - "gracias"
3. Los resultados se filtran en tiempo real
4. La busqueda es **full-text** con coincidencias parciales: escribir "ventil" encuentra "ventiladores"

**Opcion B: Filtrar por categoria**

1. En la barra lateral izquierda, click en una categoria
2. La lista se filtra a solo mensajes de esa categoria
3. El contador en cada categoria te dice cuantos mensajes tiene
4. Click en "Todas" o "Favoritos" para limpiar el filtro

**Opcion C: Marcar como favorito**

1. Click en la estrella de una card
2. Los favoritos se identifican con estrella amarilla
3. En la barra lateral, click en "Favoritos" para ver solo esos

---

## 2. Copiar un Mensaje

**Forma rapida:**

1. Click en el boton **Copiar** (azul) en la card
2. Listo, el mensaje ya esta en tu portapapeles
3. Pega en el chat de Facebook (`Ctrl+V`)

**Con navegacion por teclado (rapidisimo):**

1. `Ctrl+K` para enfocar la barra de busqueda
2. Escribe lo que queres buscar
3. `ArrowDown` o `ArrowUp` para navegar entre resultados (la card seleccionada tiene borde resaltado)
4. `Enter` para copiar el mensaje seleccionado
5. Pegar en Facebook

**Si el mensaje tiene variables:**

1. Click en **Copiar** abre un modal pidiendo los valores
2. Completa cada campo (ej. nombre del cliente, producto)
3. El preview abajo muestra como quedara el mensaje final
4. Click en **Copiar** para confirmar
5. (O click en **Copiar sin variables** para copiar el texto con `{{marcadores}}` literales)

---

## 3. Crear un Mensaje Nuevo

1. Click en el boton **+ Nuevo mensaje** (esquina superior derecha)
2. Completa el formulario:
   - **Titulo**: nombre interno del mensaje (ej. "Promo de fin de semana")
   - **Contenido**: el texto que se enviara. Puedes usar `{{variables}}` si queres personalizar
   - **Categoria**: selecciona una de la lista
   - **Tags** (opcional): palabras clave adicionales (ej. "promo", "descuento")
   - **Favorito**: marca si lo usas frecuentemente
3. Las variables se detectan automaticamente y aparecen como pills abajo
4. Click **Guardar**

---

## 4. Editar o Archivar un Mensaje

1. Pasa el mouse sobre la card (en desktop) o toca la card (en mobile)
2. Aparecen los botones:
   - **Copiar** (azul)
   - **Editar** (borde)
   - **Archivar** (icono papelera, esquina derecha)
3. **Editar**: abre el modal con los datos pre-llenados
4. **Archivar**: oculta el mensaje de busquedas (no se borra, se puede recuperar)

---

## 5. Gestion de Categorias

1. Click en **Categorias** en el menu superior
2. Veras una tabla con:
   - Nombre
   - Color (8 colores disponibles)
   - Cantidad de mensajes
   - Estado (Activo/Archivado)
3. Acciones:
   - **+ Nueva categoria** (boton arriba a la derecha)
   - Click en el icono de **editar** (lapiz) para modificar
   - Click en el icono de **archivar** (papelera) para ocultar

---

## 6. Configurar Datos de Contacto

Los datos de contacto (telefono, Instagram, direccion, horario) son **globales** y aparecen en todos los mensajes que los referencien.

1. Abre `http://localhost:8000/admin/` (Django admin) en tu navegador
2. Login con las credenciales configuradas
3. Click en **Contact blocks**
4. Edita el unico registro (es un singleton):
   - **Phone**: tu numero (ej. `3001234567`)
   - **Instagram**: tu handle (ej. `@g3multistore`)
   - **Address**: direccion de la tienda
   - **Schedule**: horario de atencion
5. **Guardar**

> **Nota tecnica:** En el frontend, los datos del ContactBlock se exponen via `GET /api/contact/`. Si queres mostrarlos en alguna card o panel personalizado, solo tienes que hacer fetch a ese endpoint.

---

## 7. Atajos de Teclado

| Atajo | Accion |
|---|---|
| `Ctrl+K` (o `Cmd+K` en Mac) | Enfocar barra de busqueda |
| `Esc` | Limpiar busqueda |
| `ArrowUp` / `ArrowDown` | Navegar entre cards de resultados |
| `Enter` (sin focus en input) | Copiar mensaje seleccionado |
| `Enter` (en modal de variables) | Avanzar al siguiente campo / confirmar |

---

## 8. Indicadores Visuales

- **Card resaltada con borde azul**: mensaje actualmente seleccionado (navegacion por teclado)
- **Estrella amarilla**: favorito
- **Chip "Archivado"**: mensaje oculto de busquedas
- **Numero de "X usos"**: cuantas veces se ha copiado este mensaje
- **Pills mono con fondo gris**: variables `{{detectadas}}` en el mensaje
- **Toast verde abajo a la derecha**: confirmacion de copia exitosa (desaparece en 2 segundos)

---

## 9. Solucion de Problemas

### "No encuentro un mensaje que deberia estar"

- Verifica que no este archivado (filtro `is_archived`)
- Revisa la categoria correcta
- Escribe una palabra mas simple (ej. "bomba" en vez de "bomba periferica")
- Si lo creaste recien, puede estar oculto por el filtro de favoritos

### "El boton Copiar no hace nada"

- Verifica que el navegador tenga permisos de clipboard
- En algunos navegadores antiguos, hace falta HTTPS para la Clipboard API
- Quickreply tiene fallback automatico a `document.execCommand('copy')` para esos casos

### "El backend no responde"

- Verifica que `python manage.py runserver` este corriendo (deberia decir "Quit the server with CTRL-BREAK")
- Abre `http://localhost:8000/api/messages/` directamente para confirmar
- Si ves errores de CORS, verifica que el frontend este en `http://localhost:4321` (no otro puerto)

### "El frontend muestra pantalla en blanco"

- Verifica que el servidor de Astro este corriendo (`npm run dev` o `npm start`)
- Abre la consola del navegador (`F12`) y reporta el error
- Si hubo un cambio reciente en el schema, rebuildea: `npm run build`

### "Las variables no se reemplazan"

- Verifica que el formato sea `{{nombre_variable}}` (doble llave, sin espacios)
- En el modal, completa todos los campos antes de hacer click en Copiar
- Si una variable no tiene valor, se reemplaza por string vacio (no por error)

---

## 10. Mobile

Quickreply esta optimizado para usar en celular (375px → desktop):

- Botones tienen 44px de alto minimo (estandar de touch)
- El menu lateral se colapsa en mobile
- La busqueda funciona con teclado virtual
- Los modales se ajustan a pantallas pequenas

---

> Si tenes una duda que no esta aca, contacta al equipo de desarrollo.
