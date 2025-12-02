# Sistema de Adivinanza de Personajes con Machine Learning

## Descripción General

Este proyecto implementa un sistema inteligente de adivinanza de personajes que utiliza algoritmos de teoría de información para optimizar el proceso de identificación. El sistema emplea conceptos de entropía de Shannon y ganancia de información para seleccionar las preguntas más efectivas, reduciendo progresivamente el espacio de búsqueda hasta identificar el personaje correcto.

## Características Técnicas

### Funcionalidades Principales

- **Motor de Machine Learning**: Implementación de algoritmos basados en teoría de información (entropía y ganancia de información) para la selección óptima de preguntas
- **Persistencia Dual**: Sistema de almacenamiento que combina SQLite para consultas relacionales y JSON para intercambio de datos
- **Sistema de Estadísticas**: Registro completo de partidas, métricas de rendimiento y análisis de patrones de uso
- **Aprendizaje Incremental**: Capacidad de agregar nuevos personajes dinámicamente durante la ejecución
- **Sincronización Automática**: Mantenimiento de consistencia entre las bases de datos SQLite y JSON
- **Interfaz Binaria**: Sistema simplificado de preguntas con respuestas sí/no
- **Auditoría Completa**: Registro detallado de todas las preguntas, respuestas y decisiones del sistema

## Arquitectura del Sistema

### Diseño Modular

El proyecto sigue los principios de diseño SOLID y utiliza una arquitectura modular de tres capas:

```
┌─────────────────────────────────────────────┐
│           GameController                    │
│         (Capa de Presentación)              │
└────────────┬──────────────┬─────────────────┘
             │              │
    ┌────────▼──────┐  ┌───▼──────────────┐
    │  ML Module    │  │  Persistence     │
    │  (Lógica)     │  │  (Datos)         │
    └───────────────┘  └──────────────────┘
```

### Componentes del Sistema

#### Capa de Presentación
- **main.py**: Punto de entrada de la aplicación
- **game_controller.py**: Controlador principal que orquesta la interacción entre componentes

#### Capa de Lógica de Negocio
- **ml/predictor.py**: Motor de predicción que implementa algoritmos de teoría de información
- **ml/game_session.py**: Gestor de sesiones de juego individuales

#### Capa de Persistencia
- **persistence/database.py**: Gestor de base de datos con soporte dual SQLite/JSON

## Requisitos del Sistema

### Requisitos de Software

- Python 3.8 o superior
- SQLite3 (incluido en Python estándar)
- Bibliotecas estándar de Python (sin dependencias externas)

### Requisitos de Hardware

- Memoria RAM: 512 MB mínimo
- Espacio en disco: 10 MB mínimo
- Procesador: Cualquier procesador moderno

## Instalación

### Proceso de Instalación

1. Clonar el repositorio:
   ```bash
   git clone <url-del-repositorio>
   cd Python_ProgramacionAvanzada
   ```

2. Verificar la estructura de directorios:
   ```bash
   tree -L 2
   ```

3. Ejecutar el programa:
   ```bash
   python3 main.py
   ```

### Verificación de Instalación

El sistema creará automáticamente las estructuras necesarias:
- `database/personajes.db` - Base de datos SQLite
- `data/personajes.json` - Archivo JSON de personajes

## Manual de Usuario

### Inicio del Sistema

Para iniciar el sistema, ejecutar:

```bash
python3 main.py
```

### Menú Principal

El sistema presenta cuatro opciones principales:

1. **Jugar**: Iniciar una nueva partida de adivinanza
2. **Ver estadísticas**: Consultar métricas de rendimiento del sistema
3. **Listar personajes**: Ver todos los personajes en la base de datos
4. **Salir**: Cerrar la aplicación

### Proceso de Juego

#### Iniciar Partida

1. Seleccionar opción `1` en el menú principal
2. Pensar en un personaje de la base de datos
3. Responder las preguntas del sistema

#### Formato de Respuestas

El sistema acepta los siguientes formatos de respuesta:

- **Respuesta afirmativa**: `s`, `si`, `sí`, `1`
- **Respuesta negativa**: `n`, `no`, `0`

#### Proceso de Adivinanza

El sistema seguirá este flujo:

1. Formular pregunta basada en ganancia de información
2. Procesar respuesta del usuario
3. Filtrar candidatos según la respuesta
4. Repetir hasta alcanzar confianza suficiente (70% o 1 candidato)
5. Intentar adivinanza (máximo 3 intentos)

### Agregar Nuevos Personajes

Cuando el sistema alcanza el límite de 3 intentos fallidos:

