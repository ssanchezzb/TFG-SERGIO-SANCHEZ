import pandas as pd
from datetime import timedelta

# Cargar archivos
buses_df = pd.read_csv("Bd_Buses_con_velocidades_limpio_x.csv")
espiras_df = pd.read_csv("espiras_con_fechas_uniformes.csv")
paradas_df = pd.read_csv("paradas_actualizadas.csv")

# Preprocesamiento: formatear fechas y horas
buses_df["hora"] = buses_df["hora"].astype(str).str.extract(r"(\d{1,2}:\d{2}(?::\d{2})?)")
buses_df["datetime"] = pd.to_datetime(buses_df["fecha"] + " " + buses_df["hora"], dayfirst=True, errors='coerce')
espiras_df["datetime"] = pd.to_datetime(espiras_df["fecha"] + " " + espiras_df["hora"], dayfirst=True, errors='coerce')

# Asociar distancias de paradas
parada_dist = paradas_df.set_index("ID Parada")["Distancia"].to_dict()
buses_df["dist_ini_real"] = buses_df["stop_ini"].map(parada_dist)
buses_df["dist_fin_real"] = buses_df["stop_fin"].map(parada_dist)
buses_df = buses_df.dropna(subset=["datetime", "dist_ini_real", "dist_fin_real"])

# Crear identificador de tramo
buses_df["tramo_id"] = buses_df["stop_ini"].astype(str) + "-" + buses_df["stop_fin"].astype(str)

# Inicializar lista para resultados parciales
resultados = []

print("Procesando por bus...")

for bus_id, grupo_bus in buses_df.groupby("bus"):
    print(f"Bus {bus_id}...")
    ocupaciones_mean = []
    ocupaciones_max = []
    ocupaciones_std = []

    for idx, row in grupo_bus.iterrows():
        t = row["datetime"]
        tramo = row["tramo_id"]
        if pd.isna(tramo) or pd.isna(t):
            ocupaciones_mean.append(None)
            ocupaciones_max.append(None)
            ocupaciones_std.append(None)
            continue

        d_min = min(row["dist_ini_real"], row["dist_fin_real"])
        d_max = max(row["dist_ini_real"], row["dist_fin_real"])

        # Filtro por ventana de tiempo ±5 min y rango de distancia
        mask = (
            (espiras_df["datetime"] >= t - timedelta(minutes=5)) &
            (espiras_df["datetime"] <= t + timedelta(minutes=5)) &
            (espiras_df["distancia"] >= d_min) &
            (espiras_df["distancia"] <= d_max)
        )

        ocup_values = espiras_df.loc[mask, "ocup"]
        ocupaciones_mean.append(ocup_values.mean())
        ocupaciones_max.append(ocup_values.max())
        ocupaciones_std.append(ocup_values.std())

    grupo_bus["ocupacion_media_tramo"] = ocupaciones_mean
    grupo_bus["ocupacion_maxima_tramo"] = ocupaciones_max
    grupo_bus["ocupacion_std_tramo"] = ocupaciones_std
    resultados.append(grupo_bus)

# Concatenar resultados finales
total_df = pd.concat(resultados)

print("Guardando archivo final con estadísticas de ocupación por bus...")
total_df.to_csv("Bd_Buses_con_ocupacion_media_max.csv", index=False)
print("Hecho. Archivo guardado como 'Bd_Buses_con_ocupacion.csv'")
