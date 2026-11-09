
import math
from scipy import stats


def pruebas_estadisticas():

    # ==========================================
    # DATOS DE ENTRADA
    # ==========================================

    datos = [
        0.8797, 0.9848, 0.4557, 0.9170, 0.8376,
        0.3884, 0.3469, 0.1592, 0.2204, 0.6235,
        0.6289, 0.7977, 0.8536, 0.5991, 0.3681,
        0.8750, 0.5844, 0.8846, 0.5461, 0.2088,
        0.5999, 0.8147, 0.3410, 0.5739, 0.8589,
        0.9996, 0.6431, 0.1492, 0.3254, 0.1525,
        0.2006, 0.7387, 0.8681, 0.0856, 0.4720,
        0.2415, 0.5613, 0.5291, 0.2258, 0.4272,
        0.3808, 0.0318, 0.3188, 0.4603, 0.6360,
        0.9606, 0.7401, 0.5992, 0.5027, 0.0954
    ]

    N = len(datos)
    alpha = 0.05

    # Validaciones
    if N < 2:
        print("Error: Se necesitan al menos 2 datos.")
        return

    if not all(0 <= x <= 1 for x in datos):
        print("Error: Todos los datos deben estar entre 0 y 1.")
        return

    print("=" * 50)
    print("PRUEBAS ESTADISTICAS DE NUMEROS ALEATORIOS")
    print("=" * 50)

    print(f"Total de datos (N): {N}")
    print(f"Nivel de significancia: {alpha}")
    print(f"Nivel de confianza: {(1-alpha)*100}%")

    # ==========================================
    # 1. PRUEBA DE MEDIA
    # ==========================================

    media = sum(datos) / N

    media_teorica = 0.5
    varianza_teorica = 1 / 12

    z0 = (media - media_teorica) / math.sqrt(
        varianza_teorica / N
    )

    z_critico = stats.norm.ppf(1 - alpha / 2)

    print("\n" + "=" * 50)
    print("1. PRUEBA DE MEDIA")
    print("=" * 50)

    print(f"Media muestral: {media:.4f}")
    print(f"Media teorica: {media_teorica:.4f}")
    print(f"Estadistico Z0: {z0:.4f}")
    print(f"Valor critico: +/-{z_critico:.4f}")

    if abs(z0) <= z_critico:
        print("RESULTADO: NO SE RECHAZA H0")
        print("Los datos pasan la prueba de media.")
    else:
        print("RESULTADO: SE RECHAZA H0")
        print("Los datos no pasan la prueba de media.")

    # ==========================================
    # 2. PRUEBA DE VARIANZA
    # ==========================================

    varianza = sum(
        (x - media) ** 2 for x in datos
    ) / (N - 1)

    chi2_0 = ((N - 1) * varianza) / varianza_teorica

    chi2_inf = stats.chi2.ppf(alpha / 2, df=N - 1)
    chi2_sup = stats.chi2.ppf(1 - alpha / 2, df=N - 1)

    print("\n" + "=" * 50)
    print("2. PRUEBA DE VARIANZA")
    print("=" * 50)

    print(f"Varianza muestral: {varianza:.4f}")
    print(f"Varianza teorica: {varianza_teorica:.4f}")
    print(f"Estadistico Chi2: {chi2_0:.4f}")
    print(f"Limite inferior: {chi2_inf:.4f}")
    print(f"Limite superior: {chi2_sup:.4f}")

    if chi2_inf <= chi2_0 <= chi2_sup:
        print("RESULTADO: NO SE RECHAZA H0")
        print("Los datos pasan la prueba de varianza.")
    else:
        print("RESULTADO: SE RECHAZA H0")
        print("Los datos no pasan la prueba de varianza.")

    # ==========================================
    # 3. PRUEBA DE UNIFORMIDAD
    # ==========================================

    k = round(math.sqrt(N))

    frec_esperada = N / k
    frec_observadas = [0] * k

    for x in datos:

        idx = min(int(x * k), k - 1)

        frec_observadas[idx] += 1

    chi2_uniformidad = sum(
        (fo - frec_esperada) ** 2 / frec_esperada
        for fo in frec_observadas
    )

    chi2_critico = stats.chi2.ppf(
        1 - alpha, df=k - 1
    )

    p_valor = stats.chi2.sf(
        chi2_uniformidad, df=k - 1
    )

    print("\n" + "=" * 50)
    print("3. PRUEBA DE UNIFORMIDAD")
    print("=" * 50)

    print(f"Numero de intervalos: {k}")
    print(f"Frecuencia esperada: {frec_esperada:.2f}")
    print(f"Frecuencias observadas: {frec_observadas}")
    print(f"Chi2 calculado: {chi2_uniformidad:.4f}")
    print(f"Chi2 critico: {chi2_critico:.4f}")
    print(f"Valor p: {p_valor:.4f}")

    if chi2_uniformidad <= chi2_critico:
        print("RESULTADO: NO SE RECHAZA H0")
        print("Los datos pasan la prueba de uniformidad.")
    else:
        print("RESULTADO: SE RECHAZA H0")
        print("Los datos no pasan la prueba de uniformidad.")

    # ==========================================
    # RESUMEN FINAL
    # ==========================================

    print("\n" + "=" * 50)
    print("RESUMEN DE RESULTADOS")
    print("=" * 50)

    print(f"Media: {media:.4f}")
    print(f"Varianza: {varianza:.4f}")
    print(f"Uniformidad Chi2: {chi2_uniformidad:.4f}")

    print("\nFin del analisis estadistico.")


if __name__ == "__main__":
    pruebas_estadisticas()
