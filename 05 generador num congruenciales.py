def encontrar_periodo_lcg(a, c_val, m, x0):
    """Calcula el periodo para un generador congruencial lineal: x_{i+1} = (a * x_i + c) mod m"""
    secuencia = []
    vistos = {}
    x = x0
    i = 0
    while x not in vistos:
        vistos[x] = i
        secuencia.append(x)
        x = (a * x + c_val) % m
        i += 1
    periodo = i - vistos[x]
    return periodo, secuencia


def encontrar_periodo_multistep(a1, a2, m, x0, x1):
    """Calcula el periodo para un generador de orden superior: x_{i+1} = (a1 * x_i + a2 * x_{i-1}) mod m"""
    secuencia = [x0, x1]
    vistos = {}
    i = 0
    # Guardamos tuplas de los últimos dos valores como estado
    while True:
        estado = (secuencia[-2], secuencia[-1])
        if estado in vistos:
            punto_inicio = vistos[estado]
            periodo = i - punto_inicio
            return periodo, secuencia
        vistos[estado] = i
        siguiente = (a1 * secuencia[-1] + a2 * secuencia[-2]) % m
        secuencia.append(siguiente)
        i += 1


# a) x_{i+1} = (21x_i + 15) mod 31, con x_0 = 21
per_a, seq_a = encontrar_periodo_lcg(
    a=21, c_val=15, m=31, x0=21
)  #

# b) x_{i+1} = (13x_i + 9) mod 128, con x_0 = 7
per_b, seq_b = encontrar_periodo_lcg(
    a=13, c_val=9, m=128, x0=7
)  #

# c) x_{i+1} = (17x_i) mod 31, con x_0 = 23 (c = 0)
per_c, seq_c = encontrar_periodo_lcg(
    a=17, c_val=0, m=31, x0=23
)  #

# d) x_{i+1} = (121 + x_i) mod 256, con x_0 = 17 (a = 1, c = 121)
per_d, seq_d = encontrar_periodo_lcg(
    a=1, c_val=121, m=256, x0=17
)  #

# e) x_{i+1} = (21x_i + 15x_{i-1}) mod 64, con x_0 = 21 y x_1 = 43
per_e, seq_e = encontrar_periodo_multistep(
    a1=21, a2=15, m=64, x0=21, x1=43
)  #

print(f"a) Periodo: {per_a} | Secuencia inicial: {seq_a[:10]}...")
print(f"b) Periodo: {per_b} | Secuencia inicial: {seq_b[:10]}...")
print(f"c) Periodo: {per_c} | Secuencia inicial: {seq_c[:10]}...")
print(f"d) Periodo: {per_d} | Secuencia inicial: {seq_d[:10]}...")
print(f"e) Periodo: {per_e} | Secuencia inicial: {seq_e[:10]}...")