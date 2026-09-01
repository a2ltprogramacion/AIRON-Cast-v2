# context7
## Propósito de Herramienta
Define las condicionantes metodológicas estrictas sobre cuándo y cómo utilizar la extensión `context7` para absorber documentación técnica blindada oficial (frameworks, core, librerías, empaquetados, etc.). Esta skill funge como el portal maestro para que los agentes operantes eludan las alucinaciones por "laguna de memoria de base".

## 1. Condición de Activación Universal
Los agentes invocan esta macro exigentemente **"Antes de usar una librería o framework o una regla del stack sobre el cual no estás 100% peritamente seguro y comprobable respecto a su API actual."** (Ejemplos concretos: integraciones de librerías modernas de UI reactiva en un stack Alpine.js, despliegue de validadores recientes asíncronos en Django, u operaciones de Stripe/Pasarelas recientemente alteradas).

## 2. Metodología Obligatoria de Consulta
La resolución del flujo exime las suposiciones o atajos directos, pautando rigurosamente que las interrogantes sigan la pauta bifurcada:
- **Paso 1:** Ejecutar obligatoriamente `resolve-library-id` precisando el nombre general del empaquetado y extrayendo su ID resolutivo específico.
- **Paso 2:** Recurrir al núcleo usando el ID decodificado anterior con `query-docs` interrogando explícitamente y delimitando funcionalmente la duda de código puntual.

## 3. Disposición e Integración del Resultado Doc.
Al empaparse y compilar las respuestas resolutivas emitidas por el recurso, el agente debe:
Integrarlo fluidamente a su propio contexto cognitivo dinámico. El agente NO hace "copy & paste" puro ni vuelca el texto retornado dentro del artefacto código como una bola en crudo o comentario desproporcionado del backend/frontend. El agente adapta y codifica los principios rectores entendidos por el manual.

## 4. Cuándo NO Usar context7
Prohibido desgastar los canales o los tokens activándolo recursivamente. **SI este agente u operante asimiló ya el contexto normativo devuelto en su sesión/turno vivo actual y es un contexto asimilado activo**, o bien, el paso de un agente correlacionado ya dispuso en archivo este framework documentado.
