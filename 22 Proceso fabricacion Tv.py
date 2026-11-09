
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from collections import Counter

# ============================================================
# 1. CONFIGURACION GENERAL
# ============================================================

N_SIMULACIONES = 500_000
SEMILLA = 20261103

POLITICAS = [60, 70, 80, 90, 100]

COSTO_FALTANTE = 40
COSTO_INVENTARIO = 20
COSTO_DEFECTO_FABRICA = 90
COSTO_DEFECTO_CLIENTE = 120

PROB_DEFECTO_FABRICA = 0.03
PROB_DEFECTO_CLIENTE = 0.05


# ============================================================
# 2. DATOS HISTORICOS
# ============================================================

demanda = [
99,94,80,73,86,95,90,70,92,83,89,93,62,94,86,62,77,72,
63,88,96,99,98,77,96,74,86,81,94,81,70,98,78,86,74,94,
95,77,79,89,65,94,88,72,71,70,76,95,92,96,93,72,97,75,
97,72,76,69,61,69,99,83,83,61,64,95,80,70,79,65,80,85,
72,68,83,78,84,64,72,67,94,100,78,93,66,99,97,74,93,95,
70,93,64,86,72,80,83,65,66,96,95,84,88,68,65,70,88,90,
85,92,81,68,92,64,84,69,73,71,98,66,68,74,93,94,86,69,
82,71,79,100,84,65,99,100,61,78,73,80,72,100,100,98,82,
60,93,75,84,75,76,71,94,74,84,72,71,71,85,69,88,97,93,
63,91,89,89,99,93,62,99,77,69,82,66,91,73,88,61,63,67,
76,100,93,82,72,75,92,87,74,60,93,77,60,84,64,83,75,68,
64,97,78
]

inspeccion = [
4,2,3,0,0,2,4,1,2,0,2,2,3,3,2,1,1,1,4,2,1,0,3,1,2,
3,1,1,1,0,1,2,1,1,1,1,0,0,2,1,1,1,3,1,0,3,0,1,0,1,
2,0,1,2,0,1,2,1,3,1,2,1,1,2,1,1,1,1,3,1,0,0,1,1,2,
0,0,0,1,0,2,0,2,1,2,0,1,1,2,0,1,2,1,2,3,0,0,0,2,2
]


# ============================================================
# 3. FUNCIONES DE ANALISIS
# ============================================================

def titulo(texto):
    print("\n" + "=" * 75)
    print(texto.center(75))
    print("=" * 75)


def intervalo_confianza(datos):
    n = len(datos)
    media = np.mean(datos)
    desviacion = np.std(datos, ddof=1)
    error = desviacion / np.sqrt(n)

    t = stats.t.ppf(0.975, n - 1)

    inferior = media - t * error
    superior = media + t * error

    return inferior, superior, desviacion, error


def mostrar_estadisticas(datos, nombre):

    serie = pd.Series(datos)

    tabla = pd.DataFrame({
        "Indicador": [
            "Cantidad de observaciones",
            "Media",
            "Mediana",
            "Desviacion estandar",
            "Minimo",
            "Maximo",
            "Percentil 25",
            "Percentil 75",
            "Percentil 90"
        ],
        nombre: [
            len(serie),
            serie.mean(),
            serie.median(),
            serie.std(),
            serie.min(),
            serie.max(),
            serie.quantile(0.25),
            serie.quantile(0.75),
            serie.quantile(0.90)
        ]
    })

    print(tabla.to_string(index=False))


# ============================================================
# 4. VALIDACION Y ANALISIS DE LOS DATOS
# ============================================================

if len(demanda) == 0 or len(inspeccion) == 0:
    raise ValueError("Los datos historicos no pueden estar vacios.")

if not all(60 <= x <= 100 for x in demanda):
    raise ValueError("Se encontraron valores de demanda fuera del rango.")

if not all(x in [0, 1, 2, 3, 4] for x in inspeccion):
    raise ValueError("Se encontraron valores invalidos de inspeccion.")


titulo("PROBLEMA 22 - FABRICACION DE TELEVISORES")

print("ANALISIS ESTADISTICO DE LOS DATOS HISTORICOS")

