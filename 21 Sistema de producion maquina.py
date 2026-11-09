# ============================================================
# SIMULACION DE PRODUCCION, FALLAS Y MANTENIMIENTO
# MAQUINA INDUSTRIAL - 300 DIAS
# Metodo: Simulacion de Monte Carlo
# ============================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, Image, PageBreak
)
from reportlab.lib.units import cm

# ============================================================
# 1. PARAMETROS DEL PROBLEMA
# ============================================================

SEMILLA = 42
DIAS = 300

PRODUCCION_NORMAL = 1000
HORAS_DIA = 24

PROBABILIDAD_FALLA = 0.80

PRECIO_VENTA = 100
COSTO_REPARACION = 11

TIPOS_FALLA = ["Leve", "Moderada", "Grave", "Fatal"]

# Probabilidades calculadas de los registros historicos
PROBABILIDADES = np.array([10, 15, 25, 35]) / 85

rng = np.random.default_rng(SEMILLA)


# ============================================================
# 2. FUNCIONES DE GENERACION DE TIEMPOS DE REPARACION
# ============================================================

def tiempo_reparacion(tipo):

    if tipo == "Leve":

        # Erlang de orden 4, media 4 horas
        return rng.gamma(shape=4, scale=1)

    elif tipo == "Moderada":

        # Normal: media 3.5 y desviacion 1.1
        # Se rechazan valores negativos
        t = rng.normal(3.5, 1.1)

        while t < 0:
            t = rng.normal(3.5, 1.1)

        return t

    elif tipo == "Grave":

        # Distribucion f(t) = t - 6
        # Intervalo: 6 <= t <= 6 + raiz(2)
        u = rng.random()

        return 6 + np.sqrt(2 * u)

    elif tipo == "Fatal":

        # Exponencial con lambda = 0.2
        return rng.exponential(scale=1 / 0.2)


# ============================================================
# 3. SIMULACION DE LOS 300 DIAS
# ============================================================

resultados = []

for dia in range(1, DIAS + 1):

    # Determinar si ocurre una falla
    falla = rng.random() < PROBABILIDAD_FALLA

    if falla:

        # Seleccionar tipo de falla
        tipo = rng.choice(
            TIPOS_FALLA,
            p=PROBABILIDADES
        )

        # Generar tiempo de reparacion
        tiempo = tiempo_reparacion(tipo)

    else:

        tipo = "Sin falla"
        tiempo = 0

    # Tiempo de parada limitado a una jornada
    tiempo_parada = min(tiempo, HORAS_DIA)

    # ========================================================
    # 4. CALCULOS DE PRODUCCION Y ECONOMICOS
    # ========================================================

    produccion = PRODUCCION_NORMAL * (
        1 - tiempo_parada / HORAS_DIA
    )

    ingresos = produccion * PRECIO_VENTA

    costo = tiempo_parada * COSTO_REPARACION

    utilidad = ingresos - costo

    resultados.append({

        "Dia": dia,
        "Falla": falla,
        "Tipo de falla": tipo,
        "Tiempo reparacion": tiempo,
        "Tiempo parada": tiempo_parada,
        "Produccion": produccion,
        "Ingresos": ingresos,
        "Costo reparacion": costo,
        "Utilidad": utilidad

    })


# Convertir resultados en DataFrame
df = pd.DataFrame(resultados)


# ============================================================
# 5. INDICADORES GENERALES
# ============================================================

dias_con_falla = df["Falla"].sum()

produccion_total = df["Produccion"].sum()

produccion_promedio = df["Produccion"].mean()

ingresos_totales = df["Ingresos"].sum()

ingresos_promedio = df["Ingresos"].mean()

costos_totales = df["Costo reparacion"].sum()

costos_promedio = df["Costo reparacion"].mean()

utilidad_total = df["Utilidad"].sum()

utilidad_promedio = df["Utilidad"].mean()

produccion_maxima = PRODUCCION_NORMAL * DIAS

perdida_produccion = produccion_maxima - produccion_total


# ============================================================
# 6. RESULTADOS POR TIPO DE FALLA
# ============================================================

frecuencia = (
    df[df["Falla"]]["Tipo de falla"]
    .value_counts()
    .reindex(TIPOS_FALLA, fill_value=0)
)

print("\n==============================================")
print(" RESULTADOS DE LA SIMULACION - 300 DIAS")
print("==============================================")

print(f"Dias simulados: {DIAS}")