1. El sistema solicita el nombre del personaje pensado
2. Verifica si existe en la base de datos:
   - **Si existe**: Registra la partida como fallida
   - **Si no existe**: Ofrece agregarlo al sistema
3. Si se acepta agregar:
   - Solicita todas las características del personaje
   - Almacena en SQLite
   - Sincroniza con JSON
   - Recarga el predictor

## Estructura del Proyecto

```
Python_ProgramacionAvanzada/
│
├── main.py                      # Punto de entrada del sistema
├── game_controller.py           # Controlador principal
├── README.md                    # Documentación del proyecto
│
├── ml/                          # Módulo de Machine Learning
│   ├── __init__.py
│   ├── predictor.py            # Algoritmos de teoría de información
│   └── game_session.py         # Gestión de sesiones
│
├── persistence/                 # Módulo de persistencia
│   ├── __init__.py
│   └── database.py             # Gestión SQLite y JSON
│
├── data/                        # Directorio de datos
│   └── personajes.json         # Base de datos JSON
│
└── database/                    # Directorio de base de datos
    └── personajes.db           # Base de datos SQLite
```

## Fundamentos Teóricos

### Teoría de Información

El sistema implementa conceptos fundamentales de teoría de información desarrollados por Claude Shannon.

#### Entropía de Shannon

La entropía mide la cantidad de incertidumbre en un conjunto de datos:

```
H(S) = -Σ p(xᵢ) * log₂(p(xᵢ))
```

Donde:
- `H(S)` es la entropía del conjunto S
- `p(xᵢ)` es la probabilidad del elemento i
- La suma se realiza sobre todos los elementos únicos

**Interpretación:**
- Entropía alta: Mayor incertidumbre, muchos candidatos equiprobables
- Entropía baja: Menor incertidumbre, pocos candidatos o distribución sesgada

#### Ganancia de Información

La ganancia de información cuantifica la reducción de entropía al particionar el conjunto:

```
IG(S, A) = H(S) - Σ (|Sᵥ|/|S|) * H(Sᵥ)
```

Donde:
- `IG(S, A)` es la ganancia de información del atributo A
- `S` es el conjunto actual de candidatos
- `Sᵥ` es el subconjunto con valor v para el atributo A
- `|S|` denota la cardinalidad del conjunto

**Proceso de Selección:**

1. Para cada pregunta posible, calcular ganancia de información
2. Seleccionar la pregunta con mayor ganancia
3. Aplicar la pregunta y particionar el espacio de búsqueda
4. Iterar hasta alcanzar criterio de parada

### Algoritmo de Predicción

```python
function SELECCIONAR_PREGUNTA(candidatos, preguntas_realizadas):
    mejor_ganancia = -∞
    mejor_pregunta = None

    for cada (característica, valor) not in preguntas_realizadas:
        ganancia = CALCULAR_GANANCIA(candidatos, característica, valor)
        if ganancia > mejor_ganancia:
            mejor_ganancia = ganancia
            mejor_pregunta = (característica, valor)

    return mejor_pregunta

function CALCULAR_GANANCIA(candidatos, característica, valor):
    entropia_inicial = CALCULAR_ENTROPIA(candidatos)

    grupo_si = FILTRAR(candidatos, característica == valor)
    grupo_no = FILTRAR(candidatos, característica != valor)

    peso_si = |grupo_si| / |candidatos|
    peso_no = |grupo_no| / |candidatos|

    entropia_ponderada = peso_si * CALCULAR_ENTROPIA(grupo_si) +
                         peso_no * CALCULAR_ENTROPIA(grupo_no)

    return entropia_inicial - entropia_ponderada
```

## Modelo de Datos

### Base de Datos SQLite

#### Tabla: personajes