print(f"\nObservaciones de demanda: {len(demanda)}")
print(f"Observaciones de inspeccion: {len(inspeccion)}")

titulo("ESTADISTICAS DE LA DEMANDA")

mostrar_estadisticas(demanda, "Demanda diaria")

titulo("ESTADISTICAS DE INSPECCION")

mostrar_estadisticas(inspeccion, "Inspeccion diaria")


# ============================================================
# 5. DISTRIBUCION DE FRECUENCIAS
# ============================================================

titulo("FRECUENCIA DE INSPECCION DEL CLIENTE")

frecuencias = Counter(inspeccion)

tabla_frecuencia = pd.DataFrame({
    "Televisores inspeccionados": range(5),
    "Frecuencia": [frecuencias[i] for i in range(5)]
})

tabla_frecuencia["Porcentaje"] = (
    tabla_frecuencia["Frecuencia"] / len(inspeccion) * 100
)

print(tabla_frecuencia.to_string(index=False))


# ============================================================
# 6. SIMULACION MONTE CARLO
# ============================================================

titulo("INICIANDO SIMULACION MONTE CARLO")

print(f"Numero de simulaciones: {N_SIMULACIONES:,}")
print(f"Politicas evaluadas: {POLITICAS}")
print("Generando escenarios aleatorios...\n")

rng = np.random.default_rng(SEMILLA)

# Demanda diaria generada a partir de los datos historicos.
demanda_simulada = rng.choice(
    demanda,
    size=N_SIMULACIONES,
    replace=True
)

# Cantidad de televisores inspeccionados por el cliente.
inspeccion_simulada = rng.choice(
    inspeccion,
    size=N_SIMULACIONES,
    replace=True
)

# Defectos encontrados por el cliente.
defectos_cliente = rng.binomial(
    inspeccion_simulada,
    PROB_DEFECTO_CLIENTE
)

resultados = []
costos_simulados = {}

# ============================================================
# 7. EVALUACION DE CADA POLITICA
# ============================================================

for Q in POLITICAS:

    # Defectos generados durante la fabricacion.
    defectos_fabrica = rng.binomial(
        Q,
        PROB_DEFECTO_FABRICA,
        size=N_SIMULACIONES
    )

    # Produccion que realmente puede venderse.
    produccion_utilizable = Q - defectos_fabrica

    # Cantidad de televisores faltantes.
    faltantes = np.maximum(
        demanda_simulada - produccion_utilizable,
        0
    )

    # Inventario sobrante.
    sobrantes = np.maximum(
        produccion_utilizable - demanda_simulada,
        0
    )

    # Costos individuales.
    costo_fabrica = (
        defectos_fabrica * COSTO_DEFECTO_FABRICA
    )

    costo_faltantes = (
        faltantes * COSTO_FALTANTE
    )

    costo_inventario = (
        sobrantes * COSTO_INVENTARIO
    )

    costo_cliente = (
        defectos_cliente * COSTO_DEFECTO_CLIENTE
    )

    # Costo total diario.
    costo_total = (
        costo_fabrica
        + costo_faltantes
        + costo_inventario
        + costo_cliente
    )

    costos_simulados[Q] = costo_total

    # Estadisticas.
    promedio = np.mean(costo_total)

    inferior, superior, desviacion, error = (
        intervalo_confianza(costo_total)
    )

    resultados.append({
        "Produccion": Q,
        "Costo promedio": promedio,
        "Desviacion estandar": desviacion,
        "Error estandar": error,
        "IC inferior": inferior,
        "IC superior": superior,
        "Costo fabrica": np.mean(costo_fabrica),
        "Costo faltantes": np.mean(costo_faltantes),
        "Costo inventario": np.mean(costo_inventario),
        "Costo cliente": np.mean(costo_cliente),
        "Demanda media": np.mean(demanda_simulada),
        "Oferta utilizable": np.mean(produccion_utilizable),
        "Faltantes medios": np.mean(faltantes),
        "Inventario medio": np.mean(sobrantes)
    })

    print(f"Politica de {Q} televisores: simulacion completada.")


# ============================================================
# 8. TABLA GENERAL DE RESULTADOS
# ============================================================

df = pd.DataFrame(resultados)