print(
    f"Dias con fallas: {dias_con_falla}"
)

print(
    f"Porcentaje de fallas: "
    f"{dias_con_falla / DIAS * 100:.2f}%"
)

print("\n--- PRODUCCION ---")

print(
    f"Produccion total: "
    f"{produccion_total:,.2f} piezas"
)

print(
    f"Produccion promedio diaria: "
    f"{produccion_promedio:,.2f} piezas"
)

print(
    f"Perdida de produccion: "
    f"{perdida_produccion:,.2f} piezas"
)

print("\n--- INGRESOS Y COSTOS ---")

print(
    f"Ingresos totales: "
    f"${ingresos_totales:,.2f}"
)

print(
    f"Ingresos promedio diarios: "
    f"${ingresos_promedio:,.2f}"
)

print(
    f"Costos totales de reparacion: "
    f"${costos_totales:,.2f}"
)

print(
    f"Costos promedio diarios: "
    f"${costos_promedio:,.2f}"
)

print("\n--- UTILIDAD ---")

print(
    f"Utilidad total: "
    f"${utilidad_total:,.2f}"
)

print(
    f"Utilidad promedio diaria: "
    f"${utilidad_promedio:,.2f}"
)

print("\n--- FRECUENCIA DE FALLAS ---")

print(frecuencia)


# ============================================================
# 7. GRAFICO DE PRODUCCION DIARIA
# ============================================================

plt.figure(figsize=(10, 5))

plt.plot(
    df["Dia"],
    df["Produccion"],
    label="Produccion diaria"
)

plt.axhline(
    produccion_promedio,
    linestyle="--",
    label=f"Promedio: {produccion_promedio:.2f}"
)

plt.axhline(
    PRODUCCION_NORMAL,
    linestyle=":",
    label="Produccion normal"
)

plt.title("Produccion diaria durante 300 dias")

plt.xlabel("Dias")

plt.ylabel("Piezas producidas")

plt.legend()

plt.grid(alpha=0.3)

plt.tight_layout()

plt.savefig("produccion.png", dpi=150)

plt.close()


# ============================================================
# 8. GRAFICO DE UTILIDAD DIARIA
# ============================================================

plt.figure(figsize=(10, 5))

plt.plot(
    df["Dia"],
    df["Utilidad"],
    label="Utilidad diaria"
)

plt.axhline(
    utilidad_promedio,
    linestyle="--",
    label=f"Promedio: ${utilidad_promedio:,.2f}"
)

plt.title("Utilidad diaria durante 300 dias")

plt.xlabel("Dias")

plt.ylabel("Utilidad en dolares")

plt.legend()

plt.grid(alpha=0.3)

plt.tight_layout()

plt.savefig("utilidad.png", dpi=150)

plt.close()


# ============================================================
# 9. GRAFICO DE TIPOS DE FALLA
# ============================================================

plt.figure(figsize=(9, 5))

plt.bar(
    frecuencia.index,
    frecuencia.values
)

plt.title("Frecuencia de tipos de falla")

plt.xlabel("Tipo de falla")

plt.ylabel("Cantidad de fallas")

plt.grid(axis="y", alpha=0.3)

plt.tight_layout()

plt.savefig("fallas.png", dpi=150)

plt.close()


# ============================================================
# 10. GRAFICO DE TIEMPOS DE REPARACION
# ============================================================

plt.figure(figsize=(9, 5))

for tipo in TIPOS_FALLA:

    datos = df[
        df["Tipo de falla"] == tipo
    ]["Tiempo reparacion"]

    if len(datos) > 0:

        plt.hist(
            datos,
            bins=15,
            alpha=0.5,
            label=tipo
        )

plt.title("Distribucion de tiempos de reparacion")

plt.xlabel("Horas")

plt.ylabel("Frecuencia")

plt.legend()

plt.tight_layout()

plt.savefig("tiempos_reparacion.png", dpi=150)

plt.close()


# ============================================================
# 11. EXPORTAR RESULTADOS A EXCEL Y CSV
# ============================================================

df.to_csv(
    "resultados_300_dias.csv",
    index=False
)

df.to_excel(
    "resultados_300_dias.xlsx",
    index=False
)


# ============================================================
# 12. GENERAR INFORME PDF
# ============================================================

archivo_pdf = "Informe_Final_Maquina.pdf"