```sql
CREATE TABLE personajes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    caracteristicas TEXT NOT NULL,      -- Almacenado como JSON
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabla: partidas

```sql
CREATE TABLE partidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    personaje_objetivo_id INTEGER NOT NULL,
    adivinado BOOLEAN NOT NULL,
    intentos INTEGER NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (personaje_objetivo_id) REFERENCES personajes(id)
);
```

#### Tabla: partida_preguntas

```sql
CREATE TABLE partida_preguntas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    partida_id INTEGER NOT NULL,
    caracteristica TEXT NOT NULL,
    valor_esperado TEXT NOT NULL,
    valor_usuario TEXT NOT NULL,
    orden INTEGER NOT NULL,
    FOREIGN KEY (partida_id) REFERENCES partidas(id)
);
```

### Formato JSON

```json
{
  "personajes": [
    {
      "id": 1,
      "nombre": "Nombre del Personaje",
      "caracteristicas": {
        "color_pelo": "valor",
        "color_ojos": "valor",
        "origen": "valor",
        "personalidad": "valor"
      }
    }
  ],
  "metadata": {
    "version": "1.0",
    "fecha_exportacion": "2024-12-02T10:00:00",
    "total_personajes": 20
  }
}
```

### Sincronización de Datos

El sistema mantiene sincronización bidireccional entre SQLite y JSON:

**SQLite → JSON:**
```python
db.exportar_a_json("data/personajes.json")
```

**JSON → SQLite:**
```python
db.importar_desde_json("data/personajes.json")
```

**Recarga del Predictor:**
```python
predictor.cargar_datos()  # Lee desde JSON
```

## Métricas y Estadísticas

El sistema calcula y almacena las siguientes métricas:

- **Total de partidas**: Número total de juegos realizados
- **Partidas ganadas**: Número de adivinanzas correctas
- **Tasa de éxito**: Porcentaje de partidas ganadas
- **Promedio de intentos**: Número medio de intentos por partida
- **Personaje más jugado**: Personaje más frecuente en el historial

### Consulta de Estadísticas

```python
stats = db.obtener_estadisticas()

print(f"Total de partidas: {stats['total_partidas']}")
print(f"Tasa de éxito: {stats['tasa_exito']:.2f}%")
print(f"Promedio de intentos: {stats['promedio_intentos']}")
```

## Consideraciones Técnicas

### Principios de Diseño

**SOLID Principles:**

1. **Single Responsibility Principle**: Cada clase tiene una única responsabilidad bien definida
2. **Open/Closed Principle**: El sistema es extensible (nuevas características) sin modificar código existente
3. **Dependency Inversion**: Las dependencias se inyectan en los constructores

**Patrones de Diseño:**

- **MVC (Model-View-Controller)**: Separación entre lógica, presentación y datos
- **Repository Pattern**: Abstracción de acceso a datos en `DatabaseManager`
- **Strategy Pattern**: Algoritmos de selección de preguntas intercambiables

### Manejo de Errores

El sistema implementa manejo robusto de errores:

1. **Validación de entrada**: Todas las entradas del usuario son validadas
2. **Valores None**: Manejo explícito de características faltantes
3. **Caracteres especiales**: Escape de caracteres en consultas SQL
4. **Sincronización**: Verificación de consistencia entre SQLite y JSON

### Seguridad

**Medidas de Seguridad Implementadas:**

- Validación con expresiones regulares para nombres de características
- Uso de parámetros preparados en consultas SQL (prevención de SQL injection)
- Manejo seguro de valores nulos y características faltantes
- Validación de tipos de datos antes de operaciones críticas

### Rendimiento

**Optimizaciones Implementadas:**

- Uso de `json_extract` de SQLite para búsquedas eficientes
- Cálculo incremental de entropía
- Índices en campos de búsqueda frecuente
- Caché de características disponibles

## Pruebas

### Archivos de Prueba

- `test_database.py`: Pruebas unitarias para el módulo de persistencia
- `test_ml.py`: Pruebas para algoritmos de Machine Learning
- `test_ml_binario.py`: Pruebas específicas para preguntas binarias

### Ejecutar Pruebas

```bash
python3 -m pytest test_database.py
python3 -m pytest test_ml.py
python3 -m pytest test_ml_binario.py
```

## Limitaciones Conocidas

1. El sistema asume que todas las características son categóricas (no numéricas)
2. No hay soporte para características con múltiples valores
3. La interfaz es únicamente por línea de comandos
4. No hay sistema de autenticación o múltiples usuarios

## Trabajo Futuro

### Mejoras Propuestas

- Implementación de interfaz gráfica (GUI)
- Soporte para características numéricas con rangos
- Sistema de pesos para características más discriminatorias
- Modo de entrenamiento con aprendizaje supervisado
- API REST para acceso remoto
- Soporte para múltiples idiomas

## Referencias

1. Shannon, C. E. (1948). "A Mathematical Theory of Communication". Bell System Technical Journal.
2. Quinlan, J. R. (1986). "Induction of Decision Trees". Machine Learning, 1(1), 81-106.
3. Mitchell, T. M. (1997). "Machine Learning". McGraw-Hill.

## Licencia

Este proyecto ha sido desarrollado con fines académicos como parte del curso de Programación Avanzada en Python.

## Información de Contacto

Para reportar problemas o sugerencias, consultar con el instructor del curso o abrir un issue en el repositorio del proyecto.

---

**Última actualización**: Diciembre 2024
**Versión**: 1.0.0
