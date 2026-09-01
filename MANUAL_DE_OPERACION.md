# MANUAL DE OPERACIÓN — AIRON-Cast v2.0 (Edición Final $0 Budget)

> **Operador:** Argenis @ A2LT Soluciones  
> **Arquitectura:** Orquestación Determinista Round-Robin + SQLite/FTS5 + $0 Model Fallbacks  
> **Estado:** Listo para operación local autónoma sin suscripciones de pago.

---

## 1. Visión General y Filosofía de Operación

AIRON-Cast está diseñado para que no dependas de ninguna plataforma propietaria ni suscripción costosa:
1. **Pizarra Compartida y Memoria Persistente:** Todo el estado, bitácoras, checkpoints y decisiones técnicas (ADRs) se guardan localmente en SQLite (`central_intelligence.db`) con soporte de búsqueda semántica FTS5.
2. **Motor Desacoplado ($0 Budget):** Puedes usar cualquier LLM (gratuito vía OpenRouter, Groq, Ollama en tu PC local, o Gemini Free) para ejecutar los roles de los agentes. El orquestador te entrega el prompt estructurado y tú (o un script) ejecutas el paso.
3. **Supervisor y Dashboard Autónomos:** El watchdog supervisa la base de datos y sirve una interfaz gráfica local en tiempo real.

---

## 2. Iniciar el Ecosistema

### Paso 1: Levantar el Supervisor y Dashboard
En una terminal (PowerShell o CMD):
```powershell
python tools/airon_nl.py "levanta el dashboard"
```
O directamente:
```powershell
python tools/dashboard_server.py
```
- **URL del Dashboard:** [http://localhost:8765](http://localhost:8765)
- El Dashboard monitorea en vivo: estado del supervisor, proyectos activos, porcentaje de avance, artefactos generados y timeline de eventos.

### Paso 2: Verificar la Salud del Sistema
```powershell
python tools/airon_nl.py "salud"
# o:
python tools/airon_executor.py health
```

---

## 3. Flujo de Trabajo en un Proyecto (Paso a Paso)

### A. Crear un nuevo proyecto
1. Crea una carpeta en `workspace/<slug>/` (ejemplo: `workspace/mi-landing/`).
2. Añade un archivo `BACKLOG.md` con la tabla de tareas y prioridades (puedes tomar como plantilla `workspace/cafe-cenit/BACKLOG.md`).
3. Registra el proyecto en el ecosistema:
```powershell
python tools/airon_executor.py bootstrap mi-landing
```

### B. Consultar el estado del proyecto
```powershell
python tools/airon_nl.py "estado mi-landing"
# o para ver todos los proyectos:
python tools/airon_nl.py "estado"
```

### C. Despachar el siguiente turno (Round-Robin)
Pide el siguiente turno listo para trabajar:
```powershell
python tools/airon_executor.py dispatch mi-landing
```
*El orquestador devolverá un JSON con el rol del agente asignado (ej. `ux-ui_specialist`, `frontend_worker`, `tester`), el contexto acumulado y el prompt listo para ser ejecutado por el LLM.*

### D. Completar la tarea y registrar artefactos
Una vez que el modelo genere los archivos en `workspace/<slug>/`:
```powershell
python tools/airon_executor.py complete mi-landing <task_id> --artifacts workspace/mi-landing/src/archivo.astro
```

### E. Aprobar por QA y Finalizar
- **Aprobar (QA Auditor):**
  ```powershell
  python tools/airon_executor.py approve mi-landing <task_id>
  ```
- **Finalizar:**
  ```powershell
  python tools/airon_executor.py finalize mi-landing <task_id>
  ```

---

## 4. Modelos Gratuitos Recomendados ($0 Budget)

Puedes configurar tus agentes o alimentar los prompts del orquestador en cualquiera de estas opciones sin costo:

| Función | Modelo Recomendado | Proveedor | Costo |
|---|---|---|---|
| **Arquitectura y Código Complejo** | `deepseek/deepseek-chat-v3-0324:free` | OpenRouter | $0 |
| **Generación Rápida de Componentes** | `qwen/qwen-2.5-coder-32b-instruct:free` | OpenRouter | $0 |
| **Alta Velocidad y Revisión** | `llama-3.1-8b-instant` | Groq API | $0 (Tier Free) |
| **Razonamiento Multimodal y Contexto Largo** | `gemini-2.0-flash` / `gemini-1.5-flash` | Google AI Studio | $0 (Free Tier) |
| **100% Offline / Local** | `qwen2.5-coder:7b` o `deepseek-r1:8b` | Ollama (Local) | $0 (Local PC) |

---

## 5. Mantenimiento y Comandos de Emergencia

- **Detener todos los servicios:**
  ```powershell
  python tools/stop_supervisor.py --force
  ```
- **Reinicializar la base de datos limpia:**
  ```powershell
  python tools/init_ecosystem.py
  ```
- **Ejecutar suite de pruebas de integridad:**
  ```powershell
  python -m pytest
  ```
