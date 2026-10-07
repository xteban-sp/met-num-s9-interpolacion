"""
Análisis Numérico · Unidad 2 · Sesión 9
Interpolación polinomial de Newton — latencia media de una API REST según la carga concurrente.

Datos de las pruebas del equipo de SRE:
    x (x 100 req/s) :   1     2     4     7
    y (ms)          :  45    65   110   220

Objetivo: estimar la latencia cuando el sistema opera a 500 req/s (x = 5).

Fernando Istaña Flores · Universidad Peruana Unión
"""

from fractions import Fraction


# --------------------------------------------------------------------------
# Construcción de la matriz: tabla completa de diferencias divididas
# --------------------------------------------------------------------------
def diferencias_divididas(X, Y):
    """
    Devuelve la matriz triangular n x n con la tabla completa.

        T[i][j] = f[x_i, x_{i+1}, ..., x_{i+j}]
        T[i][j] = (T[i+1][j-1] - T[i][j-1]) / (x_{i+j} - x_i)

    La columna 0 son los valores de f y la PRIMERA FILA son los coeficientes
    del polinomio de Newton. Debajo de la antidiagonal la matriz queda en cero.
    """
    n = len(X)
    if len(Y) != n:
        raise ValueError("X e Y deben tener el mismo tamaño.")
    if len(set(X)) != n:
        raise ValueError("Hay nodos repetidos: se dividiría entre cero.")
    T = [[0] * n for _ in range(n)]
    for i in range(n):
        T[i][0] = Y[i]
    for j in range(1, n):                 # columna = orden de la diferencia
        for i in range(n - j):            # fila
            T[i][j] = (T[i + 1][j - 1] - T[i][j - 1]) / (X[i + j] - X[i])
    return T


# --------------------------------------------------------------------------
# Evaluación eficiente: multiplicación anidada (el Horner de la forma de Newton)
# --------------------------------------------------------------------------
def evaluar_newton(coefs, X, x):
    """
    P(x) = c0 + (x - x0)·(c1 + (x - x1)·(c2 + ... + (x - x_{n-1})·cn))

    Se recorre de adentro hacia afuera: n multiplicaciones y n sumas.
    Evaluar término por término costaría del orden de n^2 / 2 multiplicaciones.
    """
    p = coefs[-1]
    for k in range(len(coefs) - 2, -1, -1):
        p = coefs[k] + (x - X[k]) * p
    return p


# --------------------------------------------------------------------------
# Forma estándar a_n x^n + ... + a_1 x + a_0
# --------------------------------------------------------------------------
def forma_estandar(coefs, X):
    """Desarrolla la forma de Newton y devuelve [a_n, ..., a_1, a_0]."""
    p = [coefs[-1]]
    for k in range(len(coefs) - 2, -1, -1):
        nuevo = p + [0]                   # p(x) · x
        for i, a in enumerate(p):
            nuevo[i + 1] -= X[k] * a      # - x_k · p(x)
        nuevo[-1] += coefs[k]             # + c_k
        p = nuevo
    return p


def newton_texto(coefs, X):
    partes = []
    for k, c in enumerate(coefs):
        if c == 0:
            continue
        factores = "".join("(x %s %s)" % ("-" if X[j] >= 0 else "+", abs(X[j])) for j in range(k))
        val = "%s" % abs(c)
        if "/" in val and factores:
            val = "(" + val + ")"
        signo = " + " if c > 0 and partes else (" - " if c < 0 and partes else ("-" if c < 0 else ""))
        partes.append(signo + val + factores)
    return "".join(partes)


def polinomio_texto(coef):
    grados = len(coef) - 1
    partes = []
    for j, c in enumerate(coef):
        g = grados - j
        if c == 0:
            continue
        signo = " + " if c > 0 and partes else (" - " if c < 0 and partes else ("-" if c < 0 else ""))
        val = abs(c)
        term = "%s" % val if g == 0 else ("%s·x" % val if g == 1 else "%s·x^%d" % (val, g))
        partes.append(signo + term)
    return "".join(partes)


