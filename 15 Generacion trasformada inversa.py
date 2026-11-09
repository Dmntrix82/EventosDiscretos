import numpy as np

# Configurar semilla para reproducibilidad y tamaño de la muestra
np.random.seed(42)
N_MUESTRAS = 100

print(
    "=== GENERACIÓN DE 100 NÚMEROS ALEATORIOS (MÉTODO DE LA TRANSFORMADA"
    " INVERSA) ===\n"
)

# ==========================================
# INCISO a) f(x) = (x / 5) * e^(-x^2 / 10)
# Expresión analítica: x = sqrt(-10 * ln(R))
# ==========================================
R_a = np.random.uniform(0, 1, N_MUESTRAS)
x_a = np.sqrt(-10 * np.log(R_a))
print("--- INCISO (a) ---")
print("Expresión: x = sqrt(-10 * ln(R))")
print(f"Primeros 10 valores:\n{x_a[:10]}\n")

# ==========================================
# INCISO b) f(x) = 36 * x^2 * e^(-12 * x^3)
# Expresión analítica: x = (-1/12 * ln(R))^(1/3)
# ==========================================
R_b = np.random.uniform(0, 1, N_MUESTRAS)
x_b = (-1 / 12 * np.log(R_b)) ** (1 / 3)
print("--- INCISO (b) ---")
print("Expresión: x = (-1/12 * ln(R))^(1/3)")
print(f"Primeros 10 valores:\n{x_b[:10]}\n")

# ==========================================
# INCISO c) f(x) = 4 * x^3 * e^(-x^4)
# Expresión analítica: x = (-ln(R))^(1/4)
# ==========================================
R_c = np.random.uniform(0, 1, N_MUESTRAS)
x_c = (-np.log(R_c)) ** (1 / 4)
print("--- INCISO (c) ---")
print("Expresión: x = (-ln(R))^(1/4)")
print(f"Primeros 10 valores:\n{x_c[:10]}\n")
