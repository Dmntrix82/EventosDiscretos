import math

def resolver_serie_congruencial():
    # Parámetros iniciales definidos en la imagen
    m = 177
    a = 121
    c = 553
    x0 = 23
    
    serie = [x0]
    vistos = {x0: 0}
    
    x = x0
    while True:
        x = (a * x + c) % m
        if x in vistos:
            indice_inicio = vistos[x]
            periodo = len(serie) - indice_inicio
            break
        vistos[x] = len(serie)
        serie.append(x)
        
    print(f"Serie generada: {serie}")
    print(f"Número total de elementos antes de repetir: {len(serie)}")
    
    # a) Determinar el ciclo o periodo de vida
    print(f"\n--- a) CICLO O PERIODO DE VIDA ---")
    print(f"El periodo de vida de la serie es: {periodo}")
    
    # b) Pruebas de media, varianza y uniformidad
    # Normalizamos los valores en el intervalo [0, 1) dividiendo entre m
    r = [xi / m for xi in serie]
    N = len(r)
    
    print(f"\n--- b) PRUEBAS ESTADÍSTICAS (N = {N}) ---")
    
    # 1. Prueba de Media
    media_r = sum(r) / N
    # Estadístico Z_0 para un nivel de significancia típico (ej. alpha = 0.05 -> Z_crit = 1.96)
    z_0 = (media_r - 0.5) / math.sqrt(1 / (12 * N))
    print(f"1. Prueba de Media:")
    print(f"   - Media muestral: {media_r:.4f}")
    print(f"   - Estadístico Z_0: {z_0:.4f}")
    
    # 2. Prueba de Varianza
    varianza_r = sum((val - media_r)**2 for val in r) / (N - 1)
    chi2_0 = (N - 1) * varianza_r / (1 / 12)
    print(f"2. Prueba de Varianza:")
    print(f"   - Varianza muestral: {varianza_r:.4f}")
    print(f"   - Estadístico Chi^2_0: {chi2_0:.4f}")
    
    # 3. Prueba de Uniformidad (Chi-cuadrada)
    k = int(math.sqrt(N)) if int(math.sqrt(N)) > 0 else 5  # Número de clases o intervalos
    frec_esperada = N / k
    frec_observadas = [0] * k
    
    for val in r:
        idx = min(int(val * k), k - 1)
        frec_observadas[idx] += 1
        
    chi2_uniformidad = sum((fo - frec_esperada)**2 / frec_esperada for fo in frec_observadas)
    print(f"3. Prueba de Uniformidad (Chi-cuadrada con {k} intervalos):")
    print(f"   - Frecuencia esperada por intervalo: {frec_esperada:.2f}")
    print(f"   - Frecuencias observadas: {frec_observadas}")
    print(f"   - Estadístico Chi^2 calc: {chi2_uniformidad:.4f}")

if __name__ == "__main__":
    resolver_serie_congruencial()
