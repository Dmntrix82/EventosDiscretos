
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import t

# ============================================================
# 1. CONFIGURACION DEL MODELO
# ============================================================

np.random.seed(42)

PRECIO = 6.0
COSTO = 3.5
MARGEN = PRECIO - COSTO

N_HORAS = 100
N_CORRIDAS = 5
CONFIANZA = 0.95
ALPHA = 1 - CONFIANZA

# Demanda posible y sus probabilidades
demanda_valores = np.array([0, 1, 2, 3, 4, 5, 6])

probabilidades = np.array([
    0.10, 0.15, 0.25, 0.20, 0.15, 0.08, 0.07
])

prob_acumulada = np.cumsum(probabilidades)

# Verificar que las probabilidades sumen 1
assert np.isclose(np.sum(probabilidades), 1.0), \
    "Las probabilidades deben sumar 1."


# ============================================================
# 2. CALCULOS TEORICOS
# ============================================================

demanda_esperada = np.sum(
    demanda_valores * probabilidades
)

demanda_cuadratica = np.sum(
    demanda_valores**2 * probabilidades
)

varianza_demanda = demanda_cuadratica - demanda_esperada**2

utilidad_teorica = MARGEN * demanda_esperada

varianza_utilidad = MARGEN**2 * varianza_demanda

desviacion_teorica = np.sqrt(varianza_utilidad)

error_estandar_teorico = desviacion_teorica / np.sqrt(N_HORAS)

# ============================================================
# 3. GENERACION DE DEMANDA
# METODO DE LA TRANSFORMADA INVERSA DISCRETA
# ============================================================

def simular_demanda(n_horas):

    numeros_aleatorios = np.random.uniform(0, 1, n_horas)

    demanda = np.searchsorted(
        prob_acumulada,
        numeros_aleatorios,
        side="right"
    )

    return demanda


# ============================================================
# 4. SIMULACION DE LAS CINCO CORRIDAS
# ============================================================

resultados = []

for i in range(N_CORRIDAS):

    # Generar demanda por hora
    demanda = simular_demanda(N_HORAS)

    # Calcular utilidad de cada hora
    utilidad = demanda * MARGEN

    # Utilidad promedio acumulada
    utilidad_acumulada = (
        np.cumsum(utilidad) /
        np.arange(1, N_HORAS + 1)
    )

    # Estadisticas de la corrida
    media = np.mean(utilidad)
    desviacion = np.std(utilidad, ddof=1)
    varianza = np.var(utilidad, ddof=1)

    # Intervalo de confianza individual
    error_estandar = desviacion / np.sqrt(N_HORAS)

    t_critico = t.ppf(
        1 - ALPHA / 2,
        df=N_HORAS - 1
    )

    margen_error = t_critico * error_estandar

    limite_inferior = media - margen_error
    limite_superior = media + margen_error

    resultados.append({
        "corrida": i + 1,
        "demanda": demanda,
        "utilidad": utilidad,
        "acumulada": utilidad_acumulada,
        "media": media,
        "desviacion": desviacion,
        "varianza": varianza,
        "error_estandar": error_estandar,
        "limite_inferior": limite_inferior,
        "limite_superior": limite_superior
    })


# ============================================================
# 5. INTERVALO DE CONFIANZA GLOBAL
# ============================================================

medias_finales = np.array([
    r["media"] for r in resultados
])

media_global = np.mean(medias_finales)

desviacion_global = np.std(medias_finales, ddof=1)

error_global = desviacion_global / np.sqrt(N_CORRIDAS)

t_global = t.ppf(
    1 - ALPHA / 2,
    df=N_CORRIDAS - 1
)

margen_global = t_global * error_global

ic_global_inferior = media_global - margen_global
ic_global_superior = media_global + margen_global


# ============================================================
# 6. INFORME GENERAL DEL PROBLEMA
# ============================================================

print("\n" + "=" * 75)
print("       INFORME DE SIMULACION - RESTAURANTE DE HAMBURGUESAS")
print("=" * 75)

print("\n1. PARAMETROS DEL MODELO")
print("-" * 75)

