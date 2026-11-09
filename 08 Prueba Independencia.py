import numpy as np
from scipy.stats import chi2

# 1. Lista de los 50 números limpios (corrigiendo errores de escaneo: Q6213->0.6213, etc.)
datos = [
    0.5858, 0.8863, 0.8378, 0.3203, 0.4115, 0.2710, 0.9238, 0.1959, 0.9268, 0.6702, 0.6213, 0.4360,
    0.6279, 0.8415, 0.5786, 0.0543, 0.3567, 0.1655, 0.3880, 0.8080, 0.1931, 0.0843, 0.9152, 0.6093,
    0.7587, 0.4515, 0.3203, 0.5139, 0.7070, 0.9123, 0.1242, 0.8826, 0.9921, 0.8523, 0.6723, 0.8540,
    0.4722, 0.4781, 0.2101, 0.1680, 0.8658, 0.4028, 0.6136, 0.8720, 0.1126, 0.5857, 0.9172, 0.8943,
    0.8095, 0.6408
]

N = len(datos)
print(f"Total de números analizados: {N}")

# 2. Formar parejas consecutivas (r_i, r_{i+1})
# Usaremos pares no solapados: (d[0], d[1]), (d[2], d[3]), ...
pares = [(datos[i], datos[i+1]) for i in range(0, N - 1, 2)]
num_pares = len(pares)
print(f"Número total de pares ordenados: {num_pares}")

# 3. Definir el número de intervalos por eje (m). Usualmente m = 5 para n pequeño.
m = 5
print(f"Dividiendo el espacio en una cuadrícula de {m}x{m} (Total celdas = {m**m if False else m*m})")

# Crear la matriz de frecuencias observadas (O_ij)
matriz_observada = np.zeros((m, m), dtype=int)

for r1, r2 in pares:
    # Determinar en qué intervalo cae r1 y r2 (de 0 a m-1)
    # Manejar el caso exacto de 1.0 por seguridad
    i = min(int(r1 * m), m - 1)
    j = min(int(r2 * m), m - 1)
    matriz_observada[i, j] += 1

print("\n--- MATRIZ DE FRECUENCIAS OBSERVADAS (O_ij) ---")
print(matriz_observada)

# 4. Calcular la frecuencia esperada (E) por celda
# E = (Total de pares) / (m * m)
E = num_pares / (m * m)
print(f"\nFrecuencia esperada por celda (E): {E:.4f}")

# 5. Calcular el estadístico Chi-cuadrada (Chi2_calc = sum((O - E)^2 / E))
chi2_calc = np.sum(((matriz_observada - E) ** 2) / E)
print(f"Estadístico Chi-cuadrada calculado: {chi2_calc:.4f}")

# 6. Definir nivel de aceptación y significancia
nivel_aceptacion = 0.90
alfa = 1.0 - nivel_aceptacion

# Grados de libertad para la prueba de series en cuadrícula m x m: (m^2 - 1)
grados_libertad = (m * m) - 1

# Valor crítico de Chi-cuadrada
chi2_critico = chi2.ppf(1 - alfa, grados_libertad)
print(f"Grados de libertad (gl): {grados_libertad}")
print(f"Chi-cuadrada crítica (alfa = {alfa}): {chi2_critico:.4f}")

# 7. Conclusión
print("\n--- RESULTADO DE LA PRUEBA ---")
if chi2_calc < chi2_critico:
    print(f"Como {chi2_calc:.4f} < {chi2_critico:.4f}, NO SE RECHAZA la hipótesis nula (H0).")
    print("Conclusión: Los números son independientes con un nivel de aceptación del 90%.")
else:
    print(f"Como {chi2_calc:.4f} >= {chi2_critico:.4f}, SE RECHAZA la hipótesis nula (H0).")
    print("Conclusión: Los números NO son independientes con un nivel de aceptación del 90%.")