# Workflow: ghl-admin
## Objetivo
Establecer la correcta parametrización y despliegue sobre integraciones asimiladas en GoHighLevel; operando de puente seguro para auditar reportes, modificar cadencias de calendarios u optimizar workflows de marketing corporativo.

## Modelos por fase
- **Planteo estratégico del funnel:** (Sugerido por Estratega)
- **Agente especialista / Configurador:** (Sugerido por Estratega)
- **Calibración Terminal y Validaciones Estrictas:** (Sugerido por Estratega)

## Agentes y orden de ejecución
`strategist` → `agente_especializado_ghl` → `docs` → `qa`

## Paso a paso del flujo
1. El `strategist` diseña la lógica de marketing del objetivo (agendas, flujos de re-targetting) en `spec.md`.
2. El `agente_especializado_ghl` entra al área invocando decididamente la skill nativa `ghl` interrogando las pautas (campañas, subcuentas operantes) procediendo con read-only a extraer metadatos cruciales de lo que en ese momento exista instalado.
3. Se cotejan los vacíos o los faltantes, proveyendo al operador los cambios concretos y códigos JSON o sintaxis recomendadas en el artefacto respectivo de modificaciones para integrarlos localmente. 
4. Seguidamente, de resultar viables sus proposiciones las formaliza entregando el bloque técnico documentado `docs`.
5. El validador `qa` atestigua la pertinencia general del cambio contrastando que no haya riesgos sistémicos cruzados. Se despide con el `qa_report`.

## Criterios de completado
Se logra exponer con el output de este workflow la configuración íntegra aplicable. Ninguna sugerencia ha violado los estándares de privacidad, o invocado API con key defectuoso sin ser reportada formalmente a HITL. Las especificaciones de los calendarios cuadran en base horaria reportada al CRM.

## Artefactos esperados en output/
- Un repositorio JSON o archivos yaml de parametrización propuesta que detalla todos los trigger logic y workflows asimilables (No los inyectan, los preparan localmente).
- Bloque referencial maestro: `docs/ghl-guideline.md` u anexo similar y el infractor revisor documentado de reporte predeterminado.

## Condiciones de pausa / HITL
- Escala rotundamente tras percibir de modo estricto una señal del error 401 Unauthorized u de API Token revocado impidiendo su acceso perimetral. 
- La arquitectura deseada por el cliente demanda automatizaciones prohibitivas en la lógica actual de su CRM forzando rediseño manual.