print(f"Precio de venta:             ${PRECIO:.2f}")
print(f"Costo de produccion:         ${COSTO:.2f}")
print(f"Margen por hamburguesa:      ${MARGEN:.2f}")
print(f"Horas por corrida:            {N_HORAS}")
print(f"Numero de corridas:           {N_CORRIDAS}")
print(f"Nivel de confianza:           {CONFIANZA*100:.0f}%")

print("\n2. RESULTADOS TEORICOS")
print("-" * 75)

print(f"Demanda esperada:             {demanda_esperada:.4f}")
print(f"Varianza de la demanda:       {varianza_demanda:.4f}")
print(f"Desviacion de la demanda:     {np.sqrt(varianza_demanda):.4f}")
print(f"Utilidad esperada por hora:   ${utilidad_teorica:.4f}")
print(f"Varianza de la utilidad:      {varianza_utilidad:.4f}")
print(f"Desviacion de la utilidad:    ${desviacion_teorica:.4f}")
print(f"Error estandar teorico:       ${error_estandar_teorico:.4f}")


# ============================================================
# 7. RESULTADOS INDIVIDUALES POR CORRIDA
# ============================================================

print("\n3. RESULTADOS ESTADISTICOS POR CORRIDA")
print("-" * 75)

for r in resultados:

    print(f"\nCORRIDA {r['corrida']}")

    print("Demandas de las primeras 10 horas:")
    print(r["demanda"][:10])

    print(f"Utilidad promedio:      ${r['media']:.4f}")
    print(f"Varianza:               {r['varianza']:.4f}")
    print(f"Desviacion estandar:    ${r['desviacion']:.4f}")

    print(
        f"IC 95%: [${r['limite_inferior']:.4f}, "
        f"${r['limite_superior']:.4f}]"
    )

    print(
        f"Error respecto al teorico: "
        f"${abs(r['media']-utilidad_teorica):.4f}"
    )


# ============================================================
# 8. TABLA RESUMEN DE LAS CINCO CORRIDAS
# ============================================================

print("\n\n4. TABLA COMPARATIVA")
print("=" * 100)

print(
    f"{'Corrida':<10}"
    f"{'Media':<13}"
    f"{'Desv.Est.':<13}"
    f"{'IC Inferior':<16}"
    f"{'IC Superior':<16}"
    f"{'Error':<12}"
)

for r in resultados:

    print(
        f"{r['corrida']:<10}"
        f"{r['media']:<13.4f}"
        f"{r['desviacion']:<13.4f}"
        f"{r['limite_inferior']:<16.4f}"
        f"{r['limite_superior']:<16.4f}"
        f"{abs(r['media']-utilidad_teorica):<12.4f}"
    )


# ============================================================
# 9. RESULTADO GLOBAL DE LAS CINCO CORRIDAS
# ============================================================

print("\n5. INTERVALO DE CONFIANZA GLOBAL")
print("-" * 75)

print(f"Media global:              ${media_global:.4f}")
print(f"Desviacion entre medias:   ${desviacion_global:.4f}")
print(f"Error estandar global:     ${error_global:.4f}")
print(f"Valor critico t:            {t_global:.4f}")

print(
    f"IC GLOBAL 95%: "
    f"[${ic_global_inferior:.4f}, ${ic_global_superior:.4f}]"
)

print(f"Utilidad teorica:          ${utilidad_teorica:.4f}")

if ic_global_inferior <= utilidad_teorica <= ic_global_superior:
    print("RESULTADO: El IC global contiene el valor teorico.")
else:
    print("RESULTADO: El IC global NO contiene el valor teorico.")


# ============================================================
# 10. GRAFICA DE ESTABILIZACION
# ============================================================

plt.figure(figsize=(13, 7))

for r in resultados:

    horas = np.arange(1, N_HORAS + 1)

    plt.plot(
        horas,
        r["acumulada"],
        linewidth=1.5,
        label=f"Corrida {r['corrida']}"
    )

    # Mostrar la media final
    plt.scatter(
        N_HORAS,
        r["media"],
        s=35
    )

plt.axhline(
    y=utilidad_teorica,
    color="black",
    linestyle="--",
    linewidth=2,
    label=f"Media teorica ${utilidad_teorica:.3f}"
)

