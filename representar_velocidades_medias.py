import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from matplotlib.dates import DateFormatter

# ===============================
# Cargar datos
# ===============================
df = pd.read_csv("Bd_Buses_con_velocidades_limpio.csv", parse_dates=["date"])
df_paradas = pd.read_csv("paradas_actualizadas.csv")

# Filtrar por dirección CRISTO REY y ordenar por distancia
df_paradas["Direccion"] = df_paradas["Direccion"].str.strip().str.upper()
df_paradas_cr = df_paradas[df_paradas["Direccion"] == "CRISTO REY"].copy()
df_paradas_cr = df_paradas_cr.sort_values(by="Distancia").reset_index(drop=True)

# ===============================
# Filtrar por un bus y fecha
# ===============================
bus_id = df["bus"].unique()[4]
fecha = df[df["bus"] == bus_id]["fecha"].unique()[2]

df_filtrado = df[(df["bus"] == bus_id) & (df["fecha"] == fecha)].copy()
df_filtrado.sort_values("hora_limpia", inplace=True)

# ===============================
# Normalizar velocidades para color
# ===============================
norm = mcolors.Normalize(vmin=df_filtrado["velocidad_tramo_kmh"].min(),
                         vmax=40)
cmap = cm.get_cmap("viridis")

# ===============================
# Crear la figura
# ===============================
fig, ax = plt.subplots(figsize=(14, 6))
fig.subplots_adjust(left=0.3)  # Dejar espacio para etiquetas de parada

# Dibujar líneas de recorrido por velocidad media
for ciclo_id, grupo in df_filtrado.groupby("ciclo_id"):
    grupo = grupo.sort_values("hora_limpia").reset_index(drop=True)
    for i in range(len(grupo) - 1):
        x1 = grupo.loc[i, "date"]
        x2 = grupo.loc[i + 1, "date"]
        y1 = grupo.loc[i, "distance_limpia"]
        y2 = grupo.loc[i + 1, "distance_limpia"]
        velocidad = grupo.loc[i, "velocidad_tramo_kmh"]
        color = cmap(norm(velocidad))
        ax.plot([x1, x2], [y1, y2], color=color, linewidth=2)

# Etiquetas y ejes
ax.set_xlabel("Hora")
ax.set_ylabel("Distancia recorrida (m)")
ax.set_title(f"Recorrido del autobús {bus_id} el {fecha} con color según velocidad media")
ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))

# Añadir nombres de paradas en eje Y izquierdo
ax.set_yticks(df_paradas_cr["Distancia"])
ax.set_yticklabels(df_paradas_cr["Nombre Parada"], fontsize=8)
ax.tick_params(axis='y', pad=5)

# Barra de color
sm = cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax)
cbar.set_label("Velocidad media (km/h)")

plt.grid(True)
plt.tight_layout()
plt.show()
