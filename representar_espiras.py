import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd

# Cargar los archivos proporcionados
df_espiras = pd.read_csv("espiras_con_fechas_uniformes.csv")
df_paradas = pd.read_csv("paradas_actualizadas.csv")
# Convertir la columna de hora a datetime
df_espiras['hora'] = pd.to_datetime(df_espiras['hora'], format='%H:%M:%S', errors='coerce')

# Filtrar por una fecha concreta
fecha_objetivo = "17/03/2024"
df_filtrado = df_espiras[df_espiras['fecha'] == fecha_objetivo].copy()

# Normalizar la ocupación para los colores
scaler = MinMaxScaler()
df_filtrado['ocup_norm'] = scaler.fit_transform(df_filtrado[['ocup']])

# Crear el gráfico
plt.figure(figsize=(14, 8))

# Representar cada espira como un punto con color por ocupación
scatter = plt.scatter(
    df_filtrado['hora'],
    df_filtrado['distancia'],
    c=df_filtrado['ocup'],
    cmap='viridis',
    s=10,
    alpha=0.8
)

# Añadir etiquetas de paradas en el eje Y
paradas_cr = df_paradas[df_paradas['Direccion'] == 'CRISTO REY']
plt.yticks(paradas_cr['Distancia'], paradas_cr['Nombre Parada'])

# Configurar eje X con formato de hora
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
plt.xticks(rotation=45)

# Añadir barra de color, título y etiquetas
cbar = plt.colorbar(scatter)
cbar.set_label("Ocupación (%)")

plt.title(f"Ocupación de espiras el {fecha_objetivo}")
plt.xlabel("Hora del día")
plt.ylabel("Paradas (según distancia)")
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()