plt.title(
    "Estabilizacion de la utilidad promedio por hora",
    fontsize=14
)

plt.xlabel("Horas de trabajo")
plt.ylabel("Utilidad promedio acumulada ($)")

plt.xlim(1, N_HORAS)
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()


# ============================================================
# 11. GRAFICA DE INTERVALOS DE CONFIANZA INDIVIDUALES
# ============================================================

plt.figure(figsize=(11, 6))

for r in resultados:

    inferior = r["limite_inferior"]
    superior = r["limite_superior"]
    media = r["media"]

    plt.errorbar(
        r["corrida"],
        media,
        yerr=[
            [media - inferior],
            [superior - media]
        ],
        fmt="o",
        capsize=7,
        markersize=8,
        label=f"Corrida {r['corrida']}"
    )

plt.axhline(
    utilidad_teorica,
    color="red",
    linestyle="--",
    label=f"Teorico ${utilidad_teorica:.3f}"
)

plt.title("Intervalos de confianza individuales al 95%")
plt.xlabel("Numero de corrida")
plt.ylabel("Utilidad promedio por hora ($)")
plt.xticks(range(1, N_CORRIDAS + 1))
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()


# ============================================================
# 12. GRAFICA DEL INTERVALO GLOBAL
# ============================================================

plt.figure(figsize=(9, 5))

plt.errorbar(
    1,
    media_global,
    yerr=[[
        media_global - ic_global_inferior
    ], [
        ic_global_superior - media_global
    ]],
    fmt="o",
    capsize=10,
    markersize=9,
    label="Intervalo global 95%"
)

plt.axhline(
    utilidad_teorica,
    color="red",
    linestyle="--",
    label=f"Valor teorico ${utilidad_teorica:.3f}"
)

plt.title("Intervalo de confianza global de las 5 corridas")
plt.xlabel("Estimacion global")
plt.ylabel("Utilidad promedio por hora ($)")
plt.xticks([1], ["Cinco corridas"])
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()


# ============================================================
# 13. FRECUENCIAS DE DEMANDA OBSERVADAS
# ============================================================

demandas_totales = np.concatenate([
    r["demanda"] for r in resultados
])

frecuencias = np.array([
    np.mean(demandas_totales == d)
    for d in demanda_valores
])

print("\n6. COMPARACION DE FRECUENCIAS DE DEMANDA")
print("-" * 75)

print(
    f"{'Demanda':<12}"
    f"{'Prob. Teorica':<18}"
    f"{'Frecuencia Sim.':<18}"
)

for d, p, f in zip(
    demanda_valores,
    probabilidades,
    frecuencias
):
    print(f"{d:<12}{p:<18.4f}{f:<18.4f}")

plt.figure(figsize=(10, 5))

ancho = 0.35

plt.bar(
    demanda_valores - ancho/2,
    probabilidades,
    width=ancho,
    label="Probabilidad teorica"
)

plt.bar(
    demanda_valores + ancho/2,
    frecuencias,
    width=ancho,
    label="Frecuencia simulada"
)

plt.title("Distribucion teorica vs. demanda simulada")
plt.xlabel("Cantidad de hamburguesas")
plt.ylabel("Probabilidad / Frecuencia")
plt.xticks(demanda_valores)
plt.legend()
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.show()


# ============================================================
# 14. CONCLUSION AUTOMATICA
# ============================================================

print("\n" + "=" * 75)
print("7. CONCLUSION DE LA SIMULACION")
print("=" * 75)

print(
    f"Se realizaron {N_CORRIDAS} corridas de "
    f"{N_HORAS} horas, para un total de "
    f"{N_CORRIDAS*N_HORAS} horas simuladas."
)

print(
    f"La utilidad teorica esperada es de "
    f"${utilidad_teorica:.3f} por hora."
)

print(
    f"La utilidad promedio global simulada fue de "
    f"${media_global:.3f} por hora."
)

print(
    f"La diferencia entre el promedio global y "
    f"el teorico es de "
    f"${abs(media_global-utilidad_teorica):.3f}."
)

print("\nFIN DEL INFORME.")

