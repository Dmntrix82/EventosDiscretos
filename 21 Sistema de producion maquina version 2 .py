import os, textwrap, subprocess, sys, zipfile, pathlib, json, shutil

workdir = "/mnt/data/simulacion_maquina"
os.makedirs(workdir, exist_ok=True)

script = r'''# ============================================================
# SIMULACION DE PRODUCCION, FALLAS Y MANTENIMIENTO
# MAQUINA INDUSTRIAL - 300 DIAS
# Metodo: Simulacion de Monte Carlo
# ============================================================
#
# INSTALACION:
#   pip install numpy pandas matplotlib reportlab openpyxl
#
# EJECUCION:
#   python simulacion_maquina.py
#
# SALIDAS (carpeta resultados/):
#   - Informe_Final_Maquina.pdf
#   - resultados_300_dias.xlsx
#   - resultados_300_dias.csv
#   - produccion.png
#   - utilidad.png
#   - fallas.png
#   - tiempos_reparacion.png
# ============================================================

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib

# Permite ejecutar el programa en equipos sin interfaz gráfica.
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, Image, PageBreak, KeepTogether
)
from reportlab.lib.units import cm


# ============================================================
# 1. CONFIGURACION Y PARAMETROS
# ============================================================

SEMILLA = 42
DIAS = 300

PRODUCCION_NORMAL = 1000.0       # piezas por jornada
HORAS_DIA = 24.0                 # horas por jornada
PROBABILIDAD_FALLA = 0.80

PRECIO_VENTA = 100.0             # dinero por pieza
COSTO_REPARACION = 11.0          # dinero por hora de parada

TIPOS_FALLA = ["Leve", "Moderada", "Grave", "Fatal"]
FRECUENCIAS_HISTORICAS = np.array([10, 15, 25, 35], dtype=float)

CARPETA_SALIDA = Path("resultados")
CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)


def validar_parametros():
    """Comprueba que la configuración sea válida antes de simular."""
    if not isinstance(DIAS, int) or DIAS <= 0:
        raise ValueError("DIAS debe ser un entero mayor que cero.")
    if PRODUCCION_NORMAL < 0 or HORAS_DIA <= 0:
        raise ValueError("La producción debe ser >= 0 y las horas > 0.")
    if not 0 <= PROBABILIDAD_FALLA <= 1:
        raise ValueError("PROBABILIDAD_FALLA debe estar entre 0 y 1.")
    if PRECIO_VENTA < 0 or COSTO_REPARACION < 0:
        raise ValueError("Los precios y costos no pueden ser negativos.")
    if len(FRECUENCIAS_HISTORICAS) != len(TIPOS_FALLA):
        raise ValueError("Debe existir una frecuencia histórica por tipo de falla.")
    if np.any(FRECUENCIAS_HISTORICAS < 0) or FRECUENCIAS_HISTORICAS.sum() <= 0:
        raise ValueError("Las frecuencias históricas deben ser no negativas y sumar más de cero.")


validar_parametros()
PROBABILIDADES = FRECUENCIAS_HISTORICAS / FRECUENCIAS_HISTORICAS.sum()
rng = np.random.default_rng(SEMILLA)


# ============================================================
# 2. GENERACION DE TIEMPOS DE REPARACION
# ============================================================

def tiempo_reparacion(tipo, generador=rng):
    """
    Genera el tiempo de reparación en horas según el tipo de falla.

    Leve: Erlang/Gamma, k=4 y escala=1 (media 4 horas).
    Moderada: Normal(3.5, 1.1), rechazando valores negativos.
    Grave: densidad f(t)=t-6 en [6, 6+sqrt(2)].
    Fatal: Exponencial con lambda=0.2 (media 5 horas).
    """
    if tipo == "Leve":
        return float(generador.gamma(shape=4, scale=1))

    if tipo == "Moderada":
        # Método de rechazo: el tiempo nunca puede ser negativo.
        tiempo = generador.normal(loc=3.5, scale=1.1)
        while tiempo < 0:
            tiempo = generador.normal(loc=3.5, scale=1.1)
        return float(tiempo)

    if tipo == "Grave":
        # Inversa de F(t)=(t-6)^2/2 para 6 <= t <= 6+sqrt(2).
        u = generador.random()
        return float(6 + np.sqrt(2 * u))

    if tipo == "Fatal":
        return float(generador.exponential(scale=1 / 0.2))

    raise ValueError(f"Tipo de falla desconocido: {tipo}")


# ============================================================
# 3. SIMULACION
# ============================================================

def ejecutar_simulacion():
    registros = []

    for dia in range(1, DIAS + 1):
        hay_falla = bool(rng.random() < PROBABILIDAD_FALLA)

        if hay_falla:
            tipo = str(rng.choice(TIPOS_FALLA, p=PROBABILIDADES))
            tiempo = tiempo_reparacion(tipo)
        else:
            tipo = "Sin falla"
            tiempo = 0.0

        # El modelo contabiliza como máximo una jornada de parada.
        tiempo_parada = min(tiempo, HORAS_DIA)
        tiempo_operacion = HORAS_DIA - tiempo_parada

        produccion = PRODUCCION_NORMAL * (tiempo_operacion / HORAS_DIA)
        perdida_produccion_dia = PRODUCCION_NORMAL - produccion
        ingresos = produccion * PRECIO_VENTA
        costo = tiempo_parada * COSTO_REPARACION
        utilidad = ingresos - costo

        registros.append({
            "Dia": dia,
            "Falla": hay_falla,
            "Tipo de falla": tipo,
            "Tiempo reparacion (h)": tiempo,
            "Tiempo parada (h)": tiempo_parada,
            "Tiempo operativo (h)": tiempo_operacion,
            "Produccion (piezas)": produccion,
            "Perdida produccion (piezas)": perdida_produccion_dia,
            "Ingresos": ingresos,
            "Costo reparacion": costo,
            "Utilidad": utilidad,
        })

    return pd.DataFrame(registros)


# ============================================================
# 4. INDICADORES Y RESUMENES
# ============================================================

def calcular_indicadores(df):
    dias_con_falla = int(df["Falla"].sum())
    dias_sin_falla = DIAS - dias_con_falla

    produccion_total = float(df["Produccion (piezas)"].sum())
    produccion_maxima = PRODUCCION_NORMAL * DIAS
    perdida_produccion = produccion_maxima - produccion_total

    ingresos_totales = float(df["Ingresos"].sum())
    costos_totales = float(df["Costo reparacion"].sum())
    utilidad_total = float(df["Utilidad"].sum())

    horas_parada = float(df["Tiempo parada (h)"].sum())
    horas_operativas = float(df["Tiempo operativo (h)"].sum())
    horas_disponibles = HORAS_DIA * DIAS
    disponibilidad = (horas_operativas / horas_disponibles * 100) if horas_disponibles else 0

    indicadores = {
        "Días simulados": DIAS,
        "Días con falla": dias_con_falla,
        "Días sin falla": dias_sin_falla,
        "Porcentaje de días con falla (%)": dias_con_falla / DIAS * 100,
        "Producción máxima teórica (piezas)": produccion_maxima,
        "Producción total (piezas)": produccion_total,
        "Producción promedio diaria (piezas)": produccion_total / DIAS,
        "Pérdida de producción (piezas)": perdida_produccion,
        "Ingresos totales": ingresos_totales,
        "Ingresos promedio diarios": ingresos_totales / DIAS,
        "Costos totales de reparación": costos_totales,
        "Costos promedio diarios": costos_totales / DIAS,
        "Utilidad total": utilidad_total,
        "Utilidad promedio diaria": utilidad_total / DIAS,
        "Horas totales de parada": horas_parada,
        "Horas operativas": horas_operativas,
        "Disponibilidad (%)": disponibilidad,
    }

    frecuencia = (
        df.loc[df["Falla"], "Tipo de falla"]
        .value_counts()
        .reindex(TIPOS_FALLA, fill_value=0)
        .rename_axis("Tipo de falla")
        .reset_index(name="Cantidad")
    )
    frecuencia["Porcentaje de fallas (%)"] = (
        frecuencia["Cantidad"] / max(dias_con_falla, 1) * 100
    )

    return indicadores, frecuencia


# ============================================================
# 5. GRAFICOS
# ============================================================

def generar_graficos(df, frecuencia):
    rutas = {}

    # Producción diaria
    ruta = CARPETA_SALIDA / "produccion.png"
    plt.figure(figsize=(10, 5))
    plt.plot(df["Dia"], df["Produccion (piezas)"], label="Producción diaria", linewidth=1.5)
    plt.axhline(df["Produccion (piezas)"].mean(), linestyle="--",
                label=f"Promedio: {df['Produccion (piezas)'].mean():.2f}")
    plt.axhline(PRODUCCION_NORMAL, linestyle=":", label="Producción normal")
    plt.title(f"Producción diaria durante {DIAS} días")
    plt.xlabel("Día")
    plt.ylabel("Piezas producidas")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(ruta, dpi=160)
    plt.close()
    rutas["produccion"] = ruta

    # Utilidad diaria
    ruta = CARPETA_SALIDA / "utilidad.png"
    plt.figure(figsize=(10, 5))
    plt.plot(df["Dia"], df["Utilidad"], label="Utilidad diaria", linewidth=1.5)
    plt.axhline(df["Utilidad"].mean(), linestyle="--",
                label=f"Promedio: ${df['Utilidad'].mean():,.2f}")
    plt.title(f"Utilidad diaria durante {DIAS} días")
    plt.xlabel("Día")
    plt.ylabel("Utilidad")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(ruta, dpi=160)
    plt.close()
    rutas["utilidad"] = ruta

    # Frecuencia de fallas
    ruta = CARPETA_SALIDA / "fallas.png"
    plt.figure(figsize=(9, 5))
    plt.bar(frecuencia["Tipo de falla"], frecuencia["Cantidad"])
    plt.title("Frecuencia de tipos de falla")
    plt.xlabel("Tipo de falla")
    plt.ylabel("Cantidad de fallas")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(ruta, dpi=160)
    plt.close()
    rutas["fallas"] = ruta

    # Tiempos de reparación
    ruta = CARPETA_SALIDA / "tiempos_reparacion.png"
    plt.figure(figsize=(9, 5))
    for tipo in TIPOS_FALLA:
        datos = df.loc[df["Tipo de falla"] == tipo, "Tiempo reparacion (h)"]
        if not datos.empty:
            plt.hist(datos, bins=15, alpha=0.5, label=tipo)
    plt.title("Distribución de tiempos de reparación")
    plt.xlabel("Horas de reparación")
    plt.ylabel("Frecuencia")
    plt.legend()
    plt.grid(alpha=0.2)
    plt.tight_layout()
    plt.savefig(ruta, dpi=160)
    plt.close()
    rutas["tiempos"] = ruta

    return rutas


# ============================================================
# 6. EXPORTACION CSV Y EXCEL
# ============================================================

def exportar_datos(df, indicadores, frecuencia):
    ruta_csv = CARPETA_SALIDA / "resultados_300_dias.csv"
    ruta_excel = CARPETA_SALIDA / "resultados_300_dias.xlsx"

    df.to_csv(ruta_csv, index=False, encoding="utf-8-sig")

    resumen_df = pd.DataFrame({
        "Indicador": list(indicadores.keys()),
        "Resultado": list(indicadores.values())
    })

    with pd.ExcelWriter(ruta_excel, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Resultados diarios", index=False)
        resumen_df.to_excel(writer, sheet_name="Resumen", index=False)
        frecuencia.to_excel(writer, sheet_name="Frecuencia fallas", index=False)

        # Formato básico y legible en todas las hojas.
        from openpyxl.styles import Font, PatternFill, Alignment
        from openpyxl.utils import get_column_letter

        for ws in writer.book.worksheets:
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill("solid", fgColor="1F4E78")
                cell.alignment = Alignment(horizontal="center")
            for col in ws.columns:
                max_length = max(
                    len(str(cell.value)) if cell.value is not None else 0
                    for cell in col
                )
                ws.column_dimensions[get_column_letter(col[0].column)].width = min(max_length + 3, 34)

    return ruta_csv, ruta_excel


# ============================================================
# 7. GENERACION DEL INFORME PDF
# ============================================================

def generar_pdf(indicadores, frecuencia, rutas):
    ruta_pdf = CARPETA_SALIDA / "Informe_Final_Maquina.pdf"

    doc = SimpleDocTemplate(
        str(ruta_pdf),
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm
    )

    estilos = getSampleStyleSheet()
    estilos.add(ParagraphStyle(
        name="SubtituloCentrado",
        parent=estilos["Heading2"],
        alignment=TA_CENTER,
        spaceAfter=12
    ))

    contenido = [
        Paragraph("INFORME TÉCNICO", estilos["Title"]),
        Paragraph(
            "Simulación de producción, fallas y mantenimiento de una máquina industrial",
            estilos["SubtituloCentrado"]
        ),
        Spacer(1, 8),
        Paragraph("1. OBJETIVO", estilos["Heading2"]),
        Paragraph(
            f"Evaluar el comportamiento de una máquina industrial durante {DIAS} días "
            "mediante simulación de Monte Carlo, considerando la ocurrencia de fallas, "
            "los tipos de avería, sus tiempos de reparación y los costos económicos asociados.",
            estilos["BodyText"]
        ),
        Spacer(1, 10),
        Paragraph("2. PARÁMETROS DEL MODELO", estilos["Heading2"]),
    ]

    datos_parametros = [
        ["Parámetro", "Valor"],
        ["Días simulados", str(DIAS)],
        ["Producción normal", f"{PRODUCCION_NORMAL:,.0f} piezas/día"],
        ["Jornada", f"{HORAS_DIA:g} horas/día"],
        ["Probabilidad diaria de falla", f"{PROBABILIDAD_FALLA:.2%}"],
        ["Precio por pieza", f"${PRECIO_VENTA:,.2f}"],
        ["Costo por hora de reparación", f"${COSTO_REPARACION:,.2f}"],
        ["Semilla aleatoria", str(SEMILLA)],
    ]
    contenido.append(crear_tabla(datos_parametros, [8 * cm, 7 * cm]))
    contenido.extend([Spacer(1, 10), Paragraph("3. PROBABILIDADES HISTÓRICAS", estilos["Heading2"])])

    datos_fallas = [["Tipo", "Frecuencia histórica", "Probabilidad"]]
    for tipo, cantidad, prob in zip(TIPOS_FALLA, FRECUENCIAS_HISTORICAS, PROBABILIDADES):
        datos_fallas.append([tipo, f"{cantidad:g}", f"{prob:.2%}"])
    contenido.append(crear_tabla(datos_fallas, [5 * cm, 5 * cm, 5 * cm]))

    contenido.extend([
        Spacer(1, 10),
        Paragraph("4. MODELO MATEMÁTICO", estilos["Heading2"]),
        Paragraph(
            "Cada día se determina si ocurre una falla mediante una variable Bernoulli "
            f"con probabilidad p={PROBABILIDAD_FALLA:.2f}. Si ocurre, el tipo de falla se "
            "selecciona de acuerdo con las probabilidades históricas normalizadas.",
            estilos["BodyText"
            ]
        ),
        Paragraph(
            "Los tiempos de reparación se generan con las siguientes distribuciones: "
            "Leve: Gamma/Erlang (k=4, escala=1); Moderada: Normal (media 3.5 h, "
            "desviación 1.1 h) condicionada a valores no negativos; Grave: densidad "
            "f(t)=t−6 en [6, 6+√2]; Fatal: Exponencial (λ=0.2).",
            estilos["BodyText"]
        ),
        Paragraph(
            "La parada diaria se limita a 24 horas. La producción se calcula como "
            "Producción normal × (24 − horas de parada) / 24. Los ingresos son "
            "producción × precio unitario; el costo es horas de parada × costo por hora; "
            "la utilidad es ingresos menos costo. No se trasladan reparaciones entre días.",
            estilos["BodyText"]
        ),
        Spacer(1, 10),
        Paragraph("5. RESULTADOS GENERALES", estilos["Heading2"]),
    ])

    datos_resumen = [["Indicador", "Resultado"]]
    for clave, valor in indicadores.items():
        if isinstance(valor, (float, np.floating)):
            if "($)" in clave or "Ingresos" in clave or "Costos" in clave or "Utilidad" in clave:
                mostrado = f"${valor:,.2f}"
            elif "(%)" in clave:
                mostrado = f"{valor:.2f}%"
            else:
                mostrado = f"{valor:,.2f}"
        else:
            mostrado = str(valor)
        datos_resumen.append([clave, mostrado])

    contenido.append(crear_tabla(datos_resumen, [9 * cm, 6 * cm]))
    contenido.extend([Spacer(1, 10), Paragraph("6. FRECUENCIA DE FALLAS", estilos["Heading2"])])

    datos_frec = [["Tipo", "Cantidad", "Porcentaje de fallas"]]
    for _, fila in frecuencia.iterrows():
        datos_frec.append([
            fila["Tipo de falla"],
            str(int(fila["Cantidad"])),
            f'{fila["Porcentaje de fallas (%)"]:.2f}%'
        ])
    contenido.append(crear_tabla(datos_frec, [5 * cm, 5 * cm, 5 * cm]))

    contenido.extend([PageBreak(), Paragraph("7. GRÁFICOS DE RESULTADOS", estilos["Heading2"])])

    for clave, titulo in [
        ("produccion", "Producción diaria"),
        ("utilidad", "Utilidad diaria"),
        ("fallas", "Frecuencia de tipos de falla"),
        ("tiempos", "Tiempos de reparación"),
    ]:
        contenido.append(Paragraph(titulo, estilos["Heading3"]))
        contenido.append(Image(str(rutas[clave]), width=16 * cm, height=8 * cm))
        contenido.append(Spacer(1, 8))

    contenido.extend([
        PageBreak(),
        Paragraph("8. CONCLUSIONES", estilos["Heading2"]),
        Paragraph(
            f"Durante los {DIAS} días simulados se registraron {indicadores['Días con falla']} "
            f"días con fallas ({indicadores['Porcentaje de días con falla (%)']:.2f}%). "
            f"La producción acumulada fue de {indicadores['Producción total (piezas)']:,.2f} "
            f"piezas, frente a una producción teórica de "
            f"{indicadores['Producción máxima teórica (piezas)']:,.2f} piezas. "
            f"La pérdida estimada fue de {indicadores['Pérdida de producción (piezas)']:,.2f} piezas.",
            estilos["BodyText"]
        ),
        Spacer(1, 6),
        Paragraph(
            f"Los ingresos acumulados alcanzaron ${indicadores['Ingresos totales']:,.2f}, "
            f"los costos de reparación fueron ${indicadores['Costos totales de reparación']:,.2f} "
            f"y la utilidad acumulada fue ${indicadores['Utilidad total']:,.2f}. "
            f"La disponibilidad estimada de la máquina fue "
            f"{indicadores['Disponibilidad (%)']:.2f}%.",
            estilos["BodyText"]
        ),
        Spacer(1, 6),
        Paragraph(
            "Se recomienda priorizar el mantenimiento preventivo de los modos de falla "
            "más frecuentes y revisar periódicamente los tiempos reales de reparación para "
            "actualizar las distribuciones del modelo.",
            estilos["BodyText"]
        ),
        Spacer(1, 12),
        Paragraph("9. CONSIDERACIONES Y LIMITACIONES", estilos["Heading2"]),
        Paragraph(
            "Los resultados corresponden a una única ejecución reproducible con la semilla "
            f"{SEMILLA}. La probabilidad de tipo de falla se obtiene de los conteos históricos "
            f"{FRECUENCIAS_HISTORICAS.astype(int).tolist()}. Se supone como máximo una ocurrencia "
            "de falla por jornada. Las reparaciones superiores a la jornada se limitan a "
            f"{HORAS_DIA:g} horas para los cálculos diarios y no se arrastran al día siguiente. "
            "El modelo no incorpora inventarios, turnos parciales, costos fijos, demanda, "
            "repuestos ni fallas múltiples dentro de un mismo día.",
            estilos["BodyText"]
        ),
    ])

    doc.build(contenido)
    return ruta_pdf


def crear_tabla(datos, anchos):
    tabla = Table(datos, colWidths=anchos, repeatRows=1)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9EAF7")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F6F7")]),
    ]))
    return tabla


# ============================================================
# 8. PROGRAMA PRINCIPAL
# ============================================================

def main():
    print("=" * 58)
    print(" SIMULACIÓN MONTE CARLO - MÁQUINA INDUSTRIAL")
    print("=" * 58)

    df = ejecutar_simulacion()
    indicadores, frecuencia = calcular_indicadores(df)
    rutas = generar_graficos(df, frecuencia)
    ruta_csv, ruta_excel = exportar_datos(df, indicadores, frecuencia)
    ruta_pdf = generar_pdf(indicadores, frecuencia, rutas)

    print("\n--- RESUMEN DE RESULTADOS ---")
    for clave, valor in indicadores.items():
        if isinstance(valor, (float, np.floating)):
            print(f"{clave}: {valor:,.2f}")
        else:
            print(f"{clave}: {valor}")

    print("\n--- FRECUENCIA POR TIPO DE FALLA ---")
    print(frecuencia.to_string(index=False))

    print("\n--- ARCHIVOS GENERADOS ---")
    for ruta in [ruta_pdf, ruta_excel, ruta_csv, *rutas.values()]:
        print(f"  {ruta.resolve()}")

    print("\nSimulación finalizada correctamente.")


if __name__ == "__main__":
    main()
'''
script_path = os.path.join(workdir, "simulacion_maquina.py")
with open(script_path, "w", encoding="utf-8") as f:
    f.write(script)

# Ejecutar el script para comprobar que realmente funciona.
proc = subprocess.run(
    [sys.executable, script_path],
    cwd=workdir,
    capture_output=True,
    text=True,
    timeout=120
)

print("CODIGO DE SALIDA:", proc.returncode)
print(proc.stdout[-6000:])
if proc.stderr:
    print("ERRORES / ADVERTENCIAS:")
    print(proc.stderr[-4000:])