titulo("RESULTADOS GENERALES DE LAS POLITICAS")

tabla_general = df[
    [
        "Produccion",
        "Costo promedio",
        "IC inferior",
        "IC superior",
        "Desviacion estandar"
    ]
].copy()

print(
    tabla_general.to_string(
        index=False,
        formatters={
            "Costo promedio": "${:,.2f}".format,
            "IC inferior": "${:,.2f}".format,
            "IC superior": "${:,.2f}".format,
            "Desviacion estandar": "${:,.2f}".format
        }
    )
)


# ============================================================
# 9. DESCOMPOSICION DE COSTOS
# ============================================================

titulo("DESCOMPOSICION DEL COSTO PROMEDIO DIARIO")

columnas_costos = [
    "Costo fabrica",
    "Costo faltantes",
    "Costo inventario",
    "Costo cliente"
]

tabla_costos = df[["Produccion"] + columnas_costos].copy()

print(
    tabla_costos.to_string(
        index=False,
        formatters={
            col: "${:,.2f}".format
            for col in columnas_costos
        }
    )
)


# ============================================================
# 10. DETERMINACION DE LA POLITICA OPTIMA
# ============================================================

indice_optimo = df["Costo promedio"].idxmin()

mejor = df.loc[indice_optimo]

Q_optimo = int(mejor["Produccion"])

titulo("DETERMINACION DE LA POLITICA OPTIMA")

print(f"\nProduccion recomendada: {Q_optimo} televisores diarios")

print(f"Costo promedio: ${mejor['Costo promedio']:,.2f}")

print(
    f"Intervalo de confianza 95%: "
    f"[${mejor['IC inferior']:,.2f}, "
    f"${mejor['IC superior']:,.2f}]"
)

print("\nComparacion frente a las otras politicas:")

for _, fila in df.iterrows():

    diferencia = (
        fila["Costo promedio"] - mejor["Costo promedio"]
    )

    print(
        f"Produccion {int(fila['Produccion'])}: "
        f"${fila['Costo promedio']:,.2f} "
        f"(diferencia: ${diferencia:,.2f})"
    )


# ============================================================
# 11. EXPORTACION DE RESULTADOS
# ============================================================

titulo("EXPORTACION DE RESULTADOS")

df.to_csv(
    "resultados_politicas.csv",
    index=False,
    encoding="utf-8-sig"
)

tabla_frecuencia.to_csv(
    "frecuencia_inspeccion.csv",
    index=False,
    encoding="utf-8-sig"
)

estadisticas_demanda = pd.DataFrame({
    "Indicador": [
        "Observaciones",
        "Media",
        "Mediana",
        "Desviacion estandar",
        "Minimo",
        "Maximo"
    ],
    "Demanda": [
        len(demanda),
        np.mean(demanda),
        np.median(demanda),
        np.std(demanda, ddof=1),
        np.min(demanda),
        np.max(demanda)
    ]
})

with pd.ExcelWriter(
    "analisis_televisores.xlsx",
    engine="openpyxl"
) as writer:

    df.to_excel(
        writer,
        sheet_name="Politicas",
        index=False
    )

    estadisticas_demanda.to_excel(
        writer,
        sheet_name="Demanda",
        index=False
    )

    tabla_frecuencia.to_excel(
        writer,
        sheet_name="Inspeccion",
        index=False
    )

print("Archivo CSV generado correctamente.")
print("Archivo Excel generado correctamente.")


# ============================================================
# 12. VISUALIZACIONES CON MATPLOTLIB
# ============================================================

titulo("GENERANDO GRAFICOS ESTADISTICOS")

# GRAFICO 1: Distribucion de demanda.

plt.figure(figsize=(10, 5))

plt.hist(
    demanda,
    bins=np.arange(59.5, 101.5, 2),
    edgecolor="black"
)

plt.axvline(
    np.mean(demanda),
    linestyle="--",
    label=f"Media: {np.mean(demanda):.2f}"
)

plt.title("Distribucion historica de la demanda")
plt.xlabel("Televisores demandados por dia")
plt.ylabel("Frecuencia")
plt.legend()
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

plt.savefig("grafico_demanda.png", dpi=150)