if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # Entrada de datos: dos arreglos del mismo tamaño
    # ----------------------------------------------------------------------
    X = [1, 2, 4, 7]             # vector de cargas (x 100 req/s)
    Y = [45, 65, 110, 220]       # vector de latencias (ms)
    x_eval = 5                   # 500 req/s
    n = len(X) - 1

    print("=" * 74)
    print("DATOS EXPERIMENTALES")
    print("=" * 74)
    print("   i   x_i (x100 req/s)     y_i (ms)")
    for i, (a, b) in enumerate(zip(X, Y)):
        print("  %2d   %12.2f   %12.2f" % (i, a, b))

    # con fracciones la tabla sale exacta (5/6 en lugar de 0.8333...)
    Xf = [Fraction(v) for v in X]
    Yf = [Fraction(v) for v in Y]
    T = diferencias_divididas(Xf, Yf)
    coefs = T[0]

    print()
    print("=" * 74)
    print("TABLA DE DIFERENCIAS DIVIDIDAS (matriz triangular)")
    print("=" * 74)
    cab = ["i", "x_i", "f[x_i]"] + ["%d.a dif." % j for j in range(1, len(X))]
    print("  " + "".join("%11s" % c for c in cab))
    for i in range(len(X)):
        fila = [str(i), str(Xf[i])] + [str(T[i][j]) for j in range(len(X) - i)]
        print("  " + "".join("%11s" % c for c in fila))
    print()
    print("  En decimales:")
    Td = diferencias_divididas(X, [float(v) for v in Y])
    for i in range(len(X)):
        fila = [str(i), "%g" % X[i]] + ["%.4f" % Td[i][j] for j in range(len(X) - i)]
        print("  " + "".join("%11s" % c for c in fila))
    print()
    print("  Coeficientes (primera fila): " + ", ".join(str(c) for c in coefs))

    print()
    print("=" * 74)
    print("POLINOMIO INTERPOLADOR")
    print("=" * 74)
    est = forma_estandar(coefs, Xf)
    print("  Forma de Newton : P%d(x) = %s" % (n, newton_texto(coefs, Xf)))
    print("  Forma estándar  : P%d(x) = %s" % (n, polinomio_texto(est)))
    print("  coeficientes decimales: " + ", ".join("%+.6f" % float(c) for c in est))

    print()
    print("=" * 74)
    print("EVALUACIÓN ANIDADA EN x = %g" % x_eval)
    print("=" * 74)
    b = coefs[-1]
    print("  b%d = c%d = %s" % (n, n, b))
    for k in range(n - 1, -1, -1):
        nuevo = coefs[k] + (x_eval - Xf[k]) * b
        print("  b%d = c%d + (x - x%d)·b%d = %s + (%s)·(%s) = %s"
              % (k, k, k, k + 1, coefs[k], x_eval - Xf[k], b, nuevo))
        b = nuevo

    print()
    print("=" * 74)
    print("RESULTADO")
    print("=" * 74)
    p = evaluar_newton(coefs, Xf, x_eval)
    print("  P%d(%g) = %.4f ms" % (n, x_eval, float(p)))
    print()
    print("  Grado por grado (cada uno agrega un término al anterior):")
    for g in range(1, n + 1):
        print("    P%d(%g) = %9.4f ms   con los nodos x = %s"
              % (g, x_eval, float(evaluar_newton(coefs[:g + 1], Xf, x_eval)), X[:g + 1]))
    print()
    print("  Verificación en los nodos:")
    for a, c in zip(X, Y):
        v = float(evaluar_newton(coefs, Xf, a))
        print("    P%d(%2g) = %8.4f   (dato: %g)   error = %.2e" % (n, a, v, c, abs(v - c)))

    # ----------------------------------------------------------------------
    # Gráfica: los 4 puntos, las curvas de grado 1, 2 y 3 y el punto x = 5
    # ----------------------------------------------------------------------
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        cf = [float(c) for c in coefs]
        malla = [X[0] + i * (X[-1] - X[0]) / 400 for i in range(401)]
        pv = float(p)

        fig, ax = plt.subplots(figsize=(7.4, 4.3), dpi=200)
        ax.plot(malla, [evaluar_newton(cf[:2], X, t) for t in malla], color="#8a97ad", linewidth=1.1,
                linestyle="--", label="P₁(x) · 2 puntos", zorder=1)
        ax.plot(malla, [evaluar_newton(cf[:3], X, t) for t in malla], color="#5b7fb8", linewidth=1.2,
                linestyle="-.", label="P₂(x) · 3 puntos", zorder=1)
        curva = [evaluar_newton(cf, X, t) for t in malla]
        ax.plot(malla, curva, color="#14366b", linewidth=2, label="P₃(x) interpolante", zorder=2)
        ax.scatter(X, Y, s=48, color="#101c33", zorder=3, label="puntos medidos")
        ax.scatter([x_eval], [pv], s=90, color="#c8890a", zorder=4,
                   edgecolor="white", linewidth=1.4, label="P₃(5) = %.2f ms" % pv)
        ax.vlines(x_eval, min(curva) - 12, pv, color="#c8890a", linestyle=":", linewidth=1.2, zorder=1)
        ax.annotate("500 req/s → %.2f ms" % pv, (x_eval, pv), textcoords="offset points",
                    xytext=(-104, 12), color="#8a6a12", fontsize=9)
        for a, c in zip(X, Y):
            ax.annotate("(%g, %g)" % (a, c), (a, c), textcoords="offset points",
                        xytext=(8, -13), color="#3c4a63", fontsize=8)
        ax.set_xlabel("Carga concurrente x (× 100 req/s)")
        ax.set_ylabel("Latencia media y (ms)")
        ax.set_title("Interpolación de Newton de la latencia frente a la carga")
        ax.grid(color="#dfe5ef", linewidth=0.8)
        ax.set_axisbelow(True)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
        ax.legend(frameon=False, fontsize=9)
        fig.tight_layout()
        fig.savefig("interpolacion_s9.png")
        print()
        print("  Gráfica guardada en interpolacion_s9.png")
    except ImportError:
        print()
        print("  (matplotlib no está instalado: se omitió la gráfica)")
