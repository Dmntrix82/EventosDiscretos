
import numpy as np

# ============================================================
# 1. CONFIGURACION Y DATOS DEL PROBLEMA
# ============================================================

np.random.seed(42)

n = 300  # Numero de barras a simular

# Primera barra: distribucion normal
media_x1 = 30
varianza_x1 = 0.81
desviacion_x1 = np.sqrt(varianza_x1)

# Segunda barra: distribucion Erlang
k = 10
media_x2 = 14.5
theta = media_x2 / k

# Especificaciones de diseno
LSL = 40
objetivo = 45
USL = 50


# ============================================================
# 2. SIMULACION DE LAS DOS BARRAS
# ============================================================

# Generar 300 valores de X1 (distribucion normal)
x1 = np.random.normal(
    loc=media_x1,
    scale=desviacion_x1,
    size=n
)

# Generar 300 valores de X2 (distribucion Erlang)
# Erlang = Gamma con k entero
x2 = np.random.gamma(
    shape=k,
    scale=theta,
    size=n
)

# Longitud final despues de la soldadura
longitud_final = x1 + x2


# ============================================================
# 3. ESTADISTICOS DE LAS BARRAS SOLDADAS
# ============================================================

media_proceso = np.mean(longitud_final)
desviacion_proceso = np.std(longitud_final, ddof=1)
varianza_proceso = np.var(longitud_final, ddof=1)

print("=" * 60)
print("       SIMULACION DE SOLDADURA DE 300 BARRAS")
print("=" * 60)

print(f"Media de X1: {np.mean(x1):.4f} cm")
print(f"Media de X2: {np.mean(x2):.4f} cm")

print(f"\nMedia de longitud final: {media_proceso:.4f} cm")
print(f"Desviacion estandar: {desviacion_proceso:.4f} cm")
print(f"Varianza: {varianza_proceso:.4f} cm^2")


# ============================================================
# 4. DETERMINAR BARRAS DENTRO Y FUERA DE ESPECIFICACIONES
# ============================================================

# Barras que cumplen las especificaciones
dentro = (longitud_final >= LSL) & (longitud_final <= USL)

# Barras que no cumplen las especificaciones
fuera = (longitud_final < LSL) | (longitud_final > USL)

cantidad_dentro = np.sum(dentro)
cantidad_fuera = np.sum(fuera)

# Separar defectos por cada limite
debajo = np.sum(longitud_final < LSL)
encima = np.sum(longitud_final > USL)

# Estimador de probabilidad de estar fuera
probabilidad_fuera = cantidad_fuera / n

# Porcentaje de barras defectuosas
porcentaje_fuera = probabilidad_fuera * 100

print("\n" + "=" * 60)
print("       ANALISIS DE ESPECIFICACIONES")
print("=" * 60)

print(f"Limite inferior: {LSL} cm")
print(f"Objetivo: {objetivo} cm")
print(f"Limite superior: {USL} cm")

print(f"\nBarras dentro de especificaciones: {cantidad_dentro}")
print(f"Barras fuera de especificaciones: {cantidad_fuera}")

print(f"Barras menores a 40 cm: {debajo}")
print(f"Barras mayores a 50 cm: {encima}")

print(f"\nProbabilidad estimada de estar fuera: "
      f"{probabilidad_fuera:.4f}")

print(f"Porcentaje fuera de especificaciones: "
      f"{porcentaje_fuera:.2f}%")


# ============================================================
# 5. CALCULO DEL INDICE DE CAPACIDAD Cp
# ============================================================

Cp = (USL - LSL) / (6 * desviacion_proceso)


# ============================================================
# 6. CALCULO DEL INDICE DE CAPACIDAD Cpk
# ============================================================

Cpu = (USL - media_proceso) / (3 * desviacion_proceso)

Cpl = (media_proceso - LSL) / (3 * desviacion_proceso)

Cpk = min(Cpu, Cpl)


print("\n" + "=" * 60)
print("       INDICES DE CAPACIDAD DEL PROCESO")
print("=" * 60)

print(f"Cp: {Cp:.4f}")
print(f"Cpu: {Cpu:.4f}")
print(f"Cpl: {Cpl:.4f}")
print(f"Cpk: {Cpk:.4f}")


# ============================================================
# 7. INTERPRETACION DE LA CAPACIDAD
# ============================================================

print("\n" + "=" * 60)
print("       CONCLUSION DEL PROCESO")
print("=" * 60)

if Cp >= 1.33 and Cpk >= 1.33:
    print("El proceso es potencialmente capaz.")
elif Cp >= 1 and Cpk >= 1:
    print("El proceso tiene capacidad limitada.")
else:
    print("El proceso NO es capaz de cumplir las especificaciones.")

if Cpk < Cp:
    print("El proceso presenta descentrado respecto a las especificaciones.")

print("\nNOTA:")
print("Los indices Cp y Cpk miden capacidad, no control estadistico.")
print("Para verificar el control se necesita analizar el proceso")
print("en el tiempo mediante graficos de control.")
