# Workflow: ghl-snapshot
## Objetivo
Coordinar el ciclo estricto y ordenado para diseñar, componer y entregar assets visuales engarzados a la configuración administrativa general de snapshots empaquetables de GoHighLevel apuntando primariamente a nichos técnicos o corporativos concretos en la industria.

## Modelos por fase
- **Diseño Estratégico:** (Sugerido por Estratega)
- **Layouts e Integraciones:** (Sugerido por Estratega)
- **QA Final y Verificación:** (Sugerido por Estratega)

## Agentes y orden de ejecución
`strategist` → `frontend` → `configurador_ghl` → `docs` → `qa`

## Paso a paso del flujo
1. Planifica tempranamente el `strategist` identificando el perfil nicho y los insumos requeridos trazando el blueprint en `spec.md`.
2. Habilita paso inicial el rol `frontend` para pre-armar cualquier dependencia visual (banners, logos, templates de landing page codificados estáticamente a usarse más adelante). Registra sus entregables.
3. Una vez surtido el banco de assets, interviene el genérico de la `configurador_ghl` usando interactivamente los recursos generados para formalizar en JSON/YAML los embudos, listados del snapshot, workflows automáticos referenciales y valores base.
4. El agente `docs` documentará la guía final de implementación ("Cómo instalar este Snapshot"), explicando paso a paso todos los custom values a rellenar por el usuario destinatario.
5. El escrutinio severo por parte de `qa` se desencadena comprobando en bloque todas las huellas transaccionales (checksums) y los cruces documentales para emitir un status válido reportado.

## Criterios de completado
Contar fehacientemente con los lineamientos gráficos exportables empaquetados e inicuos y los repositorios base textuales de la infraestructura GHL, acoplados fielmente a las normativas globales estipuladas por Argenis, libre de placeholders vacíos de la plataforma y bien referenciados inter-documentos.

## Artefactos esperados en output/
- Un paquete bien anidado `src/assets/` con las pautas de diseño exportadas por frontend.
- Subdirectorio `src/snapshot/` de manifiestos y esqueletos JSON/YAML lógicos.
- Pieza insustituible documental de usuario final: `docs/installation-guide.md` más reporte integrador de QA.

## Condiciones de pausa / HITL
- Fallos serializados al codificar o pre-visualizar el andamiaje del snapshot localmente que paralicen al configurador en tres instancias forzando `HITL_ESCALATION`.
