
import math
import random
import matplotlib.pyplot as plt

# Parámetros de la simulación
N = 5000  # Número de mantenimientos/simulaciones


# Definición de funciones para generar variables aleatorias (Distribución Erlang/Gamma)
def generar_a():
    # x_i = -20 * ln(r_i * r_j) = -20 * (ln(r_i) + ln(r_j))
    r_i = random.random()
    r_j = random.random()
    return -20 * math.log(r_i * r_j)


def generar_b():
    # x_i = -10 * ln(r_i * r_j * r_k * r_l)
    r = [random.random() for _ in range(4)]
    producto = 1.0
    for val in r:
        producto *= val
    return -10 * math.log(producto)


def generar_c():
    # x_i = -5 * ln(r_i * r_j * r_k * r_l * r_m * r_n * r_o * r_p)
    r = [random.random() for _ in range(8)]
    producto = 1.0
    for val in r:
        producto *= val
    return -5 * math.log(producto)


# Listas para almacenar el promedio móvil acumulado
promedios_a = []
promedios_b = []
promedios_c = []

suma_a, suma_b, suma_c = 0.0, 0.0, 0.0

# Simulación
for i in range(1, N + 1):
    val_a = generar_a()
    val_b = generar_b()
    val_c = generar_c()

    suma_a += val_a
    suma_b += val_b
    suma_c += val_c

    promedios_a.append(suma_a / i)
    promedios_b.append(suma_b / i)
    promedios_c.append(suma_c / i)

# Graficación del promedio móvil acumulado
plt.figure(figsize=(12, 6))
plt.plot(promedios_a, label="Función a (k=2, β=20)", color="blue", alpha=0.8)
plt.plot(promedios_b, label="Función b (k=4, β=10)", color="green", alpha=0.8)
plt.plot(promedios_c, label="Función c (k=8, β=5)", color="red", alpha=0.8)
plt.axhline(
    y=40, color="gray", linestyle="--", label="Valor Teórico Esperado (E[X] = 40)"
)

plt.title("Promedio Móvil Acumulado de Tiempos de Reparación")
plt.xlabel("Número de Mantenimientos")
plt.ylabel("Tiempo Promedio")
plt.legend()
plt.grid(True)
plt.show()

# Impresión de resultados finales
print(f"Promedio final Función a: {promedios_a[-1]:.4f}")
print(f"Promedio final Función b: {promedios_b[-1]:.4f}")
print(f"Promedio final Función c: {promedios_c[-1]:.4f}")