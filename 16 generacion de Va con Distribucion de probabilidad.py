
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import kstest

# ============================================================
# 1. CONFIGURACIÓN GENERAL
# ============================================================

np.random.seed(42)

N = 100
ALPHA = 0.05

print("=" * 70)
print(" GENERACIÓN DE VARIABLES ALEATORIAS - TRANSFORMADA INVERSA")
print("=" * 70)
print(f"Número de muestras: {N}")
print(f"Nivel de significancia: {ALPHA}")
print("Método: Transformada inversa\n")


# ============================================================
# 2. DEFINICIÓN DE LAS DISTRIBUCIONES
# ============================================================

def cdf_a(x):
    return np.where(
        x < -2, 0,
        np.where(x <= 2, ((x + 1)**3 + 1) / 28, 1)
    )

def pdf_a(x):
    return np.where((x >= -2) & (x <= 2),
                    3 * (x + 1)**2 / 28, 0)


def cdf_b(x):
    return np.where(
        x < 9, 0,
        np.where(x <= 12, ((x - 9) / 3)**2, 1)
    )

def pdf_b(x):
    return np.where((x >= 9) & (x <= 12),
                    2 * (x - 9) / 9, 0)


def cdf_c(x):
    return np.where(
        x < 5, 0,
        np.where(x <= 8, 1 - ((8 - x) / 3)**2, 1)
    )

def pdf_c(x):
    return np.where((x >= 5) & (x <= 8),
                    2 * (8 - x) / 9, 0)


def cdf_d(x):
    return np.where(
        x < 11, 0,
        np.where(x <= 15, 1 - ((15 - x) / 4)**2, 1)
    )

def pdf_d(x):
    return np.where((x >= 11) & (x <= 15),
                    (15 - x) / 8, 0)


# ============================================================
# 3. GENERACIÓN DE VARIABLES ALEATORIAS
# ============================================================

R_a = np.random.uniform(0, 1, N)
R_b = np.random.uniform(0, 1, N)
R_c = np.random.uniform(0, 1, N)
R_d = np.random.uniform(0, 1, N)

# Transformada inversa
x_a = np.cbrt(28 * R_a - 1) - 1
x_b = 9 + 3 * np.sqrt(R_b)
x_c = 8 - 3 * np.sqrt(1 - R_c)
x_d = 15 - 4 * np.sqrt(1 - R_d)


# ============================================================
# 4. DATOS TEÓRICOS
# ============================================================

distribuciones = {
    "Inciso A": {
        "x": x_a,
        "R": R_a,
        "intervalo": (-2, 2),
        "media": 0.0,
        "varianza": 1.0,
        "cdf": cdf_a,
        "pdf": pdf_a,
        "formula": "cbrt(28R - 1) - 1"
    },
    "Inciso B": {
        "x": x_b,
        "R": R_b,
        "intervalo": (9, 12),
        "media": 11.0,
        "varianza": 0.5,
        "cdf": cdf_b,
        "pdf": pdf_b,
        "formula": "9 + 3*sqrt(R)"
    },
    "Inciso C": {
        "x": x_c,
        "R": R_c,
        "intervalo": (5, 8),
        "media": 6.0,
        "varianza": 0.5,
        "cdf": cdf_c,
        "pdf": pdf_c,
        "formula": "8 - 3*sqrt(1-R)"
    },
    "Inciso D": {
        "x": x_d,
        "R": R_d,
        "intervalo": (11, 15),
        "media": 37/3,
        "varianza": 8/9,
        "cdf": cdf_d,
        "pdf": pdf_d,
        "formula": "15 - 4*sqrt(1-R)"
    }
}


# ============================================================
# 5. ANÁLISIS ESTADÍSTICO
# ============================================================

print("\n" + "=" * 70)
print(" RESULTADOS ESTADÍSTICOS")
print("=" * 70)

