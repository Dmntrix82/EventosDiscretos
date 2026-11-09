
import numpy as np

# ==========================================================
# 1. CONFIGURACION DEL PROBLEMA
# ==========================================================

np.random.seed(42)

DIAS = 300
HORAS_DIA = 8
MINUTOS_DIA = HORAS_DIA * 60

# Llegadas: 15 clientes por hora
TASA_LLEGADA = 15

# Servicio: media de 2.2 minutos por transaccion
MEDIA_SERVICIO = 2.2

# Distribucion del numero de transacciones
TRANSACCIONES = [1, 2, 3, 4]
PROBABILIDADES = [0.40, 0.30, 0.20, 0.10]


# ==========================================================
# 2. VARIABLES PARA ALMACENAR LOS RESULTADOS
# ==========================================================

esperas_totales = []
promedios_diarios = []
clientes_por_dia = []

# Contadores generales
clientes_sin_espera = 0
clientes_con_espera = 0


# ==========================================================
# 3. SIMULACION DE LOS 300 DIAS
# ==========================================================

for dia in range(DIAS):

    # ------------------------------------------------------
    # A. GENERAR LLEGADAS DE CLIENTES
    # ------------------------------------------------------

    llegadas = []
    tiempo = 0

    # Tiempo entre llegadas: exponencial
    media_entre_llegadas = 60 / TASA_LLEGADA

    while True:

        tiempo += np.random.exponential(media_entre_llegadas)

        # Solo llegan clientes durante las 8 horas
        if tiempo > MINUTOS_DIA:
            break

        llegadas.append(tiempo)

    n_clientes = len(llegadas)

    clientes_por_dia.append(n_clientes)

    # ------------------------------------------------------
    # B. DETERMINAR NUMERO DE TRANSACCIONES
    # ------------------------------------------------------

    numero_transacciones = np.random.choice(
        TRANSACCIONES,
        size=n_clientes,
        p=PROBABILIDADES
    )

    # ------------------------------------------------------
    # C. GENERAR TIEMPOS DE SERVICIO
    # ------------------------------------------------------

    servicios = []

    for cantidad in numero_transacciones:

        # Cada transaccion tiene servicio exponencial
        tiempos = np.random.exponential(
            scale=MEDIA_SERVICIO,
            size=cantidad
        )

        # Tiempo total de servicio del cliente
        servicios.append(np.sum(tiempos))

    # ------------------------------------------------------
    # D. CALCULAR TIEMPOS DE ESPERA EN LA FILA
    # ------------------------------------------------------

    fin_servicio_anterior = 0
    esperas_dia = []

    for i in range(n_clientes):

        llegada = llegadas[i]
        servicio = servicios[i]

        # El cliente comienza cuando llega o cuando
        # termina el servicio del cliente anterior
        inicio_servicio = max(
            llegada,
            fin_servicio_anterior
        )

        # Tiempo de espera en la fila
        espera = inicio_servicio - llegada

        esperas_dia.append(espera)

        # Actualizar el momento de finalizacion
        fin_servicio_anterior = inicio_servicio + servicio

        # Clasificar clientes
        if espera == 0:
            clientes_sin_espera += 1
        else:
            clientes_con_espera += 1

    # ------------------------------------------------------
    # E. ALMACENAR RESULTADOS DEL DIA
    # ------------------------------------------------------

    esperas_totales.extend(esperas_dia)

    if n_clientes > 0:
        promedios_diarios.append(np.mean(esperas_dia))
    else:
        promedios_diarios.append(0)


# ==========================================================
# 4. CALCULO DE RESULTADOS GENERALES
# ==========================================================

total_clientes = len(esperas_totales)

tiempo_promedio_espera = np.mean(esperas_totales)

promedio_diario_espera = np.mean(promedios_diarios)

desviacion_espera = np.std(esperas_totales, ddof=1)

promedio_clientes_dia = np.mean(clientes_por_dia)

porcentaje_con_espera = (
    clientes_con_espera / total_clientes
) * 100

porcentaje_sin_espera = (
    clientes_sin_espera / total_clientes
) * 100


# ==========================================================
# 5. ANALISIS TEORICO DE LA CAPACIDAD
# ==========================================================

# Numero esperado de transacciones por cliente
media_transacciones = sum(
    t * p for t, p in zip(
        TRANSACCIONES, PROBABILIDADES
    )
)

# Tiempo medio de servicio por cliente
servicio_promedio = (
    media_transacciones * MEDIA_SERVICIO
)

# Tasa de servicio por hora
tasa_servicio = 60 / servicio_promedio

# Utilizacion teorica
utilizacion = TASA_LLEGADA / tasa_servicio


# ==========================================================
# 6. PRESENTACION DE RESULTADOS
# ==========================================================

print("=" * 60)
print("       SIMULACION DE COLA BANCARIA")
print("=" * 60)

print(f"Numero de dias simulados: {DIAS}")
print(f"Horas por dia: {HORAS_DIA}")
print(f"Total de clientes: {total_clientes}")
print(f"Promedio de clientes por dia: {promedio_clientes_dia:.2f}")

print("\n--- ANALISIS DE ESPERA ---")

print(
    f"Tiempo promedio de espera general: "
    f"{tiempo_promedio_espera:.4f} minutos"
)

print(
    f"Promedio de los promedios diarios: "
    f"{promedio_diario_espera:.4f} minutos"
)

print(
    f"Desviacion estandar de espera: "
    f"{desviacion_espera:.4f} minutos"
)

print(f"Clientes que esperaron: {clientes_con_espera}")
print(f"Clientes sin espera: {clientes_sin_espera}")

print(f"Porcentaje que espero: {porcentaje_con_espera:.2f}%")
print(f"Porcentaje sin espera: {porcentaje_sin_espera:.2f}%")

print("\n--- ANALISIS DE CAPACIDAD ---")

print(f"Transacciones promedio por cliente: {media_transacciones:.2f}")

print(f"Servicio promedio por cliente: {servicio_promedio:.2f} min")

print(f"Tasa de llegada: {TASA_LLEGADA:.2f} clientes/hora")

print(f"Tasa de servicio: {tasa_servicio:.4f} clientes/hora")

print(f"Utilizacion teorica: {utilizacion * 100:.2f}%")

print("\n--- CONCLUSION ---")

if utilizacion >= 1:
    print("El sistema esta SOBRECARGADO.")
    print("La demanda supera la capacidad de atencion.")
    print("Se recomienda incorporar otra cajera.")
else:
    print("El sistema es estable en promedio.")

print("=" * 60)