documento = SimpleDocTemplate(
    archivo_pdf,
    pagesize=A4,
    rightMargin=1.5 * cm,
    leftMargin=1.5 * cm,
    topMargin=1.5 * cm,
    bottomMargin=1.5 * cm
)

estilos = getSampleStyleSheet()

contenido = []

contenido.append(
    Paragraph(
        "INFORME TECNICO",
        estilos["Title"]
    )
)

contenido.append(
    Paragraph(
        "Simulacion de produccion, fallas y mantenimiento "
        "de una maquina industrial",
        estilos["Heading2"]
    )
)

contenido.append(Spacer(1, 15))


# ------------------------------------------------------------
# OBJETIVO
# ------------------------------------------------------------

contenido.append(
    Paragraph(
        "1. OBJETIVO",
        estilos["Heading2"]
    )
)

contenido.append(
    Paragraph(
        "Evaluar el comportamiento de una maquina industrial "
        "durante 300 dias mediante simulacion de Monte Carlo, "
        "considerando la probabilidad de falla, los tipos de "
        "averias, sus tiempos de reparacion y los costos "
        "economicos asociados.",
        estilos["BodyText"]
    )
)

contenido.append(Spacer(1, 12))


# ------------------------------------------------------------
# DATOS
# ------------------------------------------------------------

contenido.append(
    Paragraph(
        "2. DATOS DEL PROBLEMA",
        estilos["Heading2"]
    )
)

tabla_datos = [

    ["Parametro", "Valor"],

    ["Produccion diaria", "1000 piezas"],

    ["Jornada laboral", "24 horas"],

    ["Probabilidad de falla", "0.80"],

    ["Precio por pieza", "$100"],

    ["Costo por hora", "$11"],

    ["Periodo", "300 dias"]

]

tabla = Table(tabla_datos, colWidths=[8*cm, 7*cm])

tabla.setStyle(
    TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),

        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),

        ("PADDING", (0, 0), (-1, -1), 7)

    ])
)

contenido.append(tabla)

contenido.append(Spacer(1, 12))


# ------------------------------------------------------------
# PROBABILIDADES
# ------------------------------------------------------------

contenido.append(
    Paragraph(
        "3. PROBABILIDADES DE FALLA",
        estilos["Heading2"]
    )
)

tabla_fallas = [
    ["Tipo", "Dias historicos", "Probabilidad"]
]

for tipo, cantidad in zip(
    TIPOS_FALLA,
    [10, 15, 25, 35]
):

    tabla_fallas.append([

        tipo,

        str(cantidad),

        f"{cantidad / 85 * 100:.2f}%"

    ])

tabla = Table(
    tabla_fallas,
    colWidths=[5*cm, 5*cm, 5*cm]
)

tabla.setStyle(
    TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),

        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),

        ("PADDING", (0, 0), (-1, -1), 7)

    ])
)

contenido.append(tabla)

contenido.append(Spacer(1, 12))


# ------------------------------------------------------------
# MODELO MATEMATICO
# ------------------------------------------------------------

contenido.append(
    Paragraph(
        "4. MODELO MATEMATICO",
        estilos["Heading2"]
    )
)

contenido.append(
    Paragraph(
        "La probabilidad de ocurrencia de una falla diaria "
        "es de 0.80. Cuando ocurre una falla, el tipo se "
        "selecciona utilizando las probabilidades historicas.",
        estilos["BodyText"]
    )
)

contenido.append(
    Paragraph(
        "Los tiempos de reparacion se generan mediante "
        "distribuciones Erlang, Normal, la distribucion "
        "definida para fallas graves y Exponencial.",
        estilos["BodyText"]
    )
)

contenido.append(Spacer(1, 8))

contenido.append(
    Paragraph(
        "Formulas utilizadas:",
        estilos["BodyText"]
    )
)

contenido.append(
    Paragraph(
        "Produccion = 1000 * (24 - T) / 24",
        estilos["BodyText"]
    )
)

contenido.append(
    Paragraph(
        "Ingresos = Produccion * 100",
        estilos["BodyText"]
    )
)

contenido.append(
    Paragraph(
        "Costo = T * 11",
        estilos["BodyText"]
    )
)

contenido.append(
    Paragraph(
        "Utilidad = Ingresos - Costo",
        estilos["BodyText"]
    )
)

contenido.append(
    Paragraph(
        "T representa las horas de parada imputadas a la jornada, "
        "limitadas a un maximo de 24 horas. Se supone una "
        "falla como maximo por jornada y no se arrastran "
        "reparaciones entre dias.",
        estilos["BodyText"]
    )
)

