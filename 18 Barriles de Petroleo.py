
import numpy as np
from scipy import stats
import math

# =========================================================
# 1. DATOS DE ENTRADA
# =========================================================

# Resultados de las 5 replicas (USD por barril)
datos = np.array([125.50, 132.75, 120.80, 138.20, 127.50])

n_inicial = len(datos)

# Estadisticos muestrales
media = np.mean(datos)
desviacion = np.std(datos, ddof=1)
varianza = np.var(datos, ddof=1)

print("=" * 55)
print("       ESTADISTICOS MUESTRALES")
print("=" * 55)

print(f"Numero de replicas: {n_inicial}")
print(f"Media muestral: {media:.4f} USD")
print(f"Desviacion estandar: {desviacion:.4f} USD")
print(f"Varianza muestral: {varianza:.4f} USD^2")


# =========================================================
# INCISO A: EXACTITUD CON 95% DE CONFIANZA
# =========================================================

confianza_a = 0.95
alpha_a = 1 - confianza_a

# Grados de libertad
gl_a = n_inicial - 1

# Valor critico de t de Student
t_a = stats.t.ppf(1 - alpha_a / 2, gl_a)

# Margen de error o exactitud
exactitud_a = t_a * desviacion / np.sqrt(n_inicial)

# Intervalo de confianza
limite_inferior = media - exactitud_a
limite_superior = media + exactitud_a

print("\n" + "=" * 55)
print("       INCISO A: EXACTITUD DEL 95%")
print("=" * 55)

print(f"Nivel de confianza: {confianza_a * 100:.0f}%")
print(f"Grados de libertad: {gl_a}")
print(f"Valor critico t: {t_a:.4f}")
print(f"Exactitud: +/- {exactitud_a:.4f} USD")

print(f"Intervalo de confianza: "
      f"[{limite_inferior:.2f}, {limite_superior:.2f}] USD")


# =========================================================
# INCISO B: NUMERO DE REPLICAS PARA EXACTITUD +/- 0.35
# =========================================================

confianza_b = 0.90
alpha_b = 1 - confianza_b

exactitud_deseada = 0.35

# Estimacion inicial mediante la distribucion normal
z = stats.norm.ppf(1 - alpha_b / 2)

n = math.ceil((z * desviacion / exactitud_deseada) ** 2)

# Iteracion usando t de Student
while True:

    gl_b = n - 1

    # Valor critico actualizado
    t_b = stats.t.ppf(1 - alpha_b / 2, gl_b)

    # Nuevo calculo de replicas
    n_nuevo = math.ceil(
        (t_b * desviacion / exactitud_deseada) ** 2
    )

    if n_nuevo == n:
        break

    n = n_nuevo

# Comprobacion de la exactitud obtenida
exactitud_final = t_b * desviacion / np.sqrt(n)

print("\n" + "=" * 55)
print("       INCISO B: CALCULO DE REPLICAS")
print("=" * 55)

print(f"Nivel de confianza: {confianza_b * 100:.0f}%")
print(f"Exactitud deseada: +/- {exactitud_deseada:.2f} USD")
print(f"Desviacion estimada: {desviacion:.4f} USD")
print(f"Valor critico t final: {t_b:.4f}")
print(f"Grados de libertad: {gl_b}")
print(f"Numero total de replicas: {n}")
print(f"Exactitud obtenida: +/- {exactitud_final:.6f} USD")

# Verificacion
if exactitud_final <= exactitud_deseada:
    print("\nRESULTADO: Se cumple la exactitud deseada.")
else:
    print("\nRESULTADO: No se cumple la exactitud deseada.")
