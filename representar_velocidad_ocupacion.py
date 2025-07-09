import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm

# ================================
# Cargar datos
# ================================
df = pd.read_csv("Bd_Buses_con_ocupacion_media_max.csv", parse_dates=["date"])
df_paradas = pd.read_csv("paradas_actualizadas.csv")

# ================================
# Filtrar paradas por dirección CRISTO REY y ordenarlas
# ================================
df_paradas["Direccion"] = df_paradas["Direccion"].str.strip().str.upper()
df_paradas_cr = df_paradas[df_paradas["Direccion"] == "CRISTO REY"].copy()
df_paradas_cr = df_paradas_cr.sort_values(by="Distancia").reset_index(drop=True)

# ================================
# Seleccionar bus y fecha automáticamente
# ================================
bus_id = df["bus"].unique()[4]
fecha = df[df["bus"] == bus_id]["fecha"].unique()[2]

# ================================
# Filtrar y ordenar datos
# ================================
df_filtrado = df[(df["bus"] == bus_id) & (df["fecha"] == fecha)].copy()
df_filtrado.sort_values("date", inplace=True)

# ================================
# Normalizar velocidad para mapa de color
# ================================
vel_norm = mcolors.Normalize(vmin=df_filtrado["velocidad_tramo_kmh"].min(),
                             vmax=40)
cmap = cm.get_cmap("viridis")

# ================================
# Crear figura
# ================================
fig, ax = plt.subplots(figsize=(15, 6))

# Dibujar líneas por ciclo_id
for ciclo_id, grupo in df_filtrado.groupby("ciclo_id"):
    grupo = grupo.sort_values("date").reset_index(drop=True)
    for i in range(len(grupo) - 1):
        x1, x2 = grupo.loc[i, "date"], grupo.loc[i + 1, "date"]
        y1, y2 = grupo.loc[i, "distance_limpia"], grupo.loc[i + 1, "distance_limpia"]
        velocidad = grupo.loc[i, "velocidad_tramo_kmh"]
        ocupacion = grupo.loc[i, "ocupacion_media_tramo"]
        color = cmap(vel_norm(velocidad))
        linewidth = 1 + (ocupacion / df_filtrado["ocupacion_media_tramo"].max()) * 4 if pd.notna(ocupacion) else 1
        ax.plot([x1, x2], [y1, y2], color=color, linewidth=linewidth)

# ================================
# Añadir etiquetas de paradas
# ================================
ax.set_yticks(df_paradas_cr["Distancia"])
ax.set_yticklabels(df_paradas_cr["Nombre Parada"], fontsize=8)
ax.tick_params(axis='y', pad=5)

# Título y ejes
ax.set_title(f"Recorrido bus {bus_id} el {fecha}\nColor = Velocidad media, Grosor = Ocupación media")
ax.set_xlabel("Hora")
ax.set_ylabel("Paradas (posición sobre la línea)")

# Barra de color
sm = cm.ScalarMappable(cmap=cmap, norm=vel_norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax)
cbar.set_label("Velocidad media (km/h)")

plt.grid(True)
plt.tight_layout()
plt.show()
