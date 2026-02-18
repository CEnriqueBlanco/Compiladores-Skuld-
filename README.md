# 🦅 Skuld IDE — Compiladores 1

> **Universidad Autónoma de Aguascalientes**  
> Materia: Compiladores 1 | Dra. Blanca G. Estrada Rentería  
> Fecha: 13 de febrero de 2026

---

## 👥 Creadores

| Nombre | 
|--------|
| **Alan Gael Gallardo Jiménez** |
| **Carlos Enrique Blanco Ortiz** |

---

## 📌 Descripción General

**Skuld IDE** es un Entorno de Desarrollo Integrado (IDE) diseñado e implementado como herramienta independiente para interactuar con las distintas fases de un compilador para un lenguaje de alto nivel.

El IDE actúa como **interfaz gráfica** que facilita:
- La edición de código fuente.
- La compilación por fases.
- La visualización de resultados en tiempo real.
- La depuración del proceso de compilación.

> El IDE y el compilador son **módulos completamente separados**. El IDE únicamente invoca al compilador mediante llamadas al sistema (system calls), y el compilador puede ejecutarse de forma autónoma desde la línea de comandos.

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                         SKULD IDE                           │
│                   (Interfaz Gráfica / GUI)                  │
│                                                             │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────┐  │
│  │  Editor de   │   │   Menú de    │   │  Botones de    │  │
│  │    Texto     │   │   Archivos   │   │ Acceso Rápido  │  │
│  └──────────────┘   └──────────────┘   └────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               Paneles de Resultados                  │   │
│  │  Léxico | Sintáctico | Semántico | Cód. Intermedio   │   │
│  │  Tabla de Símbolos | Errores | Ejecución             │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │  System Call
                           │  (archivos / parámetros)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    COMPILADOR (Analizador)                   │
│                  Módulo Independiente / CLI                  │
│                                                             │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Análisis │→ │ Análisis  │→ │ Análisis │→ │   Gen.   │  │
│  │  Léxico  │  │ Sintáctico│  │ Semántico│  │  Código  │  │
│  └──────────┘  └───────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Principios de Arquitectura
- **Desacoplamiento total**: El IDE y el compilador son módulos separados.
- **Compilador autónomo**: Puede ejecutarse desde consola sin necesidad del IDE.
- **Comunicación**: Mediante archivos intermedios o parámetros de ejecución.
- **Modularidad**: Estructurado para facilitar futuras extensiones.

---

## ⚙️ Fases del Compilador

| # | Fase | Descripción |
|---|------|-------------|
| 1 | **Análisis Léxico** | Tokenización del código fuente |
| 2 | **Análisis Sintáctico** | Construcción del árbol sintáctico |
| 3 | **Análisis Semántico** | Validación de tipos y semántica |
| 4 | **Generación de Código Intermedio** | Código de tres direcciones u otra representación |
| 5 | **Ejecución** | Ejecución del programa compilado |

---

## 🖥️ Requerimientos Funcionales

### 2.1 Gestión de Archivos

El IDE incluye un **menú principal** con las siguientes opciones bajo `Archivo`:

- 📄 **Nuevo** — Crea un nuevo archivo de código fuente.
- 📂 **Abrir** — Carga un archivo existente.
- ❌ **Cerrar** — Cierra el archivo actual.
- 💾 **Guardar** — Guarda el archivo actual.
- 💾 **Guardar como** — Guarda con un nombre/ubicación diferente.
- 🚪 **Salir** — Cierra el IDE.

### 2.2 Proceso de Compilación

El menú `Compilar` permite acceder a cada fase del compilador:
- Análisis Léxico
- Análisis Sintáctico
- Análisis Semántico
- Generación de Código Intermedio
- Ejecución

Además, se incluyen **botones de acceso rápido** para cada acción.

---

## 🗃️ Componentes de la Interfaz Gráfica

| Panel | Descripción |
|-------|-------------|
| **Editor de Texto** | Edición de código fuente con numeración de líneas y posición del cursor |
| **Resultado Léxico** | Lista de tokens generados por el analizador léxico |
| **Resultado Sintáctico** | Árbol sintáctico o salida estructurada |
| **Resultado Semántico** | Validaciones y verificación de tipos |
| **Código Intermedio** | Representación generada (ej. código de tres direcciones) |
| **Tabla de Símbolos** | Variables, funciones e identificadores del programa |
| **Lista de Errores** | Errores léxicos, sintácticos y semánticos con número de línea y descripción |
| **Resultado de Ejecución** | Salida del programa compilado |

---

## 📋 Criterios de Evaluación

- ✅ La fase se considera completa **únicamente si cumple el 100%** de los requerimientos especificados.
- ⏰ Cada día de retraso implica una **penalización del 10%** sobre la calificación de la fase.
- 🚫 No se aceptarán fases incompletas.
- 👥 El equipo deberá presentarse **completo** en la revisión correspondiente.

---

## 🗺️ Fases del Proyecto

- [x] **Fase 1** — Desarrollo del IDE (Entorno de Desarrollo Integrado)
- [ ] **Fase 2** — Análisis Léxico
- [ ] **Fase 3** — Análisis Sintáctico
- [ ] **Fase 4** — Análisis Semántico
- [ ] **Fase 5** — Generación de Código Intermedio

---

## 🛠️ Consideraciones de Diseño

- El IDE debe ser **intuitivo y funcional**.
- Debe permitir visualizar **simultáneamente múltiples paneles**.
- Debe facilitar la **depuración** del proceso de compilación.
- Debe estar estructurado de forma **modular** para futuras extensiones.
- El desarrollo es completamente propio, aunque se toman como referencia IDEs existentes como VS Code, Eclipse y NetBeans.

---

<p align="center">
  <strong>Skuld IDE</strong> — Compiladores 1 · UAA · 2026
</p>
