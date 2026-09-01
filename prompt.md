# Gestor Académico de Notas - Especificación Técnica

## Rol
Eres un desarrollador Python full-stack especializado en aplicaciones educativas con Streamlit. Tu objetivo es construir un sistema robusto, escalable y fácil de usar.

## Objetivo
**Problema:** Los estudiantes y docentes necesitan una herramienta local para organizar y calcular calificaciones de múltiples asignaturas con un sistema de cortes (parciales).

**Usuario:** Estudiantes de educación media/superior y docentes.

**Resultado esperado:** Una aplicación web interactiva que gestione asignaturas, cortes, actividades y notas, con cálculos automáticos, persistencia en SQLite y visualización gráfica.

## Stack Tecnológico
- **Backend:** Python 3.9+
- **Frontend:** Streamlit
- **Base de datos:** SQLite (local, sin servidor)
- **Datos y gráficos:** Pandas, Plotly
- **Gestión de dependencias:** pip + requirements.txt
- **Versionado:** Git

## Requisitos Funcionales (RF)

| ID   | Requisito |
|------|-----------|
| RF01 | Crear y seleccionar asignaturas. |
| RF02 | Cada asignatura debe manejar exactamente tres cortes. |
| RF03 | Definir el porcentaje de cada corte y validar que la suma de los tres sea 100%. |
| RF04 | Agregar actividades ilimitadas dentro de cada corte. |
| RF05 | Definir el porcentaje de cada actividad dentro del corte y validar que la suma del corte pueda llegar a 100%. |
| RF06 | Registrar y actualizar la nota de cada actividad en escala de 0,0 a 5,0. |
| RF07 | Calcular automáticamente la nota de cada corte según el peso de sus actividades. |
| RF08 | Calcular la nota acumulada de la asignatura y mostrar la nota final cuando esté evaluado el 100%. |
| RF09 | Mostrar el porcentaje de la asignatura que ya ha sido evaluado. |
| RF10 | Mostrar un gráfico de barras con las asignaturas y su nota acumulada/final. |
| RF11 | Calcular el promedio general de las asignaturas registradas. |
| RF12 | Guardar asignaturas, cortes, actividades y notas en SQLite y recuperarlos al reiniciar la app local. |

## Requisitos No Funcionales (RNF)

| ID    | Requisito |
|-------|-----------|
| RNF01 | Interfaz clara, consistente y comprensible sin explicación extensa. |
| RNF02 | Validar campos obligatorios, porcentajes y notas antes de guardar. |
| RNF03 | Código organizado en funciones y, si es necesario, módulos. |
| RNF04 | Persistencia local mediante SQLite con creación automática de tablas. |
| RNF05 | No guardar contraseñas, tokens ni secretos dentro del código o repositorio. |
| RNF06 | La aplicación debe ejecutarse desde requirements.txt y publicarse en Streamlit. |
| RNF07 | El repositorio debe mostrar commits que evidencien el proceso de desarrollo. |

## Modelo de Datos (Entidades)

### Asignatura
- `id` (INT, PRIMARY KEY, AUTO_INCREMENT)
- `nombre` (VARCHAR, UNIQUE, NOT NULL)
- `fecha_creacion` (TIMESTAMP, DEFAULT NOW)

### Corte
- `id` (INT, PRIMARY KEY, AUTO_INCREMENT)
- `asignatura_id` (INT, FOREIGN KEY → Asignatura.id)
- `numero` (INT, CHECK 1-3, NOT NULL)
- `porcentaje` (DECIMAL 5,2, NOT NULL)
- `constraint UNIQUE(asignatura_id, numero)`

### Actividad
- `id` (INT, PRIMARY KEY, AUTO_INCREMENT)
- `corte_id` (INT, FOREIGN KEY → Corte.id)
- `nombre` (VARCHAR, NOT NULL)
- `porcentaje` (DECIMAL 5,2, NOT NULL)
- `nota` (DECIMAL 3,1, CHECK 0-5, DEFAULT NULL)
- `fecha_creacion` (TIMESTAMP, DEFAULT NOW)

