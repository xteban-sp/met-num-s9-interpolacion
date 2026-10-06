# Interpolación de Newton · Sesión 9

Aplicativo que automatiza la interpolación polinomial de Newton por diferencias divididas, en web y en Python.

Universidad Peruana Unión · Ingeniería de Sistemas · Fernando Istaña Flores
Curso: Análisis Numérico / Métodos Numéricos

---

## Qué hay aquí

| Archivo | Contenido |
|---|---|
| `index.html` | La app web. Un solo archivo, sin dependencias: se abre con doble clic o desde GitHub Pages |
| `python/newton.py` | `diferencias_divididas(X, Y)`, evaluación anidada, forma estándar y gráfica con matplotlib |
| `python/salida_newton.txt` | La salida del programa, para pegarla en el informe |
| `python/interpolacion_s9.png` | La gráfica generada |
| `informes/` | El informe de la GAA de la Sesión 9 en Word y en PDF |

## La app web

- **Nodos editables** (2 a 8 puntos) y punto `x` a evaluar: todo se recalcula al tipear.
- **Tabla de diferencias divididas** con la primera fila (los coeficientes) resaltada, y el cálculo de
  cada casilla: `f[1, 2, 4] = (45/2 − 20) / (4 − 1) = 5/6`. En fracciones exactas cuando los datos son enteros.
- **Polinomio** en forma de Newton y en forma estándar, exacto y en decimales.
- **Pasos del reemplazo numérico**: cada término con su producto `(x − x_j)` y la suma acumulada.
- **Evaluación anidada** `P(x) = c₀ + (x − x₀)(c₁ + (x − x₁)(c₂ + …))`, que es la que usa el programa.
- **Gráfica**: curva de `P_n(x)`, los puntos medidos y el punto interpolado resaltado, con crosshair,
  tooltip y un deslizador para recorrer la curva.
- **Grado por grado**: botones para ver `P₁`, `P₂`, … sobre la gráfica y una tabla con el valor
  interpolado en cada grado. Subir de grado es sumar un término; la tabla no se rehace.
- **Verificación en los nodos** y **aviso de extrapolación** si el punto cae fuera del rango medido.

## Ejecutar la versión en Python

```bash
python python/newton.py
```

Solo necesita `matplotlib` para la gráfica; el resto es biblioteca estándar (`fractions`).

## Caso resuelto — latencia vs. carga concurrente

Cuatro mediciones del equipo de SRE sobre una API REST:

| x (× 100 req/s) | 1 | 2 | 4 | 7 |
|---|---|---|---|---|
| y (ms) | 45 | 65 | 110 | 220 |

Tabla de diferencias divididas (los coeficientes son la primera fila):

| i | x | f[x] | 1.ª | 2.ª | 3.ª |
|---|---|---|---|---|---|
| 0 | 1 | **45** | **20** | **5/6** | **1/3** |
| 1 | 2 | 65 | 45/2 | 17/6 | |
| 2 | 4 | 110 | 110/3 | | |
| 3 | 7 | 220 | | | |

```
P3(x) = 45 + 20(x - 1) + (5/6)(x - 1)(x - 2) + (1/3)(x - 1)(x - 2)(x - 4)
P3(x) = 1/3·x^3 - 3/2·x^2 + 133/6·x + 24
P3(5) = 139 ms
```

Grado por grado en x = 5: P₁ = 125, P₂ = 135, P₃ = 139 ms. La pendiente entre mediciones pasa de 20 a
22.5 y a 36.67 ms por cada 100 req/s: la API se degrada cada vez más rápido al subir la carga.
