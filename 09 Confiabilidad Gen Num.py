
import numpy as np
import pandas as pd
from scipy import stats

# =====================================================
# CONFIGURACIÓN GENERAL
# =====================================================

np.random.seed(42)

N = 100
ALPHA = 0.05

# Generar números pseudoaleatorios
numeros = np.random.random(N)

print("=" * 65)
print(" GENERACIÓN Y PRUEBAS ESTADÍSTICAS DE NÚMEROS ALEATORIOS")
print("=" * 65)

# Mostrar los 100 números generados
print("\n1. NÚMEROS PSEUDOALEATORIOS GENERADOS:\n")

for i, numero in enumerate(numeros, start=1):
    print(f"Número {i:03d}: {numero:.6f}")

# =====================================================
# A. PRUEBA DE MEDIAS
# =====================================================

print("\n" + "=" * 65)
print("2. PRUEBA DE MEDIAS")
print("=" * 65)

media_teorica = 0.5
media_observada = np.mean(numeros)

# Error estándar de la media para U(0,1)
error_media = np.sqrt(1 / (12 * N))

z_calculado = (media_observada - media_teorica) / error_media

z_critico = stats.norm.ppf(1 - ALPHA / 2)

p_media = 2 * stats.norm.sf(abs(z_calculado))

print(f"Media teórica:       {media_teorica:.6f}")
print(f"Media observada:     {media_observada:.6f}")
print(f"Error estándar:      {error_media:.6f}")
print(f"Z calculado:         {z_calculado:.6f}")
print(f"Z crítico:           ±{z_critico:.6f}")
print(f"Valor p:             {p_media:.6f}")

if p_media > ALPHA:
    print("RESULTADO: APROBADA")
    print("La media no presenta diferencias significativas.")
else:
    print("RESULTADO: RECHAZADA")
    print("La media presenta diferencias significativas.")

# =====================================================
# B. PRUEBA DE VARIANZA
# =====================================================

print("\n" + "=" * 65)
print("3. PRUEBA DE VARIANZA")
print("=" * 65)

varianza_teorica = 1 / 12
varianza_observada = np.var(numeros, ddof=1)

# Aproximación normal para la varianza muestral
# Var((X - 0.5)^2) = 1/180 para U(0,1)
error_varianza = np.sqrt(1 / (180 * N))

z_varianza = (
    varianza_observada - varianza_teorica
) / error_varianza

p_varianza = 2 * stats.norm.sf(abs(z_varianza))

z_critico_var = stats.norm.ppf(1 - ALPHA / 2)

print(f"Varianza teórica:    {varianza_teorica:.6f}")
print(f"Varianza observada:  {varianza_observada:.6f}")
print(f"Error estándar:      {error_varianza:.6f}")
print(f"Z calculado:         {z_varianza:.6f}")
print(f"Z crítico:           ±{z_critico_var:.6f}")
print(f"Valor p:             {p_varianza:.6f}")

if p_varianza > ALPHA:
    print("RESULTADO: APROBADA")
    print("La varianza no presenta diferencias significativas.")
else:
    print("RESULTADO: RECHAZADA")
    print("La varianza presenta diferencias significativas.")

# =====================================================
# C. PRUEBA DE UNIFORMIDAD (CHI-CUADRADA)
# =====================================================

print("\n" + "=" * 65)
print("4. PRUEBA DE UNIFORMIDAD")
print("=" * 65)

K = 10

frecuencias_observadas, limites = np.histogram(
    numeros,
    bins=K,
    range=(0, 1)
)

frecuencia_esperada = N / K

chi_uniformidad = np.sum(
    (frecuencias_observadas - frecuencia_esperada) ** 2
    / frecuencia_esperada
)

grados_libertad = K - 1

chi_critico = stats.chi2.ppf(
    1 - ALPHA,
    grados_libertad
)

p_uniformidad = stats.chi2.sf(
    chi_uniformidad,
    grados_libertad
)

print("\nTABLA DE FRECUENCIAS:")
print("-" * 55)
print(f"{'Intervalo':<20}{'Observada':<15}{'Esperada':<15}")

for i in range(K):
    print(
        f"[{limites[i]:.1f}, {limites[i+1]:.1f})"
        f"{frecuencias_observadas[i]:>12}"
        f"{frecuencia_esperada:>15.2f}"
    )

print("-" * 55)

print(f"\nChi cuadrada calculada: {chi_uniformidad:.6f}")
print(f"Chi cuadrada crítica:   {chi_critico:.6f}")
print(f"Grados de libertad:     {grados_libertad}")
print(f"Valor p:                {p_uniformidad:.6f}")

if p_uniformidad > ALPHA:
    print("RESULTADO: APROBADA")
    print("Los números cumplen la prueba de uniformidad.")
else:
    print("RESULTADO: RECHAZADA")
    print("Los números no cumplen la prueba de uniformidad.")

# =====================================================
# D. PRUEBA DE INDEPENDENCIA (SERIES)
# =====================================================

print("\n" + "=" * 65)
print("5. PRUEBA DE INDEPENDENCIA (SERIES)")
print("=" * 65)

# Formar parejas consecutivas:
# (r1,r2), (r3,r4), ..., (r99,r100)

x = numeros[0::2]
y = numeros[1::2]

# Dividir cada variable en dos intervalos
M = 2

tabla_observada, _, _ = np.histogram2d(
    x,
    y,
    bins=M,
    range=[[0, 1], [0, 1]]
)

# Prueba de independencia Chi-cuadrada
chi_independencia, p_independencia, gl, tabla_esperada = (
    stats.chi2_contingency(
        tabla_observada,
        correction=False
    )
)

chi_critico_ind = stats.chi2.ppf(
    1 - ALPHA,
    gl
)

print("\nTABLA DE FRECUENCIAS OBSERVADAS:")
print(pd.DataFrame(
    tabla_observada.astype(int),
    index=["X: 0.0 - 0.5", "X: 0.5 - 1.0"],
    columns=["Y: 0.0 - 0.5", "Y: 0.5 - 1.0"]
))

print("\nTABLA DE FRECUENCIAS ESPERADAS:")
print(pd.DataFrame(
    tabla_esperada,
    index=["X: 0.0 - 0.5", "X: 0.5 - 1.0"],
    columns=["Y: 0.0 - 0.5", "Y: 0.5 - 1.0"]
).round(2))

print(f"\nCantidad de parejas:  {len(x)}")
print(f"Chi cuadrada:         {chi_independencia:.6f}")
print(f"Chi crítica:          {chi_critico_ind:.6f}")
print(f"Grados de libertad:   {gl}")
print(f"Valor p:              {p_independencia:.6f}")

if p_independencia > ALPHA:
    print("RESULTADO: APROBADA")
    print("No se detecta dependencia significativa entre las parejas.")
else:
    print("RESULTADO: RECHAZADA")
    print("Se detecta dependencia significativa entre las parejas.")

# =====================================================
# RESUMEN GENERAL
# =====================================================

print("\n" + "=" * 65)
print("6. RESUMEN GENERAL DE LAS PRUEBAS")
print("=" * 65)

resultados = pd.DataFrame({
    "Prueba": [
        "Medias",
        "Varianza",
        "Uniformidad",
        "Independencia"
    ],
    "Valor p": [
        p_media,
        p_varianza,
        p_uniformidad,
        p_independencia
    ]
})

resultados["Resultado"] = np.where(
    resultados["Valor p"] > ALPHA,
    "APROBADA",
    "RECHAZADA"
)

print(resultados.to_string(index=False))

print("\nNivel de significancia:", ALPHA)
print("FIN DEL PROGRAMA")