## Reglas de Negocio y Cálculos

### Validaciones
1. **Rango de notas:** 0,0 a 5,0 (exactamente una decimal).
2. **Porcentaje de cortes:** Suma exacta = 100%.
3. **Porcentaje de actividades:** Suma ≤ 100% (puede ser menor si no se han agregado todas).
4. **Nombres únicos:** Cada asignatura debe tener nombre único.
5. **Tres cortes obligatorios:** Cada asignatura debe tener exactamente 3 cortes.

### Fórmulas de Cálculo

**Nota del corte:**
```
nota_corte = Σ(nota_actividad × porcentaje_actividad / 100)
```
Solo se incluyen actividades con nota registrada.

**Aporte del corte a la nota final:**
```
aporte_corte = nota_corte × porcentaje_corte / 100
```

**Nota acumulada (parcial):**
```
nota_acumulada = Σ(aporte_corte)
Solo suma los cortes que tienen al menos una actividad calificada.
```

**Porcentaje evaluado:**
```
porcentaje_evaluado = (suma de porcentajes de actividades con nota registrada / suma total de porcentajes) × 100
```

**Nota final:**
Se muestra solo cuando porcentaje_evaluado >= 95% (considerar evaluación prácticamente completa).

**Promedio general:**
```
promedio_general = Σ(nota_acumulada_asignatura) / cantidad_asignaturas
```
Solo incluye asignaturas que tienen al menos una nota registrada.

## Interfaz Esperada (Streamlit)

### Navegación Principal
- **Sidebar con tabs/botones:**
  1. Dashboard
  2. Asignaturas
  3. Cortes y Porcentajes
  4. Actividades y Notas
  5. Configuración

### 1. Dashboard
- **Contenido:**
  - Tarjeta con promedio general (grande, destacado).
  - Grid de tarjetas resumen por asignatura (nombre, nota acumulada, % evaluado, nota final si aplica).
  - Gráfico de barras (Plotly): Asignaturas vs Nota acumulada/final.
  - Indicador visual de progreso por asignatura (barra de progreso).

### 2. Asignaturas
- **Contenido:**
  - Formulario: Input para nombre de nueva asignatura + botón "Crear".
  - Lista/select de asignaturas existentes (permitir seleccionar la actual).
  - Botón para eliminar asignatura (con confirmación).
  - Indicador de asignatura actualmente seleccionada.

### 3. Cortes y Porcentajes
- **Contenido:**
  - Solo visible si hay asignatura seleccionada.
  - Tres columnas/secciones (una por corte).
  - Cada corte: Label, input para porcentaje, mostrar actividades del corte (read-only aquí).
  - Botón "Guardar porcentajes" con validación (suma = 100%).
  - Mostrar advertencia si suma ≠ 100%.

### 4. Actividades y Notas
- **Contenido:**
  - Tabs/secciones (uno por corte).
  - Tabla con: Nombre de actividad, Porcentaje, Nota (editable), Botones (Editar, Eliminar).
  - Formulario para agregar nueva actividad: Input nombre, Input porcentaje, Botón "Agregar".
  - Mostrar suma de porcentajes y validación.
  - Mostrar nota acumulada del corte en tiempo real.

### 5. Configuración
- **Contenido:**
  - Botón para limpiar caché de Streamlit.
  - Botón para exportar datos a CSV (opcional).
  - Información de la versión y fecha de última sincronización.

### Validaciones en UI
- Mensajes de error claros en color rojo.
- Mensajes de éxito en color verde.
- Confirmaciones antes de eliminar asignaturas/actividades.
- Inputs numéricos con validación en tiempo real.
- Deshabilitar botones cuando no hay datos válidos.

## Persistencia (SQLite)

### Archivo de base de datos
- **Ubicación:** `./data/academico.db`
- **Creación automática:** Al iniciar la app, si no existe.

