import requests
import json
import sqlite3
import csv
from datetime import datetime
import time  # Para agregar pausas entre solicitudes

# Credenciales de la API de EMT Madrid
EMAIL = "ssanchezzbl@gmail.com"
PASSWORD = "Se."

# Obtener el token de autenticación
def get_token():
    """
    Obtiene el token de autenticación desde la API de EMT Madrid.
    """
    url = "https://openapi.emtmadrid.es/v1/mobilitylabs/user/login/"
    headers = {'email': EMAIL, 'password': PASSWORD}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        if 'data' not in response_data or not response_data['data']:
            print("Error: No se obtuvo un token válido.")
            return None
        return response_data['data'][0]['accessToken']
    except requests.RequestException as e:
        print(f"Error al obtener el token: {e}")
        return None

# Obtener llegada de autobuses a una parada específica
def find_closest(array, value):
	for i in range(0, len(array)):
		num = array[i]
		resta = value - int(num)
		if resta <= 0:
			return array[i-1]
def time_arrival_bus(stop_id, line_id, stop_distance, cursor, list_id_buses, today):
    """
    Consulta las llegadas de autobuses a una parada específica y línea.
    """
    token = get_token()
    if not token:
        print("No se pudo obtener el token.")
        return 8795

    url = f"https://openapi.emtmadrid.es/v2/transport/busemtmad/stops/{stop_id}/arrives/1/"
    headers = {
        'accessToken': token,
        'Accept': 'application/json'
    }

    # Payload necesario para la solicitud
    payload = {
        'cultureInfo': 'ES',
        'Text_StopRequired_YN': 'Y',
        'Text_EstimationsRequired_YN': 'Y',
        'Text_IncidencesRequired_YN': 'Y',
        'DateTime_Referenced_Incidencies_YYYYMMDD': today
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        json_data = response.json()
      

        if json_data.get('code') != '00':
            print(f"Error en la respuesta de la API: {json_data.get('description')}")
            return 8795

        # Procesar los datos recibidos
        lista_distance_buses = []
        for item in json_data['data']:
            for bus in item.get('Arrive', []):
                if bus['destination'] == 'PROSPERIDAD':
                    bus_ident = bus['bus']
                    distance_to_stop = int(bus['DistanceBus'])
                    distance = int(stop_distance) - distance_to_stop
                    lista_distance_buses.append(distance)
                    #print(f"BUS ID: {bus_ident}")
                    fecha_ddmmaaaa = datetime.now().strftime("%d/%m/%Y")
                    hora_hhmmss = datetime.now().strftime("%H:%M:%S")
                    # Condición más restrictiva: distancia en un rango reducido
                    if 0 <= distance <= 8818 :
                        list_id_buses.append(bus_ident)
                        cursor.execute(
                            '''INSERT INTO Datos (date, id_bus, distancia_to_stop, distancia_bus, id_parada, dis_parada, fecha, hora)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # date en formato ISO
                            str(bus_ident), str(distance_to_stop), str(distance),
                            str(stop_id), str(stop_distance), fecha_ddmmaaaa, hora_hhmmss)
                        )

        # Retornar la distancia mínima de los autobuses procesados
        #print(f"LISTA DE DISTANCIAS: {lista_distance_buses}")
        #print(f"LISTA BUSES: {list_id_buses}")
        return min(lista_distance_buses) if lista_distance_buses else 8795

    except requests.RequestException as e:
        print(f"Error al obtener la llegada del autobús: {e}")
        return 8795
def find_closest(array, value):
	for i in range(0, len(array)):
		num = array[i]
		resta = value - int(num)
		if resta <= 0:
			return array[i-1]

# Programa principal
if __name__ == "__main__":
    print("Iniciando el monitoreo continuo de la línea...")

    # Leer archivo CSV de paradas
    dicc_stops = {}
    dicc_stops_reverse = {}
    list_stops = []

    try:
        with open('paradas_actualizadas.csv') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['Direccion'] == 'Cristo Rey':  # Filtrar solo las paradas hacia Cristo Rey
                    id_stop = row['ID Parada']
                    distance = int(row['Distancia']) if row['Distancia'] != "N/A" else 0
                    list_stops.append(distance)
                    dicc_stops[distance] = id_stop #diccionario dada la distancia sacamos id
                    dicc_stops_reverse[id_stop] = distance #diccionario dada el id sacamos la distancia
    except FileNotFoundError as e:
        print(f"Error al leer el archivo CSV: {e}")
        exit()
    # Conexión a la base de datos SQLite
    #print(dicc_stops_reverse)
    bd = sqlite3.connect(r"C:\Users\ssanc\OneDrive\Escritorio\TFG AUTOBUSES\ARTICULOS PARA EL TFG\TFG SEPT\L1 GENERAL\script\Buses_data.db")

    cursor = bd.cursor()

    # Crear tabla si no existe
    cursor.execute('''CREATE TABLE IF NOT EXISTS Datos (
                  date TEXT,
                  id_bus INTEGER,
                  distancia_to_stop INTEGER,
                  distancia_bus INTEGER,
                  id_parada INTEGER,
                  dis_parada INTEGER,
                  fecha TEXT,
                  hora TEXT)''')

    # Obtener fecha actual
    today_date = datetime.now().strftime("%Y%m%d")

    # Comenzar desde la última parada
    list_id_buses = []
    current_stop = '273'
  # Última parada
    stop_distance = dicc_stops_reverse[current_stop]
    distance_min_bus = time_arrival_bus(current_stop, 1, stop_distance, cursor, list_id_buses, today_date)
    bd.commit()
    while True:
        # Buscar la siguiente parada
        try:
            #print("--------------------------------------")
            next_stop = dicc_stops[find_closest(list_stops, distance_min_bus)]
            #print(f"ID PARADA: {next_stop}")
            stop_distance = dicc_stops_reverse[next_stop]
            distance_min_bus = time_arrival_bus(next_stop, 1, stop_distance, cursor, list_id_buses, today_date)
            
            #print(f"ID DIS PARADA: {stop_distance}")
            #print(f"DISTANCIA MINIMA {distance_min_bus}")
            bd.commit()
        except ValueError:
            print("Error: No se pudo encontrar la siguiente parada.")
            break

        

        time.sleep(5)  # Esperar 5 segundos entre solicitudes para no saturar la API

    cursor.close()
    bd.close()
    print("Monitoreo finalizado.")
