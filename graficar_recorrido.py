import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.cm as cm

# ===============================
# Función para graficar recorridos múltiples como líneas
# ===============================
def graficar_recorridos_multiples(df_buses, df_paradas, fecha, hora_inicio, hora_fin):
    """
    Grafica recorridos de varios buses con líneas (sin puntos), eje Y con nombres de paradas
    y filtrado por franja horaria.
    """
    # Crear figura
    fig, ax = plt.subplots(figsize=(14, 6))

    # Obtener lista de buses únicos
    buses = df_buses["bus"].unique()

    # Crear mapa de colores
    cmap = cm.get_cmap("tab20", len(buses))
    colores = [cmap(i) for i in range(len(buses))]

    # Graficar cada bus como línea
    for i, bus_id in enumerate(buses):
        df_bus = df_buses[df_buses["bus"] == bus_id].sort_values("date")
        ax.plot(df_bus["date"], df_bus["distance_limpia"],
                label=f'Bus {bus_id}',
                color=colores[i],
                linewidth=2)

    # Eje X
    ax.set_xlabel("Hora")
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))

    # Eje Y con nombres de paradas
    df_paradas = df_paradas.sort_values("Distancia").reset_index(drop=True)
    ax.set_yticks(df_paradas["Distancia"])
    ax.set_yticklabels(df_paradas["Nombre Parada"], fontsize=8)
    ax.set_ylabel("Paradas / Distancia (m)")
    ax.tick_params(axis='y', pad=5)

    # Líneas horizontales para paradas
    for dist in df_paradas["Distancia"]:
        ax.axhline(y=dist, color='grey', linestyle='--', linewidth=0.5, alpha=0.5)

    # Título con rango horario
    ax.set_title(f"Recorrido de buses el {fecha} ({hora_inicio}–{hora_fin})")
    ax.legend(loc='best')
    ax.set_ylim(0, 9000)
    # Estética
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.show()

# ===============================
# Cargar datos desde CSV
# ===============================
df = pd.read_csv("Bd_Buses_con_velocidades_limpio.csv", parse_dates=["date"])
df_paradas = pd.read_csv("paradas_actualizadas.csv")

# ===============================
# Preparar paradas dirección CRISTO REY
# ===============================
df_paradas["Direccion"] = df_paradas["Direccion"].str.strip().str.upper()
df_paradas_cr = df_paradas[df_paradas["Direccion"] == "CRISTO REY"].copy()
df_paradas_cr = df_paradas_cr.sort_values(by="Distancia").reset_index(drop=True)

# ===============================
# Elegir fecha y filtrar
# ===============================
fecha_objetivo = df["fecha"].unique()[10]  # Cambia el índice si deseas otra fecha
df_fecha = df[df["fecha"] == fecha_objetivo].copy()

# Asegurar formato datetime para filtrado horario
df_fecha["date"] = pd.to_datetime(df_fecha["date"])

# Filtrar por franja horaria: 08:00 a 13:00
hora_inicio = "08:00"
hora_fin = "13:00"
df_fecha = df_fecha[
    (df_fecha["date"].dt.time >= pd.to_datetime(hora_inicio).time()) &
    (df_fecha["date"].dt.time <= pd.to_datetime(hora_fin).time())
]

# Limitar a los primeros 5 buses
primeros_5_buses = df_fecha["bus"].unique()[:7]
df_fecha = df_fecha[df_fecha["bus"].isin(primeros_5_buses)]

# ===============================
# Dibujar recorridos múltiples
# ===============================
graficar_recorridos_multiples(df_fecha, df_paradas_cr, fecha_objetivo, hora_inicio, hora_fin)