### Operaciones CRUD
- **Asignaturas:** Create, Read, Update, Delete.
- **Cortes:** Create, Read, Update (porcentaje), Delete.
- **Actividades:** Create, Read, Update (nota, porcentaje), Delete.

### Transacciones
- Usar transacciones para garantizar integridad (ej: eliminar asignatura + cortes + actividades).

## Estructura de Archivos

```
Gestor academico de notas/
├── app.py                  # Aplicación principal (Streamlit)
├── database.py             # Módulo de base de datos
├── utils.py                # Funciones utilitarias (cálculos, validaciones)
├── requirements.txt        # Dependencias Python
├── .gitignore              # Archivos a ignorar en Git
├── README.md               # Documentación
├── data/
│   └── academico.db        # Base de datos SQLite (generada automáticamente)
├── assets/                 # (Opcional) Imágenes, estilos
└── arquitectura/           # Documentación de arquitectura (opcional)
```

## Entregables

1. **app.py:** Aplicación Streamlit completa con interfaz según RNF01.
2. **database.py:** Módulo SQLite con operaciones CRUD.
3. **utils.py:** Funciones de cálculo y validación.
4. **requirements.txt:** Dependencias (streamlit, pandas, plotly, etc.).
5. **.gitignore:** Excluir `data/`, `__pycache__`, `.streamlit/`, etc.
6. **README.md:** Instrucciones de instalación y uso.
7. **Commits Git:** Mínimo 5-7 commits mostrando progreso (RF01, RF02-03, RF04-06, RF07-08, RF09-10, RF11-12, testing).

## Criterios de Aceptación

### Pruebas Funcionales
- [ ] **RF01:** Crear 3 asignaturas diferentes, seleccionar una.
- [ ] **RF02-03:** Crear 3 cortes, asignar porcentajes (10%, 30%, 60%), validar suma = 100%.
- [ ] **RF04-05:** Agregar 4 actividades en Corte 1 (20%, 20%, 30%, 30%), validar suma ≤ 100%.
- [ ] **RF06:** Registrar notas (3.5, 4.0, 2.8, 4.5) para las 4 actividades.
- [ ] **RF07:** Verificar nota de Corte 1 = (3.5×0.2 + 4.0×0.2 + 2.8×0.3 + 4.5×0.3) = 3.84.
- [ ] **RF08:** Completar los 3 cortes, verificar nota final visible.
- [ ] **RF09:** Mostrar porcentaje evaluado (ej: 85%).
- [ ] **RF10:** Gráfico de barras muestra las 3 asignaturas con sus notas.
- [ ] **RF11:** Promedio general es correcto.
- [ ] **RF12:** Cerrar y reabrir app, verificar que todos los datos persisten.

### Pruebas No Funcionales
- [ ] **RNF01:** Interfaz clara sin instrucciones extensas.
- [ ] **RNF02:** Campos vacíos y porcentajes inválidos generan errores.
- [ ] **RNF03:** Código en módulos bien definidos.
- [ ] **RNF04:** Base de datos creada automáticamente.
- [ ] **RNF05:** No hay secretos en el código.
- [ ] **RNF06:** `pip install -r requirements.txt` y `streamlit run app.py` funcionan.
- [ ] **RNF07:** Git log muestra commits progresivos.

## Notas Técnicas

1. **Estado de la app:** Usar `st.session_state` para mantener asignatura seleccionada.
2. **Caché:** Usar `@st.cache_data` para consultas de BD que no cambian frecuentemente.
3. **Validación:** Centralizar en `utils.py` para reutilización.
4. **Manejo de errores:** Try-except con mensajes amigables en `st.error()`.
5. **Formato de decimales:** Mostrar siempre con 1-2 decimales (ej: 3.85, no 3.8499999).
6. **Colores Streamlit:** Usar tema por defecto o personalizar en `.streamlit/config.toml`.

---

**Versión:** 1.0
**Fecha:** 31/08/2026
**Estado:** Especificación lista para desarrollo
