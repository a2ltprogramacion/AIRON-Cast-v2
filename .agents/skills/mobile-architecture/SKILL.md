---
name: mobile-architecture
description: "Ingeniería Mobile-First estricta para iOS y Android. Impone Cálculo de Riesgos (MFRI), prohibiciones de UI (tamaño táctil de 44-48px), Optimización de Rendimiento (FlatList) y Manejo de estado Offline usando React Native o Flutter."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Mobile Engineering Architecture (A2LT Standard)

Esta skill previene automáticamente el "Pensamiento de Escritorio" al diseñar para móviles. Imponer el uso restrictivo de UI/UX orientado a dispositivos móviles y su rendimiento en sistemas cruzados o nativos.

---

## 1. El Índice de Factibilidad Móvil (MFRI)

Antes de construir CUALQUIER feature, evalúa las siguientes dimensiones penalizadoras y positivas:

- Claridad de Plataforma vs Complejidad de Interacción.
- Riesgo de Rendimiento vs Dependencia Offline.
- Si el puntaje resultante dicta alto riesgo ("Dangerous"), detente y rediseña antes de escribir la primera línea de código.

## 2. Los Pecados del Rendimiento (Hard Bans)

No negocies estas reglas, bajo ningún contexto:

- **ScrollView para Listas Infinitas:** `PROHIBIDO`. Utiliza siempre `FlatList` (o `FlashList`) en React Native y `ListView.builder` en Flutter. Explotarás la memoria si usas ScrollView normal.
- **Componentes Anidados (Inline Render):** Extrae los componentes de listas y memoízalos con `React.memo` o marcándolos como `const Widget` en Flutter.
- **Animaciones en el Hilo de JS:** `PROHIBIDO`. Utiliza controladores nativos de animación o hardware-accelerated drivers.

## 3. Psicología UX y Reglas Táctiles (Ley de Fitts)

Un error fundamental de IA es asumir un ratón o puntero preciso cuando hay dedos gruesos e interfaces temblorosas.

- **Zonas Pulgares:** Los Call-to-Actions (CTAs) principales deben ubicarse en la mitad inferior de la pantalla o flotantes, al alcance de un pulgar natural.
- **Blancos Táctiles (Touch Targets):** `NUNCA` uses áreas touch más pequeñas de 44pt (iOS) o 48dp (Android).
- **Feedback y Tiempo Real:** Cada tap debe tener un cambio visual de estado (Ripple, Opacity) instántaneo o un spinner de carga no bloqueante.

## 4. Diferenciación de Plataforma Obligatoria

- iOS: `SF Pro` / `44pt min` / Navegación por Swipe lateral y Bottm Sheets. Modales apilados.
- Android: `Roboto` / `48dp min` / System Back navigation / Bottom Sheets modales (Dialogs).

## 5. El Límite de Offline y Seguridad

- **Offline Fallbacks:** Muestra inmediatamente la interfaz en caché. Nunca bloquees una app entera detrás de un loading de Splash si no hay conexión. Inyecta colas de sync.
- **Seguridad PII/Tokens:** Prohibidísimo el uso de `AsyncStorage` o SharedPreferences sin encriptar para Tokens JWT. Usa siempre `SecureStore` (iOS Keychain, Android Keystore).