for nombre, datos in distribuciones.items():

    x = datos["x"]
    minimo, maximo = datos["intervalo"]

    media_exp = np.mean(x)
    varianza_exp = np.var(x, ddof=1)
    desviacion = np.std(x, ddof=1)
    mediana = np.median(x)

    media_teo = datos["media"]
    error = abs(media_exp - media_teo)

    # Prueba de Kolmogorov-Smirnov
    resultado_ks = kstest(x, datos["cdf"])
    D = resultado_ks.statistic
    p_valor = resultado_ks.pvalue

    # Verificación de límites
    dentro_intervalo = np.all(
        (x >= minimo) & (x <= maximo)
    )

    print(f"\n--- {nombre} ---")
    print(f"Fórmula: {datos['formula']}")

    print("Primeros 10 valores:")
    print(np.round(x[:10], 4))

    print(f"\nMínimo experimental:       {np.min(x):.4f}")
    print(f"Máximo experimental:       {np.max(x):.4f}")
    print(f"Media experimental:        {media_exp:.4f}")
    print(f"Media teórica:             {media_teo:.4f}")
    print(f"Mediana:                   {mediana:.4f}")
    print(f"Varianza experimental:     {varianza_exp:.4f}")
    print(f"Desviación estándar:       {desviacion:.4f}")
    print(f"Error absoluto de la media:{error:.4f}")

    print(f"\nValores dentro del intervalo: {dentro_intervalo}")
    print(f"Prueba Kolmogorov-Smirnov D:  {D:.4f}")
    print(f"Valor p:                      {p_valor:.4f}")

    if p_valor > ALPHA:
        print("Conclusión KS: No se rechaza H0.")
    else:
        print("Conclusión KS: Se rechaza H0.")


# ============================================================
# 6. TABLA COMPARATIVA
# ============================================================

print("\n" + "=" * 90)
print(" TABLA RESUMEN COMPARATIVA")
print("=" * 90)

print(
    f"{'Inciso':<12}"
    f"{'Media Exp.':<14}"
    f"{'Media Teo.':<14}"
    f"{'Varianza':<14}"
    f"{'Desv. Est.':<14}"
    f"{'Error Media':<14}"
)

for nombre, datos in distribuciones.items():

    x = datos["x"]

    print(
        f"{nombre:<12}"
        f"{np.mean(x):<14.4f}"
        f"{datos['media']:<14.4f}"
        f"{np.var(x, ddof=1):<14.4f}"
        f"{np.std(x, ddof=1):<14.4f}"
        f"{abs(np.mean(x)-datos['media']):<14.4f}"
    )


# ============================================================
# 7. GRÁFICAS: HISTOGRAMA Y DENSIDAD TEÓRICA
# ============================================================

fig, axes = plt.subplots(2, 2, figsize=(13, 9))

for ax, (nombre, datos) in zip(axes.flat, distribuciones.items()):

    x = datos["x"]
    minimo, maximo = datos["intervalo"]

    valores = np.linspace(minimo, maximo, 300)

    ax.hist(
        x,
        bins=12,
        density=True,
        alpha=0.6,
        edgecolor="black",
        label="Histograma experimental"
    )

    ax.plot(
        valores,
        datos["pdf"](valores),
        linewidth=2,
        label="Densidad teórica"
    )

    ax.set_title(nombre)
    ax.set_xlabel("Valores de X")
    ax.set_ylabel("Densidad")
    ax.legend()
    ax.grid(alpha=0.3)

plt.suptitle(
    "Comparación de distribuciones experimentales y teóricas",
    fontsize=14
)

plt.tight_layout()
plt.show()


# ============================================================
# 8. GRÁFICAS: FUNCIÓN DE DISTRIBUCIÓN ACUMULADA
# ============================================================

fig, axes = plt.subplots(2, 2, figsize=(13, 9))

for ax, (nombre, datos) in zip(axes.flat, distribuciones.items()):

    x = np.sort(datos["x"])
    minimo, maximo = datos["intervalo"]

    # Función de distribución empírica
    F_empirica = np.arange(1, N + 1) / N

    valores = np.linspace(minimo, maximo, 300)

    ax.step(
        x,
        F_empirica,
        where="post",
        label="Distribución empírica"
    )

    ax.plot(
        valores,
        datos["cdf"](valores),
        linewidth=2,
        label="Distribución teórica"
    )

    ax.set_title(nombre)
    ax.set_xlabel("Valores de X")
    ax.set_ylabel("F(x)")
    ax.legend()
    ax.grid(alpha=0.3)

plt.suptitle(
    "Comparación de funciones de distribución acumulada",
    fontsize=14
)

plt.tight_layout()
plt.show()


# ============================================================
# 9. VERIFICACIÓN DE LOS NÚMEROS UNIFORMES
# ============================================================

print("\n" + "=" * 70)
print(" VERIFICACIÓN DE LOS NÚMEROS ALEATORIOS UNIFORMES")
print("=" * 70)

for nombre, R in [
    ("A", R_a),
    ("B", R_b),
    ("C", R_c),
    ("D", R_d)
]:
    print(
        f"Inciso {nombre}: "
        f"mínimo R={np.min(R):.4f}, "
        f"máximo R={np.max(R):.4f}, "
        f"media R={np.mean(R):.4f}"
    )

print("\nPROCESO FINALIZADO CORRECTAMENTE.")

