# Máquina de Turing (Multicinta) — Análisis de Tiempo + Regresión Polinomial

Este proyecto simula una **Máquina de Turing multicinta** definida por un archivo JSON de transiciones (ej. `Suma.json`) usando el simulador `turing.py`.  
Además incluye un script `analisis.py` que mide **tiempo de ejecución** en función del **tamaño de entrada** y genera un **diagrama de dispersión** con **regresión polinomial** (para ajustar mejor los datos).

## 1. Descripción de las convenciones elegidas

### Modelo de Máquina
El simulador implementa una **Máquina de Turing determinista multicinta**, donde:
- Las transiciones se cargan desde un archivo **JSON**.
- Cada transición tiene la forma: `estado|s1,s2,s3,...`
  - `next`: estado siguiente
  - `write`: símbolos a escribir por cinta
  - `move`: movimiento por cinta (`L`, `R`, `S`)
- Se soporta el comodín `*` en transiciones para:
  - coincidir con cualquier símbolo en la lectura
  - no modificar la celda cuando aparece en `write`

### Alfabeto de trabajo
Símbolos principales:
- `1` → unidad en representación unaria
- `_` → blanco 
- `#` → delimitador o fin de bloque
- `X` → marcador temporal 
- `*` → comodín en transiciones

### Organización modular
El cálculo de Fibonacci se construye mediante módulos independientes:
- **Suma** → concatena bloques unarios.
- **Decremento** → reduce en una unidad un número unario.
- **Copia** → transfiere contenido entre cintas.

Esto permite estructurar la máquina principal como una secuencia de macro-estados que combinan estos módulos para implementar iterativamente:
F(n) = F(n-1) + F(n-2)


---

## Estructura del proyecto

- `turing.py`  
  Simulador de Máquina de Turing multicinta (carga JSON, ejecuta transiciones).
- `Suma.json`  
  Definición del módulo de suma unaria con marcador `X`.
- `analisis.py`  
  Script de análisis experimental:
  - mide **tiempo de ejecución** por tamaño de entrada
  - corre múltiples repeticiones por punto (`runs`)
  - usa calentamiento (`warmup`)
  - genera `CSV` con resultados
  - genera `PNG` con el scatter + regresión polinomial (grado 2 recomendado)

---

## Requisitos

- Python 3.x
- Dependencias:
  - `matplotlib`
  - `numpy`

Instalación rápida:

```bash
pip install matplotlib numpy


## Ejecución de análisis
python analisis.py --json Suma.json --m_max <MAX> --k <k1 k2 ...> --runs <N> --warmup <W>

## Ejemplos
python analisis.py --json Suma.json --m_max 20 --k 0 --runs 10 --warmup 2

python analisis.py --json Suma.json --m_max 40 --k 0 5 10 --runs 20 --warmup 3

python analisis.py --json Suma.json --m_max 60 --k 0 5 10 --runs 25 --warmup 5

python analisis.py --json Suma.json --m_max 100 --k 0 5 10 20 --runs 25 --warmup 5

python analisis.py --json Suma.json --m_max 100 --k 0 --runs 25 --warmup 5

python analisis.py --json Suma.json --m_max 100 --k 20 --runs 25 --warmup 5 --max_steps 2000000