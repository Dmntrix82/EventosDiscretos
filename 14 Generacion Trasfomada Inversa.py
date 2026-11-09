import numpy as np

# Configurar semilla para reproducibilidad y definir el tamaño de la muestra
np.seed = 42
N_MUESTRAS = 100

print("=== GENERACIÓN DE 100 NÚMEROS ALEATORIOS (MÉTODO DE LA TRANSFORMADA INVERSA) ===\n")

# ==========================================
# INCISO a) p(x) = (1/5)*(4/5)^(x-1) para x = 1, 2, 3, ...
# ==========================================
# Es una distribución geométrica con base analítica despejada:
# x = ceil( ln(R) / ln(4/5) )
R_a = np.random.uniform(0, 1, N_MUESTRAS)
x_a = np.ceil(np.log(R_a) / np.log(4/5)).astype(int)
print(f"a) Primeros 10 valores (Inciso a):\n{x_a[:10]}\n")

# ==========================================
# INCISO b) p(x) = (1/2)*(1/2)^x para x = 0, 1, 2, ...
# ==========================================
# p(x) = (1/2)^(x+1). Despejando: x = ceil( ln(R) / ln(0.5) ) - 1
R_b = np.random.uniform(0, 1, N_MUESTRAS)
x_b = np.ceil(np.log(R_b) / np.log(0.5)).astype(int) - 1
print(f"b) Primeros 10 valores (Inciso b):\n{x_b[:10]}\n")


# Función general para distribuciones discretas finitas usando la CDF acumulada
def generar_discreta_inversa(valores, probabilidades, n_muestras):
    cdf = np.cumsum(probabilidades)
    r = np.random.uniform(0, 1, n_muestras)
    resultados = []
    for val in r:
        # Encuentra el índice del primer elemento donde r < cdf
        idx = np.searchsorted(cdf, val, side='right')
        resultados.append(valores[min(idx, len(valores) - 1)])
    return np.array(resultados)


# ==========================================
# INCISO c) p(x) = (20 + 10x) / 200 para x = 0, 1, 2, 3, 4
# ==========================================
val_c = np.array([0, 1, 2, 3, 4])
prob_c = (20 + 10 * val_c) / 200.0
x_c = generar_discreta_inversa(val_c, prob_c, N_MUESTRAS)
print(f"c) Primeros 10 valores (Inciso c):\n{x_c[:10]}\n")

# ==========================================
# INCISO d) p(x) = (18 - 4x) / 50 para x = 0, 1, 2, 3, 4
# ==========================================
val_d = np.array([0, 1, 2, 3, 4])
prob_d = (18 - 4 * val_d) / 50.0
x_d = generar_discreta_inversa(val_d, prob_d, N_MUESTRAS)
print(f"d) Primeros 10 valores (Inciso d):\n{x_d[:10]}\n")

# ==========================================
# INCISO e) p(x) = (3x + 8) / 100 para x = 2, 3, 4, 5, 6
# ==========================================
val_e = np.array([2, 3, 4, 5, 6])
prob_e = (3 * val_e + 8) / 100.0
x_e = generar_discreta_inversa(val_e, prob_e, N_MUESTRAS)
print(f"e) Primeros 10 valores (Inciso e):\n{x_e[:10]}\n")

# ==========================================
# INCISO f) p(x) = 1/6 para x = 6, 7, 8, 9, 10, 11
# ==========================================
val_f = np.array([6, 7, 8, 9, 10, 11])
prob_f = np.ones(6) / 6.0
x_f = generar_discreta_inversa(val_f, prob_f, N_MUESTRAS)
print(f"f) Primeros 10 valores (Inciso f):\n{x_f[:10]}\n")

# ==========================================
# INCISO g) p(x) = [p(1-p)^(x-1)] / [1 - (1-p)^n] para x = 1, 2, ..., n
# ==========================================
# Definimos parámetros de ejemplo: p = 0.4 y n = 5
p_g = 0.4
n_g = 5
val_g = np.arange(1, n_g + 1)
prob_g = (p_g * (1 - p_g) ** (val_g - 1)) / (1 - (1 - p_g) ** n_g)
x_g = generar_discreta_inversa(val_g, prob_g, N_MUESTRAS)
print(
    f"g) Primeros 10 valores (Inciso g, con p={p_g}, n={n_g}):\n{x_g[:10]}\n"
)