contenido.append(Spacer(1, 12))


# ------------------------------------------------------------
# RESULTADOS
# ------------------------------------------------------------

contenido.append(
    Paragraph(
        "5. RESULTADOS DE LA SIMULACION",
        estilos["Heading2"]
    )
)

tabla_resultados = [

    ["Indicador", "Resultado"],

    ["Dias simulados", str(DIAS)],

    ["Dias con falla", str(dias_con_falla)],

    ["Produccion total",
     f"{produccion_total:,.2f} piezas"],

    ["Produccion promedio diaria",
     f"{produccion_promedio:,.2f} piezas"],

    ["Ingresos totales",
     f"${ingresos_totales:,.2f}"],

    ["Costo total",
     f"${costos_totales:,.2f}"],

    ["Utilidad promedio diaria",
     f"${utilidad_promedio:,.2f}"],

    ["Utilidad acumulada",
     f"${utilidad_total:,.2f}"]

]

tabla = Table(
    tabla_resultados,
    colWidths=[8*cm, 7*cm]
)

tabla.setStyle(
    TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),

        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),

        ("PADDING", (0, 0), (-1, -1), 7)

    ])
)

contenido.append(tabla)

contenido.append(Spacer(1, 12))


# ------------------------------------------------------------
# GRAFICOS
# ------------------------------------------------------------

contenido.append(
    Paragraph(
        "6. GRAFICOS DE RESULTADOS",
        estilos["Heading2"]
    )
)

for grafico in [

    "produccion.png",

    "utilidad.png",

    "fallas.png",

    "tiempos_reparacion.png"

]:

    contenido.append(
        Image(
            grafico,
            width=16*cm,
            height=8*cm
        )
    )

    contenido.append(Spacer(1, 10))


# ------------------------------------------------------------
# CONCLUSIONES
# ------------------------------------------------------------

contenido.append(PageBreak())

contenido.append(
    Paragraph(
        "7. CONCLUSIONES",
        estilos["Heading2"]
    )
)

conclusion = f"""
Durante los 300 dias simulados, la maquina presento
{dias_con_falla} dias con fallas, equivalente a un
{dias_con_falla / DIAS * 100:.2f}% de las jornadas.

La produccion total fue de {produccion_total:,.2f}
piezas, con un promedio diario de
{produccion_promedio:,.2f} piezas.

Los ingresos acumulados alcanzaron
${ingresos_totales:,.2f}, mientras que los costos
de reparacion fueron de ${costos_totales:,.2f}.

La utilidad promedio diaria fue de
${utilidad_promedio:,.2f}, y la utilidad total
durante los 300 dias fue de ${utilidad_total:,.2f}.

Se concluye que las fallas afectan directamente
la capacidad productiva y economica de la maquina.
Por ello, resulta importante implementar estrategias
de mantenimiento preventivo, especialmente para
los tipos de falla con mayor frecuencia historica.
"""

contenido.append(
    Paragraph(
        conclusion,
        estilos["BodyText"]
    )
)

contenido.append(Spacer(1, 15))

contenido.append(
    Paragraph(
        "8. CONSIDERACIONES DE LA SIMULACION",
        estilos["Heading2"]
    )
)

contenido.append(
    Paragraph(
        "Los resultados corresponden a una realizacion "
        "aleatoria reproducible con semilla 42. Los "
        "resultados pueden variar si se modifica la semilla. "
        "Los tiempos de reparacion superiores a 24 horas "
        "se limitan a una jornada para calcular produccion "
        "y costo diario. El modelo no representa el "
        "arrastre de una reparacion hacia dias posteriores.",
        estilos["BodyText"]
    )
)


# ============================================================
# 13. CREAR DOCUMENTO FINAL
# ============================================================

documento.build(contenido)


# ============================================================
# 14. FINALIZACION
# ============================================================

print("\n==============================================")
print(" SIMULACION FINALIZADA CORRECTAMENTE")
print("==============================================")

print("\nArchivos generados:")

print("1. Informe_Final_Maquina.pdf")

print("2. resultados_300_dias.csv")

print("3. resultados_300_dias.xlsx")

print("4. produccion.png")

print("5. utilidad.png")

print("6. fallas.png")

print("7. tiempos_reparacion.png")

print("\nTodos los resultados corresponden a la")
print("simulacion de Monte Carlo de 300 dias.")