# GRAFICO 2: Frecuencia de inspeccion.

plt.figure(figsize=(9, 5))

plt.bar(
    tabla_frecuencia["Televisores inspeccionados"],
    tabla_frecuencia["Frecuencia"],
    edgecolor="black"
)

plt.title("Distribucion de inspecciones del cliente")
plt.xlabel("Televisores inspeccionados")
plt.ylabel("Frecuencia")
plt.xticks(range(5))
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

plt.savefig("grafico_inspeccion.png", dpi=150)


# GRAFICO 3: Comparacion de costos.

plt.figure(figsize=(10, 5))

x = df["Produccion"]
medias = df["Costo promedio"]

errores = [
    medias - df["IC inferior"],
    df["IC superior"] - medias
]

plt.errorbar(
    x,
    medias,
    yerr=errores,
    fmt="o-",
    capsize=5,
    linewidth=2,
    label="Costo promedio e IC 95%"
)

plt.axvline(
    Q_optimo,
    linestyle="--",
    label=f"Politica optima: {Q_optimo}"
)

plt.title("Comparacion del costo promedio por politica")
plt.xlabel("Produccion diaria")
plt.ylabel("Costo promedio ($/dia)")
plt.xticks(POLITICAS)
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig("grafico_costos.png", dpi=150)


# GRAFICO 4: Composicion de costos.

plt.figure(figsize=(10, 6))

plt.bar(
    df["Produccion"].astype(str),
    df["Costo fabrica"],
    label="Defectos de fabrica"
)

plt.bar(
    df["Produccion"].astype(str),
    df["Costo faltantes"],
    bottom=df["Costo fabrica"],
    label="Faltantes"
)

base = df["Costo fabrica"] + df["Costo faltantes"]

plt.bar(
    df["Produccion"].astype(str),
    df["Costo inventario"],
    bottom=base,
    label="Inventario"
)

base = base + df["Costo inventario"]

plt.bar(
    df["Produccion"].astype(str),
    df["Costo cliente"],
    bottom=base,
    label="Defectos del cliente"
)

plt.title("Composicion del costo total por politica")
plt.xlabel("Produccion diaria")
plt.ylabel("Costo promedio ($/dia)")
plt.legend()
plt.tight_layout()

plt.savefig("grafico_composicion.png", dpi=150)


# Mostrar todos los graficos.
plt.show()


# ============================================================
# 13. INFORME FINAL EN TERMINAL
# ============================================================

titulo("INFORME FINAL DEL PROBLEMA 22")

print("""
OBJETIVO:
Determinar la cantidad optima de televisores que debe
fabricar diariamente la empresa, minimizando sus costos.
""")

print("DATOS PRINCIPALES:")
print(f"- Demanda historica: {len(demanda)} observaciones.")
print(f"- Demanda promedio: {np.mean(demanda):.2f} televisores.")
print(f"- Inspecciones historicas: {len(inspeccion)} observaciones.")
print(f"- Simulaciones realizadas: {N_SIMULACIONES:,} por politica.")
print(f"- Politicas evaluadas: {POLITICAS}")

print("\nRESULTADO DE LA EVALUACION:")

print(
    f"\nLa politica de menor costo es producir "
    f"{Q_optimo} televisores diarios."
)

print(
    f"Costo promedio estimado: "
    f"${mejor['Costo promedio']:,.2f} por dia."
)

print(
    f"Intervalo de confianza del 95%: "
    f"[${mejor['IC inferior']:,.2f}, "
    f"${mejor['IC superior']:,.2f}]."
)

print("\nCONCLUSION:")

print(
    f"La empresa debe implementar una politica de "
    f"produccion de {Q_optimo} televisores diarios, "
    f"ya que presenta el menor costo promedio entre "
    f"las cinco alternativas evaluadas."
)

print("\nARCHIVOS GENERADOS:")
print("- resultados_politicas.csv")
print("- frecuencia_inspeccion.csv")
print("- analisis_televisores.xlsx")
print("- grafico_demanda.png")
print("- grafico_inspeccion.png")
print("- grafico_costos.png")
print("- grafico_composicion.png")

titulo("FIN DEL ANALISIS")
